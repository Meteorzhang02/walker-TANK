# TEST-REPORT — Assignment 7: Animation (walker-TANK)

- **Source revision tested:** `4f88f1b` (the revision the film shows). Later commits add documentation and film records only.
- **Engine:** Godot 4.7.2 stable, Forward+, Windows 11, Git Bash. Every run goes through `scripts/run-test.sh` (A7 wrapper: also fails on `Failed loading resource`).
- **Earlier reports:** A6 in `docs/a6/TEST-REPORT-a6.md`, A5 in `docs/a5/`.
- "N resources still in use at exit" and "ObjectDB instances were leaked" messages appear on some runs before and after A7; they are not failures (A6 README).

## Baseline — every earlier suite, before and after

Before: `logs/a7-baseline.txt` (commit `0c10f5d`, before any A7 code). After: `logs/a7-after-fix.txt` (after wiring and its fixes).

| Suite | Mode | Before | After |
|---|---|---|---|
| test_hit_flash | 30 / 60 / 144 | 50 / 50 / 50 | 50 / 50 / 50 |
| test_materials | 60 | 76 | 76 |
| check_tools_parse | 60 | 9 | 9 |
| check_a3_assets | 60 | PASS (0 failures) | PASS (0 failures) |
| test_sound_triggers | 60 | 0 failed | 0 failed |
| test_cover_hit_burst_config | 60 | 128 | 128 |
| test_cover_hit_burst_state | 30 / 60 / 144 | 82 / 82 / 82 | 82 / 82 / 82 |
| test_damage_smoke_config | 60 | 76 | 76 |
| test_damage_smoke_state | 30 / 60 / 144 | 81 / 81 / 81 | 81 / 81 / 81 |

**Regressions found on the way, and how each was resolved.** After wiring, my own full run (`logs/a7-after-wiring.txt`) found two suites the agent had not run and had said would survive:

- `test_cover_hit_burst_state` 79/2: it takes "the newest shell" when `fired` arrives, and `fired` came two ticks before its shell. **Game fix:** `fired` is now emitted on frame 1 with the shell (`prompts/a7/fix_shot_capture.py`).
- `test_hit_flash` 17/1, stopping early: the test freezes every enemy (`PROCESS_MODE_DISABLED`, line 205), and the shell now leaves on the shooter's own physics tick, so it never left. Also, with the aim read on frame 1, the enemy AI could re-aim during startup. **Game fix:** the muzzle position and aim are captured on the press tick (same script). **Test edit:** the frozen enemy runs from its press until the hit, with `target = null` (`prompts/a7/fix_hit_flash_test.py`, 5 added lines, nothing removed). Its old check "enemy try_fire() spawns a shell" only checked the return value, so it passed while no shell appeared.
- `test_sound_triggers` (A4): counted the fire sound on the press tick. **Test edit (agent, session 5b):** four added lines wait for the weapon to leave FIRING before counting. This is the change the brief predicted ("any pin that reads the shell or fire sound on the press tick now sees it 2 physics ticks later").

## Pins — before and after

`tests/test_pins.gd`, at 60, driving `scenes/main.tscn` through `Input.parse_input_event`.

| | Result | Commit |
|---|---|---|
| Before any clip was wired | 11 passed, 0 failed | pins commit |
| After wiring | 8 passed, 3 failed: PIN-1 (shells 2/50/98 instead of 0/48/96), PIN-2 (2 instead of 0), PIN-4 (2 instead of 0) | `6600d89` |
| After re-pin | 11 passed, 0 failed | `f12f9f9` |

Every pin that changed moved by +2 physics ticks, which the brief predicted: the shell, muzzle FX and fire sound now come on frame 1 at 30 fps. PIN-3 (reload interval 48 ticks), PIN-0 (input latency 1 tick at 60) and every other pin did not change. The re-pin is its own commit, with `SHOT_DELAY_TICKS := 2` and its reason in a comment.

## Read-back — both clips

`tests/test_clip_readback.gd`, at 60: **49 passed, 0 failed.** It instantiates `scripts/tank.gd` and reads both AnimationPlayers.

