---
name: scene-distillation-zine
description: "Transform a user-supplied photo into a broadly appealing, source-specific illustrated paper poster with no retained photographic pixels. Prioritize first-glance beauty, a clear and attractive main subject, harmonious composition and color, graceful abstraction, and designed breathing room; preserve one quieter source-derived tension and tactile authorial residue for longer viewing. Use for accessible editorial reinterpretations, preserve source orientation by default, and support the exact `单色块模式` trigger for one contiguous saturated color field against neutral ink."
---

# 影像蒸馏 · Scene Distillation Zine v1.6

Create an independently compelling paper-poster artwork that feels beautiful before it feels clever. Treat the supplied photo as semantic, photographic, and aesthetic evidence, never as a visual layer in the final image.

Return the generated raster image, a brief Chinese creative rationale, and concise art-direction notes. Do not reveal the generation prompt.

Aim for **broad appeal with authorial residue**:

- make the first glance clear, harmonious, balanced, attractive, and emotionally readable;
- keep the main subject or defining relationship as the first visual entry point;
- let the second glance reveal one source-specific tension, asymmetry, material event, or unresolved relation;
- do not sacrifice immediate visual pleasure merely to appear conceptual or experimental;
- do not erase source character merely to make the work safe or generic.

## Core Contract

Resolve aesthetic conflicts in this order:

1. Make the complete image beautiful, coherent, and visually inviting before explanation.
2. Keep the main subject or defining scene relationship recognizable, attractive, and emotionally readable.
3. Preserve the source's spirit and at least one irreplaceable source-specific quality.
4. Establish clear hierarchy, readable balance, harmonious color, graceful light, and shaped breathing room.
5. Embody one source-derived central tension that can be felt without explanation.
6. Preserve enough asymmetry, surprise, ambiguity, or incompleteness to avoid generic prettiness.
7. Maintain a tactile, flat, non-commercial paper-and-ink identity.
8. Apply technical rules only when they serve the decisions above.

Treat beauty as coherence among subject presence, proportion, interval, rhythm, hierarchy, visual weight, light, color, tension, material, silence, and surprise—not as polish, fashionable styling, visual difficulty, or an accumulation of artistic effects.

### Broad-Appeal Beauty

Aim for two levels of response:

1. **Immediate appeal:** make the image clear, balanced, harmonious, emotionally readable, and visually pleasant at first glance.
2. **Lasting interest:** preserve one restrained tension, interruption, asymmetry, material irregularity, or interpretive opening that rewards longer viewing.

Use roughly 70% immediate visual appeal, 20% source-specific character, and 10% poetic ambiguity as an aesthetic orientation, never as a numeric composition formula.

If conceptual sophistication and immediate visual appeal conflict, prefer immediate appeal unless the user explicitly requests experimental, conceptual, avant-garde, challenging, or highly artistic treatment.

### Subject First

When the source has a clear person, animal, flower, food, landscape feature, building, product, vehicle, or other emotionally legible subject, keep its newly illustrated form as the primary visual entry point unless the user requests stronger abstraction.

Protect recognizable silhouette, expression, gesture, attractive proportions, successful source light, elegant contour, meaningful color relation, and intentional framing. Simplify identity when likeness is not requested, but do not degrade faces, hands, anatomy, or defining object structure merely to appear expressive.

Do not let abstraction, negative space, material distress, typography, or conceptual devices make the subject less attractive merely to prove authorship.

Keep these boundaries hard:

- Follow explicit user constraints.
- Use the supplied photo only as a reference.
- Do not reproduce, embed, crop, collage, trace, or retain photographic pixels or photorealistic regions.
- Keep the final image entirely original illustration, paper, and typography.
- Apply `单色块模式` exactly when explicitly triggered.

Do not treat minimalism, asymmetry, ambiguity, or irregularity as automatic correctness. Remove an element only when it lacks a distinct visual or expressive function; retain necessary density when density carries the source or tension.

## Source Handling

- Treat a supplied photo plus a transformation request as consent to use image generation.
- Ask for the photo only when the required source is missing.
- Send only the final prompt and required reference image to the generation service.
- Do not browse for, share, save, commit, or upload the source elsewhere.
- Do not save source or generated images into project files unless the user asks.

## Layer 1 — Read the Photograph

Build a compact internal **Source Card** before composing:

