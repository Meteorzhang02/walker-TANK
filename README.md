# walker-TANK

## Assignment 3

Assignment 3 adds a 3D asset room to this repository; the 2D game from Assignment 2 (below) is unchanged.

- **3D asset room:** `scenes/asset_room_3d.tscn` puts the three assets next to a grey 6.0 × 1.6 × 3.4 m box that stands in for the YunqiZ hull, under one light.
- **Three assets**, built from Blender cubes, 36 triangles each, exported to `assets/models/`:
  - `cover_wall` — broken brick cover wall, 4.0 × 1.0 × 1.8 m (includes one hand edit of my own)
  - `ammo_crate` — olive crate with an off-white stripe, 1.24 × 0.84 × 0.71 m
  - `tank_hedgehog` — three crossed steel beams, 1.794 × 1.794 × 1.400 m
- **Build and export scripts:** `tools/blender/build_cover_wall.py`, `build_ammo_crate.py`, `build_tank_hedgehog.py` rebuild each asset from nothing and check it; `tools/blender/export_glb.py` exports a `.blend` to `.glb`.
- **Headless check:** `tests/check_a3_assets.gd` measures each `.glb` in Godot (size, lowest Y, root scale, height axis): 18 / 18 PASS.
- **Final film:** [link to be added]

**Versions:** Godot 4.7.2 · Blender 5.2.2 LTS · MCP for Blender add-on 1.8 · Windows 11.

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
