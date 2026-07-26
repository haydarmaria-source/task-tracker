"""SQLite storage layer for the Task Tracker.

Kept intentionally small: plain sqlite3, no ORM. The database path is read from
the TASK_TRACKER_DB environment variable so tests can point it at a temporary
file (see backend/tests/conftest.py).
"""
import os
import sqlite3
from datetime import datetime, timezone


def db_path() -> str:
    return os.environ.get("TASK_TRACKER_DB", "task_tracker.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db() -> None:
    """Create the tasks table if it does not exist.

    due_date and tags were added in the mid-course project. New databases
    get the columns straight from CREATE TABLE; a pre-existing
    task_tracker.db from before that project gets them added via ALTER
    TABLE so older local databases keep working without a manual migration.
    """
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status      TEXT NOT NULL DEFAULT 'todo',
                priority    TEXT NOT NULL DEFAULT 'medium',
                assignee    TEXT NOT NULL DEFAULT '',
                due_date    TEXT,
                tags        TEXT NOT NULL DEFAULT '',
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            )
            """
        )
        existing_cols = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
        if "due_date" not in existing_cols:
            conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
        if "tags" not in existing_cols:
            conn.execute("ALTER TABLE tasks ADD COLUMN tags TEXT NOT NULL DEFAULT ''")
        conn.commit()


def row_to_dict(row: sqlite3.Row) -> dict:
    return {k: row[k] for k in row.keys()}


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()
