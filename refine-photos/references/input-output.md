# Input and Output

## Supported source path

- Process one JPEG, PNG, or TIFF per invocation.
- Treat a 16-bit TIFF as supported only when `tifffile` can read it and the embedded profile is sRGB-compatible. Refuse an unhandled wide-gamut profile rather than silently misinterpret it.
- Route RAW files through RawTherapee, darktable, LibRaw, or another reliable developer to a 16-bit TIFF. Never use the embedded JPEG preview as the editing source.
- Preserve source dimensions except for confirmed composition correction. Do not upscale unless explicitly requested.

## Color management

- Read the embedded ICC profile when present.
- Convert supported 8-bit input into an sRGB working representation through LittleCMS, edit in floating-point linear light where appropriate, and convert back to the source profile when possible.
- If no profile exists, assume sRGB and record that assumption in the audit.
- Keep an sRGB profile on review previews.
- Preserve supported 16-bit TIFF depth. Do not reduce a 16-bit TIFF to 8-bit silently.

## Metadata and privacy

Preserve ordinary photographic metadata when the output format supports it:

- capture time;
- exposure, aperture, ISO, focal length;
- camera and lens model;
- artist and copyright.

Remove by default:

- GPS and location metadata;
- camera and lens serial numbers;
- owner identifiers and maker notes that may contain private identifiers.

Set output orientation to normal, update dimensions, and identify `refine-photos` as processing software. Keep the applied recipe as a sidecar so the result is not represented as an untouched camera original.

## Output safety

- Never allow input and output paths to resolve to the same file.
- Refuse to overwrite an existing output unless the caller explicitly passes `--overwrite`.
- Write to a temporary sibling file and replace the requested output only after rendering and audit succeed.
- Name previews with `_preview` and final images with `_refined` unless the user gives another non-destructive path.
- Write `<output-stem>.recipe.json` and `<output-stem>.audit.json` next to the accepted image by default.
