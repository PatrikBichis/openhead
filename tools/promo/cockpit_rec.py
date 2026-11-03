"""Record `openhead cockpit` for the promo's cockpit scene.

    cd python
    uv run --extra sim python ../tools/promo/cockpit_rec.py ../build/promo/cockpit

Runs a simulated Pro head and the cockpit in this process, opens the page in Chromium and plays
what the scene shows: the front camera (capture), the Hello example said through the Speak card
(when the film's voice says it), then sensing with the back camera and the ARKit map. Writes
screenshots and `times.json` (seconds into the scene per shot); compose.py picks the shot for
each film frame.
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import story
from playwright.async_api import async_playwright

from openhead.client import Head
from openhead.cockpit import Cockpit
from openhead.sim import SimServer
from openhead.tokens import TokenStore

SCENE = next(s for s in story.SCENES if s.key == "cockpit")
SAY_AT = next(at for at, kind, _ in SCENE.cues if kind == "say")
VIEW = (1440, 900)


async def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        sim = SimServer(host="127.0.0.1", port=0, mdns=False, pro=True)
        await sim.start()
        head = await Head.connect("127.0.0.1", sim.port, client="promo", store=TokenStore(Path(tmp) / "t.json"))
        await head.pair("0000")
        await head.mode.set("capture")
        cockpit = Cockpit(head, port=0)
        await cockpit.start()
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page(viewport={"width": VIEW[0], "height": VIEW[1]}, device_scale_factor=1.5)
            await page.goto(cockpit.url)
            await page.locator(".video img").wait_for(state="visible", timeout=10000)
            await page.wait_for_timeout(1500)  # the plots fill a little
            say = page.locator('.card[data-id="say"]')
            steps = [  # (seconds into the scene, action)
                (SAY_AT - 0.5, lambda: say.locator(".chip", has_text="Hello").click()),
                (SAY_AT - 0.1, lambda: say.get_by_role("button", name="Say").click()),
                (4.6, lambda: page.locator('.card[data-id="mode"] button', has_text="Sensing").click()),
            ]
            times = []
            start = time.monotonic()
            n = 0
            while (t := time.monotonic() - start) < SCENE.end - SCENE.start:
                while steps and t >= steps[0][0]:
                    await steps.pop(0)[1]()
                await page.screenshot(path=str(out / f"{n:04d}.jpg"), type="jpeg", quality=92)
                times.append(round(t, 3))
                n += 1
            (out / "times.json").write_text(json.dumps(times))
            await browser.close()
        await cockpit.stop()
        await head.close()
        await sim.stop()
    print(f"{n} shots, {n / (SCENE.end - SCENE.start):.1f} per second ->", out)


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1])))
