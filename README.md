# walker-TANK

A tank-battle asset slice for CSYE7270 Assignment 2. You drive **YunqiZ**, a worn olive tank with a dozer blade and a white identification stripe, through a ruined brick battlefield: hide behind cover that breaks under fire, pick your moment, and destroy all three enemy tanks.

- **Started from:** an empty Godot 4 project (see [SOURCES.md](SOURCES.md)).
- **Engine:** Godot 4.7.2 stable.
- **Film:** `[course media link]` — `[filename]`, SHA-256 `[checksum]`

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

[CONCEPT](CONCEPT.md) · [STORYBOARD](STORYBOARD.md) · [CHARACTER-SHEET](CHARACTER-SHEET.md) · [CHANGE-BRIEF](CHANGE-BRIEF.md) · [ASSET-LOG](ASSET-LOG.md) · [TEST-REPORT](TEST-REPORT.md) · [SOURCES](SOURCES.md) · [FRICTIONAL](FRICTIONAL.md)
