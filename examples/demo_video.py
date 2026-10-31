"""Record a demo video of the simulated head: every theme, every emotion, and speech.

Shows how a host drives the head: text-to-speech runs on the host, its loudness is
streamed as `face.envelope` at 25 Hz, and emotions are separate commands that can change
while speaking, layer on top of each other or expire on their own.

    cd python
    uv run --with imageio-ffmpeg python ../examples/demo_video.py -o ../demo/openhead-demo.mp4

Speech uses Windows SAPI voices (PowerShell); elsewhere the video is silent.
"""

from __future__ import annotations

import argparse
import array
import asyncio
import math
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

from openhead.client import Head
from openhead.sim import SimServer
from openhead.tokens import TokenStore

RATE = 22050  # Hz, mono 16-bit for all speech
ENVELOPE_HZ = 25
EMOTIONS = ["neutral", "happy", "curious", "thinking", "surprised", "sad", "angry", "sleepy",
            "scared", "mischievous"]
LINES = {
    "intro": "Hello! I am Open Head. A phone, working as a robot's face.",
    "cartoon": "This is the cartoon theme. Round eyes, a warm palette, and a clear mouth.",
    "minimal": "The minimal theme. Two light bars and a line. Very few pixels, for low power.",
    "halloween": "And this is Halloween. The eyes and the grin are images, not vectors.",
    "angry_talk": "I can talk while I am angry.",
    "mixed": "My mood can change in the middle of a sentence, while my mouth keeps talking.",
    "cackle": "Ha ha ha ha!",
    "outro": "Expressions and speech are separate. The robot decides both.",
}


# --- speech ------------------------------------------------------------------


def synthesize(lines: dict[str, str], out: Path) -> dict[str, Path]:
    """One WAV per line with a Windows SAPI voice; empty dict if unavailable."""
    if sys.platform != "win32":
        return {}
    files = {key: out / f"{key}.wav" for key in lines}
    script = ["Add-Type -AssemblyName System.Speech",
              "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
              "try { $s.SelectVoice('Microsoft Zira Desktop') } catch {}",
              "$s.Rate = 0",
              (f"$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo({RATE}, "
               "[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, "
               "[System.Speech.AudioFormat.AudioChannel]::Mono)")]
    for key, text in lines.items():
        script += [f"$s.SetOutputToWaveFile('{files[key]}', $fmt)", f"$s.Speak(\"{text}\")"]
    script.append("$s.Dispose()")
    subprocess.run(["powershell", "-NoProfile", "-Command", "; ".join(script)], check=True)
    return files


def read_wav(path: Path) -> array.array:
    with wave.open(str(path)) as w:
        assert w.getframerate() == RATE and w.getsampwidth() == 2 and w.getnchannels() == 1
        return array.array("h", w.readframes(w.getnframes()))


def envelope(samples: array.array) -> list[float]:
    """Loudness per 40 ms window, normalised to 0-1 (what a host's TTS pipeline would send)."""
    step = RATE // ENVELOPE_HZ
    rms = [math.sqrt(sum(s * s for s in samples[i:i + step]) / step) or 0.0
           for i in range(0, len(samples) - step + 1, step)]
    peak = sorted(rms)[int(len(rms) * 0.95)] or 1.0
    return [min(1.0, (r / peak) ** 0.8) if r > peak * 0.08 else 0.0 for r in rms]


# --- demo --------------------------------------------------------------------


