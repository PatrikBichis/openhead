"""Host-side token store: ~/.openhead/tokens.json, one token per device address."""

from __future__ import annotations

import json
import os
from pathlib import Path


def default_path() -> Path:
    return Path(os.environ.get("OPENHEAD_TOKENS", Path.home() / ".openhead" / "tokens.json"))


class TokenStore:
    def __init__(self, path: Path | None = None):
        self.path = path or default_path()

    def _load(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get(self, key: str) -> str | None:
        return self._load().get(key, {}).get("token")

    def set(self, key: str, token: str, device: str | None = None) -> None:
        data = self._load()
        data[key] = {"token": token, "device": device}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def remove(self, key: str) -> None:
        data = self._load()
        if data.pop(key, None) is not None:
            self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
