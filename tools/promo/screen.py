"""Render the phone screen for every frame of the promo with the real face engine.

    cd python
    uv run python ../tools/promo/screen.py OUT_DIR [--every N] [--voice ../build/promo/voice.json]

Drives face/dist in headless Chromium in test mode (no clock: the engine advances exactly
1/30 s per frame), with the emotions, gaze, spoken subtitles and camera view from story.py.
With voice.py's output the subtitles appear when each line is heard and the mouth follows the
voice's loudness (the envelope), as on the phone; without it the mouth follows the text.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from openhead.sim.face import ORIGIN, BrowserFace

sys.path.insert(0, str(Path(__file__).parent))
import story

HUD_VALUES = {"battery": 86, "charging": True, "thermal": "nominal", "heading": 47, "pitch": 2.0,
              "roll": 0.0, "x": 0.0, "y": 0.0, "z": 0.0, "tracking": "normal", "mode": "capture",
              "clients": 1}


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    p.add_argument("--every", type=int, default=1, help="render every Nth frame (previews)")
    p.add_argument("--frames", type=str, help="a:b, only these frames")
    p.add_argument("--voice", type=Path, help="voice.json from voice.py")
    args = p.parse_args()
    voice = json.loads(args.voice.read_text(encoding="utf-8")) if args.voice else None
    said = {}  # film frame -> subtitle text, when the voice says it
    if voice:
        heads = [c for c in voice["clips"] if c["who"] == "head"]
        cues = [(s, v) for s in story.SCENES for _, k, v in s.cues if k == "say"]
        for clip, (_, text) in zip(heads, cues, strict=True):
            said[int(clip["start"] * story.FPS)] = text
    args.out.mkdir(parents=True, exist_ok=True)

    face = BrowserFace(size=(844, 390), pixel_ratio=2)
    await face.start("cartoon")
    page = face._page
    # Test mode: the page only moves when we tick it.
    await page.goto(f"{ORIGIN}/index.html?test&theme=cartoon")
    await page.wait_for_function("document.documentElement.dataset.ready === '1'")
    await page.evaluate("document.fonts.load('600 24px \"Inter Variable\"')")

    first, last = 0, story.FRAMES
    if args.frames:
        a, b = args.frames.split(":")
        first, last = int(a), int(b)
    scene = None
    for n in range(last):
        f = story.frame(n)
        s = f.scene
        if s is not scene:
            await page.evaluate("([e]) => window.openhead.setEmotion(e, 1, 'replace')", [s.emotion])
            if s.screen == "camera":
                await page.evaluate("() => window.openhead.show('camera', '', {hud: 'hunter'})")
                await page.evaluate("(v) => window.openhead.setHudValues(v)", HUD_VALUES)
            elif scene is not None and scene.screen == "camera":
                await page.evaluate("() => window.openhead.show('face')")
            if scene is not None and any(k == "say" for _, k, _ in scene.cues):
                await page.evaluate("() => window.openhead.subtitle('', {mode: 'clear'})")
            scene = s
        for at, kind, value in s.cues:
            if int((s.start + at) * story.FPS) == n:
                if kind == "emotion":
                    await page.evaluate("([e]) => window.openhead.setEmotion(e, 1, 'replace')", [value])
                elif kind == "say" and not voice:
                    await page.evaluate("(t) => window.openhead.subtitle(t, {mode: 'append', mouth: true})",
                                        value)
                else:
                    await page.evaluate("() => window.openhead.subtitle('', {mode: 'clear'})")
        if n in said:
            await page.evaluate("(t) => window.openhead.subtitle(t, {mode: 'append'})", said[n])
        if voice and voice["envelope"][n] > 0.03:
            await page.evaluate("(v) => window.openhead.setEnvelope(v)", voice["envelope"][n])
        if s.screen == "camera":
            bearing, elevation = story.face_bearing(f)
            size = 0.16
            face_json = {"id": 1, "bearing": bearing, "elevation": elevation, "size": size,
                         "confidence": 0.95, "locked": True,
                         "box": {"x": 0.5 - bearing / 70 - size / 2, "y": 0.42 - elevation / 50 - 0.16,
                                 "w": size, "h": size * 2.1}}
            await page.evaluate("(f) => window.openhead.setFaces(f)", [face_json])
            heading = (47 + f.joints["head_yaw"] * 57.3) % 360
            await page.evaluate("(h) => window.openhead.setHudValues(h)",
                                {**HUD_VALUES, "heading": heading})
        await page.evaluate("([x, y]) => window.openhead.setGaze(x, y)", list(f.gaze))
        await page.evaluate(f"() => window.openhead.tick({1000 / story.FPS})")
        if n >= first and n % args.every == 0:
            await page.evaluate("() => window.openhead.render()")
            await page.screenshot(path=str(args.out / f"{n:05d}.png"))
        if n % 150 == 0:
            print(f"screen {n}/{last}", flush=True)
    await face.close()


if __name__ == "__main__":
    asyncio.run(main())
