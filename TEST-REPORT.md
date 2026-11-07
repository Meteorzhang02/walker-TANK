# TEST-REPORT — Assignment 6: particle effects

The A5 report is at [docs/a5/TEST-REPORT.md](docs/a5/TEST-REPORT.md) (and at tag a5).

**Setup.** Godot 4.7.2 stable (`ed1daf0bf`) · Forward+ · Windows 11, Git Bash · CPU 12th Gen Intel Core i7-12700H · GPU NVIDIA GeForce RTX 3060 Laptop GPU. Godot's startup line reads "Vulkan 1.4.325 - Forward+ - Using Device #0: NVIDIA - NVIDIA GeForce RTX 3060 Laptop GPU". The internal display runs at 144 Hz, and the game window at 1280 × 720.

**Game source revision.** The game source (effects and scripts) last changed at `96d38be` (Effect B r1). Every later commit touches only tests, previews, logs and docs.

**The two effects:**

| Effect | Scene | Node | Job | Driven by |
|---|---|---|---|---|
| A, cover hit burst | `effects/cover_hit_burst.tscn` | 3 × CPUParticles2D (Flash, Debris, Dust) | a one-shot burst on a repeating event | `cover.gd` `take_hit()` (line 40) |
| B, damage smoke | `effects/damage_smoke.tscn` | GPUParticles2D + ParticleProcessMaterial | a feedback loop following health | `follow()`, called from `tank.gd` |

## Baseline (every earlier suite, before and after)

All suites run through `scripts/run-test.sh`, each in its pinned mode.

| Suite | Mode | Before (`a9513d3`) | After (final rerun) |
|---|---|---|---|
| `test_hit_flash.gd` | 30 / 60 / 144 fps | 50 / 50 / 50 | 50 / 50 / 50 |
| `test_materials.gd` | 60 fps | 76 | 76 |
| `check_tools_parse.gd` | 60 fps | 9 | 9 |
| `check_a3_assets.gd` | 60 fps | 18 | 18 |
| `test_sound_triggers.gd` | 60 fps | 8 | 8 |

Every run in both columns exits 0, and no log has `SHADER ERROR` or `SCRIPT ERROR`.

The suites were also rerun after each code step:
- Effect A wiring, `d2d50fc`;
- Effect B wiring, `7009248` and `e79d23b`;
- the final run.

The agent could not print exit codes, because compound commands are blocked by its allow list. So every exit code in this report is from my own runs.

**Leak messages are not failures.** The leak message at exit varies from run to run, with no code change in between: 15, 18, 22, 16, 6 or 4 ObjectDB instances, and 2–7 resources still in use. None of these is an error, and the cause is not investigated.

## Configuration (fixed rate, 60 fps)

| Test | Result |
|---|---|
| `test_cover_hit_burst_config.gd` | **128/128**, exit 0. It was 126 before R3 added a colour stop. |
| `test_damage_smoke_config.gd` | **76/76**, exit 0. |

`test_cover_hit_burst_config.gd` reads every value of every emitter back from the loaded scene, including:
- gravity (0, 0) on all three emitters;
- both ends of every `_min`/`_max` pair;
- the curve and colour-ramp points;
- the texture files;
- Flash's `CanvasItemMaterial` with blend ADD;
- that the root frees itself after Dust's `finished` (0.783 s).

`test_damage_smoke_config.gd` checks:
- every material value, including the Vector3 direction and gravity, the turbulence values and `visibility_rect`;
- `follow()` for h = 0.5, 0.3, 0.1, 1.0, 0.6, dead, and 1.0 after dead, against rule 1;
- that `amount` stays 48;
- that 141 other saved properties are unchanged by `follow()`.

**Effect A mutations** (`logs/a6_mutation1_godot3_name_60fps.log`, `logs/a6_mutation2_value_drift_60fps.log`):