- **Tracks:** `track_problems()` (from the assignment) resolves every track of `MotionAnim` and `FireAnim` to a real node and property.
- **Key times:** `track_dust` keys at 0, 0.1, 0.2, 0.3 s; `shoot` position keys on frames 0, 1, 5 and scale keys on frames 0, 1, 2 at 30 fps; tolerance half a frame period (the saved times are 32-bit floats, e.g. `0.033333335`).
- **Step:** 0.1 s for `track_dust`, 1/30 s for `shoot`.
- **Loop mode:** `LOOP_LINEAR` for `track_dust`, `LOOP_NONE` for `shoot`.
- **Update mode:** discrete for the `Dust.frame` track (only value tracks are asked).
- **Frame range:** every frame key inside `hframes * vframes` = 4; the sheet is sliced 4 × 1.
- **Seam:** no duplicate cell across the wrap, and the gap from the last key to `length` is one interval.
- Also: both players use `ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`, and `autoplay` is empty.

## Mutations — each in its own git worktree

Scripts: `prompts/a7/run_mutations.sh`, `prompts/a7/run_mutations_2.sh`. Log: `logs/a7-mutations.txt`, per-run logs `logs/mutation_*.log`. Each run: fresh worktree at HEAD, `--import`, control run (must pass), one-line edit, the test that should catch it.

| # | Mutation | Test | Control | Mutated | Caught by |
|---|---|---|---|---|---|
| Assignment 1 (M5) | track subname `Dust:frame` → `Dust:frames` | read-back | 0 | **1** | `track_problems`: "every track resolves (1 problems)" |
| Assignment 2 (M2) | `track_dust` loop mode → `LOOP_NONE` | read-back | 0 | **1** | "track_dust loops LINEAR" (brief prediction 1) |
| Assignment 3 (M6) | last frame key → cell 4 = `hframes * vframes` | read-back | 0 | **1** | "key 3 = cell 3" and "key 3 inside the sheet" |
| Assignment 4 (M7) | rig from an empty cache: fresh worktree, no `.godot`, `--import`, read-back | read-back | — | **0, as expected** | Did not fail, and should not: the rig is baked by `tools/bake_tank_clips.gd` into the committed `animations/fire_clips.tres`; its loop mode is in that resource, and no importer holds it. |
| Extra (M1) | track node path `Dust` → `Dustt` | read-back | 0 | **1** | `track_problems` |
| Extra (M3) | `Dust.frame` track → continuous | read-back | 0 | **1** | "track_dust discrete" |
| Extra (M4) | `SHOOT_ACTIVE_FRAME` 1 → 2 | anim_states / pins | 0 / 0 | **1 / 1** | 11 anim_states checks (W3–W5, G1, F2, every hit and death case); PIN-1/2/4 |

**Blind spot found by M4:** check C1 (two clocks) compares the absolute gap, so when the shell moved from one tick *before* the clip's frame 1 to one tick *after*, C1 still passed. It checks the size of the gap, not its order.

## Fresh cache

M7 above: in a fresh worktree with no `.godot`, `--import` then the read-back gives 49/0. Every other mutation's control run also started from an empty cache and passed.

## State machine

`tests/test_anim_states.gd` (agent wrote, I ran): **34 passed, 0 failed at 30, 60 and 144.**

- **Structure:** both clips each state requests exist on the right player; `MotionAnim` plays `track_dust` only while MOVING and is stopped with the dust hidden on IDLE and on death; `FireAnim` plays `shoot` from its start on entering FIRING; weapon READY again on P+10.
- **Real input:** moving and firing go through `Input.parse_input_event` only. The press tick P is read from the game (first FIRING tick), because the input latency is 1 tick at 60 and 144 and 2 ticks at 30 (two physics ticks per frame).
- **Direct calls, by decision:** `take_damage()` for hits and deaths, as `test_hit_flash.gd` does; and in G1 only, `reload_left = 0.0` each tick, because the 48-tick reload otherwise hides the FIRING guard.

## Edges — every phase boundary, before, on and after

`tests/test_anim_edges.gd` (agent wrote, I ran): **27 passed, 0 failed at 30, 60 and 144.** Boundaries derived from `tank.gd` constants: P+2 (startup → active), P+4 (active → recovery), P+10 (end). Each interrupt injected one tick before, on and one tick after each boundary:

