# Quality Gates

Use the audit as a rejection aid, not as a substitute for visual inspection. Metrics cannot determine photographic taste or semantic truth alone.

## Hard failures

Reject before delivery when any of these occurs:

- input and output paths are identical;
- the recipe contains an unknown or forbidden operation;
- local face or body geometry can change;
- a source-pixel repair is unconfirmed, oversized, out of bounds, samples its own target, or exceeds the cumulative area limit;
- crop plus rotation-safe trimming retains less than 90% of source area;
- rotation exceeds 3 degrees;
- perspective correction is requested with people present, displaces a corner by more than 5%, or retains less than 90% source area;
- a creative effect lacks explicit authorization and acknowledgment;
- the source profile or bit depth cannot be handled without silent degradation;
- the output would require invented semantic content or missing detail.

## Soft failures

Use source-relative thresholds rather than absolute beauty targets:

- highlight clipping increases beyond `max_highlight_clip_delta`;
- shadow clipping increases beyond `max_shadow_clip_delta`;
- protected-region high-frequency energy falls below `min_texture_ratio` of the source;
- protected skin mean hue moves beyond `max_skin_hue_shift_degrees` without source-supported colored light;
- gradient energy around a local-mask boundary exceeds `max_mask_halo_ratio` of the source boundary;
- extreme saturation expands materially beyond the source;
- visual review finds pasted-on subjects, plastic skin, false detail, color contamination, obvious masks, or an AI-generated appearance.

## Safe rerender

When `--auto-safe` is active and the first render has only soft failures:

1. multiply tone, color, local, detail, and creative-effect amplitudes by a conservative safety factor;
2. preserve the composition and hard contract unchanged;
3. render and audit once more;
4. accept only a passing result;
5. record `safety_adjusted: true` in the applied recipe and audit.

Do not continue iterating automatically. If the second render fails, leave the requested output absent and report the causes.

## Required visual review

Inspect the final preview at full view and at meaningful detail scale. Check:

- immediate photographic readability;
- subject-background light and color coherence;
- identity and natural inter-person skin differences;
- skin, fabric, masonry, foliage, water, mist, and other meaningful texture;
- halos, seams, posterization, banding, clipping, and excessive color;
- crop integrity, horizon, architecture, and protected subject edges;
- whether style supports rather than replaces the source.
