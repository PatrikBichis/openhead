"""Contract tests: the generated models agree with the schemas' example messages."""

import json
from pathlib import Path

import pytest

from openhead.protocol import MESSAGE_TYPES, PROTOCOL_VERSION, models, parse_message

REPO = Path(__file__).resolve().parents[2]
EXAMPLES = REPO / "protocol" / "examples"
MESSAGE_EXAMPLES = sorted(EXAMPLES.glob("*.json"))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", MESSAGE_EXAMPLES, ids=lambda p: p.name)
def test_example_round_trips(path: Path) -> None:
    data = load(path)
    message = parse_message(data)
    assert message.model_dump(mode="json", exclude_unset=True) == data


def test_every_type_has_an_example() -> None:
    covered = {load(p)["type"] for p in MESSAGE_EXAMPLES}
    assert covered == set(MESSAGE_TYPES)


def test_unknown_fields_are_ignored() -> None:
    # A newer device may add fields; older clients must still parse the message.
    data = {**load(EXAMPLES / "status.json"), "added_in_a_later_minor": 1}
    assert isinstance(parse_message(data), models.Status)


def test_version_matches_protocol_file() -> None:
    assert PROTOCOL_VERSION == (REPO / "protocol" / "VERSION").read_text().strip()


@pytest.mark.parametrize(
    ("name", "model"),
    [
        ("face.list.json", models.FaceListResult),
        ("system.diagnostics.json", models.SystemDiagnosticsResult),
        ("system.logs.json", models.SystemLogsResult),
        ("system.settings.json", models.SystemSettingsResult),
        ("subscribe.json", models.SubscribeResult),
        ("mode.get.json", models.ModeGetResult),
        ("system.status.json", models.StatusPayload),
    ],
)
def test_results_round_trip(name: str, model: type) -> None:
    data = load(EXAMPLES / "results" / name)
    assert model.model_validate(data).model_dump(mode="json", exclude_unset=True) == data
