# FACTCHECK — claims in the narration and where they were verified

Source revision for every claim: walker-TANK commit `4616fc7`. "Log" = `capture/run-01-inputs.jsonl` (frame = movie frame;
calibrated against the pause label, frame 739, and the victory panel, frame 1426). Narration spells YunqiZ as
"Yoon-chee Zee" for Kokoro (whisper round-trip of "YunqiZ" heard "Yunkisei").

| Beat | Claim | Verified against |
|---|---|---|
| B00 | CSYE7270 Assignment 2 asset slice; prompt is a reconstruction | assignment brief; label on screen |
| B02 | Minimum: two character states + one environment asset, four SFX events, one clean loop | brief "What counts as a generated asset" (quoted verbatim on screen) |
| B02 | Started from an empty Godot project; Godot 4.7.2 | SOURCES.md, README.md, `--version` |
| B03 | Native 4K Movie Maker, scripted input | CAPTURE.md; probed 3840×2160, 1667 frames |
| B05 | ~64 px; up = down at first; blade + box added | CHARACTER-SHEET.md silhouette section |
| B06 | v1 at 0.55 / 0.70 flat, 0.80 panels but blade lost; seed + prompt fixed | ASSET-LOG G-01–G-03, FRICTIONAL 2026-10-02 |
| B07 | Per-face gradient 1.12× / 0.82×; grain script with fixed seed 7 | draw_guides_v2.py 14–20; texture_guides_v2.py line 4 |
| B09 | Settings read from the PNG match ASSET-LOG | ComfyUI `prompt` metadata (evidence/raw-output-metadata.json): seed 846322750311363, 25 steps, cfg 7.0, dpmpp_2m karras, 0.55, guide2_hull_right.png |
| B09 | 0.65 added a turret dome → rejected | ASSET-LOG G-05 |
| B10 | First cutout dropped the blade; ≥2000 px rule; docstring stale | FRICTIONAL "Mistake caught"; cutout_hull.py lines 3 vs 18–23 |
| B11 | Overlap ≈ 0.99 | ASSET-LOG ("IoU 0.991–0.993"): reported by the log, not re-measured here |
| B12 | Down hull 15–20 % brighter; per-channel gain toward #4B5320 on olive pixels | ASSET-LOG G-10; process_sprites.py 12, 25, 30–37 |
| B13 | 5 generated + 3 mirrored; no cupola on up/right, 1–2 px | CHARACTER-SHEET, tank.gd SLOT_FLIP, ASSET-LOG decisions |
| B14 | Hull from movement only while moving; turret from aim; idle 0.2 px vs moving 0.6 px ("a third") | tank.gd 123–131 |
| B15 | Two hits during the tour, smoke starts | log: hp 75 @ f153, hp 50 smoke @ f356 |
| B16/B17 | Crack at 2, break at 4, shape disabled; seen at f420 / f505 | cover.gd 5–6, 33–45; log cover_stage |
| B18/B19 | Smoke ≤ 60 %, flames ≤ 30 %; fatal hit → explosion only | tank.gd 163–175, 195–198; log f975 (50 %, smoke), f1207 (25 %, flames) |
| B19 | Second enemy destroyed, camera shakes | log enemy_destroyed f1002; tank.gd die() → world.shake(6.0) |
| B20/B21 | Music stops on death, 2 s wait, respawn with music from 0 | main.gd 257–268; log music_state stopped f554, playing pos 0.03 f614 |
| B21 | Pause holds the music's place | log music paused at 4.203 s (f739), resumed at 4.214 s (f814) |
| B22/B24 | level_won guard; one victory sound | main.gd 271–280; log victory count 1 @ f1426 |
| B25/B26 | Grey fill hard to read (line 299); thresholds 0.6/0.3 | main.gd 299, 378; play-01 screenshot; run-01 frames 100/380/450 at hp 100/50/25 |
| B27 | Test calls `_on_body_entered` by hand | test_sound_triggers.gd 47–48 |
| B28 | 8/8 pass, exit 0, leak warnings still printed; report says fixed | tests/test-run-01-stdout.txt; TEST-REPORT "the test now frees the scene" |
| B29 | Human checks: sound on + muted, loop seam; not tested: others, laptop speakers | TEST-REPORT Results + "Not tested" |
| B30 | Model → asset mapping; effects are code particles | SOURCES.md, ASSET-LOG models table, main.gd/tank.gd CPUParticles2D |
| B31 | Decisions: student chose 0.75 first, Claude raised stripe/shape, student chose 0.60 | FRICTIONAL "turret denoise" entry |
| B32 | T-12 log row disagrees with the file | ASSET-LOG T-12 vs PNG metadata of CHAR-turret_down_00009_.png (0.55, seed 499619143762383) vs FRICTIONAL |
| B32 | Missing referenced files / placeholders | `ls` of the repo at 4616fc7; TEST-REPORT text |
| B33 | All observed items | coverage.json + log |

## Corrections made while writing
- The take's events differ from the rehearsals (random enemies); every gameplay sentence was written after reading
  the final take's log and contact sheets, not from the rehearsal.
- B21 narration (11.4 s) did not fit its first 9.7 s window: the window was extended to 18–30 s (real footage), not the speech retimed.
- "A fatal hit skips the hit sound" was checked against tank.gd 168–173 (die() returns before `_play_hit_sound`).
- No math notation appears in the film (MATH-TYPESETTING.md not triggered).
