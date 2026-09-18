---
name: scenes-gathered-zine
description: "Transform a user-supplied photo into a broadly appealing editorial paper-poster with truthful photography as the dominant factual and emotional anchor, at least 25% designed quiet paper in ordinary use, restrained source-derived collage, harmonious color, and a subtle vintage paper environment that does not recolor the defining subject. Use for attractive, immediately readable zines by default, and switch to a more asymmetric editorial layout when the user asks for magazine, editorial, generous negative-space, or authorial treatment."
---

# 实景拼贴 · Gathered Scenes Zine v1.7

Create a beautiful editorial paper-poster from a supplied photo. Keep the main subject and defining scene unmistakably photographic; use illustration, quiet paper, material, color, and optional text to improve composition without replacing the photographic fact.

Return the generated raster image and one brief Chinese creative rationale. Reveal the final prompt or detailed art direction only when the user explicitly asks.

## Decision Order

Resolve choices in this order:

1. Maximize immediate broad-audience beauty and emotional readability.
2. Enforce photographic truth as a hard boundary; reject any attractive option that breaks identity, anatomy, perspective, defining light, or scene relationships.
3. Establish clear composition, hierarchy, eye path, and designed breathing room.
4. Add only necessary collage, illustration, color, and material behavior.
5. Preserve one quiet source-specific authorial residue.

Use this orientation, not a literal score:

- 80% immediate visual appeal and photographic pleasure;
- 15% source-specific character;
- 5% ambiguity, asymmetry, interruption, or poetic residue.

Make the image beautiful before making it conspicuously artistic. If an unusual device does not improve the complete image, omit it.

## Reference Routing

This file is sufficient for Default Mode.

Read [references/art-direction.md](references/art-direction.md) before compiling the prompt when any of these apply:

- Editorial Mode or Strong Collage Mode is active;
- the user requests magazine-like layout, authorial composition, typography, temporal traces, visible tearing, abrasion, or complex materials;
- dense foliage, crowds, architecture, repeated detail, or another difficult source requires advanced compression;
- the first generated result needs targeted correction.

## Hard Boundaries

- Follow explicit user constraints.
- Keep a substantial, coherent photographic anchor; a token photo fragment does not qualify.
- Preserve defining people, faces, expressions, hands, anatomy, objects, architecture, actions, perspective, scale, overlap, natural color, and source light.
- Do not redraw, repaint, stylize away, obscure, or replace the defining photographic subject.
- Keep the main subject as the first perceptual and emotional entry point unless the user explicitly requests strong abstraction.
- Keep illustration and opaque material effects off defining facial, anatomical, product, food, floral, vehicle, or architectural cues.
- Preserve user-supplied wording exactly.
- Keep the result flat and paper-native; never create a 3D mockup.
- Do not damage a strong photograph merely to prove that transformation occurred.

## Source Handling

- Treat a supplied photo plus a transformation request as consent to use image generation.
- Ask for the photo only when it is missing.
- Send only the final prompt and required reference image to the generation service.
- Do not browse for, share, save, commit, or upload the source elsewhere.
- Do not save source or generated images into project files unless the user asks.
- Generalize identifiable details only when requested or when scene identity remains intact.

## Read the Photograph

Build an internal **Scene Card**:

- **Semantic minimum:** the smallest subject-and-relationship set that identifies the scene.
- **Core subject:** the defining person, animal, object, building, product, food, flower, vehicle, landscape feature, or relationship.
- **Subject appeal:** the light, expression, gesture, silhouette, color, texture, atmosphere, intimacy, scale, or timing that already makes it attractive.
- **Photography preservation map:** the subject, context, light, color, texture, focus, perspective, depth, and timing that must stay photographic.
- **Truth invariants:** identity, anatomy, gesture, relative position, facing direction, horizon, path, perspective, scale, overlap, and factual scene relationships.
- **Photographic event:** viewpoint, distance, framing, crop, focus, blur, decisive moment, or off-frame continuation.
- **Spatial structure:** foreground, middle ground, background, compression, enclosure, opening, occlusion, depth, or intentional flatness.
- **Dominant gesture:** the strongest axis, gaze, curve, diagonal, convergence, repetition, or movement.
- **Light architecture:** direction, value hierarchy, temperature, shadow mass, reflection, haze, glow, backlight, or edge loss.
- **Color atmosphere:** dominant family, temperature, value range, existing saturated events, and meaningful minor colors.
- **Source logic:** one or two contours, axes, intervals, rhythms, gaps, directions, occlusions, light transitions, movements, or pressure fields that can organize the intervention.
- **Temporal evidence:** credible movement, waiting, repetition, weathering, growth, fading, arrival, departure, passing, or disappearance.
- **Natural quiet areas:** sky, water, wall, ground, haze, reflection, shadow, or another low-information field.
- **Broad-appeal risk:** anything likely to become confusing, empty, harsh, distressed, gimmicky, weak, or less attractive than the source.

