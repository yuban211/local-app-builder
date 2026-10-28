"""本地 Web 服务：标准库 http.server + JSON API，零第三方依赖。

只监听 127.0.0.1 —— 不上网、不对外暴露，符合「本地私有 APP」定位。

用法：
    python src/app.py            # 默认 8770 端口，自动开浏览器
    python src/app.py 9000       # 指定端口
    python src/app.py --no-browser
"""

from __future__ import annotations

import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:  # Windows 控制台默认 GBK，中文会乱码
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import db  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "src" / "web"
DEFAULT_PORT = 8770


class Handler(BaseHTTPRequestHandler):
    server_version = "LocalApp/1.0"

    # ── 输出 ──
    def _send(self, code: int, body, ctype: str = "application/json; charset=utf-8") -> None:
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code: int, obj) -> None:
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _body(self) -> dict:
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    @staticmethod
    def _item_id(path: str):
        parts = [p for p in urlparse(path).path.split("/") if p]
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "items":
            try:
                return int(parts[2])
            except ValueError:
                return None
        return None

    # ── 路由 ──
    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            f = WEB / "index.html"
            if not f.exists():
                return self._json(404, {"ok": False, "error": "index.html missing"})
            return self._send(200, f.read_bytes(), "text/html; charset=utf-8")
        if path == "/api/items":
            return self._json(200, {"ok": True, "items": db.list_items()})
        if path == "/api/health":
            return self._json(200, {"ok": True, "db": str(db.DB_PATH)})
        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/items":
            b = self._body()
            title = str(b.get("title") or "").strip()
            if not title:
                return self._json(400, {"ok": False, "error": "title required"})
            return self._json(201, {"ok": True, "item": db.add_item(title, str(b.get("note") or ""))})
        if path == "/api/backup":
            dest = db.backup()
            return self._json(200, {"ok": dest is not None, "file": str(dest) if dest else None})
        self._json(404, {"ok": False, "error": "not found"})

    def do_PATCH(self):
        iid = self._item_id(self.path)
        if iid is None:
            return self._json(404, {"ok": False, "error": "not found"})
        b = self._body()
        item = db.update_item(iid, **{k: v for k, v in b.items() if k in db.UPDATABLE})
        if not item:
            return self._json(404, {"ok": False, "error": "not found"})
        return self._json(200, {"ok": True, "item": item})

    def do_DELETE(self):
        iid = self._item_id(self.path)
        if iid is None:
            return self._json(404, {"ok": False, "error": "not found"})
        if not db.delete_item(iid):
            return self._json(404, {"ok": False, "error": "not found"})
        return self._json(200, {"ok": True, "deleted": iid})

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    db.init_db()
    port = DEFAULT_PORT
    args = [a for a in sys.argv[1:]]
    for a in list(args):
        if a.isdigit():
            port = int(a)
            args.remove(a)
    url = f"http://127.0.0.1:{port}/"
    print(f"服务已启动: {url}")
    print(f"数据文件:   {db.DB_PATH}")
    print("停止服务:   在本窗口按 Ctrl+C")
    if "--no-browser" not in args:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


if __name__ == "__main__":
    main()
