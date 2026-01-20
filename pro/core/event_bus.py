from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Iterable


EventCallback = Callable[[str, dict[str, Any]], None]


@dataclass(frozen=True)
class Event:
    name: str
    payload: dict[str, Any]


class EventBus:
    def __init__(self) -> None:
        self._listeners: DefaultDict[str, list[EventCallback]] = defaultdict(list)

    def subscribe(self, event_names: Iterable[str], callback: EventCallback) -> None:
        for name in event_names:
            self._listeners[name].append(callback)

    def publish(self, name: str, payload: dict[str, Any]) -> None:
        for callback in list(self._listeners.get(name, [])):
            callback(name, payload)