Name one direct source-supported tension. Prefer stillness/movement, density/openness, near/far, light/shadow, warm/cool, order/irregularity, solid/empty, continuity/interruption, enclosure/openness, or weight/release. Use a more conceptual tension only when the source clearly supports it.

## Select the Mode

Treat every percentage as a perceptual diagnostic, not a pixel quota. Photography weight, quiet-paper area, illustration field, and active ink may overlap and do not need to sum to 100%.

### Default Mode

Use unless the request activates another mode:

- photography: 60–70% perceptual weight;
- designed quiet paper: 25–35% of the canvas;
- illustration/collage influence field: 20–30%;
- active illustrated ink or opaque collage: 8–14%;
- restrained-to-balanced intervention;
- familiar, centered, symmetric, or conventionally balanced composition is valid when it serves the source;
- nearly seamless paper handoff or quiet fiber seam;
- source-native photographic color.

### Editorial Mode

Activate when the user requests or clearly implies magazine, editorial, editorial negative space, authorial, or similar treatment:

- photography: 55–65% perceptual weight;
- designed quiet paper: 30–45%;
- illustration/collage influence field: 25–40%;
- active illustrated ink or opaque collage: 10–18%;
- balanced intervention;
- source-driven editorial asymmetry and stronger interval rhythm;
- the photographic subject still appears before the effect.

### Strong Collage Mode

Activate only when the user explicitly asks for strong collage, experimental, heavily stylized, avant-garde, challenging, or strongly abstracted treatment:

- photography may fall to 40–55% perceptual weight;
- preserve the semantic minimum and all defining truth invariants;
- preserve recognizable photographic texture, light, perspective, and subject integrity;
- never convert the defining subject into an illustrated reconstruction.

### Quiet-Paper Exception

Treat 25% quiet paper as the ordinary diagnostic floor and 25–40% as the normal range. Allow less when the user requests full bleed or when celebration, crowding, forest density, urban pressure, abundance, or another source-specific density would be damaged by forced emptiness.

## Map Truth and Intervention

Assign each important region or relationship:

- **Preserve:** keep the coherent photographic anchor, subject appeal, truth invariants, source light, color, texture, and necessary context.
- **Protect:** prohibit alteration or obstruction of defining identity, anatomy, action, architecture, product form, perspective, or successful source light.
- **Crop:** reframe only when recognition, subject appeal, directional breathing room, and key relationships survive.
- **Extend:** continue a source contour, axis, interval, rhythm, gap, direction, light transition, or movement into paper or illustration.
- **Translate:** convert selected secondary detail—not the defining subject—into a mass, contour, field, rhythm, counterform, or exposed paper.
- **Omit:** remove clutter, redundant detail, competing marks, and unnecessary effects.

Let photography carry recognition and emotional pleasure. Let collage improve framing, balance, rhythm, continuity, atmosphere, or finish.

## Choose the Direction

Draft two internal directions that preserve the same photographic truth but differ in one spatial relationship and one material, chromatic, or light decision.

For each, check:

- first-glance attractiveness;
- photographic integrity and subject appeal;
- dominant field, focal relationship, eye path, and quiet exit;
- one source-derived tension and one or two source logics;
- intervention strength and mode budgets;
- risk of becoming generic, empty, decorative, nostalgic, confusing, or overdesigned.

Choose the more beautiful direction. If beauty is comparable, choose the one with clearer photography, stronger hierarchy, more harmonious color, and fewer attention-seeking effects.

## Direct the Visible Form

### Composition and Hierarchy

- Preserve source orientation by default; use 3:5 portrait only when requested or source geometry benefits.
- Establish one dominant field, one subordinate field, one focal relationship, and one coherent eye path.
- Keep photography dominant or co-dominant within the active mode budget.
- Preserve directional breathing room before a gaze, path, wave, vehicle, figure, or diagonal.
- Balance visual weight rather than equal area.
- Use symmetry or familiar balance when beautiful; use asymmetry only when source logic or Editorial Mode supports it.
- Reserve the strongest combined contrast for one primary event.
- Keep at least two supporting systems quiet: illustration, structural color, material edge, texture, temporal trace, or typography.
- Never make core photography dull or muddy merely to reserve contrast for an effect.

### Negative Space

- Shape quiet paper as breathing room, passage, pressure, silence, or release—not leftover background.
- Use it to improve subject presence, hierarchy, eye movement, rhythm, clarity, and atmosphere.
- Keep it visibly intentional and compositionally connected to a source edge, gesture, direction, light transition, or spatial opening.
- Avoid passive emptiness created only by shrinking the photograph.

### Photography and Illustration

Prefer support field or continuation in Default Mode. Use counterform, displacement, or dissolution only when source-supported.

- **Support field:** place a broad low-density structure behind or around photography.
- **Continuation:** extend a real axis, contour, rhythm, gap, light transition, or movement across the handoff.
- **Counterform:** derive a positive or negative shape from a source silhouette, shadow, opening, or quiet area.
- **Displacement:** repeat or relocate one source interval to alter balance.
- **Dissolution:** let one secondary fact weaken into paper while the photographic anchor remains stable.

