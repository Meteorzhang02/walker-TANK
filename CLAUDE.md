# CLAUDE.md — walker-TANK

## Project context

- **Engine:** Godot 4.7.2 stable (`README.md` lines 16, 57; `scripts/run-test.sh` line 5 runs `Godot_v4.7.2-stable_win64_console.exe`). `project.godot` line 19: `config/features=PackedStringArray("4.7")`.
- **Project root:** `project.godot` is at the repository root; there is no `godot/` folder, so shaders go in `shaders/` and tests in `tests/` (`CHANGE-BRIEF.md` line 7; `scripts/run-test.sh` line 8 uses `--path .`).
- **Renderer:** Forward+. `project.godot` has no `rendering/` section and no renderer key (whole file, lines 1–25), so the engine default applies; confirmed by the human in Project Settings → Rendering → Renderer → Rendering Method = `forward_plus` (2026-10-27).
- **2D settings:** viewport 1280×720, stretch mode `canvas_items` (`project.godot` lines 23–25). No `hdr_2d` key (`project.godot`; `CHANGE-BRIEF.md` line 78).
- **Main scene:** `res://scenes/main.tscn` (`project.godot` line 18). That scene is a single `Node2D` with `scripts/main.gd` attached (`scenes/main.tscn` lines 5–6); `main.gd` builds everything else in code.

### The shaded object (2D hit flash)

- YunqiZ is a `CharacterBody2D` running `scripts/player.gd`, which extends `scripts/tank.gd` (`player.gd` line 1; `tank.gd` line 1). `main.gd` creates it under `World/Actors` (`main.gd` lines 71–76).
- It is drawn by two `Sprite2D` nodes made in code, `hull` and `turret`, each at scale 0.5; the turret sits at `TURRET_OFFSET` (`tank.gd` lines 54–60). Their textures are `res://assets/game/yunqiz/hull_<dir>.png` / `turret_<dir>.png` for 5 directions; the other 3 facings use `flip_h` (`tank.gd` lines 15–16, 51–53, 98–100).
- Colour reaches the sprites through the tank's `modulate`: `modulate = tint` in `_ready()` (line 63), the white `_flash()` tween to 2.2 and back over 0.15 s (lines 201–203), grey on `die()` (line 185), back to `tint` in `reset_full()` (line 212).
- Enemies run the same `tank.gd` (via `scripts/enemy.gd`) with `tint = ENEMY_TINT` (`main.gd` lines 16, 79–90). The player's tint is `Color(1, 1, 1)` (`tank.gd` line 23).

### Game state that drives the effect

- Owned by `scripts/tank.gd`. `take_damage()` (lines 163–175) ignores hits while `invuln_left > 0`, sets `invuln_left = 0.3`, calls `die()` and returns on a fatal hit, otherwise calls `_flash()` and emits `damaged(tank, amount)` (line 175).
- `die()` emits `destroyed(tank)` (line 192); `reset_full()` restores health and sets `invuln_left = 1.0` (lines 206–214). Signals are declared at lines 6–8.
- `scripts/main.gd` connects the player's `destroyed` and `damaged` signals (lines 77–78) and calls `player.reset_full(SPAWN)` on respawn (line 265).
- Pause: `world` is `PROCESS_MODE_PAUSABLE` (`main.gd` line 50); `main` itself is `PROCESS_MODE_ALWAYS` (line 43).

### The 3D object for the textured shader

- `cover_wall` is the node `CoverWall` in `scenes/asset_room_3d.tscn`, an instance of `res://assets/models/cover_wall.glb` at x = −6.77 (lines 3, 35–36). The scene's only light is `Sun`, a `DirectionalLight3D` with `shadow_enabled = true` (lines 26–28).
- Its material currently comes from inside the `.glb` import: `cover_wall.glb.import` has `materials/extract=0` and `_subresources={}` (lines 39, 42), so no external material or per-material override is set yet. The Blender build gives it two flat-colour materials, `M_Brick` and `M_BrickDark` (`tools/blender/build_cover_wall.py` lines 53–54).
- The brick textures are in `assets/textures/brick/` (`red_bricks_04_diff_1k.png`, `red_bricks_04_rough_1k.png`, `red_bricks_04_nor_gl_1k.png`, `ATTRIBUTION.md`; tracked in git, commit ed1976a).

