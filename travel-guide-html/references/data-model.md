# 数据模型 Schema（travel-guide-html）

全部数据集中在 HTML 内联 `<script>` 的 `OVERVIEW` / `PREP` / `DAYS` / `STAY` / `SOUVENIRS` 五个变量里。字段名用短 key，渲染层按 key 读取。下面给出完整结构。

## 顶层：总览 OVERVIEW

```js
const OVERVIEW = {
  route: "南京 → 成都(2晚) → 九寨沟/黄龙(2晚) → 成都 → 南京",
  dailyCore: [
    { day: "DAY 1", title: "抵蓉 · 武侯祠/锦里/春熙路", highlights: "武侯祠三国文化、锦里小吃、九眼桥夜生活" },
    // ...每个 day 一条
  ],
  budget: {
    total: "≈ ¥9,800（2人）",
    breakdown: [
      { item: "往返机票(南京⇄成都)", amount: "¥3,600" },
      { item: "动车+景区直通车(成都⇄九寨)", amount: "¥760" },
      { item: "住宿 4 晚", amount: "¥2,400" },
      { item: "门票+观光车+索道", amount: "¥1,740" },
      { item: "餐饮", amount: "¥1,200" },
      { item: "市内交通", amount: "¥100" }
    ]
  },
  transport: [
    { mode: "✈️ 飞机", detail: "南京禄口 ⇄ 成都天府，往返约 ¥1,800/人" },
    { mode: "🚄 动车", detail: "成都东 ⇄ 黄龙九寨站，约 2h，二等座 ¥143" },
    { mode: "🚌 直通车", detail: "黄龙九寨站 ⇄ 黄龙/九寨沟口，九旅悦行约 1h" }
  ],
  intensity: [
    { day: "DAY 1", level: "适中" },   // 轻松 / 适中 / 较累
    { day: "DAY 2", level: "较累" }
  ],
  bookings: [
    { item: "机票", lead: "提前 1–2 个月" },
    { item: "成都东→黄龙九寨站动车票", lead: "提前 3–10 天(旺季秒空)" },
    { item: "九寨沟/黄龙门票(阿坝旅游网实名)", lead: "提前 1–3 天，旺季限流" },
    { item: "酒店(沟口/市区)", lead: "提前 2–4 周" }
  ]
};
```

## 顶层：准备清单 PREP

```js
const PREP = {
  groups: [
    { cat: "机票", items: [ { name: "南京⇄成都 往返", lead: "提前 1–2 个月" } ] },
    { cat: "高铁票", items: [ { name: "成都东→黄龙九寨站(去/回)", lead: "提前 3–10 天" } ] },
    { cat: "酒店", items: [ { name: "成都市区 2 晚 / 九寨沟口 1–2 晚", lead: "提前 2–4 周" } ] },
    { cat: "景区门票", items: [ { name: "九寨沟 ¥169+观光车 ¥90 / 黄龙 ¥170+索道", lead: "提前 1–3 天" } ] },
    { cat: "观光车/索道", items: [ { name: "九寨观光车 / 黄龙上行索道 ¥80", lead: "购票时一并选" } ] },
    { cat: "演出", items: [ { name: "藏羌风情晚会(可选)", lead: "沟口现场或携程" } ] }
  ]
};
```

## 顶层：住宿推荐 STAY（可选）

渲染在「总览」页「住宿推荐」区块，并供每天 `stay` 字段引用同一区域名。

```js
const STAY = {
  summary: "全程以「市中心/景区附近」为大本营，减少每日交通往返；高原/山区日可按需加住一晚。",
  areas: [
    { area: "市中心·核心区", price: "¥300–600/晚", reason: "步行/地铁可达多数景点，吃饭逛街集中", fit: "多数日大本营（推荐）" },
    { area: "景区附近(可选)", price: "¥400–800/晚", reason: "看完返程直接回酒店、免深夜奔波", fit: "深度游某景区时可选" }
  ]
};
```

## 顶层：伴手礼 SOUVENIRS（可选）

渲染为独立「特产」导航页（`总览 / DAY1..N / 特产 / 准备清单`），每项必须含**购买地址**与**推荐理由**。

```js
const SOUVENIRS = [
  { name: "特产A", type: "类别(肉制品/山货/饮品…)", where: "老字号/商场/超市地址", price: "¥35–50/斤", reason: "推荐理由：代表性、好携带、性价比" }
];
```

## 顶层：每日 DAYS[]

```js
const DAYS = [
  {
    day: "DAY 1", icon: "🏮", date: "10/27 周二", title: "抵蓉 · 武侯祠与锦里",   // icon 为导航图标（可选，缺省 🗓）
    summary: "落地成都，武侯祠追三国，锦里尝小吃，夜逛九眼桥。",
    // —— 每日 Dashboard 字段 ——
    weather: "18–24°C 多云转晴",
    clothing: "薄外套+舒适步行鞋",
    budget: "≈ ¥2,100（2人）",
    intensity: "适中",            // 轻松 / 适中 / 较累（三色 chip）
    walk: "≈ 1.2 万步",
    transportTime: "主交通 ≈ 1.5h",
    maxAlt: "500m",               // 涉及高原日才写，如 DAY2 "2977m 黄龙九寨站"
    highlights: "武侯祠 · 锦里小吃 · 九眼桥夜酒",
    // —— 每日住宿（结合次日景点地理位置）——
    stay: "市中心·春熙路/太古里一带",   // 今晚住哪（区域/酒店范围）
    stayWhy: "首晚落地就近入住，放行李即可步行逛春熙路，次日去景区地铁直达",  // 为什么住这（地理考量）
    // —— POI 列表（时间轴）——
    pois: [ /* 见下 */ ],
    // —— 备用方案（4 个折叠）——
    spare: {
      complete: "完整路线…………",
      easy: "轻松版（删减步行项）…………",
      rainy: "雨天备用（改室内：武侯祠/锦里/博物馆/茶馆）…………",
      short: "时间不足精简（只去武侯祠+锦里）…………"
    }
  },
  // ...DAY 2..5
];
```

