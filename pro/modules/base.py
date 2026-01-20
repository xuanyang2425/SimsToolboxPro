from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModuleMeta:
    module_id: str
    name: str
    version: str


class Module(Protocol):
    meta: ModuleMeta

    def register_actions(self, app: object) -> None: ...

    def create_docks(self, app: object) -> list[object]: ...

    def create_tabs(self, app: object) -> list[object]: ...

    def subscribe_events(self, bus: object) -> None: ...
