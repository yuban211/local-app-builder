# local-app-builder

零代码、用任意 AI 智能体构建**只给自己用的**本地化工作生活管理 APP 的全流程工作流。

平台无关：豆包 / Kimi / 通义千问 / Cursor / Codex / Claude Code 均可执行。

**仓库地址**：https://github.com/yuban211/local-app-builder

## 安装

### DeepSeek Harness

```sh
git clone https://github.com/yuban211/local-app-builder.git ~/.dsh/skills/local-app-builder
```

放进 `~/.dsh/skills/` 后重启（或新建会话）即可用 `skill` 工具加载 `local-app-builder`。

### 其他 AI 智能体

不需要任何安装——把 `SKILL.md` 和 `references/prompts.md` 直接喂给智能体即可。
Cursor / Codex 这类能读写本地文件的，clone 到项目里再让它读 `SKILL.md`。

## 快速开始

1. 新建空文件夹作为项目根目录（默认名 `木子的APP`）。
2. 加载本技能（DSH：`skill` 工具加载 `local-app-builder`；其他智能体：直接把 `SKILL.md` + `references/prompts.md` 喂给它）。
3. 从 `references/prompts.md` 的 §0 开始，按顺序发提示词：需求 → 界面设计 → PRD → 开发计划 → 分阶段开发 → Git → 走查 → 修复 → 美化 → 开源。

## 目录

| 路径 | 作用 |
|---|---|
| `SKILL.md` | 主工作流：零门槛启动 / 四段式提示词 / 9 阶段流水线 / PRD 六维度 / Git 极简实践 / 三套 UI 风格引擎 / 开源复用 / 启动脚本交付 / 执行清单 |
| `references/prompts.md` | 全流程可直接复制的提示词库 |
| `templates/PRD模板.md` | PRD 骨架（六维度 + 暂不实现项 + 验收标准表） |
| `templates/开发计划模板.md` | 9 阶段任务分解骨架 + 阶段执行指令模板 |
| `templates/走查与缺陷分级模板.md` | 走查路径表 + 功能型/视觉型缺陷分级 + 修复排期 |
| `templates/验收清单.md` | 第一版逐条判定清单（A~G 七组） |

## 七条铁律

1. 数据永久本地存储（禁 localStorage / 浏览器缓存依赖）
2. 分阶段推进，每阶段注入自动化测试
3. 测试即验收：定位 → 修复 → 重测，禁止跳过或作弊通过
4. 全链路闭环，产出可双击启动脚本 + 本地 Web 服务
5. Git 原子提交，每次功能/缺陷修复各一次
6. 范围管控：第一版不做登录、联网部署、手机端
7. 美化零风险：仅外观变更，不改动功能逻辑

## 认知分工

- **PRD** = 产品经理文档，人必须逐条审阅。
- **开发计划** = AI 工程师文档，人不需看懂，只需确认它存在且被严格执行。

## 三套 UI 风格引擎

毛玻璃拟态风 · Notion 笔记风（深/浅双模）· 新粗野主义风 —— 做成可切换的主题变量层。

## 口号

> 你的生活，你的 APP，你的规则。
