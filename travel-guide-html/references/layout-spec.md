# 页面布局规范（travel-guide-html · 无地图 · 移动优先）

视觉默认 **Stripe 风格**：浅色底、顶部柔光渐变 banner、卡片圆角 + 轻投影、强调色克制。单文件、所有 CSS/JS 内联、**零外部依赖（不引任何 CDN script）**、可离线打开。

## 设计基调

- **无地图模块**：页面不渲染任何地图（无 `TMap`、无 `#map` 容器、无地图 Key、无坐标连线），数据中**不含 `lat/lng` 坐标字段**。
- **移动优先（Mobile-First）**：CSS 以窄屏为默认，桌面用 `@media(min-width:...)` 增强。结构：banner → 吸顶横向滚动导航 → 单栏内容。

## 配色体系（CSS 变量，固定不要乱改）

```
--bg:#f6f9fc;            /* 页面底色 */
--card:#ffffff;
--ink:#0a2540;           /* 主文字 深蓝 */
--muted:#697386;         /* 次要文字 */
--line:#e6ebf1;          /* 分隔线 */
--scenic:#11b3a3;        /* 景点 青绿 */
--food:#ff6b6b;          /* 美食 珊瑚红 */
--culture:#8b7cf6;       /* 文化 紫罗兰 */
--transit:#9aa5b1;      /* 交通 灰 */
--route:#3b82f6;        /* 强调蓝（展开按钮等） */
--photo:#e8590c;        /* 摄影模块专属暖橙（机位标签，不替代主色） */
/* 强度三色：轻松 #2bbf7a / 适中 #f5a623 / 较累 #ef5b5b */
```

banner 用渐变：`linear-gradient(120deg,#0a2540,#1a3a6b 60%,#11b3a3)` + 顶部柔光高光（伪元素径向白光）。

📷 拍照打卡模块统一使用暖橙系浅底：区块底 `#fffaf5`、描边 `#ffe8d1`、标签底 `#fff0e3`/字 `#c14a0c`，与四类 POI 配色区分但视觉权重明显低于景点介绍。

## 组件清单（自上而下）

### 1. 顶部 Banner（移动优先：徽章居中堆叠于标题下方）
- 大标题（如「南京 → 哈尔滨 · 东北冰雪 5 日攻略」）+ 副标题（出行日期/人数），均 `text-align:center`。
- 3 枚**徽章**：天数 / POI 数 / 总预算（如 `5 天` `19 POI` `≈¥10,000`）。
- 移动优先实现（**易错**）：`.badges` 默认 `display:flex; justify-content:center; flex-wrap:wrap; margin-top:14px`（堆叠在标题下方居中）。`@media(min-width:760px)` 时改 `position:absolute; top:50%; right:24px; transform:translateY(-50%)`，同时 `.banner` 设 `padding-right:280px` 预留右侧空间。**绝不能在同一条规则里混写 `position:absolute` 和 `position:relative`**（会覆盖，徽章掉到标题下方左侧）。

### 2. 顶部导航 Tab（横向滚动 + 吸顶 + 居中）
- 项：**总览 / DAY 1 / DAY 2 / … / DAY n / 特产 / 准备清单**；每项前缀小图标（总览 🧭 / DAYn 用数据 `icon` 字段 / 特产 🎁 / 准备清单 ✅），图标+文字作为一个整体按钮居中。
- 默认高亮「总览」。`position:sticky; top:0` 吸顶；`overflow-x:auto`（移动端可横向滑动，隐藏滚动条）；按钮 `white-space:nowrap; flex:0 0 auto`。
- **水平居中（易错）**：`.nav` 加 `.nav::before,.nav::after{content:"";margin:auto}`——两个空伪元素各占一半剩余空间，把导航项整体推向正中（宽屏居中）；内容溢出时 `margin:auto` 自动归零、从起始位排列，**横向滚动不受影响、左侧不裁切**。不要用 `justify-content:center`（溢出时会裁掉左侧且滚不到头）。
- 切换时当前 Tab 调 `scrollIntoView({block:"nearest",inline:"center"})` 自动滚入视野。

## 页面居中（整体原则）

- 内容主体 `.layout` 恒为 `max-width:920px; margin:0 auto`（桌面水平居中，窄屏铺满）。
- **区块标题** `.sec h2` 统一 `text-align:center`（总览/每日/准备清单/特产各页标题居中）。
- **每日 Dashboard** `.dash` 加 `justify-content:center`，信息条居中排布。
- **Banner 桌面端（易错）**：`@media(min-width:760px)` 下 `.banner` 用**左右对称** padding（如 `34px 280px 30px 280px`），保证标题在视口正中；若左右 padding 不对称，`text-align:center` 只在剩余区域内居中，标题会明显左偏。

### 3. 总览页（renderOverview，单栏）
- 整体路线（一行文字/流向）。
- 每日核心安排（卡片网格，窄屏单列、`≥560px` 多列 auto-fill：日期+标题+亮点）。
- 总预算（总额 + breakdown 条形/列表）。
- 交通结构（飞机/动车/直通车 三段）。
- **住宿推荐**（`STAY`）：summary 一段 + areas 卡片网格（区域/价格/理由/适合哪几天）。
- 行程强度分布（day → 轻松/适中/较累 chip）。
- 重要预约项目（item + 提前多久）。

