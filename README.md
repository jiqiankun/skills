# Codex Skills

个人 Codex Skills 集合，覆盖方案追问、Java 开发规范、规划模式、摄影精修与纸海报创作等场景。

## 技能总览

| Skill | 功能 | 适用场景 |
|---|---|---|
| `grilling` | 对计划、决策或想法进行连续追问访谈，一次一个问题并附推荐答案 | 方案压力测试、设计澄清 |
| `grill-me` | `grilling` 的快捷别名 | 直接以 `/grilling` 方式追问 |
| `grill-with-docs` | `grilling` 的快捷别名，额外产出 ADR 与术语表文档 | 需要边访谈边沉淀文档 |
| `java-dev` | 基于阿里 Java 开发手册（嵩山版）的 Java 开发规范 | Java 编码、评审、重构、数据库与 API 设计、单元测试、并发与安全 |
| `plan-mode` | Claude Code Plan Mode 架构的完整复刻（增强版） | 复杂任务的深度规划，强制代码落地与显式暂停询问 |
| `refine-photos` | 确定性、非生成式的摄影精修 | 人像、风光、环境人像的调色、局部精修与瑕疵修复 |
| `scene-distillation-zine` | 将照片转化为插画风纸海报（不保留照片像素） | 编辑性视觉再诠释 |
| `scenes-gathered-zine` | 将照片转化为编辑风纸海报（以摄影真实为主导） | 美观易读的纸海报创作 |

## 安装

将任一 Skill 目录复制到 Codex 个人技能目录即可：

```powershell
Copy-Item -LiteralPath .\<skill> -Destination "$env:USERPROFILE\.codex\skills\<skill>" -Recurse
```

随后在新的对话轮次中通过技能名或斜杠命令调用，例如 `使用 $refine-photos ...` 或 `/grilling`。

## 方案追问

`grilling` 会对一个计划、决策或想法进行穷追不舍的访谈：一次只问一个问题并等待反馈，每个问题附带推荐答案；可通过环境查证的事实会自行查证，只把真正的决策交还用户，并在达成共识前不采取行动。`grill-me` 与 `grill-with-docs` 是它的快捷别名，后者会额外产出 ADR 与术语表文档。

## Java 开发规范

`java-dev` 基于阿里 Java 开发手册（嵩山版），覆盖命名规范、编码规范、并发编程、异常与日志、数据库设计、安全实现、单元测试与架构设计，内置 8 份分主题参考文档，用于编写、评审和重构 Java 代码。

## 规划模式

`plan-mode` 完整复刻 Claude Code Plan Mode 架构：只读模式下产出包含具体代码实现的详细计划，计划文件必须包含核心函数签名、逻辑伪代码与约 80% 骨架代码；遇到需求歧义或技术选型分歧时强制暂停并向用户提问；退出前通过计划质量闸门清单。内置 9 份参考文档与 6 个质量检查/搜索脚本。

## 摄影精修

`refine-photos` 以保留摄影真实性为前提，先分析人物与环境的主次关系，再生成受约束的 Recipe，完成调色、局部精修、瑕疵处理、轻微裁剪与角度校正，并在交付前执行自动质量检查。

### 核心能力

- 支持人像、风光、环境人像及人物与风景均衡构图。
- 使用“摄影审美风格 → 色彩倾向 → 光影倾向 → 风格强度”四层风格体系。
- 提供自然真实、纪实克制、电影叙事、胶片复古、黑白摄影、宫苑华章、江南雅韵和徽州烟雨等摄影审美风格。
- 支持独立的三级风格强度与三级精修强度，默认均为二档标准强度。
- 保护人物身份、肤色、皮肤与织物纹理、建筑材质及场景语义。
- 仅使用原图像素进行确定性修复；不使用扩散生成、生成式填充、AI 超分辨率或神经人脸重建。
- 允许在用户明确要求并确认后增加受限的渐变光、辉光、光晕、漏光、光束、薄雾或暗角效果。
- 支持 JPEG、PNG 和 8/16 位 TIFF；RAW 需先通过可靠的外部解码器转换为 16 位 TIFF。

### 使用方式

将 Skill 安装到 Codex 个人目录：

```powershell
Copy-Item -LiteralPath .\refine-photos -Destination "$env:USERPROFILE\.codex\skills\refine-photos" -Recurse
```

在新的对话轮次中调用：

```text
使用 $refine-photos 自然精修这张照片，并先给我方案和预览。
```

若未指定工作方式，Skill 会先用中文询问：查看方案与预览，还是直接交付成片。

### 本地运行

建议使用 Python 3.11 或 3.12：

```powershell
python -m pip install -r .\refine-photos\scripts\requirements.txt
python .\refine-photos\scripts\refine.py check
python .\refine-photos\scripts\refine.py template .\recipe.json
python .\refine-photos\scripts\refine.py validate .\recipe.json
```

渲染命令：

```powershell
python .\refine-photos\scripts\refine.py render .\source.jpg .\recipe.json .\source_refined.jpg --auto-safe
```

渲染器不会覆盖原图，并会在输出图旁生成实际应用的 Recipe 与质量审计文件。

### 验证

```powershell
python -m unittest discover -s .\refine-photos\tests -p "test_*.py" -v
```

当前自动化测试共 9 项，覆盖 Recipe 白名单、固定数组边界、创意光效授权、黑白风格冲突、构图保留率、JPEG 渲染、ICC 往返、16 位 TIFF 以及确定性源像素瑕疵修复。

## 影像蒸馏

`scene-distillation-zine` 将用户提供的照片转化为独立成画的插画风纸海报，最终画面不保留任何照片像素；强调第一眼的普适美感、清晰的主角和协调的构图色彩，同时保留一处来自源图的安静张力。支持「单色块模式」触发词。输出为生成图像、简短中文创作说明与美术指导说明。

## 实景拼贴

`scenes-gathered-zine` 将照片转化为编辑风纸海报，以摄影真实作为主导的事实与情感锚点，默认至少 25% 的设计留白纸面；用户要求杂志、编辑或作者性排版时，切换为更不对称的编辑版式。输出为生成图像与简短中文创作说明。

## 版本

当前版本：`v1.2.0`（2026-08-11）。详细内容见 [版本变更记录](CHANGELOG.md)。

## 项目结构

```text
grilling/                    方案追问
grill-me/                    方案追问别名
grill-with-docs/             方案追问别名（含文档产出）
java-dev/                    阿里 Java 开发规范
plan-mode/                   Claude Code Plan Mode 复刻
refine-photos/               确定性摄影精修
scene-distillation-zine/     影像蒸馏纸海报
scenes-gathered-zine/        实景拼贴纸海报
```

每个 Skill 目录遵循统一结构：

```text
<skill>/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── (scripts/、schemas/、tests/ 按需)
```
