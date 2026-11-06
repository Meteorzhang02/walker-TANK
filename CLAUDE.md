# CLAUDE.md — walker-TANK

## Project context

- **Engine:** Godot 4.7.2 stable (`README.md` line 6; `scripts/run-test.sh` line 7 runs `Godot_v4.7.2-stable_win64_console.exe`). `project.godot` line 19: `config/features=PackedStringArray("4.7")`.
- **Project root:** `project.godot` is at the repository root; there is no `godot/` folder. Effects go in `effects/`, previews in `previews/`, tests in `tests/` (`CHANGE-BRIEF.md` line 5; `run-test.sh` line 14 uses `--path .`). `effects/` and `previews/` do not exist yet.
- **Renderer:** Forward+. `project.godot` has no `rendering/` section (whole file, lines 1–25), so the engine default applies; confirmed by the human in Project Settings → Rendering Method = `forward_plus` (2026-10-27).
- **2D settings:** viewport 1280×720, stretch `canvas_items` (`project.godot` lines 23–25). Camera fixed at (640, 360) (`main.gd` lines 61–64); `shake()` moves `camera.offset`, not a layer (`main.gd` lines 216–227).
- **Main scene:** `res://scenes/main.tscn` (`project.godot` line 18), a single `Node2D` with `scripts/main.gd` (`scenes/main.tscn` lines 5–6); `main.gd` builds everything in code: `World` (PAUSABLE, line 50) holds the ground, `Actors` (y-sorted, lines 53–56), `FX` (`fx_layer`, `z_index = 20`, lines 57–60) and the camera. `main` itself is `PROCESS_MODE_ALWAYS` (line 43).

### Effect A — cover hit burst (`CHANGE-BRIEF.md` lines 23–28)

- **Node type:** 3 × `CPUParticles2D` (`Flash`, `Debris`, `Dust`) under one `Node2D` root, scene `effects/cover_hit_burst.tscn` (brief lines 27, 96–102).
- **Event owner:** `scripts/cover.gd` `take_hit(_shell)` (line 33), after the `if stage >= 2: return` guard (line 34); it plays `cover_hit` (line 39) and today calls `world.spawn_fx("debris", global_position + Vector2(0, -8))` (line 40). There is no signal; the event is the method call. Stages: `HITS_TO_CRACK` 2, `HITS_TO_BREAK` 4 (lines 5–6); at stage 2 the shape is disabled, the node is not freed (lines 44–45).
- **Caller:** `scripts/shell.gd` `_on_body_entered()` calls `body.take_hit(self)` (line 46), spawns `"impact"` at `global_position + DRAW_OFFSET` (line 50), then `queue_free()` (line 51). `DRAW_OFFSET` is line 5, `dir` line 9, `damage` 25 line 11; an expired shell frees itself at line 31.
- **Spawner:** `main.gd` `spawn_fx()` (lines 161–213) adds code-made `CPUParticles2D` to `fx_layer`; `spawn_shell()` (lines 150–157) also parents shells to `fx_layer`. The brief adds `spawn_cover_burst(shell)` to `main.gd`.
- **Appears in:** `World/FX` in the game; `previews/cover_hit_burst_preview.tscn` (to be created, brief line 169).

### Effect B — damage smoke (`CHANGE-BRIEF.md` lines 187–211)

- **Node type:** 1 × `GPUParticles2D` with a `ParticleProcessMaterial`, scene `effects/damage_smoke.tscn` (brief line 27). Today `smoke` is a `CPUParticles2D` (`tank.gd` line 35) built by `_make_trail()` (line 61, lines 68–90) with no texture.
- **Condition owner:** `scripts/tank.gd`. Value `health / max_health` (`health` line 26, `max_health` line 19; enemies 75, `main.gd` line 85). `take_damage()` (lines 163–175) calls `_update_damage_look()` (lines 195–198); `die()` (lines 179–192) sets `smoke.emitting = true` (line 187); `reset_full()` (lines 206–214) sets it false (line 213). `flames` is line 36 / 62.
- **Signals:** `fired`, `damaged(tank, amount)`, `destroyed(tank)` (`tank.gd` lines 6–8). `main.gd` connects the player's `destroyed` / `damaged` (lines 77–78) and each enemy's `destroyed` (line 92). Respawn has no signal: `main.gd` calls `player.reset_full(SPAWN)` at line 266.
- **Tanks:** YunqiZ is `scripts/player.gd` (extends `tank.gd`, line 1), speed 110 (`tank.gd` line 20); three enemies are `scripts/enemy.gd` (extends `tank.gd`, line 1), speed 70, reload 1.8 (`main.gd` lines 80–93). All live under `World/Actors`.
- **Appears in:** every tank in `scenes/main.tscn`; also every tank in `scenes/gallery.tscn`, because `scripts/gallery.gd` preloads `tank.gd` and `enemy.gd` (lines 5–6); `previews/damage_smoke_preview.tscn` (to be created, brief line 318).
- **A5 driver, unchanged:** `scripts/hit_flash_driver.gd` is attached to YunqiZ only (`main.gd` line 79).

