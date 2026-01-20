from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtWidgets

from .base import ModuleMeta


@dataclass(frozen=True)
class DownloaderModule:
    meta: ModuleMeta = ModuleMeta(
        module_id="downloader",
        name="Downloader",
        version="0.1.0",
    )

    def register_actions(self, app: object) -> None:
        return None

    def create_docks(self, app: object) -> list[QtWidgets.QDockWidget]:
        return []

    def create_tabs(self, app: object) -> list[QtWidgets.QWidget]:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel("下载器骨架：链接解析 + 队列 + 去重检查。"))
        layout.addStretch(1)
        tab.setObjectName("Downloader")
        return [tab]

    def subscribe_events(self, bus: object) -> None:
        return None
