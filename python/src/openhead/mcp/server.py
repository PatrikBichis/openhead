"""MCP server: the head as tools and resources for LLM agents.

A thin adapter over `openhead.client` (no second protocol implementation). It is a client
like any other: it needs its own pairing token, and it can do nothing the WebSocket API
cannot. High-rate streams (IMU, envelope) are deliberately not exposed.
"""

from __future__ import annotations

import asyncio
import contextlib
import hmac
import json
import logging
import sys
import time
from collections import deque
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import Image, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .. import __version__
from ..client import Head, HeadError, MediaServer, resolve_device
from ..tokens import TokenStore

log = logging.getLogger("openhead.mcp")

INSTRUCTIONS = """\
Controls an OpenHead robot head: a phone showing an expressive face.
- Expressions: set_emotion with one of the names from list_themes (28 shared names such as
  happy, curious, confused, shocked, worried, laughing; themes may add extras). Use
  intensity 0-1, duration_ms for a short reaction, blend="add" to layer one on another.
- Look: look_at with x, y in [-1, 1] on the screen (+x right, +y up).
- Show things: show_image and show_video (URL or local file), show_web (URL), show_camera
  (what the head sees, with a HUD), show_face to go back.
- Sense people and place: set_mode capture (camera, several faces) or sensing (ARKit pose and
  one face); get_faces, get_pose; look_at_face makes the eyes follow someone. get_location
  (GPS) and get_environment (air pressure, magnetic field, compass) work in any mode. subtitle writes text on screen (append to stream an answer; mouth=True to "speak").
- Talk (0.4): say speaks with the head's own voice, the mouth moving and the words as a subtitle.
  Put cues in square brackets where they belong, so the face acts as it speaks: an expression
  ([happy], [sad 0.5], [surprised], [focused] for serious ...), an action ([laugh], [sigh],
  [pause 0.5], [blink]) or a gesture for a body ([nod], [shake], [tilt]). E.g. "[happy] Why did
  the robot go on holiday? [pause 0.5] It needed to recharge! [laugh]". Then call listen to hear
  the answer: it returns what the person said (the face looks attentive, then thoughtful).
  A conversation is a loop: say, listen, say, listen.
- Check your work: take_screenshot shows what is on screen; tail_logs and get_status explain
  what happened; wait_for blocks until a status or log condition holds.
- Screenshots, logs and diagnostics need dev mode on the device.
- If a tool says the head is not paired, ask the user for the code shown on the device and
  call pair(code)."""

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True,
                            openWorldHint=False)
CHANGES_FACE = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True,
                               openWorldHint=False)
MAX_INLINE_IMAGE = 1_000_000


class HeadLink:
    """Lazily connected head plus cached status, themes and log lines for resources."""

    def __init__(self, device: str, *, client: str = "openhead-mcp",
                 store: TokenStore | None = None):
        self.device = device
        self.client = client
        self.store = store or TokenStore()
        self.head: Head | None = None
        self.status: dict | None = None
        self.logs: deque[dict] = deque(maxlen=500)
        self._lock = asyncio.Lock()
        self._tasks: list[asyncio.Task] = []
        self.media: MediaServer | None = None
        self.heard: deque[str] = deque(maxlen=5)   # what was said and not yet returned by listen
        self.heard_event = asyncio.Event()
        self.listening = False

    async def connect(self) -> Head:
        async with self._lock:
            if self.head is None:  # a paired head reconnects by itself
                host, port = await resolve_device(self.device)
                self.head = await Head.connect(host, port, client=self.client, store=self.store)
                if self.head.paired:
                    self._start_cache()
            return self.head

    async def get(self) -> Head:
        """A paired head, or a ToolError that tells the agent what to do."""
        try:
            head = await self.connect()
        except (OSError, ConnectionError, TimeoutError) as exc:
            raise ToolError(f"cannot reach the head at {self.device}: {exc}") from exc
        if not head.paired:
            hint = head.pairing.code_hint if head.pairing else "a code is shown on the device"
            raise ToolError(f"not paired with {head.key} ({hint}). Ask the user for the code and "
                            "call pair(code).")
        return head

    def _start_cache(self) -> None:
        async def follow(topic: str, rate: float | None) -> None:
            with contextlib.suppress(Exception):
                async for msg in self.head.subscribe(topic, rate):
                    data = msg.model_dump(exclude_none=True, exclude={"type", "seq"})
                    if topic == "status":
                        self.status = data
                    elif topic == "speech":
                        if data.get("event") == "heard" and data.get("text"):
                            self.heard.append(data["text"])
                            self.heard_event.set()
                    else:
                        self.logs.append(data)

        # speech: kept open so nothing said between two listen calls is lost (absent before 0.4)
        self._tasks = [asyncio.create_task(follow("status", 1)),
                       asyncio.create_task(follow("log", None)),
                       asyncio.create_task(follow("speech", None))]

    async def close(self) -> None:
        for task in self._tasks:
            task.cancel()
        if self.media:
            self.media.close()
        if self.head:
            await self.head.close()

    async def serve_file(self, path: Path) -> str:
        """A URL on this machine for a local file the head should fetch (large image, video)."""
        head = await self.get()
        if self.media is None:
            self.media = MediaServer().start()
        return self.media.url_for(path, head)


