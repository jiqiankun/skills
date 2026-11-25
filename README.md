# Codex Skills

个人维护的 Codex Skills 集合，面向需要澄清方案、练习后端面试、规范 Java 开发、中文宝宝取名，或制作照片海报与旅行攻略的用户。每个 Skill 提供可复用的工作流程，由 Codex 读取指令并结合当前会话、文件和可用工具执行。

本仓库按 Skill 目录分发，没有统一应用、构建入口或依赖安装步骤；按需要安装即可。最近记录版本为 `v2.2.0`（2026-10-17），最新未发布变更见 [CHANGELOG](CHANGELOG.md) 的 `Unreleased` 部分。

## Skills 总览

共 9 个 Skill 目录，其中 2 个是方案追问的快捷入口。

| 分类 | Skill | 核心功能与适用场景 | 文档入口 |
|---|---|---|---|
| 方案推敲 | `grilling` | 对计划、决策或设计逐个问题追问，附建议答案，帮助澄清取舍 | [使用说明](#方案追问)、[执行指令](grilling/SKILL.md) |
| 方案推敲 | `grill-me` | 显式启动 `grilling` 的快捷入口，需同时安装主 Skill | [依赖说明](#方案追问)、[执行指令](grill-me/SKILL.md) |
| 方案推敲 | `grill-with-docs` | 追问并结合领域建模沉淀文档；还依赖仓库外的 `domain-modeling` | [依赖说明](#方案追问)、[执行指令](grill-with-docs/SKILL.md) |
| 开发与面试 | `java-dev` | 基于阿里 Java 开发手册（嵩山版）的编码、评审、重构及设计指导 | [使用说明](#java-开发规范)、[规范索引](java-dev/SKILL.md#reference-documentation) |
| 开发与面试 | `backend-mock-interview` | 结合 JD、真实经历和回答动态面试，提供岗位匹配复盘及重答训练 | [使用指南](docs/backend-mock-interview.md)、[执行指令](backend-mock-interview/SKILL.md) |
| 生活与取名 | `chinese-baby-naming` | 按完整姓名分析音形义、出处及使用风险，生成、比较并定向优化候选（传统姓名学可选） | [使用说明](chinese-baby-naming/README.md)、[执行指令](chinese-baby-naming/SKILL.md) |
| 图像创作 | `scene-distillation-zine` | 把照片重新创作为插画纸海报，最终不保留摄影像素 | [海报选型与示例](docs/photo-posters.md)、[执行指令](scene-distillation-zine/SKILL.md) |
| 图像创作 | `scenes-gathered-zine` | 保留摄影主体，以留白、插画与克制拼贴制作编辑风纸海报 | [海报选型与示例](docs/photo-posters.md)、[执行指令](scenes-gathered-zine/SKILL.md) |
| 旅行交付 | `travel-guide-html` | 规划旅行、整理已有行程或修改攻略，交付手机优先、支持打印导出的单文件 HTML | [使用指南](docs/travel-guide-html.md)、[执行指令](travel-guide-html/SKILL.md) |

两种海报都需要原照片及图像生成能力；旅行规划需要联网核验动态信息，最终 HTML 可引用在线资源；中文宝宝取名的普通使用不依赖 Python，可选辅助脚本仅做机械约束、同名标记与算分。这些运行环境能力由宿主提供，复制 Skill 本身不会安装工具。

## 安装与快速上手

### 选择安装位置

当前 Codex 官方文档推荐以下本地目录。将完整 Skill 文件夹放入其中，保留 `SKILL.md` 及其资源的相对位置；只克隆本仓库不会自动安装根目录下的 Skill。

| 范围 | 位置 | 用途 |
|---|---|---|
| 个人 | `~/.agents/skills/<skill>/` | 在个人多个项目中使用 |
| 项目 | `<目标项目>/.agents/skills/<skill>/` | 随目标项目维护，供该项目使用 |

既有环境或安装器可能仍使用 `$CODEX_HOME/skills`（默认 `~/.codex/skills`）。已有安装应先核对客户端实际识别的目录，避免在多个位置重复放置同名 Skill。路径与调用方式已于 2026-10-16 核对 [Codex 官方 Skills 文档](https://learn.chatgpt.com/docs/build-skills)。

### 复制完整目录

以下以 Windows PowerShell 的个人安装为例。尚未取得仓库时，先执行（需要 Git）：

```powershell
git clone https://github.com/jiqiankun/skills.git
Set-Location .\skills
```

在仓库根目录选择并复制一个 Skill：

```powershell
$skillName = "backend-mock-interview"
$skillRoot = Join-Path $HOME ".agents\skills"
$destination = Join-Path $skillRoot $skillName
if (Test-Path -LiteralPath $destination) { throw "目标目录已存在，请先按下方更新说明处理：$destination" }
New-Item -ItemType Directory -Force -Path $skillRoot | Out-Null
Copy-Item -LiteralPath ".\$skillName" -Destination $destination -Recurse
```

更换 `$skillName` 可安装其他 Skill；项目安装则把 `$skillRoot` 改为目标项目的 `.agents\skills` 绝对路径。安装 `grill-me` 时还要复制 `grilling`；`grill-with-docs` 的额外依赖见[方案追问](#方案追问)。

**更新已有安装**：先比较并备份本地自定义内容，将旧 Skill 文件夹移出技能扫描目录，再复制新目录，避免目录嵌套和已删除文件残留。更新仓库不会自动更新已经复制出去的安装副本。

### 启用与调用

安装后在后续对话中显式指定 Skill，例如：

```text
使用 $backend-mock-interview 开始一场后端模拟面试。
```

Codex CLI／IDE 可通过 `/skills` 或输入 `$` 选择技能；其他客户端使用其技能选择入口。新安装或修改未出现时，重启 Codex，并检查目录层级及 `SKILL.md` 的名称、描述是否正确；若曾在 `~/.codex/config.toml` 中禁用，还需恢复对应配置。无需为本集合设置统一配置文件。

## 方案追问

`grilling` 一次只问一个问题并等待反馈，每题附建议答案；能够从文件或工具查证的事实会自行查证，决策由用户确认。达成共同理解并获得确认前，不执行正在讨论的方案。

```text
使用 $grilling 帮我推敲订单服务的拆分方案，逐步确认业务边界、迁移顺序和失败回退。
```

`grill-me` 与 `grill-with-docs` 都要求显式调用，不依赖自动匹配。前者只转交给 `grilling`；后者还调用 `domain-modeling`，其描述目标包括 ADR 与术语表，但本仓库没有提供该外部 Skill 或安装来源。未自行配齐时，不能保证文档产出流程完整；可先单独使用 `grilling`。别名内部保留了 `/grilling`、`/domain-modeling` 写法，使用时需确认客户端能解析这些转交指令。

## Java 开发规范

`java-dev` 提供命名、编码、并发、异常与日志、MySQL、安全、单元测试和架构／API 设计指导。现有 [8 份分主题参考](java-dev/SKILL.md#reference-documentation) 已有完整索引，按任务查阅即可。

```text
使用 $java-dev 评审当前项目的订单服务，重点检查事务边界、异常日志和并发安全。
```

这是规范指导 Skill；加载它不要求预装 JDK、Maven 或测试框架。编译和测试仍取决于目标 Java 项目的工具链；参考代码片段并非独立可运行项目。

## 中文宝宝取名

`chinese-baby-naming` 支持从零取名、已有姓名评价、多个名字比较、定向优化、指定文化来源及明确请求的传统姓名学；始终按完整姓名分析并支持复姓、禁字、字辈与多轮约束继承，默认直接在聊天中交付。

```text
使用 $chinese-baby-naming，姓林，给宝宝推荐 3 个简洁自然的双字名，不用轩。
```

完整用法、多场景示例与外部工具边界见 [使用说明](chinese-baby-naming/README.md)，测试范围与限制见 [验收记录](chinese-baby-naming/tests/verification.md)。

## 项目结构与文档导航

```text
README.md                    项目总览、安装、选型与维护入口
CHANGELOG.md                 未发布变更与历史版本记录
docs/
├── backend-mock-interview.md 后端模拟面试使用指南
├── photo-posters.md          两种照片海报的选择与使用
└── travel-guide-html.md      旅行攻略输入、交付与模板维护
backend-mock-interview/       后端模拟面试
chinese-baby-naming/          中文宝宝取名、姓名分析与辅助脚本
grilling/                    方案追问主 Skill
grill-me/                    方案追问快捷入口
grill-with-docs/             追问与文档快捷入口（有外部依赖）
java-dev/                    Java 规范与 8 份参考
scene-distillation-zine/     插画纸海报
scenes-gathered-zine/        摄影拼贴纸海报
travel-guide-html/           旅行攻略指令、规范、模板与检查脚本
```

多入口或规则较丰富的用户指南集中在 `docs/` 目录（`chinese-baby-naming` 自带 [README](chinese-baby-naming/README.md)）；简单 Skill 直接在本页说明。各 Skill 的 `SKILL.md` 是执行入口，`references/` 是按需读取的规则；可选的 `agents/openai.yaml` 提供界面元数据，`assets/` 存放模板资源，`scripts/` 存放辅助脚本，`tests/` 存放验收用例，并非每个 Skill 都有这些目录。原有参考文件保留在各自 Skill 内，便于完整复制安装。

## 维护与扩展

- 新增 Skill 时，在根目录建立与技能名一致的目录，编写带 `name`、`description` 的 `SKILL.md`；只按实际需要添加引用、资源、脚本或界面元数据。
- 同步更新 Skills 总览和目录说明，提供一个能体现实际用途的调用示例；声明跨 Skill 依赖、外部工具要求及不适用场景。
- 仅在多入口、过程控制或使用限制需要展开时增加 `docs/` 用户指南。共用输入和限制优先合并说明，不把执行细则复制成另一份长期维护的规则。
- 修改能力、触发条件或依赖时，同步检查用户指南、相关别名及引用链接。改动 Java 规则时复用对应参考文档，改动旅行模板时按[指南中的维护说明](docs/travel-guide-html.md#维护模板与验收)执行检查。
- 将有意义的变更追加到 CHANGELOG 的 `Unreleased`，按新增、变更、修复、移除等分类，并注明涉及的 Skill、文档或兼容性影响。正式记录版本时再填写有依据的版本号和日期，不补造历史。
- 提交前检查 Markdown 相对链接、标题锚点、示例路径与目录清单；能力变化需按影响范围验证。历史验证结果不能替代本次检查，也不应把未测试的平台标记为通过。
