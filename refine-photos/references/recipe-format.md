# Recipe Format

Use `schemas/recipe.schema.json` as the authoritative structural whitelist. `scripts/recipe.py` adds semantic checks that JSON Schema cannot express clearly.

## Required top-level fields

- `version`: recipe version, currently `1`.
- `analysis`: source observations, hierarchy rationale, planned changes, and limitations.
- `intent`: interaction mode, scene hierarchy, people flag, style layers, strengths, reference use, and creative-light authorization.
- `global`: bounded source-responsive correction.

Optional sections are `color_ranges`, `color_balance`, `monochrome`, `local_adjustments`, `protected_masks`, `repairs`, `detail`, `composition`, `creative_effects`, and `quality`. The renderer may add top-level `safety_adjusted: true` after its single conservative rerender.

## Coordinate rules

- Express points and crop values as normalized source coordinates from `0` to `1`.
- Express an ellipse as `center: [x, y]` and `radius: [rx, ry]`.
- Express a polygon as three or more normalized points.
- Express a linear gradient with `start` and `end`; the mask grows from zero at start to one at end.
- Express a radial gradient with `center`, `inner_radius`, and `outer_radius`.
- Use `feather` as a normalized fraction of the shorter image edge.

## Example

```json
{
  "version": 1,
  "analysis": {
    "subject_hierarchy": "The person and garden are co-subjects.",
    "observations": ["Face is slightly green from foliage spill.", "Highlights are recoverable."],
    "planned_changes": ["Correct the global cast.", "Lift the face locally.", "Restrain garden greens."],
    "limitations": []
  },
  "intent": {
    "interaction": "plan",
    "scene": "balanced",
    "contains_people": true,
    "aesthetic": "jiangnan-elegance",
    "color_tendency": "qingdai-soft",
    "light_tendency": "airy-soft",
    "style_level": 2,
    "retouch_level": 2,
    "reference_used": false,
    "creative_light": {"enabled": false, "acknowledged": false}
  },
  "global": {
    "exposure_ev": 0.1,
    "temperature": 0.0,
    "tint": 0.02,
    "contrast": -0.04,
    "highlights": -0.16,
    "shadows": 0.08,
    "whites": -0.03,
    "blacks": 0.02,
    "saturation": -0.03,
    "vibrance": 0.06
  },
  "local_adjustments": [
    {
      "name": "primary-face",
      "mask": {"type": "ellipse", "center": [0.47, 0.35], "radius": [0.08, 0.12], "feather": 0.04},
      "adjustments": {"exposure_ev": 0.08, "tint": 0.02, "smoothing": 0.08}
    }
  ],
  "protected_masks": [
    {
      "name": "skin",
      "role": "skin",
      "mask": {"type": "ellipse", "center": [0.47, 0.35], "radius": [0.08, 0.12], "feather": 0.03}
    }
  ],
  "detail": {"denoise": 0.05, "sharpen": 0.08, "grain": 0.0},
  "composition": {"crop": [0.0, 0.0, 1.0, 1.0], "rotate_degrees": 0.0},
  "quality": {
    "max_highlight_clip_delta": 0.005,
    "max_shadow_clip_delta": 0.005,
    "min_texture_ratio": 0.72,
    "max_skin_hue_shift_degrees": 10.0,
    "max_mask_halo_ratio": 2.5
  }
}
```

## Semantic constraints

- Require `creative_light.enabled` and `creative_light.acknowledged` before accepting any `creative_effects`.
- Require `monochrome.enabled: true` when the aesthetic is `black-and-white`; reject monochrome conversion for other aesthetics.
- Reject perspective correction when `contains_people` is true.
- Keep every perspective corner within 5% of its original corner and retain at least 90% polygon area.
- Keep total composition retention at or above 90% after crop and rotation-safe trimming.
- Cap smoothing by retouch level and never allow geometry keys such as eye size, face shape, body shape, liquify, warp, object removal, sky replacement, or generated detail.
- Require an evidence note and `evidence_confirmed: true` for every source-pixel repair. Copy only a nearby patch from the same real surface. Keep transient-blemish radius at or below 1.5% of the short edge, every other repair at or below 3%, and cumulative repair area at or below 1% of the frame.
- Reject unknown fields rather than guessing their meaning.