def build_server(link: HeadLink) -> MCPServer:
    mcp = MCPServer("openhead", title="OpenHead", instructions=INSTRUCTIONS, version=__version__)

    async def call(coro_fn: Any, *args: Any, **kwargs: Any) -> Any:
        head = await link.get()
        try:
            return await coro_fn(head, *args, **kwargs)
        except HeadError as exc:
            raise ToolError(f"{exc.code}: {exc.message}") from exc
        except (ConnectionError, TimeoutError) as exc:
            raise ToolError(f"lost the connection to the head: {exc}") from exc

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=True))
    async def pair(code: str) -> str:
        """Pair with the head using the code shown on its screen (ask the user for it)."""
        try:
            head = await link.connect()
            if head.paired:
                return f"already paired with {head.welcome.device.name}"
            welcome = await head.pair(code)
        except HeadError as exc:
            raise ToolError(f"{exc.code}: {exc.message}") from exc
        link._start_cache()
        return f"paired with {welcome.device.name}; token saved"

    @mcp.tool(annotations=READ_ONLY)
    async def list_themes() -> dict:
        """Installed themes with their expression names (shared and theme extras)."""
        result = await call(lambda h: h.face.list())
        return result.model_dump()

    @mcp.tool(annotations=CHANGES_FACE)
    async def set_theme(name: str) -> str:
        """Switch the face to an installed theme (see list_themes)."""
        await call(lambda h: h.face.set_theme(name))
        return f"theme={name}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def set_emotion(name: str, intensity: float = 1.0, duration_ms: int | None = None,
                          blend: Literal["replace", "add"] = "replace") -> str:
        """Show an emotion, independent of speech. duration_ms returns to rest afterwards;
        blend="add" layers it on the current one. Unknown names fall back to neutral."""
        await call(lambda h: h.face.set_emotion(name, intensity, duration_ms=duration_ms,
                                                blend=blend))
        return f"emotion={name} intensity={intensity}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def look_at(x: float, y: float, frame: Literal["screen", "head"] = "screen",
                      duration_ms: int | None = None) -> str:
        """Point the gaze. screen: x, y in [-1, 1] (+x right, +y up).
        head: x = yaw, y = pitch in degrees (+yaw is the head's left)."""
        await call(lambda h: h.face.look_at(x, y, frame=frame, duration_ms=duration_ms))
        return f"looking at {frame} ({x}, {y})"

    @mcp.tool(annotations=CHANGES_FACE)
    async def look_at_face(face_id: int | None = None, duration_ms: int | None = None) -> str:
        """Make the eyes follow a person the camera sees (default: the locked, largest face)
        until the next look_at. Needs mode capture or sensing (show_camera sets capture)."""
        await call(lambda h: h.face.look_at_face(face_id, duration_ms=duration_ms))
        return f"following face {face_id if face_id is not None else '(locked)'}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_camera(hud: str = "hunter", overlay: Literal["none", "face-corner"] = "none",
                          duration_ms: int | None = None) -> str:
        """Show what the head's front camera sees, with a HUD theme drawn over it (boxes around
        faces, the locked target, text). HUDs: hunter, camcorder, boot, or none. Switches the
        head to mode capture."""
        await call(lambda h: h.display.show_camera(hud, overlay=overlay, duration_ms=duration_ms))
        return f"camera view with HUD {hud}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def set_hud(values: dict[str, Any] | None = None, lines: list[str] | None = None,
                      at: Literal["top-left", "top-right", "bottom-left", "bottom-right", "left"] = "bottom-left",
                      widgets: list[Literal["compass", "horizon", "battery"]] | None = None,
                      clear: bool = False) -> str:
        """Put your own information on the camera HUD. values: names for templates, e.g.
        {"speed": 0.4, "task": "DELIVER CUP"}; lines: text lines that may use them and the built-in
        values ({battery} {thermal} {heading} {pitch} {roll} {faces} {target} {mode}), e.g.
        ["TASK {task}", "SPEED {speed} M/S"]; widgets: compass, horizon, battery. clear removes
        what was added."""
        await call(lambda h: h.display.hud(values, blocks=[{"at": at, "lines": lines}] if lines else None,
                                           widgets=[{"type": w} for w in widgets] if widgets else None,
                                           clear=clear))
        return "HUD cleared" if clear else "HUD updated"

    @mcp.tool(annotations=CHANGES_FACE)
    async def set_mode(mode: Literal["idle", "capture", "sensing"]) -> str:
        """Who owns the cameras. capture: front camera, several faces with boxes. sensing: ARKit
        pose (position and orientation in the world) and one face. idle: no camera."""
        await call(lambda h: h.mode.set(mode))
        return f"mode {mode}"

    @mcp.tool(annotations=READ_ONLY)
    async def get_faces(timeout_s: float = 3.0) -> dict:
        """The people the head sees now: id, bearing and elevation in degrees (+ is the head's
        left / up), size (bigger is closer), box on screen. Needs mode capture or sensing."""
        head = await link.get()
        try:
            mode = await head.mode.get()
        except HeadError as exc:
            raise ToolError(f"{exc.code}: {exc.message}") from exc
        if mode == "idle":
            raise ToolError("the cameras are off: set_mode capture or sensing first")
        source = {"capture": "vision", "sensing": "arkit"}.get(mode)

        async def latest() -> dict | None:
            # Right after a mode change the first samples may be empty or still carry the old
            # camera's label: skip those from the wrong source, and give the camera a moment
            # to find someone before answering "nobody".
            seen = None
            settle = time.monotonic() + min(1.0, timeout_s / 2)
            async with head.subscribe("faces", 15) as sub:
                async for msg in sub:
                    if source and msg.source not in (source, "sim"):
                        continue
                    seen = msg.model_dump(exclude_none=True, exclude={"type", "seq"})
                    if msg.faces or time.monotonic() > settle:
                        return seen
            return seen

        try:
            result = await asyncio.wait_for(latest(), timeout_s)
        except TimeoutError as exc:
            raise ToolError("no faces data: is the mode capture or sensing? (set_mode)") from exc
        if result is None:
            raise ToolError("subscription ended")
        return result

    @mcp.tool(annotations=READ_ONLY)
    async def get_pose(timeout_s: float = 3.0) -> dict:
        """Where the head is (ARKit): position in metres and orientation in the world frame,
        tracking state. Needs mode sensing."""
        head = await link.get()

        async def first() -> dict:
            async with head.subscribe("pose", 30) as sub:
                async for msg in sub:
                    return msg.model_dump(exclude_none=True, exclude={"type", "seq"})
            raise ToolError("subscription ended")

        try:
            return await asyncio.wait_for(first(), timeout_s)
        except TimeoutError as exc:
            raise ToolError("no pose: is the mode sensing? (set_mode)") from exc

    async def first_sample(topic: str, rate: float, timeout_s: float, hint: str) -> dict:
        head = await link.get()

        async def first() -> dict:
            async with head.subscribe(topic, rate) as sub:
                async for msg in sub:
                    return msg.model_dump(exclude_none=True, exclude={"type", "seq"})
            raise ToolError("subscription ended")

        try:
            return await asyncio.wait_for(first(), timeout_s)
        except TimeoutError as exc:
            raise ToolError(hint) from exc

    @mcp.tool(annotations=READ_ONLY)
    async def get_location(timeout_s: float = 10.0) -> dict:
        """Where the head is on Earth: lat, lon (degrees), alt_m, h_accuracy_m, speed and course.
        The first call asks the user on the device to allow location access."""
        return await first_sample("gps", 1, timeout_s,
                                  "no location yet: allow location access on the device, or wait for a fix")

    @mcp.tool(annotations=READ_ONLY)
    async def get_environment(timeout_s: float = 3.0) -> dict:
        """Air pressure (kPa) and altitude change, raw magnetic field (uT) and compass heading
        (degrees from north) from the head's barometer, magnetometer and compass."""
        return await first_sample("env", 10, timeout_s, "no environment data: the device may lack these sensors")

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_image(url_or_path: str,
                         overlay: Literal["none", "face-corner"] = "none",
                         duration_ms: int | None = None) -> str:
        """Show an image: an http(s) URL, or a PNG, JPEG, GIF, WebP or SVG file on this machine.
        overlay="face-corner" keeps the face running in a corner."""
        source: str | bytes = url_or_path
        if not url_or_path.startswith(("http://", "https://", "data:")):
            path = Path(url_or_path).expanduser()
            if not path.is_file():
                raise ToolError(f"no such file: {path}")
            data = path.read_bytes()
            source = data if len(data) <= MAX_INLINE_IMAGE else await link.serve_file(path)
        await call(lambda h: h.display.show_image(source, overlay=overlay,
                                                  duration_ms=duration_ms))
        return f"showing {url_or_path}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_video(url_or_path: str, overlay: Literal["none", "face-corner"] = "none",
                         loop: bool = False, muted: bool = False,
                         duration_ms: int | None = None) -> str:
        """Play a video: an http(s) URL or a file on this machine (H.264 MP4 plays everywhere).
        Without loop the face comes back when it ends."""
        url = url_or_path
        if not url.startswith(("http://", "https://")):
            path = Path(url_or_path).expanduser()
            if not path.is_file():
                raise ToolError(f"no such file: {path}")
            url = await link.serve_file(path)
        await call(lambda h: h.display.show_video(url, overlay=overlay, loop=loop, muted=muted,
                                                  duration_ms=duration_ms))
        return f"playing {url_or_path}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def subtitle(text: str = "", mode: Literal["replace", "append", "clear"] = "replace",
                       position: Literal["bottom", "top"] = "bottom",
                       duration_ms: int | None = None, mouth: bool = False) -> str:
        """Show text on top of the screen, e.g. an answer when the robot has no speaker.
        mode="append" adds to the text (stream an answer in pieces), "clear" removes it.
        mouth=True moves the mouth with the text as if speaking."""
        await call(lambda h: h.display.subtitle(text, mode=mode, position=position,
                                                duration_ms=duration_ms, mouth=mouth))
        return "subtitle cleared" if mode == "clear" else f"subtitle ({mode}): {text}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def say(text: str, wait: bool = True, voice: str | None = None, rate: float | None = None) -> str:
        """Speak with the head's own voice: the mouth moves with the audio and the words show as
        a subtitle. Cues in square brackets act at that point: an expression from list_themes
        ([happy], [sad 0.5], [surprised], [focused] for serious), an action ([laugh], [sigh],
        [pause 0.5], [blink]) or a body gesture ([nod], [shake], [tilt]). wait=True returns when it
        has finished speaking. voice: a language such as en-US (default) or a voice identifier;
        rate: 0.5-2 relative to normal."""
        from ..speech import parse, spoken_text
        try:
            segments = parse(text)
        except ValueError as exc:
            raise ToolError(str(exc)) from exc
        head = await link.get()
        words = spoken_text(segments)
        try:
            if not wait:
                uid = await head.speech.say(segments, voice=voice, rate=rate)
                return f"speaking ({uid}): {words}"
            async with head.subscribe("speech") as sub:
                uid = await head.speech.say(segments, voice=voice, rate=rate)

                async def done() -> bool:
                    async for msg in sub:
                        if msg.event == "say_end" and msg.utterance_id == uid:
                            return bool(msg.interrupted)
                    return True

                interrupted = await asyncio.wait_for(done(), len(words) / 6 + 15)
        except HeadError as exc:
            raise ToolError(f"{exc.code}: {exc.message}") from exc
        except TimeoutError:
            return f"still speaking ({uid}): {words}"
        return f"{'interrupted' if interrupted else 'said'}: {words}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def listen(timeout_s: float = 30.0, locale: str = "en-US") -> str:
        """What the person says next, as text (speech to text on the head). Starts listening the
        first time (the device asks for microphone permission once). Returns what was said
        since the last call if anything is waiting, else waits up to timeout_s for someone to
        speak and pause. Returns an empty string if nobody spoke."""
        head = await link.get()
        if not link.listening:
            try:
                await head.speech.listen(True, locale=locale)
            except HeadError as exc:
                raise ToolError(f"{exc.code}: {exc.message}") from exc
            link.listening = True
        if not link.heard:
            link.heard_event.clear()
            try:
                await asyncio.wait_for(link.heard_event.wait(), timeout_s)
            except TimeoutError:
                return ""
        text = " ".join(link.heard)
        link.heard.clear()
        return text

    @mcp.tool(annotations=CHANGES_FACE)
    async def stop_speaking() -> str:
        """Stop speaking now (drops anything queued)."""
        await call(lambda h: h.speech.stop())
        return "stopped"

    @mcp.tool(annotations=CHANGES_FACE)
    async def stop_listening() -> str:
        """Switch the microphone off."""
        await call(lambda h: h.speech.listen(False))
        link.listening = False
        link.heard.clear()
        return "not listening"

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_web(url: str, overlay: Literal["none", "face-corner"] = "none",
                       duration_ms: int | None = None) -> str:
        """Show a web page (http/https URL) full screen."""
        await call(lambda h: h.display.show_web(url, overlay=overlay, duration_ms=duration_ms))
        return f"showing {url}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_face() -> str:
        """Remove any image, video or web page and show the face full screen."""
        await call(lambda h: h.display.show_face())
        return "showing the face"

    @mcp.tool(annotations=READ_ONLY)
    async def take_screenshot(scale: float = 0.5) -> Image:
        """What is on the head's screen right now, as an image (dev mode)."""
        png = await call(lambda h: h.system.screenshot(scale))
        return Image(data=png, format="png")

    @mcp.tool(annotations=READ_ONLY)
    async def tail_logs(n: int = 50, level: Literal["debug", "info", "notice", "warning",
                                                     "error", "fault"] | None = None) -> str:
        """The head's most recent log lines (dev mode). Every received command is logged."""
        entries = await call(lambda h: h.system.logs(n, level))
        return "\n".join(
            f"{time.strftime('%H:%M:%S', time.localtime(e.time_ms / 1000))} {e.level:<7} "
            f"{e.subsystem:<9} {e.message}" for e in entries) or "(no log lines)"

    @mcp.tool(annotations=READ_ONLY)
    async def get_status() -> dict:
        """Battery, thermal state, what is on screen, theme, emotion, mode, clients."""
        return (await call(lambda h: h.system.status())).model_dump(exclude_none=True)

    @mcp.tool(annotations=READ_ONLY)
    async def get_diagnostics() -> dict:
        """Uptime, memory, frame rate, permissions, ARKit support, last crash (dev mode)."""
        return (await call(lambda h: h.system.diagnostics())).model_dump(exclude_none=True)

    @mcp.tool(annotations=READ_ONLY)
    async def wait_for(topic: Literal["status", "log"], predicate: dict[str, Any],
                       timeout_s: float = 10.0) -> dict:
        """Wait until a condition holds, then return the matching message.
        status: predicate is field values, e.g. {"theme": "halloween", "view": "face"}.
        log: predicate may hold "contains", "level" (minimum) and "subsystem"."""
        head = await link.get()
        if topic == "status":
            status = (await call(lambda h: h.system.status())).model_dump(exclude_none=True)
            if _status_matches(status, predicate):
                return status
        levels = ["debug", "info", "notice", "warning", "error", "fault"]

        async def first_match() -> dict:
            async with head.subscribe(topic, 1 if topic == "status" else None) as sub:
                async for msg in sub:
                    data = msg.model_dump(exclude_none=True, exclude={"type", "seq"})
                    if topic == "status" and _status_matches(data, predicate):
                        return data
                    if topic == "log" and (
                        predicate.get("contains", "") in data.get("message", "")
                        and levels.index(data.get("level", "debug"))
                        >= levels.index(predicate.get("level", "debug"))
                        and predicate.get("subsystem", data.get("subsystem"))
                        == data.get("subsystem")
                    ):
                        return data
            raise ToolError("subscription ended")

        try:
            return await asyncio.wait_for(first_match(), timeout_s)
        except TimeoutError as exc:
            raise ToolError(f"no {topic} matching {json.dumps(predicate)} within "
                            f"{timeout_s} s") from exc

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, idempotentHint=False))
    async def run_scenario(path: str, compare: bool = False) -> list:
        """Run a YAML scenario file (see scenarios/) and return its report and screenshots.
        compare=True checks screenshots against scenarios/golden/ (simulator only)."""
        from ..scenario import run_scenario as run

        file = Path(path).expanduser()
        if not file.is_file():
            raise ToolError(f"no such scenario: {file}")
        head = await link.get()
        report = await run(head, file, golden_dir=file.parent / "golden" if compare else None)
        shots = [s.artifact for s in report.steps if s.artifact][:4]
        return [report.text(), *(Image(path=p) for p in shots)]

    @mcp.resource("openhead://status", mime_type="application/json",
                  description="Latest status of the head (1 Hz cache)")
    async def status_resource() -> str:
        if link.status is None:
            link.status = (await call(lambda h: h.system.status())).model_dump(exclude_none=True)
        return json.dumps(link.status)

    @mcp.resource("openhead://themes", mime_type="application/json",
                  description="Installed themes and their expressions")
    async def themes_resource() -> str:
        return json.dumps((await call(lambda h: h.face.list())).model_dump())

    @mcp.resource("openhead://logs", mime_type="text/plain",
                  description="Log lines received since the MCP server connected")
    async def logs_resource() -> str:
        await link.get()
        return "\n".join(f"{e.get('level', '')} {e.get('subsystem', '')} {e.get('message', '')}"
                         for e in link.logs)

    return mcp