### Tests (always through `scripts/run-test.sh`)

Usage: `scripts/run-test.sh <file-in-tests/> <fps|realtime> [timeout-seconds]` (`run-test.sh` line 2). It runs the console exe `--headless --path . --script res://tests/<file>`; with a number it adds `--fixed-fps <n>` and logs to `logs/<name>_<n>fps.log`; with `realtime` it adds no fps flag and logs to `logs/<name>_realtime.log` (lines 8–13). Timeout is the third argument, default 120 s (line 14). It exits with Godot's status (`pipefail`, line 5), or 1 if the log contains `SHADER ERROR` or `SCRIPT ERROR` (line 16). The Godot path can be overridden with `GODOT=` (line 7). From the repo root in Git Bash:

```bash
bash scripts/run-test.sh test_hit_flash.gd 30
bash scripts/run-test.sh test_hit_flash.gd 60
bash scripts/run-test.sh test_hit_flash.gd 144
bash scripts/run-test.sh test_materials.gd 60
bash scripts/run-test.sh check_tools_parse.gd 60
bash scripts/run-test.sh check_a3_assets.gd 60
bash scripts/run-test.sh test_sound_triggers.gd 60
# realtime mode (no --fixed-fps), optional timeout in seconds:
bash scripts/run-test.sh <test>.gd realtime 180
```

Baseline at a9513d3 (`CHANGE-BRIEF.md` lines 11–19): 50/50/50, 76, 9, 18, 8, all exit 0. All five tests are `extends SceneTree` and `quit(1)` on any FAIL (`test_hit_flash.gd` lines 1, 60; `test_materials.gd` 1, 51; `check_tools_parse.gd` 1, 26; `check_a3_assets.gd` 1, 93; `test_sound_triggers.gd` 1, 101). `test_hit_flash.gd` and `test_sound_triggers.gd` load `res://scenes/main.tscn` (lines 198, 20). A "5 resources still in use at exit" message is pre-existing, not a failure.

## Headless facts

- A headless run uses a dummy renderer: it draws nothing. Headless tests prove that the shaders parse, their uniforms are declared and driven, and the materials are wired; they never prove what the screen shows. Every look is a human check recorded in `TEST-REPORT.md`.
- Headless does report shader parse errors: deleting a semicolon from `shaders/hit_flash.gdshader` printed `SHADER ERROR: Expected a ';'.` and the test exited 1 (`logs/mutation1_semicolon_60fps.log`).
- A headless run uses a dummy renderer: it draws no particles and runs no GPU particle process. Node state
  (emitting, one_shot, amount_ratio, visibility, instance counts) is observable; the look is not.
- A GPU effect's headless CPU price is near zero by construction.
- Frame strips come from a windowed Movie Maker run, which I start.

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `shaders/` (`shaders/hit_flash.gdshader`, `shaders/brick_surface.gdshader`, `shaders/hint_experiment.gdshader`) is hand-written by the human. An agent never creates, edits, reformats or "fixes" a file in `shaders/`. If a shader looks wrong, report it and stop.
- `shaders/standard_generated.gdshader` and the coming `shaders/particles_generated.gdshader` are saved by the human from Godot's converters; agents do not edit them. The answers in `LANGUAGE-NOTES.md` are written by the human.
- Effect settings live in the scene files in `effects/` (`cover_hit_burst.tscn`, `damage_smoke.tscn`), not in code. Scripts only instance them, place / rotate them, and set the runtime values the brief names (`emitting`, `amount_ratio`).
- `tools/make_particle_textures.gd` and its PNGs are run and committed by the human.
- `CHANGE-BRIEF.md` is the human's spec. Its original text is never edited; changes go only under *Revisions*, dated, and only when the human asks.

## Godot 4 names

