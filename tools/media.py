"""Render README and App Store media from the face engine (face/dist must be built).

    cd python
    uv run --with imageio-ffmpeg python ../tools/media.py [stills] [preview] [readme]

stills   App Store screenshots at Apple's exact sizes (apps/ios/appstore/screenshots/),
         README pictures and per-theme emotion sheets (docs/media/)
preview  App Store app preview: 1920x886, 30 fps, H.264 + stereo AAC, 15-30 s, with speech
         (apps/ios/appstore/previews/); also the README GIF and a short mp4 (docs/media/)

Renders the same engine the app ships, in headless Chromium at the device's pixel ratio.
Speech uses a Windows SAPI voice (see examples/demo_video.py); elsewhere it is silent.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import math
import subprocess
import tempfile
import time
from io import BytesIO
from pathlib import Path

from openhead.sim.face import BrowserFace

ROOT = Path(__file__).resolve().parent.parent
APPSTORE = ROOT / "apps" / "ios" / "appstore"
MEDIA = ROOT / "docs" / "media"

# Apple's required sizes, landscape: (name, points, pixel ratio)
DEVICES = [("iphone-6.9", (956, 440), 3),   # 2868 x 1320 (iPhone 16/17 Pro Max class)
           ("ipad-13", (1376, 1032), 2)]    # 2752 x 2064
SCENES = [  # (file, theme, emotion, gaze)
    ("01-cartoon-happy", "cartoon", "happy", (0, 0)),
    ("02-cartoon-curious", "cartoon", "curious", (0.6, -0.2)),
    ("03-halloween-cackle", "halloween", "cackle", (0, 0)),
    ("04-minimal-surprised", "minimal", "surprised", (0, 0)),
    ("05-cartoon-laughing", "cartoon", "laughing", (0, 0)),
    ("06-halloween-scared", "halloween", "scared", (-0.5, 0.2)),
]
# Camera view scenes for the App Store: the HUD over the synthetic camera (two people).
HUD_SCENES = [("07-hud-hunter", "hunter"), ("08-hud-flight", "flight")]
HUD_FACES = [
    {"id": 3, "bearing": 12, "elevation": -4, "size": 0.2, "confidence": 0.94,
     "box": {"x": 0.26, "y": 0.2, "w": 0.16, "h": 0.34}},
    {"id": 7, "bearing": -20, "elevation": 3, "size": 0.1, "confidence": 0.81,
     "box": {"x": 0.68, "y": 0.28, "w": 0.09, "h": 0.19}},
]
HUD_VALUES = {"battery": 82, "charging": False, "thermal": "nominal", "heading": 47, "pitch": 4.5,
              "roll": -3, "x": 0.4, "y": 0.02, "z": -1.2, "tracking": "normal", "mode": "capture",
              "clients": 1}
EMOTIONS = ["neutral", "happy", "curious", "thinking", "surprised", "sad", "angry", "sleepy",
            "scared", "mischievous", "confused", "shocked", "excited", "bored", "skeptical",
            "worried", "disgusted", "embarrassed", "proud", "determined", "relieved", "annoyed",
            "suspicious", "laughing", "disappointed", "focused", "nervous", "smug"]


def demo_module():
    """examples/demo_video.py: speech synthesis, envelope and ffmpeg helpers."""
    spec = importlib.util.spec_from_file_location("demo_video", ROOT / "examples" / "demo_video.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def pose(face: BrowserFace, theme: str, emotion: str, gaze: tuple[float, float]) -> None:
    await face.set_theme(theme, 0)
    await face.set_emotion(emotion, 1.0, "replace", None)
    await face.set_gaze(*gaze)
    await asyncio.sleep(0.9)  # let the transition settle


async def shot(face: BrowserFace) -> bytes:
    return await face._page.screenshot(type="png")


def save_png(png: bytes, path: Path, *, max_width: int | None = None) -> None:
    from PIL import Image

    image = Image.open(BytesIO(png)).convert("RGB")
    if max_width and image.width > max_width:
        image = image.resize((max_width, round(image.height * max_width / image.width)),
                             Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)
    print(f"{path.relative_to(ROOT)}  {image.width}x{image.height}  {path.stat().st_size // 1024} KB")


async def stills() -> None:
    from PIL import Image, ImageDraw, ImageFont

    for device, size, ratio in DEVICES:
        face = BrowserFace(size=size, idle=False, pixel_ratio=ratio)
        await face.start()
        try:
            for name, theme, emotion, gaze in SCENES:
                await pose(face, theme, emotion, gaze)
                save_png(await shot(face), APPSTORE / "screenshots" / device / f"{name}.png")
            await face.set_theme("cartoon", 0)
            await face.set_emotion("happy", 1.0, "replace", None)
            for name, hud in HUD_SCENES:
                await face.show_camera(hud)
                await face.set_faces(HUD_FACES)
                await face.set_hud_values(HUD_VALUES)
                await asyncio.sleep(1.2)
                save_png(await shot(face), APPSTORE / "screenshots" / device / f"{name}.png")
            await face.clear()
        finally:
            await face.close()

    face = BrowserFace(size=(844, 390), idle=False, pixel_ratio=2)
    await face.start()
    try:
        for name, theme, emotion, gaze in SCENES:
            await pose(face, theme, emotion, gaze)
            save_png(await shot(face), MEDIA / f"{name.split('-', 1)[1]}.png", max_width=1200)
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except OSError:
            font = ImageFont.load_default()
        for theme in ("cartoon", "minimal", "halloween"):
            names = EMOTIONS + (["cackle"] if theme == "halloween" else [])
            tiles = []
            for emotion in names:
                await pose(face, theme, emotion, (0, 0))
                tiles.append((emotion, Image.open(BytesIO(await shot(face))).convert("RGB")))
            w, h = 560, 259  # tile size
            cols, label = 6, 40
            rows = math.ceil(len(tiles) / cols)
            sheet = Image.new("RGB", (cols * w, rows * (h + label)), "white")
            draw = ImageDraw.Draw(sheet)
            for i, (emotion, image) in enumerate(tiles):
                x, y = (i % cols) * w, (i // cols) * (h + label)
                sheet.paste(image.resize((w, h), Image.Resampling.LANCZOS), (x, y + label))
                draw.text((x + 12, y + 6), emotion, fill="black", font=font)
            out = BytesIO()
            sheet.save(out, format="PNG")
            save_png(out.getvalue(), MEDIA / f"emotions-{theme}.png", max_width=1800)
    finally:
        await face.close()


LINES = {
    "intro": "Hi! I'm Open Head. A phone that works as a robot's face.",
    "feel": "I can show how I feel.",
    "style": "And change my style in a second.",
    "cackle": "Ha ha ha ha!",
    "outro": "Your robot decides what I say, and how I feel.",
}


async def preview() -> None:
    demo = demo_module()
    out = APPSTORE / "previews" / "iphone-6.9-landscape.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        speech = {k: demo.read_wav(p) for k, p in demo.synthesize(LINES, work).items()}
        # Full-size viewport: Playwright records CSS pixels, so a pixel ratio would not help.
        face = BrowserFace(size=(1920, 886), idle=True, record_video_dir=work / "video")
        await face.start()
        audio: list = []

        async def say(key: str, during: list[tuple[float, str, str | None]] = ()) -> None:
            samples = speech.get(key)
            if samples is None:
                await asyncio.sleep(len(LINES[key]) / 15)
                return
            audio.append((time.monotonic() - face.video_started, samples))
            changes = sorted(during)
            start = time.monotonic()
            for i, level in enumerate(demo.envelope(samples)):
                while changes and changes[0][0] <= i / demo.ENVELOPE_HZ:
                    _, emotion, theme = changes.pop(0)
                    if theme:
                        await face.set_theme(theme, 400)
                    await face.set_emotion(emotion, 1.0, "replace", None)
                await face.envelope(level)
                await asyncio.sleep(max(0.0, start + (i + 1) / demo.ENVELOPE_HZ - time.monotonic()))
            await face.envelope(0)

        async def emotions(names: list[str], hold: float) -> None:
            for name in names:
                await face.set_emotion(name, 1.0, "replace", None)
                await asyncio.sleep(hold)

        try:
            await face.set_emotion("happy", 1.0, "replace", None)
            await asyncio.sleep(0.8)
            await say("intro")
            await say("feel", [(0.3, "curious", None), (0.9, "surprised", None)])
            await emotions(["laughing", "skeptical", "angry", "sad", "sleepy", "shocked",
                            "mischievous", "happy"], 0.75)
            await say("style", [(0.4, "happy", "minimal"), (1.2, "excited", "halloween")])
            await asyncio.sleep(0.6)
            await face.set_emotion("cackle", 1.0, "replace", None)
            await say("cackle")
            await emotions(["scared", "suspicious"], 0.8)
            await face.set_theme("cartoon", 400)
            await face.set_emotion("happy", 1.0, "replace", None)
            for x, y in ((-0.7, 0.1), (0.7, 0.1), (0, 0)):
                await face.set_gaze(x, y)
                await asyncio.sleep(0.5)
            await say("outro", [(1.2, "proud", None), (2.4, "happy", None)])
            await asyncio.sleep(1.2)
            length = time.monotonic() - face.video_started
        finally:
            await face.close()

        wav = None
        if audio:
            wav = work / "speech.wav"
            demo.mix(audio, length, wav)
        encode(face.video_path, wav, out, length)
        readme_media(out)
    print(f"{out.relative_to(ROOT)} ({length:.1f} s)")


def ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def encode(video: Path, wav: Path | None, out: Path, length: float) -> None:
    """App Store app preview: H.264 high, 30 fps, 1920x886, stereo AAC 48 kHz, <= 30 s."""
    out.parent.mkdir(parents=True, exist_ok=True)
    seconds = min(length - 0.3, 29.5)  # the last recorded frame is black
    if seconds < 15:
        raise SystemExit(f"preview is {seconds:.1f} s; the App Store needs 15-30 s")
    cmd = [ffmpeg(), "-y", "-loglevel", "error", "-i", str(video)]
    if wav:
        cmd += ["-i", str(wav)]
    else:  # previews must carry an audio track
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
    cmd += ["-t", f"{seconds:.2f}", "-map", "0:v", "-map", "1:a",
            "-vf", "scale=1920:886:flags=lanczos,fps=30,format=yuv420p",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.0", "-crf", "16",
            "-c:a", "aac", "-b:a", "256k", "-ac", "2", "-ar", "48000",
            "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


def readme_media(preview_mp4: Path) -> None:
    """A GIF for the README (GitHub plays it inline) and a smaller mp4 with sound."""
    MEDIA.mkdir(parents=True, exist_ok=True)
    gif = MEDIA / "openhead.gif"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-t", "16", "-i", str(preview_mp4),
                    "-filter_complex",
                    ("fps=12,scale=640:-1:flags=lanczos,split[a][b];"
                     "[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4"),
                    str(gif)], check=True)
    mp4 = MEDIA / "openhead-preview.mp4"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(preview_mp4),
                    "-vf", "scale=1280:-2", "-c:v", "libx264", "-crf", "26",
                    "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(mp4)], check=True)
    for f in (gif, mp4):
        print(f"{f.relative_to(ROOT)}  {f.stat().st_size // 1024} KB")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("what", nargs="*", choices=["stills", "preview"],
                        default=["stills", "preview"])
    args = parser.parse_args()
    if "stills" in args.what:
        await stills()
    if "preview" in args.what:
        await preview()


if __name__ == "__main__":
    asyncio.run(main())
