from __future__ import annotations

import io
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import tifffile
from PIL import Image, ImageCms, ImageOps

from recipe import composition_retention, largest_rotated_rectangle


SUPPORTED_INPUTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
SUPPORTED_OUTPUTS = SUPPORTED_INPUTS
SRGB_PROFILE = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
SRGB_PROFILE_BYTES = SRGB_PROFILE.tobytes()


@dataclass
class LoadedPhoto:
    """保存已转换到线性 sRGB 工作空间的照片及元数据。"""

    source_path: Path
    linear: np.ndarray
    alpha: np.ndarray | None
    bit_depth: int
    source_format: str
    icc_profile: bytes | None
    profile_name: str
    assumed_srgb: bool
    profile_converted: bool
    exif_bytes: bytes | None
    exif_values: dict[int, Any]
    warnings: list[str] = field(default_factory=list)


@dataclass
class RenderedPhoto:
    """保存质检所需的渲染前后数据。"""

    source_linear: np.ndarray
    source_srgb: np.ndarray
    pre_composition_linear: np.ndarray
    final_linear: np.ndarray
    final_alpha: np.ndarray | None
    composition_retention: float
    protected_masks: list[dict[str, Any]]
    local_masks: list[dict[str, Any]]
    warnings: list[str]


def load_photo(path: str | Path) -> LoadedPhoto:
    """读取 JPEG、PNG 或 TIFF，并建立受控工作空间。"""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED_INPUTS:
        raise ValueError(f"Unsupported input format: {suffix}")
    if not source.is_file():
        raise FileNotFoundError(source)

    with Image.open(source) as metadata_image:
        source_format = metadata_image.format or suffix.lstrip(".").upper()
        icc_profile = metadata_image.info.get("icc_profile")
        exif = metadata_image.getexif()
        exif_values = dict(exif.items())
        try:
            exif_bytes = exif.tobytes() if exif_values else None
        except Exception:
            exif_bytes = None
        orientation = int(exif_values.get(274, 1))

    if suffix in {".tif", ".tiff"}:
        array = tifffile.imread(source)
        array = _normalize_tiff_shape(array)
        if array.dtype not in (np.uint8, np.uint16):
            raise ValueError(
                f"Unsupported TIFF dtype {array.dtype}; use unsigned 8-bit or 16-bit TIFF."
            )
        bit_depth = 16 if array.dtype == np.uint16 else 8
        array = _apply_orientation(array, orientation)
        maximum = float(np.iinfo(array.dtype).max)
        gamma_rgb = array[..., :3].astype(np.float32) / maximum
        alpha = array[..., 3].astype(np.float32) / maximum if array.shape[-1] == 4 else None
        profile_name = _profile_name(icc_profile)
        assumed_srgb = icc_profile is None
        if bit_depth == 16 and icc_profile and not _is_srgb_profile(profile_name):
            raise ValueError(
                "A 16-bit TIFF with a non-sRGB ICC profile requires an external color-managed "
                "developer; refusing silent profile degradation."
            )
        profile_converted = False
        if bit_depth == 8 and icc_profile and not _is_srgb_profile(profile_name):
            try:
                source_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_profile))
                rgb_image = Image.fromarray(array[..., :3], mode="RGB")
                rgb_image = ImageCms.profileToProfile(
                    rgb_image,
                    source_profile,
                    SRGB_PROFILE,
                    outputMode="RGB",
                    renderingIntent=0,
                )
                gamma_rgb = np.asarray(rgb_image, dtype=np.float32) / 255.0
                profile_converted = True
            except Exception as exc:
                raise ValueError(f"Cannot transform source ICC profile '{profile_name}': {exc}") from exc
        warnings = ["No ICC profile was present; the renderer assumed sRGB."] if assumed_srgb else []
    else:
        with Image.open(source) as raw_image:
            transposed = ImageOps.exif_transpose(raw_image)
            alpha_image = transposed.getchannel("A") if "A" in transposed.getbands() else None
            rgb_image = transposed.convert("RGB")
            profile_name = _profile_name(icc_profile)
            assumed_srgb = icc_profile is None
            profile_converted = False
            warnings = ["No ICC profile was present; the renderer assumed sRGB."] if assumed_srgb else []
            if icc_profile and not _is_srgb_profile(profile_name):
                try:
                    source_profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_profile))
                    rgb_image = ImageCms.profileToProfile(
                        rgb_image,
                        source_profile,
                        SRGB_PROFILE,
                        outputMode="RGB",
                        renderingIntent=0,
                    )
                    profile_converted = True
                except Exception as exc:
                    raise ValueError(f"Cannot transform source ICC profile '{profile_name}': {exc}") from exc
            gamma_rgb = np.asarray(rgb_image, dtype=np.float32) / 255.0
            alpha = (
                np.asarray(alpha_image, dtype=np.float32) / 255.0
                if alpha_image is not None
                else None
            )
        bit_depth = 8

    return LoadedPhoto(
        source_path=source,
        linear=srgb_to_linear(gamma_rgb),
        alpha=alpha,
        bit_depth=bit_depth,
        source_format=source_format,
        icc_profile=icc_profile,
        profile_name=profile_name,
        assumed_srgb=assumed_srgb,
        profile_converted=profile_converted,
        exif_bytes=exif_bytes,
        exif_values=exif_values,
        warnings=warnings,
    )