- Use Godot 4 classes: `CPUParticles2D`, `GPUParticles2D`, `ParticleProcessMaterial`, `CanvasItemMaterial`, `Gradient`, `GradientTexture1D`, `Curve`, `CurveTexture`. Never Godot 3 `Particles2D`, `ParticlesMaterial`, `GradientTexture`.
- Use the `_min` / `_max` pairs: `initial_velocity_min/max`, `angular_velocity_min/max`, `damping_min/max`, `hue_variation_min/max`, and `scale_amount_min/max` (CPU) / `scale_min/max` (`ParticleProcessMaterial`). Never `initial_velocity`, `scale_amount`, or any `*_random`.
- `CPUParticles2D` takes `Gradient` / `Curve` directly (`color_ramp`, `scale_amount_curve`) and `Vector2` `direction` / `gravity`. `ParticleProcessMaterial` takes textures (`color_ramp` as `GradientTexture1D`, `scale_curve` as `CurveTexture`) and `Vector3` `direction` / `gravity`; set `particle_flag_disable_z` for 2D.
- Blend: `CanvasItemMaterial.blend_mode = BLEND_MODE_ADD` / `BLEND_MODE_MIX`, on the node's `material`. Emission shapes: `EMISSION_SHAPE_POINT`, `EMISSION_SHAPE_SPHERE` with `emission_sphere_radius`.
- Checked in this build by `tests/probe_particle_props.gd` (`logs/probe_particle_props_60fps.log`, 2026-11-06):
  `CPUParticles2D` has `use_fixed_seed`, `seed`, the `finished` signal, the `_min`/`_max` pairs and `scale_amount_curve`,
  and has **no** `amount_ratio`, `initial_velocity`, `scale_amount` or `scale_amount_random`.
  `GPUParticles2D` has `amount_ratio`, `use_fixed_seed`, `seed`, `visibility_rect`, `preprocess` and `finished`.
  `ParticleProcessMaterial` has the brief's `turbulence_*` names, `scale_min`/`max`, `scale_curve`, `angle_min` and
  `particle_flag_disable_z`. The class `ParticlesMaterial` does not exist.
- Trap: `ParticleProcessMaterial` *does* list a property called `initial_velocity` beside `initial_velocity_min`/`max`,
  so a Godot 3 name there may not be rejected. Always set and read back the `_min`/`_max` pair.
- Still unchecked: the unit of `angle_min`/`max` (degrees assumed) and 2D sphere emission on `ParticleProcessMaterial`;
  the config test and the frame strip check them.

## Out of scope

- Only the brief's three code edits: `cover.gd` line 40, one new `spawn_cover_burst()` in `main.gd`, and the smoke lines in `tank.gd` (line 35, line 61, `_update_damage_look()`, one added line in `die()`). No other line of any script changes.
- Game state is read, never written: health, damage, `invuln_left`, reload, cover stages and hit counts, every timing, and `modulate` (white `_flash()`, death grey, `tint`) stay as they are. `flames` stays a `CPUParticles2D`.
- `shell.gd` is untouched, including its `"impact"` spark. The `"debris"` and other branches of `spawn_fx` stay in `main.gd`.
- Bursts are never parented to the shell or the cover, never reused, and never rely on default `gravity`. The smoke never changes `amount` at runtime.
- Movement, collision, input, enemy AI, HUD, audio, music, pause handling, victory screen, the A5 hit flash and `hit_flash_driver.gd` are unchanged. Do not touch `Engine.time_scale` or `get_tree().paused` logic in `main.gd`.
- The five existing tests and their expectations are not edited, and must still pass at the baseline counts. `scripts/run-test.sh`, `project.godot`, every source texture, `.glb`, `.import` and `shaders/` file are not changed.
- No new effects beyond A and B, no post-processing, no change to the 3D scenes.

## Unconfirmed

- Resolved in `CHANGE-BRIEF.md` revision R1 (2026-11-06): the shell-less `take_hit()` in `test_sound_triggers.gd` line 94 (fallback position and rotation), the debris gravity (0, 160) at `main.gd` line 191, the two line references, and the gallery smoke. Property names: see *Godot 4 names*.
- Whether a `GPUParticles2D` under a PAUSABLE parent stays visible and frozen when paused, and what headless reports for it, is the brief's prediction, not yet observed.
- `scripts/audio.gd` and `tests/test_hit_flash.gd`, `test_materials.gd`, `check_tools_parse.gd`, `check_a3_assets.gd` were read only for their headers, `quit()` lines and scene loads.
- The test commands assume Git Bash with GNU `timeout` and the Godot path in `run-test.sh` line 7.