| Mutation | Result |
|---|---|
| 1. Godot 3 name: Debris `initial_velocity_min` → `initial_velocity` | **exit 1**. The test printed `FAIL Debris.initial_velocity_min == 180.0 (got 0.0)`. Godot loaded the scene with **no warning**: the unknown name was ignored silently and the minimum fell back to 0. |
| 2. Value drift: Debris `damping_min` 400 → 300, brief unchanged | **exit 1**. The test printed `FAIL Debris.damping_min == 400.0 (got 300.0)`. |

After each mutation I restored the file, and the test was back to 126/126.

The property names were checked first, in this build, by `tests/probe_particle_props.gd` (`logs/probe_particle_props_60fps.log`):
- CPUParticles2D has no `amount_ratio`, `initial_velocity` or `scale_amount`.
- ParticleProcessMaterial **does** list a property called `initial_velocity`. So the same Godot 3 name on a GPU node might not have been caught; that is why both tests read back the `_min`/`_max` pair.

**Not done:** watching the effect with mutation 1 in place (the "it still fires" look).

## State (fixed rate, real game loop, real input)

| Test | 30 fps | 60 fps | 144 fps |
|---|---|---|---|
| `test_cover_hit_burst_state.gd` | 82 | 82 | 82 |
| `test_damage_smoke_state.gd` | 81 | 81 | 81 |

All six runs exit 0.

**Effect A** (`test_cover_hit_burst_state.gd`). YunqiZ is aimed by real mouse events and fires with a real Space key event. The second shell in P3 goes through the game's own `main.spawn_shell()`. The test never calls `spawn_cover_burst()` or `take_hit()`, except in one section labelled "R1 fallback check: direct call, not a gameplay event".

| Brief rule | What passed |
|---|---|
| 1 | No burst on load, on a tank hit, on an expired shell or on broken cover. 4 hits on one wall gave 4 bursts. Totals: 7 bursts = 7 cover hits = 7 `cover_hit` sounds. |
| 2 | Each burst is 0.000 px from its shell's drawn contact point, with exact rotation. |
| 3 | **Two events inside one lifetime:** two hits 0.317 s apart left 2 bursts alive at once. The first freed itself 0.750 s after its own start, so it was not restarted. |
| 4 | Every burst outlived its shell. |
| 5 | Under pause, `can_process()` is false and the burst still exists after 1 s paused. After unpause it finishes its remaining 0.517 s; 0.233 + 0.517 = 0.750 s, so it resumes where it was. |
| R1 fallback | `take_hit()` with no shell puts the burst at the cover + (0, −8), rotated −π/2. |

**Effect B** (`test_damage_smoke_state.gd`). Health is changed only by real shells and by `main.gd`'s own respawn timer.

| Brief rule | What passed |
|---|---|
| 7 | No smoke emitting on the first 30 frames after load. |
| 1 | YunqiZ 75 HP → off; 50 HP → 0.375; 25 HP → 0.6875; dead → 1.0. Enemy 50 HP → off; 25 HP → 0.5833; wreck → 1.0. |
| 3 | Off on the frame before the threshold hit, on as the hit returns. |
| 6 | Hiding changes nothing; a hit while hidden still sets 0.6875. |
| 5 | Under pause, `can_process()` is false and nothing changes. |
| 4 | Off on the first frame after the respawn (2.02 s after death); the wreck still smokes at 1.0. |
| 2 | `amount` stays 48, and each tank keeps the same smoke node, for all 428 frames. |
| Gallery | `scenes/gallery.tscn` loads without errors. |

**Test-only setup writes**, each labelled in the test:
- freezing enemy AI, with `disable_mode = KEEP_ACTIVE`, or with `target = null` plus INHERIT;
- moving enemy 0 into YunqiZ's line of fire;
- `visible = false`.

**What headless cannot prove:** anything drawn. The dummy renderer runs no GPU particle process. So none of these is proven here:
- that a particle is emitted at all;
- that `amount_ratio` thins the column;
- that the column fades after a stop;
- the frozen look;
- that nothing is drawn while hidden;
- turbulence, and the trail.

Those are the human checks below.

