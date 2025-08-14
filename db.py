from __future__ import annotations
import sqlite3, datetime
from typing import Iterable, Optional

def get_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(path: str, seed: bool = False) -> None:
    conn = get_db(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    if seed:
        now = datetime.datetime.utcnow().isoformat()
        cur.executemany(
            "INSERT INTO tasks(title, done, created_at, updated_at) VALUES (?, 0, ?, ?)",
            [("Read a book", now, now), ("Write code", now, now), ("Push to GitHub", now, now)],
        )
        conn.commit()
    conn.close()

# CRUD helpers

def list_tasks(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()

def get_task(conn: sqlite3.Connection, task_id: int) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()

def add_task(conn: sqlite3.Connection, title: str) -> int:
    now = datetime.datetime.utcnow().isoformat()
    cur = conn.execute(
        "INSERT INTO tasks(title, done, created_at, updated_at) VALUES (?, 0, ?, ?)",
        (title, now, now),
    )
    conn.commit()
    return int(cur.lastrowid)

def toggle_done(conn: sqlite3.Connection, task_id: int) -> bool:
    row = get_task(conn, task_id)
    if not row:
        return False
    new_done = 0 if row["done"] else 1
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("UPDATE tasks SET done=?, updated_at=? WHERE id=?", (new_done, now, task_id))
    conn.commit()
    return True

def update_title(conn: sqlite3.Connection, task_id: int, title: str) -> bool:
    if not get_task(conn, task_id):
        return False
    now = datetime.datetime.utcnow().isoformat()
    conn.execute("UPDATE tasks SET title=?, updated_at=? WHERE id=?", (title, now, task_id))
    conn.commit()
    return True

def delete_task(conn: sqlite3.Connection, task_id: int) -> bool:
    cur = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    return cur.rowcount > 0

def clear_completed(conn: sqlite3.Connection) -> int:
    cur = conn.execute("DELETE FROM tasks WHERE done=1")
    conn.commit()
    return cur.rowcount