# CHANGE-BRIEF — Assignment 6: particle effects

**Project.** walker-TANK · Godot 4.7.2 stable (`ed1daf0bf`) · Forward+ (engine default; `project.godot` has no renderer key) · Windows 11, Git Bash.

**Layout.** `project.godot` is at the repository root, so effects go in `effects/`, previews in `previews/` and tests in `tests/`.

**Window.** 1280 × 720 viewport, stretch `canvas_items` (`project.godot` lines 23–25). The camera is fixed at (640, 360) (`main.gd` line 62).

**Display and GPU.** The laptop has an NVIDIA GeForce RTX 3060 Laptop GPU and an Intel Iris Xe. The internal display runs at 144 Hz through the Iris Xe. GPU prices are read with Godot running on the RTX 3060.

**Baseline before this change** (commit a9513d3, all exit 0):

| Test | fps | PASS |
|---|---|---|
| `test_hit_flash.gd` | 30 / 60 / 144 | 50 / 50 / 50 |
| `test_materials.gd` | 60 | 76 |
| `check_tools_parse.gd` | 60 | 9 |
| `check_a3_assets.gd` | 60 | 18 |
| `test_sound_triggers.gd` | 60 | 8 |

The Assignment 5 brief is in history at tag a5. Revisions to this brief go, dated, under *Revisions* at the bottom.

| | Effect A — cover hit burst | Effect B — damage smoke |
|---|---|---|
| Job | a one-shot burst on a repeating event | a feedback loop that follows a game value |
| Scene | `effects/cover_hit_burst.tscn` | `effects/damage_smoke.tscn` |
| Node | 3 × `CPUParticles2D` under one `Node2D` root | 1 × `GPUParticles2D` + `ParticleProcessMaterial` |
| Replaces | the code-made `"debris"` call in `cover.gd` line 40 | the code-made `smoke` trail in `tank.gd` line 61 |

---

## Effect A — cover hit burst

### The job

