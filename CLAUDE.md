# CLAUDE.md — walker-TANK

No `AGENTS.md` exists in the repository, so there is no `@AGENTS.md` line.

## Project context

- **Engine:** Godot 4.7.2 stable (`README.md` line 6; `scripts/run-test.sh` line 7 runs `Godot_v4.7.2-stable_win64_console.exe`). `project.godot` line 19 (`config/features=PackedStringArray("4.7")`).
- **Renderer:** Forward+, the engine default: `project.godot` has no `rendering/` section (`README.md` line 6 says "Forward+ (engine default)"). Human-confirmed in Project Settings, 2026-10-27.
- **Layout:** `project.godot` is at the repository root; there is no `godot/` folder. Brief paths map to `tests/`, `animations/`, `shaders/` (`CHANGE-BRIEF.md` line 7). `animations/` does not exist yet. Neither do `tools/bake_tank_clips.gd`, `tools/make_dust_sheet.gd`, `assets/game/fx/` or `previews/shoot_preview.tscn`; the brief names them.
- **2D:** viewport 1280×720, stretch `canvas_items` (`project.godot` lines 23–25). Main scene `res://scenes/main.tscn` (`project.godot` line 18): one `Node2D` with `scripts/main.gd` (`scenes/main.tscn` lines 5–6).
- **Clip 1, `track_dust` (brief lines 21–28, 63–69):** Sprite2D `Dust` under Node2D `DustMount`, driven by an AnimationPlayer `MotionAnim` with a `frame` track. Sheet `assets/game/fx/track_dust_sheet.png`, 4×1 cells of 16×16, 10 fps, looping.
- **Clip 2, `shoot` (brief lines 30–36, 71–82):** cutout rig. `Suspension` (Node2D) holds `hull` and `turret`; AnimationPlayer `FireAnim` plays the clip, baked by `tools/bake_tank_clips.gd` into `animations/fire_clips.tres`. 30 fps, length 5/30 s, no loop.
- **State machine owner:** `scripts/tank.gd`. No AnimationTree, no AnimatedSprite2D (brief line 88). The three state variables are changed only there (brief line 88).
- **Tank code today (nothing of A7 exists yet):** `tank.gd` `_ready()` (line 42) adds `hull` (lines 54–56) and `turret` (lines 57–60) as direct children, plus `smoke` (line 61) and `flames` (line 64). `_physics_process()` is line 116; it returns on `is_dead` at lines 120–121, then calls `_think()`. It writes `hull.position` and `turret.position` at lines 132–133. `try_fire()` is line 143; it spawns the shell, muzzle FX and fire sound on the press tick (lines 148–151).
- **Tank classes:** `scripts/player.gd` (YunqiZ) and `scripts/enemy.gd` extend `tank.gd` (line 1 of each). `player.gd` `_think()` (line 7) polls `Input.is_action_pressed("fire")` (line 13) and calls `try_fire()`. `enemy.gd` calls `try_fire()` at line 32. `move_dir` is set in `_think()` (`player.gd` line 11, `enemy.gd` line 27).
- **Scenes the clips appear in:** `scenes/main.tscn` — `main.gd` builds the player (lines 71–76) and three enemies (lines 80–93) under `World/Actors` (lines 53–56). `scenes/gallery.tscn` — `scripts/gallery.gd` preloads `tank.gd` and `enemy.gd` (lines 5–6) and builds tanks with them. Previews (`previews/`, `effects/`) hold A6 files only.
- **A5/A6 code on the tank:** `scripts/hit_flash_driver.gd` is attached to YunqiZ only (`main.gd` line 79) and drives the ShaderMaterial shared by `hull` and `turret`. `tank.gd` instances `effects/damage_smoke.tscn` as `smoke` (A6). `smoke` and `flames` stay direct children of the tank; only `hull` and `turret` move under `Suspension`.
- **Tests, always through the wrapper.** Usage is `scripts/run-test.sh <file-in-tests/> <fps|realtime> [timeout-seconds]` (line 2). It runs `--headless --path . --script res://tests/<file>`. A number adds `--fixed-fps <n>` and logs to `logs/<name>_<n>fps.log`. `realtime` adds no fps flag and logs to `logs/<name>_realtime.log` (lines 8–13). The timeout is the third argument, default 120 s (line 14). The exit status is Godot's, forced to 1 if the log has `SHADER ERROR`, `SCRIPT ERROR` or `Failed loading resource` (line 16). `GODOT=` overrides the exe path (line 7). Git Bash, repo root:

```bash
bash scripts/run-test.sh test_hit_flash.gd 30      # also 60, 144   (50 passed)
bash scripts/run-test.sh test_materials.gd 60                      # 76
bash scripts/run-test.sh check_tools_parse.gd 60                   # 9
bash scripts/run-test.sh check_a3_assets.gd 60                    # PASS (0 failures)
bash scripts/run-test.sh test_sound_triggers.gd 60                 # RESULT: 0 failed
bash scripts/run-test.sh test_cover_hit_burst_config.gd 60         # 128
bash scripts/run-test.sh test_cover_hit_burst_state.gd 30          # also 60, 144 (82)
bash scripts/run-test.sh test_damage_smoke_config.gd 60            # 76
bash scripts/run-test.sh test_damage_smoke_state.gd 30             # also 60, 144 (81)
bash scripts/run-test.sh <test>.gd realtime 180                    # realtime mode, optional timeout
```

- Baseline: `logs/a7-baseline.txt` (all runs exit 0, counts as above). "N resources still in use at exit" is not a failure. Every test is `extends SceneTree` and `quit(1)` on a failure (e.g. `test_hit_flash.gd` line 60).

## Headless facts

