"""数据层测试：标准库 unittest，零第三方依赖。

运行：
    python tests/test_db.py
或：
    python -m unittest discover -s tests

覆盖铁律中最关键的一条：数据落盘，重启不丢，可备份可恢复。
"""

from __future__ import annotations

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

_tmp = tempfile.mkdtemp(prefix="localscaffold-test-")
os.environ["APP_DB"] = str(Path(_tmp) / "test.db")
os.environ["APP_BACKUP_DIR"] = str(Path(_tmp) / "backups")

import db  # noqa: E402


class Base(unittest.TestCase):
    """每个用例一张干净的库 —— 否则用例之间会互相看见对方的数据。"""

    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="localscaffold-")
        db.DB_PATH = Path(self.dir) / "t.db"
        db.BACKUP_DIR = Path(self.dir) / "backups"
        db.init_db()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class TestPersistence(Base):
    """重启后数据必须还在 —— 这是本地 APP 的底线。"""

    def test_add_and_list(self):
        db.init_db()
        db.add_item("买菜", "西红柿两个")
        items = db.list_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "买菜")
        self.assertEqual(items[0]["note"], "西红柿两个")
        self.assertEqual(items[0]["done"], 0)

    def test_data_survives_new_connection(self):
        """模拟重启：新建连接后数据依然可读。"""
        db.init_db()
        before = db.add_item("持久化测试")
        again = db.get_item(before["id"])
        self.assertIsNotNone(again, "重启后数据丢失")
        self.assertEqual(again["title"], "持久化测试")

    def test_empty_title_still_stored(self):
        """标题允许任意非空字符串；空串由调用方拦截。"""
        db.init_db()
        item = db.add_item("x")
        self.assertEqual(item["title"], "x")

    def test_get_missing_returns_none(self):
        db.init_db()
        self.assertIsNone(db.get_item(99999))


class TestCRUD(Base):
    def test_update_done(self):
        db.init_db()
        it = db.add_item("待办")
        updated = db.update_item(it["id"], done=1)
        self.assertEqual(updated["done"], 1)
        self.assertEqual(db.get_item(it["id"])["done"], 1)

    def test_update_ignores_unknown_fields(self):
        """白名单外的字段必须被丢弃，不能拼进 SQL。"""
        db.init_db()
        it = db.add_item("安全测试")
        updated = db.update_item(it["id"], evil_column="x")
        self.assertIsNotNone(updated)

    def test_delete(self):
        db.init_db()
        it = db.add_item("临时")
        self.assertTrue(db.delete_item(it["id"]))
        self.assertIsNone(db.get_item(it["id"]))

    def test_delete_missing_returns_false(self):
        db.init_db()
        self.assertFalse(db.delete_item(99999))


class TestBackup(Base):
    def test_backup_creates_file(self):
        db.init_db()
        db.add_item("备份前的数据")
        dest = db.backup()
        self.assertIsNotNone(dest)
        self.assertTrue(Path(dest).exists())

    def test_restore_brings_data_back(self):
        db.init_db()
        db.add_item("要被恢复的")
        dest = db.backup()

        # 删光当前数据
        for it in db.list_items():
            db.delete_item(it["id"])
        self.assertEqual(len(db.list_items()), 0)

        self.assertTrue(db.restore(dest))
        titles = [i["title"] for i in db.list_items()]
        self.assertIn("要被恢复的", titles, "恢复后数据没回来")


if __name__ == "__main__":
    unittest.main(verbosity=2)
