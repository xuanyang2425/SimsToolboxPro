from __future__ import annotations

from pathlib import Path

from PySide6 import QtWidgets

from pro.core.db_service import DBService
from pro.core.event_bus import EventBus
from pro.core.file_index_service import FileIndexService
from pro.core.log_service import LogService
from pro.core.migrations import MIGRATIONS
from pro.core.op_log_service import OpLogService
from pro.core.settings_service import SettingsService
from pro.core.task_service import TaskService
from pro.ui.main_window import MainWindow


def main() -> None:
    app = QtWidgets.QApplication([])
    data_dir = Path.home() / ".simstoolbox_pro"
    settings = SettingsService(data_dir)
    settings.load()

    db = DBService(data_dir / "sims_toolbox.db", MIGRATIONS)
    db.initialize()
    file_index = FileIndexService(db)
    file_index.ensure_schema()

    event_bus = EventBus()
    tasks = TaskService()
    log_service = LogService()
    op_log = OpLogService(db)

    window = MainWindow(
        settings=settings,
        event_bus=event_bus,
        tasks=tasks,
        log_service=log_service,
        file_index=file_index,
        op_log=op_log,
    )
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
