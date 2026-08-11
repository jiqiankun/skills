---
name: refine-photos
description: "Deterministic, non-generative photo refinement for portraits, landscapes, and environmental portraits. Use for color grading, portrait retouching, landscape editing, subject-background harmonization, reference style matching, blemish correction, and limited crop, rotation, or perspective correction while preserving identity, content, texture, and photographic truth."
---

# Refine Photos

Refine one portrait, landscape, or environmental portrait through source-responsive analysis, a validated JSON recipe, deterministic pixel editing, and post-render quality checks. Never use image generation for ordinary refinement.

## Communicate with the user

- Ask questions, present plans, explain warnings, and report results in Chinese by default.
- Keep internal recipe keys, script arguments, and Markdown instructions in English.
- If the user explicitly asks for another response language, follow that request.

## Enforce the photographic contract

Treat these as non-negotiable unless the creative-light exception below applies:

1. Preserve identity, semantic content, meaningful texture, material character, scene logic, and the source photograph's physical light.
2. Edit source pixels deterministically. Do not use diffusion, generative fill, inpainting, outpainting, neural face restoration, or AI super-resolution.
3. Do not reshape a face or body, move a subject, replace a sky, invent detail, change season, weather, or time of day, or remove real scene objects as "blemishes."
4. Repair only technical defects, confirmed image damage, and high-confidence small transient skin blemishes. Preserve moles, freckles, scars, wrinkles, birthmarks, and other identity-bearing features.
5. Correct capture problems before styling, but do not neutralize an intentional color cast, silhouette, high-key treatment, low-key treatment, haze, or other supported photographic intent.
6. Build tonal hierarchy before creative color, then preserve color relationships rather than applying indiscriminate saturation.
7. Reject any recipe operation not allowed by `schemas/recipe.schema.json` or the semantic checks in `scripts/recipe.py`.

Read [photography-principles.md](references/photography-principles.md) when principles conflict or an edit approaches a preservation boundary.

## Start every task with interaction routing

Infer the route from the user's words:

- If the user asks to see a plan first, use **plan mode**.
- If the user asks for direct delivery, one-step editing, or no questions, use **direct mode**.
- If the user gives no preference, ask exactly one Chinese question: whether to review a plan and preview first or receive the finished image directly.

Do not ask the user to fill in the four style layers. Infer omitted layers from the source and the request. Ask only when a material ambiguity cannot be resolved from the image, the request, or the preservation rules.

## Inspect and classify the source

1. Work on one image per run. Do not promise batch or cross-image consistency in this version.
2. Inspect the source visually before proposing parameters.
3. Classify the narrative hierarchy as `portrait-led`, `landscape-led`, `balanced`, `portrait-only`, or `landscape-only`.
4. Give explicit user intent priority. Otherwise infer hierarchy from subject scale, focus, depth of field, visual center, contrast, leading lines, and contextual importance.
5. Detect every person as protected. Apply detailed retouching only to primary or co-primary faces with sufficient source pixels.
6. Distinguish recoverable information from irrecoverable clipping, blur, or missing detail. Never claim to recover information that is absent.

Read [scene-strategies.md](references/scene-strategies.md) after classification and before writing local adjustments.

## Build a dynamic style decision

Represent style as four layers:

1. photographic aesthetic;
2. color tendency;
3. light tendency;
4. style strength from 1 to 3.

Keep retouch strength as a separate 1-to-3 control. Default both strengths to level 2. Treat those defaults as upper targets: automatically use less processing when the source resolution, noise, subject scale, or scene does not support level 2 safely.

Use dynamic rules, never a fixed LUT or fixed parameter preset. If the user provides a reference image, extract only tone hierarchy, contrast, color relationships, saturation, atmosphere, texture treatment, and subject-background weighting. Do not copy its content, lighting setup, geometry, or histogram mechanically.

Read [style-system.md](references/style-system.md) whenever selecting, translating, combining, or validating a style.

