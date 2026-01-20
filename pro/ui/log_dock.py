from __future__ import annotations

from PySide6 import QtWidgets

from ..core.log_service import LogEntry, LogService


class LogDock(QtWidgets.QDockWidget):
    def __init__(self, log_service: LogService) -> None:
        super().__init__("日志")
        self.setObjectName("LogDock")
        self._log_service = log_service
        self._list = QtWidgets.QListWidget()
        self._list.setAlternatingRowColors(True)
        self.setWidget(self._list)
        self._log_service.add_listener(self._append)
        for entry in self._log_service.entries():
            self._append(entry)

    def _append(self, entry: LogEntry) -> None:
        timestamp = entry.timestamp.strftime("%H:%M:%S")
        self._list.addItem(f"[{timestamp}] {entry.level}: {entry.message}")
