# TEST-REPORT — Assignment 5: hit flash shader and brick surface materials

| | |
|---|---|
| **Source revision** | `3d48047` (`git rev-parse --short HEAD`). This report and the other A5 documents are uncommitted on top of it. The rerun below also rewrote `logs/test_hit_flash_{30,60,144}fps.log`; only the shutdown leak lines changed. |
| **Engine** | Godot 4.7.2 stable (`v4.7.2.stable.official.ed1daf0bf`, printed by every log) |
| **Renderer** | Forward+ (engine default; `project.godot` has no renderer key; I checked it in Project Settings → Rendering → Renderer, value `forward_plus`) |
| **OS / shell** | Windows 11, Git Bash. Every test runs through `scripts/run-test.sh` (headless, `--fixed-fps`, 120 s `timeout`, exits 1 if the log contains `SHADER ERROR` or `SCRIPT ERROR`) |
| **Spec** | [CHANGE-BRIEF.md](CHANGE-BRIEF.md), including its two dated *Revisions* |

The Assignment 3 report is kept unchanged at the end of this file ([below](#test-report--assignment-3-three-3d-assets)). The Assignment 2 report is in [docs/a2/TEST-REPORT.md](docs/a2/TEST-REPORT.md).

**Headless vs human.** A headless run uses a dummy renderer and draws nothing. Headless tests prove that the shaders parse, their uniforms are declared and driven, and the materials are wired. They never prove what the screen shows. Every section marked **HUMAN CHECK** comes from my own windowed run (capture tools in `tools/`, run by me) or my own playtest.

## Rerun at `3d48047` (2026-10-27), one command per call

| Command | Result | Exit | Log |
|---|---|---|---|
| `bash scripts/run-test.sh test_hit_flash.gd 30` | **50 passed, 0 failed** (frame period 0.03333 s, 205 samples) | 0 | [logs/test_hit_flash_30fps.log](logs/test_hit_flash_30fps.log) |
| `bash scripts/run-test.sh test_hit_flash.gd 60` | **50 passed, 0 failed** (0.01667 s, 397 samples) | 0 | [logs/test_hit_flash_60fps.log](logs/test_hit_flash_60fps.log) |
| `bash scripts/run-test.sh test_hit_flash.gd 144` | **50 passed, 0 failed** (0.00694 s, 933 samples) | 0 | [logs/test_hit_flash_144fps.log](logs/test_hit_flash_144fps.log) |
| `bash scripts/run-test.sh test_materials.gd 60` | **76 passed, 0 failed** | 0 | [logs/test_materials_60fps.log](logs/test_materials_60fps.log) |
| `bash scripts/run-test.sh check_tools_parse.gd 60` | **9 passed, 0 failed** | 0 | [logs/check_tools_parse_60fps.log](logs/check_tools_parse_60fps.log) |
| `bash scripts/run-test.sh check_a3_assets.gd 60` | **18 / 18 PASS** (`RESULT: PASS (0 failure(s))`) | 0 | [logs/check_a3_assets_60fps.log](logs/check_a3_assets_60fps.log) |
| `bash scripts/run-test.sh test_sound_triggers.gd 60` | **8 / 8 PASS** (`RESULT: 0 failed`) | 0 | [logs/test_sound_triggers_60fps.log](logs/test_sound_triggers_60fps.log) |

None of the seven logs contains `SHADER ERROR` or `SCRIPT ERROR`. At shutdown, `test_hit_flash` prints "13 / 16 / 14 ObjectDB instances were leaked" (at 30 / 60 / 144) and "5 resources still in use at exit". `test_sound_triggers` prints "22 ObjectDB instances" and "7 resources still in use". These are engine shutdown messages, not test failures (see Baseline).

---

## 1. Baseline (before and after)

| | `check_a3_assets.gd` @ 60 | `test_sound_triggers.gd` @ 60 |
|---|---|---|
| **Before A5** (commit `c4a1f84`, brief line 9) | 18/18 PASS, exit 0 | 8/8 PASS, exit 0, with "5 resources still in use at exit" |
| After Step 2 (`9217896`, [docs/a5/step2-output.txt](docs/a5/step2-output.txt)) | 18/18, exit 0 | 8/8, exit 0 (log: 18 ObjectDB, 5 resources) |
| After Step 3 (`97fdec6`, [docs/a5/step3-finish-b.txt](docs/a5/step3-finish-b.txt)) | 18/18, exit 0 | 8/8, exit 0 (log: 22 ObjectDB, 7 resources) |
| **After A5** (this rerun at `3d48047`) | **18/18 PASS, exit 0** | **8/8 PASS, exit 0** (22 ObjectDB, 7 resources) |

The pass counts are unchanged and neither test file was edited. **Finding:** the shutdown message in `test_sound_triggers` grew from 5 to 7 resources (and 18 to 22 ObjectDB instances) between `9217896` and `97fdec6`. It is still not a SHADER or SCRIPT ERROR, and the exit code is 0. Why it grew: TBD (not investigated).

## 2. Shaders parse

From `tests/test_hit_flash.gd` (all three rates, identical lines) and `tests/test_materials.gd`:

- `hit_flash.gdshader` loads, and `get_shader_uniform_list()` is non-empty, so the shader compiled. It reports `hit_amount` (type 3 float, hint 1 range `0.0,1.0,0.001`), `flash_color` (type 20 Color, hint 0) and `flash_strength` (float, range `0.0,1.0,0.001`).
- `source_color` is not visible in the uniform list (it reports the vec4 as a Color with hint 0), so the test checks it from the source text: `flash_color vec4 source_color = vec4(1.0, 0.0, 0.0, 1.0)`, `hit_amount ... = 0.0`, `flash_strength ... = 0.6`, `shader_type canvas_item`. All PASS.
- "shader declares every uniform the driver sets: hit_amount" PASS.
- `brick_surface.gdshader`: compiled, 6 uniforms, every source uniform in the compiled list. `hint_experiment.gdshader`: compiled, `render_mode unshaded`. All PASS ([logs/test_materials_60fps.log](logs/test_materials_60fps.log)).
- No `SHADER ERROR` in any of the seven logs.

**Mutations.** I made each mutation by hand, ran the test, then restored the file (restore diff empty). Output: [docs/a5/step2-output.txt](docs/a5/step2-output.txt) sections 3a and 3b.

| # | Mutation in `shaders/hit_flash.gdshader` | What the log shows | Exit | Log |
|---|---|---|---|---|
| 1 | delete the `;` after `flash_strength ... = 0.6` (line 5) | `SHADER ERROR: Expected a ';'.`, `ERROR: Shader compilation failed.`, 5 FAILs (uniform list empty, the three uniforms, driver-uniform check); `RESULT: 45 passed, 5 failed` | **1** | [logs/mutation1_semicolon_60fps.log](logs/mutation1_semicolon_60fps.log) |
| 2 | rename `hit_amount` → `hit_amt` (lines 3 and 8) | no shader error (the shader is valid). The driver prints `ERROR: hit_flash_driver: ... does not declare uniform 'hit_amount'`; 3 FAILs; `RESULT: 47 passed, 3 failed` | **1** | [logs/mutation2_rename_60fps.log](logs/mutation2_rename_60fps.log) |

Mutation 1 settled a question the agent could not answer in session 2: headless does report shader parse errors. Mutation 2 is brief failure case 5: `set_shader_parameter` on an undeclared name raises no error by itself. Here the driver's own check printed an `ERROR:` line and the uniform-list assertions failed, but that `ERROR:` line alone would not make the wrapper exit 1 (it only looks for `SHADER ERROR` / `SCRIPT ERROR`). The exit 1 comes from the test's FAILs.

## 3. Driver (`scripts/hit_flash_driver.gd`, attached in `scripts/main.gd` by one line)

`tests/test_hit_flash.gd` runs the real game loop and samples `hit_amount` every frame from a high-`process_priority` node. Results are the same at all three rates (50/50 each):

| Check (brief rule) | 30 fps | 60 fps | 144 fps |
|---|---|---|---|
| Before any hit | 0.0 | 0.0 | 0.0 |
| **Real shell hit:** enemy `try_fire()` spawns a shell that hits YunqiZ (`damaged` emitted, health 75) | PASS | PASS | PASS |
| Existing white `_flash()` still runs (modulate 2.2 at the signal) | PASS | PASS | PASS |
| Rule 1: **first** sampled frame after the hit | **1.0** | **1.0** | **1.0** |
| Rule 2: falls linearly on game time (1 − t/D) | PASS | PASS | PASS |
| Rule 2: **last** value 0.0, reached after **0.5000 s** game time (tolerance ± one frame) | 0.5000 s (± 0.0333) | 0.5000 s (± 0.0167) | 0.5000 s (± 0.0069) |
| Rule 2: stays 0.0 afterwards | 12 frames | 24 frames | 58 frames |
| Rule 5: pause mid-fade, value before pause | 0.6667 | 0.6333 | 0.6111 |
| Rule 5: holds on all 12 paused frames, falls again after unpause | 0.6667 → 0.5333 | 0.6333 → 0.5667 | 0.6111 → 0.5833 |
| Rule 3: **retrigger** lands after invulnerability | at 0.400 s (value before 0.2667) | at 0.400 s (0.2333) | at 0.403 s (0.2083) |
| Rule 3: first frame after retrigger | 1.0 | 1.0 | 1.0 |
| Rule 6: fatal hit → `destroyed`, no `damaged`; first frame after | 0.0 | 0.0 | 0.0 |
| Rule 6: 0.0 on every frame from `destroyed` through `reset_full()` (health 100) | PASS | PASS | PASS |
| Second retrigger after respawn restarts at 1.0, then full fade 0.5000 s | PASS | PASS | PASS |
| Rule 7: hull has the ShaderMaterial; hull and turret return the same material object; no enemy sprite has a ShaderMaterial (checked at start and end) | PASS | PASS | PASS |

Rule 4 (scaled time): the fade lasts the same 0.5000 s of game time at 30, 60 and 144 fps, so the driver does not count frames (brief failure case 2). Nothing in the project changes `Engine.time_scale`, so no run had a time scale other than 1.

Known limit (from the session-2 report, in my notes): `reset_full()` on a *living* tank mid-fade would not clear the value. The game only calls it after death, and rule 6 covers that path.

## 4. Controlled values — HUMAN CHECK

**How captured:** `tools/capture_hit_flash.gd` (written by Claude Code, session 5). I ran it windowed at 1280×720. It freezes the enemies, faces YunqiZ right (slot 0, `hull_right.png`, no flip, modulate = tint = (1,1,1)), stops the driver, sets `hit_amount`, waits for the frame to be drawn, saves `get_viewport().get_texture().get_image()`, and reads the value back. Printed output: [docs/a5/captures-output.txt](docs/a5/captures-output.txt). CSV: [docs/a5/captures/hit_flash_pixels.csv](docs/a5/captures/hit_flash_pixels.csv). Captures: [hit_flash_0.0.png](docs/a5/captures/hit_flash_0.0.png), [hit_flash_0.5.png](docs/a5/captures/hit_flash_0.5.png), [hit_flash_1.0.png](docs/a5/captures/hit_flash_1.0.png), [hit_flash_2.0.png](docs/a5/captures/hit_flash_2.0.png).

P1 = hull texel (99, 50), screen (155, 590). P2 = hull texel (59, 109), screen (135, 620). The table shows measured centre pixels; the 3×3 screen mean is in the CSV. Tolerance (brief §3): ±2 per channel.

| `hit_amount` | P1 predicted (hull) | P1 measured | max diff | P2 predicted | P2 measured | max diff |
|---|---|---|---|---|---|---|
| 0.0 | (87, 97, 40) | (70, 76, 31) | **21** | (16, 16, 16) | (16, 16, 16) | **0** |
| 0.5 | (137, 68, 28) | (126, 53, 22) | **15** | (88, 11, 11) | (88, 11, 11) | **0** |
| 1.0 | (188, 39, 16) | (181, 31, 12) | **8** | (159, 6, 6) | (159, 6, 6) | **0** |

- **P2 matches exactly** at all three values.
- **P1 does not match the hull prediction.** The tool reports turret alpha 1.00 over P1: the **turret sprite covers that pixel**. See *Inspect-and-revise cycle* below.
- **Recomputed turret values** (CHANGE-BRIEF *Revision* 2026-10-27, computed **after** the observation, so not a prediction). Turret texel `turret_right.png` (99, 71) = (70, 76, 31), alpha 252, read with PIL ([docs/a5/use-it-part2.txt](docs/a5/use-it-part2.txt) section 3):

  | `hit_amount` | turret recomputed | measured | max diff |
  |---|---|---|---|
  | 0.0 | (70, 76, 31) | (70, 76, 31) | 0 |
  | 0.5 | (126, 53, 22) | (126, 53, 22) | 0 |
  | 1.0 | (181, 30, 12) | (181, 31, 12) | 1 |

- **2.0 capture and the hint_range answer:** with `hit_amount = 2.0` set from code (read back as 2.0 after saving), both P1 and P2 are **(255, 0, 0)**. The brief §7 prediction was that `hint_range` does not clamp a value set from code. **Confirmed:** at 1.0 the pixels are still well inside the range, and at 2.0 (t = 1.2) the mix extrapolates past red and the display clips to (255, 0, 0). `hint_range` shapes only the Inspector slider.
- **Which capture I trust, and why.** I trust the engine capture (`get_viewport().get_texture().get_image()`) for measurement. From the sources: it is the 1280×720 viewport image itself, taken in the frame after the value was set, and the tool read the value back after saving. I also tried OS screenshots. The first captured the wrong window (an 850×287 terminal screenshot). The second (1920×1080, Win+PrtScn) showed the same values (my notes record this for the six hint bands). My notes record the choice without a further reason. The OS screenshot files are not in the repo: TBD.

## 5. In play — HUMAN CHECK

My playtest (2026-10-27, in the editor), verbatim from my notes:

> Got hit several times by enemy shells. Each hit flashed YunqiZ red and faded quickly; a second hit during the fade restarted it. Enemies hit by my shells did not flash red (only their existing white flash and the impact effect). After being destroyed and respawning there was no red left. I did not see the existing white flash on YunqiZ: the test shows modulate still reaches 2.2, but at the same moment the red is at its strongest. I tried to pause with Esc during the fade but could not press it within 0.5 s, so rule 5 rests on the headless test only.

Playtesters other than me: none recorded. Captures or video of the playtest: TBD.

## 6. Hint experiment — HUMAN CHECK

`tools/capture_hint.gd`, run windowed by me. Capture: [docs/a5/captures/hint_both.png](docs/a5/captures/hint_both.png). CSV: [docs/a5/captures/hint_pixels.csv](docs/a5/captures/hint_pixels.csv). Scene `scenes/hint_experiment.tscn` (Linear tonemap, exposure 1.0, glow/fog/adjustments off, unshaded). Tool output: [docs/a5/captures-output.txt](docs/a5/captures-output.txt).

| Band (file value) | Quad A `hint_srgb` (with `source_color`): predicted | measured | Quad B `hint_raw` (without): predicted | measured |
|---|---|---|---|---|
| 64 | 64 | **64** | 137 | **137** |
| 128 | 128 | **128** | 188 | **188** |
| 192 | 192 | **192** | 225 | **225** |

All six bands match exactly, centre and 3×3 mean (difference 0). Quad A shows the file's values because the sRGB decode at the sample and the encode at the output cancel. Quad B is brighter because the stored value is treated as linear and still encoded. My 1920×1080 OS screenshot showed the same six values (my notes).

## 7. Interface sweep — HUMAN CHECK

`tools/capture_materials.gd`, run windowed by me on `materials/cover_wall_intact.tres` as loaded on CoverWall; the damaged wall was untouched. Values are the mean RGB of an 11×11 px box on the front face at (334, 371); CoverWall2's box at (134, 371) stays at (49.9, 36.1, 27.1) in every sweep capture. CSV: [docs/a5/captures/materials_captures.csv](docs/a5/captures/materials_captures.csv). Output: [docs/a5/captures-output.txt](docs/a5/captures-output.txt). Light: the scene's only light, `Sun` (DirectionalLight3D, shadows on), no WorldEnvironment ([MATERIALS.md](MATERIALS.md) §4).

**I am describing these images from the numbers only.** Where my notes say nothing about the look, it is marked *to confirm by eye*.

| Uniform | Step | Value | CoverWall mean RGB | Capture |
|---|---|---|---|---|
| `albedo_tint` | min | (0, 0, 0, 1) | (22.1, 22.1, 22.1) | [sweep_albedo_tint_min.png](docs/a5/captures/sweep_albedo_tint_min.png) |
| | default | (1, 1, 1, 1) | (73.4, 54.1, 37.7) | [sweep_albedo_tint_default.png](docs/a5/captures/sweep_albedo_tint_default.png) |
| | max (= default) | (1, 1, 1, 1) | (73.4, 54.1, 37.7) | [sweep_albedo_tint_max.png](docs/a5/captures/sweep_albedo_tint_max.png) |
| `brightness` | min | 0.0 | (22.1, 22.1, 22.1) | [sweep_brightness_min.png](docs/a5/captures/sweep_brightness_min.png) |
| | default | 1.0 | (73.4, 54.1, 37.7) | [sweep_brightness_default.png](docs/a5/captures/sweep_brightness_default.png) |
| | max | 2.0 | (99.7, 72.7, 48.5) | [sweep_brightness_max.png](docs/a5/captures/sweep_brightness_max.png) |
| `roughness_scale` | min | 0.0 | (68.8, 47.4, 26.9) | [sweep_roughness_scale_min.png](docs/a5/captures/sweep_roughness_scale_min.png) |
| | default | 1.0 | (73.4, 54.1, 37.7) | [sweep_roughness_scale_default.png](docs/a5/captures/sweep_roughness_scale_default.png) |
| | max (= default) | 1.0 | (73.4, 54.1, 37.7) | [sweep_roughness_scale_max.png](docs/a5/captures/sweep_roughness_scale_max.png) |
| `uv_scale` | min | 0.1 | (76.8, 52.0, 34.4) | [sweep_uv_scale_min.png](docs/a5/captures/sweep_uv_scale_min.png) |
| | default | 0.5 | (73.4, 54.1, 37.7) | [sweep_uv_scale_default.png](docs/a5/captures/sweep_uv_scale_default.png) |
| | max | 4.0 | (79.8, 52.7, 33.1) | [sweep_uv_scale_max.png](docs/a5/captures/sweep_uv_scale_max.png) |

What changed, uniform by uniform:

- **`albedo_tint`.** Black gives (22.1, 22.1, 22.1), **not black**. My notes: "specular/ambient remain". The default and maximum are the same value, so the sweep has only one real step. The look of a coloured tint (brief: "darker or warmer tints recolour them") was not captured: TBD.
- **`brightness`.** 0 gives the same (22.1, 22.1, 22.1) as a black tint, again not black. At 2 the mean rises from 73.4 to 99.7 on R, not to 146. My notes: "because brightness multiplies linear colour and the output is sRGB-encoded ((73.4/255)^2.2 × 2 → ~100.5)". The brief expected 2 to "start to wash out": *to confirm by eye*.
- **`roughness_scale`.** 0 makes the sampled front-face box **darker** (73.4 → 68.8 R, 37.7 → 26.9 B); my notes say "roughness 0 makes the wall darker". The brief expected "glossy with sharp highlights". Whether a highlight appears elsewhere on the wall: *to confirm by eye*. Default and maximum coincide.
- **`uv_scale`.** My notes: "uv_scale changes brick size". The box mean shifts only a little (76.8 at 0.1, 79.8 at 4.0), as expected when the same bricks are averaged at a different scale. The brief expected huge bricks at the minimum and tiny, repetitive bricks at the maximum: *to confirm by eye*.
- **What breaks the look** at each end of each range: not in my notes, so TBD for all four uniforms.

File-size note (fact, not a look): every default/max capture that equals the saved values is 70 087 bytes, the same as `materials_side_by_side.png` ([docs/a5/captures-output.txt](docs/a5/captures-output.txt) lines 138–148). This is consistent with each restore really returning to the saved values.

## 8. One shader, two materials — HUMAN CHECK

| Observation | How | CoverWall (intact) mean R G B | CoverWall2 (damaged) mean R G B | Capture / CSV |
|---|---|---|---|---|
| Saved values | — | (73.4, 54.1, 37.7) | (49.9, 36.1, 27.1) | [materials_side_by_side.png](docs/a5/captures/materials_side_by_side.png) |
| **Material edit** | `brightness` 0.7 → 0.5 on the **damaged material only**, in the running instance, then restored | (73.4, 54.1, 37.7) **unchanged** | **(43.8, 32.6, 25.7)** | [material_edit_damaged_only.png](docs/a5/captures/material_edit_damaged_only.png), [materials_captures.csv](docs/a5/captures/materials_captures.csv) |
| **Shader edit** | I temporarily edited `shaders/brick_surface.gdshader` line 33 to `... * brightness * 0.5;`, reran the tool with `--tag=shader_edit`, then restored the file | **(54.7, 41.5, 30.9)** | **(38.6, 29.9, 24.7)** | [shader_edit_materials_side_by_side.png](docs/a5/captures/shader_edit_materials_side_by_side.png), [shader_edit_materials_captures.csv](docs/a5/captures/shader_edit_materials_captures.csv) |
| Material edit during the shader edit | damaged `brightness` 0.5 | (54.7, 41.5, 30.9) unchanged | (34.6, 27.8, 24.0) | [shader_edit_material_edit_damaged_only.png](docs/a5/captures/shader_edit_material_edit_damaged_only.png) |

**Result:** editing the shader changed **both** walls. Editing one material changed **only** the wall that uses it. The shader is shared code; each material holds its own current values. The shader-edit output and the restore are in [docs/a5/use-it-part2.txt](docs/a5/use-it-part2.txt) section 4. `shaders/` is clean against `3d48047`, and line 33 has no `* 0.5`. A consistency check from the numbers: in the shader-edit run, brightness 2.0 gives (73.4, 54.1, 37.7), exactly the unedited default (0.5 × 2 = 1). All shader-edit sweep captures are prefixed `shader_edit_` in `docs/a5/captures/`.

## 9. Material wiring

- `tests/test_materials.gd`: **76 passed, 0 failed, exit 0** (this rerun; also 76/76 at `97fdec6`). It checks:
  - both brick materials share one Shader object, and their textures are bound;
  - intact = shader defaults; damaged differs in exactly `albedo_tint` (0.78, 0.72, 0.66, 1) and `brightness` 0.7;
  - the colour sampler has `source_color` and the roughness sampler does not;
  - the brick and hint `.import` values (§11);
  - `CoverWall2` surface-0 override = `cover_wall_damaged.tres`;
  - `CoverWall` surface 0 resolves to `cover_wall_intact.tres` through Use External, and surface 1 is the imported `M_BrickDark` on both walls;
  - placement and camera framing;
  - the hint scene.
- History: before session 4 it was **75/1**. The Use External check looked for a key `use_external`, but Godot 4.7.2 saves `"use_external/enabled"` and `"use_external/path"`. Session 4 fixed only that check ([docs/a5/step3-finish-b.txt](docs/a5/step3-finish-b.txt), `docs/a5/sessions/prompt-4.txt`, `session-4.jsonl`).
- **Mutation 3** (delete `source_color` from `albedo_tex`, `brick_surface.gdshader` line 4; I restored it afterwards): **exit 1**. The log shows `FAIL source: colour sampler albedo_tex has source_color` and `RESULT: 74 passed, 2 failed` ([logs/mutation3_no_source_color_60fps.log](logs/mutation3_no_source_color_60fps.log)). **Caveat:** this run was made before the session-4 fix, so the second FAIL is the then-broken Use External check. The exit 1 therefore does not come from the mutation alone. The mutation's own FAIL line is present. Mutation 3 has not been rerun since the fix: TBD.
- **After a fresh import** (clone, `--import`, then `test_materials`): TBD, filled at clone verification.

## 10. Texture data — not applicable

The texture-data check in the Use It table applies to a normal map. No game material uses one. `red_bricks_04_nor_gl_1k.png` is used only in the Step 4 scratch material (`scenes/scratch_standard.tscn`), which the game never loads. The two brick materials sample only the colour map (`source_color`) and the roughness map (data, no `source_color`). That data/colour split is checked by `test_materials` and mutation 3 (§9), and shown by the hint experiment (§6).

## 11. Import settings

Every `.import` change in A5, and why. Enum meanings: `compress/mode` 0 Lossless, 2 VRAM Compressed; `compress/normal_map` 0 Detect, 1 Enable, 2 Disabled; `detect_3d/compress_to` 0 Disabled, 1 VRAM Compressed.

| File | Before | After | Who / how | Why | Evidence |
|---|---|---|---|---|---|
| `red_bricks_04_diff_1k.png.import` | mode 0, normal_map 0, mipmaps false, detect_3d 1 | **2, 2, true, 0** | me, by a script (written by Claude chat), then headless reimport, exit 0 | brief §5 values; detect_3d disabled so the editor cannot silently switch it when it is used in 3D | [docs/a5/step3-info.txt](docs/a5/step3-info.txt) §4, [docs/a5/step3-setup.txt](docs/a5/step3-setup.txt), [logs/reimport_brick.log](logs/reimport_brick.log), commit `9d14b83` |
| `red_bricks_04_rough_1k.png.import` | same as above | **2, 2, true, 0** | same | same; roughness is data | same |
| `red_bricks_04_nor_gl_1k.png.import` | same as above | **2, 1, true, 0** | same | normal map Enable (brief §5) | same |
| `assets/hint/grey_3x1.png.import` | did not exist | created by a first headless import, then set to **mode 0 (Lossless), mipmaps false, detect_3d 0** and reimported | me, by a script (written by Claude chat), after running `tools/make_hint_png.gd` | VRAM compression or a detect-3D switch would change the grey values the experiment measures | [docs/a5/step3-finish-a.txt](docs/a5/step3-finish-a.txt), [logs/reimport_hint_1.log](logs/reimport_hint_1.log), [logs/reimport_hint_2.log](logs/reimport_hint_2.log), commit `08ddf87` |
| `assets/models/cover_wall.glb.import` | `_subresources={}` | `_subresources.materials.M_Brick` with `"use_external/enabled"` and `"use_external/path" = res://materials/cover_wall_intact.tres` | me, in the editor's Advanced Import Settings → Use External | brief §5 / Revision: CoverWall's intact material goes behind the importer's per-material setting; the `.glb` is unchanged | commit `08ddf87` (+10 / −1), [logs/test_materials_60fps.log](logs/test_materials_60fps.log) |
| `docs/a5/captures/*.import` | Godot auto-imported the captures and CSVs | removed; empty `docs/.gdignore` added | me | captures are evidence, not game assets | commits `423c61c` (added), `d9b1837` (removed) |

**Editor re-saves that were reverted:**

- After session 2, `scenes/asset_room_3d.tscn` showed a diff: `load_steps` removed, a scene `uid`, and `unique_id` on every node ([docs/a5/step2-output.txt](docs/a5/step2-output.txt) section 1). It was the Godot editor re-saving in 4.7 format, not the agent, and I reverted it. A later editor re-save of the same kind was present before session 3. The agent left it as it was ([MATERIALS.md](MATERIALS.md) §6 item 7), and it was committed together with CoverWall2 in `81b364b`.
- In Step 4 the editor re-saved `shaders/brick_surface.gdshader` (line endings only). I restored it. I had also first saved the scratch scene into `shaders/` by mistake and moved it to `scenes/`.

**Open:** Godot also imported the capture CSVs as translations. 32 `docs/a5/captures/*.translation` files were committed in `423c61c` and are still tracked; `d9b1837` removed only the `.import` files. Not cleaned up yet.

## 12. Inspect-and-revise cycle: P1 is covered by the turret

1. **Predicted** (brief §3, before any shader): P1 = hull texel (99, 50), olive, (87, 97, 40). It was chosen as a flat 3×3 area in `hull_right.png` with a PIL script.
2. **Flagged before the capture:** Claude Code's session-5 report listed as unconfirmed that "the turret may cover P1" (the turret is drawn over the hull at (0, −10.85), and P1 is about 5 px above the hull centre). It could not check this because its PIL call was not approved, so it made the tool print the turret's alpha at each pixel (`docs/a5/sessions/session-5.jsonl`).
3. **Observed** (windowed capture): P1 was 21 / 15 / 8 off at 0.0 / 0.5 / 1.0, far outside ±2, while P2 matched exactly. The capture tool reported turret alpha 1.00 at that screen pixel.
4. **Inspected:** I read the turret texel under the screen pixel with PIL. It is `turret_right.png` (99, 71) = (70, 76, 31), alpha 252 ([docs/a5/use-it-part2.txt](docs/a5/use-it-part2.txt) section 3).
5. **Revised:** I added a dated *Revision* to CHANGE-BRIEF.md (commit `d9b1837`; the original text is unedited). It recomputes the turret values **after** the observation, labelled as not a prediction: (70, 76, 31) / (126, 53, 22) / (181, 30, 12). Measured: (70, 76, 31) / (126, 53, 22) / (181, 31, 12), within 1.
6. **Lesson:** a named pixel must be chosen on the final drawn layer, not on one texture of a layered sprite. The colour line itself was not at fault; the prediction was made for the wrong layer.

## 13. What no headless run shows

- Whether the red tint **reads as "you were hit"** to a player. Only my own playtest (§5) covers that, and no other playtester has seen it.
- The existing white `_flash()` is **still in code** (the test sees modulate 2.2 at the hit) but **I did not see it in play**, because the red is strongest at the same moment.
- **Rule 5 (pause)** has no human check: I could not press Esc within 0.5 s.
- Any **colour value on screen**. The hit-flash, hint and material numbers come from windowed captures, not from the tests.
- How the bricks look: brick size, gloss, wash-out, seams of the box projection on the wall's ends and top, and the shadow from CoverWall onto CoverWall2's end face. *To confirm by eye*, except where §7 quotes my notes.
- The look under any light other than the single `Sun`, or in the editor viewport's preview environment (MATERIALS.md §6 item 5).
- Whether the imports behave the same **after a fresh clone and import**: TBD.

---
---

# TEST-REPORT — Assignment 3: three 3D assets

The Assignment 2 report has moved, unchanged, to `docs/a2/TEST-REPORT.md`.

**Versions:** Blender 5.2.2 LTS · MCP for Blender add-on 1.8 (protocol 13) · Godot 4.7.2 · Claude Code 2.1.299 (Opus 5.5) · Windows 11, RTX 3060 laptop.

**How to re-run the checks (Windows, Git Bash, from the repo root):**

```bash
# Blender: rebuild each asset from scratch and check it (exit 0 = pass)
"/d/blender/blender.exe" -b --factory-startup --python-exit-code 1 --python tools/blender/build_cover_wall.py
# (same for build_ammo_crate.py and build_tank_hedgehog.py)

# Godot: import, then the headless asset check (exit 0 = all pass, 1 = any FAIL, 124 = time limit hit)
GODOT="/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe"
"$GODOT" --headless --path . --import
timeout 120 "$GODOT" --headless --path . --script res://tests/check_a3_assets.gd --fixed-fps 60
```

The course commands are written for macOS. On Windows I use Git Bash's GNU `timeout` (coreutils 8.32), because Windows' own `timeout.exe` only waits and does not stop a program; and `--path .` because my Godot project is the repo root, not a `godot/` folder.

## Results

All sizes in metres. Blender is Z-up, Godot is Y-up, so a Blender (x, y, z) size appears in Godot as (x, z, y).

| Check | cover_wall | ammo_crate | tank_hedgehog |
|---|---|---|---|
| **Brief** (w × d × h) | 4.0 × 1.0 × 1.8 | 1.2 × 0.8 × 0.7 (±0.1) | about 1.9 × 1.9 × 1.4 (±0.15) |
| **Blender** (x × y × z; build-script check; my sidebar for cover_wall) | 4.0 × 1.0 × 1.8 | 1.24 × 0.84 × 0.71 | 1.794 × 1.794 × 1.400 |
| **Godot headless** (x × y × z) | 4.000032 × 1.8 × 1.0 | 1.24 × 0.71 × 0.84 | 1.794236 × 1.400074 × 1.794236 |
| Matches brief? | yes | yes, +0.04 / +0.04 / +0.01, inside ±0.1 | yes after the revision below; height exact |
| **Upright** (height on Godot Y) | PASS | PASS | PASS |
| **Root node scale** in Godot | 1, 1, 1 | 1, 1, 1 | 1, 1, 1 |
| **Lowest Y** in Godot (origin on floor) | 0.0000 | 0.0000 | 0.0000 (3 vertices at Blender Z = 0) |
| **Triangles** (budget 60) | 36 | 36 | 36 |
| **Background rebuild** in Blender | exit 0 | exit 0 | exit 0 |
| **Godot check** overall | 18 / 18 PASS, exit 0 | | |

Every number above comes from a script output I kept (Blender build-script runs, and `tests/check_a3_assets.gd`, commit `ee1c67a`).

## The check failing on purpose

A check that has never failed may be broken. Claude ran a scratch copy of `check_a3_assets.gd` whose only difference (confirmed with `diff`) was ammo_crate's expected height changed from 0.71 to 0.81. It printed two FAIL lines and `RESULT: FAIL (2 failure(s))` with **exit code 1**; the other 16 checks still passed. The real script and the assets were not changed.

## What the checks do and do not show

- **The Blender build scripts** show that each asset can be rebuilt from nothing with the stated size, origin, applied transforms, triangle count and material slot *names*. They do not check colour values, and they say nothing about the asset after export.
- **The tank_hedgehog script's "apply rotation" step tested nothing.** The beams' rotation was already baked into the mesh during the join, so the bake step found identity transforms (it printed `identity: True`). The result is correct, but that step never had a real rotation to apply.
- **The Godot check** measures each `.glb` on its own, instantiated at the origin: size, lowest Y, root scale and the height axis, to 0.01 m. It does **not** check the copies placed in `asset_room_3d.tscn`, whether they rest on the floor there, colours, lighting, shadows, or whether the shapes read as what they are. Headless Godot uses a dummy renderer, so none of that is visible to it.
- **Hidden faces:** each asset is made of overlapping boxes, so faces inside the asset (the crate lid's underside, the wall's block bottoms, the hedgehog's crossing) still count towards the 36 triangles. They are never visible, so I left them.

## Problems found and what I changed

1. **tank_hedgehog's brief was wrong (evidence-based revision).** I asked Claude to work out the bounding box *before* building. With the brief's 2.4 m beams it came to 2.011 × 2.011 × **1.559** m, 0.009 m over the height tolerance, because the brief's numbers used the beam centrelines and left out the 0.15 m section. Claude recommended turning each beam 45° to fit. I chose instead to shorten the beams to **2.125 m**, because the overall size is what the game design depends on (lower than the 1.6 m hull, a barrier at hull scale), while the beam length was only a construction detail and was the number that was wrong. Result: 1.794 × 1.794 × 1.400 m. The change is recorded under *Revisions* in `CHANGE-BRIEF.md`; the original text is unchanged.
2. **ammo_crate's brief size left out the lid.** The brief lists the body size, but the lid overhangs by 0.02 m on each side and the stripe adds 0.01 m, so the real box is 1.24 × 0.84 × 0.71 m. Inside the ±0.1 m tolerance, so I kept it; the build script checks both the exact size and the brief tolerance.
3. **ammo_crate z-fighting avoided.** Claude noticed before building that a stripe exactly as deep as the lid (0.84 m) would share the lid's front and back faces and could flicker. I accepted its suggestion to make the stripe 0.83 m deep. The overall size did not change.
4. **My hand edit on cover_wall was 0.7 mm short.** I moved block B +0.6 m in Edit Mode. My sidebar then showed 4 m wide and I thought it was flush. Claude's read-only background inspection showed it had moved 0.5993 m, 0.7 mm short: **the sidebar rounds, so it could not show that error.** My correction (G X 0.0007, computed from a 4-decimal printout that was itself rounded) overshot by 0.032 mm. That is inside the build check's 0.1 mm tolerance and far below anything visible, so I stopped there. Lesson: to place something exactly, type the coordinate into the sidebar instead of nudging with G; and decide the tolerance first, then stop when inside it.

## HUMAN CHECK: look

*My own observations in the Godot editor (`scenes/asset_room_3d.tscn`), with the grey 6.0 × 1.6 × 3.4 m box standing in for the YunqiZ hull. Screenshot: `design/godot/asset_room_3d.png`.*

- **From the top** (the game's camera direction): the ammo crate's off-white stripe is the most readable feature in the scene, which is what the brief wanted. The hedgehog reads as three crossing beams. The wall's shadow shows its broken top, higher on the left.
- **Floor contact:** every asset casts a shadow that meets its base; none of them floats. (This is the check the headless script cannot do for the scene copies.)
- **Scale:** next to the hull box, the wall is wider than the hull is deep and lower than the turret would be, the crate is small enough to drive over, and the hedgehog is clearly lower than the hull. All three look in proportion.
- **From behind and below:** I switched the editor to the rear and bottom views for each asset. I saw no missing faces and no wrong colours; I found no problems to fix.
- **Not resolved:** with one light and no ambient fill, faces turned away from the light are very dark. The brief asked for one light; whether the game's real lighting suits these colours is not tested here.

## Brief failure cases, predicted vs. what happened

| # | Predicted | What happened |
|---|---|---|
| 1 | Lying on its side (Z-up vs Y-up) | Did not happen; height is on Godot Y for all three |
| 2 | Scale or rotation not applied | Did not happen; scale 1, 1, 1 in Blender and Godot. Building from mesh data meant scale was never non-1 |
| 3 | Origin in the middle, floats or sinks | Did not happen; lowest Y 0.0000 in Godot |
| 4 | Claude builds more than asked | Did not happen; 36 triangles each, 3 boxes each |
| 5 | Colours lost on export | Did not happen; colours visible in the Godot screenshot (checked by eye, not measured) |
| 6 | MCP will not connect on Windows | Connected, after one failed command (see FRICTIONAL.md) |

Not predicted: the hedgehog's brief size being wrong, the crate's lid overhang, and a Blender error (`AttributeError ... 'select_set'`) during cover_wall's join.
