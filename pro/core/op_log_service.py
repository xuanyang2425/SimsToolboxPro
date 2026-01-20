from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .db_service import DBService


@dataclass(frozen=True)
class OperationRecord:
    op_type: str
    payload: dict[str, Any]
    status: str
    created_at: str


class OpLogService:
    def __init__(self, db: DBService) -> None:
        self._db = db

    def record(self, op_type: str, payload: dict[str, Any], status: str = "done") -> None:
        self._db.execute(
            """
            INSERT INTO op_log (op_type, payload_json, status, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                op_type,
                json.dumps(payload, ensure_ascii=False),
                status,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self._db.commit()

    def recent(self, limit: int = 50) -> list[OperationRecord]:
        rows = self._db.execute(
            "SELECT op_type, payload_json, status, created_at FROM op_log ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            OperationRecord(
                op_type=row["op_type"],
                payload=json.loads(row["payload_json"]),
                status=row["status"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
