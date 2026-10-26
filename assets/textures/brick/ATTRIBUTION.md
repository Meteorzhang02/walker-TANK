# Texture credits — red_bricks_04

| Field | Value |
|---|---|
| Asset | Red Bricks 04 (`red_bricks_04`), Poly Haven |
| Source URL | https://polyhaven.com/a/red_bricks_04 |
| Author | Rob Tuytel |
| Licence | CC0 (Poly Haven licence: no credit required; recorded for course provenance) |
| Date checked | 2026-10-25 |
| Resolution / format | 1K PNG, downloaded one map at a time (not the .blend package) |

| File | Role | Sampled as |
|---|---|---|
| `red_bricks_04_diff_1k.png` | brick colour (sRGB) | colour, `source_color`, in `shaders/brick_surface.gdshader` |
| `red_bricks_04_rough_1k.png` | roughness, stored linearly | data, no `source_color`, in `shaders/brick_surface.gdshader` |
| `red_bricks_04_nor_gl_1k.png` | tangent-space normal map, **OpenGL convention (`_nor_gl`)**, which Godot expects | only in the Step 4 scratch StandardMaterial3D (not used by the game's materials) |

Not downloaded: AO, AO/Rough/Metal, Displacement, Normal (DX).
