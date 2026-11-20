# CHANGE-BRIEF — Assignment 7: Animation (walker-TANK)

Date: 2026-11-20 · Godot 4.7.2 · repository `walker-TANK`

This replaces the A6 brief (kept at tag `a6`). Later changes go in *Revisions* at the end, dated.

Project note: `project.godot` is at the repository root, so the assignment's `godot/` paths map to the root (`godot/tests/` → `tests/`, `godot/animations/` → `animations/`, `godot/shaders/` → `shaders/`). All tests run through `scripts/run-test.sh`.

## Facts this brief is built on

- Every tank (player and enemies) runs `scripts/tank.gd`; `scripts/player.gd` and `scripts/enemy.gd` extend it.
- `tank.gd` `_ready()` builds the tank's nodes in code: `hull` and `turret` (Sprite2D, scale 0.5).
- Facing is shown by swapping textures, not by rotation: `_set_sprite()` writes `texture` and `flip_h` from `_slot_for()` (8 slots, 5 textures, 3 mirrored).
- Every physics tick `_physics_process()` writes `hull.position` and `turret.position` (idle shake, moving wobble, recoil kick).
- `player.gd` `_think()` polls `Input.is_action_pressed("fire")` and calls `try_fire()`, inside `_physics_process()`.
- `try_fire()` today spawns the shell, the muzzle FX and the fire sound on the press tick; `reload_time` is 0.8 s.
- A2 made no track-rolling frames (TEST-REPORT, "Character against the sheet").

## The two clips

### Clip 1 — `track_dust` (the cycle)

- **Communicates:** the tank is driving. The hull art has no track frames, so a moving tank only wobbles; dust kicked up behind the tracks says "moving" at a glance, and stops when the tank stops.
- **Plays on:** `Dust` (Sprite2D) under `DustMount` (Node2D), children of every tank, built in `tank.gd` `_ready()`.
- **Route:** Sprite2D with an AnimationPlayer frame track.
- **Why this route:** the AnimationPlayer read-back sees the frame track, and one AnimationPlayer owns the sprite.
- **Authority:** `MotionAnim` (AnimationPlayer, child of the tank), played only by `tank.gd` on entering motion state `MOVING`.

### Clip 2 — `shoot` (the committing action)

- **Communicates:** the tank fired. The whole tank sits down on its suspension and springs back, so the shot has weight in every one of the 8 facings.
- **Plays on:** cutout rig: `Suspension` (Node2D pivot, child of the tank) with `hull` and `turret` (Sprite2D) as its parts.
- **Route:** cutout rig, baked from code — `tools/bake_tank_clips.gd` builds the clip and saves it with `ResourceSaver.save()` to the committed `animations/fire_clips.tres`.
- **Why this route:** the motion is a move of parts, not a frame swap; a vertical dip reads the same in every facing, so it needs no per-direction keys.
- **Authority:** `FireAnim` (AnimationPlayer, child of the tank), played only by `tank.gd` on entering weapon state `FIRING`.

### One authority per animated node

| Node | Property | Only writer |
|---|---|---|
| `Dust` | `frame` | `MotionAnim` |
| `DustMount` | `position`, `visible` | `tank.gd` (behind the tank; visible only while `MOVING`) |
| `Suspension` | `position`, `scale` | `FireAnim` |
| `hull`, `turret` | `texture`, `flip_h`, `position` | `tank.gd` (unchanged A2 code) |
| `MotionAnim`, `FireAnim` | which clip plays | `tank.gd` state machine; `autoplay` stays empty |

Two AnimationPlayers, because one AnimationPlayer plays one clip at a time: firing while driving must not stop the dust.

## The sheet

| Field | Value |
|---|---|
| Source | written by code: `tools/make_dust_sheet.gd` (Claude, reviewed by me) |
| Author | me, with Claude |
| Licence | my own work; no third-party art; allows a public repository and a published film |
| Date checked | 2026-11-20 |
| File | `assets/game/fx/track_dust_sheet.png` (the generator output, committed with its generator) |
| Credits file | `assets/game/fx/ATTRIBUTION.md` |
| Cell size | 16 × 16 px |
| Grid | hframes = 4, vframes = 1 |
| Frame order for `track_dust` | cells 0, 1, 2, 3 |

## Cycle spec — `track_dust`

