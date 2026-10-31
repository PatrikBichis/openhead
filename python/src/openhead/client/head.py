"""Asyncio client for an OpenHead device (the iOS app or the simulator)."""

from __future__ import annotations

import asyncio
import base64
import contextlib
import itertools
import json
import logging
import random
import urllib.request
from dataclasses import dataclass
from typing import Any, Self

from pydantic import BaseModel
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from ..protocol import DEFAULT_PORT, PROTOCOL_VERSION, models, now_ms, parse_message
from ..tokens import TokenStore

log = logging.getLogger("openhead.client")

TOPIC_MODELS: dict[str, type[BaseModel]] = {
    "imu": models.Imu, "status": models.Status, "log": models.Log,
}


class HeadError(Exception):
    """The device answered with `error`."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.details = details or {}


@dataclass
class PairingRequired:
    code_hint: str
    code_length: int
    expires_in_ms: int
    attempts_left: int


def parse_address(device: str) -> tuple[str, int]:
    """`host`, `host:port` or `[v6]:port` to (host, port)."""
    if device.startswith("["):
        host, _, rest = device[1:].partition("]")
        return host, int(rest.lstrip(":") or DEFAULT_PORT)
    if device.count(":") == 1:
        host, port = device.split(":")
        return host, int(port)
    return device, DEFAULT_PORT


class Head:
    """One connection to a head device.

    >>> head = await Head.connect("head-01.local")
    >>> if head.pairing: await head.pair("123456")
    >>> await head.face.set_emotion("curious", 0.7)
    >>> async for sample in head.subscribe("imu", 100): ...
    """

    def __init__(self, host: str, port: int, *, client: str, store: TokenStore | None,
                 token: str | None, auto_reconnect: bool):
        self.host = host
        self.port = port
        self.client = client
        self.store = store
        self.token = token if token is not None else (store.get(self.key) if store else None)
        self.auto_reconnect = auto_reconnect
        self.welcome: models.Welcome | None = None
        self.pairing: PairingRequired | None = None
        self.face = _Face(self)
        self.display = _Display(self)
        self.system = _System(self)
        self.mode = _Mode(self)
        self._ws: ClientConnection | None = None
        self._seq = itertools.count()
        self._ids = itertools.count(1)
        self._pending: dict[str, asyncio.Future] = {}
        self._handshake: asyncio.Future | None = None
        self._subs: dict[str, list[Subscription]] = {}
        self._reader: asyncio.Task | None = None
        self._closed = False
        self.connected = asyncio.Event()

    @property
    def key(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def paired(self) -> bool:
        return self.welcome is not None

    @classmethod
    async def connect(cls, host: str = "localhost", port: int = DEFAULT_PORT, *,
                      client: str = "openhead-python", token: str | None = None,
                      store: TokenStore | None = None, auto_reconnect: bool = True) -> Head:
        """Connect and say hello. Check `head.pairing` / `head.paired` afterwards."""
        head = cls(host, port, client=client, store=store or TokenStore(), token=token,
                   auto_reconnect=auto_reconnect)
        await head._open()
        return head

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    # --- connection -----------------------------------------------------------

    async def _open(self) -> None:
        self._ws = await connect(f"ws://{_host(self.host)}:{self.port}", max_size=8 * 1024 * 1024)
        self._seq = itertools.count()
        self._reader = asyncio.create_task(self._read(self._ws))
        reply = await self._hello()
        if isinstance(reply, models.Welcome):
            self._welcomed(reply)
        elif isinstance(reply, models.PairRequired):
            self.pairing = PairingRequired(reply.code_hint, reply.code_length,
                                           reply.expires_in_ms, reply.attempts_left)

    async def _hello(self) -> BaseModel:
        fields: dict[str, Any] = {"client": self.client, "protocol_version": PROTOCOL_VERSION}
        if self.token:
            fields["token"] = self.token
        return await self._exchange("hello", fields)

    async def _exchange(self, type_: str, fields: dict) -> BaseModel:
        self._handshake = asyncio.get_running_loop().create_future()
        await self._send(type_, fields)
        reply = await asyncio.wait_for(self._handshake, 10)
        if isinstance(reply, models.Error):
            raise HeadError(reply.code, reply.message, reply.details)
        return reply

    def _welcomed(self, welcome: models.Welcome) -> None:
        self.welcome = welcome
        self.pairing = None
        self.token = welcome.token
        if self.store:
            self.store.set(self.key, welcome.token, welcome.device.name)
        self.connected.set()

    async def pair(self, code: str) -> models.Welcome:
        """Send the code shown on the device; stores the token on success."""
        reply = await self._exchange("pair", {"code": code})
        assert isinstance(reply, models.Welcome)
        self._welcomed(reply)
        return reply

    async def close(self) -> None:
        self._closed = True
        if self._ws:
            await self._ws.close()
        if self._reader:
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader

    async def _send(self, type_: str, fields: dict) -> None:
        if self._ws is None:
            raise ConnectionError("not connected")
        msg = {"type": type_, "ts": now_ms(), "seq": next(self._seq), **fields}
        await self._ws.send(json.dumps(msg))

    async def _read(self, ws: ClientConnection) -> None:
        try:
            async for raw in ws:
                self._dispatch(json.loads(raw))
        except ConnectionClosed:
            pass
        finally:
            self.connected.clear()
            error = ConnectionError("connection to head lost")
            for fut in [*self._pending.values(), self._handshake]:
                if fut and not fut.done():
                    fut.set_exception(error)
            self._pending.clear()
            if not self._closed and self.auto_reconnect and self.welcome:
                asyncio.create_task(self._reconnect())
            elif self._closed or not self.auto_reconnect:
                for subs in self._subs.values():
                    for sub in subs:
                        sub._queue.put_nowait(None)

    def _dispatch(self, data: dict) -> None:
        type_ = data.get("type")
        try:
            msg = parse_message(data)
        except Exception:  # noqa: BLE001 - never let one bad message stop the reader
            log.warning("ignoring unparseable %s message", type_)
            return
        if type_ in ("ack", "error") and data.get("id") in self._pending:
            fut = self._pending.pop(data["id"])
            if not fut.done():
                if type_ == "ack":
                    fut.set_result(data.get("result") or {})
                else:
                    fut.set_exception(HeadError(data["code"], data["message"], data.get("details")))
        elif type_ in ("welcome", "pair_required", "error"):
            if self._handshake and not self._handshake.done():
                self._handshake.set_result(msg)
            elif type_ == "error":
                log.warning("device error: %s %s", data.get("code"), data.get("message"))
        elif type_ in TOPIC_MODELS:
            for sub in self._subs.get(type_, []):
                sub._queue.put_nowait(msg)

    async def _reconnect(self) -> None:
        delay = 0.5
        while not self._closed:
            await asyncio.sleep(delay + random.uniform(0, delay / 2))
            try:
                await self._open()
            except (TimeoutError, OSError, ConnectionClosed, HeadError) as exc:
                log.info("reconnect to %s failed: %s", self.key, exc)
                delay = min(delay * 2, 10)
                continue
            if not self.paired:
                log.warning("reconnected to %s but the token was rejected", self.key)
                return
            for subs in self._subs.values():
                if subs:
                    await subs[-1]._request()
            log.info("reconnected to %s", self.key)
            return

    # --- commands -------------------------------------------------------------

    async def command(self, type_: str, **params: Any) -> dict:
        """Send a command and return its `ack.result` (empty dict if none)."""
        msg_id = f"c{next(self._ids)}"
        fut = asyncio.get_running_loop().create_future()
        self._pending[msg_id] = fut
        try:
            await self._send(type_, {"id": msg_id, **_drop_none(params)})
            return await asyncio.wait_for(fut, 30)
        finally:
            self._pending.pop(msg_id, None)

    async def stream(self, type_: str, **fields: Any) -> None:
        """Fire-and-forget stream message (e.g. `face.envelope`)."""
        await self._send(type_, fields)

    def subscribe(self, topic: str, rate_hz: float | None = None,
                  fields: list[str] | None = None) -> Subscription:
        """Async iterator (and async context manager) over a topic's messages."""
        return Subscription(self, topic, rate_hz, fields)


