"""Render the iOS app icon (1024 x 1024, no alpha) from the face engine itself.

    (cd face && npm run build)
    uv run --project python python tools/app_icon.py
"""

import asyncio
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from openhead.sim.face import BrowserFace

ROOT = Path(__file__).resolve().parents[1]
ICONSET = ROOT / "apps" / "ios" / "OpenHead" / "Resources" / "Assets.xcassets" / "AppIcon.appiconset"


async def main() -> None:
    face = BrowserFace(size=(1024, 1024), headless=True, idle=False)
    await face.start("cartoon")
    try:
        await face.set_emotion("happy", 1.0, "replace", None)
        await asyncio.sleep(0.6)
        png, _, _ = await face.screenshot()
    finally:
        await face.close()
    ICONSET.mkdir(parents=True, exist_ok=True)
    # App Store icons must not have an alpha channel.
    Image.open(BytesIO(png)).convert("RGB").save(ICONSET / "AppIcon.png", optimize=True)
    (ICONSET / "Contents.json").write_text(json.dumps({
        "images": [{"filename": "AppIcon.png", "idiom": "universal", "platform": "ios",
                    "size": "1024x1024"}],
        "info": {"author": "xcode", "version": 1},
    }, indent=2) + "\n", encoding="utf-8")
    assets = ICONSET.parent / "Contents.json"
    assets.write_text(json.dumps({"info": {"author": "xcode", "version": 1}}, indent=2) + "\n",
                      encoding="utf-8")
    print(ICONSET / "AppIcon.png")


if __name__ == "__main__":
    asyncio.run(main())
