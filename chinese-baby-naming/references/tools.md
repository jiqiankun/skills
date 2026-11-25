# 可选确定性助手

只在批量候选、严格约束或数字算分需要复核时运行 [name_checks.py](../scripts/name_checks.py)。普通取名直接语言分析即可。Python 3.10+ 标准库，无网络、第三方包或付费 API。

从仓库根目录运行：

```powershell
python -B chinese-baby-naming/scripts/name_checks.py chinese-baby-naming/tests/sample-input.json
```

从其他目录运行时，将脚本与输入文件替换为各自实际路径。也可传 `-` 从 UTF-8 标准输入读 JSON。`--help` 返回 JSON 用法。文件可含 UTF-8 BOM；输出是 ASCII 转义的合法 UTF-8 JSON，避免 Windows 终端编码误差。成功退出 0；无效输入、无法读取文件等返回 JSON `error`、退出 2，不输出 traceback。

## 输入约定

```json
{
  "surname": "欧阳",
  "constraints": {
    "banned_chars": ["梓", "轩"],
    "banned_names": [],
    "rejected_names": ["欧阳旧名"],
    "required_chars": [],
    "given_lengths": [2]
  },
  "candidates": [
    {
      "given": "明川",
      "scores": {
        "phonology": {"value": 4, "reason": "人工观察理由；本例只示范结构。"},
        "family": {"value": null, "reason": "没有家庭偏好信息。"}
      },
      "risks": [{"severity": "unverified", "reason": "方言尚未核对。"}]
    }
  ]
}
```

- 根必填 `surname`、非空 `candidates`；不自动拆姓，完整姓名由 `surname + given` 构成。多个不同姓氏分批处理。
- 姓名保留字形，只裁切首尾空白，不做简繁、异体、NFC/NFKC 转换；拒绝内部空白、控制字符和无效代理字符。允许扩展汉字输入，但不判断其登记合法性。
- `banned_chars` 与 `required_chars` 为单字符列表，只作用于新取的名字；`banned_names`、`rejected_names` 是完整姓名。名长为 Unicode 字符数量；`given_lengths` 缺省/空数组表示不限。精确字辈位置、偏旁与语义避讳须由 Agent 另行检查。
- `scores` 的键只能是 `phonology`、`meaning`、`usability`、`longevity`、`distinctiveness`、`context`、`family`；每项为 `{value, reason}`。值须为 0～5 有限数或 `null`，理由非空。缺项补未知，不能填中分。
- `risks` 的级别只能为 `serious / moderate / minor / none / unverified`，每项附非空理由。严重风险来自人工输入，工具不判断理由是否真实充分。
- 可选 `weights` 必须一次给齐七个键，0～100 非负数且合计恰为 100；默认依次 20/20/20/15/10/10/5。零权重的未知项不妨碍总分。
- 所有层拒绝未知字段、重复 JSON 键、布尔值冒充数字、NaN/Infinity、冲突约束及无效类型。传统分数没有输入字段，不能悄悄并入现代分。

## 如何解释输出

`candidates` 按输入顺序保留所有评估，`duplicate` 和 `duplicate_of` 标识相同全名；索引从 0 开始。`unique_full_names` 为首次出现顺序的去重名单，`duplicates` 记录重复索引。对重复姓名必须查看全部证据，不能只保留第一条评分。任何一条同名评估有严重风险，该全名所有评估均 `blocked=true`，传播原因会注明另一评估索引。

每个候选包含：

| 字段 | 含义 |
|---|---|
| `objective_checks` | 明确约束的 `pass/fail` 和未实现检查的 `unverified`，均带理由；未设约束会注明「无此限制」 |
| `hard_constraints_passed` | 仅表示所给机械约束没有失败；不等于所有客观检查通过 |
| `blocked` / `blocked_reasons` | 违约或严重风险的独立拦截；不被拦截不等于推荐 |
| `scores` / `contributions` | 人工输入各维判断及加权贡献，不是脚本自动评名 |
| `coverage` | 已知权重、未知权重及维度；`percent` 是已知权重百分比，不是证据可信概率 |
| `score` | 所有非零权重维已填时，按公式半入取整数；否则 `null` |
| `score_interval` | 已知贡献向下取整至「已知贡献＋未知权重」向上取整的数学范围，不是置信区间；完整分仍保留向外取整范围 |

样例文件的首个候选已知权重 85%，已知贡献 66，未知权重 15，因此 `score=null`、区间 `[66,81]`。第二条保留重复评估，第三条因禁字而拦截。它们只是结构演示，未验证任何实际名字质量。

工具固定将字表、户籍、读音、方言、重名人数、语义典故、审美列为 `unverified`，因为它没有对应数据和能力。即使人工评分理由写「已查」，脚本也不能把这些项目升级为验证通过；Agent 应另附实际证据。脚本不排序，不能直接把输出当最终推荐榜单。

测试命令见 [README](../README.md)，具体执行结果见 [verification.md](../tests/verification.md)。
