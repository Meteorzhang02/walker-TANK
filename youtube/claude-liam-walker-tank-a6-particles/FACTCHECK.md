# FACTCHECK — claude-liam-walker-tank-a6-particles

Every spoken or on-screen claim, against the sources of truth at walker-TANK `41a6b8b` (read from `_scratch/src`).

| Beat | Claim | Source |
|---|---|---|
| B00 | Two particle effects; A = 3 × CPUParticles2D, B = GPUParticles2D | TEST-REPORT.md "The two effects" table |
| B00 | Prompt is a reconstruction | (film decision; labelled on screen) |
| B02 | A's job "your shell landed on that wall, right there"; fires from take_hit, line 40 | CHANGE-BRIEF Effect A "The job"; TEST-REPORT table; `scripts/cover.gd` line 40 `world.spawn_cover_burst(_shell, …)` inside `take_hit()` (line 33) |
| B02 | B's job "this tank is badly hurt, and how badly"; on at h ≤ 0.6; amount_ratio follows health; wreck 1.0 | CHANGE-BRIEF Effect B rule 1; `effects/damage_smoke.gd` `follow()` |
| B03 | amount 48, lifetime 1.6 (emission); velocity, gravity (process) → shader 232, 412/425; soft_dot_32.png, blend MIX, visibility_rect (draw) | `damage_smoke.tscn` lines 50, 54, 30, 32, 4, 7 (`blend_mode = 0`), 58; TEST-REPORT "The process shader" table |
| B04 | Headless: dummy renderer runs no GPU particle process; B −0.009 ms; render_gpu 0.000 | TEST-REPORT "What headless cannot prove", "Headless CPU price"; `logs/price_measure_realtime.log` diff mode2 −0.0090, render_gpu 0.0000 |
| B05 | Intent: gone by ≈ 0.7 s | CHANGE-BRIEF Effect A timing phases |
| B05 | First look quote; "nothing to change" in the game | TUNING.md Effect A r0 (quotes verbatim) |
| B06 | A's revision strip-driven | TUNING.md "Driven by: Claude's reading of the r0 strip"; TEST-REPORT "Claude against me" |
| B06 | Chips vanish by frame 20; last stop #5A3A2E ≈ ground's value; R3 adds #8E5040 a1 @0.6; prediction ≈ 20 opaque red-brown chips 50–60 px | TUNING.md r1; CHANGE-BRIEF R3; `cover_hit_burst.tscn` lines 25–26 |
| B07 | Claude: partly held, faint, ~80 px; next lever chip size; kept r1, lever declined; quote | TUNING.md Effect A r1 (session 4c, verdict) |
| B08 | Three hits on one wall, each its own burst | `a6-play.mp4` ≈ 13.3, 14.2, 15.1 s (checked frame by frame in `_qc/wall.png`) |
| B08 | Retrigger: second burst at frame 16, 0.2 s later | `previews/cover_hit_burst_preview.gd`; `capture/godot/burst_retrigger.log` (bursts at frames 10 and 16) |
| B08 | "the second burst doesn't restart the first" | TEST-REPORT rule 3 (two hits 0.317 s apart, first freed 0.750 s after its own start) |
| B08 | Rapid hits from several tanks not checked separately | TEST-REPORT "In play" |
| B09 | Intent: rising, wavering column 2–3 hull lengths; turbulence is the feature A doesn't use (GPU-only) | CHANGE-BRIEF Effect B intent, "Feature Effect A doesn't use" |
| B09 | In the game: 一团 (a lump) | TUNING.md Effect B game check 2 |
| B10 | Claude's reading: brief values carry a mean puff only ~59 px; R5 20/40 → 50/80; prediction thin column y ≈ 270–290 at 58, detached at 140 | TUNING.md Effect B r1; CHANGE-BRIEF R5; `damage_smoke.tscn` lines 30–31 |
| B11 | Claude (7c): prediction failed, still a lump 5–10 px higher | TUNING.md Claude's comparison |
| B11 | Student: 是柱子，保留，往上升 — kept; strip reading overruled | TUNING.md verdict; TEST-REPORT "Claude against me" (B r1) |
| B12 | State test 81/81 at 30/60/144; load, threshold, respawn (first frame after), wreck 1.0, pause | TEST-REPORT State table and Effect B rules |
| B12 | Game checks 有 / 拖烟条 / 对 / 会; stop on respawn headless only | TUNING.md game-check table; TEST-REPORT "In play" |
| B13 | Line 232 picks start speed between min and max (50/80); line 447 turbulence blends velocity 10–20 % toward noise every step | `particles_generated.gdshader` lines 232, 443–447; LANGUAGE-NOTES A6 |
| B14 | ≈ 0.85ⁿ: ≈ 0.38 after 0.2 s, < 0.01 after 1 s; confirmed from code, not by a turbulence-off strip | LANGUAGE-NOTES A6 turbulence; TEST-REPORT "Still uncertain" |
| B15 | Config 128/128 and 76/76; mutation 1 Godot 3 name → exit 1, Godot silent; mutation 2 damping 400 → 300 → exit 1; state 82 and 81 at 30/60/144; two hits 0.317 s apart; headless can't show anything drawn | TEST-REPORT Configuration, mutations, State, "What headless cannot prove" |
| B16 | CPU A +0.074 (≤ 0.5), B −0.009 ≈ 0, drift 0.020; GPU A +0.023 (≤ 0.2), B +0.077 (≤ 0.3), drift 0.005 | `logs/price_measure_realtime.log`, `logs/price_measure_windowed.log`; CHANGE-BRIEF budget |
| B17 | First cost script 6.90 ms everywhere incl. empty scene = 1/144 s; control caught it; FPS 143–144 every mode; 143 with vsync off; capped | TEST-REPORT Headless CPU price, GPU price; FRICTIONAL Step 7 |
| B18 | Student caught: cost script measuring itself; "R5 uncommitted" (it was 96d38be); exit codes the agent could only infer; test setups that froze enemies (no bodies, stopped timers), fixed in tests only | TEST-REPORT; TUNING.md; FRICTIONAL (sessions 3, 6c, 7c, 8) |
| B18 | Agent caught: old debris gravity (0, 160); null-shell test break; 0.94 vs 0.875 | CHANGE-BRIEF R1.1, R1.2, R4.1; FRICTIONAL Step 1 |
| B18 | Uncertain: turbulence from code only; leak counts vary | TEST-REPORT "Still uncertain"; FRICTIONAL Unresolved |
| B18 | Next step: lower B's turbulence influence, or lighten base colour | LANGUAGE-NOTES ("the next lever … is the turbulence influence"); TEST-REPORT background (#4A4A48 not fixed) |
| B18 | Contributions; textures drawn by code | SOURCES.md A6 (walker-TANK) |
| B18 | Repo 41a6b8b, game source 96d38be | `git log`; TEST-REPORT "Game source revision" |

**Wording choices.** "Exit codes the agent could only infer" (the user's phrase; TEST-REPORT: "The agent could not print exit codes … every exit code is from my own runs"). "It measured itself" (the user's phrase for "measuring the frame pacing").
