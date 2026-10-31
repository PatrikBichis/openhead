"""Measure a head: command round trip, envelope-to-mouth delay and smoothness (plan step 9).

    uv run --project python python tools/latency.py [--device HOST] [--seconds 8] [--out DIR]

1. Round trip of `system.status` and `face.set_emotion` (sent until acknowledged).
2. Envelope: streams a 0.5 Hz sine at 25 Hz to the cartoon mouth while taking screenshots,
   measures how open the mouth is in each one (dark mouth-interior pixels) and finds the delay
   that best lines the two up. A smooth mouth follows the sine closely (high correlation).
3. Frame rate and thermal state before and after.

Needs dev mode on the device (screenshots, diagnostics). Results go to stdout and DIR/latency.json.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import statistics
import sys
import time
from io import BytesIO
from pathlib import Path

from openhead.cli.main import _load_dotenv
from openhead.client import Head, resolve_device

HZ = 25
SINE_HZ = 0.5


def pct(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p / 100 * len(xs)))]


def mouth_open(png: bytes) -> float:
    """Share of the lower-middle screen that is mouth interior (red tongue or dark gap)."""
    from PIL import Image

    img = Image.open(BytesIO(png)).convert("RGB")
    w, h = img.size
    box = img.crop((int(w * 0.3), int(h * 0.55), int(w * 0.7), int(h * 0.98))).resize((160, 80))
    px = box.tobytes()
    inside = sum(1 for i in range(0, len(px), 3)
                 if (px[i] > 140 and px[i + 1] < 90 and px[i + 2] < 90) or px[i] + px[i + 1] + px[i + 2] < 120)
    return inside / (160 * 80)


def correlate(sent: list[tuple[float, float]], seen: list[tuple[float, float]]) -> tuple[float, float]:
    """(delay in ms, correlation) that best aligns what was seen with what was sent."""
    def level_at(t: float) -> float:
        before = [lv for ts, lv in sent if ts <= t]
        return before[-1] if before else 0.0

    best = (0.0, -1.0)
    ys = [v for _, v in seen]
    for delay_ms in range(0, 401, 5):
        xs = [level_at(t - delay_ms / 1000) for t, _ in seen]
        if statistics.pstdev(xs) == 0 or statistics.pstdev(ys) == 0:
            continue
        r = statistics.correlation(xs, ys)
        if r > best[1]:
            best = (float(delay_ms), r)
    return best


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device", default=None)
    parser.add_argument("--seconds", type=float, default=8)
    parser.add_argument("--out", type=Path, default=Path("scenario-reports/latency"))
    args = parser.parse_args()
    _load_dotenv()
    host, port = await resolve_device(args.device or os.environ.get("OPENHEAD_DEVICE", "auto"))
    result: dict = {}
    async with await Head.connect(host, port, auto_reconnect=False) as head:
        if not head.paired:
            print(f"not paired with {head.key}: run `openhead pair`", file=sys.stderr)
            return 1
        before = (await head.system.diagnostics()).model_dump(exclude_none=True)
        result["device"] = head.welcome.device.model_dump(exclude_none=True)

        # 1. Round trips
        for name, call in (("status", lambda: head.system.status()),
                           ("set_emotion", lambda: head.face.set_emotion("happy"))):
            times = []
            for _ in range(50):
                t = time.perf_counter()
                await call()
                times.append((time.perf_counter() - t) * 1000)
            result[f"rtt_{name}_ms"] = {"p50": round(pct(times, 50), 1), "p95": round(pct(times, 95), 1),
                                        "max": round(max(times), 1)}
            print(f"{name:<12} round trip ms  p50 {pct(times, 50):5.1f}  p95 {pct(times, 95):5.1f}  "
                  f"max {max(times):5.1f}")

        one_way = result["rtt_status_ms"]["p50"] / 2000

        # 2. Envelope while taking screenshots
        await head.face.set_theme("cartoon")
        await head.face.set_emotion("neutral")
        await asyncio.sleep(0.8)
        sent: list[tuple[float, float]] = []
        seen: list[tuple[float, float]] = []
        gaps: list[float] = []
        t0 = time.perf_counter()
        stop = t0 + args.seconds

        async def stream() -> None:
            i = 0
            last = None
            while (now := time.perf_counter()) < stop:
                level = 0.5 - 0.5 * math.cos(2 * math.pi * SINE_HZ * (now - t0))
                await head.face.envelope(level)
                sent.append((now, level))
                if last is not None:
                    gaps.append((now - last) * 1000)
                last = now
                i += 1
                await asyncio.sleep(max(0.0, t0 + i / HZ - time.perf_counter()))
            await head.face.envelope(0)

        async def shoot() -> None:
            while time.perf_counter() < stop:
                t = time.perf_counter()
                png = await head.system.screenshot(0.25, inline=True)
                # The device captures on receipt: one way (half a status round trip) after sending.
                seen.append((t + one_way, mouth_open(png)))

        await asyncio.gather(stream(), shoot())
        delay, r = correlate(sent, seen)
        result["envelope"] = {
            "sent_hz": round(len(sent) / args.seconds, 1),
            "send_gap_ms": {"p50": round(pct(gaps, 50), 1), "p95": round(pct(gaps, 95), 1),
                            "max": round(max(gaps), 1)},
            "screenshots": len(seen),
            "delay_ms": delay,
            "correlation": round(r, 3),
        }
        print(f"envelope     sent {len(sent) / args.seconds:.1f} Hz (gap p95 {pct(gaps, 95):.0f} ms), "
              f"{len(seen)} screenshots; mouth follows with ~{delay:.0f} ms delay, correlation {r:.2f}")

        after = (await head.system.diagnostics()).model_dump(exclude_none=True)
        result["frame_rate"] = {"before": before.get("frame_rate"), "after": after.get("frame_rate")}
        result["thermal_state"] = {"before": before.get("thermal_state"), "after": after.get("thermal_state")}
        print(f"frame rate   {before.get('frame_rate')} -> {after.get('frame_rate')} fps; thermal "
              f"{before.get('thermal_state')} -> {after.get('thermal_state')}")
        await head.face.set_emotion("neutral")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "latency.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (args.out / "envelope.csv").write_text(
        "kind,t_s,value\n" + "".join(f"sent,{t - t0:.3f},{v:.3f}\n" for t, v in sent)
        + "".join(f"seen,{t - t0:.3f},{v:.4f}\n" for t, v in seen), encoding="utf-8")
    print(f"written {args.out / 'latency.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