## Frame strips (fixture captures)

Every strip is a **fixture**: a preview scene rendered with Movie Maker at 30 fps, `--write-movie`, NVIDIA GPU, with a fixed seed set on the preview's instance only.

| Strip | Frames kept | Revision |
|---|---|---|
| `captures/cover_hit_burst/r0/` | 10, 12, 15, 20, 30, 50 | Effect A before tuning |
| `captures/cover_hit_burst/r1/` | same | Effect A after R3 (Debris `color_ramp`) |
| `captures/damage_smoke/r0/` | 10, 25, 58, 90, 112, 140, 165 | Effect B before tuning |
| `captures/damage_smoke/r1/` | same | Effect B after R5 (initial velocity 50/80) |

The predictions, Claude's readings and my verdicts for each are in [TUNING.md](TUNING.md). `captures/.gdignore` keeps Godot from importing the PNGs.

## In play (HUMAN CHECK)

Main scene, 1280 × 720, on the RTX 3060. My answers, as I gave them:

| Check | Result |
|---|---|
| A: four hits on one wall until it broke | done: every hit visible |
| A: firing while moving, chips on the ground | done: readable |
| A: chips go back toward the shooter | **not checked separately** |
| A: rapid repeats in normal play from several tanks | **not checked separately.** Price mode 1 shows 4–6 bursts alive at once, but that is a fixture, not normal play. |
| A: size at window size | preview: "大小合适" (the size is right) |
| B: start (taking hits until smoking) | done |
| B: denser on a further hit | "有" (yes) |
| B: trail while driving | "拖烟条" (a trail of smoke) |
| B: shape standing still | r0: "一团" (a lump). r1: "是柱子，往上升" (it is a column, it rises). See TUNING. |
| B: wreck keeps smoking | "会" (yes) |
| B: stop on respawn | headless only. Not separately checked by eye. |
| B: paused (Esc while smoking) | "对" (yes). My one-word answer also covers A's chips right after a hit. |
| B: hidden | not reachable in normal play, because tanks are never hidden. Headless only. |
| Boundaries holding | nothing else in the game changed in play. All earlier suites stay at baseline. |

## Against the background (HUMAN CHECK)

The level is one dark-brown ground tile plus brick cover. In r0 the **brick is the lighter surface** and the ground the darker one, the opposite of what I first wrote in the brief (corrected in brief R2).

- **A on the brick face:** the flash and dust carry the first frames (r0 frames 10–12).
- **A on the dark ground:** "看得清" (readable). In r0 the chips faded into the ground by frame 20. R3 fixed this; r1 frame 20 shows faint red-brown chips.
- **B:** readable over the ground, both in the preview ("看得清") and in the game. The dark base colour #4A4A48 has about the ground's value, so the dark-to-light change cannot be seen (Claude, session 7a). Not fixed.
- **B over brick:** not checked separately.

## Edge of screen (HUMAN CHECK)

Driving a smoking YunqiZ to the screen edge: the smoke does not vanish all at once ("不会"). `visibility_rect` is Rect2(−200, −220, 400, 420).

## Scene load (HUMAN CHECK)

No tank is smoking on the first frames after the main scene loads ("没有冒烟"). The headless rule 7 check agrees.

## Claude against me