- **Semantic nucleus:** the smallest subject, relationship, or event that gives the source meaning.
- **Core relationship:** one primary subject or at most two inseparable subjects and their relationship.
- **Subject appeal:** what makes the main subject attractive, expressive, elegant, warm, vivid, intimate, dramatic, or memorable.
- **Photographic event:** viewpoint, viewing distance, framing, crop, focus, blur, decisive moment, or off-frame continuation that shapes the source.
- **Spatial structure:** foreground, middle ground, background, depth compression, overlap, enclosure, direction, or scale relation worth preserving or transforming.
- **Dominant gesture:** the strongest gaze, lean, curve, diagonal, path, rhythm, convergence, or movement.
- **Light architecture:** source direction, value pattern, temperature, reflection, glow, shadow mass, haze, or edge loss.
- **Visual-weight and contrast map:** weight from area, darkness, saturation, faces, isolation, sharpness, texture, and edge pressure.
- **Native color atmosphere:** dominant hue family, temperature, value range, and meaningful minor color.
- **Material and weather:** water, snow, glass, foliage, stone, fabric, wind, rain, dust, or another behavior that can become paper-and-ink form.
- **Emotional residue:** what remains after factual description is removed.
- **Irreplaceable cue:** one accident, silhouette, interval, overlap, light event, gesture, or material fact that would make little sense unchanged in another photograph.
- **Negative-space opportunity:** a gap, corridor, enclosure, directional opening, absence, or pressure field that can become active composition.
- **Broad-appeal risk:** what could make the result confusing, harsh, overly sparse, overly distressed, gimmicky, weak, or less attractive than the source.

Choose two to four source anchors. Include the irreplaceable cue when it has visual value.

## Layer 2 — Build the Distillation Map

Assign source information to five actions:

- **Preserve:** retain the semantic nucleus, essential relationship, dominant gesture, subject appeal, successful source light, and source singularity.
- **Compress:** merge repeated or secondary detail into a mass, interval, rhythm, or sparse trace.
- **Transmute:** turn selected space, light, weather, movement, or material into abstract shape, contour, field, edge, or negative space.
- **Remove:** discard clutter, redundant objects, realistic background information, and generic detail.
- **Invent:** add only source-consistent forms that clarify relationship, rhythm, eye path, balance, tension, or aesthetic coherence.

Preserve source specificity rather than the original photographic arrangement. Prefer subtraction and recomposition before invention. Never replace an unusual source relationship with a more conventional generic arrangement merely because it is easier to beautify.

## Layer 3 — Make the Aesthetic Decision

Draft two internal art directions that share the same source anchors but differ in one major spatial decision and one transformation decision. For each direction, resolve:

- one source-specific artistic proposition;
- one primary tension and its visible carriers;
- the dominant composition and eye path;
- the treatment of light, color, material, and text;
- the likely first-glance appeal;
- the main risk of becoming generic, weak, confusing, harsh, or less attractive than the source.

Choose the direction that best satisfies the Core Contract. Prefer the simpler direction only when it is also the stronger and more beautiful one.

### Intervention Strength

Use balanced intervention by default.

Choose restrained intervention when the source already has beautiful light, framing, atmosphere, color, elegant subject presence, or visual completeness. Choose assertive intervention only when strong movement, fragmentation, density, graphic geometry, or emotional intensity already exists in the source, or when the user explicitly asks for experimental or heavily stylized work.

### Proposition and Tension

Write one internal sentence stating what the artwork asks the viewer to feel, notice, or reconsider. Require it to alter a visible relationship such as scale, interval, direction, enclosure, rhythm, color, light, material, or visibility.

Choose one primary tension with strong source evidence and formal potential. For broad-audience work, prefer perceptually direct tensions such as stillness/movement, density/openness, near/far, light/shadow, warm/cool, order/irregularity, solid/empty, continuity/interruption, enclosure/openness, and weight/release. Use more conceptual tensions—presence/absence, smallness/vastness, intimacy/distance, shelter/confinement, familiarity/estrangement, complete/incomplete, legible/obscured, organic/geometric, or restraint/eruption—only when strongly supported by the source. Use at most one subordinate tension when it deepens rather than duplicates the primary one. Treat these as prompts for seeing, not presets.

Make each tension visible through at least two formal carriers. Do not invent psychological conflict merely because it sounds poetic.

### Metaphor and Interpretive Opening

Use a source-derived visual metaphor only when it is stronger than a direct formal relationship. Let an object, space, gesture, light behavior, or material fact shift function without becoming a universal-symbol cliché.

Leave one relationship deliberately unresolved through omission, interval, incomplete action, scale shift, obstruction, material disappearance, or a text–image gap. Keep the overall composition resolved and legible.

### Semantic Economy