Use one primary illustration grammar and at most one supporting grammar. Keep it simpler and usually lower in perceptual weight than the photographic subject. Enlarge the field before adding detail.

### Light and Color

- Preserve attractive source light, natural perspective, focal hierarchy, skin or surface rendering, and successful source color.
- Transform strong value, edge, or depth behavior mainly in secondary regions and transitions.
- Add no new hue when the photograph already contains the strongest chromatic event.
- When useful, add one source-related print hue for balance, eye path, continuity, temperature, or figure–ground.
- Prefer source resonance, analogous harmony, then a temperature bridge; use complementary contrast only when it clearly improves attractiveness and legibility.
- Apply subtle vintage warmth only to paper, fibers, neutral illustration inks, and transition zones.
- Do not brown, mute, bleach, or globally recolor the defining photographic subject.

### Material, Time, and Text

- Prefer a nearly seamless handoff or quiet fiber seam.
- Use visible tearing, abrasion, or emulsion loss only when source movement, pressure, weathering, fading, or user intent justifies it.
- Keep paper effects subordinate; reduce them when noticed before the subject.
- Use at most one source-supported temporal device and keep it clean at first glance.
- Use no text by default. Add one quiet editorial trace only when language contributes something the image cannot carry through silence.
- Preserve supplied text exactly; keep authored text brief, concrete, legible, and subordinate.

## Compile the Generation Prompt

Write four compact visible-pixel sections:

1. **Canvas and attention:** orientation, active mode, photographic anchor, main subject, dominant/subordinate fields, first entry, eye path, quiet paper, tension, and contrast budget.
2. **Photographic truth:** semantic minimum, protected regions, truth invariants, subject appeal, source light, natural color, texture, perspective, focus, depth, context, and source logic.
3. **Intervention:** preserve/crop/extend/translate/omit map, illustration relationship and grammar, field versus active density, negative-space role, handoff, optional hue, time, and exact text.
4. **Reproduction and boundaries:** paper and print behavior, subtle vintage paper tone, emotional temperature, broad-appeal restraint, mode-specific composition, source-specific anti-template direction, and hard exclusions.

State what must disappear as clearly as what must remain. Compile only instructions that can become visible pixels; omit file paths, analysis notes, and design theory.

Generate with the supplied photo as the only required visual reference. Stop at prompt-only only when explicitly requested.

## Inspect and Correct

Inspect at thumbnail and normal scale.

### Broad-Appeal Gate

- Is the main subject immediately attractive, clear, and emotionally readable?
- Is the complete image harmonious, balanced, memorable, and understandable without rationale?
- Is there one obvious hierarchy and one primary contrast event?
- Does the quiet paper feel designed rather than empty?
- Would removing an unusual effect make the result more beautiful?

### Photographic Truth Gate

- Does the photograph remain dominant or co-dominant within the active mode?
- Are identity, anatomy, expression, action, architecture, product form, perspective, source light, color, texture, focus, depth, and context credible?
- Does the viewer remember the subject before the collage technique?
- Has any token fragment, repainting, opaque effect, or over-abstraction displaced the photographic fact?

### Composition and Intervention Gate

- Do photography, illustration, color, and paper share source-derived logic?
- Do the mode budgets function as guardrails rather than visible formulas?
- Are at least two supporting systems quiet?
- Are material, aging, time, and typography necessary and subordinate?
- Does one source-specific relation prevent generic prettiness?

Regenerate at most once. Correct only the dominant failure. Read [references/art-direction.md](references/art-direction.md) for the targeted correction matrix.

## Hard Avoids

Avoid altered identity, distorted anatomy, damaged or repainted core photography, token photo fragments, full-scene tracing, dense filigree, timid doodles, arbitrary geometry, generic motifs, forced asymmetry, empty-for-minimalism layouts, decorative aging, gratuitous distress, multiple temporal effects, multiple added hues, detached color marks, fluorescent color without source support, every device peaking together, clean digital masks, sticker borders, uniform torn frames, heavy paper shadows, curled paper, layered 3D depth, scrapbooking, faux metadata, generic poetic captions, large polished type, commercial advertising hierarchy, logos, CTA, glossy mockups, imposed cinematic depth of field, fashion-editorial rewriting of the source, aggressive sharpening, AI smoothing, over-retouching, deliberate ugliness used to signal seriousness, visual confusion presented as sophistication, generic prettiness without source character, and watermarks.

## Output

Return:

```markdown
![Gathered Scenes Zine poster](absolute-image-path-or-rendered-image)

**创作思路**

[用 1–3 句中文说明主体、来源张力、摄影与拼贴共享的视觉逻辑，以及为什么整体更美、更完整；不要披露完整提示词。]
```

Add detailed notes only when requested. Do not reveal the generation prompt unless explicitly requested.
