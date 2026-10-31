"""Every scenario in scenarios/ passes against the headless simulator, screenshots
matching scenarios/golden/ (written on the first run; review and commit them)."""

from pathlib import Path

import pytest

from openhead.scenario import run_scenario

from .conftest import REPO

SCENARIOS = sorted((REPO / "scenarios").glob("*.yaml"))


@pytest.mark.parametrize("path", SCENARIOS, ids=lambda p: p.stem)
async def test_scenario(head, path: Path, tmp_path: Path):
    report = await run_scenario(head, path, out_dir=tmp_path,
                                golden_dir=REPO / "scenarios" / "golden")
    assert report.passed, report.text()
    assert (tmp_path / "report.json").exists() and (tmp_path / "log.txt").exists()