- Frame count: 4. Frame rate: 10 fps → key interval 0.1 s. Length 0.4 s.
- `Animation.step` = 0.1 s.
- Loop mode: `Animation.LOOP_LINEAR`. Update mode: `Animation.UPDATE_DISCRETE`.
- **Seam rule (frame track):** no duplicate across the wrap (last key cell 3, first key cell 0), and the gap from the last key (0.3 s) to `length` (0.4 s) equals the key interval (0.1 s).
- Each cell holds four puffs at four life stages, one stage apart, so cell 3 → cell 0 continues the emission instead of restarting it.

## Phase table — `shoot`

Frame rate: 30 fps. `Animation.step` = 1/30 s. Length 5/30 = 0.1667 s. Loop mode: `Animation.LOOP_NONE`. At 60 physics ticks per second, one frame = 2 ticks.

| Phase | Frames | Begins on frame | Key time | What the player may do | What the game reads |
|---|---|---|---|---|---|
| Startup | 1 | 0 | 0.0000 s | move and aim; "fire" ignored | reload starts (0.8 s); recoil kick starts; no shell yet |
| Active | 1 | 1 | 0.0333 s | move and aim; "fire" ignored | shell, muzzle FX and fire sound spawn (physics tick 2 after the press) |
| Recovery | 3 | 2 | 0.0667 s | move and aim; "fire" ignored | nothing new |
| (end) | — | 5 | 0.1667 s = length | weapon back to `READY`; "fire" still waits for reload | — |

Keys: `Suspension:position` (0, 0) on frame 0 → (0, 2) on frame 1 → (0, 0) on frame 5, ease-out from frame 1 (settles through recovery). `Suspension:scale` (1, 1) on frame 0 → (1.04, 0.96) on frame 1 → (1, 1) on frame 2.

Reference: the current game, played by me. Firing should feel crisp: the shell leaves almost as soon as I press fire, so startup gets one frame. Playing the A6 build, I cannot feel any recoil when the tank fires (the code kick is 3 px and fades in about 0.15 s), so the weight of the shot has to come from this clip: the tank sits down on frame 1 and settles over three recovery frames. I did not measure external footage; the frame counts are my design, to be checked in the frame strip and in play.

## State machine

Owner: `scripts/tank.gd`. No AnimationTree. Three state variables, each changed only in `tank.gd`.

| Machine | State | Clip | Transition → | Condition |
|---|---|---|---|---|
| Motion | `IDLE` | none (`MotionAnim` stopped, `DustMount` hidden) | `MOVING` | `move_dir != Vector2.ZERO` on a physics tick |
| Motion | `MOVING` | `track_dust` | `IDLE` | `move_dir == Vector2.ZERO`, or the tank dies |
| Weapon | `READY` | none | `FIRING` | `try_fire()` succeeds (alive, reload 0) |
| Weapon | `FIRING` | `shoot` | `READY` | physics tick 10 after the press (frame 5) |
| Health (A2, unchanged) | alive → hit → destroyed | none new | — | `take_damage()`, `die()`, `reset_full()` |

Interrupts during `FIRING`:

| Event | Startup | Active | Recovery |
|---|---|---|---|
| Tank is hit | shot continues | shot continues | shot continues |
| Tank is destroyed | shot continues; the shell still spawns on frame 1 | shot continues | shot continues |
| "fire" pressed again | ignored | ignored | ignored |

The weapon tick runs before the `is_dead` early return in `_physics_process()`, so a shot already committed finishes after death. A dead tank cannot start a new one (`try_fire()` checks `is_dead`).

## The two clocks

- `MotionAnim.callback_mode_process` = `AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`.
- `FireAnim.callback_mode_process` = `AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`.
- No AnimatedSprite2D is used.
- Gameplay reads the active window on the physics tick: the shell spawns from a physics-tick counter in `_physics_process()`, not from the clip.
- Largest disagreement: predicted ≤ 1 physics tick (0.0167 s), from whether the AnimationPlayer advances before or after `tank.gd` on the press tick. Measured: <测出来填>
- No method track is used.

## Boundaries

Unchanged: collision, movement, input, `reload_time`, the recoil kick, existing tests, `shaders/` (A5, hand-written), the A6 effects, `enemy.gd` AI, every other object. Presentation code may read game state; it never writes it.

Changes this brief makes:

- `tank.gd` `_ready()`: adds `Suspension` (parent of `hull` and `turret`), `DustMount`/`Dust`, `MotionAnim`, `FireAnim`.
- `tank.gd`: motion and weapon states; the shell, muzzle FX and fire sound move from the press tick to frame 1 (2 physics ticks later).
- Enemies get the same clips, because they run `tank.gd`.

Pins expected to change: any pin that reads the shell or fire sound on the press tick now sees it 2 physics ticks (1/30 s) later. Nothing else.

## Evidence split