## Create and validate the recipe

1. Generate one JSON recipe conforming to [recipe.schema.json](schemas/recipe.schema.json).
2. Use normalized coordinates in the range `0..1` for crop and mask geometry.
3. Use protected masks for skin, identity-bearing regions, important textiles, architectural detail, or other texture that must survive local processing.
4. Use `repairs` only for evidenced sensor dust, hot pixels, confirmed damage, or high-confidence transient blemishes. Sample a nearby source region from the same real surface; never use a repair to remove a scene object or identity feature.
5. Keep global correction moderate, then use the smallest local adjustment that solves an isolated problem.
6. Record observations, planned changes, and known limitations in the recipe analysis block.
7. Run validation before rendering:

```powershell
python scripts/refine.py validate path\to\recipe.json
```

Read [recipe-format.md](references/recipe-format.md) before creating the first recipe in a task or whenever validation fails.

## Render and review

Check dependencies once per environment:

```powershell
python scripts/refine.py check
```

If dependencies are missing, use a Python 3.11 or 3.12 environment and request approval before installing `scripts/requirements.txt`.

Render a review-sized preview:

```powershell
python scripts/refine.py render source.jpg recipe.json preview.jpg --preview-max 2048 --auto-safe
```

Always inspect the rendered preview visually. Check the main subject, background harmony, mask boundaries, skin, protected textures, clipping, color casts, and whether the result still reads immediately as a photograph.

In **plan mode**:

1. Present a short Chinese analysis, the chosen hierarchy and four style layers, intended global and local edits, limitations, and crop risk.
2. Show the low-resolution preview.
3. Wait for confirmation before full-resolution rendering.

In **direct mode**:

1. Render and inspect the preview internally without asking for approval.
2. If it passes, render the full-resolution output with the same applied recipe.
3. Deliver the image, applied recipe, and audit summary.

Render the final image to a new path; never overwrite the source:

```powershell
python scripts/refine.py render source.jpg applied-recipe.json source_refined.jpg --auto-safe
```

The renderer writes an applied-recipe sidecar and an audit sidecar next to the output unless explicit paths are supplied.

## Handle quality failures

- Treat identity, semantic-content, local-geometry, forbidden-operation, crop-retention, and creative-light-authorization violations as hard failures. Do not render or deliver them.
- Treat excess clipping, texture loss, skin hue movement, halo risk, and excessive saturation as soft failures.
- With `--auto-safe`, allow one reduced-strength rerender. Do not loop.
- If no edited result passes, preserve the source and explain the limiting cause in Chinese.

Read [quality-gates.md](references/quality-gates.md) when interpreting an audit or revising a failed recipe.

## Apply the explicit creative-light exception

Keep synthetic light disabled by default. Enable it only when the user explicitly asks to add a new optical effect and acknowledges that it departs from the captured light.

Allow deterministic gradients, glow, flare, light leak, beam, haze, or vignette shaping. Mark `creative_light.enabled` and `creative_light.acknowledged` as `true`, warn the user in Chinese, and identify the result as a creative version. Still forbid generated objects, a new visible sun or lamp, fabricated shadows or reflections, generative relighting, or content reconstruction.

## Respect composition and format boundaries

- Retain at least 90% of source area after all crop, perspective, and rotation-safe trimming.
- Limit rotation to `±3` degrees.
- Use perspective correction only for landscape or architecture with no people, and limit every corner displacement to 5% of the frame.
- Never fill rotation or crop gaps with generated pixels.
- Do not upscale by default. Use traditional interpolation only when explicitly requested, and state that it does not restore detail.
- Accept JPEG, PNG, and supported 16-bit TIFF in this version. Route RAW through a reliable external developer to a 16-bit TIFF first; never use the embedded RAW preview as the source.

Read [input-output.md](references/input-output.md) for ICC handling, TIFF limitations, metadata privacy, output naming, and RAW routing.
