# Scene Strategies

Choose one hierarchy before choosing local edits. All people remain protected regardless of hierarchy.

## Portrait-led and portrait-only

- Prioritize identity, natural skin within the source light, eyes as existing optical detail, hair, garment texture, and believable facial dimensionality.
- Balance the background to support the person without turning it into a disconnected plate.
- Apply detailed retouching only when the face resolution supports it.
- Permit small transient-blemish correction at high confidence. Preserve moles, freckles, scars, wrinkles, birthmarks, and lasting asymmetry.
- For an allowed blemish repair, sample nearby skin with the same texture and light; record the visual evidence and never sample across a facial feature or shadow boundary.
- Neutralize eye whites or teeth only slightly and only from captured pixels. Never change eye shape, eye size, teeth geometry, catchlights, or facial structure.
- Use local exposure and chroma correction for under-eye or uneven facial shadow before smoothing.

## Landscape-led and landscape-only

- Prioritize light structure, atmospheric depth, sky-ground balance, water and foliage relationships, material readability, and the scene's actual weather.
- Treat a small person as a protected scale or narrative element, not an automatic portrait target.
- Recover only recorded highlight and shadow information. Do not create clouds, stars, foliage, reflections, mist, or distant detail.
- Use dehaze and clarity sparingly so atmospheric perspective, rain, fog, and soft distance remain believable.
- Protect known colors such as vegetation, water, stone, painted architecture, and culturally significant surfaces from indiscriminate saturation.
- Repair sensor dust, hot pixels, or confirmed capture damage only with a nearby patch from the same sky, wall, water, foliage, or material plane; never clone away a scene object.

## Balanced environmental portrait

- Treat person and environment as co-authors of the image.
- Build one shared light and color logic before applying region-specific refinement.
- Keep the face readable without making it brighter, cleaner, sharper, or warmer than the environment can support.
- Preserve environmental color spill on skin and clothing while preventing unhealthy or accidental casts.
- Use local contrast and color separation instead of excessive background blur or artificial relighting.

## Multiple people

- Protect every detected person equally from identity and geometry changes.
- Retouch only the explicit or compositionally primary people in detail.
- Apply basic exposure and color harmony to secondary people.
- Preserve natural differences among skin tones; never normalize everyone to a single target color.
- Never rank importance from age, gender, ethnicity, or skin tone.

## Region-mask policy

- Prefer broad, feathered, source-supported masks over tight semantic cutouts.
- Use normalized ellipses or polygons for people, faces, garments, buildings, and bounded scene regions.
- Use linear or radial gradients for sky, ground, light falloff, and broad atmosphere.
- Combine a geometric mask with a color gate when geometry alone would affect unrelated pixels.
- Create protected masks before smoothing, sharpening, HSL routing, or strong local exposure.
- If a boundary cannot be placed confidently, reduce the edit or keep it global and mild.
