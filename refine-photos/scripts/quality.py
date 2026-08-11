from __future__ import annotations

import math
from typing import Any

import cv2
import numpy as np

from engine import RenderedPhoto, linear_to_srgb


def audit_render(rendered: RenderedPhoto, recipe: dict[str, Any]) -> dict[str, Any]:
    """计算源图相对指标并返回机器可读质检结果。"""
    quality = recipe["quality"]
    source, edited, masks = _working_copy(rendered)
    source_luma = _luminance(source)
    edited_luma = _luminance(edited)

    highlight_before = float(np.mean(source_luma >= 0.995))
    highlight_after = float(np.mean(edited_luma >= 0.995))
    shadow_before = float(np.mean(source_luma <= 0.005))
    shadow_after = float(np.mean(edited_luma <= 0.005))
    saturation_before = _extreme_saturation_fraction(source)
    saturation_after = _extreme_saturation_fraction(edited)

    texture_ratio, texture_details = _texture_ratio(source_luma, edited_luma, masks)
    skin_hue_shift = _skin_hue_shift(source, edited, masks)
    halo_ratio, halo_details = _halo_ratio(source_luma, edited_luma, masks)

    metrics = {
        "highlight_clip_before": highlight_before,
        "highlight_clip_after": highlight_after,
        "highlight_clip_delta": highlight_after - highlight_before,
        "shadow_clip_before": shadow_before,
        "shadow_clip_after": shadow_after,
        "shadow_clip_delta": shadow_after - shadow_before,
        "extreme_saturation_before": saturation_before,
        "extreme_saturation_after": saturation_after,
        "extreme_saturation_delta": saturation_after - saturation_before,
        "minimum_protected_texture_ratio": texture_ratio,
        "protected_texture_details": texture_details,
        "maximum_skin_hue_shift_degrees": skin_hue_shift,
        "maximum_mask_halo_ratio": halo_ratio,
        "mask_halo_details": halo_details,
        "composition_retention": rendered.composition_retention,
    }

    hard_failures: list[dict[str, Any]] = []
    soft_failures: list[dict[str, Any]] = []
    if rendered.composition_retention < 0.9 - 1e-6:
        hard_failures.append(
            _failure(
                "composition-retention",
                rendered.composition_retention,
                0.9,
                "Combined composition retention is below the hard minimum.",
            )
        )

    _append_if_over(
        soft_failures,
        "highlight-clipping",
        highlight_after - highlight_before,
        quality["max_highlight_clip_delta"],
        "Highlight clipping increased beyond the source-relative limit.",
    )
    _append_if_over(
        soft_failures,
        "shadow-clipping",
        shadow_after - shadow_before,
        quality["max_shadow_clip_delta"],
        "Shadow clipping increased beyond the source-relative limit.",
    )
    _append_if_over(
        soft_failures,
        "extreme-saturation",
        saturation_after - saturation_before,
        quality["max_extreme_saturation_delta"],
        "Extreme saturation expanded beyond the source-relative limit.",
    )
    if texture_ratio is not None and texture_ratio < quality["min_texture_ratio"]:
        soft_failures.append(
            _failure(
                "protected-texture-loss",
                texture_ratio,
                quality["min_texture_ratio"],
                "A protected region lost too much high-frequency texture.",
            )
        )
    if skin_hue_shift is not None and skin_hue_shift > quality["max_skin_hue_shift_degrees"]:
        soft_failures.append(
            _failure(
                "skin-hue-shift",
                skin_hue_shift,
                quality["max_skin_hue_shift_degrees"],
                "Protected skin moved too far in hue.",
            )
        )
    if halo_ratio is not None and halo_ratio > quality["max_mask_halo_ratio"]:
        soft_failures.append(
            _failure(
                "mask-halo",
                halo_ratio,
                quality["max_mask_halo_ratio"],
                "A local-mask boundary gained excessive gradient energy.",
            )
        )

    return {
        "version": 1,
        "passed": not hard_failures and not soft_failures,
        "safety_adjusted": bool(recipe.get("safety_adjusted", False)),
        "hard_failures": hard_failures,
        "soft_failures": soft_failures,
        "metrics": metrics,
        "warnings": rendered.warnings
        + [
            "Metric checks do not replace visual review of identity, semantics, masks, and photographic realism."
        ],
    }


