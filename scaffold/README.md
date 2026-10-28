# scaffold —— 最小可跑起点

`local-app-builder` 工作流第 1 阶段的**真实起点**：一个能双击启动、能存数据、带测试的骨架。
不是示例伪代码，是真能跑的东西。

## 它是什么

一个本地待办清单（增删改查 + 完成状态），用来验证整套流程跑得通。
**拿去改成任何主题**（记账、读书、健身……）就是你的 APP。

技术栈刻意做到最简：

- 后端：Python 标准库 `http.server`
- 数据：Python 标准库 `sqlite3`
- 前端：单个 HTML 文件，原生 JS

**零第三方依赖** —— 不需要 `pip install`，装了 Python 就能跑。

## 怎么用

Windows 双击 `scripts/start.bat`，或命令行：

```bash
python src/app.py            # 默认 8770 端口，自动开浏览器
python src/app.py 9000       # 指定端口
python src/app.py --no-browser
```

打开 http://127.0.0.1:8770/ 即可使用。停止服务：Ctrl+C。

## 跑测试

```bash
python tests/test_db.py
```

覆盖：增删改查、重启后数据不丢、备份与恢复、非法字段被拦截。

## 目录

```
scaffold/
├─ src/
│  ├─ db.py            # 数据层：SQLite，备份/恢复
│  ├─ app.py           # Web 服务：JSON API
│  └─ web/index.html   # 界面
├─ scripts/start.bat   # 双击启动
├─ tests/test_db.py    # 测试
└─ data/               # 数据库（运行时生成）
   backups/            # 备份（运行时生成）
```

## 改造成你的 APP

1. 改 `db.py` 的 `SCHEMA` 和 `UPDATABLE`，换成你的表和字段
2. 改 `app.py` 的路由，换成你的接口
3. 改 `src/web/index.html`，换成你的界面
4. 每改一块就补一个测试，全绿再往下走

## 安全边界

- 只监听 `127.0.0.1`，不对局域网暴露
- SQL 字段名走白名单，不接受外部传入列名
- 无登录、无联网 —— 符合工作流「第一版不做登录/联网/手机端」的范围管控

如果要多人用或放公网，那是另一回事，本骨架不适用。
