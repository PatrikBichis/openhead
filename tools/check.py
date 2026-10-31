"""Run every local check (level 1). This replaces CI testing: GitHub Actions only builds
the iOS app for TestFlight. Also runs as the git pre-push hook.

    uv run --project python python tools/check.py           # everything
    uv run --project python python tools/check.py --fast    # skip face build/Playwright and Swift

Swift models are compiled and round-tripped when `swiftc` is on PATH or installed in WSL;
otherwise that check is reported as skipped.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WIN = sys.platform == "win32"
SWIFT_SOURCES = "apps/ios/OpenHead/Protocol/*.swift tools/swift_contract/main.swift"


def run(name: str, cmd: list[str] | str, cwd: Path = ROOT, shell: bool = False) -> bool:
    start = time.monotonic()
    print(f"\n=== {name}", flush=True)
    ok = subprocess.run(cmd, check=False, cwd=cwd, shell=shell).returncode == 0
    print(f"--- {name}: {'ok' if ok else 'FAILED'} ({time.monotonic() - start:.1f}s)", flush=True)
    return ok


def swift_command() -> list[str] | None:
    script = (
        f"swiftc -swift-version 6 -o /tmp/openhead-contract {SWIFT_SOURCES}"
        " && /tmp/openhead-contract protocol/examples"
    )
    if shutil.which("swiftc") and not WIN:
        return ["bash", "-c", script]
    if WIN and shutil.which("wsl"):
        probe = subprocess.run(["wsl", "-e", "bash", "-lc", "command -v swiftc"], check=False,
                               capture_output=True)
        if probe.returncode == 0:
            path = subprocess.run(["wsl", "wslpath", "-a", str(ROOT)], check=True, capture_output=True,
                                  text=True).stdout.strip()
            return ["wsl", "-e", "bash", "-lc", f"cd '{path}' && {script}"]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fast", action="store_true", help="skip face build/tests and Swift")
    args = parser.parse_args()

    uv = ["uv", "run", "--project", "python"]
    results: dict[str, bool] = {}
    skipped: list[str] = []

    def check(name: str, cmd: list[str] | str, cwd: Path = ROOT, shell: bool = False) -> bool:
        results[name] = run(name, cmd, cwd, shell)
        return results[name]

    check("protocol: schemas, examples, themes", [*uv, "python", "tools/protocol.py", "check"])
    check("protocol: generated files up to date",
          [*uv, "python", "tools/protocol.py", "generate", "--check"])
    check("python: ruff", ["uv", "run", "ruff", "check", ".", "../tools"], cwd=ROOT / "python")

    face = ROOT / "face"
    if args.fast:
        skipped += ["face build and Playwright", "swift"]
    else:
        if not (face / "node_modules").exists():
            run("face: npm ci", "npm ci", cwd=face, shell=True)
        # Built before pytest: the simulator renders face/dist.
        if check("face: build", "npm run build", cwd=face, shell=True):
            check("face: playwright", "npx playwright test", cwd=face, shell=True)
    # Contract, simulator, scenario and CLI tests (simulator tests skip without face/dist).
    check("python: pytest (protocol, simulator, scenarios, CLI)", ["uv", "run", "pytest", "-q"],
          cwd=ROOT / "python")
    if not args.fast:
        swift = swift_command()
        if swift:
            check("swift: models compile and round-trip", swift)
        else:
            skipped.append("swift (no swiftc locally or in WSL; see docs/dev-loop.md)")

    print("\n=== summary")
    for name, ok in results.items():
        print(f"{'ok    ' if ok else 'FAILED'} {name}")
    for name in skipped:
        print(f"skip   {name}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