def render_photo(photo: LoadedPhoto, recipe: dict[str, Any]) -> RenderedPhoto:
    """按固定顺序执行白名单像素操作。"""
    source = np.asarray(photo.linear, dtype=np.float32)
    source_srgb = linear_to_srgb(source)
    current, repair_mask = apply_repairs(source, recipe.get("repairs", []))
    current = apply_adjustments(current, recipe["global"])

    protected_masks = [
        {
            "name": item["name"],
            "role": item["role"],
            "mask": build_mask(item["mask"], source_srgb),
        }
        for item in recipe.get("protected_masks", [])
    ]
    skin_protection = _combined_role_mask(protected_masks, "skin", source.shape[:2])

    current = apply_color_ranges(
        current, recipe.get("color_ranges", []), skin_protection
    )
    current = apply_color_balance(current, recipe.get("color_balance", {}))
    if recipe.get("monochrome", {}).get("enabled"):
        current = apply_monochrome(current, recipe["monochrome"])

    local_masks: list[dict[str, Any]] = []
    if repair_mask is not None:
        local_masks.append({"name": "source-pixel-repairs", "mask": repair_mask})
    for item in recipe.get("local_adjustments", []):
        mask = build_mask(item["mask"], source_srgb)
        local_masks.append({"name": item["name"], "mask": mask})
        adjusted = apply_adjustments(current, item["adjustments"])
        adjusted = apply_detail(adjusted, item["adjustments"])
        current = _blend(current, adjusted, mask)

    current = apply_detail(current, recipe.get("detail", {}))
    current = apply_grain(current, recipe.get("detail", {}))

    for item in recipe.get("creative_effects", []):
        mask = build_mask(item["mask"], source_srgb)
        adjusted = apply_adjustments(current, item["adjustments"])
        color = item["adjustments"].get("color")
        color_strength = item["adjustments"].get("color_strength", 0.0)
        if color is not None and color_strength > 0:
            adjusted_srgb = linear_to_srgb(adjusted)
            color_array = np.asarray(color, dtype=np.float32).reshape(1, 1, 3)
            adjusted_srgb = (
                adjusted_srgb * (1.0 - color_strength) + color_array * color_strength
            )
            adjusted = srgb_to_linear(np.clip(adjusted_srgb, 0.0, 1.0))
        current = _blend(current, adjusted, mask)

    pre_composition = np.clip(current, 0.0, 1.0)
    final, final_alpha = apply_composition(
        pre_composition, photo.alpha, recipe.get("composition", {})
    )
    retention = composition_retention(
        recipe, (photo.linear.shape[1], photo.linear.shape[0])
    )
    warnings = list(photo.warnings)
    if recipe.get("repairs"):
        warnings.append(
            "Source-pixel repairs were applied; visually verify every target and identity-bearing detail."
        )
    return RenderedPhoto(
        source_linear=source,
        source_srgb=source_srgb,
        pre_composition_linear=pre_composition,
        final_linear=final,
        final_alpha=final_alpha,
        composition_retention=retention,
        protected_masks=protected_masks,
        local_masks=local_masks,
        warnings=warnings,
    )


