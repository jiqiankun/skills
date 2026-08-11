from __future__ import annotations

import argparse
import importlib.metadata
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = SKILL_ROOT / "scripts" / "requirements.txt"
DEPENDENCIES = {
    "numpy": "numpy",
    "PIL": "Pillow",
    "cv2": "opencv-python-headless",
    "tifffile": "tifffile",
    "jsonschema": "jsonschema",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and render deterministic refine-photos recipes."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check", help="Check required Python dependencies.")

    validate_parser = subparsers.add_parser("validate", help="Validate a recipe.")
    validate_parser.add_argument("recipe", type=Path)

    template_parser = subparsers.add_parser("template", help="Write a safe recipe template.")
    template_parser.add_argument("output", type=Path)
    template_parser.add_argument("--overwrite", action="store_true")

    render_parser = subparsers.add_parser("render", help="Render and audit one image.")
    render_parser.add_argument("source", type=Path)
    render_parser.add_argument("recipe", type=Path)
    render_parser.add_argument("output", type=Path)
    render_parser.add_argument(
        "--preview-max",
        type=int,
        default=None,
        help="Downsize the accepted render to this maximum edge and encode a review copy.",
    )
    render_parser.add_argument(
        "--auto-safe",
        action="store_true",
        help="Allow one conservative rerender after soft quality failures.",
    )
    render_parser.add_argument("--audit", type=Path, default=None)
    render_parser.add_argument("--applied-recipe", type=Path, default=None)
    render_parser.add_argument("--overwrite", action="store_true")
    return parser


def command_check() -> int:
    """报告运行依赖，不自动安装任何软件包。"""
    rows = []
    missing = []
    for module, distribution in DEPENDENCIES.items():
        available = importlib.util.find_spec(module) is not None
        version = None
        if available:
            try:
                version = importlib.metadata.version(distribution)
            except importlib.metadata.PackageNotFoundError:
                version = "available"
        else:
            missing.append(distribution)
        rows.append(
            {
                "module": module,
                "distribution": distribution,
                "available": available,
                "version": version,
            }
        )
    report = {
        "python": sys.version.split()[0],
        "supported_python": sys.version_info[:2] in {(3, 11), (3, 12)},
        "dependencies": rows,
        "requirements": str(REQUIREMENTS_PATH),
        "passed": not missing and sys.version_info[:2] in {(3, 11), (3, 12)},
    }
    if missing:
        report["install_hint"] = f'python -m pip install -r "{REQUIREMENTS_PATH}"'
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


def command_validate(path: Path) -> int:
    """校验 Recipe 并输出规范化结果摘要。"""
    from recipe import load_recipe

    recipe = load_recipe(path)
    summary = {
        "valid": True,
        "version": recipe["version"],
        "scene": recipe["intent"]["scene"],
        "aesthetic": recipe["intent"]["aesthetic"],
        "style_level": recipe["intent"]["style_level"],
        "retouch_level": recipe["intent"]["retouch_level"],
        "local_adjustments": len(recipe.get("local_adjustments", [])),
        "repairs": len(recipe.get("repairs", [])),
        "creative_effects": len(recipe.get("creative_effects", [])),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def command_template(output: Path, overwrite: bool) -> int:
    """写入安全模板，供 Agent 根据原片填充。"""
    from recipe import save_recipe, template_recipe

    save_recipe(output, template_recipe(), overwrite=overwrite)
    print(json.dumps({"template": str(output.resolve())}, ensure_ascii=False, indent=2))
    return 0


def command_render(args: argparse.Namespace) -> int:
    """渲染、审计并仅在通过后发布输出。"""
    from engine import load_photo, render_photo, save_photo
    from quality import audit_render
    from recipe import load_recipe, save_recipe, soften_recipe, validate_recipe

    source = args.source.resolve()
    output = args.output.resolve()
    if source == output:
        raise ValueError("Input and output paths must differ; the source is never overwritten.")
    if args.preview_max is not None and args.preview_max < 256:
        raise ValueError("--preview-max must be at least 256 pixels.")

    applied_path = (
        args.applied_recipe.resolve()
        if args.applied_recipe
        else output.with_name(f"{output.stem}.recipe.json")
    )
    audit_path = (
        args.audit.resolve()
        if args.audit
        else output.with_name(f"{output.stem}.audit.json")
    )
    _guard_outputs([output, applied_path, audit_path], args.overwrite)

    photo = load_photo(source)
    recipe = load_recipe(args.recipe)
    recipe = validate_recipe(recipe, (photo.linear.shape[1], photo.linear.shape[0]))
    rendered = render_photo(photo, recipe)
    audit = audit_render(rendered, recipe)

    if audit["hard_failures"]:
        _write_json(audit_path, audit, overwrite=args.overwrite)
        raise ValueError("Render failed a hard quality gate; see the audit sidecar.")
    if audit["soft_failures"] and args.auto_safe:
        recipe = soften_recipe(recipe)
        recipe = validate_recipe(recipe, (photo.linear.shape[1], photo.linear.shape[0]))
        rendered = render_photo(photo, recipe)
        audit = audit_render(rendered, recipe)
    if not audit["passed"]:
        _write_json(audit_path, audit, overwrite=args.overwrite)
        raise ValueError("Render failed quality gates; no edited image was published.")

    output.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(
        prefix=f".{output.stem}.", suffix=output.suffix, dir=output.parent, delete=False
    )
    temporary_output = Path(handle.name)
    handle.close()
    try:
        save_photo(photo, rendered, temporary_output, preview_max=args.preview_max)
        save_recipe(applied_path, recipe, overwrite=args.overwrite)
        _write_json(audit_path, audit, overwrite=args.overwrite)
        os.replace(temporary_output, output)
    except Exception:
        temporary_output.unlink(missing_ok=True)
        raise

    report = {
        "passed": True,
        "output": str(output),
        "applied_recipe": str(applied_path),
        "audit": str(audit_path),
        "safety_adjusted": recipe.get("safety_adjusted", False),
        "warnings": audit["warnings"],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def _guard_outputs(paths: list[Path], overwrite: bool) -> None:
    """拒绝路径碰撞与非授权覆盖。"""
    resolved = [path.resolve() for path in paths]
    if len(set(resolved)) != len(resolved):
        raise ValueError("Output image, recipe sidecar, and audit sidecar must use distinct paths.")
    if overwrite:
        return
    existing = [str(path) for path in resolved if path.exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite existing output(s): " + ", ".join(existing))


def _write_json(path: Path, payload: dict[str, Any], overwrite: bool) -> None:
    """以同目录临时文件原子写入 JSON。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            return command_check()
        if args.command == "validate":
            return command_validate(args.recipe)
        if args.command == "template":
            return command_template(args.output, args.overwrite)
        if args.command == "render":
            return command_render(args)
        parser.error(f"Unknown command: {args.command}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
