"""Put the titles, the sensor panel and the end card on the rendered frames and encode.

    cd python
    uv run --with pillow --with imageio-ffmpeg python ../tools/promo/compose.py \
        ../build/promo/frames ../docs/media/desk-assistant.mp4

Text and colours follow the website (docs/site.css). Every frame says it is a render: real
footage of the bench head comes later. The sound is voice.py's track; the walking scene's map
is the phone's path from duck_walk.py, as ARKit's `pose` would report it. The cockpit scene
shows cockpit_rec.py's recording of `openhead cockpit` in a browser window over the desk.
"""

from __future__ import annotations

import argparse
import json
import math
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


PROMO = ROOT / "build" / "promo"


@lru_cache
def voice() -> dict:
    path = PROMO / "voice.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"clips": []}


@lru_cache
def walk_path() -> list[tuple[float, float, float]]:
    """The phone's path as ARKit reports it: metres right of and ahead of where tracking started, and yaw."""
    path = PROMO / "duck.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [m["mesh"] for m in data["meshes"]]
    i, r = names.index("screen"), names.index("cam_rear")

    def axes(row):
        x, y, z, w, qx, qy, qz = row[i]
        # the screen box's z axis, from its quaternion
        n = (2 * (qx * qz + w * qy), 2 * (qy * qz - w * qx), 1 - 2 * (qx * qx + qy * qy))
        return (x, y, z), n

    p0, n0 = axes(data["frames"][0])
    rear = data["frames"][0][r][:3]
    sign = 1 if sum(n0[k] * (p0[k] - rear[k]) for k in range(3)) > 0 else -1
    yaw0 = math.atan2(sign * n0[1], sign * n0[0])
    out = []
    rows = data["frames"]
    for k, row in enumerate(rows):
        p, n = axes(row)
        # the walk, not the sway of every step (as the trail in the scene)
        near = [axes(r)[0] for r in rows[max(0, k - 7):k + 8]]
        p = tuple(sum(q[j] for q in near) / len(near) for j in range(3))
        dx, dy = p[0] - p0[0], p[1] - p0[1]
        ahead = dx * math.cos(yaw0) + dy * math.sin(yaw0)
        left = -dx * math.sin(yaw0) + dy * math.cos(yaw0)
        yaw = math.atan2(sign * n[1], sign * n[0]) - yaw0
        out.append((-left, ahead, yaw))
    return out


@lru_cache
def mono(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(FONTS / "consola.ttf"), size)
    except OSError:
        return font("regular", size)


TOP_X = (W - 480) // 2 + 40  # centre of the space left of the sensor panel


def pill(layer: Image.Image, parts: list[tuple[str, str, ImageFont.FreeTypeFont]], a: float,
         dot: str | None = None):
    """A rounded label of coloured runs of text at the top of the frame."""
    if a <= 0:
        return
    d = ImageDraw.Draw(layer)
    pad = 26
    lead = 34 if dot else 0
    tw = sum(d.textlength(t, font=f) for t, _, f in parts)
    w, h = int(tw + pad * 2 + lead), 62
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle((0, 0, w - 1, h - 1), radius=31, fill=rgba(story.CREAM_2, 0.94),
                         outline=rgba(story.INK, 0.10), width=1)
    x = pad
    if dot:
        bd.ellipse((x, h / 2 - 9, x + 18, h / 2 + 9), fill=rgba(dot))
        x += lead
    for text, colour, f in parts:
        bd.text((x, h / 2), text, font=f, fill=rgba(colour), anchor="lm")
        x += bd.textlength(text, font=f)
    layer.alpha_composite(_fade(box, a), (int(TOP_X - w / 2), 132))


def heard(layer: Image.Image, t: float, a: float):
    """What the microphone hears, word by word, then that it went to the agent."""
    clip = next((c for c in voice()["clips"] if c["who"] == "person"), None)
    start, end = (clip["start"], clip["end"]) if clip else (12.4, 13.4)
    words = story.HEARD.split()
    k = len(words) if t >= end else max(0, math.ceil((t - start) / (end - start) * len(words)))
    if k == 0:
        return
    parts = [("heard  ", story.TEAL, font("bold", 22)),
             (f"“{' '.join(words[:k])}”", story.INK, font("semibold", 28))]
    if t > end + 0.4:
        parts.append(("   → your agent", story.INK_2, font("regular", 24)))
    pill(layer, parts, a, dot=story.TEAL)


def markup(layer: Image.Image, a: float):
    """The agent's say call, with the cues that drive the face in coral."""
    f = mono(25)
    parts = [('say("', story.INK_2, f)]
    for tok in story.SAY.replace("[", "|[").replace("]", "]|").split("|"):
        if tok:
            parts.append((tok, story.CORAL if tok.startswith("[") else story.INK, f))
    parts.append(('")', story.INK_2, f))
    pill(layer, parts, a)


