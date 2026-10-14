# CHANGE-BRIEF — walker-TANK

The plan and predictions for the Assignment 2 asset slice, written before the first generation.

## Slice scope

One small arena with destructible cover and **three enemy tanks that move and fire back**. The player drives YunqiZ, fires from cover, takes damage, can be destroyed and respawn at the spawn point, and wins by destroying all three enemies.

- **Storyboard panels the slice covers:** 2, 3, 4, 5, 6, 7, 8.
- **Panel 1 (top-down opening zoom):** stretch goal. If it is not built, the slice starts directly in the gameplay view, and TEST-REPORT.md names panel 1 as not covered.

## Asset list

"Source" says how each asset is planned to be made. Every art, sound and music category includes at least one asset from a generative model.

### Art

| ID | Asset | Panels | Source |
|---|---|---|---|
| `CHAR-hull` | YunqiZ hull, 5 generated directions (3 mirrored) | 2–7 | Generative model |
| `CHAR-turret` | YunqiZ turret, 5 generated directions (3 mirrored) | 2–7 | Generative model |
| `CHAR-move` | Track-rolling frames for the hull (moving state) | 3, 7 | Generative model, edited into frames |
| `CHAR-recoil` | Hull jolt after firing | 2 | Hull sprite offset in code (no new image) |
| `CHAR-destroyed` | YunqiZ wreck, 1 direction | 6 | Generative model |
| `CHAR-victory` | YunqiZ, hatch open, flag raised, low angle | 8 | Generative model |
| `FX-muzzle` | Muzzle flash overlay | 2 | Generative model |
| `FX-hit` | Hit flash overlay | 5 | Code (white flash shader) |
| `FX-smoke` | Smoke overlay (medium health) | 5 | Generative model (fallback: Godot particles) |
| `FX-burn` | Fire overlay (low health) | 5 | Generative model (fallback: Godot particles) |
| `FX-explosion` | Explosion frames | 4, 6 | Generative model |
| `ENEMY-tank` | Enemy tank hull and turret, 5 directions each | 2–4, 7 | Generative model |
| `ENEMY-wreck` | Enemy wreck | 4, 7 | Edited from `ENEMY-tank` (darkened, damaged) |
| `ENV-ground` | Mud and broken-brick ground tile | 2–7 | Generative model |
| `ENV-cover` | Cover block in three stages: intact, cracked, broken | 2, 3, 6, 7 | Generative model |
| `PROJ-shell` | Shell projectile | 2, 3 | Code-drawn |
| `UI-health` | Health bar | 5 | Godot UI (code) |
| `UI-victory` | Victory screen layout | 8 | Godot UI (code) around `CHAR-victory` |

### Sound effects

| ID | Sound | Panels | Source |
|---|---|---|---|
| `SFX-fire` | Deep, heavy cannon shot | 2 | Generative model |
| `SFX-cover-hit` | Stone and brick crumbling | 3 | Generative model |
| `SFX-player-hit` | Sharp metallic impact | 5 | Generative model |
| `SFX-explode` | Tank explosion with a long fading tail | 4, 6 | Generative model |
| `SFX-victory` | Short, restrained victory sound | 8 | Generative model |

### Music

| ID | Music | Panels | Source |
|---|---|---|---|
| `MUS-battle-loop` | Low, slow loop built on drums and bass | 2–7 | Generative model, trimmed to a bar-aligned loop |

## Event-to-sound map

Each sound plays from the code that already represents its event. Game state changes first; the sound only reports it, so a muted or missing sound changes nothing.

| Sound | Exact triggering event | How double triggers are prevented |
|---|---|---|
| `SFX-fire` | The player's fire function spawns a shell, after the reload check passes | Reload timer (about 0.8 s): if it is still running, no shell spawns and no sound plays. |
| `SFX-cover-hit` | A shell collides with a cover block and the block's stage is reduced | The shell is marked `has_hit` and freed on its first collision, so one shell gives one hit and one sound. |
| `SFX-player-hit` | YunqiZ's `take_damage()` reduces health and health is still above zero | A short invulnerability window (about 0.3 s) ignores repeat hits; no hit sound when the hit is the fatal one. |
| `SFX-explode` | A tank's `die()` runs (enemy or YunqiZ) | `die()` returns at once if `is_dead` is already true; `is_dead` is set before the sound plays. |
| `SFX-victory` | The enemy counter reaches zero | A `level_won` flag is checked and set before the sound plays, so the counter cannot fire it twice. |