def save_photo(
    photo: LoadedPhoto,
    rendered: RenderedPhoto,
    path: str | Path,
    preview_max: int | None = None,
) -> None:
    """按目标格式保存通过质检的成片。"""
    destination = Path(path)
    suffix = destination.suffix.lower()
    if suffix not in SUPPORTED_OUTPUTS:
        raise ValueError(f"Unsupported output format: {suffix}")

    gamma = linear_to_srgb(rendered.final_linear)
    alpha = rendered.final_alpha
    if preview_max:
        gamma, alpha = _resize_preview(gamma, alpha, preview_max)

    if suffix in {".tif", ".tiff"} and not preview_max:
        _save_tiff(photo, gamma, alpha, destination)
        return

    rgb8 = np.rint(np.clip(gamma, 0.0, 1.0) * 255.0).astype(np.uint8)
    image = Image.fromarray(rgb8, mode="RGB")
    output_icc = SRGB_PROFILE_BYTES
    if not preview_max and photo.icc_profile and photo.profile_converted:
        try:
            target_profile = ImageCms.ImageCmsProfile(io.BytesIO(photo.icc_profile))
            image = ImageCms.profileToProfile(
                image,
                SRGB_PROFILE,
                target_profile,
                outputMode="RGB",
                renderingIntent=0,
            )
            output_icc = photo.icc_profile
        except Exception as exc:
            raise ValueError(f"Cannot restore source ICC profile '{photo.profile_name}': {exc}") from exc
    elif not preview_max and photo.icc_profile:
        output_icc = photo.icc_profile

    exif_bytes = _safe_exif_bytes(photo.exif_bytes, image.size)
    save_args: dict[str, Any] = {"icc_profile": output_icc}
    if exif_bytes:
        save_args["exif"] = exif_bytes

    if suffix in {".jpg", ".jpeg"}:
        if alpha is not None and np.any(alpha < 0.999):
            raise ValueError("JPEG output cannot preserve source transparency; use PNG or TIFF.")
        image.save(destination, format="JPEG", quality=95, subsampling=0, optimize=True, **save_args)
    elif suffix == ".png":
        if alpha is not None:
            alpha8 = np.rint(np.clip(alpha, 0.0, 1.0) * 255.0).astype(np.uint8)
            image.putalpha(Image.fromarray(alpha8, mode="L"))
        image.save(destination, format="PNG", compress_level=6, **save_args)
    else:
        image.save(destination, **save_args)


def apply_repairs(
    rgb: np.ndarray, repairs: list[dict[str, Any]]
) -> tuple[np.ndarray, np.ndarray | None]:
    """从原图明确取样并羽化覆盖小型技术瑕疵，不推断或生成内容。"""
    if not repairs:
        return np.asarray(rgb, dtype=np.float32), None

    base = np.asarray(rgb, dtype=np.float32)
    result = base.copy()
    height, width = result.shape[:2]
    short_edge = min(width, height)
    combined_mask = np.zeros((height, width), dtype=np.float32)

    for item in repairs:
        radius = max(1, int(round(float(item["radius"]) * short_edge)))
        size = radius * 2 + 1
        target_x = int(round(float(item["target"][0]) * (width - 1)))
        target_y = int(round(float(item["target"][1]) * (height - 1)))
        source_center = (
            float(item["source"][0]) * (width - 1),
            float(item["source"][1]) * (height - 1),
        )
        x0, x1 = target_x - radius, target_x + radius + 1
        y0, y1 = target_y - radius, target_y + radius + 1
        if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
            raise ValueError(f"Repair '{item['name']}' target patch extends outside the image.")
        if not (
            radius <= source_center[0] <= width - 1 - radius
            and radius <= source_center[1] <= height - 1 - radius
        ):
            raise ValueError(f"Repair '{item['name']}' source patch extends outside the image.")

        source_patch = cv2.getRectSubPix(base, (size, size), source_center)
        yy, xx = np.mgrid[-radius : radius + 1, -radius : radius + 1]
        distance = np.sqrt(xx.astype(np.float32) ** 2 + yy.astype(np.float32) ** 2)
        normalized = distance / max(radius, 1)
        feather = float(item.get("feather", 0.4))
        if feather <= 0:
            mask = (normalized <= 1.0).astype(np.float32)
        else:
            mask = 1.0 - _smoothstep(max(0.0, 1.0 - feather), 1.0, normalized)
            mask = mask.astype(np.float32)
        mask *= float(item.get("opacity", 1.0))

        target_patch = result[y0:y1, x0:x1]
        result[y0:y1, x0:x1] = (
            target_patch * (1.0 - mask[..., None]) + source_patch * mask[..., None]
        )
        combined_mask[y0:y1, x0:x1] = np.maximum(
            combined_mask[y0:y1, x0:x1], mask
        )

    return np.clip(result, 0.0, 1.0), combined_mask


