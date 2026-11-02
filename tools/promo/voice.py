"""The promo's sound: the person's question and the head's answer, with the head's mouth envelope.

    cd python
    uv run python ../tools/promo/voice.py ../build/promo

Speaks the lines with Windows' own voices (System.Speech, via PowerShell), lays them on one
track at the times story.py gives, and writes `voice.wav` and `voice.json`: when each line
starts and the loudness of the head's voice per film frame, which screen.py streams to the
face as the envelope (as the app does with its own voice) and compose.py muxes into the film.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import story

RATE = 22050
HEAD_VOICE = ("Microsoft Zira Desktop", "+8%", 1)      # name, pitch, rate (-10..10)
PERSON_VOICE = ("Microsoft David Desktop", "default", 0)


def speak(text: str, voice: tuple[str, str, int], out: Path) -> None:
    name, pitch, rate = voice
    ssml = (f"<speak version='1.0' xml:lang='en-US'><prosody pitch='{pitch}'>{text}</prosody></speak>")
    ps = (
        "Add-Type -AssemblyName System.Speech;"
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        f"$s.SelectVoice('{name}'); $s.Rate = {rate};"
        f"$f = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo({RATE}, 'Sixteen', 'Mono');"
        f"$s.SetOutputToWaveFile('{out}', $f); $s.SpeakSsml(\"{ssml}\"); $s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)


def samples(path: Path) -> list[float]:
    with wave.open(str(path)) as w:
        raw = w.readframes(w.getnframes())
    vals = struct.unpack(f"<{len(raw) // 2}h", raw)
    # trim the silence SAPI puts around a line
    lo = next((i for i, v in enumerate(vals) if abs(v) > 300), 0)
    hi = len(vals) - next((i for i, v in enumerate(reversed(vals)) if abs(v) > 300), 0)
    return [v / 32768 for v in vals[lo:hi]]


def lines() -> list[tuple[float, str, str]]:
    """(wanted start in s, who, text): the question in the listen scene, then the head's cues."""
    out = []
    for s in story.SCENES:
        if s.key == "listen":
            out.append((s.start + 0.4, "person", story.HEARD))
        for at, kind, value in s.cues:
            if kind == "say":
                out.append((s.start + at, "head", value.strip()))
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("out", type=Path)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    track = [0.0] * int(story.LENGTH * RATE)
    head = [0.0] * len(track)
    clips = []
    free = 0.0  # a line never starts before the last one ended, as speech.say queues them
    with tempfile.TemporaryDirectory() as tmp:
        for i, (want, who, text) in enumerate(lines()):
            wav = Path(tmp) / f"{i}.wav"
            speak(text, HEAD_VOICE if who == "head" else PERSON_VOICE, wav)
            pcm = samples(wav)
            start = max(want, free) if who == "head" else want
            a = int(start * RATE)
            for k, v in enumerate(pcm[: len(track) - a]):
                track[a + k] += v * (1.0 if who == "head" else 0.85)
                if who == "head":
                    head[a + k] = v
            end = start + len(pcm) / RATE
            if who == "head":
                free = end + 0.12
            clips.append({"who": who, "text": text, "start": round(start, 3), "end": round(end, 3)})
            print(f"{who:6} {start:6.2f}-{end:6.2f}  {text}")
    # the head's loudness per frame (RMS over the frame), scaled so speech opens the mouth well
    per = RATE // story.FPS
    rms = []
    for n in range(story.FRAMES):
        chunk = head[n * per:(n + 1) * per]
        rms.append(math.sqrt(sum(v * v for v in chunk) / max(1, len(chunk))))
    peak = sorted(rms)[int(len(rms) * 0.995)] or 1.0
    envelope = [round(min(1.0, (v / peak) ** 0.7), 3) for v in rms]
    with wave.open(str(args.out / "voice.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(struct.pack(f"<{len(track)}h", *(int(max(-1, min(1, v)) * 32000) for v in track)))
    (args.out / "voice.json").write_text(json.dumps({"clips": clips, "envelope": envelope}), encoding="utf-8")
    print("wrote", args.out / "voice.wav")


if __name__ == "__main__":
    main()