def _working_copy(
    rendered: RenderedPhoto, max_edge: int = 2048
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    """将质检副本限制在合理尺寸，避免大图审计占用过多内存。"""
    source = linear_to_srgb(rendered.source_linear)
    edited = linear_to_srgb(rendered.pre_composition_linear)
    height, width = source.shape[:2]
    if max(height, width) <= max_edge:
        masks = rendered.protected_masks + rendered.local_masks
        return source, edited, masks

    scale = max_edge / max(height, width)
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    source = cv2.resize(source, size, interpolation=cv2.INTER_AREA)
    edited = cv2.resize(edited, size, interpolation=cv2.INTER_AREA)
    masks = []
    for item in rendered.protected_masks + rendered.local_masks:
        resized = cv2.resize(item["mask"], size, interpolation=cv2.INTER_AREA)
        masks.append({**item, "mask": resized})
    return source, edited, masks


def _texture_ratio(
    source_luma: np.ndarray,
    edited_luma: np.ndarray,
    masks: list[dict[str, Any]],
) -> tuple[float | None, list[dict[str, Any]]]:
    protected = [item for item in masks if "role" in item]
    if not protected:
        return None, []
    source_detail = np.abs(cv2.Laplacian(source_luma, cv2.CV_32F, ksize=3))
    edited_detail = np.abs(cv2.Laplacian(edited_luma, cv2.CV_32F, ksize=3))
    details: list[dict[str, Any]] = []
    ratios: list[float] = []
    for item in protected:
        weight = np.clip(item["mask"], 0.0, 1.0)
        total = float(weight.sum())
        if total < 25.0:
            continue
        before = float(np.sum(source_detail * weight) / total)
        after = float(np.sum(edited_detail * weight) / total)
        if before < 1e-5:
            continue
        ratio = after / before
        ratios.append(ratio)
        details.append(
            {
                "name": item["name"],
                "role": item["role"],
                "before": before,
                "after": after,
                "ratio": ratio,
            }
        )
    return (min(ratios) if ratios else None), details


def _skin_hue_shift(
    source: np.ndarray,
    edited: np.ndarray,
    masks: list[dict[str, Any]],
) -> float | None:
    skin_masks = [item["mask"] for item in masks if item.get("role") == "skin"]
    if not skin_masks:
        return None
    mask = np.maximum.reduce(skin_masks)
    source_hls = cv2.cvtColor(source.astype(np.float32), cv2.COLOR_RGB2HLS)
    edited_hls = cv2.cvtColor(edited.astype(np.float32), cv2.COLOR_RGB2HLS)
    weight = mask * (source_hls[..., 2] > 0.08) * (source_hls[..., 1] > 0.03) * (
        source_hls[..., 1] < 0.98
    )
    if float(weight.sum()) < 25.0:
        return None
    before = _circular_hue_mean(source_hls[..., 0], weight)
    after = _circular_hue_mean(edited_hls[..., 0], weight)
    return abs((after - before + 180.0) % 360.0 - 180.0)


def _halo_ratio(
    source_luma: np.ndarray,
    edited_luma: np.ndarray,
    masks: list[dict[str, Any]],
) -> tuple[float | None, list[dict[str, Any]]]:
    local_masks = [item for item in masks if "role" not in item]
    if not local_masks:
        return None, []
    source_gradient = _gradient_magnitude(source_luma)
    edited_gradient = _gradient_magnitude(edited_luma)
    details: list[dict[str, Any]] = []
    ratios: list[float] = []
    kernel = np.ones((3, 3), dtype=np.uint8)
    for item in local_masks:
        mask = np.clip(item["mask"], 0.0, 1.0)
        boundary = (mask > 0.02) & (mask < 0.98)
        if int(boundary.sum()) < 25:
            binary = (mask >= 0.5).astype(np.uint8)
            boundary = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel).astype(bool)
        if int(boundary.sum()) < 25:
            continue
        before = float(np.mean(source_gradient[boundary]))
        after = float(np.mean(edited_gradient[boundary]))
        ratio = after / max(before, 0.002)
        ratios.append(ratio)
        details.append(
            {"name": item["name"], "before": before, "after": after, "ratio": ratio}
        )
    return (max(ratios) if ratios else None), details


def _extreme_saturation_fraction(rgb: np.ndarray) -> float:
    hls = cv2.cvtColor(rgb.astype(np.float32), cv2.COLOR_RGB2HLS)
    valid_light = (hls[..., 1] > 0.02) & (hls[..., 1] < 0.98)
    return float(np.mean((hls[..., 2] >= 0.98) & valid_light))


def _circular_hue_mean(hue: np.ndarray, weight: np.ndarray) -> float:
    radians = np.deg2rad(hue)
    sine = float(np.sum(np.sin(radians) * weight))
    cosine = float(np.sum(np.cos(radians) * weight))
    return math.degrees(math.atan2(sine, cosine)) % 360.0


def _gradient_magnitude(values: np.ndarray) -> np.ndarray:
    dx = cv2.Sobel(values, cv2.CV_32F, 1, 0, ksize=3)
    dy = cv2.Sobel(values, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(dx, dy)


def _luminance(rgb: np.ndarray) -> np.ndarray:
    return np.sum(rgb * np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32), axis=2)


def _append_if_over(
    failures: list[dict[str, Any]],
    code: str,
    value: float,
    limit: float,
    message: str,
) -> None:
    if value > limit:
        failures.append(_failure(code, value, limit, message))


def _failure(code: str, value: float, limit: float, message: str) -> dict[str, Any]:
    return {"code": code, "value": value, "limit": limit, "message": message}