- A headless run uses a dummy renderer: it draws nothing. Tests prove node state, properties and timing, never what the screen shows. Every look is a human check recorded in `TEST-REPORT.md`.
- Headless does report shader parse errors: a deleted semicolon in `shaders/hit_flash.gdshader` printed `SHADER ERROR` and exited 1 (`logs/mutation1_semicolon_60fps.log`).
- Headless `realtime` runs are paced at about 1/144 s, so frame time prices nothing; GPU render time reads 0 headless (`tests/price_measure.gd`).
- Headless window is 64×64, so mouse positions need `get_final_transform()`. `process_mode = DISABLED` removes a body from physics; use KEEP_ACTIVE.
- A headless run advances clips and reads their structure (tracks, keys, `step`, `loop_mode`, `current_animation`); it draws nothing, so it never shows whether motion reads.
- Key times are saved as 32-bit floats (`0.033333335` in `animations/fire_clips.tres`): compare with half a frame period, never `==`.
- `value_track_get_update_mode()` is asked only of value tracks (`tests/test_clip_readback.gd`).
- `Input.parse_input_event` is buffered: the game sees an injected action 1 tick later at 60/144 and 2 ticks later at `--fixed-fps 30` (`tests/test_pins.gd` PIN-0, `tests/test_anim_states.gd`).
- Frame strips come from a windowed Movie Maker run of `previews/shoot_preview.tscn`, which I start; it moves the real mouse.

## Current change

@CHANGE-BRIEF.md

## Ownership

- Every file in `shaders/` is hand-written by the human. An agent never creates, edits, reformats or "fixes" a file in `shaders/`. If a shader looks wrong, report it and stop. `shaders/standard_generated.gdshader` and `shaders/particles_generated.gdshader` are saved by the human from Godot's converters.
- Clips live as resources in `animations/` or in the scene that owns them, and are never built in code at runtime. Building one in `tools/bake_tank_clips.gd` and saving it with `ResourceSaver.save()` is the brief's route; `tank.gd` loads the saved resource and only plays it.
- `CHANGE-BRIEF.md` is the human's spec. Its original text is never edited; changes go only under *Revisions*, dated, and only when the human asks. `LANGUAGE-NOTES.md` is written by the human.

## One authority

Exactly one node writes each animated property (brief lines 38–45). Never add a second writer to a node that has one.

- `Dust.frame`: only `MotionAnim`.
- `DustMount.position` and `.visible`: only `tank.gd` (behind the tank; visible only while `MOVING`).
- `Suspension.position` and `.scale`: only `FireAnim`. Do not point the per-tick position code in `tank.gd` at `Suspension`.
- `hull`, `turret` `texture`, `flip_h`, `position`: only `tank.gd` (the A2 code, lines 126–133, unchanged).
- Which clip plays on `MotionAnim` and `FireAnim`: only the `tank.gd` state machine. `autoplay` stays empty.
- Two AnimationPlayers, so firing while driving does not stop the dust.

## Godot 4 names

- Use `AnimationPlayer`, `Animation`, `AnimationLibrary`, `Sprite2D` with `hframes` / `vframes` / `frame`. Never `AnimatedSprite` (Godot 3) and, by the brief, no `AnimatedSprite2D` either.
- Loop is `Animation.loop_mode` with `Animation.LOOP_NONE` / `LOOP_LINEAR`. Never the Godot 3 boolean `loop`; it loads without error and changes nothing (brief line 154). Always read `loop_mode` back.
- Speed is `AnimationPlayer.speed_scale`, never `playback_speed`. Frame length is `Animation.step` and `Animation.length`.
- Callback clock: `callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS` (brief lines 110–111). Update mode `Animation.UPDATE_DISCRETE` for the frame track.
- Particle names from A6 still apply: `CPUParticles2D`, `GPUParticles2D`, `ParticleProcessMaterial`, the `_min` / `_max` pairs, never Godot 3 `Particles2D` / `ParticlesMaterial`.
- `track_problems()` is a helper in `tests/test_clip_readback.gd`, taken from the assignment; it is not an engine name.
- Not yet checked in this build: `AnimationPlayer.autoplay`, `AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`, `Animation.step`, `value_track_set_update_mode()`. `tests/test_clip_readback.gd` reads each one back; until it passes, say so instead of guessing.

## Out of scope

- Do not change `collision`, movement, input, `reload_time`, the recoil kick, enemy AI, HUD, audio, music, pause handling or the victory screen (brief line 119).
- Do not change `shaders/`, the A5 hit flash and `hit_flash_driver.gd`, the A6 effects in `effects/`, `project.godot`, `scripts/run-test.sh`, or the existing tests and their expectations.
- Health stays as it is: `take_damage()`, `die()`, `reset_full()` and `modulate`. Presentation code may read game state; it never writes it.
- The one intended gameplay change: the shell, muzzle FX and fire sound move from the press tick to frame 1, two physics ticks later (brief line 127). Pins that read them on the press tick may change by that and nothing else.
- No new clips beyond `track_dust` and `shoot`, no AnimationTree, no method track, no 3D scene change.

## Unconfirmed

- Whether `test_hit_flash.gd` (line 239) and `test_sound_triggers.gd` (lines 32, 36) still pass with the shell and sound two ticks late. The brief expects pin changes (line 127); I did not read those tests in full.
- The clock disagreement is unmeasured: the brief has a placeholder (line 114).
- The weapon tick that runs before the `is_dead` return (brief) does not exist yet; it is added in the wiring step. Today the return is at `tank.gd` lines 120–121.
- `scripts/audio.gd` and the older tests were read only for headers, `quit()` lines and scene loads. Test commands assume Git Bash with GNU `timeout`.