It tells the player: **"your shell landed on that wall, right there, and the wall took damage."** Cover breaks in stages (intact → cracked after 2 hits → broken after 4; `cover.gd` lines 2–6), so the player is counting hits. Each hit has to register at the point the shell struck, readable with sound muted (A2's muted-readability rule).

The current cover debris (`cover.gd` line 40 → `main.gd` `spawn_fx("debris")`) fails at both:

- It is spawned at the **cover's centre** (`global_position + (0, -8)`), not where the shell struck.
- `spawn_fx` never sets `gravity` (`main.gd` lines 161–168), so as far as lines 161–190 show, CPUParticles2D's default (0, 980) applies. In a top-down game the chips fall down the screen.

**Event.** `cover.gd` `take_hit(_shell)` (line 33) gets past `if stage >= 2: return` (line 34) and plays `cover_hit` (line 39). That is the same point the existing sound test counts.

**Position and direction.**
- Position: the shell's drawn position at contact, `_shell.global_position + _shell.DRAW_OFFSET`. That is the same point `shell.gd` line 50 uses for `"impact"`.
- Direction: back out of the wall, `-_shell.dir` (`shell.gd` line 9).

**Who triggers it.**
- `cover.gd` line 40 changes from `world.spawn_fx("debris", …)` to `world.spawn_cover_burst(_shell)`. That is the only line of `cover.gd` that changes.
- `main.gd` gains `spawn_cover_burst(shell)`, which instances the scene into `fx_layer` (`World/FX`, `main.gd` lines 57–60). It sets the position and the rotation `(-shell.dir).angle()`.
- Both only read game state.

**What stays as it is.**
- The shell's own small `"impact"` spark (`shell.gd` line 50) is a separate existing effect on every shell hit, tanks included. It stays unchanged.
- The `"debris"` branch of `spawn_fx` stays in the file.

### The intent block

**Timing phases** (whole burst ≈ 0.7 s):

| Time | Frames at 30 fps | Phase | What happens |
|---|---|---|---|
| 0–0.07 s | 0–2 | impact | A pale flash, brightest on frame one; chips already leaving the point. |
| 0.07–0.3 s | 2–9 | outward | Brick chips fly back out of the wall in a fan, fast at first, braking hard; a dust puff swells. |
| 0.3–0.7 s | 9–21 | dissipation | Chips stop, shrink and darken to the wall's own brown, then fade; the dust thins. |

It is gone by 0.7 s, so on one wall each hit reads as its own event. YunqiZ's reload is about 0.8 s and the enemies' is 1.8 s (`main.gd` line 87).

**Contrast against the real background.** The level is one ground tile repeated (`assets/game/env/ground_tile.png`, laid by `_build_ground()` in `main.gd`) plus brick cover (`cover_intact.png`, `cover_cracked.png`, `cover_broken.png`).
- **Darkest stretch:** the red-brown brick face of intact or cracked cover. That is where every burst starts.
- **Lightest stretch:** the open ground tile the chips fly out over.
- Brick-red chips on red brick have almost no value contrast. So in the first 0.3 s the read comes from the **flash** (near-white, additive) and the **dust** (light sand), and the chips only need to read once they are over the ground.
- Checked by eye in the running game on both, never over the editor grey.

**Scale against the character.** YunqiZ's hull is about 33 display px wide (`RADIUS := 16.6`, half the hull width, `tank.gd`), and a cover block is 72.6 × 22 px (`cover.gd` line 27).

| Layer | Size |
|---|---|
| Flash | about 1 hull width across |
| Chips | reach about 2 hull widths (≈ 60 px) from the impact point |
| Dust | ends about 1.5 hull widths across |

The whole burst stays smaller than one cover block plus a hull on each side. It is judged at 1280 × 720.

**Change over life.**
- Chips: pale dust-yellow → brick red → dark brown, shrinking to 40 %.
- Flash: grows to 160 % while it fades.
- Dust: grows from 60 % to 180 % while it fades.
- No layer fades in alpha alone.

**Variation.** This matters most here, because a wall takes four hits.
- Chips vary in speed (180–320 px/s), size (0.6–1.2), spin (±720 °/s) and hue (±0.03), within a 60° fan.
- Repeats on the same wall must not look stamped.

**Layering.** Three emitters under one root `Node2D`:

| Emitter | Job |
|---|---|
| `Flash` | the instant of impact |
| `Debris` | direction and force, aimed back along the shell's path |
| `Dust` | the wall giving way, and the part that lingers |

### The settings

**Node type: CPUParticles2D.**
- No GPU-only feature is needed: no turbulence, collision, attractor, sub-emitter or trail.
- A burst is ≤ 37 particles.
- A CPU node gives Effect A a headless CPU price that is not near zero, so it is compared on **both** prices.

The root is rotated so that the emitters' `direction = (1, 0)` points back out of the wall.

| Setting | Flash | Debris | Dust |
|---|---|---|---|
| amount | 3 | 24 | 10 |
| one_shot | true | true | true |
| explosiveness | 1.0 | 1.0 | 0.9 |
| lifetime | 0.12 s | 0.6 s | 0.7 s |
| emission_shape | point | sphere, radius 4 px | sphere, radius 8 px |
| direction / spread | (1, 0) / 180° | (1, 0) / 60° | (1, 0) / 180° |
| initial_velocity_min / max | 0 / 0 | 180 / 320 px/s | 30 / 70 px/s |
| gravity | (0, 0) | (0, 0) | (0, 0) |
| damping_min / max | 0 / 0 | 400 / 600 | 60 / 90 |
| angular_velocity_min / max | 0 / 0 | −720 / 720 | −60 / 60 |
| scale_amount_min / max | 1.6 / 2.0 | 0.6 / 1.2 | 1.0 / 1.4 |
| scale_amount_curve | 1.0 → 1.6 | 1.0 → 0.4 | 0.6 → 1.8 |
| color_ramp | #FFF4D0 a1 → #FFF4D0 a0 | #E8D8B0 a1 @0 → #B5523A a1 @0.3 → #5A3A2E a0 @1 | #CFC2A8 a0.6 → #CFC2A8 a0 |
| hue_variation_min / max | 0 / 0 | −0.03 / 0.03 | 0 / 0 |
| texture | `soft_dot_32.png` | `chip_6.png` | `soft_dot_32.png` |
| material | CanvasItemMaterial, blend **ADD** | none (mix) | none (mix) |
| local_coords | false | false | false |

- **Gravity (0, 0) is deliberate.** Top-down: chips brake, they don't fall. The slow-down is damping. The config test must read gravity back, because the default is (0, 980).
- **local_coords false.** Particles stay where they were emitted. `World/FX` never moves, and `shake()` moves the camera, not the layer.
- **Textures** are written by code in `tools/make_particle_textures.gd` (run by me, code and PNGs committed): `chip_6.png` is a 6 px irregular chip, `soft_dot_32.png` a 32 px radial falloff. There are no sourced or generated textures.
- **No visibility_rect** (CPU node). **No preprocess** (a one-shot on an event).
- **The root frees itself** when `Dust` emits `finished`.

### Observable rules

1. **Fires exactly when it should.** Effect A fires once for every `take_hit` that passes line 34, and never otherwise:
   - not on scene load;
   - not when a shell hits a tank;
   - not when a shell expires without hitting anything (`shell.gd` line 31).

   Four hits on one block give four bursts.
2. **At the event's place.** It appears at the shell's drawn contact point, within 2 px, rotated to `(-shell.dir).angle()`.
3. **Retrigger rule: overlap.** Each hit instances a new burst. Bursts never share a node, so a second hit inside 0.7 s neither restarts nor drops the first.
   - Most bursts alive at once: **4**. YunqiZ plus three enemies can each land at most one shell inside 0.7 s, given their reloads.
4. **Freed parent.** The shell frees itself right after `take_hit` (`shell.gd` line 51), and the burst must survive that. So the burst is added to `World/FX`, never to the shell or the cover. The cover itself is not freed when it breaks; its shape is disabled (`cover.gd` lines 44–45). Even so, the burst is not parented to it.
5. **Paused tree.** `World` is `PROCESS_MODE_PAUSABLE` (`main.gd` line 50), so a burst alive at pause freezes and resumes where it was.

### The evidence split

| Rule | Checked by | How |
|---|---|---|
| Every setting above | headless config test | `test_cover_hit_burst_config.gd` reads each value back from the loaded scene, by emitter path |
| 1 fires on every hit, never otherwise | headless state test | the real game loop and real fire input; counts burst instances over load, cover hits, a tank hit and an expired shell |
| 2 position and rotation | headless state test | burst `global_position` and `rotation` against the shell at contact |
| 3 overlap | headless state test | two hits inside one lifetime (one from YunqiZ by real input, one from a second shell through `main.gd` `spawn_shell()`) → 2 bursts alive, the first not restarted |
| 4 freed parent | headless state test | the burst is still in the tree and emitting after the shell is freed |
| 5 paused | headless state test + eyes | `can_process()` false under pause; the frozen look by eye |
| Timing phases, layering, change over life | frame strip (fixture) | frames 10, 12, 15, 20, 30, 50 |
| Contrast and scale | eyes in the running game | on the brick face and the open ground, at 1280 × 720 |
| Repeats don't look stamped | eyes in the running game | four hits on one wall, and rapid hits from several tanks |

### The frame strip

- **Preview:** `previews/cover_hit_burst_preview.tscn`. A cover block on the real ground tile, camera at in-game scale (zoom 1, 1280 × 720). The burst is placed on the block's face, aimed as a shell from the left would be.
- **Trigger:** frame 10. When the preview's `retrigger` export is on, it triggers again at frame 16, 0.2 s later, inside one lifetime.
- **Fixture:** the preview's instance uses a fixed seed if 4.7's CPUParticles2D has `use_fixed_seed`; the effect scene never does.
- **Capture:** 30 fps, `--quit-after 60`. Read frames **10, 12, 15, 20, 30, 50**:

| Frame | Time after trigger | What it should show |
|---|---|---|
| 10 | 0 s | the flash at full brightness; chips just leaving the point |
| 12 | 0.07 s | the flash fading; chips in a 60° fan back out of the wall, pale |
| 15 | 0.17 s | chips about 1.5 hull widths out, turning brick red; dust swelling |
| 20 | 0.33 s | chips almost stopped, about 2 hull widths out, red-brown and smaller |
| 30 | 0.67 s | the last dust, nearly transparent; chips gone |
| 50 | 1.33 s | nothing left |

The shell's own `"impact"` spark is not in the preview, because the preview triggers Effect A alone. It is seen together with Effect A in the running game.

---

## Effect B — damage smoke

### The job

It tells the player: **"this tank is badly hurt — and how badly."** It works for YunqiZ and for each enemy at a glance, without the health bar. After death the same smoke marks a wreck.

The current smoke (`tank.gd` line 61, `_make_trail(...)`) is a CPUParticles2D with **no texture** (`_make_trail`, lines 68–90). It draws as grey squares scaled 3–6 px, at one fixed density whatever the damage.

- **Job:** a feedback loop that follows a game value.
- **Game value:** `health / max_health` (`tank.gd` lines 19, 26).
  - YunqiZ: `max_health` 100.
  - Enemies: `max_health` 75 (`main.gd` line 85).
- **Where state changes:**
  - `take_damage()` lines 163–175 calls `_update_damage_look()`;
  - `die()` lines 179–192 sets `smoke.emitting = true` on line 187;
  - `reset_full()` lines 206–214 sets it false on line 213.
- **Feature Effect A doesn't use:** **turbulence** (process, GPU-only). B also uses a value-driven `amount_ratio`, a real texture on a GPU node, and world-space trailing behind a moving node.

**What changes in `tank.gd`** (presentation lines only):
- line 35: `var smoke: GPUParticles2D`;
- line 61: `smoke` becomes an instance of `effects/damage_smoke.tscn` at `TURRET_OFFSET`;
- `_update_damage_look()` (line 195): also sets `smoke.amount_ratio` from the mapping below;
- `die()`: also sets `smoke.amount_ratio = 1.0` beside line 187.

No health, damage, invulnerability, timing or `modulate` line changes. `flames` stays as it is.

### The intent block

**Timing phases:**

| Phase | Time | What happens |
|---|---|---|
| Start | 0–0.3 s after the threshold hit | first wisps rise from the engine deck |
| Build | 0.3–1.6 s | the column fills to its full length over one lifetime |
| Steady | | a continuous, wavering column, denser after each further hit |
| Stop | ≤ 1.6 s (respawn only) | emission ends; the column already in the air drifts off and fades, never cut off |

**Contrast.** Grey smoke over the ground tile is a value problem: mid-grey on mid-grey.
- So the smoke is born **darker than the ground** (#4A4A48) and turns **lighter as it thins** (#8A8A86). It reads against the open ground tile (the lightest stretch) by being dark at its base, and against brick cover (the darkest) by being light at its top.
- Checked by eye, driving a smoking tank over both.

**Scale.**
- A puff is born about ½ hull width across and grows to about 1.5 hull widths.
- A standing tank's column is about 2–3 hull lengths tall.
- A moving tank leaves a trail behind it.

**Change over life.**
- Alpha rises 0 → 0.7 in the first 15 % of life, then falls to 0.
- Size grows 0.5 → 2.0.
- Colour goes dark → light grey.

**Variation.** Turbulence makes each puff waver. Speed varies 20–40 px/s, scale 0.8–1.2, and the angle is random.

**Layering.** One emitter, the smoke column. The ≤ 30 % flames are the existing separate emitter (`tank.gd` line 62).

### The settings

**Node type: GPUParticles2D.** It needs turbulence, which is GPU-only, and `amount_ratio`, which on GPU nodes in 4.2+ changes how many allocated particles emit without restarting the system. Being a GPU node, it is compared on **GPU time**: its headless CPU price is near zero by construction.

| Group | Setting | Value |
|---|---|---|
| emission | amount | 48 |
| | amount_ratio | set by `tank.gd`, 0.25 … 1.0 (mapping below); 1.0 in the scene file |
| | one_shot | false |
| | emitting | false in the scene file |
| | explosiveness | 0.0 |
| | lifetime | 1.6 s |
| | preprocess | 0 s (see below) |
| | emission_shape | sphere, radius 6 px |
| process | direction / spread | (0, −1) / 20° |
| | initial_velocity_min / max | 20 / 40 px/s |
| | gravity | (0, −15) — buoyancy up the screen |
| | damping_min / max | 5 / 8 |
| | angle_min / max | 0 / 360 |
| | scale_min / max | 0.8 / 1.2 |
| | scale_curve | 0.5 → 2.0 |
| | color_ramp | #4A4A48 a0 @0 → #4A4A48 a0.7 @0.15 → #8A8A86 a0 @1 |
| | turbulence_enabled | true |
| | turbulence_noise_strength | 2.0 |
| | turbulence_noise_scale | 4.0 |
| | turbulence_influence_min / max | 0.1 / 0.2 |
| draw | texture | `soft_dot_32.png` |
| | material | CanvasItemMaterial, blend MIX |
| | local_coords | **false** — smoke stays where it was emitted, so a moving tank leaves a trail |
| | visibility_rect | **set and checked:** Rect2(−200, −220, 400, 420) |

**Why preprocess is 0.** The condition always starts mid-game, on a hit. A preprocessed column would appear fully grown on the frame of the hit. On scene load every tank is at full health, so there is nothing to preprocess.

**Why visibility_rect is set by hand.** With `local_coords` false, the column trails behind a moving tank. YunqiZ moves at 110 px/s (`tank.gd` line 20) and enemies at 70 (`main.gd` line 86). Over one 1.6 s lifetime the oldest smoke can be ≈ 176 px behind the node and ≈ 80 px above it. The rect covers ± 200 px around the node, and I check it by eye at the screen edge.

### Observable rules

1. **Mapping**, with h = health / max_health:
   - h > 0.6 and alive: `emitting = false`.
   - 0 < h ≤ 0.6: `emitting = true`, and `amount_ratio = 0.25 + 0.75 × (0.6 − h) / 0.6`. That is 0.25 at 60 %, 0.625 at 30 % and 1.0 at 0 %.
   - Dead (a wreck): `emitting = true` and `amount_ratio = 1.0`.

   With 25-damage shells (`shell.gd` line 11):

   | Tank | Health after hits | Smoke |
   |---|---|---|
   | YunqiZ | 75 | none |
   | | 50 | ratio 0.375 |
   | | 25 | ratio 0.6875 |
   | | dead | 1.0 |
   | Enemy | 50 | none |
   | | 25 | ratio ≈ 0.583 |
   | | dead | 1.0 |

2. **Only `amount_ratio` changes, never `amount`.** `amount` stays 48: changing it would reallocate the buffer and restart the system, so the column would pop on every hit.
3. **Start.** Emission starts on the hit that takes h to ≤ 0.6, the first frame after `take_damage()` returns.
4. **Stop.** Emission stops on `reset_full()` (YunqiZ's respawn, `main.gd` line 265). The column already in the air is left to fade. A destroyed enemy is not freed and keeps smoking as a wreck at 1.0, the same as today (line 187).
5. **Paused tree.** Tanks are under `World` (PAUSABLE), so the smoke freezes in place, stays visible, emits nothing new during the pause, and resumes on unpause.
6. **Hidden node.** Nothing is drawn. `emitting` and `amount_ratio` still follow health, so the smoke is right the moment it is shown again. Tanks are never hidden in normal play; this rule is checked by setting `visible = false` in the test.
7. **Scene load.** No tank is smoking on the first frames, because all are at full health.

### The evidence split

| Rule | Checked by | How |
|---|---|---|
| Every setting, including turbulence | headless config test | `test_damage_smoke_config.gd` |
| 1, 2 mapping; `amount` never changes | headless state test | real shells through the real loop bring YunqiZ to 50 and 25 HP; assert `amount_ratio` 0.375 and 0.6875 (±0.001) and `amount` still 48 |
| 3, 4 start, stop, wreck | headless state test | `emitting` before and after the threshold hit; after `reset_full()`; on a destroyed enemy |
| 5 paused | headless state test + eyes | `can_process()` false and `emitting` unchanged under `get_tree().paused`; the frozen look by eye |
| 6 hidden | headless state test + eyes | `visible = false` doesn't change `emitting` or `amount_ratio`; nothing drawn, by eye |
| 7 scene load | headless state test + eyes | no smoke node emitting after load; the first frames by eye |
| Column look, waver, density step, stop | frame strip (fixture) | frames below |
| Contrast, scale, trail while moving, edge of screen | eyes in the running game | drive a smoking YunqiZ over ground and cover, and to the screen edge |

### The frame strip

- **Preview:** `previews/damage_smoke_preview.tscn`. A standing tank on the real ground tile beside a cover block, camera at in-game scale.
- **Driving the value:** the preview drives h through the same mapping code the tank uses:

| Frame | h | amount_ratio | Event |
|---|---|---|---|
| 10 | 0.5 | 0.375 | condition starts |
| 60 | 0.1 | ≈ 0.94 | heavier damage |
| 110 | 1.0 | — | condition ends, as on respawn |

- **Capture:** 30 fps, `--quit-after 170`. The preview's instance uses `use_fixed_seed` if 4.7's GPUParticles2D has it. Read frames **10, 25, 58, 90, 112, 140, 165**:

| Frame | What it should show |
|---|---|
| 10 | the condition starts: nothing yet, or one faint wisp |
| 25 | a short, thin column (half a lifetime) |
| 58 | a full, thin column at steady state (0.375) |
| 90 | a full, dense column at steady state (0.94); no gap or pop after frame 60 |
| 112 | just after the stop: the column still all there, nothing new at the base |
| 140 | the column detached from the tank, thinner, higher |
| 165 | empty |

---

## Boundaries

**Allowed code changes, and nothing else:**

| File | Change |
|---|---|
| `cover.gd` | line 40 |
| `main.gd` | one new function, `spawn_cover_burst()` |
| `tank.gd` | the smoke lines 35, 61, `_update_damage_look()`, and one added line in `die()` |

**New files:** `effects/`, `previews/`, `tools/make_particle_textures.gd` and its PNGs, the new tests, the cost script, and `shaders/particles_generated.gdshader` (saved by me in Step 6).

**Unchanged:**
- collision, movement, input, the enemy AI;
- reload, damage, invulnerability and every timing;
- cover stages;
- the shells (`shell.gd` untouched, including its `"impact"` spark);
- the A5 hit flash and its driver;
- flames, HUD, audio, pause handling;
- the existing tests and their expectations;
- the Assignment 5 shaders in `shaders/`;
- every source texture;
- `project.godot`.

Presentation code reads game state; it never writes it.

---

## Predicted failures

| # | Failure | Check that catches it |
|---|---|---|
| 1 | **Godot 3 names.** `initial_velocity`, `scale_amount_random`, `ParticlesMaterial` load silently and leave defaults. | config tests read every value back; Effect A mutation 1 |
| 2 | **Default gravity (0, 980) on CPUParticles2D.** The agent omits `gravity`, as `spawn_fx` does today, and chips fall down the screen. | config test reads gravity == (0, 0) per emitter; frames 15–20 show a fan, not a downward streak |
| 3 | **Freed parent.** The burst is parented to the shell (freed on line 51 right after `take_hit`), so it never appears. | state test rule 4; frame 12 |
| 4 | **Dropped retrigger.** A single reused one-shot node per cover silently drops the second hit. | state test rule 3: two hits inside 0.7 s → 2 bursts |
| 5 | **Popping feedback loop.** `tank.gd` sets `amount` instead of `amount_ratio`, and the column vanishes and re-emits on every hit. | state test asserts `amount` stays 48; strip frames 58 → 90 show no gap |
| 6 | **Visibility rect too small** for world-space smoke behind a moving tank, so the column pops out at the screen edge. | human edge-of-screen check while driving |
| 7 | **The look the old smoke has today.** Null texture, or ADD set without a CanvasItemMaterial: grey squares, no glow. | config tests: texture not null, material class and blend mode; strip frames 10 (A) and 58 (B) |
| 8 | **No value contrast.** Red chips on red brick; grey smoke on grey ground. | strips plus the human check over the brick face and the open ground |

## Price predictions and budget

**Instruments:**
- **Headless CPU:** the cost script, mean ± spread of frame time at 60 fps. It runs an empty-scene control, the game scene with both effects off, Effect A at 4 bursts and Effect B on 4 tanks.
- **On screen:** the Visual Profiler's GPU time, effect off and then on at its heaviest. Godot has to be on the **NVIDIA GeForce RTX 3060 Laptop GPU**: set it to High performance in Windows Graphics settings, and confirm it in the GPU line Godot prints at startup.

| | Peak particles | Predicted headless CPU (over the game, effects off) | Predicted GPU time (over effect off) | Budget | Compared on |
|---|---|---|---|---|---|
| A | 4 bursts × 37 = **148** | +0.05 – 0.15 ms | +0.01 – 0.03 ms | CPU ≤ 0.5 ms **and** GPU ≤ 0.2 ms | both (CPU node) |
| B | 4 tanks × 48 = **192** | ≈ 0 (≤ 0.02 ms, the CPU's share only) | +0.03 – 0.08 ms | GPU ≤ 0.3 ms | GPU time (GPU node) |

## Answers

**Which node type does each effect use, and which features does it lack?**
- A is CPUParticles2D. Compared with GPUParticles2D it lacks turbulence, attractors, collision, sub-emitters and trails. A uses none of them.
- Whether 4.7's CPUParticles2D has `amount_ratio` and `use_fixed_seed` I check in the 4.7 class reference while reviewing CLAUDE.md. It doesn't affect B, which is a GPU node.
- B is GPUParticles2D with a ParticleProcessMaterial. That has the two things B needs: turbulence and `amount_ratio`.

**With local_coords false, what does A do if its parent moves after the event?**
Nothing. The particles stay at the impact point in world space. Its parent, `World/FX`, never moves anyway; camera shake moves the camera.

**How many A bursts can be alive at once, and what peak count does that give?**
Up to **4** under overlap, one per tank inside 0.7 s, so the peak is 148 particles. Normal play is 1–2.

**What will a headless run report as the cost of a GPU effect, and why? What does FPS read with vsync on?**
- Headless: almost nothing. The dummy renderer runs no GPU particle process and draws nothing; all that remains is the node's CPU bookkeeping.
- With vsync on, FPS reads **144** (the display's refresh rate) both with B off and with B on, because B costs far less than one 6.9 ms frame. FPS hides the cost; only GPU time shows it.

**What does B show on the first frame after its scene loads? Paused? Hidden?**
- **In the game:** nothing, with or without preprocess, because no tank is damaged at load.
- **In a scene where the condition is already true at load** (the preview, if it started at frame 0): without preprocess it starts empty and fills over 1.6 s; with preprocess 1.6 s the column is already full.
- **Paused:** frozen and visible.
- **Hidden:** not drawn, but still following health.

**Which settings belong to emission, which to process, and which to draw?**
- **Emission:** amount, amount_ratio, one_shot, emitting, explosiveness, lifetime, preprocess, emission_shape.
- **Process:** direction, spread, initial velocity, gravity, damping, angle and angular velocity, scale and the scale curve, color_ramp, hue variation, turbulence.
- **Draw:** texture, the CanvasItemMaterial and its blend mode, visibility_rect, and the FX layer's z_index.
- `local_coords` chooses the space the process step runs in, which in turn decides where the particles are drawn.

---

## Revisions

(dated revisions are added below during this assignment)