### Tests (always through `scripts/run-test.sh`)

Usage: `scripts/run-test.sh <file-in-tests/> <fps>` (`run-test.sh` line 2). It runs the Godot console exe headless with `--fixed-fps`, a 120 s `timeout`, logs to `logs/<name>_<fps>fps.log`, and exits 1 if the log contains `SHADER ERROR` or `SCRIPT ERROR` (lines 6–11). Run from the repo root in Git Bash:

```bash
bash scripts/run-test.sh check_a3_assets.gd 60
bash scripts/run-test.sh test_sound_triggers.gd 60
# frame-rate checks named in CHANGE-BRIEF.md section 2 use 30, 60 and 144:
bash scripts/run-test.sh <test>.gd 30
bash scripts/run-test.sh <test>.gd 144
```

Baseline (`CHANGE-BRIEF.md` line 9): `check_a3_assets.gd` 18/18 PASS, `test_sound_triggers.gd` 8/8 PASS, both exit 0; a "5 resources still in use at exit" leak message at shutdown is pre-existing and is not a failure. Both tests are `extends SceneTree` scripts that `quit(1)` on any FAIL (`tests/check_a3_assets.gd` lines 1, 93; `tests/test_sound_triggers.gd` lines 1, 101).

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `shaders/` (`shaders/hit_flash.gdshader`, `shaders/brick_surface.gdshader`, `shaders/hint_experiment.gdshader`) is hand-written by the human. An agent never creates, edits, reformats or "fixes" a file in `shaders/`. If a shader looks wrong, report it and stop.
- `shaders/standard_generated.gdshader` is produced by Godot's *Convert to ShaderMaterial* and saved by the human; agents do not edit it either. The answers in `LANGUAGE-NOTES.md` are written by the human.
- `CHANGE-BRIEF.md` is the human's spec. Its original text is never edited; changes go only under *Revisions*, dated, and only when the human asks.

## Out of scope

- Game rules and timings in `tank.gd`: `take_damage()`, `die()`, `invuln_left` (0.3 s), `reset_full()`, and the existing white `_flash()` (0.15 s) stay exactly as they are. The red tint is added on top; it never replaces or retimes the white flash.
- Presentation code only reads game state (listens to `damaged` / `destroyed` / respawn); it never writes health, invulnerability, `modulate` timing or any other gameplay variable.
- Enemies get no ShaderMaterial and must never show the flash. Hull and turret share one material instance; no per-sprite copies.
- No frame counting: the fade is driven by scaled `delta`. Do not touch `Engine.time_scale`.
- Movement, collision, input, AI, shells, covers (2D), HUD, audio, music, pause handling and the victory screen are unchanged.
- The existing tests and their expectations (`tests/check_a3_assets.gd`, `tests/test_sound_triggers.gd`) are not edited; they must still pass at the baseline counts.
- The `.glb` files, the Blender build scripts, the texture files and their import settings beyond what section 5 of the brief names, and `scripts/run-test.sh` are not changed.
- No new lights, environment, SSAO or post-processing in `asset_room_3d.tscn` beyond what the brief asks for; the 3D change is limited to `cover_wall` and its second comparison instance. New files the brief calls for are allowed: the hint-experiment scene, its materials and `tools/make_hint_png.gd` (brief section 4), and the Step 4 scratch scene for the generated StandardMaterial3D.
- `project.godot` settings (renderer, `hdr_2d`, stretch) are not changed.

## Unconfirmed

- Whether `COLOR` in a `canvas_item` fragment already includes the node's `modulate` (the brief's reading, to be confirmed).
- The material names as they appear after glTF import (assumed to be `M_Brick` / `M_BrickDark` from the Blender script; not checked in the imported `.scn`), and whether the `.glb` has UVs suitable for the brick textures.
- How the second `cover_wall` instance gets its material (brief section 5 defers this to a revision).
- Import settings of the three brick PNGs: I did not read their `.import` files, so the compress / normal-map / mipmap values in brief section 5 are not confirmed as applied.
- `scripts/enemy.gd`, `cover.gd`, `shell.gd`, `audio.gd` and `scenes/gallery.tscn` were not read in full.
- `tests/` has no hit-flash or material test yet; their file names are not fixed by the brief.
- The test commands above assume Git Bash with GNU `timeout` and the Godot path hard-coded in `run-test.sh` line 5.
