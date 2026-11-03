"""The cockpit's server: the page in `static/`, and a WebSocket bridge from the page to the head.

The page never sees the head's pairing token. It talks to this server only, over `/ws`, with a
key that is new every run and handed to the browser in the URL fragment; the server also checks
that the request comes from its own page (Origin equals Host) on a loopback name, so another web
page or a DNS-rebinding trick cannot drive the head.

Bridge messages (JSON, field `op`), page to server:
  command {id, type, params}   any protocol command; answered with result {id, ok, result|error}
  say {id, text}               speech.say with cues in brackets (`openhead.speech.parse`)
  subscribe {topic, rate_hz?, max_px?} / unsubscribe {topic}
Server to page: hello {device, capabilities, themes, protocol_version, dev_mode, head},
  link {connected}, topic {topic, data}, result {...}.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import secrets
from http import HTTPStatus
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit

from websockets.asyncio.server import ServerConnection, serve
from websockets.datastructures import Headers
from websockets.exceptions import ConnectionClosed
from websockets.http11 import Request, Response

from ..client import Head, HeadError, Subscription
from ..speech import parse

log = logging.getLogger("openhead.cockpit")

STATIC = Path(__file__).parent / "static"
TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".js": "text/javascript; charset=utf-8", ".png": "image/png", ".svg": "image/svg+xml"}
LOOPBACK = {"127.0.0.1", "localhost", "[::1]"}
# The page's own files and camera frames (data: URLs) only; scripts never inline.
CSP = "default-src 'self'; img-src 'self' data:; connect-src 'self'; style-src 'self'"


class Cockpit:
    def __init__(self, head: Head, *, host: str = "127.0.0.1", port: int = 8770):
        self.head = head
        self.host = host
        self.port = port
        self.key = secrets.token_urlsafe(18)
        self.pages: set[ServerConnection] = set()
        self._server: Any = None
        self._watch: asyncio.Task | None = None

    @property
    def url(self) -> str:
        host = "127.0.0.1" if self.host in ("0.0.0.0", "::") else self.host
        return f"http://{host}:{self.port}/#k={self.key}"

    async def start(self) -> None:
        self._server = await serve(self._page, self.host, self.port, process_request=self._http,
                                   max_size=1024 * 1024)
        self.port = self._server.sockets[0].getsockname()[1]
        self._watch = asyncio.create_task(self._watch_link())

    async def stop(self) -> None:
        if self._watch:
            self._watch.cancel()
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    async def serve_forever(self) -> None:
        await self.start()
        try:
            await asyncio.Future()
        finally:
            await self.stop()

    # --- HTTP: the static page, and the guard in front of /ws -----------------

    def _allowed_host(self, host: str) -> bool:
        name = host.rsplit(":", 1)[0] if not host.endswith("]") else host
        return name in LOOPBACK or (self.host not in ("127.0.0.1", "localhost") and name == self.host)

    def _http(self, connection: ServerConnection, request: Request) -> Response | None:
        url = urlsplit(request.path)
        host = request.headers.get("Host", "")
        if not self._allowed_host(host):
            return connection.respond(HTTPStatus.FORBIDDEN, "host not allowed\n")
        if url.path == "/ws":
            key = parse_qs(url.query).get("k", [""])[0]
            if request.headers.get("Origin") != f"http://{host}" or not secrets.compare_digest(key, self.key):
                return connection.respond(HTTPStatus.FORBIDDEN, "not this cockpit\n")
            return None
        name = "index.html" if url.path == "/" else url.path.lstrip("/")
        path = (STATIC / name).resolve()
        if path.parent != STATIC.resolve() or not path.is_file() or path.suffix not in TYPES:
            return connection.respond(HTTPStatus.NOT_FOUND, "not found\n")
        body = path.read_bytes()
        headers = Headers([("Content-Type", TYPES[path.suffix]), ("Content-Length", str(len(body))),
                           ("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff"),
                           ("Content-Security-Policy", CSP)])
        return Response(200, "OK", headers, body)

    # --- the bridge -------------------------------------------------------------

    def _hello(self) -> dict:
        w = self.head.welcome
        return {"op": "hello", "head": self.head.key, "connected": self.head.connected.is_set(),
                "device": w.device.model_dump(mode="json", exclude_none=True) if w else None,
                "capabilities": list(w.capabilities) if w else [],
                "themes": list(w.themes) if w else [],
                "protocol_version": w.protocol_version if w else None,
                "dev_mode": bool(w and w.dev_mode)}

    async def _page(self, ws: ServerConnection) -> None:
        self.pages.add(ws)
        subs: dict[str, tuple[Subscription, asyncio.Task]] = {}
        try:
            await ws.send(json.dumps(self._hello()))
            async for raw in ws:
                try:
                    msg = json.loads(raw)
                except ValueError:
                    continue
                match msg.get("op"):
                    case "command" | "say":
                        asyncio.create_task(self._command(ws, msg))
                    case "subscribe":
                        await self._unsubscribe(subs, msg.get("topic"))
                        sub = self.head.subscribe(msg["topic"], msg.get("rate_hz"), max_px=msg.get("max_px"))
                        subs[msg["topic"]] = (sub, asyncio.create_task(self._forward(ws, sub)))
                    case "unsubscribe":
                        await self._unsubscribe(subs, msg.get("topic"))
        except ConnectionClosed:
            pass
        finally:
            self.pages.discard(ws)
            for topic in list(subs):
                await self._unsubscribe(subs, topic)

    async def _unsubscribe(self, subs: dict, topic: str | None) -> None:
        if topic in subs:
            sub, task = subs.pop(topic)
            task.cancel()
            with contextlib.suppress(Exception):
                await sub.close()

    async def _forward(self, ws: ServerConnection, sub: Subscription) -> None:
        try:
            async with sub:
                async for msg in sub:
                    data = msg.model_dump(mode="json", exclude_none=True, exclude={"type", "seq"})
                    await ws.send(json.dumps({"op": "topic", "topic": sub.topic, "data": data}))
        except HeadError as exc:  # e.g. mesh on a phone without LiDAR
            with contextlib.suppress(ConnectionClosed):
                await ws.send(json.dumps({"op": "topic_error", "topic": sub.topic, "code": exc.code,
                                          "message": exc.message}))
        except (ConnectionClosed, asyncio.CancelledError):
            pass

    async def _command(self, ws: ServerConnection, msg: dict) -> None:
        reply: dict[str, Any] = {"op": "result", "id": msg.get("id")}
        try:
            if msg["op"] == "say":
                result = await self.head.command("speech.say", segments=parse(msg["text"]))
            else:
                result = await self.head.command(msg["type"], **(msg.get("params") or {}))
            reply.update(ok=True, result=result)
        except HeadError as exc:
            reply.update(ok=False, error={"code": exc.code, "message": exc.message})
        except (ValueError, KeyError, TypeError) as exc:
            reply.update(ok=False, error={"code": "invalid_params", "message": str(exc)})
        except (ConnectionError, TimeoutError) as exc:
            reply.update(ok=False, error={"code": "not_connected", "message": str(exc) or "head not reachable"})
        with contextlib.suppress(ConnectionClosed):
            await ws.send(json.dumps(reply))

    async def _watch_link(self) -> None:
        """Tell the pages when the head goes away and comes back (the client reconnects)."""
        last = self.head.connected.is_set()
        while True:
            await asyncio.sleep(0.5)
            now = self.head.connected.is_set()
            if now != last:
                last = now
                for ws in list(self.pages):
                    with contextlib.suppress(ConnectionClosed):
                        await ws.send(json.dumps(self._hello() | {"op": "link"}))
