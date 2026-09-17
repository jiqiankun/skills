# Codex Skills

个人 Codex Skills 集合，覆盖方案追问、Java 开发规范、纸海报创作与旅行攻略等场景。

## 技能总览

| Skill | 功能 | 适用场景 |
|---|---|---|
| `grilling` | 对计划、决策或想法进行连续追问访谈，一次一个问题并附推荐答案 | 方案压力测试、设计澄清 |
| `grill-me` | `grilling` 的快捷别名 | 直接以 `/grilling` 方式追问 |
| `grill-with-docs` | `grilling` 的快捷别名，额外产出 ADR 与术语表文档 | 需要边访谈边沉淀文档 |
| `java-dev` | 基于阿里 Java 开发手册（嵩山版）的 Java 开发规范 | Java 编码、评审、重构、数据库与 API 设计、单元测试、并发与安全 |
| `backend-mock-interview` | 根据 JD、真实经历与现场回答动态追问，探索能力边界，复盘后支持重答训练 | 初级、中级、高级后端模拟面试 |
| `scene-distillation-zine` | 将照片转化为插画风纸海报（不保留照片像素） | 编辑性视觉再诠释 |
| `scenes-gathered-zine` | 将照片转化为编辑风纸海报（以摄影真实为主导） | 美观易读的纸海报创作 |
| `travel-guide-html` | 规划并制作攻略内容优先、手机阅读舒适的单文件旅行 HTML（无地图） | 旅行 HTML、交互式网页攻略、已有行程转 HTML |

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

`travel-guide-html` 将旅行计划制作成**单个可直接打开、手机阅读舒适的 HTML 文件**，支持“规划并生成 HTML”和“已有行程转 HTML”两种入口。普通旅行咨询、纯文字行程和单项景点或酒店推荐不触发。规划时区分硬约束与偏好，核对顺路关系、首尾交通、用餐休息、行李安排及预算；关键动态信息注明来源、核验时间和待确认事项。

内容包含总览、每日时间轴与 Dashboard、可展开的景点玩法、住宿区域与地理理由、路线内的美食、异常备用方案、可选顺路推荐、伴手礼与准备清单。总览解释“为什么这样走”，核心景点讲清看点、游览顺序与取舍，不为填满模板堆砌栏目。

页面沿用 Stripe 风格，以浅色背景、柔和渐变、清晰卡片层级和响应式布局改善阅读。保留单文件、无地图和无坐标依赖；核心 CSS、JS 与正文内联，**不再强制离线或零网络依赖**，允许按需使用有来源的在线图片与资料链接。正文直接存在于 HTML，原生折叠配合轻量导航增强；JS 禁用或增强失败时仍可阅读，在线资源失效不应遮挡正文。

摄影是按需增强：普通攻略可附一句拍照提示，明确有摄影需求时再补机位、光线、时间与拍法，专业器材建议按需提供。普通旅行的可选时间微调每次不超过30分钟，须核对当天累计影响，不挤占餐住与硬性交通；摄影主导旅行在规划开始时识别。摄影信息放在地点详情内，不另建独立页面。

### 使用方式

将 Skill 安装到 Codex 个人目录：

```powershell
Copy-Item -LiteralPath .\travel-guide-html -Destination "$env:USERPROFILE\.codex\skills\travel-guide-html" -Recurse
```

在新的对话轮次中调用：

```text
使用 $travel-guide-html 规划 X 天 X 地旅行，并生成手机阅读舒适的单文件 HTML 攻略，不需要地图。

使用 $travel-guide-html 将下面已经确定的行程整理成 HTML，保留已订交通和住宿，补充景点玩法与实用提醒。
```

生成后按 [Skill 完成标准](travel-guide-html/SKILL.md) 检查行程可执行性、事实状态、预算一致性、手机布局和交互，再交付最终文件。使用在线资源时说明联网需求；手机文件管理器或内置预览器的支持情况以实际验证为准。

维护模板时可运行 `node travel-guide-html/scripts/check-template.cjs`，需要现有 Node、Playwright 和可用浏览器；`GUIDE_BROWSER` 可指定本机 Chromium 浏览器路径，`GUIDE_ENGINE` 可选已有的 WebKit 环境。测试依赖不进入最终 HTML，也不是使用 Skill 生成攻略的前置要求。

## 版本

当前版本：`v2.1.0`（2026-09-17）。详细内容见 [版本变更记录](CHANGELOG.md)。

## 项目结构

```text
grilling/                    方案追问
grill-me/                    方案追问别名
grill-with-docs/             方案追问别名（含文档产出）
java-dev/                    阿里 Java 开发规范
backend-mock-interview/       后端模拟面试与岗位匹配复盘
scene-distillation-zine/     影像蒸馏纸海报
scenes-gathered-zine/        实景拼贴纸海报
travel-guide-html/           交互式旅行攻略 HTML
```

每个 Skill 以 `SKILL.md` 为入口，其他目录按需提供：

```text
<skill>/
├── SKILL.md
├── agents/openai.yaml        可选的界面元数据
├── references/              按需读取的说明
├── assets/                  模板与资源
└── scripts/                 必要的生成或检查脚本
```
