from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import tifffile
from PIL import Image, ImageCms


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from engine import SRGB_PROFILE_BYTES, load_photo, render_photo, save_photo  # noqa: E402
from quality import audit_render  # noqa: E402
from recipe import RecipeError, template_recipe, validate_recipe  # noqa: E402


class RefinePhotosPipelineTest(unittest.TestCase):
    """覆盖白名单校验、确定性渲染与高位深输出。"""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_schema_rejects_unknown_operation(self) -> None:
        recipe = template_recipe()
        recipe["eye_size"] = 1.2
        with self.assertRaises(RecipeError):
            validate_recipe(recipe)

    def test_schema_rejects_short_fixed_array(self) -> None:
        recipe = template_recipe()
        recipe["composition"]["crop"] = [0.0, 0.0, 1.0]
        with self.assertRaises(RecipeError):
            validate_recipe(recipe)

    def test_creative_effect_requires_explicit_acknowledgment(self) -> None:
        recipe = template_recipe()
        recipe["creative_effects"] = [
            {
                "name": "warm-edge",
                "kind": "light-leak",
                "mask": {
                    "type": "radial-gradient",
                    "center": [0.0, 0.2],
                    "inner_radius": 0.0,
                    "outer_radius": 0.5,
                },
                "adjustments": {"exposure_ev": 0.1},
            }
        ]
        with self.assertRaises(RecipeError):
            validate_recipe(recipe)

    def test_black_and_white_rejects_color_conflict(self) -> None:
        recipe = template_recipe()
        recipe["intent"]["aesthetic"] = "black-and-white"
        recipe["intent"]["color_tendency"] = "forest-fresh"
        recipe["monochrome"] = {
            "enabled": True,
            "channel_mix": [0.3, 0.6, 0.1],
            "toning_color": [0.9, 0.85, 0.75],
            "toning_strength": 0.05,
        }
        with self.assertRaises(RecipeError):
            validate_recipe(recipe)

    def test_jpeg_render_and_audit(self) -> None:
        source = self.directory / "mixed-scene.jpg"
        output = self.directory / "mixed-scene_refined.jpg"
        Image.fromarray(self._scene_uint8(), mode="RGB").save(
            source, quality=96, icc_profile=SRGB_PROFILE_BYTES
        )

        recipe = self._balanced_recipe()
        recipe = validate_recipe(recipe, (320, 240))
        photo = load_photo(source)
        rendered = render_photo(photo, recipe)
        audit = audit_render(rendered, recipe)
        self.assertTrue(audit["passed"], json.dumps(audit, indent=2))
        save_photo(photo, rendered, output)

        self.assertTrue(output.is_file())
        self.assertEqual(source.stat().st_size > 0, True)
        with Image.open(output) as result:
            self.assertEqual(result.mode, "RGB")
            self.assertGreater(result.width, 280)
            self.assertGreater(result.height, 210)
            self.assertIsNotNone(result.info.get("icc_profile"))

    def test_source_pixel_repair_is_confirmed_local_and_deterministic(self) -> None:
        source = self.directory / "blemish.png"
        array = self._scene_uint8()
        array[112, 145] = [255, 255, 255]
        Image.fromarray(array, mode="RGB").save(
            source, icc_profile=SRGB_PROFILE_BYTES
        )

        recipe = template_recipe()
        recipe["intent"].update(
            {"scene": "portrait-only", "contains_people": True}
        )
        repair = {
            "name": "confirmed-transient-spot",
            "kind": "transient-blemish",
            "target": [145 / 319, 112 / 239],
            "source": [150 / 319, 112 / 239],
            "radius": 0.006,
            "feather": 0.3,
            "opacity": 1.0,
            "evidence": "A single isolated bright spot inconsistent with surrounding skin.",
            "evidence_confirmed": False,
        }
        recipe["repairs"] = [repair]
        with self.assertRaises(RecipeError):
            validate_recipe(recipe, (320, 240))

        repair["evidence_confirmed"] = True
        recipe = validate_recipe(recipe, (320, 240))
        photo = load_photo(source)
        first = render_photo(photo, recipe)
        second = render_photo(photo, recipe)

        np.testing.assert_array_equal(first.final_linear, second.final_linear)
        self.assertLess(
            float(first.final_linear[112, 145].mean()),
            float(photo.linear[112, 145].mean()),
        )
        np.testing.assert_allclose(
            first.final_linear[20, 20], photo.linear[20, 20], atol=1e-7
        )

    def test_16_bit_tiff_stays_16_bit(self) -> None:
        source = self.directory / "source-16.tif"
        output = self.directory / "output-16.tif"
        array = (self._scene_uint8().astype(np.uint16) * 257).astype(np.uint16)
        tifffile.imwrite(
            source,
            array,
            photometric="rgb",
            metadata=None,
            extratags=[
                (
                    34675,
                    "B",
                    len(SRGB_PROFILE_BYTES),
                    SRGB_PROFILE_BYTES,
                    False,
                )
            ],
        )

        recipe = validate_recipe(template_recipe(), (320, 240))
        photo = load_photo(source)
        rendered = render_photo(photo, recipe)
        audit = audit_render(rendered, recipe)
        self.assertTrue(audit["passed"], json.dumps(audit, indent=2))
        save_photo(photo, rendered, output)

        result = tifffile.imread(output)
        self.assertEqual(result.dtype, np.uint16)
        self.assertEqual(result.shape, array.shape)
        with tifffile.TiffFile(output) as tif:
            self.assertEqual(tif.pages[0].tags[305].value, "refine-photos")
            self.assertEqual(tif.pages[0].tags[34675].value, SRGB_PROFILE_BYTES)

    def test_8_bit_tiff_restores_converted_profile(self) -> None:
        source = self.directory / "source-profiled.tif"
        output = self.directory / "output-profiled.tif"
        array = self._scene_uint8()
        tifffile.imwrite(
            source,
            array,
            photometric="rgb",
            metadata=None,
            extratags=[
                (
                    34675,
                    "B",
                    len(SRGB_PROFILE_BYTES),
                    SRGB_PROFILE_BYTES,
                    False,
                )
            ],
        )

        with patch("engine._is_srgb_profile", return_value=False):
            photo = load_photo(source)
            self.assertTrue(photo.profile_converted)
            recipe = validate_recipe(template_recipe(), (320, 240))
            rendered = render_photo(photo, recipe)
            save_photo(photo, rendered, output)

        with tifffile.TiffFile(output) as tif:
            self.assertEqual(tif.pages[0].tags[34675].value, SRGB_PROFILE_BYTES)

    def test_combined_composition_limit_is_enforced(self) -> None:
        recipe = template_recipe()
        recipe["composition"] = {
            "crop": [0.02, 0.02, 0.98, 0.98],
            "rotate_degrees": 3.0,
        }
        with self.assertRaises(RecipeError):
            validate_recipe(recipe, (320, 240))

    @staticmethod
    def _scene_uint8() -> np.ndarray:
        """生成包含天空、植被、建筑和肤色区域的测试照片。"""
        height, width = 240, 320
        yy, xx = np.mgrid[0:height, 0:width]
        image = np.zeros((height, width, 3), dtype=np.float32)
        sky = yy < 105
        image[sky] = np.stack(
            [
                0.36 + 0.12 * yy[sky] / 105,
                0.56 + 0.10 * yy[sky] / 105,
                0.76 + 0.08 * yy[sky] / 105,
            ],
            axis=1,
        )
        ground = ~sky
        image[ground] = np.stack(
            [
                0.16 + 0.08 * xx[ground] / width,
                0.34 + 0.18 * xx[ground] / width,
                0.18 + 0.06 * yy[ground] / height,
            ],
            axis=1,
        )
        image[125:220, 215:300] = [0.45, 0.28, 0.18]
        face = ((xx - 145) / 24) ** 2 + ((yy - 112) / 32) ** 2 <= 1
        image[face] = [0.70, 0.47, 0.35]
        garment = ((xx - 145) / 34) ** 2 + ((yy - 175) / 55) ** 2 <= 1
        texture = ((xx + yy) % 7) / 255.0
        image[garment] = np.stack(
            [0.34 + texture[garment], 0.12 + texture[garment], 0.18 + texture[garment]],
            axis=1,
        )
        return np.rint(np.clip(image, 0.0, 1.0) * 255.0).astype(np.uint8)

    @staticmethod
    def _balanced_recipe() -> dict:
        recipe = template_recipe()
        recipe["analysis"] = {
            "subject_hierarchy": "The person and landscape are co-subjects.",
            "observations": ["The face is slightly dark relative to the landscape."],
            "planned_changes": ["Lift the face and restrain vegetation saturation."],
            "limitations": [],
        }
        recipe["intent"].update(
            {
                "interaction": "direct",
                "scene": "balanced",
                "contains_people": True,
                "aesthetic": "natural",
                "color_tendency": "source-derived",
                "light_tendency": "natural-balanced",
            }
        )
        recipe["global"].update(
            {
                "exposure_ev": 0.05,
                "contrast": 0.03,
                "highlights": -0.08,
                "shadows": 0.06,
                "vibrance": 0.03,
            }
        )
        recipe["color_ranges"] = [
            {
                "name": "vegetation",
                "hue_center": 120.0,
                "hue_width": 55.0,
                "hue_shift": -2.0,
                "saturation": -0.04,
                "luminance": 0.01,
                "protect_skin": True,
            }
        ]
        face_mask = {
            "type": "ellipse",
            "center": [145 / 319, 112 / 239],
            "radius": [26 / 319, 35 / 239],
            "feather": 0.02,
        }
        recipe["local_adjustments"] = [
            {
                "name": "face",
                "mask": face_mask,
                "adjustments": {
                    "exposure_ev": 0.05,
                    "tint": 0.01,
                    "smoothing": 0.02,
                },
            }
        ]
        recipe["protected_masks"] = [
            {"name": "skin", "role": "skin", "mask": face_mask},
            {
                "name": "garment",
                "role": "textile",
                "mask": {
                    "type": "ellipse",
                    "center": [145 / 319, 175 / 239],
                    "radius": [38 / 319, 58 / 239],
                    "feather": 0.015,
                },
            },
        ]
        recipe["detail"] = {"denoise": 0.0, "sharpen": 0.02, "grain": 0.0}
        recipe["composition"] = {
            "crop": [0.005, 0.005, 0.995, 0.995],
            "rotate_degrees": 0.0,
        }
        recipe["quality"] = {
            "max_highlight_clip_delta": 0.05,
            "max_shadow_clip_delta": 0.05,
            "min_texture_ratio": 0.5,
            "max_skin_hue_shift_degrees": 30.0,
            "max_mask_halo_ratio": 5.0,
            "max_extreme_saturation_delta": 0.1,
        }
        return recipe


if __name__ == "__main__":
    unittest.main()