| Reading | Claude said | I said or did |
|---|---|---|
| A r0 duration | (none) | I said "about one or two seconds". The strip shows it gone by frame 50, with faint dust at 0.67 s, so my look overestimated it. |
| A r0 → r1 | the chips vanish by frame 20; proposed the Debris ramp change | Approved. In the game I had found nothing to change, so A's revision is strip-driven, not driven by my observation. |
| A r1 | the prediction held only partly at frame 20 (faint, ~80 px); named chip size as the next lever | **Kept r1 and declined the next lever:** "不是纯 3D 游戏，目前状态不用纠结" (this isn't a full 3D game, no need to fuss). |
| **B r1, where we disagreed** | **"The prediction failed"**: the stills still show a lump, only 5–10 px higher | **In the running game I saw it rise: "是柱子，保留，往上升".** The fixture is a standing tank, read one still at a time, where the rise does not show. My look decides. |
| B r1 | the R5 change was "still uncommitted" | **Wrong.** I had committed it (`96d38be`) between sessions. |

## Headless CPU price

The agent's script, `tests/cost_particles.gd`, run with `run-test.sh ... realtime 300`, failed twice:
- **Frame time read 6.90 ms in every case, the empty scene included.** That is 1/144 s: the script was measuring the frame pacing, not the effects. The agent said so itself. This is the chapter's recorded mistake.
- **Its process-time means were swamped by spike frames:** sd larger than the mean, and negative differences.

`tests/price_measure.gd` (written by Claude in chat, run by me; `logs/price_measure_realtime.log`) records per-frame `Performance.TIME_PROCESS` and reports **medians**. It runs an empty control, then the price scene in modes 0 / 1 / 2 / 3 / 0. Modes are switched by real key events, with 180 warm-up and 720 sampled frames each.

| Case | Process median, ms | Difference | Prediction | Budget |
|---|---|---|---|---|
| empty control | 0.128 | | | |
| game, effects off (mode 0) | 0.181 | +0.053 over control | | |
| A peak, 4–6 bursts (mode 1) | 0.255 | **+0.074** | +0.05 – 0.15 | ≤ 0.5 ✓ |
| B peak, 4 tanks at ratio 1.0 (mode 2) | 0.172 | **−0.009 ≈ 0** | ≈ 0 | GPU node, see below |
| both (mode 3) | 0.242 | +0.061 | | |
| mode 0 again | 0.201 | +0.020 (drift) | | |

The drift between the two mode-0 runs is 0.020 ms, so differences under about 0.02 ms are noise. The headless GPU render time reads **0.000** in every case: headless does no GPU work. B's headless number is the CPU's share only.

Physics-time medians drift by up to 0.17 ms between the two mode-0 runs, so they are not used.

## GPU price (HUMAN CHECK)

**Instrument.** A windowed run on the RTX 3060 (`logs/price_measure_windowed.log`), with the same phases. GPU time is the viewport's measured render time on the GPU, from `RenderingServer.viewport_get_measured_render_time_gpu()`. That is the number the Visual Profiler shows.

I also opened the Visual Profiler in the editor's Debugger. One reading shows "Render Viewports" GPU 0.1 ms, but I did not note which mode it was in. Reading four modes by hand there was too fiddly for me, so the per-mode numbers come from the script.

| Case | GPU render median, ms | Difference over mode 0 | Prediction | Budget |
|---|---|---|---|---|
| empty control | 0.007 | | | |
| effects off (mode 0) | 0.276 | | | |
| A peak (mode 1) | 0.299 | **+0.023** | +0.01 – 0.03 | ≤ 0.2 ✓ |
| B peak (mode 2) | 0.353 | **+0.077** | +0.03 – 0.08 | ≤ 0.3 ✓ |
| both (mode 3) | 0.354 | +0.078 | | |
| mode 0 again | 0.281 | +0.005 (drift) | | |

**Monitors read:**
- FPS, from `Engine.get_frames_per_second()` on the price scene's label: **143–144 in every mode**, so with vsync on, FPS hides the cost completely;
- process time (`Performance.TIME_PROCESS`);
- render CPU and GPU time (RenderingServer).

The windowed process time is about 8 ms, close to 1/144 s, because it includes waiting for the next frame. So it is not used as a CPU price; the headless medians are.

**FPS with vsync off:** F9 in the price scene toggles vsync (`previews/price_scene.gd`). I ran the price scene, pressed F9 and read the FPS label in mode 0 and in mode 3: **143 in both**, the same as with vsync on. FPS never rose above the 144 Hz refresh rate, so the comparison is **capped** (most likely the Windows compositor; the internal display is driven by the Iris Xe) and shows nothing about the effects. GPU time is the price that counts.

## The process shader

**File.** `shaders/particles_generated.gdshader`, 490 lines. I made it from Effect B's ParticleProcessMaterial with *Convert to ShaderMaterial*, saved the shader with *Save As*, and closed the scene without saving, so the game still uses the ParticleProcessMaterial. Nothing in the game uses this file. I did the conversion in place on an unsaved scene, not on a scratch copy.

| Question | Line(s) |
|---|---|
| `shader_type` | **3**: `shader_type particles;` |
| `start()` / `process()` | **323** / **378** |
| initial velocity from its min and max | **232**: `mix(initial_linear_velocity_min, initial_linear_velocity_max, rand_from_seed(alt_seed))`. Line **365** in `start()` sets the first velocity: `USERDATA1.xyz = get_random_direction_from_spread(alt_seed, spread) * dynamic_params.initial_velocity_multiplier;` |
| where gravity changes velocity | **412** `force = gravity;` and **425** `USERDATA1.xyz += force * DELTA;`. The particle moves on **456**. |
| colour over life sampled | **255**: `parameters.color *= texture(color_ramp, vec2(lifetime));` |
| scale over life applied | **254**: `parameters.scale *= texture(scale_curve, vec2(lifetime)).rgb;`. The random start scale is on **243**, and it is put into the transform on **475–477** (first frame) and **480–482**. |
| a line tied to a brief setting | **232**, ↔ `initial_velocity_min / max` = **50 / 80 px/s** (brief R5). Also **446–447**: turbulence influence 0.1–0.2 turns the velocity toward the noise direction every step. |

**Which of my settings live in this shader, and which belong to the draw step** (my answer):

> The shader does the per-particle work. That covers where a particle starts (`emission_shape`, sphere radius 6), which way and how fast it goes (`direction`, `spread`, initial velocity), what pushes it (`gravity`, `damping`, turbulence), and how it changes over its life (`angle`, the scale min/max and scale curve, the `color_ramp`). All of these are uniforms in this file. The draw step is not in this file. The texture `soft_dot_32.png`, the CanvasItemMaterial with blend MIX, `visibility_rect` and the draw order sit on the GPUParticles2D node and its canvas material. How many particles are emitted and when (`amount`, `amount_ratio`, `lifetime`, `one_shot`, `explosiveness`, `preprocess`, `emitting`) is also set on the node. The shader only sees the result, for example as `LIFETIME`, and as which particles are active.

LANGUAGE-NOTES.md has the longer reading. It includes **line 447**: every process step, turbulence blends the velocity 10–20 % toward a noise direction. That is why Effect B's smoke would not rise, and it is the reason Claude gave in session 7c.

## Predicted failures: what happened

| # | Prediction | Outcome |
|---|---|---|
| 1 | Godot 3 names | The agent used none. Mutation 1 shows the config test catches one. |
| 2 | Default gravity (0, 980) | The agent set (0, 0) on all emitters; the config test reads it back. My brief's claim about the *old* debris was wrong: it had (0, 160) (R1). |
| 3 | Freed parent | Did not happen. Bursts go to `World/FX`; rule 4 passes. |
| 4 | Dropped retrigger | Did not happen. Overlap, rule 3 passes. |
| 5 | Popping feedback loop | Did not happen. `amount` stays 48; there is no gap in the strip after frame 60. |
| 6 | `visibility_rect` too small | Did not happen (edge check). |
| 7 | Null texture or wrong blend | Did not happen. The config tests check them, and the strips show soft and chip textures. |
| 8 | No value contrast | **Happened**, for A's last chip colour (fixed by R3) and B's dark base colour (not fixed). |

## Still uncertain

- Turbulence as the cause of B's lump is confirmed **by reading the code**, not by a strip with turbulence off.
- The leak counts at exit vary, cause unknown.
- My pause verdict is one word for both effects.
- `tests/test_hit_flash.gd` (A5) freezes enemies with `disable_mode` REMOVE, so they have no bodies. It never needs them, and it is unchanged.
