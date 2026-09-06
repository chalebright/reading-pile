# Chimney Projection Mapping — Blender Stand-in Rig

Previz project for a projection-mapping installation on a chimney. This is the
starting point: no real survey data yet, so the geometry is a placeholder
cylinder/frustum and the "steam" is left out entirely — just the stack.

## What's here

`chimney_projection_addon/` is a small Blender add-on (not a one-off script)
because the parameters here — real-world height/radius, taper, ring
positions, UV seam, media aspect — are exactly the things that will change as
real measurements and content come in. The add-on lets you re-generate the
rig from the panel instead of re-running a script by hand each time.

## Install

1. Zip the `chimney_projection_addon/` folder (or symlink it into your
   Blender `scripts/addons` directory).
2. Blender → Edit → Preferences → Add-ons → Install..., pick the zip, enable
   "Chimney Projection Mapping Stand-in".
3. Open the 3D Viewport sidebar (`N`) → **Projection** tab.

## Workflow

1. **Media** — set `media_width`/`media_height` to your content canvas
   (defaults to 572×2429, matching what you're using now). This drives the
   demo geometry's proportions so the UV isn't stretched.
2. **Rough Geometry** — enter your rough height/radius. Click **Match Radius
   to Media Aspect** to size the stand-in so its unwrapped circumference
   matches the media aspect ratio exactly (no stretch) at that height.
   `top_radius_factor` = 1.0 is a straight cylinder (today's stand-in);
   drop it below 1.0 later once you have a real taper profile to add a
   frustum instead.
3. **Coupling Rings** — `ring_count` adds evenly spaced edge loops up the
   stack and tags each one as a vertex group (`ring_1`, `ring_2`, …). These
   mirror the visible pipe-section joints in the reference photos, so you
   can mask, deform, or split content per section later without re-modeling.
4. Click **Build / Rebuild Chimney Stand-in**. Re-run any time after
   changing a parameter — it replaces the existing mesh/material in place.
5. **UV Seam Rotation** — nudge this to move the seam to the back of the
   stack, away from the primary camera/projector angle.
6. **Export UV Template** — writes a PNG at the media resolution showing the
   unwrap, so whoever is producing the visuals has an exact canvas template
   to paint/animate against.
7. Load a still or movie into `media_filepath` (or set it directly on the
   `ProjectionMedia` image node in the material) and click **Sync Timeline
   to Media** to set the scene frame range/fps from it.

## Material

The stand-in material is Emission-based, not a lit Principled BSDF — the
content is projected light, not a surface reflecting scene lighting, so it
should preview as self-illuminated. A `Mapping` node sits between UVs and
the image texture if you need to nudge/scale content by hand beyond what the
UV unwrap already gives you.

## Once real measurements exist

- Update `chimney_height_m`, `base_radius_m`, `top_radius_factor` (and
  `ring_count`/spacing if the real joints aren't evenly spaced) and rebuild.
- If the real profile isn't a simple frustum, swap `geometry.build_chimney_mesh`
  for a lofted/photogrammetry-derived mesh — the UV authoring approach
  (per-ring V coordinate, per-segment U coordinate) still applies, it just
  needs non-uniform ring heights/radii instead of the linear interpolation
  used for the placeholder.

## Ideas for later (not built yet)

- Per-section (per-ring-group) materials/timelines so different stack
  sections can run independent content instead of one continuous texture.
- A calibration camera matched to the real projector's lens/position, to
  preview keystone and blending before going on site.
- Multi-projector edge-blend masks if the final install needs more than one
  projector to cover the full height/wrap.
- Swapping the placeholder cylinder for a photogrammetry or laser-scanned
  mesh once you can get real measurements of the chimney.