### 4. 每日页（renderDay，单栏主体）
- **每日 Dashboard**：一行可换行信息条（`.dash` flex-wrap，居中），含 天气 🌤 / 穿衣 🧥 / 当日预算 💰 / 强度 chip / 步行 🚶 / 主交通耗时 ⏱ / 最高海拔 ⛰(高原日) / 今日亮点 ✨。
- **住宿蓝条（.stay-line）**：每日头部 summary 下方展示「🏨 今晚住宿：区域 + 地理理由（stayWhy）」——说明住哪、为什么（结合次日景点地理，减少往返）。
- **不设日级摄影模块**：每日页只有 Dashboard + 时间轴，**没有**「今日必拍 / 摄影时间轴 / 摄影路线 / 追光计划」之类的独立摄影区块。摄影信息只出现在地点卡片展开区内（见组件 7）。
- **时间轴卡片列表**（按 `t` 排序）：左侧竖线 + 圆点（圆点颜色 = cat 配色），卡片含：
  - 顶部：时间 `t` + 类别标签（景点/美食/文化/交通 小 pill，配色）+ 名称。
  - 简介 `desc` + 贴士 `tip`（高频直显）。
  - 交通行 `move`（🚦 图标）：写明交通方式与预计耗时（如「🚄 动车约2h」「🚕 打车约20min」）。
  - 元信息：停留 `stay`、门票 `ticket`（小字）。
  - 「展开攻略 ▾」按钮 → 展开区块（窄屏单列、`≥560px` 两列）：`best/booking/avoid/nearby/order/mustsee/photo` + **📷 拍照打卡（photo_info，见组件 7）** + 大型景区 `internal` 内部路线 + `nearbyRecs` 附近推荐 + 美食类 `rtype/avg/dishes/order2/spice/queue/worth`（景观餐厅也可挂 photo_info）。
  - **「备用方案 ▾」** 折叠（`<details>`）：完整 / 轻松 / 雨天 / 精简 四段。

### 7. 地点卡内 📷 拍照打卡（.photo-info，轻量、可选、次级信息）

仅当 POI 含 `photo_info` 时渲染，位于展开详情网格中、跨两列，作为**地点的附属补充信息**（无独立摄影页、无日级摄影模块）。视觉上明显小于景点介绍：暖橙浅底小框（底 `#fffaf5`、描边 `#ffe8d1`），内容控制在 3–5 行：

- 标题行：`📷 拍照打卡`。
- 机位（`spots[]`，**1–2 个**）：每行 `机位名（location）` + 主题小标签（`subjects[]`，`.ps-tag` 胶囊、flex-wrap 不横向滚动）+ 一句拍法（`tip`，手机优先：1x/2x/0.5x、人像模式、夜景模式、简单构图/站位）。
- 参考时间（`best_time`）：一行小字，标注「仅供参考」。
- 当前计划（`schedule_note`）：对照该地点**已锁定的游玩时间**说明——默认「当前时段也适合拍 / 无需调整」；或给出 **≤30 分钟的可选微调**（如「16:30 微调至 17:00 赶日落前柔光，不影响晚餐」），仍以「按原时间到也能拍」收尾。

红线：
- 模块篇幅不得超过景点介绍本身；不值得拍的地点（停车场、中转点、普通餐厅）不渲染。
- 微调幅度 ≤30 分钟、不动景点/顺序/餐住/交通衔接；超过即过度调整，禁止出现在页面上。
- 文案只回答「到了顺手怎么拍」或「小幅挪半小时值不值」；不写「为了拍应该几点到」的大改建议。
- 不出现光圈/快门/ISO/RAW/滤镜等专业参数；相机焦段最多一句话带过或省略。
- 随「展开攻略」整体折叠，默认页不拥挤；美食卡（cat:food）同样支持（景观餐厅「顺手拍」）。

### 5. 特产页（renderSouvenirs，可选）
- 独立导航「特产」：SOUVENIRS 卡片网格（窄屏单列、`≥560px` 两列）。
- 每张卡：类别 pill + 名称 + 参考价 + **📍 购买地址** + **💡 推荐理由**（理由写清代表性/好携带/性价比）。
- 页头一段购买提示（集中采购点、液体托运、真空可带上机等）。

### 6. 准备清单页（renderPrep，单栏）
- 按 `groups[]` 分组（机票/高铁/酒店/门票/观光车索道/演出…），每组卡片列出「项目 + 建议提前多久预订」；酒店组备注「优先订 STAY 推荐区域」；用颜色/图标区分紧急度。

## 交互行为清单

- 默认进入「总览」保持清爽。
- 高频（Dashboard、卡片简介/贴士/交通/停留/门票）直显；低频（详细攻略含 📷 拍照打卡、备用、附近）折叠/按需。
- 点卡片「▾ 展开攻略」展开 POI 详情（内含轻量 📷 拍照打卡）；「收起攻略」收起。无需地图联动。
- 摄影信息**只做行程的附属补充**：行程时间轴、景点顺序、用餐住宿先确定并锁定，之后才在地点卡内补拍照提示；页面上不出现任何独立摄影区块。schedule_note 里的微调建议 ≤30 分钟且必须附「按原时间到也能拍」，不得暗示大改行程。
- 所有展开/收起用 `element.classList.toggle("open")` + 行内 `style.maxHeight` 或 `<details>` 原生折叠，无框架依赖。

## 技术要点（单文件 HTML，零依赖）

- `<head>` 内：`<meta charset><meta name="viewport" content="width=device-width, initial-scale=1.0">`。**不要引入任何外部 `<script>` / `<link>`**（零外部依赖）。
- 全部 CSS 写在 `<style>`（移动优先，桌面用 `@media(min-width:...)`）；数据 `OVERVIEW/PREP/DAYS` + 渲染逻辑写在末尾 `<script>`。
- JS 用原生（无框架）；渲染函数 `renderOverview / renderDay / renderSouvenirs / renderPrep`，**不含任何地图相关函数**。
- 校验：内联 JS 用 `node --check`（见 SKILL.md Step 3）；中文匹配用 Grep 工具避免 shell 编码误判。`KEY_HIT` 必须为 `false`。
