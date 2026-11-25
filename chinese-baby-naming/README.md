# 中文宝宝取名 Skill

实际入口为 [SKILL.md](SKILL.md)。适用于宝宝中文正式姓名，也支持已有姓名分析、横向比较、定向改字、指定典籍来源和用户明确请求的传统文化参考。

核心是完整姓名的音形义、长期使用和独立风险筛查。七维比较默认权重为 20/20/20/15/10/10/5；分数可解释，未知项不填分。传统分析与现代分数、排序分开。

## 使用与安装

本目录是技能源文件，位于技能集合仓库中；放在仓库根目录本身不保证进入宿主的自动发现列表。当前会话可直接指定路径：

```text
使用 E:\jqk_code\skills\chinese-baby-naming\SKILL.md，姓林，给宝宝推荐3个简洁自然的名字。
```

需要自动发现时，将整个 `chinese-baby-naming` 文件夹复制到宿主的技能搜索目录。[OpenAI 官方文档](https://developers.openai.com/codex/skills/) 当前列出用户级 `~/.agents/skills` 和项目级 `.agents/skills`。已有环境若另行配置了技能目录，以实际 Skills 列表为准。不要同时复制多份同名技能。

Windows 用户级安装示例（目标已存在则先自行比较，命令不会覆盖）：

```powershell
$namingSource = Join-Path (Get-Location) 'chinese-baby-naming'
$namingParent = Join-Path $env:USERPROFILE '.agents\skills'
$namingTarget = Join-Path $namingParent 'chinese-baby-naming'
if (Test-Path -LiteralPath $namingTarget) {
    throw "目标已存在，请先比较已有 Skill：$namingTarget"
}
New-Item -ItemType Directory -Path $namingParent -Force | Out-Null
Copy-Item -LiteralPath $namingSource -Destination $namingTarget -Recurse
```

命令从本仓库根目录运行。本次交付未修改个人技能目录或宿主配置。安装后用 `$chinese-baby-naming` 显式调用，也可自然语言触发；界面支持技能选择时可选「中文宝宝取名」。若尚未发现，检查宿主目录或重启 Codex。

```text
使用 $chinese-baby-naming，姓欧阳，想要自然开阔的双字名，给3个，不用轩。
使用 $chinese-baby-naming，评价“杜子腾”，直接说优点和问题。
使用 $chinese-baby-naming，比较沈知远、沈明远，重点看读写与成年后使用。
使用 $chinese-baby-naming，保留“清朗”的意象，换掉澄字，不要过于古风。
使用 $chinese-baby-naming，从《诗经》取3个名，核对原文及语境。
使用 $chinese-baby-naming，另加五格文化参考，说明笔画口径，不影响现代评分。
```

只给姓氏也能开始；不要求出生日期、性别、方言等整套资料。普通推荐直接在聊天中给出，只有请求文件才生成报告文件。

## 工具和边界

技能本身无需 Python、付费接口或额外安装包。可选脚本使用 Python 3.10+ 标准库，仅做候选去重、明确约束检查和评分算术，调用与 JSON 格式见 [tools.md](references/tools.md)。它不判断名字好听与否，也不自动查拼音、规范字、重名或八字。

古典出处需可识别原典/可靠数字化文本；字音字义、方言、官方用字和地区登记、重名人数、可靠历法计算分别需要相应资料或工具。工具缺失仍可做限定范围的取名，但结果标明待核，不编造已核实结论。八字、喜用神、生肖、五格三才均为用户明确选择的可选传统解释，不预测命运。

## 验收

```powershell
python -B -m unittest discover -s chinese-baby-naming/tests -p 'test_*.py' -v
python -B chinese-baby-naming/scripts/name_checks.py chinese-baby-naming/tests/sample-input.json
```

需要可用的 Python；若系统 `python` 是 Windows 商店占位程序，请使用真实 Python 可执行文件路径。无第三方运行依赖。

[行为场景](tests/scenarios.md) 用于复测语言判断与触发边界，[验收记录](tests/verification.md) 区分已执行测试和未接入的外部能力。自动脚本不证明古典出处、审美或真实地区登记已验证。
