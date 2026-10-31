"""Record a head's sensor streams and draw them as SVG charts for the website.

    uv run --project python python tools/sensor_plots.py [--device HOST] [--seconds 10]
        [--label "iPhone 18 Pro"] [--out docs/media/sensors]

Records `imu` and `faces` in mode `capture`, then `pose` and `imu` in mode `sensing`, and
writes CSV files plus one chart per measure (one y-axis each): orientation, acceleration,
rotation rate, face bearings, position over time and the path seen from above. Point it at
the simulator for synthetic data, or at a phone (move it around, stand in front of it).
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import html
import math
import os
import sys
import time
from pathlib import Path

from openhead.cli.main import _load_dotenv
from openhead.client import Head, resolve_device

ROOT = Path(__file__).resolve().parent.parent
# Categorical slots 1-3 of the dataviz reference palette, validated on the light surface.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e4df", "#fcfcfb"


def nice(lo: float, hi: float, n: int = 4) -> list[float]:
    span = (hi - lo) or 1
    step = 10 ** math.floor(math.log10(span / n))
    for m in (1, 2, 5, 10):
        if span / (step * m) <= n:
            step *= m
            break
    start = math.floor(lo / step) * step
    return [round(start + i * step, 10) for i in range(int((hi - start) / step) + 2)]


def chart(title: str, unit: str, series: dict[str, list[tuple[float, float]]], *, xlabel: str = "time (s)",
          equal: bool = False, w: int = 640, h: int = 260) -> str:
    """A line chart: one y-axis, thin 2 px lines, legend plus labels at the line ends."""
    left, right, top, bottom = 52, 92, 52, 38
    pts = [p for s in series.values() for p in s]
    if not pts:
        return ""
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    xt, yt = nice(min(xs), max(xs), 6), nice(min(ys), max(ys), 4)
    x0, x1, y0, y1 = min(xs), max(xs), yt[0], yt[-1]
    xt = [t for t in xt if x0 - 1e-9 <= t <= x1 + 1e-9]
    if equal:  # same metres per pixel on both axes (a path seen from above)
        sx = (w - left - right) / (x1 - x0)
        sy = (h - top - bottom) / (y1 - y0)
        s = min(sx, sy)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        x0, x1 = cx - (w - left - right) / s / 2, cx + (w - left - right) / s / 2
        y0, y1 = cy - (h - top - bottom) / s / 2, cy + (h - top - bottom) / s / 2
        xt = [t for t in nice(x0, x1, 6) if x0 <= t <= x1]
        yt = [t for t in nice(y0, y1, 4) if y0 <= t <= y1]

    def X(v: float) -> float:
        return left + (v - x0) / (x1 - x0) * (w - left - right)

    def Y(v: float) -> float:
        return h - bottom - (v - y0) / (y1 - y0) * (h - top - bottom)

    out = [(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
           f'aria-label="{html.escape(title)}" font-family="system-ui, -apple-system, Segoe UI, sans-serif">'),
           f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>',
           f'<text x="{left}" y="20" font-size="14" font-weight="600" fill="{INK}">{html.escape(title)}</text>',
           f'<text x="{w - right}" y="20" font-size="12" fill="{MUTED}" text-anchor="end">{html.escape(unit)}</text>']
    for t in yt:
        out.append(f'<line x1="{left}" x2="{w - right}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{left - 8}" y="{Y(t) + 4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">{t:g}</text>')
    for t in xt:
        if x0 <= t <= x1:
            out.append(f'<text x="{X(t):.1f}" y="{h - bottom + 16}" font-size="11" fill="{MUTED}" '
                       f'text-anchor="middle">{t:g}</text>')
    out.append(f'<text x="{(left + w - right) / 2}" y="{h - 6}" font-size="11" fill="{MUTED}" '
               f'text-anchor="middle">{html.escape(xlabel)}</text>')
    # legend (always for 2+ series), then the lines, each labelled at its end
    lx = left
    for i, name in enumerate(series if len(series) > 1 else []):
        out.append(f'<rect x="{lx}" y="33" width="12" height="3" rx="1.5" fill="{SERIES[i % 3]}"/>')
        out.append(f'<text x="{lx + 16}" y="39" font-size="12" fill="{MUTED}">{html.escape(name)}</text>')
        lx += 22 + 7.2 * len(name) + 14
    # end labels, pushed apart so they never overlap
    ends = sorted(((Y(s[-1][1]), i, name) for i, (name, s) in enumerate(series.items()) if s), key=lambda e: e[0])
    label_y: dict[str, float] = {}
    last = -1e9
    for y, _, name in ends:
        last = max(y, last + 13)
        label_y[name] = last
    for i, (name, s) in enumerate(series.items()):
        if not s:
            continue
        color = SERIES[i % 3]
        path = " ".join(f"{'M' if j == 0 or s[j][0] < s[j - 1][0] - 0.5 else 'L'}{X(px):.1f},{Y(py):.1f}"
                        for j, (px, py) in enumerate(s))
        out.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" '
                   f'stroke-linecap="round"><title>{html.escape(name)}</title></path>')
        ex, ey = s[-1]
        out.append(f'<circle cx="{X(ex):.1f}" cy="{Y(ey):.1f}" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>')
        if equal:  # a path: mark where it started and ended
            sx_, sy_ = s[0]
            out.append(f'<circle cx="{X(sx_):.1f}" cy="{Y(sy_):.1f}" r="4" fill="{SURFACE}" stroke="{color}" stroke-width="2"/>')
            out.append(f'<text x="{X(sx_) + 8:.1f}" y="{Y(sy_) + 4:.1f}" font-size="11" fill="{INK}">start</text>')
            out.append(f'<text x="{X(ex) + 8:.1f}" y="{Y(ey) + 4:.1f}" font-size="11" fill="{INK}">end</text>')
        else:
            out.append(f'<text x="{X(ex) + 8:.1f}" y="{label_y[name] + 4:.1f}" font-size="11" fill="{INK}">'
                       f'{html.escape(name)} {ey:.2f}</text>')
    out.append("</svg>")
    return "\n".join(out)


async def record(head: Head, topics: dict[str, float], seconds: float) -> dict[str, list]:
    data: dict[str, list] = {t: [] for t in topics}
    t0 = time.monotonic()

    async def follow(topic: str, rate: float) -> None:
        async with head.subscribe(topic, rate) as sub:
            async for msg in sub:
                data[topic].append((time.monotonic() - t0, msg))
                if time.monotonic() - t0 > seconds:
                    return

    await asyncio.wait_for(asyncio.gather(*(follow(t, r) for t, r in topics.items())), seconds + 10)
    return data


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def tilt(ax: float, ay: float, az: float) -> tuple[float, float]:
    """Pitch and roll in degrees as a viewer sees a phone in landscape-right (as the app's HUD):
    pitch + when the screen tilts up, roll + when it turns clockwise."""
    up, right = ax, -ay
    return (math.degrees(math.atan2(az, math.hypot(up, right))), math.degrees(math.atan2(right, up)))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def draw(out: Path, label: str) -> None:
    """Charts from the CSV files in `out` (written by a recording, or kept from an earlier one)."""
    label = f" · {label}"
    imu = [{k: float(v) for k, v in r.items()} for r in read_csv(out / "imu.csv")]
    faces = read_csv(out / "faces.csv")
    pose = read_csv(out / "pose.csv")
    tilts = [(r["t_s"], *tilt(r["ax"], r["ay"], r["az"])) for r in imu]
    charts = {
        "orientation": chart(f"Tilt (imu){label}", "degrees",
                             {"pitch": [(t, p) for t, p, _ in tilts], "roll": [(t, r) for t, _, r in tilts]}),
        "acceleration": chart(f"Acceleration (imu){label}", "m/s²",
                              {k: [(r["t_s"], r["a" + k]) for r in imu] for k in "xyz"}),
        "rotation": chart(f"Rotation rate (imu){label}", "rad/s",
                          {k: [(r["t_s"], r["g" + k]) for r in imu] for k in "xyz"}),
    }
    by_id: dict[str, list] = {}
    for r in faces:  # bearing per face id, the first three ids seen
        if r["id"] in by_id or len(by_id) < 3:
            by_id.setdefault(r["id"], []).append((float(r["t_s"]), float(r["bearing_deg"])))
    charts["faces"] = chart(f"Face bearing (faces){label}", "degrees, + is the head's left",
                            {f"face {i}": v for i, v in by_id.items()})
    tracked = [r for r in pose if r["tracking"] == "normal"] or pose
    charts["position"] = chart(f"Position (pose){label}", "metres",
                               {k: [(float(r["t_s"]), float(r[k])) for r in tracked] for k in "xyz"})
    charts["path"] = chart(f"Path seen from above (pose){label}", "metres",
                           {"path": [(float(r["x"]), float(r["z"])) for r in tracked]},
                           xlabel="x (m), up is z", equal=True)
    for name, svg in charts.items():
        if svg:
            (out / f"{name}.svg").write_text(svg, encoding="utf-8")
            print(out / f"{name}.svg")
    print(f"{len(imu)} imu, {len(faces)} face rows, {len(pose)} pose ({len(tracked)} tracking normal)")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--device")
    parser.add_argument("--seconds", type=float, default=10)
    parser.add_argument("--label", default="iPhone")
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "media" / "sensors")
    parser.add_argument("--from-csv", action="store_true", help="only redraw the charts from the CSV files in --out")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.from_csv:
        draw(args.out, args.label)
        return 0
    _load_dotenv()
    host, port = await resolve_device(args.device or os.environ.get("OPENHEAD_DEVICE", "auto"))
    async with await Head.connect(host, port, auto_reconnect=False) as head:
        if not head.paired:
            print(f"not paired with {head.key}", file=sys.stderr)
            return 1
        await head.mode.set("capture")
        await asyncio.sleep(1)
        capture = await record(head, {"imu": 50, "faces": 15}, args.seconds)
        await head.mode.set("sensing")
        await asyncio.sleep(1.5)
        sensing = await record(head, {"pose": 30}, args.seconds)
        await head.mode.set("idle")

    write_csv(args.out / "imu.csv", ["t_s", "gx", "gy", "gz", "ax", "ay", "az"],
              [[round(t, 3), *m.gyro, *m.accel] for t, m in capture["imu"]])
    write_csv(args.out / "faces.csv", ["t_s", "id", "bearing_deg", "elevation_deg", "size"],
              [[round(t, 3), f.id, f.bearing, f.elevation, f.size] for t, m in capture["faces"] for f in m.faces])
    write_csv(args.out / "pose.csv", ["t_s", "x", "y", "z", "tracking"],
              [[round(t, 3), *m.position, m.tracking_state] for t, m in sensing["pose"]])
    draw(args.out, args.label)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
