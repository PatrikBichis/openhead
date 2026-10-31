"""Serve local files to the head over HTTP, so it can play a video (or show an image) from disk.

The head fetches media itself. A file on the host gets a URL on the address the host uses to
reach the head; byte ranges are supported because iOS needs them for video.

    async with MediaServer() as media:
        url = media.url_for(Path("clip.mp4"), head)
        await head.display.show_video(url)
"""

from __future__ import annotations

import mimetypes
import re
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Self
from urllib.parse import quote, unquote

if TYPE_CHECKING:
    from .head import Head

TYPES = {".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime",
         ".webm": "video/webm", ".svg": "image/svg+xml"}


class MediaServer:
    """Serves only the files handed to `url_for`, under an unguessable path."""

    def __init__(self, port: int = 0):
        self._files: dict[str, Path] = {}
        self._prefix = secrets.token_urlsafe(12)
        files, prefix = self._files, self._prefix

        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self) -> None:
                self._serve(body=False)

            def do_GET(self) -> None:
                self._serve(body=True)

            def _serve(self, body: bool) -> None:
                parts = unquote(self.path.split("?")[0]).strip("/").split("/", 1)
                path = files.get(parts[1]) if len(parts) == 2 and parts[0] == prefix else None
                if not path or not path.is_file():
                    self.send_error(404)
                    return
                size = path.stat().st_size
                start, end = 0, size - 1
                ranged = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
                if ranged and (ranged[1] or ranged[2]):
                    if ranged[1]:
                        start, end = int(ranged[1]), int(ranged[2] or size - 1)
                    else:  # suffix range: the last N bytes
                        start = max(0, size - int(ranged[2]))
                    end = min(end, size - 1)
                    if start > end:
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{size}")
                        self.end_headers()
                        return
                    self.send_response(206)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                else:
                    self.send_response(200)
                kind = TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0]
                self.send_header("Content-Type", kind or "application/octet-stream")
                self.send_header("Content-Length", str(end - start + 1))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Access-Control-Allow-Origin", "*")  # frames usable in screenshots
                self.end_headers()
                if body:
                    with path.open("rb") as f:
                        f.seek(start)
                        left = end - start + 1
                        while left > 0 and (chunk := f.read(min(left, 256 * 1024))):
                            try:
                                self.wfile.write(chunk)
                            except (BrokenPipeError, ConnectionResetError):
                                return  # players drop connections when they seek
                            left -= len(chunk)

            def log_message(self, *args: object) -> None:
                pass

        self._server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
        self._server.daemon_threads = True
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def port(self) -> int:
        return self._server.server_address[1]

    def start(self) -> Self:
        self._thread.start()
        return self

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    async def __aenter__(self) -> Self:
        return self.start()

    async def __aexit__(self, *exc: object) -> None:
        self.close()

    def url_for(self, path: Path, head: Head) -> str:
        """A URL for `path` that `head` can fetch: on the host address its connection uses."""
        path = path.resolve()
        name = f"{len(self._files)}-{path.name}"
        self._files[name] = path
        host = head.local_host
        host = f"[{host}]" if ":" in host else host
        return f"http://{host}:{self.port}/{self._prefix}/{quote(name)}"