Enemy cannon fire reuses `SFX-fire` at lower volume and pitch. It is not counted as one of the four required events.

## Music behavior

- **During play:** `MUS-battle-loop` loops continuously and does not change.
- **Pause:** the music pauses and resumes from the same point when play resumes.
- **Failure (YunqiZ destroyed):** the music stops immediately; `SFX-explode` keeps playing on the effects bus, so only the explosion tail is heard.
- **Respawn:** the music restarts from the beginning.
- **Success (an enemy destroyed):** no change to the music.
- **End of the slice (all enemies destroyed):** the music stops, `SFX-victory` plays, and the victory screen appears.
- **Mute:** music and effects are on separate audio buses (`Music`, `SFX`), each with its own mute key and on-screen toggle.

## Predicted failure cases and how I will check them

1. **Generated directions drift in proportion.** The five hull and turret directions may come out with different sizes, barrel lengths or stripe positions. *Check:* place each direction over `turnaround.png` at the same height; reject any that break the consistency rules in CHARACTER-SHEET.md.
2. **Turret and hull do not line up when combined.** The turret pivot may sit in a different place on each hull direction. *Check:* in Godot, rotate through all 8 hull directions with the turret aimed in all 8 directions and screenshot the grid.
3. **Up and down facings look the same at game size.** The first silhouette test already showed this; the design now adds a front dozer blade and a rear storage box. *Risk:* the generative model may drop, shrink or move the blade or box. *Check:* redo the silhouette test at 64 px on every generated hull direction, and reject any where the blade and box are missing or the facing cannot be read.
4. **Mirrored directions show a reversed number.** *Check:* screenshot the three mirrored directions in-game and confirm no reversed digits are visible.
5. **YunqiZ disappears against the ground.** The tank and ground are both desaturated. *Check:* screenshot YunqiZ on `ENV-ground` in normal color and in grayscale; the white stripe and outline must still separate it.
6. **Realistic detail turns to noise at game size.** *Check:* view every accepted sprite at 100% in-game scale, not only enlarged; simplify or reject sprites whose shape is lost.
7. **A sound fires twice on one event.** For example, rapid fire, or two shells hitting cover at once. *Check:* an automated test that counts calls to each sound per event while simulating rapid input and simultaneous hits.
8. **The music loop clicks at the seam.** *Check:* listen through at least three loops on headphones and look at the waveform at the loop point.
9. **The slice is unreadable when muted.** *Check:* a full muted playthrough; firing, cover damage, player damage, failure and victory must all be visible.

## Authorship note

I chose the full slice scope (enemies that move and fire, failure and respawn). Claude drafted this brief from CONCEPT.md, CHARACTER-SHEET.md and STORYBOARD.md, and proposed the source plan for each asset, the double-trigger rules (reload timer, `has_hit`, invulnerability window, `is_dead`, `level_won`), pausing and resuming the music, separate audio buses, reusing `SFX-fire` for enemies, panel 1 as a stretch goal, and the predicted failure cases (several of them came from risks found while drafting the earlier documents).


## Revisions and outcomes (appended after building the slice)

- **Asset sources changed:** `ENEMY-tank` and `ENEMY-wreck` are YunqiZ tinted in code; `CHAR-move` is a code wobble; `CHAR-destroyed` is the darkened sprite; `CHAR-victory` and `FX-*` are not generated (code particles). Panel 1 was not built.
- **Sound map held:** reload timer, `has_hit`, 0.3 s invulnerability, `is_dead` and `level_won` were implemented as planned; the automated check confirms one sound per event.
- **Predicted failures, outcome:** (1) drift — held, IoU 0.99 hull / 0.97–0.98 turret; (2) turret alignment — holds at the fixed pivot offset; (3) up/down — fixed by the blade and box; (4) mirrored number — avoided, no number; (5) blending into the ground — happened for the cover on the raw ground, fixed by calming the ground; (6) detail at game size — held; (7) double triggers — none, automated check passes; (8) loop click — loop cut at a bar boundary with a crossfade, no click heard; (9) muted readability — passes.
