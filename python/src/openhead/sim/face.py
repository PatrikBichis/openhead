"""The face engine (`face/dist`) running in Chromium, driven through Playwright.

The same backend serves the windowed simulator (`headless=False`) and the headless one
used in tests: Playwright gives both a real browser and pixel-exact screenshots.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ORIGIN = "http://openhead.face"

DISPLAY_CSS = """
#display { position: fixed; inset: 0; z-index: 1; display: flex; align-items: center;
           justify-content: center; background: #000; }
#display[hidden] { display: none; }
#display img { max-width: 100%; max-height: 100%; object-fit: contain; }
#display iframe { border: 0; width: 100%; height: 100%; background: #fff; }
body.face-corner #face { position: fixed; right: 12px; bottom: 12px; width: 32vw; height: 32vh;
                         z-index: 2; border-radius: 16px; }
"""

SHOW_JS = """
async ([content, source, overlay]) => {
  let d = document.getElementById("display");
  if (!d) {
    d = document.createElement("div");
    d.id = "display";
    document.body.append(d);
  }
  const el = document.createElement(content === "image" ? "img" : "iframe");
  const loaded = new Promise((ok, fail) => {
    el.onload = ok;
    el.onerror = () => fail(new Error(`could not load ${content}`));
  });
  el.src = source;
  d.replaceChildren(el);
  d.hidden = false;
  document.body.classList.toggle("face-corner", overlay === "face-corner");
  if (content === "image") await loaded;
}
"""

CLEAR_JS = """
() => {
  const d = document.getElementById("display");
  if (d) { d.hidden = true; d.replaceChildren(); }
  document.body.classList.remove("face-corner");
}
"""


class FaceError(Exception):
    """The engine rejected a call (e.g. unknown theme)."""


def find_face_dist() -> Path:
    """`face/dist` from $OPENHEAD_FACE_DIST or the repository this package lives in."""
    if env := os.environ.get("OPENHEAD_FACE_DIST"):
        return Path(env)
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "face" / "dist"
        if (candidate / "index.html").exists():
            return candidate
    raise FileNotFoundError(
        "face/dist not found: run `npm ci && npm run build` in face/ or set OPENHEAD_FACE_DIST"
    )


class BrowserFace:
    def __init__(
        self,
        dist: Path | None = None,
        *,
        size: tuple[int, int] = (390, 844),
        headless: bool = True,
        idle: bool = True,
        on_log: Callable[[str, str], None] | None = None,
    ):
        self.dist = (dist or find_face_dist()).resolve()
        self.size = size
        self.headless = headless
        self.idle = idle
        self.on_log = on_log or (lambda level, message: None)
        self._pw: Any = None
        self._browser: Any = None
        self._page: Any = None

    async def start(self, theme: str = "cartoon") -> None:
        from playwright.async_api import async_playwright

        w, h = self.size
        self._pw = await async_playwright().start()
        args = [] if self.headless else [f"--window-size={w},{h + 90}", "--app=about:blank"]
        self._browser = await self._pw.chromium.launch(headless=self.headless, args=args)
        self._page = await self._browser.new_page(viewport={"width": w, "height": h})
        await self._page.route(f"{ORIGIN}/**", self._serve)
        self._page.on("console", self._console)
        query = f"theme={theme}" + ("" if self.idle else "&idle=0")
        await self._page.goto(f"{ORIGIN}/index.html?{query}")
        await self._page.wait_for_function("document.documentElement.dataset.ready === '1'")
        await self._page.add_style_tag(content=DISPLAY_CSS)

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()

    async def _serve(self, route: Any) -> None:
        path = urlparse(route.request.url).path.lstrip("/") or "index.html"
        file = (self.dist / path).resolve()
        if not file.is_relative_to(self.dist) or not file.is_file():
            await route.fulfill(status=404, body="not found")
        else:
            await route.fulfill(path=str(file))

    def _console(self, msg: Any) -> None:
        text = msg.text
        if text.startswith("[face] "):
            self.on_log("warning" if msg.type == "warning" else "info", text[len("[face] "):])
        elif msg.type == "error":
            self.on_log("error", text)

    async def _call(self, js: str, arg: Any = None) -> Any:
        try:
            return await self._page.evaluate(js, arg)
        except Exception as exc:  # Playwright wraps page exceptions in its own Error type
            message = str(exc).splitlines()[0]
            for prefix in ("Page.evaluate: ", "Error: "):
                message = message.removeprefix(prefix)
            raise FaceError(message) from exc

    async def set_theme(self, name: str, transition_ms: int = 300) -> None:
        await self._call("([n, t]) => window.openhead.setTheme(n, t)", [name, transition_ms])

    async def set_emotion(self, name: str, intensity: float, blend: str,
                          duration_ms: int | None) -> None:
        await self._call("([n, i, b, d]) => window.openhead.setEmotion(n, i, b, d ?? undefined)",
                         [name, intensity, blend, duration_ms])

    async def set_gaze(self, x: float, y: float) -> None:
        await self._call("([x, y]) => window.openhead.setGaze(x, y)", [x, y])

    async def blink(self) -> None:
        await self._call("() => window.openhead.blink()")

    async def envelope(self, level: float) -> None:
        await self._call("(l) => window.openhead.setEnvelope(l)", level)

    async def list_themes(self) -> list[dict]:
        return await self._call("() => window.openhead.listThemes()")

    async def state(self) -> dict:
        return await self._call(
            "() => { const s = window.openhead.state(); return {theme: s.theme, emotion: s.emotion}; }"
        )

    async def show(self, content: str, source: str, overlay: str) -> None:
        await self._call(SHOW_JS, [content, source, overlay])

    async def clear(self) -> None:
        await self._call(CLEAR_JS)

    async def screenshot(self, scale: float = 1.0) -> tuple[bytes, int, int]:
        png = await self._page.screenshot(type="png")
        from PIL import Image

        image = Image.open(BytesIO(png))
        if scale < 1:
            size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
            image = image.resize(size, Image.Resampling.LANCZOS)
            out = BytesIO()
            image.save(out, format="PNG")
            png = out.getvalue()
        return png, image.width, image.height
