"""SQLite connection helper (WAL, foreign keys)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config import settings


def connect(path=None):
    p = Path(path or settings.sqlite_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
