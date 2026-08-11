from __future__ import annotations

import copy
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "recipe.schema.json"


class RecipeError(ValueError):
    """表示 Recipe 结构或语义不符合安全约束。"""


def load_recipe(path: str | Path) -> dict[str, Any]:
    """读取、校验并补齐 Recipe 默认值。"""
    recipe_path = Path(path)
    try:
        data = json.loads(recipe_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RecipeError(f"Cannot read recipe {recipe_path}: {exc}") from exc
    return validate_recipe(data)


def validate_recipe(
    recipe: dict[str, Any], image_size: tuple[int, int] | None = None
) -> dict[str, Any]:
    """执行 JSON Schema 与跨字段语义校验。"""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(recipe), key=lambda error: list(error.path))
    if errors:
        details = []
        for error in errors[:20]:
            path = ".".join(str(part) for part in error.absolute_path) or "$"
            details.append(f"{path}: {error.message}")
        raise RecipeError("Recipe schema validation failed:\n- " + "\n- ".join(details))

    normalized = normalize_recipe(recipe)
    _validate_intent(normalized)
    _validate_masks(normalized)
    _validate_retouch_budget(normalized)
    _validate_repairs(normalized, image_size)
    _validate_composition(normalized, image_size)
    return normalized


def normalize_recipe(recipe: dict[str, Any]) -> dict[str, Any]:
    """在不放宽白名单的前提下补齐渲染默认值。"""
    result = copy.deepcopy(recipe)
    result.setdefault("safety_adjusted", False)
    result.setdefault("color_ranges", [])
    result.setdefault("color_balance", {})
    result.setdefault("local_adjustments", [])
    result.setdefault("protected_masks", [])
    result.setdefault("repairs", [])
    result.setdefault("creative_effects", [])

    global_defaults = {
        "exposure_ev": 0.0,
        "temperature": 0.0,
        "tint": 0.0,
        "contrast": 0.0,
        "highlights": 0.0,
        "shadows": 0.0,
        "whites": 0.0,
        "blacks": 0.0,
        "saturation": 0.0,
        "vibrance": 0.0,
    }
    result["global"] = {**global_defaults, **result.get("global", {})}

    result["detail"] = {
        "denoise": 0.0,
        "sharpen": 0.0,
        "grain": 0.0,
        "grain_seed": 0,
        **result.get("detail", {}),
    }
    result["composition"] = {
        "crop": [0.0, 0.0, 1.0, 1.0],
        "rotate_degrees": 0.0,
        **result.get("composition", {}),
    }
    result["quality"] = {
        "max_highlight_clip_delta": 0.005,
        "max_shadow_clip_delta": 0.005,
        "min_texture_ratio": 0.72,
        "max_skin_hue_shift_degrees": 10.0,
        "max_mask_halo_ratio": 2.5,
        "max_extreme_saturation_delta": 0.01,
        **result.get("quality", {}),
    }

    for item in result["color_ranges"]:
        item.setdefault("hue_shift", 0.0)
        item.setdefault("saturation", 0.0)
        item.setdefault("luminance", 0.0)
        item.setdefault("protect_skin", True)
    for section in result["color_balance"].values():
        if not isinstance(section, list):
            raise RecipeError("Color-balance offsets must be RGB arrays.")
    for item in result["local_adjustments"]:
        item["adjustments"] = _local_defaults(item["adjustments"])
        item["mask"] = _mask_defaults(item["mask"])
    for item in result["protected_masks"]:
        item["mask"] = _mask_defaults(item["mask"])
    for item in result["repairs"]:
        item.setdefault("feather", 0.4)
        item.setdefault("opacity", 1.0)
    for item in result["creative_effects"]:
        item["mask"] = _mask_defaults(item["mask"])
        item["adjustments"].setdefault("exposure_ev", 0.0)
        item["adjustments"].setdefault("temperature", 0.0)
        item["adjustments"].setdefault("tint", 0.0)
        item["adjustments"].setdefault("contrast", 0.0)
        item["adjustments"].setdefault("saturation", 0.0)
        item["adjustments"].setdefault("color_strength", 0.0)
    return result