class Subscription:
    def __init__(self, head: Head, topic: str, rate_hz: float | None, fields: list[str] | None):
        self.head = head
        self.topic = topic
        self.requested = rate_hz
        self.fields = fields
        self.rate_hz: float | None = None
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._started = False

    async def _request(self) -> None:
        result = await self.head.command("subscribe", topic=self.topic, rate_hz=self.requested,
                                         fields=self.fields)
        self.rate_hz = result.get("rate_hz")

    async def start(self) -> Subscription:
        if not self._started:
            self._started = True
            self.head._subs.setdefault(self.topic, []).append(self)
            await self._request()
        return self

    async def close(self) -> None:
        subs = self.head._subs.get(self.topic, [])
        if self in subs:
            subs.remove(self)
            if not subs and self.head.connected.is_set():
                with contextlib.suppress(HeadError, ConnectionError):
                    await self.head.command("unsubscribe", topic=self.topic)
        self._queue.put_nowait(None)

    async def __aenter__(self) -> Self:
        return await self.start()

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    def __aiter__(self) -> Subscription:
        return self

    async def __anext__(self) -> Any:
        await self.start()
        item = await self._queue.get()
        if item is None:
            raise StopAsyncIteration
        return item


class _Face:
    def __init__(self, head: Head):
        self._h = head

    async def set_theme(self, name: str, transition_ms: int | None = None) -> None:
        await self._h.command("face.set_theme", name=name, transition_ms=transition_ms)

    async def set_emotion(self, name: str, intensity: float = 1.0, *, duration_ms: int | None = None,
                          blend: str = "replace") -> None:
        await self._h.command("face.set_emotion", name=name, intensity=intensity,
                              duration_ms=duration_ms, blend=blend)

    async def look_at(self, x: float = 0, y: float = 0, *, frame: str = "screen",
                      duration_ms: int | None = None) -> None:
        coords = {"x": x, "y": y} if frame == "screen" else {"yaw": x, "pitch": y}
        await self._h.command("face.look_at", frame=frame, duration_ms=duration_ms, **coords)

    async def blink(self) -> None:
        await self._h.command("face.blink")

    async def envelope(self, level: float) -> None:
        await self._h.stream("face.envelope", level=max(0.0, min(1.0, level)))

    async def list(self) -> models.FaceListResult:
        return models.FaceListResult.model_validate(await self._h.command("face.list"))


