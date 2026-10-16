# FACTCHECK — claude-liam-walker-tank-a3-assets

Every on-screen or spoken claim, with its source. Game revision **9baa12c** (working tree clean when checked).
"Re-run" = run by Claude on an isolated `git archive 9baa12c` copy on 2026-10-15 (outputs in `capture/`).

| Beat | Claim | Source |
|---|---|---|
| B00 | walker-TANK is a 2D top-down tank game; A3 = three 3D assets via Blender MCP, shown in Godot | CONCEPT.md, CHANGE-BRIEF.md *Context*; README.md |
| B00 | Prompt on screen is a reconstruction | Labelled on screen and in narration; no original Walker chat was supplied |
| B01 | The checks measure, they do not show looks | `tests/check_a3_assets.gd` lines 9–18; TEST-REPORT.md *What the checks do and do not show* |
| B02 | Brief written/committed before building; three assets and roles; cover 4.0 m wide vs 3.4 m hull | CHANGE-BRIEF.md (first line; Asset 1–3); FRICTIONAL.md §1 (commit e6f9f6f) |
| B03 | Connected on port 9876; libraries and generators unchecked | `a3-evidence/02-mcp-panel.png`, `02b-scene-info-telemetry-off.png` (all "off") |
| B03 | Four tools denied in settings | `.claude/settings.json` (generate_3d, search_assets, import_asset, record_trajectory_feedback) |
| B03 | Every shape from cubes, built by code | SOURCES.md *Assets*; CHANGE-BRIEF.md *Common rules* |
| B04 | Seven-step plan, two decisions asked | `a3-evidence/03-prompt-plan-cover-wall.png` ("Proposed steps (7 execute_blender_code calls)", "Decisions I need from you" 1–2) |
| B04 | Student chose to join | FRICTIONAL.md §3 |
| B04 | 4.0 × 1.0 × 1.8 m, 36 triangles, limit 60 | `a3-evidence/03b-cover-wall-result.png` |
| B04 | The prompt's own wording | **Not shown**: the screenshots show Claude's reply, not the typed prompt. The film says "one request" and labels the panel "Claude's plan" |
| B05 | Edit Mode, block B +0.6 m in X; sidebar 4 m; moved 0.5993 m, 0.7 mm short; sidebar rounds | FRICTIONAL.md §6; TEST-REPORT.md problem 4; `05-hand-edit.png`, `06-sidebar-4m.png`, `06b-hand-edit-0.7mm-short.png` ("0.9993 to 1.9993", "+0.5993") |
| B06 | Three .glb instanced, side by side on X, scale 1; hull box 6 × 1.6 × 3.4 labelled NOT an asset | `scenes/asset_room_3d.tscn` lines 35–51, 17–19 |
| B07 | Running scene; wall wider than hull is deep; crate small; hedgehog below hull; dark faces, one light | Movie Maker capture `capture/room-run.mp4`; sizes 4.0 vs 3.4, 1.4 vs 1.6 (CHANGE-BRIEF.md); TEST-REPORT.md *Not resolved* |
| B07 | Fixed camera, no motion | `asset_room_3d.tscn` has no script/animation; frames inspected |
| B08 | Brief sizes in Godot axes; TOL 0.01 m, tighter than brief's ±0.1 m | `tests/check_a3_assets.gd` lines 22–27, 7 |
| B09 | 18/18 PASS, exit 0 | Re-run: `capture/check-stdout.txt` (18 PASS lines, `RESULT: PASS (0 failure(s))`, `check_exit=0`); matches TEST-REPORT.md and `08-check-pass.png` |
| B09 | FAIL path proven once (exit 1) | TEST-REPORT.md *The check failing on purpose*; `08b-fail-path-proven.png`. Not re-run for the film |
| B10 | 2.4 m beams → 1.559 m, over tolerance; Claude recommended 45° turn; student chose 2.125 m | `04-hedgehog-options.png`; CHANGE-BRIEF.md *Revisions*; FRICTIONAL.md §5 |
| B10 | Join AttributeError ('NoneType' … 'select_set') | `03b-cover-wall-result.png`; FRICTIONAL.md §3 |
| B10 | Comment said "0.1 m in from the front face", code centred block B | FRICTIONAL.md §3 |
| B11 | Verdict lines (checked / by eye / uncertain / next step / contributions / revision) | TEST-REPORT.md *HUMAN CHECK*; FRICTIONAL.md *Who did what*, *Unresolved*; SOURCES.md *What AI contributed*; next step derived from the check's stated gap (placed copies untested) |

## Corrections made during the build

1. **B11, "approved each call" was wrong.** FRICTIONAL.md §6 says some calls ran in auto mode before the student
   noticed ("Allowed by auto mode classifier"). Narration and verdict line changed to say the student approved the
   code calls, except a few that auto mode ran.
2. **B04 prompt wording.** The supplied screenshots do not show the typed prompt, so the film shows Claude's plan in
   reply and says "one request"; it does not quote or reconstruct the prompt.
3. Hedgehog numbers are stated as numbers only; no formula is typeset (no math beat in this film).
