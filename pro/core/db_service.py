from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Migration:
    version: int
    sql: str


class DBService:
    def __init__(self, db_path: Path, migrations: Iterable[Migration]) -> None:
        self._db_path = db_path
        self._migrations = sorted(migrations, key=lambda m: m.version)
        self._conn: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def initialize(self) -> None:
        conn = self.connection
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY
            )
            """
        )
        existing_versions = {
            row["version"] for row in conn.execute("SELECT version FROM schema_migrations")
        }
        for migration in self._migrations:
            if migration.version in existing_versions:
                continue
            conn.executescript(migration.sql)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (migration.version,),
            )
        conn.commit()

    def execute(self, sql: str, params: tuple | dict | None = None) -> sqlite3.Cursor:
        if params is None:
            return self.connection.execute(sql)
        return self.connection.execute(sql, params)

    def executemany(self, sql: str, params_seq: Iterable[tuple]) -> sqlite3.Cursor:
        return self.connection.executemany(sql, params_seq)

    def commit(self) -> None:
        self.connection.commit()
