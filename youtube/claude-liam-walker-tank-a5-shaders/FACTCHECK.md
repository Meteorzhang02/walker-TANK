# FACTCHECK — claude-liam-walker-tank-a5-shaders

Every on-screen or spoken claim, with its source. Game revision **561d47d** (`git rev-parse --short HEAD`, working
tree clean when checked, 2026-10-28). No Godot run and no new capture were made for this film: all pictures are the
student's existing captures and recording; all numbers come from the files named below.

| Beat | Claim | Source |
|---|---|---|
| B00 | walker-TANK is a 2D top-down tank game; A5 added a hit flash shader and brick materials | README.md (top, "What Assignment 5 added") |
| B00 | The prompt on screen is a reconstruction | Labelled on screen and in narration; no original Walker chat was supplied |
| B00 | State: YunqiZ just took a non-fatal hit, red fading over 0.5 s; 3D object cover_wall in asset_room_3d.tscn, two walls | CHANGE-BRIEF.md §1, §2 rule 2, §5 and Revision 1 (CoverWall + CoverWall2) |
| B01 | A shader runs for every pixel | LANGUAGE-NOTES.md Q2 ("runs once for every pixel"), Q7 |
| B02 | Code = `shaders/hit_flash.gdshader` lines 1–9, verbatim (the whole file; the requested 1–8 plus the closing brace) | the file; `gamedev-evidence.json` excerpt check |
| B02 | Typed by the student | FRICTIONAL.md Step 2 ("I typed it in myself"); SOURCES.md *What I personally did* |
| B02 | fragment() runs per pixel and cannot see the game; state only via uniform hit_amount | LANGUAGE-NOTES.md Q2, Q7; shader lines 3, 7 |
| B02 | Line 8 is the brief's colour line | CHANGE-BRIEF.md line 45 equals shader line 8 (string-compared by make_sheet.py) |
| B02 | The driver sets it (line 70; PARAM = "hit_amount", line 12) | `scripts/hit_flash_driver.gd` lines 12, 70; written by Claude Code (SOURCES.md session 2) |
| B03 | Screen recording of the student's play; a shell hits, YunqiZ turns red, fades in about half a second; second hit flashes again; enemies never red | `D:/CSYE7270/a5-evidence/play.mp4` (sha256 f1581b13…eda2) inspected frame by frame: hits at source ≈6.65 s and ≈11.0 s, red gone within ≈0.5 s at 10 fps sampling; no red enemy in 4.5–14.7 s. "About half a second" is an observation; the measured 0.5000 s is from the headless test (TEST-REPORT §3) |
| B04 | Scripted in-engine captures at 0.0/0.5/1.0/2.0 | `docs/a5/captures/hit_flash_*.png`, `tools/capture_hit_flash.gd` run windowed by the student (TEST-REPORT §4) |
| B04 | P2 matched exactly at 0/0.5/1.0 | hit_flash_pixels.csv: (16,16,16) (88,11,11) (159,6,6), predicted = measured |
| B04 | P1 missed by up to 21 because the turret covers it | CSV maxdiff_centre 21/15/8, turret_alpha_max_3x3 1.000 |
| B04 | Turret recomputed in a dated revision; matches within 1 | CHANGE-BRIEF.md Revision 2026-10-27 (P1): (70,76,31) (126,53,22) (181,30,12) vs measured (70,76,31) (126,53,22) (181,31,12) |
| B04 | At 2.0 both pixels (255,0,0): hint_range does not clamp | CSV rows value 2.0; LANGUAGE-NOTES Q5; TEST-REPORT §4 |
| B05 | Code = `shaders/hint_experiment.gdshader` lines 1–14 (whole file), lines 4–5 lit | the file |
| B05 | One grey file 64/128/192, two samplers; line 4 source_color = colour, line 5 no hint = data | CHANGE-BRIEF §4; MATERIALS.md §5; LANGUAGE-NOTES Q4, Q6; `materials/hint_*.tres` line 12 (shown as the key = value after the last "/") |
| B06 | Quad A 64/128/192, Quad B 137/188/225, as predicted, 6/6 exact | hint_pixels.csv (maxdiff 0 on all six); predictions CHANGE-BRIEF §4 |
| B06 | Background grey measures 127 (so A's 128 band blends in) | measured by make_evidence.py, pixel (640, 600) of hint_both.png |
| B06 | Brick line 4 colour with source_color; line 9 roughness data, none | `shaders/brick_surface.gdshader` lines 4, 9; LANGUAGE-NOTES Q6 |
| B07 | One shader, two materials differing in two values (tint 0.78/0.72/0.66, brightness 0.7) | `materials/cover_wall_*.tres` lines 10–13; MATERIALS.md §3 |
| B07 | Shader edit darkened both walls (R 73.4→54.7, 49.9→38.6) | shader_edit_materials_captures.csv vs materials_captures.csv (side-by-side rows); TEST-REPORT §8 |
| B07 | Material edit changed only the damaged wall (49.9→43.8; intact 73.4) | materials_captures.csv row material_edit_damaged_only.png |
| B07 | Sweep: brightness 2.0, roughness_scale 0.0, uv_scale 0.1 / 4.0, means shown | materials_captures.csv rows |
| B07 | "Brick size visibly changes, but the look is still the student's call" | Visible in the four captures (looked at for this film); TEST-REPORT human item 5 and §7 ("to confirm by eye") |
| B08 | Code = `shaders/brick_surface.gdshader` lines 1–11 | the file |
| B08 | shader_type spatial = lit 3D shader | LANGUAGE-NOTES Q1 |
| B08 | hint_range sets the Inspector slider's ends | LANGUAGE-NOTES Q4, Q8; captures-output.txt (the sweep read min/max from the uniform list) |
| B08 | Generated line 7 gives albedo source_color (like brick line 4); line 19, the normal map, has none (like line 9) | `shaders/standard_generated.gdshader` lines 7, 19 (shown as verbatim prefixes, marked "…"); LANGUAGE-NOTES Q6 |
| B09 | ALBEDO = brick line 33 | the file, line 33 (shown verbatim in the figure's excerpt strip) |
| B09 | Top 87.5, front 73.4, end 60.8 (red means) | measured by make_evidence.py from materials_side_by_side.png (boxes in the figure; `capture/litwall-means.json`); the front box equals the capture tool's own 11×11 mean (73.4, 54.1, 37.7) |
| B09 | The 2D flash had no light, so its numbers were exact | CHANGE-BRIEF §3 ("Output is unshaded: no Light2D or CanvasModulate", hdr_2d off) |
| B10 | 50/50 at 30, 60, 144 fps; 76/76; baselines 18/18 and 8/8 | logs/*.log RESULT lines; exit 0 in docs/a5/step2-output.txt and TEST-REPORT rerun at 3d48047 |
| B10 | Three mutations each exit 1 | step2-output.txt lines 122, 135 (mutation1/2 exit=1); commit 1718cdd message (mutation 3 exit 1); logs show 45/5, 47/3, 75/1 |
| B10 | Headless can't show the look, the white flash under the red, the pause rule by hand | TEST-REPORT §13; README *Known limitations (A5)*; FRICTIONAL playtest entry |
| B11 | Commit 561d47d | `git -C walker-TANK rev-parse --short HEAD` |
| B11 | Predictions held except P1 (wrong layer), revised and dated | B04/B06/B07 sources above |
| B11 | Agent mistakes caught: CLAUDE.md scope too narrow; Use External key names in test_materials; probe script left in logs/ | FRICTIONAL.md Step 1, Step 3 ("use_external/enabled" vs "use_external"), Step 2 ("The probe file was left in logs/; I deleted it") |
| B11 | Student typed all three shaders from Claude chat's suggestions; LANGUAGE-NOTES answers written in Chinese, translated | SOURCES.md *Claude (claude.ai chat)* and *What I personally did*; LANGUAGE-NOTES.md header |
| B11 | Claude Code wrote the driver, tests, materials, tools, document drafts | SOURCES.md session table 1–6; FRICTIONAL *Who did what* |
| B11 | Texture: Poly Haven red_bricks_04, Rob Tuytel, CC0 | SOURCES.md *Textures*; assets/textures/brick/ATTRIBUTION.md |
| B11 | Next step: the pause rule by hand | TEST-REPORT §13 / FRICTIONAL *Unresolved* ("The pause rule has no human check") |
| B13 | Title | exact restatement of metadata.title |

Not claimed: anything about how the bricks or the flash *look* beyond what the captures show; any fun or readability
judgement; any result not in a file. Math: the film shows no equations (the colour line is shown as source code).
