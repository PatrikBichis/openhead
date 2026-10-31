"""Regenerate the test media in this folder (committed; rerun only to change them).

    cd python
    uv run --with imageio-ffmpeg python ../scenarios/assets/make_assets.py

test-card.svg   vector card: must stay sharp at any size
spinner.gif     animated GIF, 8 frames
clip.mp4        3 s H.264, 25 fps, 480x270: one colour per second plus a moving square, so a
                screenshot at a fixed time shows which frame is on screen
"""

from __future__ import annotations

import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 90" width="160" height="90">
  <rect width="160" height="90" fill="#1f3a5f"/>
  <rect x="6" y="6" width="148" height="78" fill="none" stroke="#ffc857" stroke-width="3"/>
  <circle cx="50" cy="45" r="22" fill="#e76f51"/>
  <path d="M90 67 L112 23 L134 67 Z" fill="#2a9d8f"/>
  <path d="M20 80 C 60 60, 100 100, 140 80" fill="none" stroke="#fff" stroke-width="1.5"/>
</svg>
"""


def gif() -> None:
    from PIL import Image, ImageDraw

    frames = []
    for i in range(8):
        img = Image.new("RGB", (120, 120), "#1f3a5f")
        d = ImageDraw.Draw(img)
        d.pieslice((10, 10, 110, 110), i * 45, i * 45 + 90, fill="#ffc857")
        frames.append(img)
    frames[0].save(HERE / "spinner.gif", save_all=True, append_images=frames[1:], duration=100, loop=0)


def clip() -> None:
    import imageio_ffmpeg

    colors = ("color=c=0x1f3a5f:s=480x270:d=1,color=c=0x2a9d8f:s=480x270:d=1,"
              "color=c=0xe76f51:s=480x270:d=1,color=c=0xffc857:s=24x24:d=3")
    sources = [arg for c in colors.split(",") for arg in ("-f", "lavfi", "-i", c)]
    graph = ("[0][1][2]concat=n=3:v=1:a=0,fps=25,"
             "drawbox=x=40:y=40:w=400:h=150:color=white@0.25:t=fill[bg];"
             "[bg][3]overlay=x='40+t*130':y=210[v]")  # the square moves: shows the time
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", *sources,
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
                    "-filter_complex", graph, "-map", "[v]", "-map", "4:a",
                    "-c:v", "libx264", "-profile:v", "baseline", "-pix_fmt", "yuv420p", "-crf", "28",
                    "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", "-t", "3",
                    str(HERE / "clip.mp4")], check=True)


if __name__ == "__main__":
    (HERE / "test-card.svg").write_text(SVG, encoding="utf-8")
    gif()
    clip()
    for f in ("test-card.svg", "spinner.gif", "clip.mp4"):
        print(f, (HERE / f).stat().st_size, "bytes")
