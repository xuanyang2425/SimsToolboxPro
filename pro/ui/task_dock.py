from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from ..core.task_service import TaskHandle, TaskService


class TaskDock(QtWidgets.QDockWidget):
    def __init__(self, task_service: TaskService) -> None:
        super().__init__("任务")
        self.setObjectName("TaskDock")
        self._task_service = task_service
        self._list = QtWidgets.QListWidget()
        self._list.setAlternatingRowColors(True)
        self.setWidget(self._list)
        self._task_service.add_listener(self._on_new_task)
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1000)

    def _on_new_task(self, handle: TaskHandle) -> None:
        self._list.addItem(self._format(handle))

    def _refresh(self) -> None:
        self._task_service.cleanup_finished()
        self._list.clear()
        for handle in self._task_service.active_tasks():
            self._list.addItem(self._format(handle))

    @staticmethod
    def _format(handle: TaskHandle) -> str:
        status = "running"
        if handle.future.done():
            status = "done"
        elif handle.future.cancelled():
            status = "cancelled"
        return f"{handle.task_id:03d} · {handle.name} · {status}"