class _Display:
    def __init__(self, head: Head):
        self._h = head

    async def show_image(self, source: str | bytes, *, overlay: str = "none",
                         duration_ms: int | None = None) -> None:
        """`source` is an http(s) URL, a data: URI, or PNG/JPEG bytes (sent inline)."""
        if isinstance(source, bytes):
            mime = "image/png" if source.startswith(b"\x89PNG") else "image/jpeg"
            source = f"data:{mime};base64,{base64.b64encode(source).decode()}"
        await self._h.command("display.show", content="image", source=source, overlay=overlay,
                              duration_ms=duration_ms)

    async def show_web(self, url: str, *, overlay: str = "none",
                       duration_ms: int | None = None) -> None:
        await self._h.command("display.show", content="web", source=url, overlay=overlay,
                              duration_ms=duration_ms)

    async def show_face(self) -> None:
        await self._h.command("display.show", content="face")

    async def clear(self) -> None:
        await self._h.command("display.clear")


class _System:
    def __init__(self, head: Head):
        self._h = head

    async def status(self) -> models.StatusPayload:
        return models.StatusPayload.model_validate(await self._h.command("system.status"))

    async def screenshot(self, scale: float | None = None, *, inline: bool = False) -> bytes:
        """PNG bytes of what is on screen (dev mode)."""
        result = await self._h.command("system.screenshot", scale=scale,
                                       delivery="inline" if inline else None)
        if "png_base64" in result:
            return base64.b64decode(result["png_base64"])
        request = urllib.request.Request(result["url"],
                                         headers={"Authorization": f"Bearer {self._h.token}"})

        def fetch() -> bytes:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.read()

        # The URL stays valid for 60 s; the device's HTTP port occasionally drops a connection.
        for attempt in range(3):
            try:
                return await asyncio.to_thread(fetch)
            except OSError as exc:  # URLError and timeouts
                if attempt == 2:
                    raise
                log.warning("screenshot fetch failed (%s); retrying", exc)
                await asyncio.sleep(0.5 * (attempt + 1))
        raise AssertionError("unreachable")

    async def logs(self, n: int = 100, level: str | None = None) -> list[models.LogPayload]:
        result = await self._h.command("system.logs", n=n, level=level)
        return [models.LogPayload.model_validate(e) for e in result["entries"]]

    async def diagnostics(self) -> models.SystemDiagnosticsResult:
        return models.SystemDiagnosticsResult.model_validate(
            await self._h.command("system.diagnostics"))

    async def settings(self) -> dict:
        return (await self._h.command("system.settings", action="get"))["settings"]

    async def set_setting(self, key: str, value: Any) -> dict:
        return (await self._h.command("system.settings", action="set", key=key,
                                      value=value))["settings"]


class _Mode:
    def __init__(self, head: Head):
        self._h = head

    async def get(self) -> str:
        return (await self._h.command("mode.get"))["mode"]

    async def set(self, mode: str) -> None:
        await self._h.command("mode.set", mode=mode)


def _drop_none(params: dict) -> dict:
    return {k: v for k, v in params.items() if v is not None}


def _host(host: str) -> str:
    return f"[{host}]" if ":" in host and not host.startswith("[") else host