def walk_map(layer: Image.Image, t: float, a: float):
    """A map of the pose stream: the trail so far, the phone's heading and the numbers."""
    path = walk_path()
    if not path or a <= 0:
        return
    n = max(0, min(len(path) - 1, int((t - story.WALK.start) * story.FPS)))
    w, h, pad = 440, 330, 24
    box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=18, fill=rgba(story.CREAM_2, 0.92),
                        outline=rgba(story.INK, 0.10), width=1)
    d.text((pad, pad - 4), "POSE · ARKIT WORLD TRACKING", font=font("bold", 17), fill=rgba(story.INK_2))
    mx0, my0, mx1, my1 = pad, 56, w - pad, h - 70
    xs = [p[0] for p in path] + [0]
    ys = [p[1] for p in path] + [0]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 0.5) * 1.25
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    scale = min(mx1 - mx0, my1 - my0) / span
    ox, oy = (mx0 + mx1) / 2, (my0 + my1) / 2

    def px(x, y):
        return (ox + (x - cx) * scale, oy - (y - cy) * scale)

    step = 0.25  # grid lines every 25 cm
    for k in range(-20, 21):
        x, y = px(k * step, k * step)
        if mx0 <= x <= mx1:
            d.line((x, my0, x, my1), fill=rgba(story.INK, 0.07), width=1)
        if my0 <= y <= my1:
            d.line((mx0, y, mx1, y), fill=rgba(story.INK, 0.07), width=1)
    o = px(0, 0)  # where tracking started: x right, ahead up
    d.line((o[0], o[1], o[0] + 26, o[1]), fill=rgba(story.TEAL), width=3)
    d.line((o[0], o[1], o[0], o[1] - 26), fill=rgba(story.CORAL), width=3)
    pts = [px(x, y) for x, y, _ in path[: n + 1]]
    if len(pts) > 1:
        d.line(pts, fill=rgba(story.GOLD), width=5, joint="curve")
    x, y, yaw = path[n]
    hx, hy = px(x, y)
    ang = math.pi / 2 + yaw
    tip = (hx + math.cos(ang) * 22, hy - math.sin(ang) * 22)
    left = (hx + math.cos(ang + 2.5) * 11, hy - math.sin(ang + 2.5) * 11)
    right = (hx + math.cos(ang - 2.5) * 11, hy - math.sin(ang - 2.5) * 11)
    d.polygon([tip, left, right], fill=rgba(story.NAVY))
    d.ellipse((hx - 6, hy - 6, hx + 6, hy + 6), fill=rgba(story.NAVY))
    f = mono(20)
    # ARKit: x right, y up, z towards the viewer, so ahead is -z
    d.text((pad, h - 56), f"position  [{x:+.2f}, 0.00, {-y:+.2f}] m", font=f, fill=rgba(story.INK))
    d.text((pad, h - 30), f"yaw {math.degrees(yaw):+5.0f}°   tracking normal", font=f, fill=rgba(story.INK_2))
    layer.alpha_composite(_fade(box, a), (64, 130))


@lru_cache
def cockpit_times() -> list[float]:
    path = PROMO / "cockpit" / "times.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def browser(im: Image.Image, t: float, s: story.Scene, a: float) -> Image.Image:
    """The desk blurred behind a browser window that plays the cockpit recording."""
    times = cockpit_times()
    back = im.filter(ImageFilter.GaussianBlur(14))
    back = Image.blend(back, Image.new("RGB", (W, H), (246, 230, 204)), 0.35)
    k = ease((t - s.start) / 0.5) * ease((s.end - t) / 0.5)
    out = Image.blend(im, back, k)
    if not times:
        return out
    u = t - s.start
    i = max((j for j, v in enumerate(times) if v <= u), default=0)
    shot = Image.open(PROMO / "cockpit" / f"{i:04d}.jpg").convert("RGB")
    cw = 1056  # ends above the title card
    ch = round(cw * shot.height / shot.width)
    bar = 46
    x0, y0 = W - 72 - cw, 118 + round((1 - a) * 24)
    win = Image.new("RGBA", (cw, ch + bar), (0, 0, 0, 0))
    mask = Image.new("L", win.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch + bar - 1), radius=16, fill=255)
    d = ImageDraw.Draw(win)
    d.rectangle((0, 0, cw, bar), fill=rgba("#ece3d4"))
    for n, c in enumerate(("#e76f51", "#ffc857", "#2a9d8f")):
        d.ellipse((20 + n * 24, bar // 2 - 7, 34 + n * 24, bar // 2 + 7), fill=rgba(c))
    d.rounded_rectangle((110, 9, cw - 110, bar - 9), radius=14, fill=rgba("#ffffff"))
    d.text((128, 12), "127.0.0.1:8770 · openhead cockpit", font=font("regular", 19), fill=rgba(story.INK_2))
    win.paste(shot.resize((cw, ch), Image.LANCZOS), (0, bar))
    win.putalpha(mask.point(lambda v: int(v * a)))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 6, y0 + 14, x0 + cw + 6, y0 + ch + bar + 14), radius=18,
                                             fill=(40, 30, 20, int(70 * a)))
    out = out.convert("RGBA")
    out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(win, (x0, y0))
    return out.convert("RGB")


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
    if s.key == "cockpit":
        im = browser(im, t, s, a)
    brand(layer, (1 - end_in) * ease(t / 0.6))
    if s.key == "end":
        end_card(layer, end_in)
    else:
        card(ImageDraw.Draw(layer), layer, s, idx, a, a_in)
        if s.key == "listen":
            heard(layer, t, a)
        elif s.key == "talk":
            markup(layer, a)
        elif s.key == "walk":
            walk_map(layer, t, a)
        if s.key not in ("intro", "cockpit"):
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
    sound = PROMO / "voice.wav"
    audio = ["-i", str(sound), "-c:a", "aac", "-b:a", "128k", "-shortest"] if sound.exists() else []
    subprocess.run([ff, *base, *audio, "-c:v", "libx264", "-profile:v", "high", "-crf", "21",
                    "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(args.out)], check=True)
    # H.264 only: plays everywhere, and the VP9 WebM this ffmpeg made failed to decode in Chromium.
    poster = Image.open(work / f"{int(3.5 * story.FPS):05d}.jpg")  # intro: the rig, the desk, the agent
    poster.save(args.out.with_name(args.out.stem + "-poster.jpg"), quality=88)
    print(args.out)


if __name__ == "__main__":
    main()