Let proposition, tension, composition, light, color, material, and typography perform different roles: deepen, counterpoint, redirect, complicate, withhold, or resolve. Remove a device when another device already performs the same function more beautifully.

## Layer 4 — Direct the Visible Form

### Composition, Space, and Rhythm

- Preserve source orientation by default: use 3:5 portrait for portrait sources and 5:3 landscape for landscape sources unless the user requests another ratio.
- Recompose freely inside the canvas; do not copy the photographic framing.
- Shape negative space as active breathing room with contour, direction, pressure, interval, and meaning. Prefer a visually complete composition with generous breathing room over aggressively sparse emptiness.
- Establish one dominant focal relationship, clear figure–ground, readable balance, and an eye path with entry, encounter, movement, and release. Use asymmetry only when it improves vitality rather than merely appearing artistic.
- Use scale, overlap, occlusion, spacing, and directional breathing room to preserve or transform depth.
- Allow one productive disturbance—an abrupt crop, difficult interval, broken alignment, unusual margin, blockage, or extreme scale shift—only when it strengthens the source-derived tension without weakening first-glance beauty or subject appeal.
- Let density concentrate when the source requires force, crowding, speed, growth, or noise. Keep the rest subordinate enough to preserve hierarchy.

Check two-distance reading: the main subject, mass, hierarchy, color harmony, and eye path must feel attractive and clear at thumbnail scale; source tension, singularity, material behavior, and optional typography may reward closer viewing.

### Light Translation

Decide whether source light is structural. Protect attractive natural light before introducing stylized disruption. Translate it through exposed paper, value masses, ink density, edge loss, transparency, temperature, reflection, or interruption while preserving its flattering direction, tonal clarity, and emotional action without reproducing glossy depth.

Do not flatten a meaningful light event merely because the material world is flat. Flat material may still carry luminous or spatial relationships.

### Illustration and Material

Choose one primary illustration grammar and at most one compatible supporting grammar:

- cut-paper mass;
- dry-print silhouette;
- broken contour;
- rhythm field;
- fragment or drift structure.

Choose the grammar after identifying the source's visual problem. Prefer graceful simplification and controlled irregularity; do not distort the main subject merely to appear expressive. Avoid complete outlines, evenly rendered detail, realistic shading, polished vectors, cute cartoon, kawaii, anime, and children's-book sweetness unless explicitly requested.

Choose one plausible material world—cut paper, dry print, contour and paper, or limited-ink risograph-like printing. Let grain, ink bite, fiber, broken coverage, and registration behavior obey that world. Keep material texture subordinate to subject, composition, and color harmony; use irregularity as evidence of pressure, movement, disappearance, or contact, not as generic zine decoration.

Choose an edge treatment only when an edge has structural work to do. Allow a torn-fiber edge, narrow neutral layering, stippled dissolution, source-derived marks, or a natural illustrated contour. Remove the treatment when it attracts more attention than the subject relationship.

### Color Decision

Judge hue, value, chroma, area, adjacency, material, and eye-path role together.

In the default mode, choose between:

- **Chromatic silence:** use paper and neutral or subdued inks when an added accent would weaken the source's beauty or light structure.
- **Structural accent:** use one exact rich, clean print hue as focal entry, counterweight, bridge, directional cue, or rhythm. Choose by source resonance first, analogous harmony second, temperature bridge third, and restrained complementary counterpoint only when needed. Derive its contour, placement, or repetition from the source.

Prefer harmonious, natural-looking chroma over acidic, fluorescent, harsh, or arbitrarily fashionable color. Use strong complementary contrast only when clearly justified by the source or explicitly requested.

Use a distributed accent only when the source contains a credible repeatable supporting element. Vary scale, interval, orientation, and absence; never create confetti or an even decorative border.

When the request contains the exact trigger `单色块模式`, use exactly:

1. the natural paper tone;
2. one neutral ink system for every non-color form and any text;
3. one contiguous, opaque, fully saturated color field derived from the semantic nucleus, dominant gesture, or strongest figure–ground opportunity.

Do not split the saturated field into echoes or introduce supporting chromatic tints. Make the field the visual entry or central spatial idea, never a detached swatch.

### Typography Decision

Use no text by default. Add typography only when it contributes a relationship the image cannot carry as well alone.

Choose one role:

- **Countervoice:** add source-specific language that complicates rather than explains the image.
- **Spatial structure:** use type as rhythm, interval, boundary, interruption, or architectural form.

Preserve user-supplied wording exactly. Otherwise derive wording from a concrete source cue, spatial relation, material event, or genuine countervoice. Avoid generic poetic captions and text that names a mood already visible. Verify spelling and legibility in the generated result; remove text when silence is stronger.