- **Hit** (non-fatal `take_damage`): the shell appears once on P+2, READY on P+10, health 100 → 75.
- **Death** (fatal `take_damage`): the shell still appears once on P+2, READY on P+10, and the dead tank never starts a new shot.
- **Second "fire"** (reload held at 0): seen on P+1..P+9 → no shell, `shoot` not restarted; seen on P+10 or later → a new shot.

**Findings:** at 30 fps a press lasts two physics ticks and lands on even ticks, so presses aimed at P+9 and P+11 are seen on P+8 and P+10; each line prints the tick the game actually saw. With the reload forced to 0, a shot starting on P+10 does not replay `shoot` (the first is still finishing). In play this cannot happen, because the reload (48 ticks) is longer than the clip (10 ticks).

## Frame strips (FIXTURE captures)

Captured by me with Movie Maker, windowed, `--fixed-fps 30`, from `previews/shoot_preview.tscn` (4× zoom on YunqiZ, scripted input). All are fixtures.

- `captures/shoot_strip_v1.png` (and the boundary frames in `captures/shoot_r0/`): frames N..N+5 of `shoot`.
- `captures/dust_strip_v1.png`, `_v2.png`, `_v3.png`: frames 70–75 while driving right, before and after TUNING revisions 1 and 2.

## Human checks (my own play)

- **Cycle seam:** `track_dust` played while driving for many seconds (one wrap = 0.4 s, so far more than five wraps) at normal speed: no stutter, no jump.
- **The action in play:** fired many times at normal speed and at `--time-scale 0.25`: the dip and squash read on the shot, and the tank settles back. I did not time a hit, a death or a second press by hand into each 1/30 s phase; at that size a hand-timed interrupt per phase is not practical, so the per-phase interrupts rest on the edge tests and on the film's scripted-input captures, which show each one in the real game.
- **Registration:** in `dust_strip_v3.png` the puffs stay just behind the hull from frame to frame. In play, after revision 2, I drove in all 8 facings: the dust is behind the rear of the hull in every one.
- **Against the background:** the arena ground is one brown cobble tile everywhere the tank drives. Before revision 1 the brown dust blended into it (brief prediction 2 happened); after revisions 1 and 2 it is visible on it. My first quick answer had been that the dust was visible; looking again carefully, it was not. TUNING.md records both.
- **Brief prediction 3** (the dip too small to see) did **not** happen: the dip reads in play at normal speed.

## Two clocks

Both AnimationPlayers advance on the physics tick (`ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`); gameplay reads the active window on the physics tick (a tick counter in `tank.gd` `_weapon_tick()`). Measured by `test_anim_states.gd` check C1, 5 runs at each of 30, 60 and 144: the shell on P+2, `FireAnim` first reaches the frame-1 key on P+3. **Largest disagreement: 1 physics tick = 0.0167 s**, identical in every run; within the brief's prediction (CHANGE-BRIEF.md Revisions). At 30 fps both land in the same rendered frame N+1, so the strip cannot show it.

## Claude against me

- **Squash, strip v1:** Claude measured the hull height dropping from 105 to 100 px at 4× zoom, about 5 %, "slight". I first agreed, then looked again carefully and judged the squash clearly visible. **I disagreed and kept `shoot` unchanged.**
- **Dust, strip v2:** I said it was faintly visible. Claude measured the strip and found no dust pixel in any frame, and traced it to `DUST_BEHIND` hiding the dust under the hull. I accepted that, and strip v3 plus play confirmed it.
- **Aim on the active tick:** Claude chat recommended reading the aim on frame 1. `test_hit_flash` showed it was wrong (the AI re-aimed during startup); it was reversed to capture the aim on the press tick.

## Agent mistakes I caught

- The planning agent said `test_hit_flash` and `test_cover_hit_burst_state` would survive and did not run them; my full run found both failing.
- It wrote an unrequested `logs/_run_all.sh` outside its scope (deleted unused).
- Its `DUST_BEHIND` of 14 px was a guess, marked as a human check; it hid the dust under the hull.
- It ran `check_tools_parse.gd` as a check of the preview, but that test only loads three fixed tool scripts; it said so itself.

## What no headless run can show

Whether the dip reads, whether the dust is visible against the ground, whether the cycle stutters, and whether the shot feels crisp. Headless uses a dummy renderer and draws nothing; those are the human checks above.
