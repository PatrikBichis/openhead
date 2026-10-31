"""MCP server: the head as tools and resources for LLM agents.

A thin adapter over `openhead.client` (no second protocol implementation). It is a client
like any other: it needs its own pairing token, and it can do nothing the WebSocket API
cannot. High-rate streams (IMU, envelope) are deliberately not exposed.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import secrets
import socket
import time
from collections import deque
from pathlib import Path
from typing import Any, Literal

from mcp.server.mcpserver import Image, MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .. import __version__
from ..client import Head, HeadError, resolve_device
from ..tokens import TokenStore

log = logging.getLogger("openhead.mcp")

INSTRUCTIONS = """\
Controls an OpenHead robot head: a phone showing an expressive face.
- Expressions: set_emotion with one of the names from list_themes (28 shared names such as
  happy, curious, confused, shocked, worried, laughing; themes may add extras). Use
  intensity 0-1, duration_ms for a short reaction, blend="add" to layer one on another.
- Look: look_at with x, y in [-1, 1] on the screen (+x right, +y up).
- Show things: show_image (URL or local file), show_web (URL), show_face to go back.
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
        self._served: list[asyncio.Server] = []

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
                    else:
                        self.logs.append(data)

        self._tasks = [asyncio.create_task(follow("status", 1)),
                       asyncio.create_task(follow("log", None))]

    async def close(self) -> None:
        for task in self._tasks:
            task.cancel()
        for server in self._served:
            server.close()
        if self.head:
            await self.head.close()

    async def serve_file(self, data: bytes, suffix: str) -> str:
        """Serve bytes once over HTTP for 60 s so the head can fetch a large local file."""
        name = f"{secrets.token_urlsafe(12)}{suffix}"
        head = await self.get()

        async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            line = (await reader.readline()).decode("latin-1").split()
            while (await reader.readline()) not in (b"\r\n", b"\n", b""):
                pass
            ok = len(line) > 1 and line[1] == f"/{name}"
            body = data if ok else b"not found"
            ctype = "image/png" if suffix == ".png" else "image/jpeg" if ok else "text/plain"
            writer.write(f"HTTP/1.1 {'200 OK' if ok else '404 Not Found'}\r\nContent-Type: {ctype}"
                         f"\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
                         .encode("latin-1") + body)
            await writer.drain()
            writer.close()

        server = await asyncio.start_server(handle, "0.0.0.0", 0)
        self._served.append(server)
        asyncio.get_running_loop().call_later(60, server.close)
        port = server.sockets[0].getsockname()[1]
        return f"http://{_route_ip(head.host)}:{port}/{name}"


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
    async def show_image(url_or_path: str,
                         overlay: Literal["none", "face-corner"] = "none",
                         duration_ms: int | None = None) -> str:
        """Show an image: an http(s) URL, or a PNG/JPEG file on this machine.
        overlay="face-corner" keeps the face running in a corner."""
        source: str | bytes = url_or_path
        if not url_or_path.startswith(("http://", "https://", "data:")):
            path = Path(url_or_path).expanduser()
            if not path.is_file():
                raise ToolError(f"no such file: {path}")
            data = path.read_bytes()
            source = (data if len(data) <= MAX_INLINE_IMAGE
                      else await link.serve_file(data, path.suffix.lower()))
        await call(lambda h: h.display.show_image(source, overlay=overlay,
                                                  duration_ms=duration_ms))
        return f"showing {url_or_path}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_web(url: str, overlay: Literal["none", "face-corner"] = "none",
                       duration_ms: int | None = None) -> str:
        """Show a web page (http/https URL) full screen."""
        await call(lambda h: h.display.show_web(url, overlay=overlay, duration_ms=duration_ms))
        return f"showing {url}"

    @mcp.tool(annotations=CHANGES_FACE)
    async def show_face() -> str:
        """Remove any image or web page and show the face full screen."""
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


def _route_ip(host: str) -> str:
    """Our address on the route to the head, so it can fetch files we serve."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        try:
            sock.connect((socket.gethostbyname(host), 9))
            return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"


async def serve_stdio(device: str, client: str) -> None:
    link = HeadLink(device, client=client)
    try:
        await build_server(link).run_stdio_async()
    finally:
        await link.close()
