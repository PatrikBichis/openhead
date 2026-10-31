"""Scenario runner: YAML steps run against the simulator or a real head.

```yaml
name: halloween-scared
steps:
  - set_theme: halloween
  - set_emotion: { name: scared, intensity: 1.0 }
  - wait_ms: 600
  - screenshot: halloween-scared.png
  - expect_log: { level: info, contains: "theme=halloween" }
  - expect_status: { theme: halloween, emotion: scared }
```

Steps: set_theme, set_emotion, look_at, blink, show_image, show_web, show_face,
clear_display, envelope, wait_ms, screenshot, expect_log, expect_status.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml

from .client import Head, HeadError
from .protocol import models

LEVELS = ["debug", "info", "notice", "warning", "error", "fault"]


@dataclass
class StepResult:
    index: int
    step: str
    ok: bool
    detail: str = ""
    duration_ms: int = 0
    artifact: str | None = None


@dataclass
class ScenarioReport:
    name: str
    device: str
    passed: bool
    out_dir: str
    steps: list[StepResult] = field(default_factory=list)

    def text(self) -> str:
        lines = [f"scenario {self.name} on {self.device}: {'PASS' if self.passed else 'FAIL'}"]
        for s in self.steps:
            mark = "ok  " if s.ok else "FAIL"
            extra = f" -> {s.artifact}" if s.artifact else ""
            lines.append(f"  {mark} {s.index:>2} {s.step}{extra}" + (f"  ({s.detail})" if s.detail else ""))
        lines.append(f"report: {self.out_dir}")
        return "\n".join(lines)


class StepFailed(Exception):
    pass


async def run_scenario(head: Head, path: Path, *, out_dir: Path | None = None,
                       golden_dir: Path | None = None, update_golden: bool = False,
                       tolerance: float = 0.01) -> ScenarioReport:
    """Run one scenario file. `golden_dir` enables screenshot comparison (simulator)."""
    spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    name = spec.get("name", path.stem)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = out_dir or Path("scenario-reports") / f"{name}-{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    device = head.welcome.device.name if head.welcome else head.key
    report = ScenarioReport(name=name, device=device, passed=True, out_dir=str(out))

    logs: list[models.Log] = []
    sub = head.subscribe("log")
    await sub.start()

    async def collect() -> None:
        async for entry in sub:
            logs.append(entry)

    collector = asyncio.create_task(collect())
    runner = _Runner(head, path.parent, out, logs, golden_dir and golden_dir / name,
                     update_golden, tolerance)
    try:
        for i, step in enumerate(spec.get("steps", []), 1):
            if isinstance(step, str):  # bare step without arguments, e.g. `- blink`
                step = {step: None}
            if not isinstance(step, dict) or len(step) != 1:
                report.steps.append(StepResult(i, repr(step), False,
                                               "step must be a name or a one-key map"))
                continue
            (kind, arg), = step.items()
            label = f"{kind}: {json.dumps(arg)}" if arg is not None else kind
            start = time.monotonic()
            result = StepResult(i, label, True)
            try:
                handler = getattr(runner, f"step_{kind}", None)
                if handler is None:
                    raise StepFailed(f"unknown step {kind!r}")
                outcome = await handler(arg)
                if isinstance(outcome, tuple):
                    result.artifact, result.detail = outcome
                elif outcome:
                    result.detail = outcome
            except (TimeoutError, StepFailed, HeadError, OSError) as exc:
                result.ok = False
                result.detail = str(exc)
            result.duration_ms = int((time.monotonic() - start) * 1000)
            report.steps.append(result)
    finally:
        await sub.close()
        collector.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await collector

    report.passed = all(s.ok for s in report.steps)
    (out / "log.txt").write_text(
        "\n".join(f"{e.time_ms} {e.level:<7} {e.subsystem:<9} {e.message}"
                  + (f" (seq {e.seq_ref})" if e.seq_ref is not None else "") for e in logs) + "\n",
        encoding="utf-8")
    (out / "report.json").write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return report


class _Runner:
    def __init__(self, head: Head, base: Path, out: Path, logs: list, golden: Path | None,
                 update_golden: bool, tolerance: float):
        self.head = head
        self.base = base
        self.out = out
        self.logs = logs
        self.golden = golden
        self.update_golden = update_golden
        self.tolerance = tolerance

    @staticmethod
    def _args(arg: Any, key: str) -> dict:
        return dict(arg) if isinstance(arg, dict) else {key: arg}

    async def step_set_theme(self, arg: Any) -> None:
        a = self._args(arg, "name")
        await self.head.face.set_theme(a["name"], a.get("transition_ms"))

    async def step_set_emotion(self, arg: Any) -> None:
        a = self._args(arg, "name")
        await self.head.face.set_emotion(a["name"], a.get("intensity", 1.0),
                                         duration_ms=a.get("duration_ms"),
                                         blend=a.get("blend", "replace"))

    async def step_look_at(self, arg: dict) -> None:
        frame = arg.get("frame", "screen")
        x, y = (arg["x"], arg["y"]) if frame == "screen" else (arg["yaw"], arg["pitch"])
        await self.head.face.look_at(x, y, frame=frame, duration_ms=arg.get("duration_ms"))

    async def step_blink(self, _: Any) -> None:
        await self.head.face.blink()

    async def step_show_image(self, arg: Any) -> None:
        a = self._args(arg, "source")
        source = a["source"]
        if not source.startswith(("http://", "https://", "data:")):
            source = (self.base / source).read_bytes()
        await self.head.display.show_image(source, overlay=a.get("overlay", "none"),
                                           duration_ms=a.get("duration_ms"))

    async def step_show_web(self, arg: Any) -> None:
        a = self._args(arg, "url")
        await self.head.display.show_web(a["url"], overlay=a.get("overlay", "none"),
                                         duration_ms=a.get("duration_ms"))

    async def step_show_face(self, _: Any) -> None:
        await self.head.display.show_face()

    async def step_clear_display(self, _: Any) -> None:
        await self.head.display.clear()

    async def step_envelope(self, arg: dict) -> str:
        """Drive the mouth: `{level: 0.6, duration_ms: 1000, hz: 25}` (level may be a list)."""
        levels = arg["level"] if isinstance(arg["level"], list) else [arg["level"]]
        hz = arg.get("hz", 25)
        count = max(1, int(arg.get("duration_ms", 1000) * hz / 1000))
        for i in range(count):
            await self.head.face.envelope(levels[i % len(levels)])
            await asyncio.sleep(1 / hz)
        return f"{count} frames at {hz} Hz"

    async def step_wait_ms(self, arg: int) -> None:
        await asyncio.sleep(arg / 1000)

    async def step_screenshot(self, arg: Any) -> tuple[str, str]:
        a = self._args(arg, "file")
        png = await self.head.system.screenshot(a.get("scale"))
        target = self.out / a["file"]
        target.write_bytes(png)
        if not self.golden:
            return str(target), ""
        golden = self.golden / a["file"]
        if self.update_golden or not golden.exists():
            golden.parent.mkdir(parents=True, exist_ok=True)
            golden.write_bytes(png)
            return str(target), "golden written"
        diff = _diff_ratio(golden.read_bytes(), png)
        limit = a.get("tolerance", self.tolerance)
        if diff > limit:
            raise StepFailed(f"differs from golden {golden.name}: {diff:.2%} > {limit:.2%}")
        return str(target), f"matches golden ({diff:.2%} differs)"

    async def step_expect_log(self, arg: dict) -> str:
        floor = LEVELS.index(arg.get("level", "debug"))
        deadline = time.monotonic() + arg.get("timeout_ms", 1000) / 1000
        while True:
            for e in self.logs:
                if (LEVELS.index(e.level) >= floor and arg.get("contains", "") in e.message
                        and arg.get("subsystem", e.subsystem) == e.subsystem):
                    return e.message
            if time.monotonic() > deadline:
                raise StepFailed(f"no log line matching {arg} among {len(self.logs)}")
            await asyncio.sleep(0.05)

    async def step_expect_status(self, arg: dict) -> None:
        deadline = time.monotonic() + arg.get("timeout_ms", 1000) / 1000
        expected = {k: v for k, v in arg.items() if k != "timeout_ms"}
        while True:
            status = (await self.head.system.status()).model_dump()
            wrong = {k: status.get(k) for k, v in expected.items() if status.get(k) != v}
            if not wrong:
                return
            if time.monotonic() > deadline:
                raise StepFailed(f"status has {wrong}, expected {expected}")
            await asyncio.sleep(0.1)


def _diff_ratio(a: bytes, b: bytes) -> float:
    """Share of pixels whose largest channel difference exceeds 20 % (1.0 if sizes differ)."""
    from PIL import Image, ImageChops

    ia = Image.open(BytesIO(a)).convert("RGB")
    ib = Image.open(BytesIO(b)).convert("RGB")
    if ia.size != ib.size:
        return 1.0
    diff = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v > 51 else 0)
    return diff.histogram()[255] / (ia.width * ia.height)
