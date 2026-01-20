from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtWidgets

from .base import ModuleMeta


@dataclass(frozen=True)
class ModManagerModule:
    meta: ModuleMeta = ModuleMeta(
        module_id="mod_manager",
        name="Mod Manager",
        version="0.1.0",
    )

    def register_actions(self, app: object) -> None:
        return None

    def create_docks(self, app: object) -> list[QtWidgets.QDockWidget]:
        dock = QtWidgets.QDockWidget("虚拟组别")
        dock.setObjectName("ModGroupsDock")
        list_widget = QtWidgets.QListWidget()
        list_widget.addItems(["基础组别", "最近新增", "问题 Mod"])
        dock.setWidget(list_widget)
        return [dock]

    def create_tabs(self, app: object) -> list[QtWidgets.QWidget]:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel("Mod 管理器：虚拟组别 + 批量停用/启用 + Undo。"))
        layout.addStretch(1)
        tab.setObjectName("ModManager")
        return [tab]

    def subscribe_events(self, bus: object) -> None:
        return None
