# FACTCHECK — claude-liam-walker-tank-a7-animation

Every claim spoken or shown, with its source at walker-TANK **4f88f1b** (read from the git-archive copy `_scratch/src`).
"Prompt" = the student's film prompt plus the in-run revision message (the switch from 392d1c4 to 4f88f1b); those items
are the student's account and are marked where the repo has no separate record.

| Beat | Claim | Source | Status |
|---|---|---|---|
| B00 | walker-TANK, 2D top-down tank game, Godot 4.7.2, Forward+ | `project.godot`; capture logs "Vulkan … Forward+" | ✔ |
| B00/B15 | Revision shown 4f88f1b | `git log`: 4f88f1b "A7 edge tests…" | ✔ (replaces 392d1c4, which lacked the committed dust fix) |
| B02 | A clip is an Animation resource of keyed tracks | `animations/motion_clips.tres` line 3 `[sub_resource type="Animation"]` | ✔ |
| B02 | track_dust: frame track on Dust, keys 0/0.1/0.2/0.3, length 0.4, LOOP_LINEAR, discrete, step 0.1 | motion_clips.tres lines 4–17 (`loop_mode = 1`, `"update": 1`, `step = 0.1`, path `DustMount/Dust:frame`) | ✔ |
| B02 | On MotionAnim | `tank.gd` lines 93–97 | ✔ |
| B03 | Sheet 64×16, hframes 4, vframes 1 | PIL size of `assets/game/fx/track_dust_sheet.png` = (64, 16); tank.gd 78–79 | ✔ |
| B03 | Ten cells a second | 10 fps = key interval 0.1 s (brief "Cycle spec") | ✔ |
| B03 | Dust just behind the hull | capture `drive` frames 22–64 (looked at); tank.gd line 24 `DUST_BEHIND := 34.0` | ✔ |
| B04 | shoot = cutout rig baked from code, bake_tank_clips.gd → fire_clips.tres | `tools/bake_tank_clips.gd` header lines 1–6, `_make_shoot()` 59–80 | ✔ |
| B04 | Suspension parent of hull and turret | tank.gd 83–92 | ✔ |
| B04 | Dips 2 px, squashes (1.04, 0.96) on frame 1 | bake lines 22, 24, 72, 78; fire_clips.tres keys | ✔ |
| B04 | 30 fps, step 1/30, LOOP_NONE | bake lines 15, 65–66; fire_clips.tres has no step/loop line = Godot defaults; read-back "shoot step = 1/30", "does not loop" PASS | ✔ |
| B05 | Startup 1 / active 1 / recovery 3 frames; key times 0 / 0.0333 / 0.0667 / end 0.1667 | CHANGE-BRIEF.md lines 75–80 | ✔ |
| B05 | Startup is one frame because firing should feel crisp | CHANGE-BRIEF.md line 84 | ✔ |
| B05 | Strip v1 (FIXTURE): dip + squash peak N+1 with shell and flash, rest by N+5 | `captures/shoot_strip_v1.png` (looked at); commit 8bd123b message | ✔ |
| B06 | Authority table: Dust.frame only MotionAnim; Suspension only FireAnim; hull/turret position only tank.gd | CHANGE-BRIEF.md lines 39–45 | ✔ |
| B06 | Why Suspension was added above them | tank.gd 180–181 write hull/turret position every tick; brief line 165 | ✔ |
| B06 | Both players on the physics clock | tank.gd lines 96, 102 `ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS` | ✔ |
| B07 | Driving: track_dust plays, dust visible; stopped: clip stops, dust gone; fire: the tank sits down | capture `drive` + readout (frames 20–64 MOVING/visible, 65+ IDLE/stopped/hidden, 86 Suspension y 2.00); tank.gd 189–202 | ✔ observed |
| B08 | Shell from a tick counter in `_weapon_tick()`, tick 2 = frame 1, READY on tick 10 | tank.gd 207–219, 185 | ✔ |
| B09 | Shell P+2, clip frame 1 on P+3, 1 tick = 0.0167 s, check C1, 30/60/144 | `logs/test_anim_states_{30,60,144}fps.log` CLOCKS lines; CHANGE-BRIEF.md Revisions line 172 | ✔ |
| B09 | The capture agrees | drive.log: shell event frame 86 (= N+1) ; readout FireAnim 0.0333 s at end of frame 86 | ✔ consistent (2 ticks per frame, so P+2/P+3 share a frame) |
| B10 | Hit in startup/active/recovery: shot goes; 2nd fire during FIRING ignored | capture `hits` + hits.log (4 shells for 4 shots, "fire pressed again on tick 4 (FIRING)", no extra shell); test_anim_states H-*/G1 | ✔ observed. Note on screen: in play the reload (48 ticks) also blocks a 2nd press; the FIRING guard alone is isolated only in G1 (reload forced to 0) |
| B11 | Death in each phase: shot finishes, one shell, READY tick 10 | death_s/a/r logs; test_anim_states D-*; tank.gd 164–168 | ✔ observed |
| B12 | readback 49, anim_states 34 at 30/60/144, edges 27 at 30/60/144, pins 11 | logs `test_clip_readback_60fps`, `test_anim_states_*`, `test_anim_edges_*`, `test_pins_60fps` RESULT lines | ✔ |
| B12 | Edge test: P+2, P+4, P+10 with hit, death, 2nd fire, one tick before/on/after | `tests/test_anim_edges.gd` header; log lines | ✔ |
| B12 | PIN-1/2/4 re-pinned +2 ticks, the only pins that changed, as predicted | commit f12f9f9; test_pins.gd "RE-PINNED A7"; CHANGE-BRIEF.md line 127 | ✔ |
| B13 | M5 frame→frames caught, M2 loop caught, M6 cell 4 caught, M7 empty-cache reimport passed as expected (baked .tres, no importer), M3 continuous caught, M4 frame 2 caught, each in a worktree | `logs/a7-mutations.txt`; commits 7b1465b, 392d1c4 | ✔ |
| B13 | Blind spot: C1 checks \|shell − clip\| only; sign flipped −1 → +1 and passed | a7-mutations.txt M4 run lines (C1 PASS, per run [1,1,1,1,1]); test_anim_states.gd line 334 `absi(d)` | ✔ |
| B13 | No headless run can show whether the motion reads | prompt; CHANGE-BRIEF evidence split line 139 | ✔ |
| B14 | Claude measured the v1 squash ≈ 5 %, slight | **prompt only** (not in the repo) | student's account, labelled on screen |
| B14 | The student judged it clearly visible and kept it | TUNING.md line 13 | ✔ |
| B14 | Dust v2: the student faintly; Claude no dust pixels | TUNING.md revision 1 result | ✔ |
| B14 | v3 DUST_BEHIND 34 fixed it; all 8 facings by eye | TUNING.md revision 2 result (4f88f1b, commit 0d94913); revision message | ✔ |
| B15 | Agent said test_hit_flash and test_cover_hit_burst_state would survive, didn't run them; both failed; fixes | `prompts/a7/session-5a.jsonl` ("should survive"); commit 6600d89; CHANGE-BRIEF Revisions line 173; fix_*.py | ✔ |
| B15 | Unrequested logs/_run_all.sh, deleted | commit 1e3205d message | ✔ |
| B15 | DUST_BEHIND 14 guess hid the dust | TUNING.md line 19 | ✔ |
| B15 | check_tools_parse run to "check" the preview, never loads it | prompt; `tests/check_tools_parse.gd` lists only A5 capture tools (read in session-7a) | ✔ (claim as stated by the student; the file confirms it never loads the preview) |
| B15 | Uncertain: at 30 fps 2nd press on even ticks only (P+9, P+11 not hit exactly); reload 0: shot on P+10 doesn't replay shoot; unreachable (reload 48 > clip 10) | `logs/test_anim_edges_30fps.log` (seen rel 8 / 10); 60 fps log "FireAnim position … rel11=-1.0000"; commit 4f88f1b message | ✔ |
| B15 | Next step: replay shoot from its start on every new shot | revision message | ✔ |
| B15 | Contributions | prompt; commit messages (agent/mine labels) | student's account |
| B15 | Sheet generated by code, own work, no third-party art | `assets/game/fx/ATTRIBUTION.md`; CHANGE-BRIEF.md lines 51–58 | ✔ |
| — | Removed from "uncertain": dust in all 8 facings | checked by the student (TUNING.md revision 2 result) | ✔ |

Not claimed: TEST-REPORT.md has no A7 section at 4f88f1b; the film says so on the tests figure.
Comment drift noticed, not claimed on screen: `tools/make_dust_sheet.gd` line 11 still comments "muddy brown" next to the
revision-1 pale-sand colour.
