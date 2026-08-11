# Dynamic Style System

Select at most one value from each layer. Fill omitted layers from the source and the aesthetic defaults. Never stack complete styles.

## Layer 1: photographic aesthetic

| ID | Chinese label | Aim | Default color | Default light |
|---|---|---|---|---|
| `natural` | 自然真实 | Accurate, source-led photography | `source-derived` | `source-derived` |
| `documentary` | 纪实克制 | Present-tense realism and retained texture | `neutral` | `natural-balanced` |
| `cinematic` | 电影叙事 | Narrative color separation and controlled density | `low-saturation` | `dimensional` |
| `film-retro` | 胶片复古 | Gentle roll-off, restrained color bias, optional grain | `low-saturation` | `airy-soft` |
| `black-and-white` | 黑白摄影 | Form, luminance, gesture, and material | `neutral` | `dimensional` |
| `palace-splendor` | 宫苑华章 | Formal architecture, traditional dress, and dignified color | `vermilion-gold` | `dimensional` |
| `jiangnan-elegance` | 江南雅韵 | Garden restraint, qipao, white walls, dark tiles, and quiet space | `qingdai-soft` | `airy-soft` |
| `huizhou-rainmist` | 徽州烟雨 | Low-color tonal depth in real rain, mist, water, and Huizhou architecture | `ink-low-color` | `mist-soft` |

Chinese aesthetics are photographic interpretations, not illustration transforms. Never add calligraphy, seals, paper texture, lanterns, costume elements, brush strokes, or manufactured mist.

## Layer 2: color tendency

| ID | Chinese label | Guardrail |
|---|---|---|
| `source-derived` | 原片导向 | Preserve the source palette and correct only supported problems. |
| `neutral` | 中性 | Avoid sterile skin or gray vegetation. |
| `warm-healing` | 暖调治愈 | Warm midtones gently; keep whites and skin from turning yellow. |
| `forest-fresh` | 森系清新 | Use only with real vegetation; prevent green spill on skin. |
| `cool-clean` | 冷调清透 | Keep skin and warm materials plausible. |
| `low-saturation` | 低饱和 | Preserve color separation instead of flattening everything to gray. |
| `vermilion-gold` | 朱砂雅金 | Protect skin, vermilion architecture, gold, black, and textile detail from clipping. |
| `qingdai-soft` | 青黛柔润 | Keep walls neutral, vegetation layered, and silk color distinct from the garden. |
| `ink-low-color` | 水墨低彩 | Build black-white-gray relationships from real light; retain small source-supported color accents. |

## Layer 3: light tendency

| ID | Chinese label | Guardrail |
|---|---|---|
| `source-derived` | 原片导向 | Follow captured light. |
| `natural-balanced` | 自然均衡 | Preserve believable contrast and dynamic range. |
| `airy-soft` | 清透柔和 | Lift midtones carefully; do not erase landscape depth. |
| `dimensional` | 立体质感 | Deepen form with controlled contrast; avoid crushed blacks and harsh skin. |
| `dramatic` | 戏剧层次 | Emphasize sky, terrain, or motivated light; protect people from collateral contrast. |
| `mist-soft` | 柔雾层次 | Preserve real haze and distance; never manufacture fog or watercolor texture. |

## Layer 4: style strength

- Level 1, `restrained`: subtle expression subordinate to correction.
- Level 2, `standard`: clearly readable style while the result remains photographic. This is the default.
- Level 3, `strong`: intentional stylization within every preservation and quality gate.

## Independent retouch strength

- Level 1, `light`: technical correction and minimal local refinement.
- Level 2, `refined`: detailed but texture-preserving local work. This is the default.
- Level 3, `deep`: broader local refinement with tighter quality limits; still no geometry or identity change.

Treat both levels as maximum budgets, not multipliers. Reduce actual work when source pixels, focus, noise, or subject scale do not support the selected level.

## Compatibility

- Reject `black-and-white` with `forest-fresh`, `warm-healing`, `cool-clean`, `vermilion-gold`, or `qingdai-soft`.
- Recommend `forest-fresh` only when vegetation materially contributes to the frame.
- Treat `palace-splendor`, `jiangnan-elegance`, and `huizhou-rainmist` as explicit or evidence-supported choices, never as ethnicity-based defaults.
- Let explicit compatible color or light choices override an aesthetic default.
- If two full styles are requested, select one primary aesthetic and translate the other request into a compatible color or light tendency; ask only when the conflict changes the intended result materially.