## Layer 5 — Compile and Generate

Compile only instructions that can become visible pixels. Translate aesthetic judgment into proportion, interval, hierarchy, rhythm, negative-space shape, light behavior, hue/value/chroma relationships, material behavior, edge, and typographic geometry.

Write four compact prompt sections:

1. **Aesthetic proposition and composition:** tension, visible formal consequence, canvas, focal relationship, active negative space, eye path, and interpretive opening.
2. **Distilled source:** preserved anchors, irreplaceable cue, transformations, omissions, invented source-consistent forms, spatial structure, and light translation.
3. **Art direction:** illustration grammar, material world, edge decision, color mode, exact hue when used, and typography decision.
4. **Reproduction and boundaries:** tactile flat print behavior, emotional temperature, source-specific anti-template direction, and hard exclusions.

Always include:

```text
Do not reproduce, embed, crop, collage, trace, or retain photographic pixels or photorealistic regions from the reference.
The final image must contain original illustration, paper, and typography only.
```

Generate by default using the supplied photo as the only visual reference. Stop at prompt-only only when the user explicitly asks.

## Layer 6 — Inspect and Correct

Inspect the generated image as an artwork, not as a checklist response. Review it at thumbnail and normal scale:

- Is it visually compelling before explanation?
- Is there an immediately recognizable and attractive visual entry point?
- Does the main subject remain clear, graceful, and emotionally readable?
- Does the source spirit and one irreplaceable cue survive?
- Is the primary tension visible without explanatory text?
- Do composition, space, light, color, material, and text form one visual world?
- Is one focal relationship clearly dominant?
- Does any signature device look transferable unchanged to another photo?
- Is there visual noise, passive emptiness, generic zine styling, or an element whose removal improves the whole?
- Are the dominant colors harmonious, and does the negative space feel like breathing room rather than emptiness?
- Is the work understandable and appealing without reading the rationale?
- If the work is dense, is the density necessary and hierarchically controlled?

Regenerate at most once when a material failure is visible. Correct only the dominant failure: source loss, weak composition, flattened light, decorative color, generic abstraction, incompatible material, failed text, passive emptiness, or overdesign.

## Broad Appeal Gate

Before returning, inspect the image as if the viewer knows nothing about the design concept:

- Does the subject or defining relationship read immediately?
- Is the subject attractive and emotionally legible?
- Does the composition feel balanced without becoming mechanically centered?
- Are the dominant colors harmonious at first glance?
- Does breathing room support rather than weaken the composition?
- Are abstraction, texture, edge effects, and typography subordinate to the whole?
- Would removing one unusual effect make the image prettier or clearer?
- Would a viewer remember the subject or atmosphere before remembering the effect?

If conceptual sophistication and immediate appeal conflict, prefer immediate appeal unless the user explicitly requests a challenging artistic result.

## Authorial Residue Gate

After broad appeal is secure, preserve one quieter second layer: a source-specific asymmetry, interruption, omission, material irregularity, tension, or unresolved relation. One is enough. Do not force poetic residue when it weakens the image.

## Hard Avoids

Avoid photo fragments, photorealistic regions, tracing, rotoscoping, literal full-scene copying, subject degradation in the name of abstraction, distorted faces or hands, generic abstract motifs, arbitrary dots or grids, unsupported symbols, universal-symbol clichés, random ambiguity, visual confusion presented as sophistication, forced ugliness, forced asymmetry, empty-for-the-sake-of-minimalism composition, multiple competing material effects, decorative aging, generic ripped rectangles, sticker outlines, fuzzy halos, tape, dense scrapbooking, multiple competing bright hues, acidic or fluorescent color without source justification, passive blank space created only by shrinking the subject, generic poetic captions, commercial advertising hierarchy, logos, CTA, glossy mockups, hard 3D shadows, cinematic depth of field, neon, fashion-editorial polish, and watermarks.

## Output

Return:

```markdown
**生成图**

![Scene Distillation Zine poster](absolute-image-path-or-rendered-image)

**创作想法**

[用 1–3 句中文先说明为什么整体更漂亮、清晰和完整，再说明来源张力与最重要的视觉转化；不披露生成提示词。]

**艺术指导**

- 来源与张力：[保留的来源精神及其形式承载]
- 构图与光线：[视觉层级、负空间、眼动和光线转译]
- 材料、色彩与文字：[选择、功能及有意省略]
```

If the image renders without a local path, show it normally. Do not reveal the generation prompt unless the user explicitly requests it.
