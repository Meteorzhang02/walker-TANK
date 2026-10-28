# walker-TANK

A tank-battle game in Godot: you drive **YunqiZ** through a ruined brick battlefield and destroy three enemy tanks.

- **Starting point:** my own Assignment 2 game and Assignment 3 3D asset room in this repository (A5 baseline commit `c4a1f84`). See [SOURCES.md](SOURCES.md).
- **Engine:** Godot 4.7.2 stable. **Renderer:** Forward+ (engine default; `project.godot` sets no renderer). 2D: 1280×720, stretch `canvas_items`, no `hdr_2d`.
- **Film (Assignment 5):** see [Film](#film) below.

## Assignment 5 — hit flash shader and brick surface materials

### What Assignment 5 added

- **Hit flash on YunqiZ (2D):** `shaders/hit_flash.gdshader` (`canvas_item`, hand-written by me) mixes the sprite colour toward red: `mix(COLOR.rgb, flash_color.rgb, hit_amount * flash_strength)`. `scripts/hit_flash_driver.gd`, attached by one line in `scripts/main.gd`, puts one shared ShaderMaterial on YunqiZ's hull and turret.
  - On `damaged` it sets `hit_amount` to 1.0, then fades it to 0.0 over 0.5 s of game time.
  - A new hit restarts the fade. Pause holds it. Death and respawn clear it.
  - Enemies have no material. The existing white `_flash()` is unchanged.
- **Brick materials (3D):** `shaders/brick_surface.gdshader` (`spatial`, hand-written by me). It projects the Poly Haven red_bricks_04 colour and roughness maps from object-space position, because `cover_wall.glb` has no UVs. Uniforms: `albedo_tint`, `brightness`, `roughness_scale`, `uv_scale`.
  - Two materials share it: `materials/cover_wall_intact.tres` on `CoverWall` (through the importer's Use External on `M_Brick`) and `materials/cover_wall_damaged.tres` on a new `CoverWall2` (surface override).
- **Hint experiment:** `scenes/hint_experiment.tscn` with `shaders/hint_experiment.gdshader`. It shows the same 3×1 grey PNG (64/128/192, `tools/make_hint_png.gd`) through a sampler with `source_color` (Quad A) and one without (Quad B).
- **Generated shader for comparison:** `shaders/standard_generated.gdshader` (Godot's *Convert to ShaderMaterial* in `scenes/scratch_standard.tscn`; not used by the game).
- **Tests:** `tests/test_hit_flash.gd`, `tests/test_materials.gd`, `tests/check_tools_parse.gd`. **Capture tools:** `tools/capture_hit_flash.gd`, `tools/capture_hint.gd`, `tools/capture_materials.gd`.
- **Documents:** [CHANGE-BRIEF](CHANGE-BRIEF.md) (with Revisions) · [TEST-REPORT](TEST-REPORT.md) · [MATERIALS](MATERIALS.md) · [LANGUAGE-NOTES](LANGUAGE-NOTES.md) · [FRICTIONAL](FRICTIONAL.md) · [SOURCES](SOURCES.md) · [CLAUDE.md](CLAUDE.md). Evidence: `logs/`, `docs/a5/`.

### Film

- **Watch:** [Google Drive](https://drive.google.com/file/d/13CpPJOGbfbvrYQpmlH9hzfpWRgdgEh8Z/view?usp=drive_link) — `claude-liam-walker-tank-a5-shaders.mp4`
- **Length / size:** 3:05, 3840×2160 landscape
- **SHA-256:** `0e13fc655269689d179f19adf2a869a57c950927165d3c85a1fb14206a2d2a7c`
- **Game-source revision shown:** `561d47d`
- The MP4 is kept out of GitHub. The film's records (build log, fact check, beat sheet, QC) are in `youtube/claude-liam-walker-tank-a5-shaders/`.

### Run (Windows, Git Bash, from the repo root)

```bash
GODOT="/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe"   # as in scripts/run-test.sh line 5

# Import once after cloning
"$GODOT" --headless --path . --import

# The game (main scene, scenes/main.tscn); or open the project in the editor and press F5
"$GODOT" --path .

# The 3D asset room with the two brick walls; or open the scene in the editor and press F6
"$GODOT" --path . res://scenes/asset_room_3d.tscn

# The hint experiment
"$GODOT" --path . res://scenes/hint_experiment.tscn
```

**Tests**, always through the wrapper, one per call. The wrapper runs headless with `--fixed-fps`, a 120 s timeout, and a log in `logs/<name>_<fps>fps.log`. It exits 1 on any FAIL or on `SHADER ERROR` / `SCRIPT ERROR`.

```bash
bash scripts/run-test.sh test_hit_flash.gd 30
bash scripts/run-test.sh test_hit_flash.gd 60
bash scripts/run-test.sh test_hit_flash.gd 144
bash scripts/run-test.sh test_materials.gd 60
bash scripts/run-test.sh check_tools_parse.gd 60
bash scripts/run-test.sh check_a3_assets.gd 60
bash scripts/run-test.sh test_sound_triggers.gd 60
```

Results at `3d48047`: 50/50 at each rate, 76/76, 9/9, 18/18, 8/8, all exit 0 ([TEST-REPORT](TEST-REPORT.md)).

**Capture tools.** These need a real window, because headless draws nothing. Output goes to `docs/a5/captures/`.

```bash
"$GODOT" --path . --resolution 1280x720 --script res://tools/capture_hit_flash.gd
"$GODOT" --path . --resolution 1280x720 --script res://tools/capture_hint.gd
"$GODOT" --path . --resolution 1280x720 --script res://tools/capture_materials.gd
# optional: prefix every file, e.g. after a temporary shader edit
"$GODOT" --path . --resolution 1280x720 --script res://tools/capture_materials.gd -- --tag=shader_edit
```

The game and the two scenes can also be opened in the editor. The command-line scene runs above follow Godot's standard CLI and were not themselves recorded in my notes.

### Controls

Unchanged from Assignment 2 (table below): WASD / arrows move, mouse aims, left mouse / Space fires, Esc / P pauses, M / N mute music / SFX, R restarts after victory.

### Known limitations (A5, from my notes)

- The existing white `_flash()` still runs (the test sees modulate 2.2), but in play it is visually masked by the red at the moment of the hit.
- The pause rule (fade holds while paused) has only the headless check. I could not press Esc within 0.5 s.
- `reset_full()` on a living tank mid-fade would not clear the fade. The game only calls it after death.
- My named pixel P1 is covered by the turret. The brief's hull prediction does not apply there, and a recomputed turret value is in the brief's Revisions. P2 matched exactly.
- No game material uses a normal map. `red_bricks_04_nor_gl_1k.png` is only in the Step 4 scratch material, so the normal-map check is not applicable.
- The interface-sweep looks (wash-out, gloss, brick size) are recorded mostly as numbers. Several are still to confirm by eye.
- The helper bash/python scripts I ran were written by Claude chat and are not in the repo.

---

## Assignment 3

Assignment 3 adds a 3D asset room to this repository; the 2D game from Assignment 2 (below) is unchanged.

- **3D asset room:** `scenes/asset_room_3d.tscn` puts the three assets next to a grey 6.0 × 1.6 × 3.4 m box that stands in for the YunqiZ hull, under one light.
- **Three assets**, built from Blender cubes, 36 triangles each, exported to `assets/models/`:
  - `cover_wall` — broken brick cover wall, 4.0 × 1.0 × 1.8 m (includes one hand edit of my own)
  - `ammo_crate` — olive crate with an off-white stripe, 1.24 × 0.84 × 0.71 m
  - `tank_hedgehog` — three crossed steel beams, 1.794 × 1.794 × 1.400 m
- **Build and export scripts:** `tools/blender/build_cover_wall.py`, `build_ammo_crate.py`, `build_tank_hedgehog.py` rebuild each asset from nothing and check it; `tools/blender/export_glb.py` exports a `.blend` to `.glb`.
- **Headless check:** `tests/check_a3_assets.gd` measures each `.glb` in Godot (size, lowest Y, root scale, height axis): 18 / 18 PASS.
- **Final film:** [Watch on Google Drive](https://drive.google.com/file/d/1tCX0BUF_Jx4Uj2bW2vaNanxA3WYCKaQn/view?usp=drive_link) — `claude-liam-walker-tank-a3-assets.mp4` (3840×2160 landscape, 3:39), SHA-256 `b91f985d83d7ffed36f941aef078ee3efa676d958c6f58b1ad84931d95c98d8c`. It shows game-source revision `9baa12c`. Its beat sheet, script and evidence are in `youtube/claude-liam-walker-tank-a3-assets/`; the MP4 itself is not in Git.

**Versions:** Godot 4.7.2 · Blender 5.2.2 LTS · MCP for Blender add-on 1.8 (protocol 13) · Claude Code 2.1.299 (Opus 5.5) · Windows 11.

### Rebuild, export, import, check (Windows, Git Bash, from the repo root)

```bash
# Rebuild one asset from scratch in background Blender and check it (exit 0 = pass)
"/d/blender/blender.exe" -b --factory-startup --python-exit-code 1 --python tools/blender/build_cover_wall.py
# (same for build_ammo_crate.py and build_tank_hedgehog.py)

# Export one .blend to .glb (one asset per call)
"/d/blender/blender.exe" -b --factory-startup --python-exit-code 1 design/blender/cover_wall.blend --python tools/blender/export_glb.py -- assets/models/cover_wall.glb

# Godot: import, then the headless asset check (exit 0 = all pass, 1 = any FAIL, 124 = time limit hit)
GODOT="/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe"
"$GODOT" --headless --path . --import
timeout 120 "$GODOT" --headless --path . --script res://tests/check_a3_assets.gd --fixed-fps 60
```

`timeout` is Git Bash's GNU `timeout`; Windows' own `timeout.exe` only waits and does not stop a program. To look at the assets, open the project in Godot 4.7 and open **`scenes/asset_room_3d.tscn`**.

### Known limitations (A3)

- The Blender build scripts check material slot names, not colour values, and say nothing about the asset after export.
- The Godot check measures each `.glb` on its own at the origin. It does not check the copies placed in `asset_room_3d.tscn`, colours, lighting, shadows or whether the shapes read correctly; I checked those by eye in the editor.
- With one light and no ambient fill, faces turned away from the light are very dark; how the colours look under the game's real lighting is not tested.
- Each asset is overlapping boxes, so hidden inside faces still count towards the 36 triangles.
- tank_hedgehog's "apply rotation" build step had no real rotation to apply (already baked during the join), so that step is untested.
- ammo_crate is 1.24 × 0.84 × 0.71 m, not the brief's 1.2 × 0.8 × 0.7, because the lid overhang and stripe were left out of the brief; it is inside the ±0.1 m tolerance.
- The cover_wall hand edit overshoots by 0.032 mm, inside the build check's 0.1 mm tolerance.
- The film shows my Blender session as my own screenshots (stills), not a screen recording, and the Godot scene with a static camera.
- The film shows Claude's plan and report but not the text of my prompt (my screenshots do not include it). In its last second the toolkit's locked outro mascot overlaps the @NikBearBrown handle.

Full details: [TEST-REPORT](TEST-REPORT.md) · [BLENDER-NOTES](BLENDER-NOTES.md) · [CHANGE-BRIEF](CHANGE-BRIEF.md) · [FRICTIONAL](FRICTIONAL.md) · [SOURCES](SOURCES.md). The Assignment 2 test report is in [docs/a2/TEST-REPORT.md](docs/a2/TEST-REPORT.md).

---

## Assignment 2

A tank-battle asset slice for CSYE7270 Assignment 2. You drive **YunqiZ**, a worn olive tank with a dozer blade and a white identification stripe, through a ruined brick battlefield: hide behind cover that breaks under fire, pick your moment, and destroy all three enemy tanks.

- **Started from:** an empty Godot 4 project (see [SOURCES.md](SOURCES.md)).
- **Engine:** Godot 4.7.2 stable.
- **Film:** [Watch on Google Drive](https://drive.google.com/file/d/1wZdhVj9YaA1GIYIu9yU09Xp2JRoVltxk/view?usp=drive_link) — `claude-liam-walker-tank-gamedev.mp4` (3840×2160 landscape), SHA-256 `b13a75400f8405be572142c3ab1c4565d49f980c2c82b4a6851c6b8d074fd150`

## Run

1. Open Godot 4.7, **Import** → select `project.godot` in this folder → open.
2. Press **F5**.

Automated sound-trigger check (after opening the project once so assets are imported):

```bash
godot --headless --path . -s res://tests/test_sound_triggers.gd
```

## Controls

| Input | Action |
|---|---|
| WASD / arrow keys | Move (the hull faces the movement direction) |
| Mouse | Aim the turret |
| Left mouse button / Space | Fire (0.8 s reload) |
| Esc / P | Pause |
| **M** | Mute / unmute music |
| **N** | Mute / unmute sound effects |
| R | Play again after victory |

Music and sound are also toggled with the buttons at the top right.

## What the slice demonstrates

- **Character:** YunqiZ in 8 facings (5 generated with SDXL img2img, 3 mirrored), hull and turret as separate sprites, idle and moving states, recoil, hit flash, smoke at ≤60% health and fire at ≤30%, destruction.
- **Environment:** a generated ground tile and brick cover in three generated stages (intact, cracked after 2 hits, broken after 4 hits; broken cover no longer blocks).
- **Sound:** five generated sound effects on real events — fire, cover hit, YunqiZ hit, explosion, victory — each once per event.
- **Music:** a generated 8-bar loop at 70 BPM; pauses with the game, cuts on failure, restarts on respawn, stops at victory.
- **Loop:** three enemy tanks that move and fire back; respawn at the spawn point with destroyed enemies staying destroyed; victory screen.

## Known limitations

- Enemy tanks are the YunqiZ sprites tinted grey, not separate designs.
- Muzzle flash, explosions, smoke and fire are code particles, not generated art.
- The opening top-down zoom (storyboard panel 1) and the low-angle victory illustration (panel 8) were not built.
- The up and right turrets have no commander cupola; the other three do.
- Cannon and explosion sounds are mostly low frequency and may be quiet on laptop speakers.
- The hull snaps between 8 facings and the turret could turn more responsively.

## Documents

[CONCEPT](CONCEPT.md) · [STORYBOARD](STORYBOARD.md) · [CHARACTER-SHEET](CHARACTER-SHEET.md) · [CHANGE-BRIEF](CHANGE-BRIEF.md) · [ASSET-LOG](ASSET-LOG.md) · [TEST-REPORT](docs/a2/TEST-REPORT.md) · [SOURCES](SOURCES.md) · [FRICTIONAL](FRICTIONAL.md)