def apply_adjustments(rgb: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    """应用曝光、白平衡、明暗结构与基础色彩调整。"""
    result = np.asarray(rgb, dtype=np.float32).copy()
    exposure = float(parameters.get("exposure_ev", 0.0))
    if exposure:
        result *= np.float32(2.0**exposure)

    temperature = float(parameters.get("temperature", 0.0))
    tint = float(parameters.get("tint", 0.0))
    if temperature or tint:
        gains = np.asarray(
            [
                1.0 + 0.22 * temperature + 0.08 * tint,
                1.0 - 0.16 * tint,
                1.0 - 0.22 * temperature + 0.08 * tint,
            ],
            dtype=np.float32,
        )
        gains = np.clip(gains, 0.75, 1.25)
        neutral = float(np.dot(gains, np.asarray([0.2126, 0.7152, 0.0722])))
        result *= gains.reshape(1, 1, 3) / max(neutral, 1e-6)

    result = _apply_tone(result, parameters)
    result = _apply_saturation(
        result,
        float(parameters.get("saturation", 0.0)),
        float(parameters.get("vibrance", 0.0)),
    )
    hue_shift = float(parameters.get("hue_shift", 0.0))
    luminance_shift = float(parameters.get("luminance", 0.0))
    if hue_shift or luminance_shift:
        srgb = linear_to_srgb(result)
        hls = cv2.cvtColor(srgb.astype(np.float32), cv2.COLOR_RGB2HLS)
        hls[..., 0] = np.mod(hls[..., 0] + hue_shift, 360.0)
        hls[..., 1] = np.clip(hls[..., 1] + luminance_shift * 0.35, 0.0, 1.0)
        result = srgb_to_linear(cv2.cvtColor(hls, cv2.COLOR_HLS2RGB))
    return np.clip(result, 0.0, 1.0)


def apply_color_ranges(
    rgb: np.ndarray,
    ranges: list[dict[str, Any]],
    skin_protection: np.ndarray,
) -> np.ndarray:
    """在 HLS 空间执行有边界的色相范围调整。"""
    if not ranges:
        return rgb
    srgb = linear_to_srgb(rgb)
    hls = cv2.cvtColor(srgb.astype(np.float32), cv2.COLOR_RGB2HLS)
    hue = hls[..., 0]
    for item in ranges:
        distance = np.abs((hue - float(item["hue_center"]) + 180.0) % 360.0 - 180.0)
        half_width = float(item["hue_width"])
        weight = 1.0 - _smoothstep(half_width * 0.65, half_width, distance)
        if item.get("protect_skin", True):
            weight *= 1.0 - skin_protection
        hls[..., 0] = np.mod(hls[..., 0] + item["hue_shift"] * weight, 360.0)
        hls[..., 2] = np.clip(hls[..., 2] + item["saturation"] * weight, 0.0, 1.0)
        hls[..., 1] = np.clip(hls[..., 1] + item["luminance"] * 0.35 * weight, 0.0, 1.0)
        hue = hls[..., 0]
    return srgb_to_linear(np.clip(cv2.cvtColor(hls, cv2.COLOR_HLS2RGB), 0.0, 1.0))


def apply_color_balance(rgb: np.ndarray, balance: dict[str, Any]) -> np.ndarray:
    """按阴影、中间调和高光权重施加轻量通道偏移。"""
    if not balance:
        return rgb
    result = np.asarray(rgb, dtype=np.float32).copy()
    lightness = _luminance(result)
    weights = {
        "shadows": (1.0 - lightness) ** 2,
        "midtones": np.clip(4.0 * lightness * (1.0 - lightness), 0.0, 1.0),
        "highlights": lightness**2,
    }
    for region, weight in weights.items():
        offset = balance.get(region)
        if offset is None:
            continue
        result += weight[..., None] * np.asarray(offset, dtype=np.float32).reshape(1, 1, 3)
    return np.clip(result, 0.0, 1.0)


def apply_monochrome(rgb: np.ndarray, settings: dict[str, Any]) -> np.ndarray:
    """以可控通道混合生成摄影黑白并允许轻微调色。"""
    srgb = linear_to_srgb(rgb)
    mix = np.asarray(settings["channel_mix"], dtype=np.float32)
    mix /= max(float(mix.sum()), 1e-6)
    gray = np.clip(np.sum(srgb * mix.reshape(1, 1, 3), axis=2), 0.0, 1.0)
    monochrome = np.repeat(gray[..., None], 3, axis=2)
    strength = float(settings.get("toning_strength", 0.0))
    if strength:
        tone = np.asarray(settings["toning_color"], dtype=np.float32).reshape(1, 1, 3)
        monochrome = monochrome * (1.0 - strength) + tone * gray[..., None] * strength
    return srgb_to_linear(np.clip(monochrome, 0.0, 1.0))


def apply_detail(rgb: np.ndarray, settings: dict[str, Any]) -> np.ndarray:
    """执行传统降噪、频率保持平滑、清晰度和锐化。"""
    result = np.asarray(rgb, dtype=np.float32).copy()
    denoise = float(settings.get("denoise", 0.0))
    if denoise > 0:
        filtered = cv2.bilateralFilter(
            np.ascontiguousarray(result),
            d=0,
            sigmaColor=0.025 + 0.16 * denoise,
            sigmaSpace=1.5 + 14.0 * denoise,
        )
        result = result * (1.0 - min(1.0, denoise * 1.8)) + filtered * min(
            1.0, denoise * 1.8
        )

    smoothing = float(settings.get("smoothing", 0.0))
    if smoothing > 0:
        sigma = max(0.6, min(result.shape[:2]) * 0.0025)
        low = cv2.GaussianBlur(result, (0, 0), sigmaX=sigma, sigmaY=sigma)
        lower = cv2.GaussianBlur(low, (0, 0), sigmaX=sigma * 1.8, sigmaY=sigma * 1.8)
        frequency_preserved = lower + (result - low)
        result = result * (1.0 - smoothing) + frequency_preserved * smoothing

    clarity = float(settings.get("clarity", 0.0))
    if clarity:
        sigma = max(1.0, min(result.shape[:2]) * 0.006)
        broad = cv2.GaussianBlur(result, (0, 0), sigmaX=sigma, sigmaY=sigma)
        result += clarity * 0.6 * (result - broad)

    sharpen = float(settings.get("sharpen", 0.0))
    if sharpen > 0:
        fine = cv2.GaussianBlur(result, (0, 0), sigmaX=0.8, sigmaY=0.8)
        result += sharpen * 0.75 * (result - fine)
    return np.clip(result, 0.0, 1.0)


def apply_grain(rgb: np.ndarray, settings: dict[str, Any]) -> np.ndarray:
    """加入确定性亮度颗粒，不加入灰尘、划痕或漏光。"""
    strength = float(settings.get("grain", 0.0))
    if strength <= 0:
        return rgb
    rng = np.random.default_rng(int(settings.get("grain_seed", 0)))
    noise = rng.normal(0.0, 0.022 * strength, size=rgb.shape[:2]).astype(np.float32)
    srgb = linear_to_srgb(rgb)
    srgb = np.clip(srgb + noise[..., None], 0.0, 1.0)
    return srgb_to_linear(srgb)


def build_mask(description: dict[str, Any], source_srgb: np.ndarray) -> np.ndarray:
    """从归一化几何描述与可选颜色门控生成羽化蒙版。"""
    height, width = source_srgb.shape[:2]
    mask_type = description["type"]
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    xn = xx / max(width - 1, 1)
    yn = yy / max(height - 1, 1)

    if mask_type == "full":
        mask = np.ones((height, width), dtype=np.float32)
    elif mask_type == "ellipse":
        cx, cy = description["center"]
        rx, ry = description["radius"]
        distance = np.sqrt(((xn - cx) / rx) ** 2 + ((yn - cy) / ry) ** 2)
        mask = (distance <= 1.0).astype(np.float32)
        mask = _feather_binary(mask, description.get("feather", 0.03), width, height)
    elif mask_type == "polygon":
        mask = np.zeros((height, width), dtype=np.float32)
        points = np.asarray(
            [[round(x * (width - 1)), round(y * (height - 1))] for x, y in description["points"]],
            dtype=np.int32,
        )
        cv2.fillPoly(mask, [points], 1.0)
        mask = _feather_binary(mask, description.get("feather", 0.03), width, height)
    elif mask_type == "linear-gradient":
        start = np.asarray(description["start"], dtype=np.float32)
        end = np.asarray(description["end"], dtype=np.float32)
        vector = end - start
        length_squared = max(float(np.dot(vector, vector)), 1e-8)
        projection = ((xn - start[0]) * vector[0] + (yn - start[1]) * vector[1]) / length_squared
        mask = _smoothstep(0.0, 1.0, projection).astype(np.float32)
    elif mask_type == "radial-gradient":
        cx, cy = description["center"]
        distance = np.sqrt((xn - cx) ** 2 + (yn - cy) ** 2)
        inner = float(description["inner_radius"])
        outer = float(description["outer_radius"])
        mask = (1.0 - _smoothstep(inner, outer, distance)).astype(np.float32)
    else:
        raise ValueError(f"Unsupported mask type: {mask_type}")

    gate = description.get("color_gate")
    if gate:
        hls = cv2.cvtColor(source_srgb.astype(np.float32), cv2.COLOR_RGB2HLS)
        distance = np.abs((hls[..., 0] - gate["hue_center"] + 180.0) % 360.0 - 180.0)
        hue_weight = 1.0 - _smoothstep(
            gate["hue_width"] * 0.65, gate["hue_width"], distance
        )
        saturation_weight = _range_weight(
            hls[..., 2], gate["saturation_min"], gate["saturation_max"]
        )
        luminance_weight = _range_weight(
            hls[..., 1], gate["luminance_min"], gate["luminance_max"]
        )
        mask *= hue_weight * saturation_weight * luminance_weight

    if description.get("invert", False):
        mask = 1.0 - mask
    return np.clip(mask, 0.0, 1.0).astype(np.float32)


def apply_composition(
    rgb: np.ndarray,
    alpha: np.ndarray | None,
    composition: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray | None]:
    """执行受限透视、裁剪、旋转安全裁边与传统缩放。"""
    result = np.asarray(rgb, dtype=np.float32)
    result_alpha = None if alpha is None else np.asarray(alpha, dtype=np.float32)

    if "perspective_quad" in composition:
        height, width = result.shape[:2]
        source_quad = np.asarray(composition["perspective_quad"], dtype=np.float32)
        source_quad *= np.asarray([width - 1, height - 1], dtype=np.float32)
        target_quad = np.asarray(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
            dtype=np.float32,
        )
        transform = cv2.getPerspectiveTransform(source_quad, target_quad)
        result = cv2.warpPerspective(
            result,
            transform,
            (width, height),
            flags=cv2.INTER_LANCZOS4,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )
        if result_alpha is not None:
            result_alpha = cv2.warpPerspective(
                result_alpha,
                transform,
                (width, height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0,
            )

    left, top, right, bottom = composition.get("crop", [0.0, 0.0, 1.0, 1.0])
    height, width = result.shape[:2]
    x0, x1 = round(left * width), round(right * width)
    y0, y1 = round(top * height), round(bottom * height)
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(width, max(x0 + 1, x1)), min(height, max(y0 + 1, y1))
    result = result[y0:y1, x0:x1]
    if result_alpha is not None:
        result_alpha = result_alpha[y0:y1, x0:x1]

    angle = float(composition.get("rotate_degrees", 0.0))
    if abs(angle) > 1e-9:
        result, result_alpha = _rotate_without_fill(result, result_alpha, angle)

    resize = composition.get("resize")
    if resize:
        long_edge = int(resize["long_edge"])
        current_long = max(result.shape[:2])
        if long_edge != current_long:
            scale = long_edge / current_long
            new_size = (
                max(1, round(result.shape[1] * scale)),
                max(1, round(result.shape[0] * scale)),
            )
            interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LANCZOS4
            result = cv2.resize(result, new_size, interpolation=interpolation)
            if result_alpha is not None:
                result_alpha = cv2.resize(result_alpha, new_size, interpolation=interpolation)
    return np.clip(result, 0.0, 1.0), result_alpha


def _apply_tone(rgb: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    lightness = np.clip(_luminance(rgb), 0.0, 1.0)
    original = lightness.copy()

    shadows = float(parameters.get("shadows", 0.0))
    if shadows >= 0:
        lightness = lightness * (1.0 - shadows * 0.55) + np.sqrt(lightness) * shadows * 0.55
    else:
        amount = -shadows * 0.55
        lightness = lightness * (1.0 - amount) + lightness**2 * amount

    highlights = float(parameters.get("highlights", 0.0))
    if highlights >= 0:
        target = 1.0 - (1.0 - lightness) ** 2
        lightness = lightness * (1.0 - highlights * 0.4) + target * highlights * 0.4
    else:
        amount = -highlights * 0.4
        target = 1.0 - np.sqrt(np.clip(1.0 - lightness, 0.0, 1.0))
        lightness = lightness * (1.0 - amount) + target * amount

    whites = float(parameters.get("whites", 0.0))
    white_weight = _smoothstep(0.62, 0.98, lightness)
    lightness += whites * 0.18 * white_weight * (1.0 - lightness)

    blacks = float(parameters.get("blacks", 0.0))
    black_weight = 1.0 - _smoothstep(0.02, 0.38, lightness)
    if blacks >= 0:
        lightness += blacks * 0.16 * black_weight * (1.0 - lightness)
    else:
        lightness += blacks * 0.16 * black_weight * lightness

    contrast = float(parameters.get("contrast", 0.0))
    if contrast:
        pivot = 0.18
        contrasted = (lightness - pivot) * (1.0 + contrast) + pivot
        lightness = lightness * (1.0 - min(abs(contrast) * 1.25, 1.0)) + contrasted * min(
            abs(contrast) * 1.25, 1.0
        )

    lightness = np.clip(lightness, 0.0, 1.0)
    scale = lightness / np.maximum(original, 1e-5)
    return np.clip(rgb * scale[..., None], 0.0, 1.0)


def _apply_saturation(rgb: np.ndarray, saturation: float, vibrance: float) -> np.ndarray:
    if not saturation and not vibrance:
        return rgb
    srgb = linear_to_srgb(rgb)
    lightness = np.sum(srgb * np.asarray([0.2126, 0.7152, 0.0722]), axis=2, keepdims=True)
    chroma = srgb.max(axis=2, keepdims=True) - srgb.min(axis=2, keepdims=True)
    factor = 1.0 + saturation
    if vibrance:
        factor = factor + vibrance * (1.0 - np.clip(chroma, 0.0, 1.0))
    adjusted = lightness + (srgb - lightness) * factor
    return srgb_to_linear(np.clip(adjusted, 0.0, 1.0))


def _rotate_without_fill(
    rgb: np.ndarray, alpha: np.ndarray | None, angle: float
) -> tuple[np.ndarray, np.ndarray | None]:
    height, width = rgb.shape[:2]
    center = (width / 2.0, height / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos_a, sin_a = abs(matrix[0, 0]), abs(matrix[0, 1])
    bound_width = max(1, int(math.ceil(height * sin_a + width * cos_a)))
    bound_height = max(1, int(math.ceil(height * cos_a + width * sin_a)))
    matrix[0, 2] += bound_width / 2.0 - center[0]
    matrix[1, 2] += bound_height / 2.0 - center[1]
    rotated = cv2.warpAffine(
        rgb,
        matrix,
        (bound_width, bound_height),
        flags=cv2.INTER_LANCZOS4,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0,
    )
    rotated_alpha = None
    if alpha is not None:
        rotated_alpha = cv2.warpAffine(
            alpha,
            matrix,
            (bound_width, bound_height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )
    safe_width, safe_height = largest_rotated_rectangle(
        width, height, math.radians(abs(angle))
    )
    safe_width = min(bound_width, max(1, int(math.floor(safe_width))))
    safe_height = min(bound_height, max(1, int(math.floor(safe_height))))
    x0 = (bound_width - safe_width) // 2
    y0 = (bound_height - safe_height) // 2
    rotated = rotated[y0 : y0 + safe_height, x0 : x0 + safe_width]
    if rotated_alpha is not None:
        rotated_alpha = rotated_alpha[y0 : y0 + safe_height, x0 : x0 + safe_width]
    return rotated, rotated_alpha


def _resize_preview(
    rgb: np.ndarray, alpha: np.ndarray | None, long_edge: int
) -> tuple[np.ndarray, np.ndarray | None]:
    current_long = max(rgb.shape[:2])
    if current_long <= long_edge:
        return rgb, alpha
    scale = long_edge / current_long
    size = (max(1, round(rgb.shape[1] * scale)), max(1, round(rgb.shape[0] * scale)))
    resized = cv2.resize(rgb, size, interpolation=cv2.INTER_AREA)
    resized_alpha = cv2.resize(alpha, size, interpolation=cv2.INTER_AREA) if alpha is not None else None
    return resized, resized_alpha


def _save_tiff(
    photo: LoadedPhoto,
    gamma: np.ndarray,
    alpha: np.ndarray | None,
    destination: Path,
) -> None:
    bits = 16 if photo.bit_depth == 16 else 8
    if photo.profile_converted:
        try:
            source_profile = ImageCms.ImageCmsProfile(io.BytesIO(photo.icc_profile))
            rgb8 = np.rint(np.clip(gamma, 0.0, 1.0) * 255.0).astype(np.uint8)
            restored = ImageCms.profileToProfile(
                Image.fromarray(rgb8, mode="RGB"),
                SRGB_PROFILE,
                source_profile,
                outputMode="RGB",
                renderingIntent=0,
            )
            gamma = np.asarray(restored, dtype=np.float32) / 255.0
        except Exception as exc:
            raise ValueError(f"Cannot restore source ICC profile '{photo.profile_name}': {exc}") from exc
    maximum = (1 << bits) - 1
    channels = gamma
    if alpha is not None:
        channels = np.dstack([gamma, np.clip(alpha, 0.0, 1.0)])
    dtype = np.uint16 if bits == 16 else np.uint8
    encoded = np.rint(np.clip(channels, 0.0, 1.0) * maximum).astype(dtype)
    icc = photo.icc_profile or SRGB_PROFILE_BYTES
    extratags = _safe_tiff_extratags(photo.exif_values, icc, encoded.shape[1], encoded.shape[0])
    args: dict[str, Any] = {
        "photometric": "rgb",
        "compression": "deflate",
        "metadata": None,
        "extratags": extratags,
        "software": "refine-photos",
    }
    if encoded.shape[-1] == 4:
        args["extrasamples"] = "unassalpha"
    tifffile.imwrite(destination, encoded, **args)


def _safe_tiff_extratags(
    exif_values: dict[int, Any], icc: bytes, width: int, height: int
) -> list[tuple[int, str, int, Any, bool]]:
    tags: list[tuple[int, str, int, Any, bool]] = [
        (34675, "B", len(icc), icc, False),
    ]
    for tag in (271, 272, 306, 315, 33432, 36867, 42036):
        value = exif_values.get(tag)
        if isinstance(value, str) and value:
            tags.append((tag, "s", len(value) + 1, value, False))
    iso = exif_values.get(34855)
    if isinstance(iso, int) and 0 <= iso <= 65535:
        tags.append((34855, "H", 1, iso, False))
    tags.extend([(40962, "I", 1, width, False), (40963, "I", 1, height, False)])
    return tags


def _safe_exif_bytes(exif_bytes: bytes | None, size: tuple[int, int]) -> bytes | None:
    exif = Image.Exif()
    if exif_bytes:
        try:
            exif.load(exif_bytes)
        except Exception:
            exif = Image.Exif()
    for private_tag in (34853, 37500, 42032, 42033, 42037):
        exif.pop(private_tag, None)
    exif[274] = 1
    exif[305] = "refine-photos"
    exif[40962] = int(size[0])
    exif[40963] = int(size[1])
    return exif.tobytes() if len(exif) else None


def _normalize_tiff_shape(array: np.ndarray) -> np.ndarray:
    if array.ndim == 2:
        return np.repeat(array[..., None], 3, axis=2)
    if array.ndim != 3:
        raise ValueError(f"Unsupported TIFF array shape: {array.shape}")
    if array.shape[-1] in (3, 4):
        return array
    if array.shape[0] in (3, 4):
        return np.moveaxis(array, 0, -1)
    raise ValueError(f"TIFF must have one, three, or four channels: {array.shape}")


def _apply_orientation(array: np.ndarray, orientation: int) -> np.ndarray:
    if orientation == 2:
        return np.fliplr(array)
    if orientation == 3:
        return np.rot90(array, 2)
    if orientation == 4:
        return np.flipud(array)
    if orientation == 5:
        return np.swapaxes(array, 0, 1)
    if orientation == 6:
        return np.rot90(array, -1)
    if orientation == 7:
        return np.flip(np.swapaxes(array, 0, 1), axis=(0, 1))
    if orientation == 8:
        return np.rot90(array, 1)
    return array


def _profile_name(icc_profile: bytes | None) -> str:
    if not icc_profile:
        return "Assumed sRGB"
    try:
        profile = ImageCms.ImageCmsProfile(io.BytesIO(icc_profile))
        return ImageCms.getProfileDescription(profile).strip()
    except Exception:
        return "Unknown ICC profile"


def _is_srgb_profile(name: str) -> bool:
    lowered = name.lower()
    return "srgb" in lowered or "iec 61966" in lowered


def _combined_role_mask(
    protected_masks: list[dict[str, Any]], role: str, shape: tuple[int, int]
) -> np.ndarray:
    masks = [item["mask"] for item in protected_masks if item["role"] == role]
    if not masks:
        return np.zeros(shape, dtype=np.float32)
    return np.maximum.reduce(masks).astype(np.float32)


def _blend(original: np.ndarray, adjusted: np.ndarray, mask: np.ndarray) -> np.ndarray:
    weight = np.clip(mask, 0.0, 1.0)[..., None]
    return original * (1.0 - weight) + adjusted * weight


def _luminance(rgb: np.ndarray) -> np.ndarray:
    return np.sum(rgb * np.asarray([0.2126, 0.7152, 0.0722], dtype=np.float32), axis=2)


def _feather_binary(mask: np.ndarray, feather: float, width: int, height: int) -> np.ndarray:
    sigma = float(feather) * min(width, height)
    if sigma <= 0.25:
        return mask.astype(np.float32)
    return cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=sigma, sigmaY=sigma)


def _range_weight(values: np.ndarray, minimum: float, maximum: float) -> np.ndarray:
    if minimum <= 0 and maximum >= 1:
        return np.ones_like(values, dtype=np.float32)
    edge = min(0.05, max((maximum - minimum) * 0.2, 0.005))
    lower = _smoothstep(minimum - edge, minimum + edge, values)
    upper = 1.0 - _smoothstep(maximum - edge, maximum + edge, values)
    return np.clip(lower * upper, 0.0, 1.0).astype(np.float32)


def _smoothstep(edge0: float, edge1: float, values: np.ndarray) -> np.ndarray:
    denominator = max(edge1 - edge0, 1e-8)
    t = np.clip((values - edge0) / denominator, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=np.float32)
    return np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    ).astype(np.float32)


def linear_to_srgb(rgb: np.ndarray) -> np.ndarray:
    rgb = np.clip(np.asarray(rgb, dtype=np.float32), 0.0, 1.0)
    return np.where(
        rgb <= 0.0031308,
        rgb * 12.92,
        1.055 * np.power(rgb, 1.0 / 2.4) - 0.055,
    ).astype(np.float32)
