"""数据层：本地 SQLite，零第三方依赖。

铁律：数据落盘到真实文件，重启 + 清缓存后不丢，且可一键备份/恢复。

只依赖标准库 —— 任何装了 Python 的机器都能跑，不需要 pip install。
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 环境变量可覆盖，仅用于测试隔离；正常使用走默认路径
DB_PATH = Path(os.environ.get("APP_DB") or (ROOT / "data" / "app.db"))
BACKUP_DIR = Path(os.environ.get("APP_BACKUP_DIR") or (ROOT / "backups"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  done INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL
);
"""

# 允许更新的字段白名单 —— 防止调用方拼出任意列名
UPDATABLE = ("title", "note", "done")


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def list_items() -> list[dict]:
    with connect() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM items ORDER BY id DESC")]


def get_item(item_id: int) -> dict | None:
    with connect() as conn:
        r = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
        return dict(r) if r else None


def add_item(title: str, note: str = "") -> dict:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO items(title, note, done, created_at) VALUES(?,?,0,?)",
            (title, note, _now()),
        )
        new_id = cur.lastrowid
    return get_item(new_id)


def update_item(item_id: int, **fields) -> dict | None:
    cols = {k: v for k, v in fields.items() if k in UPDATABLE}
    if not cols:
        return get_item(item_id)
    sets = ", ".join(f"{k}=?" for k in cols)  # 键来自白名单，非用户输入
    vals = list(cols.values()) + [item_id]
    with connect() as conn:
        cur = conn.execute(f"UPDATE items SET {sets} WHERE id=?", vals)
        if cur.rowcount == 0:
            return None
    return get_item(item_id)


def delete_item(item_id: int) -> bool:
    with connect() as conn:
        cur = conn.execute("DELETE FROM items WHERE id=?", (item_id,))
        return cur.rowcount > 0


def backup() -> Path | None:
    """把当前数据库复制一份到 backups/，文件名带时间戳。"""
    if not DB_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUP_DIR / f"app-{datetime.now():%Y%m%d-%H%M%S}.db"
    shutil.copy2(str(DB_PATH), str(dest))
    return dest


def restore(backup_file: str | Path) -> bool:
    """用一份备份覆盖当前数据库。调用前请先自行备份当前数据。"""
    src = Path(backup_file)
    if not src.exists():
        return False
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(DB_PATH))
    return True
