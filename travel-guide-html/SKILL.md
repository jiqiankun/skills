---
name: travel-guide-html
description: "生成「攻略优先」的单文件 HTML 交互式旅行攻略。触发场景：用户要做一个可规划、可在旅行中直接打开使用的多日行程单（含每日时间轴、每日 Dashboard、可展开景点攻略、住宿推荐（含地理理由）、伴手礼/特产清单（含购买地址与理由）、备用方案、附近顺路推荐、美食增强、总览页与准备清单页），且强调移动端友好、无需地图。视觉默认 Stripe 风格（清爽柔光渐变），移动优先响应式设计。涉及「做一份 X 天 X 地旅游攻略 / 行程规划单 / 旅行计划 HTML / 手机看的攻略」等出行场景时使用。"
agent_created: true
version: 1.3.0
---

# 交互式旅行攻略 HTML 生成器（无地图 · 移动优先）

把一次多日旅行的行程规划，渲染为**单个可直接双击打开、手机可顺畅浏览的 HTML 文件**：攻略内容为主体，**不内置任何地图模块**（无地图底图、无小地图、无坐标依赖）。默认进入「总览」，按需展开每日正文、景点攻略、备用方案。

## 何时使用

- 用户要「做一份 X 天 X 地旅游攻略 / 行程规划单 / 旅行计划 HTML」，并希望手机能直接看、能离线用。
- 用户强调：兼顾历史文化 / 美食 / 自然 / 夜生活；美食餐厅、交通方式+耗时、实用攻略；总览和准备清单；**移动端友好**。
- 用户明确**不要地图 / 去掉地图 / 移动端优先**时，本技能即标准形态（无地图、无需坐标）。

## 核心设计原则（务必遵守）

1. **单一文件、零外部依赖**：所有 CSS / JS / 数据**内联**，不引用任何 CDN `<script>`（无任何地图、无第三方库）。双击即开、离线可用。
2. **无地图模块**：页面**不渲染任何地图**（不放 `TMap`、不写地图 Key、不保留坐标连线），数据中**不含 `lat/lng` 坐标字段**。
3. **移动优先（Mobile-First）响应式**：CSS 以窄屏为默认，桌面用 `@media(min-width:...)` 增强。单栏布局；导航 Tab 横向滚动并吸顶；详情网格窄屏单列、≥560px 两列。
4. **高频直显，低频折叠**：Dashboard 高频信息直接显示；景点详细攻略 / 备用方案 / 附近推荐按需展开（`<details>` 或点击「展开攻略」）。
5. **配色稳定**：沿用 Stripe 风（浅色底 + 柔光渐变 banner），三类 POI 固定配色：景点=青绿、美食=珊瑚红、文化=紫罗兰、交通=中性灰。不要随意改主色。

## 工作流（逻辑顺序）

### Step 1 · 设计数据模型（无需坐标）

按 `references/data-model.md` 的 schema 组织全部内容（总览 / 准备清单 / 每日 / POI / 美食 / 内部路线 / 附近推荐 / 备用方案）。**先想清楚数据再写 HTML**，字段缺失会导致渲染错位。

- POI **不含 `lat/lng` 坐标字段**（地图已移除、坐标无用途），不要为 POI 添加坐标。
- 交通方式（`move`）仍要写明「🚄 动车约2h」「🚕 打车约20min」等，这是攻略核心，与地图无关。

### Step 2 · 生成单文件 HTML

- 结构、CSS 变量、组件规范见 `references/layout-spec.md`。
- 直接以 `assets/guide-template.html` 为骨架改写（已是无地图、移动优先的单文件骨架：banner + 吸顶横向滚动导航 + 总览/DAY/特产/准备清单四页切换 + 卡片展开逻辑）。
- 关键交互：顶部导航 **总览 / DAY1–DAYn / 特产 / 准备清单** 横向滚动并居中，切换时当前 Tab 自动滚入视野；点卡片「▾ 展开攻略」展开 POI 详情（停留/顺序/必看/拍照/门票/预约/避坑/便民/内部路线/附近推荐）。
- 大型景区（九寨沟 / 黄龙 / 熊猫基地 / 冰雪大世界 / 亚布力）不要只当普通 POI：补 `internal` 内部游览路线（先去哪、如何乘车、哪段步行、优先级）。
- 不要引入 `map.qq.com` 的 `<script>`；不要写 `TMap`、`flyToPoi`、`drawDay`、`initMap` 等地图代码。

### Step 3 · 校验后交付

跑 Node 校验，全部通过再 `present_files`：

```bash
node -e 'const fs=require("fs");const h=fs.readFileSync("X.html","utf8");
const re=/gljs\?[^"\x27]*[?&]key=[A-Z0-9-]{20,}/;console.log("KEY_HIT(应为false):",re.test(h));
const m=[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)];
require("fs").writeFileSync("c.js",m[m.length-1][1]);'
node --check c.js && echo SYNTAX_OK && rm c.js
```

校验项：`KEY_HIT` 必须为 `false`（无地图 Key）、内联 JS 语法、Dashboard/备用方案/内部路线/附近推荐/美食增强/总览/准备清单 字段计数、无 `TMap`/`mapPanel`/`flyToPoi` 残留。中文匹配用 `Grep` 工具而非 node 内联（shell 编码会误判为 0）。

## 资源

- `references/data-model.md` — 完整 JSON 数据模型 schema（字段名 + 含义 + 示例；**无坐标字段**）。
- `references/layout-spec.md` — 页面布局规范（移动优先、CSS 变量、组件清单、交互行为、Stripe 风）。
- `assets/guide-template.html` — 可改写的单文件骨架（无地图、移动优先、四页切换）。