class Demo:
    def __init__(self, head: Head, sim: SimServer, speech: dict[str, Path]):
        self.head = head
        self.sim = sim
        self.speech = {k: read_wav(p) for k, p in speech.items()}
        self.audio: list[tuple[float, array.array]] = []  # (seconds into the video, samples)

    async def caption(self, text: str | None) -> None:
        await self.sim.face.caption(text)

    async def pause(self, seconds: float) -> None:
        await asyncio.sleep(seconds)

    async def say(self, key: str, during: list[tuple[float, str]] | None = None) -> None:
        """Speak a line: stream its envelope in real time; optionally change emotion at
        given seconds into the line (the mouth keeps going)."""
        samples = self.speech.get(key)
        if samples is None:  # no TTS available: just leave time for reading
            await self.pause(len(LINES[key]) / 15)
            return
        self.audio.append((time.monotonic() - self.sim.face.video_started, samples))
        changes = sorted(during or [])
        start = time.monotonic()
        for i, level in enumerate(envelope(samples)):
            while changes and changes[0][0] <= i / ENVELOPE_HZ:
                await self.head.face.set_emotion(changes.pop(0)[1])
            await self.head.face.envelope(level)
            await asyncio.sleep(max(0.0, start + (i + 1) / ENVELOPE_HZ - time.monotonic()))
        await self.head.face.envelope(0)

    async def emotions(self, names: list[str], hold: float = 1.2) -> None:
        for name in names:
            await self.caption(f"{await self.theme()} · {name}")
            await self.head.face.set_emotion(name)
            await self.pause(hold)

    async def theme(self) -> str:
        return (await self.head.system.status()).theme

    async def run(self) -> None:
        face = self.head.face
        await self.caption("OpenHead")
        await self.pause(0.8)
        await face.set_emotion("happy")
        await self.say("intro")

        for theme in ("cartoon", "minimal", "halloween"):
            await face.set_theme(theme, 500)
            await face.set_emotion("neutral")
            await self.caption(f"theme: {theme}")
            await self.pause(0.6)
            await self.say(theme)
            extras = ["cackle"] if theme == "halloween" else []
            await self.emotions(EMOTIONS + extras)

        await face.set_theme("cartoon", 500)
        await self.caption("speaking while angry")
        await face.set_emotion("angry")
        await self.say("angry_talk")

        await self.caption("mood changes mid-sentence")
        await face.set_emotion("neutral")
        await self.say("mixed", during=[(0.6, "curious"), (1.8, "surprised"), (3.0, "happy")])

        await self.caption("surprised for 1.5 s, on top of happy")
        await face.set_emotion("happy")
        await self.pause(0.6)
        await face.set_emotion("surprised", 1.0, blend="add", duration_ms=1500)
        await self.pause(2.4)

        await self.caption("looking around")
        for x, y in ((-0.8, 0.2), (0.8, 0.2), (0.0, -0.6), (0.0, 0.0)):
            await face.look_at(x, y)
            await self.pause(0.7)

        await face.set_theme("halloween", 500)
        await self.caption("halloween · cackle")
        await face.set_emotion("cackle")
        await self.say("cackle")

        await face.set_theme("cartoon", 500)
        await face.set_emotion("happy")
        await self.caption("emotions ≠ speech")
        await self.say("outro")
        await self.pause(1.0)


def mix(audio: list[tuple[float, array.array]], seconds: float, out: Path) -> None:
    track = array.array("h", bytes(2 * int((seconds + 1) * RATE)))
    for offset, samples in audio:
        start = int(offset * RATE)
        for i, s in enumerate(samples[: len(track) - start]):
            track[start + i] = s
    with wave.open(str(out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(track.tobytes())


def mux(video: Path, audio: Path | None, out: Path) -> None:
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(video)]
    if audio:
        cmd += ["-i", str(audio), "-c:a", "aac", "-b:a", "128k", "-shortest"]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart",
            str(out)]
    subprocess.run(cmd, check=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("-o", "--output", type=Path, default=Path("openhead-demo.mp4"))
    parser.add_argument("--size", default="960x444",
                        help="video size WxH (default: phone in landscape)")
    args = parser.parse_args()
    w, _, h = args.size.partition("x")

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        speech = synthesize(LINES, work)
        sim = SimServer(host="127.0.0.1", port=0, mdns=False, headless=True, idle=True,
                        size=(int(w), int(h)), record_video_dir=work / "video")
        await sim.start()
        try:
            head = await Head.connect("127.0.0.1", sim.port, client="demo",
                                      store=TokenStore(work / "tokens.json"))
            await head.pair("0000")
            demo = Demo(head, sim, speech)
            await demo.run()
            length = time.monotonic() - sim.face.video_started
            await head.close()
        finally:
            await sim.stop()

        audio = None
        if demo.audio:
            audio = work / "speech.wav"
            mix(demo.audio, length, audio)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        mux(sim.face.video_path, audio, args.output)
    print(f"{args.output} ({length:.0f} s)")


if __name__ == "__main__":
    asyncio.run(main())
