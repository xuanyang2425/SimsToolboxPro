from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from ..core.event_bus import EventBus
from ..core.file_index_service import FileIndexService, ScanSummary
from ..core.log_service import LogService
from ..core.op_log_service import OpLogService
from ..core.settings_service import SettingsService
from ..core.task_service import TaskService
from ..modules.registry import load_modules
from .log_dock import LogDock
from .task_dock import TaskDock


class MainWindow(QtWidgets.QMainWindow):
    def __init__(
        self,
        settings: SettingsService,
        event_bus: EventBus,
        tasks: TaskService,
        log_service: LogService,
        file_index: FileIndexService,
        op_log: OpLogService,
    ) -> None:
        super().__init__()
        self._settings = settings
        self._event_bus = event_bus
        self._tasks = tasks
        self._log = log_service
        self._file_index = file_index
        self._op_log = op_log
        self.setWindowTitle("SimsToolbox Pro")
        self.setObjectName("MainWindow")
        self.resize(1200, 780)

        self._tab_widget = QtWidgets.QTabWidget()
        self._tab_widget.setMovable(True)
        self.setCentralWidget(self._tab_widget)

        self._build_menu()
        self._build_toolbar()
        self._build_docks()
        self._load_modules()
        self._restore_layout()

        self._status_root = QtWidgets.QLabel("根目录: 未设置")
        self._status_scan = QtWidgets.QLabel("扫描: 未开始")
        self.statusBar().addPermanentWidget(self._status_root)
        self.statusBar().addPermanentWidget(self._status_scan)

        self._poll_timer = QtCore.QTimer(self)
        self._poll_timer.timeout.connect(self._poll_tasks)
        self._poll_timer.start(300)

        self._log.info("SimsToolbox Pro 已启动。")

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self._settings.set("main_window.geometry", self.saveGeometry().data().hex())
        self._settings.set("main_window.state", self.saveState().data().hex())
        self._settings.save()
        self._tasks.shutdown()
        super().closeEvent(event)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("文件")
        scan_action = QtGui.QAction("同步扫描", self)
        scan_action.triggered.connect(self.request_scan)
        file_menu.addAction(scan_action)

        set_root_action = QtGui.QAction("设置 Mods 根目录", self)
        set_root_action.triggered.connect(self.choose_root)
        file_menu.addAction(set_root_action)
        file_menu.addSeparator()
        file_menu.addAction("退出", self.close)

        help_menu = self.menuBar().addMenu("帮助")
        help_menu.addAction("关于", self._show_about)

    def _build_toolbar(self) -> None:
        toolbar = self.addToolBar("主工具栏")
        toolbar.setMovable(False)
        search = QtWidgets.QLineEdit()
        search.setPlaceholderText("全局搜索 / Command Palette (Ctrl+P)")
        search.setMinimumWidth(320)
        toolbar.addWidget(search)
        command_btn = QtWidgets.QPushButton("命令面板")
        toolbar.addWidget(command_btn)
        toolbar.addSeparator()
        scan_btn = QtWidgets.QPushButton("同步扫描")
        scan_btn.clicked.connect(self.request_scan)
        toolbar.addWidget(scan_btn)

    def _build_docks(self) -> None:
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, LogDock(self._log))
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, TaskDock(self._tasks))

    def _load_modules(self) -> None:
        for module in load_modules():
            module.subscribe_events(self._event_bus)
            for dock in module.create_docks(self):
                self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock)
            for tab in module.create_tabs(self):
                title = getattr(tab, "windowTitle", lambda: "")()
                if not title:
                    title = tab.objectName() or module.meta.name
                self._tab_widget.addTab(tab, title)

    def _restore_layout(self) -> None:
        geometry = self._settings.get("main_window.geometry")
        if geometry:
            self.restoreGeometry(bytes.fromhex(geometry))
        state = self._settings.get("main_window.state")
        if state:
            self.restoreState(bytes.fromhex(state))

    def choose_root(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "选择 Mods 根目录")
        if not path:
            return
        self._settings.set("mods_root", path)
        self._settings.save()
        self._status_root.setText(f"根目录: {path}")
        self._log.info(f"已设置 Mods 根目录: {path}")

    def request_scan(self) -> None:
        root = self._settings.get("mods_root")
        if not root:
            self._log.warning("请先设置 Mods 根目录。")
            QtWidgets.QMessageBox.information(self, "提示", "请先设置 Mods 根目录。")
            return
        root_path = Path(root)
        self._log.info("开始扫描 Mods 目录...")
        handle = self._tasks.submit("文件索引扫描", self._file_index.scan, root_path)
        handle.future.add_done_callback(lambda _: self._on_scan_finished(handle))

    def _on_scan_finished(self, handle) -> None:
        try:
            summary: ScanSummary = handle.future.result()
        except Exception as exc:  # noqa: BLE001
            self._log.error(f"扫描失败: {exc}")
            return
        self._status_scan.setText(
            f"扫描完成: +{summary.added} / ~{summary.changed} / -{summary.removed}"
        )
        self._log.info(
            f"扫描完成: 新增 {summary.added} · 变更 {summary.changed} · 缺失 {summary.removed}"
        )
        self._event_bus.publish(
            "index.updated",
            {
                "added": summary.added,
                "changed": summary.changed,
                "removed": summary.removed,
            },
        )

    def _poll_tasks(self) -> None:
        self._tasks.cleanup_finished()

    def _show_about(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            "关于 SimsToolbox Pro",
            "SimsToolbox Pro · 模块化 Mod 管理工具箱（示例骨架）",
        )
