"""Still images the 3D scene needs: the laptop's agent terminal.

    uv run --project python --with pillow python tools/promo/assets.py OUT_DIR
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path("C:/Windows/Fonts")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for f in (name, "consola.ttf", "DejaVuSansMono.ttf"):
        try:
            return ImageFont.truetype(str(FONTS / f), size)
        except OSError:
            continue
    return ImageFont.load_default()


def laptop(path: Path) -> None:
    w, h = 1600, 1000
    im = Image.new("RGB", (w, h), "#16294a")
    d = ImageDraw.Draw(im)
    mono, bold = font("consola.ttf", 40), font("consolab.ttf", 40)
    d.rectangle((0, 0, w, 70), fill="#1f3a5f")
    for i, c in enumerate(("#e76f51", "#ffc857", "#2a9d8f")):
        d.ellipse((28 + i * 44, 22, 56 + i * 44, 50), fill=c)
    d.text((200, 14), "agent · openhead MCP", font=mono, fill="#fbf3e6")
    lines = [
        ("> ", "#e76f51", "look at me and tell me my next meeting", "#fbf3e6"),
        ("", "", "", "#fbf3e6"),
        ("● ", "#2a9d8f", "openhead · look_at_face", "#fbf3e6"),
        ("  ", "", "following face 1 (locked)", "#9fb3c8"),
        ("● ", "#2a9d8f", "openhead · subtitle", "#fbf3e6"),
        ("  ", "", '"Your 10:00 meeting starts in five', "#9fb3c8"),
        ("  ", "", ' minutes."  mouth: on', "#9fb3c8"),
        ("● ", "#2a9d8f", "openhead · get_environment", "#fbf3e6"),
        ("  ", "", "101.8 kPa · heading 47° true", "#9fb3c8"),
        ("● ", "#2a9d8f", "openhead · get_location", "#fbf3e6"),
        ("  ", "", "fix ±5 m · 1 Hz", "#9fb3c8"),
        ("", "", "", "#fbf3e6"),
        ("> ", "#e76f51", "", "#fbf3e6"),
    ]
    y = 120
    for mark, mc, text, tc in lines:
        if mark:
            d.text((60, y), mark, font=bold, fill=mc or tc)
        d.text((110, y), text, font=mono, fill=tc)
        y += 62
    d.rectangle((110, y - 58, 132, y - 18), fill="#fbf3e6")
    im.save(path)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    laptop(out / "laptop.png")
    print(out / "laptop.png")