## POI 对象（pois[] 内每一项）

```js
{
  t: "08:00",                          // 时间
  cat: "scenic",                       // scenic 景点 / food 美食 / culture 文化 / transit 交通
  name: "九寨沟景区",
  desc: "童话世界，108 个海子。",
  tip: "穿防滑鞋，带充电宝。",         // 卡片底部高频贴士

  // —— 每次地点变更的「交通 + 耗时」（23/24 个点都要，仅出发起点无）——
  move: "🚌 九旅悦行直通车约 1h（黄龙九寨站→沟口）",

  // —— 景点/文化类攻略（可展开）——
  stay: "全天 6–8h",                   // 推荐停留时间
  best: "07:30 开园先冲日则沟",        // 最佳游览时间
  booking: "阿坝旅游网实名预约，观光车 ¥90 必买",  // 预约方式
  avoid: "沟内餐厅贵且一般，自带干粮饮水",          // 避坑提醒
  nearby: "诺日朗服务中心(餐饮/厕所)、景区医疗站",  // 便民设施
  ticket: "门票 ¥169 + 观光车 ¥90",     // 门票信息
  order: "先乘观光车到原始森林→沿栈道下行→则查洼沟→树正沟", // 推荐游览顺序
  mustsee: "五花海、珍珠滩瀑布、长海、诺日朗瀑布",  // 必看内容
  photo: "五花海观景台、镜海倒影(无风晨间)",        // 推荐拍照点

  // —— 大型景区：内部游览路线（internal[]）——
  internal: [
    { mode: "🚌 观光车", text: "游客中心→原始森林(终点站)", priority: "high" },
    { mode: "🚶 步行", text: "箭竹海→熊猫海→五花海栈道(约 2h)", priority: "high" },
    { mode: "🚌 观光车", text: "五花海→诺日朗→则查洼沟长海", priority: "mid" }
    // priority: high 必去 / mid 中 / low 可省
  ],

  // —— 附近顺路推荐（nearbyRecs[]，每个主 POI 2–3 个）——
  nearbyRecs: [
    { name: "甘海子", tag: "顺路推荐" },     // 顺路推荐 / 有时间再去 / 不建议专程
    { name: "甲勿海", tag: "有时间再去" }
  ]
}
```

## 美食 POI 增强字段（cat:"food"）

在普通 POI 字段基础上，额外：

```js
{
  t: "12:30", cat: "food", name: "蜀大侠火锅(春熙路)",
  rtype: "川味火锅",
  avg: "¥110/人",
  dishes: "麻辣牛油锅 / 鲜毛肚 / 变脸表演",
  order2: "2 人点 4 荤 3 素 1 锅 + 小吃拼盘",   // 2人建议点法
  spice: "🌶🌶🌶🌶 重辣",                         // 辣度
  queue: "晚市常排 30–60min，建议 17:00 前或公众号取号", // 排队情况
  worth: "值得专程去",                              // 值得专程 / 顺路吃即可
  move: "🚇 地铁 2/3 号线春熙路站步行 10min",
  // best/nearby/ticket 对餐厅一般省略，保留 desc+tip
}
```

## 字段速查（渲染层按 key 读取）

| key | 含义 | 适用 |
|-----|------|------|
| `t` `cat` `name` `desc` `tip` | 基础 | 所有 POI（**不含 `lat/lng` 坐标字段**：地图已移除，坐标无用途，不要添加） |
| `move` | 交通方式+耗时 | 除出发起点外所有 |
| `stay` `best` `booking` `avoid` `nearby` `ticket` `order` `mustsee` `photo` | 景点攻略 | scenic / culture |
| `internal[]` | 景区内部路线 | 大型景区 |
| `nearbyRecs[]` | 附近顺路推荐 | 主要 POI |
| `rtype` `avg` `dishes` `order2` `spice` `queue` `worth` | 美食增强 | food |
| `weather` `clothing` `budget` `intensity` `walk` `transportTime` `maxAlt` `highlights` `spare{}` | 每日 Dashboard + 备用 | 每天 |
| `icon` | 导航 Tab 图标（可选，缺省 🗓） | 每天 |
| `stay` `stayWhy` | 当晚住宿区域+地理理由（每日头部蓝条展示） | 每天 |
| `route` `dailyCore[]` `budget{}` `transport[]` `intensity[]` `bookings[]` | 总览 | OVERVIEW |
| `groups[]` | 准备清单 | PREP |
| `summary` `areas[]` | 住宿推荐（总览页区块） | STAY |
| `name` `type` `where` `price` `reason` | 伴手礼/特产（独立「特产」页） | SOUVENIRS |
