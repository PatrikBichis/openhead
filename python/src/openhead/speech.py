"""Text with cues in square brackets -> `speech.say` segments.

    parse("[happy] Why did the robot go on holiday? [pause 0.5] To recharge! [laugh]")

A cue is a word in brackets with an optional number: an emotion from `face.list` (`[sad 0.5]`
sets intensity 0.5), an action (`laugh`, `sigh`, `blink`, `pause 0.5`) or a gesture for a body
(`nod`, `shake`, `tilt`). A few words people reach for that are not expression names map to the
closest one (`serious` -> `focused`). Everything outside brackets is spoken. Unknown words in
brackets are spoken as emotions and fall back to neutral on the head (with a warning in its log).
"""

from __future__ import annotations

import re

ACTIONS = ("laugh", "sigh", "pause", "blink")
GESTURES = ("nod", "shake", "tilt")
ALIASES = {
    "serious": "focused", "calm": "neutral", "joy": "happy", "joyful": "happy", "glad": "happy",
    "sorry": "sad", "upset": "sad", "afraid": "scared", "fear": "scared", "think": "thinking",
    "amazed": "surprised", "wow": "surprised", "excitement": "excited", "giggle": "laugh",
    "chuckle": "laugh", "haha": "laugh", "laughs": "laugh", "sighs": "sigh", "nods": "nod",
    "wait": "pause", "beat": "pause",
}
CUE = re.compile(r"\[\s*([A-Za-z_][\w-]*)(?:\s+([0-9]*\.?[0-9]+))?\s*\]")


def parse(text: str) -> list[dict]:
    """Segments for `speech.say`. Text without cues becomes one `say` segment."""
    segments: list[dict] = []
    pos = 0
    for m in CUE.finditer(text):
        _say(segments, text[pos:m.start()])
        pos = m.end()
        name = ALIASES.get(m.group(1).lower(), m.group(1).lower().replace("-", "_"))
        number = float(m.group(2)) if m.group(2) else None
        if name in ACTIONS:
            seg = {"action": name}
            if name == "pause":
                seg["seconds"] = min(5.0, number if number is not None else 0.5)
            segments.append(seg)
        elif name in GESTURES:
            segments.append({"gesture": name})
        else:
            seg = {"emotion": name}
            if number is not None:
                seg["intensity"] = max(0.0, min(1.0, number))
            segments.append(seg)
    _say(segments, text[pos:])
    if not segments:
        raise ValueError("nothing to say")
    return segments


def _say(segments: list[dict], chunk: str) -> None:
    chunk = " ".join(chunk.split())
    if not chunk:
        return
    while len(chunk) > 2000:               # the protocol's limit per segment
        cut = chunk.rfind(" ", 0, 2000)
        cut = cut if cut > 0 else 2000
        segments.append({"say": chunk[:cut]})
        chunk = chunk[cut:].strip()
    segments.append({"say": chunk})


def spoken_text(segments: list[dict]) -> str:
    """What is said, without the cues (the subtitle)."""
    return " ".join(s["say"] for s in segments if "say" in s)
