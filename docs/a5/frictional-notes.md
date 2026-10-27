# My notes for FRICTIONAL.md (raw, in order; organise, do not add)

Dates: work began 2026-10-25 (setup), most work on 2026-10-27.

## Setup (2026-10-25)
- The assignment's run-test.sh assumes macOS and a godot/ folder. My project.godot is at the repo root and I use Windows + Git Bash, so I wrote a Windows version with --path . and the full Godot console path (commit 3402469).
- Git warned it would convert run-test.sh to CRLF and stored it as 100644. I added .gitattributes (*.sh text eol=lf) and set +x; checked with git ls-files -s (100755) and git ls-files --eol (i/lf w/lf) (commit c4a1f84).
- Baseline before any A5 change: check_a3_assets 18/18, test_sound_triggers 8/8, both exit 0. test_sound_triggers prints a pre-existing "5 resources still in use at exit" message; not a SHADER/SCRIPT ERROR.
- Pixel choice: a PIL search for flat 5x5 areas in hull_right.png found only 33 flat pixels, all olive; the white stripe is too thin. A 3x3 search found the dark track. I chose P1 (99,50) olive and P2 (59,109) track.

## CHANGE-BRIEF (2026-10-27, commit 1da47e9)
- Drafted with Claude (claude.ai chat) from my decisions and project facts I collected with grep. Claude suggested the colour-line form, flash_strength, pure red as the flash colour and D = 0.5 s; I accepted them.
- I computed the 6 pixel predictions and the 6 hint predictions by hand with a calculator, except the worked example P1 @ 0.5 which Claude showed as the method. Claude checked them: all 12 correct; my intermediate for 128 (0.7492) was corrected to 0.7504, same final 188.
- The A3 brief was archived to docs/a3/ first.

## Step 1 — CLAUDE.md (session-1.jsonl, 20 turns, success, no denials)
- The draft was good but limited 3D changes to cover_wall only, which would have blocked the hint-experiment scene and the Step 4 scratch scene. I widened Out of scope, confirmed the renderer in Project Settings (forward_plus), and added standard_generated.gdshader and LANGUAGE-NOTES to Ownership (commit 6514c32).
- I missed the required "Headless facts" block at first; I added it later the same day, after the mutation and Use External findings (commit 19c89b8).

## Step 2 — hit_flash shader (commit 0c20cc6)
- I did not know GDShader syntax. Claude (chat) gave the full shader with a line-by-line explanation; I typed it in myself and checked every uniform name against the brief.
- Agent session 2 (session-2.jsonl, 38 turns, success): driver + test, one line added to main.gd. 4 tool calls were denied by the allowlist: two compound test commands, one direct Godot run that bypassed the wrapper to probe a broken shader, one PowerShell delete. The probe file was left in logs/; I deleted it and added logs/.gdignore.
- The agent was unsure whether headless reports shader compile errors. Mutation 1 (delete a semicolon) settled it: SHADER ERROR: Expected a ';', exit 1. Mutation 2 (rename hit_amount) exit 1.
- asset_room_3d.tscn showed a diff after the session; it was the Godot editor re-saving in 4.7 format, not the agent; I reverted it.
- Known limit from the agent's report: reset_full() on a living tank mid-fade would not reset the value; the game only calls it after death. The uniform list reports flash_color with hint 0, so source_color is only checked from the source text.

## Step 3 — brick shader and materials
- Before writing the shader I inspected cover_wall.glb with a Godot tool (tools/inspect_cover_wall.gd): two surfaces (M_Brick 24 verts, M_BrickDark 48 verts) and NO UVs. So the shader projects from object-space position (box projection), recorded as a dated revision before the shader (commit 9d14b83).
- The brick PNGs had been imported Lossless, no mipmaps, normal map Detect, detect_3d compress_to VRAM. I set them to the brief's values with detect_3d disabled and reimported headless.
- Claude (chat) gave brick_surface.gdshader and hint_experiment.gdshader with explanations; I typed both (commit fdcc415).
- Agent session 3 (41 turns): materials, CoverWall2, hint scene, make_hint_png.gd, MATERIALS.md, test_materials.gd. I ran make_hint_png.gd, imported the PNG Lossless / no mipmaps / detect_3d off, and set Use External on M_Brick in Advanced Import Settings.
- test_materials then still failed on Use External. I read cover_wall.glb.import: the setting was there, saved as "use_external/enabled" and "use_external/path"; the agent's test looked for a key "use_external" (it had said it did not know 4.7's format). Session 4 fixed only that check: 76/76.
- Mutation 3 (delete source_color from the colour sampler): exit 1.

## Use It (windowed captures, tools by the agent in session 5, run by me)
- Hint experiment: all six bands exactly as predicted (A 64/128/192, B 137/188/225), difference 0.
- Hit flash: P2 matched exactly at 0.0/0.5/1.0. P1 was 21/15/8 off: the capture tool showed the turret covers that pixel. The turret texel under it, turret_right.png (99,71), is (70,76,31); recomputing with the colour line after the observation gives (126,53,22) and (181,30,12); measured (126,53,22) and (181,31,12). Recorded as a dated revision; lesson: choose named pixels on the final drawn layer.
- 2.0 from code: both pixels (255,0,0), so hint_range does not clamp.
- Sweep: black tint or brightness 0 gives (22,22,22), not black (specular/ambient remain); brightness 2 raises the wall mean from 73 to ~100, not 146, because brightness multiplies linear colour and the output is sRGB-encoded ((73.4/255)^2.2 x 2 -> ~100.5); roughness 0 makes the wall darker; uv_scale changes brick size.
- One shader, two materials: editing the shader's ALBEDO line (x 0.5) darkened both walls (73.4 -> 54.7, 49.9 -> 38.6); setting brightness on the damaged material only changed only CoverWall2 (49.9 -> 43.8).
- OS screenshot vs engine capture: my first attempt captured the wrong window (850x287 terminal screenshot). The second (1920x1080, Win+PrtScn) showed all six bands at exactly the same values. I still trust the engine capture for measurement.
- Godot generated .import files for the captures in docs/; I added docs/.gdignore and removed them.

## Step 4
- Converted a StandardMaterial3D (albedo, normal map, roughness) to ShaderMaterial in a scratch scene and saved shaders/standard_generated.gdshader. I first saved the scratch scene into shaders/ by mistake and moved it to scenes/. The editor had re-saved brick_surface.gdshader (line endings only); I restored it.
- LANGUAGE-NOTES: I asked Claude to write the answers; it declined because the assignment requires my own words. My first Chinese draft was copied from Claude's explanation notes; Claude pointed that out. I rewrote each answer briefly in my own words in Chinese; Claude translated and checked line references, and pointed out one mistake in question 4 (I had the 64/137 sampler reversed), which I accepted.

## Playtest (human, 2026-10-27, in the editor)
Got hit several times by enemy shells. Each hit flashed YunqiZ red and faded quickly; a second hit during the fade restarted it. Enemies hit by my shells did not flash red (only their existing white flash and the impact effect). After being destroyed and respawning there was no red left. I did not see the existing white flash on YunqiZ: the test shows modulate still reaches 2.2, but at the same moment the red is at its strongest. I tried to pause with Esc during the fade but could not press it within 0.5 s, so rule 5 rests on the headless test only.

## Unresolved / limits
- The white _flash() is still in the code but visually masked by the red at the hit.
- The pause rule has no human check.
- reset_full() on a living tank would not clear the fade.
- Normal-map curl check: not applicable, no game material uses a normal map (nor_gl is only in the Step 4 scratch material).
- Helper bash/python scripts I ran (setup, captures, commits) were written by Claude (chat).
