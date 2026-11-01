"""Put the titles, the sensor panel and the end card on the rendered frames and encode.

    cd python
    uv run --with pillow --with imageio-ffmpeg python ../tools/promo/compose.py \
        ../build/promo/frames ../docs/media/desk-assistant.mp4

Text and colours follow the website (docs/site.css). Every frame says it is a render: real
footage of the bench head comes later.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import story

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path("C:/Windows/Fonts")
W, H = story.SIZE


@lru_cache
def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    name = {"regular": "segoeui.ttf", "semibold": "seguisb.ttf", "bold": "segoeuib.ttf"}[weight]
    try:
        return ImageFont.truetype(str(FONTS / name), size)
    except OSError:
        return ImageFont.truetype("DejaVuSans.ttf", size)


def rgba(h: str, a: float = 1.0) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), round(a * 255))


@lru_cache
def icon(size: int) -> Image.Image:
    return Image.open(ROOT / "docs" / "media" / "icon.png").convert("RGBA").resize((size, size), Image.LANCZOS)


@lru_cache
def badge() -> Image.Image | None:
    path = ROOT / "build" / "promo" / "assets" / "appstore-badge.png"
    return Image.open(path).convert("RGBA") if path.exists() else None


def ease(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def bloom(im: Image.Image) -> Image.Image:
    # Only near-white highlights (the glowing effects, the screens) bloom; the cream set
    # is bright too, so the threshold sits high.
    small = im.resize((W // 4, H // 4), Image.BILINEAR)
    bright = small.point(lambda v: max(0, v - 248) * 12)
    glow = bright.filter(ImageFilter.GaussianBlur(8)).resize((W, H), Image.BILINEAR)
    return ImageChops.add(im, glow.point(lambda v: v * 0.3))


def vignette() -> Image.Image:
    v = Image.new("L", (W // 8, H // 8), 0)
    d = ImageDraw.Draw(v)
    d.ellipse((-W // 16, -H // 14, W // 8 + W // 16, H // 8 + H // 14), fill=255)
    return v.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR)


VIGNETTE = None


def card(d: ImageDraw.ImageDraw, layer: Image.Image, s: story.Scene, idx: int, a: float, slide: float):
    if a <= 0:
        return
    x, y = 72, H - 72
    pad = 30
    title_f, text_f, eye_f = font("bold", 46), font("regular", 26), font("bold", 17)
    eyebrow = "OPENHEAD" if s.key in ("intro", "end") else f"{idx:02d} · {s.title.upper()}"
    tw = max(d.textlength(s.title, font=title_f), d.textlength(s.text, font=text_f),
             d.textlength(eyebrow, font=eye_f))
    w, h = int(tw + pad * 2), 168
    y0 = int(y - h + (1 - slide) * 30)
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=rgba(story.CREAM_2, 0.93),
                         outline=rgba(story.INK, 0.10), width=1)
    bd.text((pad, 24), eyebrow, font=eye_f, fill=rgba(story.TEAL))
    bd.text((pad, 46), s.title, font=title_f, fill=rgba(story.INK))
    bd.text((pad, 110), s.text, font=text_f, fill=rgba(story.INK_2))
    box.putalpha(box.getchannel("A").point(lambda v: int(v * a)))
    layer.alpha_composite(box, (x, y0))


def panel(layer: Image.Image, s: story.Scene, a: float):
    if a <= 0:
        return
    rows = story.SENSORS
    w, row_h, pad = 400, 44, 26
    h = pad * 2 + 34 + row_h * len(rows)
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=rgba(story.CREAM_2, 0.90),
                        outline=rgba(story.INK, 0.10), width=1)
    d.text((pad, pad - 4), "SENSORS IN USE", font=font("bold", 17), fill=rgba(story.INK_2))
    for i, (key, label, colour) in enumerate(rows):
        y = pad + 34 + i * row_h
        on = key in s.sensors
        if on:
            d.rounded_rectangle((pad - 12, y - 6, w - pad + 12, y + row_h - 10), radius=10,
                                fill=(255, 255, 255, 200))
            d.rounded_rectangle((pad - 12, y - 6, pad - 7, y + row_h - 10), radius=2, fill=rgba(colour))
        cy = y + 13
        d.ellipse((pad, cy - 7, pad + 14, cy + 7), fill=rgba(colour, 1 if on else 0.25))
        d.text((pad + 28, y - 2), label, font=font("semibold" if on else "regular", 22),
               fill=rgba(story.INK if on else story.INK_2, 1 if on else 0.45))
    box.putalpha(box.getchannel("A").point(lambda v: int(v * a)))
    layer.alpha_composite(box, (W - w - 60, 120))


def brand(layer: Image.Image, a: float):
    d = ImageDraw.Draw(layer)
    layer.alpha_composite(_fade(icon(48), a), (64, 52))
    d.text((126, 58), "OpenHead", font=font("bold", 30), fill=rgba(story.INK, a))
    tag = "3D render · real footage coming"
    f = font("semibold", 18)
    tw = d.textlength(tag, font=f)
    d.rounded_rectangle((W - 64 - tw - 32, 58, W - 64, 96), radius=19, fill=rgba(story.CREAM_2, 0.85 * a))
    d.text((W - 64 - tw - 16, 64), tag, font=f, fill=rgba(story.INK_2, a))


def _fade(im: Image.Image, a: float) -> Image.Image:
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


def end_card(layer: Image.Image, a: float):
    if a <= 0:
        return
    veil = Image.new("RGBA", (W, H), rgba(story.CREAM, 0.88 * a))
    layer.alpha_composite(veil)
    d = ImageDraw.Draw(layer)
    layer.alpha_composite(_fade(icon(150), a), (W // 2 - 75, 250))
    for text, f, y, c in (("OpenHead", font("bold", 92), 420, story.INK),
                          ("An iPhone as a robot head. Free and open source.", font("regular", 34), 540,
                           story.INK_2),
                          ("github.com/PatrikBichis/openhead", font("semibold", 28), 760, story.NAVY)):
        tw = d.textlength(text, font=f)
        d.text(((W - tw) / 2, y), text, font=f, fill=rgba(c, a))
    b = badge()
    if b:
        layer.alpha_composite(_fade(b, a), ((W - b.width) // 2, 620))


def compose(args: tuple[Path, Path]) -> None:
    src, dst = args
    n = int(src.stem)
    t = n / story.FPS
    s = story.scene_at(t)
    idx = [x.key for x in story.SCENES if x.key not in ("intro", "end")].index(s.key) + 1 \
        if s.key not in ("intro", "end") else 0
    im = Image.open(src).convert("RGB")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    im = bloom(im)
    global VIGNETTE
    if VIGNETTE is None:
        VIGNETTE = vignette()
    dark = Image.new("RGB", (W, H), (60, 45, 35))
    im = Image.composite(im, Image.blend(im, dark, 0.22), VIGNETTE)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    end_in = ease((t - (story.SCENES[-1].start + 0.4)) / 0.8)
    a_in = ease((t - s.start - 0.25) / 0.45)
    a_out = ease((s.end - t - 0.05) / 0.3) if s.key != "end" else 1.0
    a = a_in * a_out
    brand(layer, (1 - end_in) * ease(t / 0.6))
    if s.key == "end":
        end_card(layer, end_in)
    else:
        card(ImageDraw.Draw(layer), layer, s, idx, a, a_in)
        if s.key != "intro":
            panel(layer, s, a)
    out = im.convert("RGBA")
    out.alpha_composite(layer)
    out.convert("RGB").save(dst, quality=95)


def make_badge():
    """The official App Store badge (docs/media) as PNG, via Chromium."""
    path = ROOT / "build" / "promo" / "assets" / "appstore-badge.png"
    if path.exists():
        return
    from playwright.sync_api import sync_playwright

    svg = (ROOT / "docs" / "media" / "appstore-badge-en.svg").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(device_scale_factor=1)
        # inline: an about:blank page may not load file:// images
        page.set_content(f'<body style="margin:0;background:transparent"><div id=b style="height:84px;'
                         f'display:inline-block">{svg}</div></body>')
        page.evaluate("() => { const s = document.querySelector('#b svg'); s.style.height = '84px';"
                      " s.style.width = 'auto'; s.style.display = 'block'; }")
        page.locator("#b svg").screenshot(path=str(path), omit_background=True)
        b.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("frames", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--only", help="a,b,c: compose these frames to build/promo/composed and stop")
    args = p.parse_args()
    make_badge()
    work = ROOT / "build" / "promo" / "composed"
    work.mkdir(parents=True, exist_ok=True)
    srcs = sorted(args.frames.glob("*.png"))
    if args.only:
        keep = {int(v) for v in args.only.split(",")}
        srcs = [s for s in srcs if int(s.stem) in keep]
    jobs = [(s, work / f"{s.stem}.jpg") for s in srcs]
    with ProcessPoolExecutor() as pool:
        list(pool.map(compose, jobs, chunksize=8))
    if args.only:
        print("composed", len(jobs))
        return
    import imageio_ffmpeg

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    base = ["-y", "-loglevel", "error", "-framerate", str(story.FPS), "-start_number", "0",
            "-i", str(work / "%05d.jpg")]
    subprocess.run([ff, *base, "-c:v", "libx264", "-profile:v", "high", "-crf", "21",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(args.out)], check=True)
    subprocess.run([ff, *base, "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", "34", "-row-mt", "1",
                    "-pix_fmt", "yuv420p", str(args.out.with_suffix(".webm"))], check=True)
    poster = Image.open(work / f"{int(3.5 * story.FPS):05d}.jpg")  # intro: the rig, the desk, the agent
    poster.save(args.out.with_name(args.out.stem + "-poster.jpg"), quality=88)
    print(args.out, args.out.with_suffix(".webm"))


if __name__ == "__main__":
    main()
