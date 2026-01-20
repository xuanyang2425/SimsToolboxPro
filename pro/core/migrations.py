from __future__ import annotations

from .db_service import Migration


MIGRATIONS: list[Migration] = [
    Migration(
        version=1,
        sql="""
        CREATE TABLE IF NOT EXISTS op_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            op_type TEXT,
            payload_json TEXT,
            status TEXT,
            created_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_op_log_created_at ON op_log(created_at);
        """,
    ),
]
