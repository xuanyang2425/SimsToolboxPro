from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .db_service import DBService


@dataclass(frozen=True)
class ScanSummary:
    root: Path
    added: int
    changed: int
    removed: int


class FileIndexService:
    def __init__(self, db: DBService) -> None:
        self._db = db

    def ensure_schema(self) -> None:
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS file_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                abs_path TEXT UNIQUE,
                rel_path TEXT,
                file_name TEXT,
                ext TEXT,
                size INTEGER,
                mtime REAL,
                quick_sig TEXT,
                sha1 TEXT,
                first_seen_at TEXT,
                last_seen_at TEXT,
                status TEXT,
                source TEXT
            )
            """
        )
        self._db.execute("CREATE INDEX IF NOT EXISTS idx_file_index_abs_path ON file_index(abs_path)")
        self._db.commit()

    def scan(self, root: Path, source: str = "external") -> ScanSummary:
        root = root.expanduser()
        now = datetime.now().isoformat(timespec="seconds")

        existing = {
            row["abs_path"]: row
            for row in self._db.execute(
                "SELECT abs_path, size, mtime FROM file_index"
            ).fetchall()
        }
        seen: set[str] = set()
        added = changed = 0

        for path in root.rglob("*"):
            if not path.is_file():
                continue
            abs_path = str(path)
            rel_path = str(path.relative_to(root))
            stat = path.stat()
            quick_sig = f"{stat.st_size}:{stat.st_mtime}"
            seen.add(abs_path)
            existing_row = existing.get(abs_path)
            if existing_row is None:
                added += 1
                self._db.execute(
                    """
                    INSERT INTO file_index (
                        abs_path, rel_path, file_name, ext, size, mtime, quick_sig,
                        sha1, first_seen_at, last_seen_at, status, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        abs_path,
                        rel_path,
                        path.name,
                        path.suffix,
                        stat.st_size,
                        stat.st_mtime,
                        quick_sig,
                        None,
                        now,
                        now,
                        "normal",
                        source,
                    ),
                )
            elif existing_row["size"] != stat.st_size or existing_row["mtime"] != stat.st_mtime:
                changed += 1
                self._db.execute(
                    """
                    UPDATE file_index
                    SET rel_path = ?, file_name = ?, ext = ?, size = ?, mtime = ?,
                        quick_sig = ?, last_seen_at = ?, status = ?
                    WHERE abs_path = ?
                    """,
                    (
                        rel_path,
                        path.name,
                        path.suffix,
                        stat.st_size,
                        stat.st_mtime,
                        quick_sig,
                        now,
                        "changed",
                        abs_path,
                    ),
                )
            else:
                self._db.execute(
                    "UPDATE file_index SET last_seen_at = ?, status = ? WHERE abs_path = ?",
                    (now, "normal", abs_path),
                )

        removed = 0
        for abs_path in existing.keys() - seen:
            removed += 1
            self._db.execute(
                "UPDATE file_index SET status = ?, last_seen_at = ? WHERE abs_path = ?",
                ("missing", now, abs_path),
            )

        self._db.commit()
        return ScanSummary(root=root, added=added, changed=changed, removed=removed)
