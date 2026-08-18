# Codex Skills

个人 Codex Skills 集合，覆盖方案追问、Java 开发规范、纸海报创作与旅行攻略等场景。

## 技能总览

| Skill | 功能 | 适用场景 |
|---|---|---|
| `grilling` | 对计划、决策或想法进行连续追问访谈，一次一个问题并附推荐答案 | 方案压力测试、设计澄清 |
| `grill-me` | `grilling` 的快捷别名 | 直接以 `/grilling` 方式追问 |
| `grill-with-docs` | `grilling` 的快捷别名，额外产出 ADR 与术语表文档 | 需要边访谈边沉淀文档 |
| `java-dev` | 基于阿里 Java 开发手册（嵩山版）的 Java 开发规范 | Java 编码、评审、重构、数据库与 API 设计、单元测试、并发与安全 |
| `scene-distillation-zine` | 将照片转化为插画风纸海报（不保留照片像素） | 编辑性视觉再诠释 |
| `scenes-gathered-zine` | 将照片转化为编辑风纸海报（以摄影真实为主导） | 美观易读的纸海报创作 |
| `travel-guide-html` | 生成「攻略优先」的单文件 HTML 交互式旅行攻略（无地图、移动优先） | 多日行程规划，手机可离线浏览的攻略单 |

## 安装

将任一 Skill 目录复制到 Codex 个人技能目录即可：

```powershell
Copy-Item -LiteralPath .\<skill> -Destination "$env:USERPROFILE\.codex\skills\<skill>" -Recurse
```

随后在新的对话轮次中通过技能名或斜杠命令调用，例如 `/grilling`。

## 方案追问

`grilling` 会对一个计划、决策或想法进行穷追不舍的访谈：一次只问一个问题并等待反馈，每个问题附带推荐答案；可通过环境查证的事实会自行查证，只把真正的决策交还用户，并在达成共识前不采取行动。`grill-me` 与 `grill-with-docs` 是它的快捷别名，后者会额外产出 ADR 与术语表文档。

## Java 开发规范

`java-dev` 基于阿里 Java 开发手册（嵩山版），覆盖命名规范、编码规范、并发编程、异常与日志、数据库设计、安全实现、单元测试与架构设计，内置 8 份分主题参考文档，用于编写、评审和重构 Java 代码。

## 影像蒸馏

`scene-distillation-zine` 将用户提供的照片转化为独立成画的插画风纸海报，最终画面不保留任何照片像素；强调第一眼的普适美感、清晰的主角和协调的构图色彩，同时保留一处来自源图的安静张力。支持「单色块模式」触发词。输出为生成图像、简短中文创作说明与美术指导说明。

## 实景拼贴

`scenes-gathered-zine` 将照片转化为编辑风纸海报，以摄影真实作为主导的事实与情感锚点，默认至少 25% 的设计留白纸面；用户要求杂志、编辑或作者性排版时，切换为更不对称的编辑版式。输出为生成图像与简短中文创作说明。

## 旅行攻略

`travel-guide-html` 将一次多日旅行的行程规划渲染为**单个可直接双击打开、手机可顺畅浏览的 HTML 文件**：攻略内容为主体，不内置任何地图模块，无需坐标依赖。包含每日时间轴、每日 Dashboard、可展开的景点攻略、住宿推荐（含地理理由）、伴手礼/特产清单（含购买地址与理由）、备用方案、附近顺路推荐、美食增强、总览页与准备清单页。单一文件、零外部依赖，所有 CSS / JS / 数据内联，离线可用；视觉沿用 Stripe 风（浅色底 + 柔光渐变），移动优先响应式设计。

### 使用方式

将 Skill 安装到 Codex 个人目录：

```powershell
Copy-Item -LiteralPath .\travel-guide-html -Destination "$env:USERPROFILE\.codex\skills\travel-guide-html" -Recurse
```

在新的对话轮次中调用：

```text
使用 $travel-guide-html 做一份 X 天 X 地旅游攻略，手机能直接看、不需要地图。
```

生成后按技能内置校验步骤检查输出 HTML（无地图 Key、内联 JS 语法无误、字段计数完整）再交付。

## 版本

当前版本：`v1.4.0`（2026-08-18）。详细内容见 [版本变更记录](CHANGELOG.md)。

## 项目结构

```text
grilling/                    方案追问
grill-me/                    方案追问别名
grill-with-docs/             方案追问别名（含文档产出）
java-dev/                    阿里 Java 开发规范
scene-distillation-zine/     影像蒸馏纸海报
scenes-gathered-zine/        实景拼贴纸海报
travel-guide-html/           交互式旅行攻略 HTML
```

每个 Skill 目录遵循统一结构：

```text
<skill>/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── (scripts/、schemas/、tests/ 按需)
```
