# Codex Skills

个人 Codex Skills 集合。当前版本新增 `refine-photos`（摄影精修），用于以确定性、非生成式方式处理人像、风光及人景结合照片。

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

## 版本

当前版本：`v1.0.0`（2026-08-11）。详细内容见 [版本变更记录](CHANGELOG.md)。

## 项目结构

```text
refine-photos/
├── SKILL.md
├── agents/openai.yaml
├── references/
├── schemas/recipe.schema.json
├── scripts/
└── tests/
```
