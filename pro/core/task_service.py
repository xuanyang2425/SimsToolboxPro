from __future__ import annotations

import itertools
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Callable, Dict, Iterable


@dataclass
class TaskHandle:
    task_id: int
    name: str
    future: Future

    def cancel(self) -> bool:
        return self.future.cancel()


class TaskService:
    def __init__(self, max_workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._counter = itertools.count(1)
        self._tasks: Dict[int, TaskHandle] = {}
        self._listeners: list[Callable[[TaskHandle], None]] = []

    def submit(self, name: str, fn: Callable, *args, **kwargs) -> TaskHandle:
        task_id = next(self._counter)
        future = self._executor.submit(fn, *args, **kwargs)
        handle = TaskHandle(task_id=task_id, name=name, future=future)
        self._tasks[task_id] = handle
        self._notify(handle)
        return handle

    def add_listener(self, callback: Callable[[TaskHandle], None]) -> None:
        self._listeners.append(callback)

    def active_tasks(self) -> Iterable[TaskHandle]:
        return list(self._tasks.values())

    def cleanup_finished(self) -> None:
        finished = [task_id for task_id, handle in self._tasks.items() if handle.future.done()]
        for task_id in finished:
            self._tasks.pop(task_id, None)

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

    def _notify(self, handle: TaskHandle) -> None:
        for listener in list(self._listeners):
            listener(handle)
