# CHANGE-BRIEF — Assignment 5: hit flash shader and brick surface materials

Written and committed **before** either shader exists and before the first prompt to Claude Code (date: 2026-10-27). This original is kept as written; later changes go in *Revisions* at the end, each dated, never by editing the text above.

Authorship: the decisions below are mine. The document was drafted with Claude (claude.ai chat) from those decisions and from project facts I collected with grep; the colour-line form, `flash_strength`, pure red and D = 0.5 s were Claude's suggestions, which I accepted (recorded in FRICTIONAL.md and SOURCES.md). The pixel and hint-experiment predictions in sections 3 and 4 I computed by hand, except the worked example P1 @ 0.5, which Claude showed as the method.

Project note: `project.godot` is at the repository root, so the assignment's `godot/` paths map to the root (`godot/shaders/` → `shaders/`, `godot/tests/` → `tests/`). All tests run through `scripts/run-test.sh` (Windows / Git Bash version, `--path .`).

Baseline before any A5 change (commit c4a1f84, 60 fps): `check_a3_assets.gd` 18/18 PASS, exit 0; `test_sound_triggers.gd` 8/8 PASS, exit 0 (with a pre-existing "5 resources still in use at exit" / ObjectDB leak message at shutdown, not a SHADER or SCRIPT ERROR).

---

## 1. The state