def _status_matches(status: dict, predicate: dict) -> bool:
    return all(status.get(k) == v for k, v in predicate.items())


async def serve_stdio(device: str, client: str) -> None:
    link = HeadLink(device, client=client)
    try:
        await build_server(link).run_stdio_async()
    finally:
        await link.close()


LOOPBACK = {"127.0.0.1", "::1", "localhost"}


class BearerAuth:
    """ASGI wrapper: every HTTP request needs `Authorization: Bearer <token>`."""

    def __init__(self, app, token: str):
        self.app = app
        self.expected = f"Bearer {token}".encode()

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http":
            given = dict(scope["headers"]).get(b"authorization", b"")
            if not hmac.compare_digest(given, self.expected):
                await send({"type": "http.response.start", "status": 401,
                            "headers": [(b"content-type", b"text/plain"), (b"www-authenticate", b"Bearer")]})
                await send({"type": "http.response.body", "body": b"missing or wrong bearer token"})
                return
        await self.app(scope, receive, send)


async def serve_http(device: str, client: str, host: str, port: int, token: str | None) -> None:
    """Streamable HTTP at http://host:port/mcp, for agents on another machine. Anyone who reaches
    it controls the head, so a non-loopback address needs a bearer token."""
    import uvicorn
    from mcp.server.transport_security import TransportSecuritySettings

    if host not in LOOPBACK and not token:
        raise SystemExit("--http on a network address needs --token (or OPENHEAD_MCP_TOKEN)")
    link = HeadLink(device, client=client)
    # Loopback keeps the SDK's DNS-rebinding check; on the network the token protects the server.
    security = None if host in LOOPBACK else TransportSecuritySettings(enable_dns_rebinding_protection=False)
    app = build_server(link).streamable_http_app(host=host, transport_security=security)
    if token:
        app = BearerAuth(app, token)
    server = uvicorn.Server(uvicorn.Config(app, host=host, port=port, log_level="warning"))
    print(f"MCP over HTTP: http://{host}:{port}/mcp" + (" (bearer token required)" if token else ""),
          file=sys.stderr)
    try:
        await server.serve()
    finally:
        await link.close()
