"""Tiny HTTP server for screenshot URLs (WebSocket port + 1), as the device provides.

`GET /shot/<id>.png` with `Authorization: Bearer <token>` of the client that asked for it;
URLs expire after 60 s.
"""

from __future__ import annotations

import asyncio
import re
import secrets
import time


class ShotServer:
    def __init__(self, ttl_s: float = 60):
        self.ttl_s = ttl_s
        self._shots: dict[str, tuple[bytes, str, float]] = {}
        self._server: asyncio.Server | None = None

    async def start(self, host: str, port: int) -> int:
        self._server = await asyncio.start_server(self._handle, host, port)
        return self._server.sockets[0].getsockname()[1]

    async def stop(self) -> None:
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    def add(self, png: bytes, token: str) -> str:
        now = time.monotonic()
        self._shots = {k: v for k, v in self._shots.items() if v[2] > now}
        shot_id = secrets.token_urlsafe(12)
        self._shots[shot_id] = (png, token, now + self.ttl_s)
        return shot_id

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            request = (await reader.readline()).decode("latin-1").split()
            headers = {}
            while (line := await reader.readline()) not in (b"\r\n", b"\n", b""):
                key, _, value = line.decode("latin-1").partition(":")
                headers[key.strip().lower()] = value.strip()
            status, body, ctype = self._respond(request, headers)
            writer.write(
                f"HTTP/1.1 {status}\r\nContent-Type: {ctype}\r\nContent-Length: {len(body)}\r\n"
                "Connection: close\r\n\r\n".encode("latin-1") + body
            )
            await writer.drain()
        finally:
            writer.close()

    def _respond(self, request: list[str], headers: dict[str, str]) -> tuple[str, bytes, str]:
        text = "text/plain"
        if len(request) < 2 or request[0] != "GET":
            return "405 Method Not Allowed", b"GET only", text
        m = re.fullmatch(r"/shot/([A-Za-z0-9_-]+)\.png", request[1])
        shot = self._shots.get(m.group(1)) if m else None
        if shot is None:
            return "404 Not Found", b"unknown screenshot", text
        png, token, expires = shot
        if time.monotonic() > expires:
            return "410 Gone", b"screenshot URL expired", text
        if headers.get("authorization") != f"Bearer {token}":
            return "401 Unauthorized", b"bearer token required", text
        return "200 OK", png, "image/png"