- **What the effect communicates:** YunqiZ (the player's tank) has just taken a non-fatal hit.
- **Why the player needs it:** the health bar sits in a corner of the HUD, but in a fight the player is looking at the tank. The existing white `_flash()` lasts only 0.15 s and reads as "something happened", not "you lost health". A red tint that fades over half a second says "you were hit" on the tank itself, where the player is already looking.
- **Where the state lives:** `scripts/tank.gd`, `take_damage()` (lines 163–175) emits `damaged(tank, amount)` after a non-fatal hit. The state "recently hit" begins at that signal and holds for D = 0.5 s (section 2).
- **Facts that shape the rules:**
  - `take_damage()` sets `invuln_left = 0.3`; hits inside that window are ignored and emit nothing (lines 164–165).
  - A fatal hit calls `die()` and returns **before** `damaged` is emitted (lines 168–170).
  - `_flash()` (lines 201–203) already tweens `modulate` to 2.2 and back to `tint` in 0.15 s. This existing white flash is A2 behaviour and stays unchanged; the red tint is added on top of it.
  - Player and enemies all run `tank.gd` (`player.gd` extends it; enemies get `tint = ENEMY_TINT`, `main.gd` lines 79–90). The player's `tint` is `Color(1, 1, 1)` (`tank.gd` line 23).

## 2. Effect specification

### The shader

| Item | Value |
|---|---|
| Path | `shaders/hit_flash.gdshader` (hand-written by me) |
| shader_type | `canvas_item` |
| render_mode | none |
| Object | YunqiZ's `hull` and `turret` Sprite2D nodes (`tank.gd` lines 54–59), sharing **one** ShaderMaterial instance. Enemies get no ShaderMaterial. |
| Sampler uniforms | none (the sprite texture arrives in `COLOR`) |

| Uniform | Type | Hint | Default | Set by |
|---|---|---|---|---|
| `hit_amount` | float | `hint_range(0.0, 1.0)` | 0.0 | the driver, from the player's `damaged` / `destroyed` signals and `reset_full()` |
| `flash_color` | vec4 | `source_color` | `vec4(1.0, 0.0, 0.0, 1.0)` | not driven; the material |
| `flash_strength` | float | `hint_range(0.0, 1.0)` | 0.6 | not driven; the material |

### The colour line

```glsl
COLOR.rgb = mix(COLOR.rgb, flash_color.rgb, hit_amount * flash_strength);
```

Alpha is left unchanged, so transparent sprite pixels stay transparent. With `flash_strength = 0.6` the tank's detail stays visible even at `hit_amount = 1.0`. Pure red has channels of only 0 and 1, which sRGB decoding leaves unchanged, so the predictions do not depend on whether `source_color` converts the value in this 2D, non-HDR shader.

### Observable rules

1. **Begin:** on `damaged` from the player, `hit_amount` is 1.0 in the first frame sampled after the signal.
2. **End:** it falls linearly from 1.0 to 0.0 over **D = 0.5 s** of game time (± one frame period: 33.3 ms at 30 fps, 16.7 ms at 60, 6.9 ms at 144), the same game time at 30, 60 and 144 fps. Then it stays at 0.0.
3. **Retrigger:** a new `damaged` during the fade **restarts** it at 1.0. Because of the 0.3 s invulnerability, a retrigger can only happen between 0.3 s and 0.5 s after the previous hit; D > 0.3 s so the rule is reachable.
4. **Time scale:** the duration is measured in **scaled** time (`delta`). The game never changes `Engine.time_scale` (grep: no `time_scale` in `scripts/`).
5. **Pause:** the tank is under `world` (`PROCESS_MODE_PAUSABLE`, `main.gd` line 50), so while the tree is paused `hit_amount` holds its current value; the fade resumes on unpause.
6. **State ends early:** on `destroyed`, `hit_amount` goes to 0.0 at once (the dead tank keeps the grey `die()` look). After `reset_full()` it is 0.0.
7. **Instances:** only YunqiZ has the material; the three enemies never show the effect. Hull and turret share one material, so they always show the same value.

### Boundaries

Collision, movement, input, `take_damage()` / `die()` logic and timings (including `invuln_left` and `_flash()`), the HUD, audio, the existing tests and their expectations, the enemies, the covers and every other object stay unchanged. Presentation code reads game state (signals) and never writes it.

### Evidence split

| Rule | Check |
|---|---|
| 1, 2, 3 | Headless test at 30/60/144 fps through the real game loop: sample `hit_amount` every frame from a node with high `process_priority`; first value, last value, duration, retrigger. |
| 4 | Headless: duration measured in game time across the three frame rates. |
| 5 | Headless: pause the tree mid-fade and check the value holds for several frames, then resumes. |
| 6 | Headless: fatal hit → 0.0; after `reset_full()` → 0.0. |
| 7 | Headless: enemies' sprites have no ShaderMaterial; hull and turret return the same material object. |
| Uniform names / types | Headless: `get_shader_uniform_list()`; defaults read from the shader source text. |
| The look | **Human:** in-engine captures at the controlled values (section 3) and normal play. |

## 3. Controlled inputs and predicted values

Output is unshaded: no Light2D or CanvasModulate in the project (grep found none). `hdr_2d` is not enabled (not set in `project.godot`; default off), so 2D blending is not in linear space and the arithmetic is on the stored 8-bit values. Captures are taken with the player's `modulate` at `tint` = (1, 1, 1), i.e. not during `_flash()`, and with **YunqiZ facing right (slot 0, `hull_right.png`, no flip)**, with the driver's processing stopped so the set value is the one drawn.

Pixels were chosen in flat areas (3×3 neighbourhood within 6 levels, fully opaque; found with a PIL script) because the sprites are drawn at scale 0.5 and filtered.

| Pixel | Where | Source RGB (0–255) |
|---|---|---|
| P1 | olive hull body, `hull_right.png` (99, 50) | 87, 97, 40 |
| P2 | dark track, `hull_right.png` (59, 109) | 16, 16, 16 |

Mixing weight t = `hit_amount × flash_strength` = `hit_amount × 0.6`. Per channel: out = src × (1 − t) + flash × t, with flash = (255, 0, 0).

| `hit_amount` | t | P1 | P2 |
|---|---|---|---|
| 0.0 | 0 | (87, 97, 40) | (16, 16, 16) |
| 0.5 | 0.3 | (137, 68, 28) | (88, 11, 11) |
| 1.0 | 0.6 | (188, 39, 16) | (159, 6, 6) |

Working:
- P1 @ 0.5: R = 87 × 0.7 + 255 × 0.3 = 60.9 + 76.5 = 137.4 → 137; G = 97 × 0.7 = 67.9 → 68; B = 40 × 0.7 = 28.0 → 28.
- P1 @ 1.0: R = 87 × 0.4 + 255 × 0.6 = 34.8 + 153 = 187.8 → 188; G = 97 × 0.4 = 38.8 → 39; B = 40 × 0.4 = 16.0 → 16.
- P2 @ 0.5: R = 16 × 0.7 + 255 × 0.3 = 11.2 + 76.5 = 87.7 → 88; G = B = 16 × 0.7 = 11.2 → 11.
- P2 @ 1.0: R = 16 × 0.4 + 255 × 0.6 = 6.4 + 153 = 159.4 → 159; G = B = 16 × 0.4 = 6.4 → 6.

Measured values within ±2 of the prediction are treated as matching (8-bit quantisation and the 0.5 sprite-scale filtering); larger differences are findings.

Background: the effect changes the tank, not the ground, so contrast is not the main signal. The ground RGB behind the tank is measured in the first in-engine capture and added as a revision.

## 4. The hint experiment

- `tools/make_hint_png.gd` writes a 3×1 PNG with greys 64, 128, 192. Imported Lossless, no mipmaps.
- `shaders/hint_experiment.gdshader`, `render_mode unshaded`, two samplers bound to the same file: one `source_color, filter_nearest`, one `filter_nearest` only; a bool uniform picks which one writes `ALBEDO`.
- Two materials (bool true / false) on two quads facing the camera; WorldEnvironment with Linear tonemap, exposure 1.0, glow, fog and adjustments off. Renderer: Forward+.

Why: the output is sRGB-encoded for display. With `source_color` the sample is decoded from sRGB to linear first, so decode and encode cancel and Quad A shows the file's values. Without it the stored value is treated as linear and still encoded, so Quad B is brighter.

Quad B: x = value / 255; y = 1.055 · x^(1/2.4) − 0.055 (x > 0.0031308); displayed = round(255 · y).
- 64: x = 0.250980, x^(1/2.4) = 0.5622, y = 0.5381, × 255 = 137.2 → 137
- 128: x = 0.501961, x^(1/2.4) = 0.7504, y = 0.7366, × 255 = 187.8 → 188
- 192: x = 0.752941, x^(1/2.4) = 0.8885, y = 0.8823, × 255 = 225.0 → 225

| Band (file value) | Quad A: with `source_color` | Quad B: without |
|---|---|---|
| 64 | 64 | 137 |
| 128 | 128 | 188 |
| 192 | 192 | 225 |

**Quad A shows the file's values unchanged**, because decoding at the sample and encoding at the output cancel. Measured values within ±2 count as matching.

## 5. Material plan (textured shader)

- **Object:** `cover_wall` in `scenes/asset_room_3d.tscn` (A3), plus a second `cover_wall` instance beside it so the two materials can be compared side by side. The first material goes behind the importer's per-material **Use External** setting; how the second instance gets its material (an override on that instance) is confirmed when built and recorded as a revision.
- **Lighting I judge under:** the single light already in `scenes/asset_room_3d.tscn` (type and settings as in the .tscn, recorded in MATERIALS.md by the audit). SSAO off when judging roughness.
- **Shader:** `shaders/brick_surface.gdshader`, `shader_type spatial`, hand-written. Albedo from the colour texture times tint and brightness; roughness from the data texture times `roughness_scale`; UVs scaled by `uv_scale`.

| Texture | Source | What its numbers mean | Sampled as | compress/mode | compress/normal_map | mipmaps/generate |
|---|---|---|---|---|---|---|
| `assets/textures/brick/red_bricks_04_diff_1k.png` | Poly Haven, Rob Tuytel, CC0 | sRGB colour of the bricks | colour, `source_color` | VRAM Compressed | Disabled | On |
| `assets/textures/brick/red_bricks_04_rough_1k.png` | same set | roughness 0–1, stored as is (data) | data, no `source_color` | VRAM Compressed | Disabled | On |
| `red_bricks_04_nor_gl_1k.png` | same set | tangent-space normal, OpenGL convention | only in the Step 4 scratch material | VRAM Compressed | Enable | On |

| Uniform | Type | Hint / range | Default | Group | Expected change across the range |
|---|---|---|---|---|---|
| `albedo_tint` | vec4 | `source_color` | (1, 1, 1, 1) | Colour | white leaves the bricks as photographed; darker or warmer tints recolour them |
| `brightness` | float | `hint_range(0.0, 2.0)` | 1.0 | Colour | 0 is black; 2 is twice as bright and starts to wash out |
| `roughness_scale` | float | `hint_range(0.0, 1.0)` | 1.0 | Surface | 0 makes the wall glossy with sharp highlights; 1 keeps the map's matte brick |
| `uv_scale` | float | `hint_range(0.5, 8.0)` | 2.0 | Surface | low values make bricks huge; high values make them tiny and repetitive |

**Two materials:** `materials/cover_wall_intact.tres` (defaults above) and `materials/cover_wall_damaged.tres` (`albedo_tint` a dusty grey-brown, `brightness` 0.7), both using `shaders/brick_surface.gdshader`. They differ in two values because cover is not permanent in walker-TANK: the damaged stage reads darker and dustier than intact cover.

## 6. Predicted failure cases

| # | Failure | Check that catches it |
|---|---|---|
| 1 | All tanks flash when YunqiZ is hit (shared material, or the material put on enemies). | Headless: enemies have no ShaderMaterial; human check in play. |
| 2 | The flash lasts a different game time at 30 and 144 fps (frame counting instead of `delta`). | Headless duration at three frame rates. |
| 3 | A retrigger during the fade is ignored instead of restarting. | Headless retrigger assertion. |
| 4 | The roughness map is sampled with `source_color`, so its values are wrongly decoded. | Material test reads the hints from the source; the source_color mutation; the interface sweep. |
| 5 | The driver sets a uniform name the shader does not declare; `set_shader_parameter` raises no error and nothing changes on screen. | Uniform-list assertion and the rename mutation. |

## 7. Questions

- **Renderer:** not set in `project.godot`, so Godot's default Forward+ (to confirm in Project Settings → Rendering → Renderer). Forward+ rules out none of the listed features: decals and compute shaders need Forward+ or Mobile, and VoxelGI, SDFGI and SSIL are only missing in Mobile and Compatibility.
- **Colour arriving in fragment():** for this canvas_item shader, `COLOR` holds the sprite texture's colour multiplied by the vertex colour, which carries the node's `modulate` (my reading of the docs, to confirm in Use It). `texture(TEXTURE, UV)` would give the raw texture colour without `modulate`, so the enemy tint and the existing white `_flash()` would be lost on any sprite using it.
- **Frame-counting version:** a version that counted 30 frames (0.5 s at 60 fps) would last 1.0 s at 30 fps, 0.5 s at 60 fps and about 0.21 s at 144 fps.
- **Default vs current value:** the default lives in the shader source (the uniform's initialiser in `hit_flash.gdshader`); the current value lives in the ShaderMaterial resource (set with `set_shader_parameter`). Two objects sharing one material share one current value, which is why hull and turret share it and enemies get none.
- **Does hint_range clamp a value set from code?** Prediction: no. `hint_range` shapes the Inspector slider only; `set_shader_parameter("hit_amount", 2.0)` reaches the shader as 2.0, giving t = 1.2, so the mix extrapolates past the flash colour and the display then clips each channel to 0–255. Checked in Use It with a capture at 2.0.

## Revisions

**2026-10-27 — cover_wall has no UVs; import settings applied (written before shader 2).**

`tools/inspect_cover_wall.gd` (output in `docs/a5/step3-info.txt`) shows `cover_wall.glb` has two surfaces: surface 0 `M_Brick` (24 vertices, the wall body) and surface 1 `M_BrickDark` (48 vertices, cap and base), and **neither has a UV array**. Changes to section 5:

- `shaders/brick_surface.gdshader` projects the textures from **object-space position** (box projection: the largest component of the object-space normal picks the plane, X → ZY, Y → XZ, Z → XY), not from `UV`. The A3 asset stays unchanged.
- `uv_scale` now means texture repeats per metre: `hint_range(0.1, 4.0)`, default 0.5 (one repeat every 2 m, so the 4 m wall shows two). Low values give huge bricks; high values give tiny, repetitive bricks.
- The brick shader goes on surface 0 (`M_Brick`) only. Surface 1 (`M_BrickDark`) keeps its imported flat colour on both walls.
- The three brick PNGs were imported as Lossless, no mipmaps, normal map Detect, `detect_3d/compress_to` = VRAM. They are now set to the section 5 values, with `detect_3d/compress_to` disabled so the editor cannot change them silently when they are used in 3D. The hint-experiment PNG needs the same: Lossless, no mipmaps, `detect_3d/compress_to` disabled, or using it in 3D would switch it to VRAM Compressed and change its grey values.
- Two walls: `CoverWall` gets `materials/cover_wall_intact.tres` on `M_Brick` through the importer's **Use External**. A new second instance, `CoverWall2`, gets `materials/cover_wall_damaged.tres` as a surface material override on surface 0.