def save_recipe(path: str | Path, recipe: dict[str, Any], overwrite: bool = False) -> None:
    """以同目录原子替换方式写入 Recipe。"""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Recipe already exists: {destination}")
    payload = json.dumps(recipe, ensure_ascii=False, indent=2) + "\n"
    fd, temporary = tempfile.mkstemp(
        prefix=f".{destination.stem}.", suffix=".tmp", dir=destination.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
        os.replace(temporary, destination)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def soften_recipe(recipe: dict[str, Any], factor: float = 0.62) -> dict[str, Any]:
    """对软失败 Recipe 做一次保守降级，不改变构图和硬约束。"""
    softened = copy.deepcopy(recipe)
    softened["safety_adjusted"] = True

    _scale_numbers(softened["global"], factor)
    for item in softened.get("color_ranges", []):
        for key in ("hue_shift", "saturation", "luminance"):
            item[key] *= factor
    for values in softened.get("color_balance", {}).values():
        for index, value in enumerate(values):
            values[index] = value * factor
    for item in softened.get("local_adjustments", []):
        _scale_numbers(item["adjustments"], factor)
        if "smoothing" in item["adjustments"]:
            item["adjustments"]["smoothing"] *= 0.8
    _scale_numbers(softened.get("detail", {}), factor, excluded={"grain_seed"})
    for item in softened.get("creative_effects", []):
        _scale_numbers(item["adjustments"], factor)
        if "color" in item["adjustments"]:
            item["adjustments"]["color"] = list(item["adjustments"]["color"])
    if "monochrome" in softened:
        softened["monochrome"]["toning_strength"] *= factor
    softened["analysis"]["planned_changes"].append(
        "Renderer reduced edit amplitudes once after a soft quality failure."
    )
    return validate_recipe(softened)


def composition_retention(
    recipe: dict[str, Any], image_size: tuple[int, int]
) -> float:
    """估算透视、裁剪与旋转安全裁边后的总保留面积。"""
    width, height = image_size
    composition = recipe.get("composition", {})
    left, top, right, bottom = composition.get("crop", [0.0, 0.0, 1.0, 1.0])
    crop_ratio = (right - left) * (bottom - top)
    perspective_ratio = 1.0
    if "perspective_quad" in composition:
        perspective_ratio = abs(_polygon_area(composition["perspective_quad"]))

    crop_width = max(1.0, width * (right - left))
    crop_height = max(1.0, height * (bottom - top))
    safe_width, safe_height = largest_rotated_rectangle(
        crop_width, crop_height, math.radians(abs(composition.get("rotate_degrees", 0.0)))
    )
    rotation_ratio = (safe_width * safe_height) / (crop_width * crop_height)
    return perspective_ratio * crop_ratio * rotation_ratio


def largest_rotated_rectangle(width: float, height: float, angle: float) -> tuple[float, float]:
    """计算旋转矩形内不含空白的最大轴对齐矩形。"""
    if width <= 0 or height <= 0:
        return 0.0, 0.0
    angle = abs(angle) % math.pi
    if angle > math.pi / 2:
        angle = math.pi - angle
    if angle < 1e-9:
        return width, height

    sin_a = abs(math.sin(angle))
    cos_a = abs(math.cos(angle))
    width_is_longer = width >= height
    side_long = width if width_is_longer else height
    side_short = height if width_is_longer else width

    if side_short <= 2.0 * sin_a * cos_a * side_long or abs(sin_a - cos_a) < 1e-9:
        x = 0.5 * side_short
        safe_width = x / sin_a
        safe_height = x / cos_a
    else:
        cos_2a = cos_a * cos_a - sin_a * sin_a
        safe_width = (width * cos_a - height * sin_a) / cos_2a
        safe_height = (height * cos_a - width * sin_a) / cos_2a
    return max(1.0, safe_width), max(1.0, safe_height)


def _validate_intent(recipe: dict[str, Any]) -> None:
    intent = recipe["intent"]
    contains_people = intent["contains_people"]
    scene = intent["scene"]
    if scene in {"portrait-led", "portrait-only", "balanced"} and not contains_people:
        raise RecipeError(f"Scene '{scene}' requires contains_people=true.")
    if scene == "landscape-only" and contains_people:
        raise RecipeError("Scene 'landscape-only' requires contains_people=false.")

    aesthetic = intent["aesthetic"]
    color = intent["color_tendency"]
    incompatible_bw = {
        "warm-healing",
        "forest-fresh",
        "cool-clean",
        "vermilion-gold",
        "qingdai-soft",
    }
    if aesthetic == "black-and-white" and color in incompatible_bw:
        raise RecipeError(f"Black-and-white is incompatible with color tendency '{color}'.")
    monochrome = recipe.get("monochrome")
    if aesthetic == "black-and-white" and not (monochrome and monochrome["enabled"]):
        raise RecipeError("Black-and-white requires monochrome.enabled=true.")
    if aesthetic != "black-and-white" and monochrome and monochrome["enabled"]:
        raise RecipeError("Monochrome conversion requires the black-and-white aesthetic.")
    if monochrome and sum(monochrome["channel_mix"]) <= 0:
        raise RecipeError("Monochrome channel_mix must contain positive weight.")

    creative = intent["creative_light"]
    effects = recipe.get("creative_effects", [])
    if effects and not (creative["enabled"] and creative["acknowledged"]):
        raise RecipeError(
            "Creative effects require creative_light.enabled=true and acknowledged=true."
        )
    if creative["enabled"] != bool(effects):
        raise RecipeError(
            "creative_light.enabled must be true exactly when creative_effects are present."
        )


def _validate_masks(recipe: dict[str, Any]) -> None:
    masks = [item["mask"] for item in recipe.get("local_adjustments", [])]
    masks += [item["mask"] for item in recipe.get("protected_masks", [])]
    masks += [item["mask"] for item in recipe.get("creative_effects", [])]
    for mask in masks:
        mask_type = mask["type"]
        if mask_type == "ellipse" and (mask["radius"][0] <= 0 or mask["radius"][1] <= 0):
            raise RecipeError("Ellipse radii must be positive.")
        if mask_type == "linear-gradient" and mask["start"] == mask["end"]:
            raise RecipeError("Linear-gradient start and end must differ.")
        if mask_type == "radial-gradient" and mask["outer_radius"] <= mask["inner_radius"]:
            raise RecipeError("Radial-gradient outer_radius must exceed inner_radius.")
        gate = mask.get("color_gate")
        if gate and (
            gate["saturation_min"] > gate["saturation_max"]
            or gate["luminance_min"] > gate["luminance_max"]
        ):
            raise RecipeError("Color-gate minimum values must not exceed maximum values.")


def _validate_retouch_budget(recipe: dict[str, Any]) -> None:
    level = recipe["intent"]["retouch_level"]
    smoothing_caps = {1: 0.12, 2: 0.25, 3: 0.35}
    for item in recipe.get("local_adjustments", []):
        smoothing = item["adjustments"].get("smoothing", 0.0)
        if smoothing > smoothing_caps[level]:
            raise RecipeError(
                f"Local adjustment '{item['name']}' smoothing {smoothing} exceeds "
                f"retouch level {level} cap {smoothing_caps[level]}."
            )


def _validate_repairs(
    recipe: dict[str, Any], image_size: tuple[int, int] | None
) -> None:
    """限制源像素修复的类型、范围和取样位置。"""
    repairs = recipe.get("repairs", [])
    if not repairs:
        return

    contains_people = recipe["intent"]["contains_people"]
    total_area_ratio = 0.0
    for item in repairs:
        kind = item["kind"]
        radius = float(item["radius"])
        if kind == "transient-blemish" and not contains_people:
            raise RecipeError("Transient-blemish repair requires contains_people=true.")
        if kind == "transient-blemish" and radius > 0.015 + 1e-9:
            raise RecipeError("Transient-blemish repair radius must not exceed 0.015.")
        if item["source"] == item["target"]:
            raise RecipeError(f"Repair '{item['name']}' source and target must differ.")

        if image_size:
            width, height = image_size
            short_edge = min(width, height)
            radius_pixels = radius * short_edge
            total_area_ratio += math.pi * radius_pixels**2 / (width * height)
            margin_x = radius_pixels / max(width - 1, 1)
            margin_y = radius_pixels / max(height - 1, 1)
            for label in ("source", "target"):
                x, y = item[label]
                if not (
                    margin_x <= x <= 1.0 - margin_x
                    and margin_y <= y <= 1.0 - margin_y
                ):
                    raise RecipeError(
                        f"Repair '{item['name']}' {label} patch extends outside the image."
                    )
            source_x, source_y = item["source"]
            target_x, target_y = item["target"]
            distance_pixels = math.hypot(
                (source_x - target_x) * max(width - 1, 1),
                (source_y - target_y) * max(height - 1, 1),
            )
            if distance_pixels < radius_pixels * 1.5:
                raise RecipeError(
                    f"Repair '{item['name']}' source is too close to the target."
                )
        else:
            total_area_ratio += math.pi * radius**2

    if total_area_ratio > 0.01 + 1e-9:
        raise RecipeError(
            f"Cumulative repair area {total_area_ratio:.4f} exceeds the 0.01 limit."
        )


def _validate_composition(
    recipe: dict[str, Any], image_size: tuple[int, int] | None
) -> None:
    intent = recipe["intent"]
    composition = recipe.get("composition", {})
    left, top, right, bottom = composition.get("crop", [0.0, 0.0, 1.0, 1.0])
    if not (left < right and top < bottom):
        raise RecipeError("Crop must satisfy left < right and top < bottom.")

    quad = composition.get("perspective_quad")
    if quad:
        if intent["contains_people"]:
            raise RecipeError("Perspective correction is forbidden when people are present.")
        corners = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        for point, corner in zip(quad, corners, strict=True):
            displacement = math.dist(point, corner)
            if displacement > 0.05 + 1e-9:
                raise RecipeError(
                    f"Perspective corner displacement {displacement:.4f} exceeds 0.05."
                )
        if abs(_polygon_area(quad)) < 0.9:
            raise RecipeError("Perspective quad must retain at least 90% source area.")

    resize = composition.get("resize")
    if resize and resize["allow_upscale"] and not resize["acknowledged"]:
        raise RecipeError("Traditional upscaling requires acknowledged=true.")
    if image_size:
        retention = composition_retention(recipe, image_size)
        if retention < 0.9 - 1e-6:
            raise RecipeError(
                f"Combined composition retention {retention:.4f} is below 0.90."
            )
        if resize:
            source_long_edge = max(image_size)
            if resize["long_edge"] > source_long_edge and not (
                resize["allow_upscale"] and resize["acknowledged"]
            ):
                raise RecipeError("Upscaling requires allow_upscale=true and acknowledged=true.")


def _local_defaults(adjustments: dict[str, Any]) -> dict[str, Any]:
    defaults = {
        "exposure_ev": 0.0,
        "temperature": 0.0,
        "tint": 0.0,
        "contrast": 0.0,
        "highlights": 0.0,
        "shadows": 0.0,
        "saturation": 0.0,
        "vibrance": 0.0,
        "hue_shift": 0.0,
        "luminance": 0.0,
        "smoothing": 0.0,
        "clarity": 0.0,
        "sharpen": 0.0,
        "denoise": 0.0,
    }
    return {**defaults, **adjustments}


def _mask_defaults(mask: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(mask)
    result.setdefault("feather", 0.03)
    result.setdefault("invert", False)
    if "color_gate" in result:
        gate = result["color_gate"]
        gate.setdefault("saturation_min", 0.0)
        gate.setdefault("saturation_max", 1.0)
        gate.setdefault("luminance_min", 0.0)
        gate.setdefault("luminance_max", 1.0)
    return result


def _scale_numbers(
    mapping: dict[str, Any], factor: float, excluded: set[str] | None = None
) -> None:
    excluded = excluded or set()
    for key, value in mapping.items():
        if key in excluded or isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            mapping[key] = value * factor


def _polygon_area(points: list[list[float]]) -> float:
    return 0.5 * sum(
        x1 * y2 - x2 * y1
        for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1], strict=True)
    )


def template_recipe() -> dict[str, Any]:
    """返回可直接修改的安全默认 Recipe。"""
    return normalize_recipe(
        {
            "version": 1,
            "analysis": {
                "subject_hierarchy": "Describe the primary and secondary subjects.",
                "observations": [],
                "planned_changes": [],
                "limitations": [],
            },
            "intent": {
                "interaction": "plan",
                "scene": "landscape-only",
                "contains_people": False,
                "aesthetic": "natural",
                "color_tendency": "source-derived",
                "light_tendency": "source-derived",
                "style_level": 2,
                "retouch_level": 2,
                "reference_used": False,
                "creative_light": {"enabled": False, "acknowledged": False},
            },
            "global": {},
        }
    )
