from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    level: str
    message: str


class LogService:
    def __init__(self) -> None:
        self._entries: list[LogEntry] = []
        self._listeners: list[Callable[[LogEntry], None]] = []

    def add_listener(self, callback: Callable[[LogEntry], None]) -> None:
        self._listeners.append(callback)

    def info(self, message: str) -> None:
        self._append("INFO", message)

    def warning(self, message: str) -> None:
        self._append("WARN", message)

    def error(self, message: str) -> None:
        self._append("ERROR", message)

    def entries(self) -> list[LogEntry]:
        return list(self._entries)

    def _append(self, level: str, message: str) -> None:
        entry = LogEntry(timestamp=datetime.now(), level=level, message=message)
        self._entries.append(entry)
        for listener in list(self._listeners):
            listener(entry)