| Rule | Checked by | How |
|---|---|---|
| Every track resolves | read-back | `track_problems()` empty for both players |
| Key times, step, loop mode, discrete, frame range, seam | read-back | tolerance half a frame period |
| Callback mode physics, autoplay empty | read-back | asserted on both players |
| State table | structure test | every clip a state requests exists; transitions driven by `Input.parse_input_event` |
| Shell on frame 1, interrupts | edge tests | input one tick before, on, after each boundary |
| Existing behaviour | pins | Step 2 pins before and after |
| Phases read as distinct | frame strip + my eyes in play | Movie Maker at 30 fps; play at normal speed and `--time-scale 0.25` |
| Dust seam, registration | my eyes, ≥ 5 wraps; strip of the cycle | |
| Over dark and light ground | my eyes | darkest and lightest ground the tank can reach |

## Frame strip

- Preview scene: `res://previews/shoot_preview.tscn` — YunqiZ on a representative stretch of the real arena ground, facing right.
- Capture at 30 fps. Trigger frame N = the frame "fire" is injected on.
  - N (startup): tank at rest, no shell
  - N + 1 (active opens): tank fully down and squashed, muzzle flash, shell at the muzzle
  - N + 2 (recovery begins): squash gone, tank rising, shell clear of the muzzle
  - N + 5 (end): tank at rest

## Predicted failures

1. **The agent writes the Godot 3 `loop = true`, so `track_dust` plays once and stops.** The property loads without complaint and `loop_mode` stays `LOOP_NONE`. Caught by the read-back assertion "track_dust loops LINEAR", and confirmed by mutation 2 (flip the cycle's loop mode).
2. **The dust disappears on light ground.** The dust colour sits between the mud and the broken brick, so on the lightest stretch of the arena it may not separate. Caught by my human check "against the background": drive over the darkest and the lightest ground and look.
3. **The dip is too small to see in play.** 2 px down and a 4 % squash for one frame may be lost at game size and normal speed. Caught by the frame strip (frame N + 1 against N) and by playing at normal speed and at `--time-scale 0.25`. If it does not read, I change the phase table or the key values in a tuning revision, not the gameplay timing.

## Answers

*Provenance: Claude explained each concept in chat; I restated questions 1–5 in my own notes (Chinese), and Claude wrote them up in English with question 6. I reviewed every answer and agree with it. See FRICTIONAL.md.*

1. **Routes, and what each read-back sees.** Both clips are on AnimationPlayers (`MotionAnim` frame track, `FireAnim` baked cutout rig), so the AnimationPlayer read-back checks every track of both. If the dust used an AnimatedSprite2D instead, it would sit outside any AnimationPlayer: this read-back would never see it, and I would need a separate check against its SpriteFrames.
2. **Frame track left on continuous updates.** `frame` is an integer, and continuous updates interpolate between keys. The worst place is the wrap: going from the last key (cell 3) back to the first (cell 0) it interpolates through 2 and 1, so the dust flashes backwards once per loop. Discrete updates jump straight to each key's cell.
3. **Animation.step.** `shoot` is at 30 fps, so its step is 1/30 s, which is also the default. `track_dust` is at 10 fps, so its step is 0.1 s. Left at the default 1/30, its keys would still land (0.1 s is 3 × 1/30), but the editor would snap edits to 1/30 s points that are not dust frames, so a hand-edited key could fall between two frames. The read-back asserts step = 0.1 s.
4. **The one authority.** `Dust.frame` is written only by `MotionAnim`; `Suspension.position` and `.scale` only by `FireAnim`; `hull` and `turret` only by `tank.gd`. The likeliest second writer is the per-tick position code in `tank.gd` `_physics_process()`: if it were pointed at `Suspension` instead of `hull`/`turret`, two writers would fight over one node and the one that runs last in the tick would win.
5. **The two clocks.** Both AnimationPlayers advance on the physics tick (`ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`), and gameplay reads the active window on the physics tick (the shell spawns from a tick counter in `_physics_process()`). The largest disagreement I expect is one physics tick, 1/60 s ≈ 0.017 s, from which of them updates first on the press tick; I will measure it.
6. **Seam rule for the cycle.** No cell repeats across the wrap, and the gap from the last key to `length` equals one key interval (0.1 s). A duplicated frame (0, 1, 2, 3, 0 with another 0 at the start) would show cell 0 for two intervals, so the dust would hitch once every 0.4 s.
7. **Imported rig loop mode.** Not applicable: the rig is not imported. Its clip is baked from code into `animations/fire_clips.tres`, so there is no importer to overwrite it on reimport.

## Revisions
