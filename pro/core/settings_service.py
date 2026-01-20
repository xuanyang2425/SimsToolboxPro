from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SettingsService:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._settings_path = data_dir / "settings.json"
        self._data: dict[str, Any] = {}

    def load(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        if self._settings_path.exists():
            self._data = json.loads(self._settings_path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._settings_path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
