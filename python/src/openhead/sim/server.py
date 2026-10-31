"""Desktop simulator: speaks the OpenHead protocol exactly as the iOS app does.

Every incoming message is validated against the JSON Schema; the face runs in Chromium.
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import platform
import secrets
import socket
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

from websockets.asyncio.server import ServerConnection, serve
from websockets.exceptions import ConnectionClosed

from .. import __version__
from ..protocol import (
    MESSAGE_TYPES,
    PROTOCOL_VERSION,
    SERVICE_TYPE,
    now_ms,
    validate,
)
from . import imu
from .face import BrowserFace, FaceError
from .shots import ShotServer

log = logging.getLogger("openhead.sim")

DEVICE_MESSAGES = {"ack", "error", "welcome", "pair_required", "imu", "status", "log"}
CAPABILITIES = ["face", "display.image", "display.web", "imu", "status", "log", "screenshot"]
TOPIC_RATES = {"imu": (50.0, 100.0), "status": (1.0, 1.0), "log": (0.0, 0.0)}  # default, max
LOG_LEVELS = ["debug", "info", "notice", "warning", "error", "fault"]
PAIR_MAX_FAILURES = 5
PAIR_LOCK_S = 300
PAIR_CODE_TTL_S = 60


class SimError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass
class SimConfig:
    host: str = "0.0.0.0"
    port: int = 8765  # 0 picks a free port (tests)
    name: str = "openhead-sim"
    dev_mode: bool = True
    headless: bool = True
    idle: bool | None = None  # default: idle motion only when windowed
    size: tuple[int, int] = (390, 844)
    face_dist: Path | None = None
    theme: str = "cartoon"
    token_path: Path | None = None  # persist paired clients; None keeps them in memory
    pairing_code: str | None = None  # default: "0000" in dev mode, random otherwise
    mdns: bool = True
    validate_outgoing: bool = False  # tests: record outgoing messages the schema rejects
    record_video_dir: Path | None = None  # record the screen with Playwright (demos)


class Session:
    def __init__(self, server: SimServer, ws: ServerConnection):
        self.server = server
        self.ws = ws
        self.seq = 0
        self.client: str | None = None
        self.token: str | None = None
        self.subs: dict[str, tuple[asyncio.Task | None, list[str] | None]] = {}
        self._lock = asyncio.Lock()

    async def send(self, type_: str, **fields: Any) -> None:
        async with self._lock:
            msg = {"type": type_, "ts": now_ms(), "seq": self.seq, **fields}
            self.seq += 1
            if self.server.config.validate_outgoing and (errors := validate(msg)):
                self.server.violations.append(f"{type_}: {errors}")
            await self.ws.send(json.dumps(msg))

    async def error(self, msg_id: str | None, code: str, message: str) -> None:
        await self.send("error", **({"id": msg_id} if msg_id else {}), code=code,
                        message=message[:1024])

    def stop_subs(self) -> None:
        for task, _ in self.subs.values():
            if task:
                task.cancel()
        self.subs.clear()


class SimServer:
    def __init__(self, config: SimConfig | None = None, **overrides: Any):
        self.config = config or SimConfig(**overrides)
        c = self.config
        self.face = BrowserFace(c.face_dist, size=c.size, headless=c.headless,
                                idle=(not c.headless) if c.idle is None else c.idle,
                                on_log=lambda level, msg: self.log(level, "face", msg),
                                record_video_dir=c.record_video_dir)
        self.shots = ShotServer()
        self.sessions: set[Session] = set()
        self.logs: deque[dict] = deque(maxlen=2000)
        self.violations: list[str] = []  # outgoing schema violations (validate_outgoing)
        self.view = "face"
        self.overlay = "none"
        self.mode = "idle"
        self.settings: dict[str, Any] = {
            "name": c.name, "port": c.port, "mount_offset": [0, 0, 0, 1], "offline_theme": c.theme,
        }
        self.tokens: dict[str, str] = self._load_tokens()
        self.port = c.port
        self.started = time.monotonic()
        self._code: str | None = None
        self._code_expires = 0.0
        self._failures = 0
        self._locked_until = 0.0
        self._timers: dict[str, asyncio.Task] = {}
        self._ws_server: Any = None
        self._zeroconf: Any = None

    # --- lifecycle ------------------------------------------------------------

    async def start(self) -> None:
        await self.face.start(self.config.theme)
        self._ws_server = await serve(self._handler, self.config.host, self.config.port,
                                      max_size=4 * 1024 * 1024)
        self.port = self._ws_server.sockets[0].getsockname()[1]
        await self.shots.start(self.config.host, self.port + 1)
        if self.config.mdns:
            await self._advertise()
        self.log("info", "link", f"listening on {self.config.host}:{self.port} "
                                 f"(screenshots on {self.port + 1})")

    async def stop(self) -> None:
        for task in self._timers.values():
            task.cancel()
        for session in list(self.sessions):
            session.stop_subs()
        if self._zeroconf:
            await self._zeroconf.async_unregister_all_services()
            await self._zeroconf.async_close()
        if self._ws_server:
            self._ws_server.close()
            await self._ws_server.wait_closed()
        await self.shots.stop()
        await self.face.close()

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.stop()

    async def serve_forever(self) -> None:
        await self.start()
        try:
            await asyncio.Future()
        finally:
            await self.stop()

    async def _advertise(self) -> None:
        try:
            from zeroconf import ServiceInfo
            from zeroconf.asyncio import AsyncZeroconf

            ip = _local_ip()
            info = ServiceInfo(
                SERVICE_TYPE, f"{self.config.name}.{SERVICE_TYPE}",
                addresses=[socket.inet_aton(ip)], port=self.port,
                server=f"{self.config.name}.local.",
            )
            self._zeroconf = AsyncZeroconf()
            await self._zeroconf.async_register_service(info)
            self.log("info", "link", f"advertising {self.config.name} on mDNS ({ip}:{self.port})")
        except Exception as exc:  # noqa: BLE001 - mDNS is a convenience, never fatal
            self.log("warning", "link", f"mDNS advertising failed: {exc}")

    # --- logging --------------------------------------------------------------

    def log(self, level: str, subsystem: str, message: str, seq_ref: int | None = None) -> None:
        entry = {"time_ms": now_ms(), "level": level, "subsystem": subsystem, "message": message}
        if seq_ref is not None:
            entry["seq_ref"] = seq_ref
        self.logs.append(entry)
        log.log(logging.WARNING if level in ("warning", "error", "fault") else logging.INFO,
                "[%s] %s", subsystem, message)
        for session in list(self.sessions):
            if "log" in session.subs:
                asyncio.create_task(self._send_quietly(session, "log", entry))

    @staticmethod
    async def _send_quietly(session: Session, type_: str, payload: dict) -> None:
        try:
            await session.send(type_, **payload)
        except ConnectionClosed:
            pass

    # --- connection -----------------------------------------------------------

    async def _handler(self, ws: ServerConnection) -> None:
        session = Session(self, ws)
        self.sessions.add(session)
        peer = ws.remote_address[0] if ws.remote_address else "?"
        self.log("info", "link", f"connection from {peer}")
        try:
            async for raw in ws:
                await self._on_message(session, raw)
        except ConnectionClosed:
            pass
        finally:
            session.stop_subs()
            self.sessions.discard(session)
            self.log("info", "link", f"{session.client or peer} disconnected")

    async def _on_message(self, s: Session, raw: str | bytes) -> None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            await s.error(None, "invalid_params", "message is not JSON")
            return
        if not isinstance(data, dict):
            await s.error(None, "invalid_params", "message must be a JSON object")
            return
        type_ = data.get("type")
        msg_id = data.get("id") if isinstance(data.get("id"), str) else None
        if type_ != "face.envelope":
            self.log("info", "link", f"recv {type_}" + (f" id={msg_id}" if msg_id else ""),
                     seq_ref=data.get("seq") if isinstance(data.get("seq"), int) else None)

        if type_ in DEVICE_MESSAGES or type_ not in MESSAGE_TYPES:
            await s.error(msg_id, "unsupported", f"unsupported message type {type_!r}")
            return
        if errors := validate(data):
            await s.error(msg_id, "invalid_params", "; ".join(errors[:3]))
            return
        if type_ == "hello":
            await self._hello(s, data)
            return
        if type_ == "pair":
            await self._pair(s, data)
            return
        if s.token is None:
            await s.error(msg_id, "unauthorized", "send hello with a token, or pair first")
            return
        if type_ == "face.envelope":
            await self.face.envelope(data["level"])
            return
        try:
            result = await self._command(s, type_, data)
        except SimError as exc:
            self.log("warning", "link", f"{type_} id={msg_id}: {exc.code}: {exc.message}",
                     seq_ref=data["seq"])
            await s.error(msg_id, exc.code, exc.message)
            return
        await s.send("ack", id=msg_id, **({"result": result} if result is not None else {}))

    # --- handshake and pairing ------------------------------------------------

    async def _hello(self, s: Session, d: dict) -> None:
        if d["protocol_version"].split(".")[0] != PROTOCOL_VERSION.split(".")[0]:
            await s.error(None, "unsupported",
                          f"protocol {d['protocol_version']} not supported; device speaks "
                          f"{PROTOCOL_VERSION}")
            return
        s.client = d["client"]
        if (token := d.get("token")) and token in self.tokens:
            s.token = token
            self.log("info", "link", f"{s.client} authenticated")
            await self._welcome(s)
            return
        if self._locked():
            await s.error(None, "rate_limited", "pairing locked after repeated failures")
            return
        if not self._code or time.monotonic() > self._code_expires:
            dev_code = "0000" if self.config.dev_mode else None
            self._code = self.config.pairing_code or dev_code or f"{secrets.randbelow(10**6):06d}"
            self._code_expires = time.monotonic() + PAIR_CODE_TTL_S
            self.log("notice", "link", f"pairing requested by {s.client}; code shown on screen")
            print(f"[openhead sim] pairing code for {s.client}: {self._code}", flush=True)
        await s.send("pair_required", code_hint=f"{len(self._code)}-digit code shown on "
                     f"{self.config.name}", code_length=len(self._code),
                     expires_in_ms=int(max(0, self._code_expires - time.monotonic()) * 1000),
                     attempts_left=PAIR_MAX_FAILURES - self._failures)

    def _locked(self) -> bool:
        return time.monotonic() < self._locked_until

    async def _pair(self, s: Session, d: dict) -> None:
        if self._locked():
            left = int(self._locked_until - time.monotonic())
            await s.error(None, "rate_limited", f"pairing locked for {left} s")
            return
        if s.client is None:
            await s.error(None, "unauthorized", "send hello first")
            return
        if not self._code or time.monotonic() > self._code_expires:
            await s.error(None, "unauthorized", "no pairing code active; send hello again")
            return
        if secrets.compare_digest(d["code"], self._code):
            token = secrets.token_urlsafe(32)
            self.tokens[token] = s.client
            self._save_tokens()
            s.token = token
            self._code = None
            self._failures = 0
            self.log("info", "link", f"paired {s.client}")
            await self._welcome(s)
            return
        self._failures += 1
        if self._failures >= PAIR_MAX_FAILURES:
            self._failures = 0
            self._code = None
            self._locked_until = time.monotonic() + PAIR_LOCK_S
            self.log("warning", "link", "pairing locked for 5 minutes after 5 wrong codes")
            await s.error(None, "rate_limited", "too many wrong codes; pairing locked for 300 s")
            return
        left = PAIR_MAX_FAILURES - self._failures
        await s.error(None, "unauthorized", f"wrong code; {left} attempts left")

    async def _welcome(self, s: Session) -> None:
        w, h = self.config.size
        themes = [t["name"] for t in await self.face.list_themes()]
        await s.send(
            "welcome", token=s.token, protocol_version=PROTOCOL_VERSION,
            device={
                "name": self.config.name, "platform": "sim", "model": "OpenHead Simulator",
                "os_version": platform.platform(terse=True)[:64], "app_version": __version__,
                "screen": {"width": w, "height": h, "scale": 1,
                           "safe_area": {"top": 0, "left": 0, "bottom": 0, "right": 0}},
            },
            capabilities=CAPABILITIES, themes=themes, dev_mode=self.config.dev_mode,
        )

    def _load_tokens(self) -> dict[str, str]:
        path = self.config.token_path
        if path and path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {}

    def _save_tokens(self) -> None:
        if path := self.config.token_path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.tokens, indent=2), encoding="utf-8")

    # --- commands -------------------------------------------------------------

    def _require_dev(self, type_: str) -> None:
        if not self.config.dev_mode:
            raise SimError("dev_mode_required", f"{type_} needs dev mode")

    def _timer(self, key: str, delay_ms: int, action: Any) -> None:
        if old := self._timers.pop(key, None):
            old.cancel()

        async def run() -> None:
            await asyncio.sleep(delay_ms / 1000)
            self._timers.pop(key, None)
            await action()

        self._timers[key] = asyncio.create_task(run())

    async def _command(self, s: Session, t: str, d: dict) -> dict | None:
        face = self.face
        try:
            match t:
                case "subscribe":
                    return self._subscribe(s, d)
                case "unsubscribe":
                    if (entry := s.subs.pop(d["topic"], None)) and entry[0]:
                        entry[0].cancel()
                    return None
                case "face.set_theme":
                    await face.set_theme(d["name"], d.get("transition_ms", 300))
                case "face.set_emotion":
                    await face.set_emotion(d["name"], d.get("intensity", 1.0),
                                           d.get("blend", "replace"), d.get("duration_ms"))
                case "face.look_at":
                    if d["frame"] == "screen":
                        x, y = d["x"], d["y"]
                    else:  # head frame: +yaw is the head's left, i.e. the viewer's right
                        x = max(-1.0, min(1.0, d["yaw"] / 45))
                        y = max(-1.0, min(1.0, d["pitch"] / 45))
                    await face.set_gaze(x, y)
                    if "duration_ms" in d:
                        self._timer("gaze", d["duration_ms"], lambda: face.set_gaze(0, 0))
                case "face.blink":
                    await face.blink()
                case "face.list":
                    state = await face.state()
                    return {"active": state["theme"], "themes": [
                        {k: th[k] for k in ("name", "version", "title", "expressions", "extras")}
                        for th in await face.list_themes()
                    ]}
                case "display.show":
                    await self._display(d)
                case "display.clear":
                    await self._clear_display()
                case "system.status":
                    return await self._status(s)
                case "system.screenshot":
                    return await self._screenshot(s, d)
                case "system.logs":
                    self._require_dev(t)
                    floor = LOG_LEVELS.index(d.get("level", "debug"))
                    entries = [e for e in self.logs if LOG_LEVELS.index(e["level"]) >= floor]
                    return {"entries": entries[-d.get("n", 100):]}
                case "system.diagnostics":
                    self._require_dev(t)
                    return {
                        "uptime_s": round(time.monotonic() - self.started, 1),
                        "thermal_state": "nominal", "memory_mb": 0, "frame_rate": 60,
                        "permissions": {"local_network": "not_required",
                                        "motion": "not_required", "camera": "not_required"},
                        "arkit": {"world_tracking": False, "face_tracking": False},
                    }
                case "system.settings":
                    if d["action"] == "set":
                        self._require_dev(t)
                        self._set_setting(d["key"], d["value"])
                    return {"settings": self.settings}
                case "mode.set":
                    if d["mode"] != "idle":
                        raise SimError("unsupported", f"mode {d['mode']} arrives in 0.2")
                case "mode.get":
                    return {"mode": self.mode}
                case _:
                    raise SimError("unsupported", f"{t} is not implemented")
        except FaceError as exc:
            raise SimError("invalid_params", str(exc)) from exc
        return None

    def _subscribe(self, s: Session, d: dict) -> dict:
        topic = d["topic"]
        default, maximum = TOPIC_RATES[topic]
        rate = min(d.get("rate_hz", default), maximum) if maximum else 0.0
        fields = d.get("fields")
        if (old := s.subs.pop(topic, None)) and old[0]:
            old[0].cancel()
        task = None
        if topic == "imu":
            task = asyncio.create_task(self._stream(s, "imu", rate, fields, self._imu))
        elif topic == "status":
            task = asyncio.create_task(self._stream(s, "status", rate, fields, self._status))
        s.subs[topic] = (task, fields)
        return {"topic": topic, "rate_hz": rate}

    async def _imu(self, s: Session) -> dict:
        return imu.sample(time.monotonic() - self.started)

    async def _stream(self, s: Session, topic: str, rate: float, fields: list[str] | None,
                      payload: Any) -> None:
        period = 1 / rate
        next_at = time.monotonic()
        try:
            while True:
                data = await payload(s)
                if fields:
                    data = {k: v for k, v in data.items() if k in fields}
                await s.send(topic, **data)
                next_at += period
                await asyncio.sleep(max(0.0, next_at - time.monotonic()))
        except (ConnectionClosed, asyncio.CancelledError):
            pass

    async def _status(self, s: Session) -> dict:
        state = await self.face.state()
        status = {
            "charging": False, "thermal_state": "nominal", "view": self.view,
            "overlay": self.overlay, "theme": state["theme"], "emotion": state["emotion"],
            "mode": self.mode, "dev_mode": self.config.dev_mode,
            "clients": sum(1 for x in self.sessions if x.token),
            "uptime_s": round(time.monotonic() - self.started, 1),
        }
        if s.ws.latency:
            status["rtt_ms"] = round(s.ws.latency * 1000, 1)
        return status

    async def _display(self, d: dict) -> None:
        if d["content"] == "face":
            await self._clear_display()
            return
        if d["content"] == "web" and not d["source"].startswith(("http://", "https://")):
            raise SimError("invalid_params", "web content needs an http(s) URL")
        # The schema already caps inline images (maxLength, about 1 MB of data).
        await self.face.show(d["content"], d["source"], d.get("overlay", "none"))
        self.view = d["content"]
        self.overlay = d.get("overlay", "none")
        if "duration_ms" in d:
            self._timer("display", d["duration_ms"], self._clear_display)

    async def _clear_display(self) -> None:
        if old := self._timers.pop("display", None):
            old.cancel()
        await self.face.clear()
        self.view = "face"
        self.overlay = "none"

    async def _screenshot(self, s: Session, d: dict) -> dict:
        self._require_dev("system.screenshot")
        png, width, height = await self.face.screenshot(d.get("scale", 1.0))
        if d.get("delivery", "url") == "inline":
            return {"width": width, "height": height,
                    "png_base64": base64.b64encode(png).decode()}
        host = s.ws.local_address[0]
        host = f"[{host}]" if ":" in host else host
        shot_id = self.shots.add(png, s.token or "")
        return {"width": width, "height": height,
                "url": f"http://{host}:{self.port + 1}/shot/{shot_id}.png", "expires_ms": 60000}

    def _set_setting(self, key: str, value: Any) -> None:
        checks = {
            "name": lambda v: isinstance(v, str) and 0 < len(v) <= 64,
            "port": lambda v: isinstance(v, int) and 1024 <= v <= 65534,
            "mount_offset": lambda v: isinstance(v, list) and len(v) == 4
            and all(isinstance(c, (int, float)) for c in v),
            "offline_theme": lambda v: isinstance(v, str),
        }
        if key not in checks:
            raise SimError("invalid_params", f"unknown setting {key!r}")
        if not checks[key](value):
            raise SimError("invalid_params", f"invalid value for {key}")
        self.settings[key] = value
        self.log("info", "settings", f"{key} set")


def _local_ip() -> str:
    """Address of the interface used for outbound traffic (no packets are sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect(("192.0.2.1", 9))
            return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"

