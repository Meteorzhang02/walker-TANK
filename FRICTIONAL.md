# Assignment 5 — hit flash shader and brick surface materials

**How this was written.** I kept raw notes in order while working ([docs/a5/frictional-notes.md](docs/a5/frictional-notes.md), commit `3d48047`; organised from my session with Claude chat and reviewed by me). Claude Code (session 6, [docs/a5/sessions/prompt-6.txt](docs/a5/sessions/prompt-6.txt)) arranged them into the dated entries below. It added only commit hashes, file paths, log and capture names and numbers taken from those files. The wording is mine where possible. **Retrospective:** every entry was written from my notes on 2026-10-27. The 2026-10-25 setup entry was written two days after the work; the others on the same day.

**Who is who:** *Me* = what I decided, typed, ran, checked or changed. *Claude chat* = Claude in claude.ai (brief drafting, the three shaders' structure, helper bash/python scripts, translation). *Claude Code* = the agent in this repo, sessions 1–6 (`docs/a5/sessions/prompt-N.txt`, `session-N.jsonl`; for session 6, [session-6-excerpt.md](docs/a5/sessions/session-6-excerpt.md)).

**Versions:** Windows 11 · Git Bash · Godot 4.7.2 stable, Forward+ · Python + PIL (helper scripts).

## 2026-10-25 — setup (retrospective, written 2026-10-27)

- **Tried:** the assignment's `run-test.sh`.
- **Expected:** to use it as given.
- **Happened:** it assumes macOS and a `godot/` folder. My `project.godot` is at the repo root and I use Windows + Git Bash.
- **Changed:** "I wrote a Windows version with --path . and the full Godot console path" (`3402469`). "Git warned it would convert run-test.sh to CRLF and stored it as 100644." I added `.gitattributes` (`*.sh text eol=lf`) and set +x, then checked with `git ls-files -s` (100755) and `git ls-files --eol` (i/lf w/lf) (`c4a1f84`).
- **Baseline before any A5 change:** check_a3_assets 18/18, test_sound_triggers 8/8, both exit 0. test_sound_triggers prints a pre-existing "5 resources still in use at exit" message; it is not a SHADER/SCRIPT ERROR.
- **Also:** I archived the A3 brief to `docs/a3/` (`19aa9c1`) and added the Poly Haven red_bricks_04 maps with `ATTRIBUTION.md` (`ed1976a`).
- **Pixel choice:** "a PIL search for flat 5x5 areas in hull_right.png found only 33 flat pixels, all olive; the white stripe is too thin. A 3x3 search found the dark track. I chose P1 (99,50) olive and P2 (59,109) track."
- **Learned:** TBD (not in my notes).
- **Who:** me. The PIL script was a helper script written by Claude chat.

## 2026-10-27 — CHANGE-BRIEF before any shader (`1da47e9`)

- **Tried:** writing the spec before any shader or agent prompt.
- **Who:** "Drafted with Claude (claude.ai chat) from my decisions and project facts I collected with grep. Claude suggested the colour-line form, flash_strength, pure red as the flash colour and D = 0.5 s; I accepted them."
- **Checked:** "I computed the 6 pixel predictions and the 6 hint predictions by hand with a calculator, except the worked example P1 @ 0.5 which Claude showed as the method. Claude checked them: all 12 correct; my intermediate for 128 (0.7492) was corrected to 0.7504, same final 188."
- **Learned:** TBD (not in my notes). The hint predictions later matched 6/6 (see Use It).

## 2026-10-27 — Step 1: CLAUDE.md (Claude Code session 1)

- **Trace:** [prompt-1.txt](docs/a5/sessions/prompt-1.txt), [session-1.jsonl](docs/a5/sessions/session-1.jsonl) (20 turns, success, no denials). Commits `63d7ba0` (draft, unedited), `6514c32` (my review), `19c89b8` (my addendum).
- **Tried:** having Claude Code draft CLAUDE.md, with nothing else changed.
- **Happened:** "The draft was good but limited 3D changes to cover_wall only, which would have blocked the hint-experiment scene and the Step 4 scratch scene."
- **Changed:** "I widened Out of scope, confirmed the renderer in Project Settings (forward_plus), and added standard_generated.gdshader and LANGUAGE-NOTES to Ownership" (`6514c32`).
- **Mistake of mine:** "I missed the required 'Headless facts' block at first; I added it later the same day, after the mutation and Use External findings" (`19c89b8`).
- **Learned:** TBD (not in my notes).
- **Who:** Claude Code drafted; I reviewed, confirmed the renderer and edited.

## 2026-10-27 — Step 2: hit flash shader, driver and test (Claude Code session 2)

- **Trace:** [prompt-2.txt](docs/a5/sessions/prompt-2.txt), [session-2.jsonl](docs/a5/sessions/session-2.jsonl) (38 turns, success). Commits `0c20cc6` (my shader), `be94463` (driver + test), `9217896` (evidence). Output [docs/a5/step2-output.txt](docs/a5/step2-output.txt). Logs [logs/test_hit_flash_30fps.log](logs/test_hit_flash_30fps.log), [_60fps](logs/test_hit_flash_60fps.log), [_144fps](logs/test_hit_flash_144fps.log), [mutation1](logs/mutation1_semicolon_60fps.log), [mutation2](logs/mutation2_rename_60fps.log).
- **Shader:** "I did not know GDShader syntax. Claude (chat) gave the full shader with a line-by-line explanation; I typed it in myself and checked every uniform name against the brief."
- **Driver and test:** Claude Code wrote `scripts/hit_flash_driver.gd`, added one line to `main.gd`, and wrote `tests/test_hit_flash.gd`.
  - Its first run gave 52 passed, 1 failed. That was a bug in the test: its number regex picked up the `4` in `vec4`. It fixed the test.
  - Final result: 50/50 at 30, 60 and 144 fps. The fade took 0.5000 s of game time at all three rates.
- **Friction:** "4 tool calls were denied by the allowlist: two compound test commands, one direct Godot run that bypassed the wrapper to probe a broken shader, one PowerShell delete. The probe file was left in logs/; I deleted it and added logs/.gdignore."
- **Expected vs happened:** "The agent was unsure whether headless reports shader compile errors. Mutation 1 (delete a semicolon) settled it: SHADER ERROR: Expected a ';', exit 1. Mutation 2 (rename hit_amount) exit 1." I ran both mutations by hand and restored the file each time (restore diff empty, `step2-output.txt` 3a/3b).
- **Editor re-save:** "asset_room_3d.tscn showed a diff after the session; it was the Godot editor re-saving in 4.7 format, not the agent; I reverted it."
- **Known limits from the agent's report:** "reset_full() on a living tank mid-fade would not reset the value; the game only calls it after death. The uniform list reports flash_color with hint 0, so source_color is only checked from the source text."
- **Learned:** headless does report shader parse errors (now in CLAUDE.md's Headless facts).
- **Who:** Claude chat gave the shader and explained it; I typed it, ran the mutations and reverted the scene. Claude Code wrote the driver and test and ran the tests.

## 2026-10-27 — Step 3 prep: cover_wall has no UVs (`9d14b83`)

- **Trace:** `tools/inspect_cover_wall.gd`, [docs/a5/step3-info.txt](docs/a5/step3-info.txt), [docs/a5/step3-setup.txt](docs/a5/step3-setup.txt), [logs/reimport_brick.log](logs/reimport_brick.log).
- **Expected:** the brief §5 plan, "UVs scaled by `uv_scale`".
- **Happened:** "Before writing the shader I inspected cover_wall.glb with a Godot tool (tools/inspect_cover_wall.gd): two surfaces (M_Brick 24 verts, M_BrickDark 48 verts) and NO UVs."
- **Changed:**
  - "So the shader projects from object-space position (box projection), recorded as a dated revision before the shader."
  - `uv_scale` became repeats per metre (0.1–4.0, default 0.5).
  - "The brick PNGs had been imported Lossless, no mipmaps, normal map Detect, detect_3d compress_to VRAM. I set them to the brief's values with detect_3d disabled and reimported headless" (reimport exit 0).
- **Learned:** TBD (not in my notes). CLAUDE.md had listed "whether the `.glb` has UVs" as unconfirmed.
- **Who:** me (inspection, revision, import settings, via helper scripts written by Claude chat).

## 2026-10-27 — Step 3: brick shader, materials, hint scene (Claude Code sessions 3 and 4)

- **Trace:**
  - Sessions: [prompt-3.txt](docs/a5/sessions/prompt-3.txt), [session-3.jsonl](docs/a5/sessions/session-3.jsonl) (41 turns), [prompt-4.txt](docs/a5/sessions/prompt-4.txt), [session-4.jsonl](docs/a5/sessions/session-4.jsonl).
  - Commits: `fdcc415` (my two shaders), `81b364b` (agent), `08ddf87` (my editor steps), `97fdec6` (evidence).
  - Outputs: [docs/a5/step3-finish-a.txt](docs/a5/step3-finish-a.txt), [step3-finish-b.txt](docs/a5/step3-finish-b.txt).
  - Logs: [logs/test_materials_60fps.log](logs/test_materials_60fps.log), [logs/mutation3_no_source_color_60fps.log](logs/mutation3_no_source_color_60fps.log), [logs/reimport_hint_1.log](logs/reimport_hint_1.log), [_2](logs/reimport_hint_2.log).
- **Shaders:** "Claude (chat) gave brick_surface.gdshader and hint_experiment.gdshader with explanations; I typed both."
- **Agent:** session 3 made the materials, CoverWall2, the hint scene, `make_hint_png.gd`, MATERIALS.md and `test_materials.gd`.
  - Its own run: 60 passed, 8 failed. All 8 were expected: 6 waited on the PNG, 2 on Use External.
  - It noted that `asset_room_3d.tscn` already had uncommitted editor-save changes and left them in place. They were committed with CoverWall2 in `81b364b`.
- **My steps:** "I ran make_hint_png.gd, imported the PNG Lossless / no mipmaps / detect_3d off, and set Use External on M_Brick in Advanced Import Settings."
- **Expected vs happened:** "test_materials then still failed on Use External" (75 passed, 1 failed).
- **Checked:** "I read cover_wall.glb.import: the setting was there, saved as "use_external/enabled" and "use_external/path"; the agent's test looked for a key "use_external" (it had said it did not know 4.7's format)."
- **Changed:** "Session 4 fixed only that check: 76/76."
- **Mutation 3:** "(delete source_color from the colour sampler): exit 1." My first run came before the session-4 fix, so it showed 74 passed, 2 failed. The second FAIL was the then-broken Use External check.
  - Rerun at `1718cdd`: exactly 1 FAIL ("colour sampler albedo_tex has source_color"), 75 passed, exit 1 ([logs/mutation3_no_source_color_60fps.log](logs/mutation3_no_source_color_60fps.log)).
  - After restoring the shader: 76/76, exit 0.
- **Learned:** Godot 4.7.2's key names for Use External (now in CLAUDE.md's Headless facts).
- **Who:** Claude chat gave the shaders; I typed them. Claude Code wrote the materials, scenes, tool, audit and test. I generated and imported the PNG, set Use External, found the key mismatch and asked for the one-check fix. I ran the mutation.

## 2026-10-27 — Use It: windowed captures (tools by Claude Code session 5, run by me)

- **Trace:**
  - Session: [prompt-5.txt](docs/a5/sessions/prompt-5.txt), [session-5.jsonl](docs/a5/sessions/session-5.jsonl).
  - Commits:
    - `240d2be` and `cb6f0bd` (17:31): tools; captures and CSVs.
    - `4721a4d` and `423c61c` (17:48): same messages, adding the files left out of the first pair (the tool test's `.uid`, the shader-edit captures, and Godot's `.import` / `.translation` files).
    - `d9b1837`: brief revision and cleanup.
  - Outputs: [docs/a5/captures-output.txt](docs/a5/captures-output.txt), [use-it-part2.txt](docs/a5/use-it-part2.txt), [use-it-part3.txt](docs/a5/use-it-part3.txt).
  - CSVs: [hit_flash_pixels.csv](docs/a5/captures/hit_flash_pixels.csv), [hint_pixels.csv](docs/a5/captures/hint_pixels.csv), [materials_captures.csv](docs/a5/captures/materials_captures.csv), [shader_edit_materials_captures.csv](docs/a5/captures/shader_edit_materials_captures.csv).
- **Tools:** Claude Code wrote three capture tools and `check_tools_parse.gd` (9/9). It could not run Godot windowed, and its PIL check was not approved. It listed "the turret may cover P1" as unconfirmed and made the tool print the turret's alpha.
- **Hint experiment:** "all six bands exactly as predicted (A 64/128/192, B 137/188/225), difference 0."
- **Hit flash:**
  - "P2 matched exactly at 0.0/0.5/1.0. P1 was 21/15/8 off: the capture tool showed the turret covers that pixel."
  - "The turret texel under it, turret_right.png (99,71), is (70,76,31); recomputing with the colour line after the observation gives (126,53,22) and (181,30,12); measured (126,53,22) and (181,31,12). Recorded as a dated revision; lesson: choose named pixels on the final drawn layer."
- **hint_range:** "2.0 from code: both pixels (255,0,0), so hint_range does not clamp."
- **Sweep:** "black tint or brightness 0 gives (22,22,22), not black (specular/ambient remain); brightness 2 raises the wall mean from 73 to ~100, not 146, because brightness multiplies linear colour and the output is sRGB-encoded ((73.4/255)^2.2 x 2 -> ~100.5); roughness 0 makes the wall darker; uv_scale changes brick size."
- **One shader, two materials:** "editing the shader's ALBEDO line (x 0.5) darkened both walls (73.4 -> 54.7, 49.9 -> 38.6); setting brightness on the damaged material only changed only CoverWall2 (49.9 -> 43.8)." I made the shader edit temporarily and restored the file.
- **OS screenshot vs engine capture:** "my first attempt captured the wrong window (850x287 terminal screenshot). The second (1920x1080, Win+PrtScn) showed all six bands at exactly the same values. I still trust the engine capture for measurement."
- **Cleanup:** "Godot generated .import files for the captures in docs/; I added docs/.gdignore and removed them." Not noticed at the time: Godot also imported the CSVs as translations. The 32 `.translation` files were removed in `1718cdd`, and `docs/.gdignore` now stops Godot importing `docs/`.
- **Learned:** the P1 lesson above. A value set from code is not limited by `hint_range`. Brightness in linear space does not double the displayed value.
- **Who:** Claude Code wrote the tools. I ran them, made the shader edit, read the turret texel with PIL (helper script by Claude chat), and wrote the revision.

## 2026-10-27 — Step 4: generated shader and LANGUAGE-NOTES

- **Trace:** commits `91e6751` (scratch scene, `shaders/standard_generated.gdshader`), `01dc14a` ([LANGUAGE-NOTES.md](LANGUAGE-NOTES.md)).
- **Tried:** "Converted a StandardMaterial3D (albedo, normal map, roughness) to ShaderMaterial in a scratch scene and saved shaders/standard_generated.gdshader."
- **Mistakes:** "I first saved the scratch scene into shaders/ by mistake and moved it to scenes/. The editor had re-saved brick_surface.gdshader (line endings only); I restored it."
- **LANGUAGE-NOTES:**
  - "I asked Claude to write the answers; it declined because the assignment requires my own words."
  - "My first Chinese draft was copied from Claude's explanation notes; Claude pointed that out."
  - "I rewrote each answer briefly in my own words in Chinese; Claude translated and checked line references, and pointed out one mistake in question 4 (I had the 64/137 sampler reversed), which I accepted."
- **Learned:** TBD (not in my notes).
- **Who:** me (conversion, answers); Claude chat (refusal, translation, line check, the question-4 correction).

## 2026-10-27 — playtest (me, in the editor)

> Got hit several times by enemy shells. Each hit flashed YunqiZ red and faded quickly; a second hit during the fade restarted it. Enemies hit by my shells did not flash red (only their existing white flash and the impact effect). After being destroyed and respawning there was no red left. I did not see the existing white flash on YunqiZ: the test shows modulate still reaches 2.2, but at the same moment the red is at its strongest. I tried to pause with Esc during the fade but could not press it within 0.5 s, so rule 5 rests on the headless test only.

## 2026-10-27 — documents (Claude Code session 6)

- **Trace:** [prompt-6.txt](docs/a5/sessions/prompt-6.txt), [session-6-excerpt.md](docs/a5/sessions/session-6-excerpt.md) (63 turns, success; the full 1.44 MB transcript is kept locally).
- **What happened:**
  - Claude Code reran all seven tests through the wrapper at `3d48047`: hit_flash 50/50 at 30/60/144, test_materials 76/76, check_tools_parse 9/9, check_a3_assets 18/18, test_sound_triggers 8/8, all exit 0.
  - It then wrote this section, the A5 parts of TEST-REPORT.md, SOURCES.md and README.md from my notes and the files, with TBD where they say nothing.
  - It changed no shader, game script, scene, material, test or `.import` file.
- **Noted:** Recorded, not investigated: the shutdown message grew from 5 resources / 18 ObjectDB instances to 7 / 22 between `9217896` and `97fdec6`. It is not a SHADER or SCRIPT ERROR and the 8/8 result is unchanged.
- **Not committed:** I review and commit.

## 2026-10-28 — Film

*Written on 2026-10-28, the same day, from the film's build log (`youtube/claude-liam-walker-tank-a5-shaders/BUILD-LOG.md`) and my notes.*

- **Tried:** an unattended Claude Code run in auto mode in `brutalist.art`. Prompt: [docs/a5/sessions/film-prompt-unattended.txt](docs/a5/sessions/film-prompt-unattended.txt).
- **Friction (from the build log):**
  - The review cut failed on a toolkit bug: its timecode `drawtext` passes an unescaped Windows font path, so ffmpeg could not parse the filter. It was retried with the toolkit's own switch (`ART_NO_DRAWTEXT=1`) and passed. The toolkit was not edited.
  - The type-lock gate (GATE T) misread the near-black wall in the "brightness 0.0" sweep crop as two overlapping text runs. The crop was swapped for `roughness_scale` 0.0, and the gate then passed.
  - ffmpeg peaked at 8.4 GB during the 4K encode, but the export finished.
  - The film is 3:05, against the ~2 minutes I asked for (cut once, from 723 to 521 words).
  - Left alone: the extra @NikBearBrown channel-title overlay the toolkit adds under the opening beat, and the toolkit files that already had uncommitted edits before this run (`GodotDesignFigure.tsx`, `package-lock.json`).
- **My play recording:** my first Game Bar recording had other things on screen, so I re-recorded 30 s of play.
- **Checked:** I watched the final film in full.
- **Skipped:** I skipped the human look checks and the "Learned" lines (see TEST-REPORT *Human items not done*).
- **Trace:** `youtube/claude-liam-walker-tank-a5-shaders/` (BUILD-PROMPT, BUILD-LOG, FACTCHECK, beat sheet, QC files).

## Who did what (A5)

- **Me:**
  - Made every decision in the brief, and computed the predictions by hand (except the worked example).
  - Typed all three hand-written shaders.
  - Wrote the Windows `run-test.sh` and the line-ending fix.
  - Chose P1/P2.
  - Reviewed and edited CLAUDE.md.
  - Ran the mutations.
  - Inspected cover_wall and revised the brief.
  - Set the import settings, generated and imported the hint PNG, and set Use External.
  - Found the Use External key mismatch.
  - Ran every capture tool windowed, and made the temporary shader edit.
  - Found and recorded the turret finding.
  - Did the Step 4 conversion.
  - Wrote the LANGUAGE-NOTES answers in my own words.
  - Playtested.
  - Reverted the editor re-saves.
- **Claude chat:**
  - Drafted the brief from my decisions; suggested the colour line, `flash_strength`, pure red and D = 0.5 s.
  - Checked my 12 predictions.
  - Gave the three shaders with explanations.
  - Wrote the helper bash/python scripts I ran.
  - Translated and checked LANGUAGE-NOTES, and refused to write the answers.
  - Organised my raw notes.
- **Claude Code:**
  - CLAUDE.md draft (session 1).
  - Driver and hit-flash test (2).
  - Materials, CoverWall2, hint scene, `make_hint_png.gd`, MATERIALS.md and test_materials (3).
  - The Use External check fix (4).
  - Capture tools and parse test (5).
  - These documents (6).
- **Accepted:** Claude chat's colour-line form, `flash_strength`, pure red, D = 0.5 s; the question-4 correction.
- **Rejected or changed:**
  - CLAUDE.md's cover_wall-only 3D limit (widened).
  - The brief's UV plan (revised to box projection).
  - test_materials' Use External key (fixed on my evidence).
  - My first copied LANGUAGE-NOTES draft (rewritten).
  - The hull prediction for P1 (revised to the turret layer, labelled as after the observation).

## Unresolved (A5)

- "The white _flash() is still in the code but visually masked by the red at the hit."
- "The pause rule has no human check."
- "reset_full() on a living tank would not clear the fade."
- "Normal-map curl check: not applicable, no game material uses a normal map (nor_gl is only in the Step 4 scratch material)."
- "Helper bash/python scripts I ran (setup, captures, commits) were written by Claude (chat)." They are not in the repo.
- test_sound_triggers' shutdown message: Recorded, not investigated: the shutdown message grew from 5 resources / 18 ObjectDB instances to 7 / 22 between `9217896` and `97fdec6`. It is not a SHADER or SCRIPT ERROR and the 8/8 result is unchanged.
- The look of the sweep extremes (wash-out, gloss, brick size) is described only from numbers except where my notes say; what breaks the look is not recorded.
- Test results after a fresh clone and import: TBD (clone verification).

Settled after session 6 (commit `1718cdd`):

- Mutation 3 was rerun after the Use External fix: exactly 1 FAIL, exit 1; restored, 76/76, exit 0. The first run, before the fix, had 2 FAILs.
- The 32 `.translation` files were removed. `docs/.gdignore` now stops Godot importing `docs/`.

---

# Assignment 3 — Blender MCP, three 3D assets

*Notes for the first session (night of 13–14 October) were written up on 15 October from my screenshots and terminal output of the session (retrospective, but every entry below is backed by a screenshot I kept).*

**Versions:** Windows 11 · Blender 5.2.2 LTS (installed at `D:\blender\blender.exe`) · MCP for Blender add-on 1.8, protocol 13 · uv 0.13.0 · Claude Code 2.1.292, auto-updated to 2.1.299 during the session · model Opus 5.5 · Godot 4.7.2.

## 1. Brief before building

- Claude proposed the three assets (cover_wall, ammo_crate, tank_hedgehog), the tank reference size and all numbers at my request; I accepted them after looking at Blender's window. I moved the Assignment 2 brief to `docs/a2/` with `git mv` and checked with `git diff HEAD:CHANGE-BRIEF.md docs/a2/CHANGE-BRIEF.md` (no output) that it was unchanged.
- Brief and interface notes committed before any building: **`e6f9f6f`**.

## 2. Getting the MCP connected (time box started about 22:00, 13 October)

What I expected: the chapter's commands would work after swapping macOS steps for Windows ones. What happened:

1. **uv.** The chapter uses `brew install uv` (macOS). I used uv's PowerShell installer instead; `uv --version` → `uv 0.13.0`. Worked first time.
2. **Registering the server failed as written.** `claude mcp add -e DISABLE_TELEMETRY=true blender -- uvx mcp-for-blender` gave *"Invalid environment variable format: blender"*: the `-e` option took the server name as another variable. Putting the name first worked: `claude mcp add blender -e DISABLE_TELEMETRY=true -- uvx mcp-for-blender`. `claude mcp list` then said *Connected*. I noted that this only proves Claude Code can start the server process, not that it reaches Blender.
3. **Add-on install.** `uvx mcp-for-blender install-addon` installed the add-on into Blender 5.2's add-on folder. Its message names the button "Connection to Blender"; the assignment lists three other names (Start MCP Server, Connect to Claude, Connect to MCP server). My panel showed *Connected on port 9876* with a *Disconnect* button.
4. **A telemetry slip.** When I ran `install-addon` a second time with Blender open, it did not exit: it started a server in that terminal, connected to Blender and queried telemetry consent — without `DISABLE_TELEMETRY` set, because that variable is only in Claude Code's server config. I stopped it with Ctrl+C. I cannot verify whether anything was sent in that window. Afterwards I called the server's own `disable_telemetry` tool; `get_addon_status` then returned `telemetry_consent: false`. The tool's own message says minimal anonymous usage counts (tool name, success, duration) are still collected.
5. **Tools.** `/mcp` listed 9 tools, matching the 2.1.9 names in the assignment. Four of them can fetch outside content or send data out (generate_3d, search_assets, import_asset, record_trajectory_feedback), so I denied them in `.claude/settings.json` instead of relying only on the prompt. All library and generator checkboxes in the Blender panel stayed off (screenshot).
6. **Login.** Claude Code auto-updated from 2.1.292 to 2.1.299 on restart, and my first prompt failed with *"Login expired"*. `/login` fixed it.
7. **Permissions.** Claude Code was in auto mode, which would run tools without asking. Because `execute_blender_code` runs any Python inside Blender, I switched to manual mode and approved each call after reading it. I allowed `look` without asking (read-only screenshot); this created `.claude/settings.local.json`, which I keep out of Git.
8. **First real check.** `get_scene_info` returned the default scene (Cube 2 × 2 × 2 m at the origin, Light, Camera, Object Mode). This was the first proof that Claude was reading my actual Blender session.

Time box result: the add-on server log shows Blender connected at 22:48; Claude Code's first successful `get_scene_info` on my scene was at about 00:01. That is about two hours from my start, of which I estimate about 100 minutes was MCP work; the rest was the Claude Code auto-update and expired login (step 6), which is not an MCP problem. Because the MCP route was working, I did not use the script route.

**Something I noticed:** every tool call carries a `user_prompt` field with my prompt text, so the MCP server sees what I write to Claude, not only the Blender scene.

## 3. cover_wall

- Claude read the brief and pointed out that it did not give the two top blocks' sizes; it proposed them and asked. It also asked whether to keep three objects or join them. I accepted its sizes and chose to join, because separate top blocks would have their origins at Z = 1.5, not on the floor. I told it to save the live `.blend` but not to save from the script.
- **Reading the code against the description:** for top block B, the comment said *0.1 m in from the front face*; the code centred it in Y (−0.4 to 0.4), so it is 0.1 m in from *both* faces. Harmless (overall size unchanged), so I left it, but it showed me the description and the code can differ.
- **A failure:** the join step worked, then raised `AttributeError: 'NoneType' object has no attribute 'select_set'` because the view layer still listed the deleted part objects. Claude refreshed the view layer and re-ran apply-and-check as a separate call, which passed. The build script keeps the join (6a) and the corrected second half (6b), not the failed version, and its header comment says so.
- **Result in Blender:** 4.0 × 1.0 × 1.8 m, lowest Z 0.0, origin at the underside centre, scale 1, 1, 1, 36 triangles (budget 60), 0 non-manifold edges, two material slots, no modifiers.
- **Background rebuild:** Claude could not find Blender at the default `C:\Program Files` path; it read `bpy.app.binary_path` from my session (`D:\blender\blender.exe`). Then `blender.exe -b --factory-startup --python-exit-code 1 --python tools/blender/build_cover_wall.py` printed the same numbers, *cover_wall checks passed*, **exit code 0**. It also printed a DeprecationWarning: `Material.use_nodes` will be removed in Blender 6.0.
- What its check does not cover: it checks material slot names, not colour values, and it says nothing about how the asset looks after export to Godot.
- Committed: **`7d8fbf0`**.

## 4. ammo_crate (15 October; sections 4–7 written the same day)

- Before building I noticed the brief's size left out the lid: the lid overhangs 0.02 m on each side and the stripe adds 0.01 m, so the real box is 1.24 × 0.84 × 0.71 m, not 1.2 × 0.8 × 0.7. Inside the ±0.1 m tolerance, so I told Claude to check against both.
- I also told Claude about cover_wall's `select_set` error. Its plan joined and baked transforms with bmesh and no operators at all, so that error could not recur.
- Claude pointed out, unasked, that a stripe as deep as the lid (0.84 m) would share the lid's front and back faces and might flicker (z-fighting). **I accepted its suggestion** to make the stripe 0.83 m.
- **It worked first time:** every step succeeded on the first call. I checked it by the background rebuild (`checks passed`, exit 0, 36 triangles, +0.04 / +0.04 / +0.01 m from the brief, within tolerance) and by looking at it in Blender.

## 5. tank_hedgehog

- I asked Claude to calculate the bounding box *before* building and to stop if it was outside the brief's tolerance. It computed with NumPy, before building anything, that 2.4 m beams would give 2.011 × 2.011 × **1.559** m: 0.009 m over the height tolerance, because the brief's numbers used beam centrelines and ignored the 0.15 m section. It stopped and offered three options. (The 1.559 m figure is a calculation, never built; only the final 2.125 m version was measured in Blender.)
- **I rejected Claude's recommendation** (turn each beam 45° on its own axis, 1.508 m high) and chose to shorten the beams to 2.125 m (exactly 1.400 m high). My reason: the overall size is what my game design depends on (lower than the 1.6 m hull, a barrier at hull scale); the beam length was a construction detail and was the wrong number. Claude added a dated entry under *Revisions* in the brief; I checked that it only appended and did not change the original text.
- Result: 1.794 × 1.794 × 1.400 m, exactly 3 vertices at Z = 0 (checked by the script), 36 triangles, background rebuild exit 0.
- Claude flagged afterwards that the "apply rotation" step had nothing to do, because the rotation was already baked during the join (`identity: True`). So that step never tested a real rotation; the result is still correct.
- Commits: ammo_crate `3b73208`, tank_hedgehog and the brief revision `90f403b`.

## 6. My hand edit

- **What and why:** on cover_wall, I selected the lower top block (block B) in Edit Mode with L and moved it +0.6 m along X (G X 0.6), so it is flush with the right end. From the game's top-down camera, two broken stubs with a gap in the middle read more like a shell-damaged wall than one block in the middle.
- **What it taught me:** moving part of a joined mesh in Edit Mode changes only the vertices; the object's location, rotation and scale stayed 0 / 0 / 1, so the origin stayed on the floor and nothing needed re-applying. In the front view the block looked as if it stuck out past the wall; my sidebar said 4 m, so I trusted the number over my eye.
- **But the sidebar was not precise enough.** Claude's read-only background inspection of the saved file showed block B had moved 0.5993 m, 0.7 mm short; the sidebar rounds to display precision, so it could not show this. I corrected by hand (G X 0.0007), computed from a 4-decimal printout that was itself rounded, so it then overshot by 0.032 mm. That is inside the build check's 0.1 mm tolerance and far below anything visible, so I stopped. Next time I would type the target coordinate into the sidebar instead of nudging with G.
- Claude added the edit to `build_cover_wall.py` as a separate, clearly labelled step 7, so the script rebuilds the final asset. Commit `4846465`.
- **Two process slips here.** (1) While doing this I found Claude Code had switched back to **auto mode**: the script append and a background run were "Allowed by auto mode classifier" without my approval. Nothing harmful ran, but I only noticed afterwards; I switched back to manual mode. (2) Claude then wanted to run a temporary inspection script I could not see. I refused, asked to see its full contents, checked it had no save or export calls, and only then approved it.

## 7. Export and Godot

- Claude checked the glTF exporter's option names in Blender 5.2 before exporting, then wrote `tools/blender/export_glb.py` (GLB, +Y Up, materials on, no cameras, lights or animation) and ran it in background Blender for each `.blend`. Godot's `--import` exited 0 and did not change any A2 `.import` file.
- Claude converted my brief's sizes from Blender Z-up to Godot Y-up for the check (for example the crate is 1.24 × 0.71 × 0.84 in Godot).
- `tests/check_a3_assets.gd`: **18 / 18 PASS, exit 0**. Windows has no macOS `timeout`; Claude used Git Bash's GNU `timeout` (coreutils 8.32), because Windows' `timeout.exe` only waits.
- **I asked for the FAIL path to be proved**, since a check that has never failed may be broken. A scratch copy with ammo_crate's expected height changed to 0.81 printed 2 FAILs and exited with code 1. Commit `ee1c67a`.
- **My own look in the Godot editor:** top, rear and bottom views of each asset. The crate's stripe is the most readable feature from above; the hedgehog reads as crossing beams; every shadow meets its asset's base; I saw no missing faces or wrong colours. Unresolved: with one light and no ambient fill, faces away from the light are very dark.
- For merging these documents I switched Claude Code to accept-edits mode (file edits auto-approved, commands still asked) and checked the result afterwards with git diff instead: only added lines, and A2 text unchanged except the one TEST-REPORT link in README's A2 section, which I changed on purpose because the A2 report moved to docs/a2/.

## 8. The film (15 October)

- **Wanted:** one short 4K landscape explainer with Brutalist's `godot-gamedev` skill in `walker` mode, showing source revision `9baa12c`.
- **Before:** in walker-TANK, `git status` was clean and HEAD was `9baa12c` (screenshot kept). I closed Blender, Godot and the browser to leave memory for the render, because memory ran out three times in the A2 film.
- **Asked:** Claude Code in `D:\CSYE7270\brutalist.art` (toolkit commit `22264a3`), started with `PYTHONUTF8=1` set, to read the skill and make the film, with the assignment's film requirements, my screenshots in `a3-evidence/` (outside the repo) as labelled stills, and firm limits (below).
- **Auto mode, on purpose this time.** In the Blender work I rejected auto mode, because `execute_blender_code` can run any Python on my computer and I wanted to read each call. For the film I chose auto mode: the Blender MCP is not connected in `brutalist.art`, the work is long and mostly rendering, and I could not approve every step in the time left. To keep it safe I gave it written limits instead of per-step approval: no state-changing git command in walker-TANK, no push or publishing, stop before any toolkit edit, stop before the final render. I checked the outcome with `git status` afterwards rather than step by step.
- **How it kept the game source fixed:** I asked it (with `/btw`, without interrupting) where its "isolated copy at 9baa12c" was. It had exported the tracked files of `9baa12c` with `git archive 9baa12c | tar -x` into its own temp scratchpad, so the copy had no `.git`, no untracked files and no link to my repo. In that copy only, it re-ran the import and the headless check (**18 / 18 PASS, exit 0**, before any edit), then added a 3840 × 2160 window override and an MJPEG quality setting to the copy's `project.godot` so Godot's Movie Maker would record the running `asset_room_3d.tscn` at 4K. Both versions of that `project.godot` are kept in the film records' `capture/`. The camera is static, so the "running scene" footage shows no motion. It did not re-run the FAIL path; the film cites my recorded run.
- **Got / friction** (from its BUILD-LOG and my terminal):
  - The A2 workarounds were needed again: `PYTHONUTF8=1` and a `python3` shim pointing at Python 3.12.1. The toolkit's own `./art doctor` aborted on a lint of the toolkit's example reels, so it checked the runtime by hand.
  - Small build errors it fixed itself: a one-beat-only render option, a missing bold font, a first Godot capture shorter than its narration (re-recorded at 540 frames), and Whisper writing numbers as digits.
  - **It corrected its own script against my log:** a draft line said I "approved each call", but FRICTIONAL says a few calls ran in auto mode before I noticed; it changed the line and regenerated that audio.
  - My screenshots do not show the text of my prompt, only Claude's plan and report, so the film says "one request" and shows those rather than inventing the prompt wording.
  - **Final export attempt 1 (4 min 47 s) was refused by the toolkit's quality gate**, not killed: the full-frame Godot footage beat was flagged by checks meant for flat cards. Free memory fell to 51 MB during it, but there was no crash this time. Claude marked that beat as full-frame footage with two labelled contrast regions and a written reason; no media changed. Attempt 2 passed (0 blockers, 0 major).
  - The film is 3:39, over the 2–3 minutes I asked for, after one round of cutting.
  - **It did not follow one limit exactly:** I named a new film folder inside `walker-TANK/youtube/`, but it built the film in a sibling folder outside the repo, `D:\CSYE7270\assignment2\walker-TANK-a3-film\`. Its log says this was my request (an earlier draft of my prompt asked for the MP4 outside the repo). The effect was safer, not worse: nothing in my repo changed. I then copied the records into the repo myself with `tar`, excluding every MP4, AVI, WAV and MP3 and the `clips/`, `media/` and `mp3/` folders (28 MB, no file over 25 MB), and added an empty `.gdignore` so Godot does not import them. My A2 `.gitignore` rule `youtube/**/*.png` keeps film images out of Git, so I force-added only the seven `evidence/` stills the film shows; the QC frame grabs stay local, and their written reports (`_qc/REPORT.md`, `_qc/GATE-V-attempt1.md`) are committed.
  - Toolkit: `git -C brutalist.art status` shows two modified files, but both are older than tonight: `GodotDesignFigure.tsx` (last changed 2026-10-07 11:01, the footer edit I approved for the A2 film) and `package-lock.json` (2026-09-22, from the toolkit's npm install). No toolkit file was changed for this film, and nothing was pushed to the toolkit.
- **After:** `git status --short` in walker-TANK printed nothing before I copied the records, and only `?? youtube/claude-liam-walker-tank-a3-assets/` after; walker-TANK stayed at `9baa12c` throughout.
- **Got:** `claude-liam-walker-tank-a3-assets.mp4`, 3:39 (218.57 s), 3840 × 2160 H.264 30 fps with AAC audio, 16 MB, SHA-256 `b91f985d83d7ffed36f941aef078ee3efa676d958c6f58b1ad84931d95c98d8c` (my own `sha256sum` matches the toolkit's `.verified.json` receipt). Uploaded to Google Drive and linked in README. The MP4 and the raw capture are not in Git.
- **Known flaw left in:** in the last second of the toolkit's locked outro, the mascot's jump briefly overlaps the @NikBearBrown handle. It is a locked toolkit component, so I left it.
- **Human / Claude / model:** Claude Code built the film end to end (capture, beat sheet, script, Kokoro `am_onyx` narration, Remotion render). I wrote the requirements and limits, chose auto mode and the checks around it, supplied my own screenshots, copied the records into the repo, and watched and listened to the whole final film myself before accepting it: the sound and the picture are clear and I found no problems. I also opened the Drive link to check that it can be viewed.
- **Trace:** `youtube/claude-liam-walker-tank-a3-assets/` (BUILD-PROMPT, BUILD-LOG, beat sheet, FACTCHECK, SOURCES, capture logs, evidence and QC files).

## Who did what

- **Claude:** proposed the assets and numbers, wrote all the Blender code and the build scripts, ran the checks, and drafted these notes from my screenshots. Claude Code with Brutalist made the film.
- **Me:** accepted the assets, made the join and save decisions, chose 2.125 m beams over Claude's recommendation, made the hand edit and its correction, switched to manual mode and read each code call before approving (and refused an unseen script until I had read it), added the deny rules, caught the telemetry issue, asked for the FAIL path to be proved, kept `.blend1` and `settings.local.json` out of Git, looked at each asset in Blender and Godot myself, and watched the final film.
- **Accepted:** the stripe made 0.83 m to avoid z-fighting; the operator-free join.
- **Rejected or changed:** the chapter's `claude mcp add` command order (changed); auto mode for the Blender work (rejected; I chose it later for the film only, with written limits and a `git status` check, see section 8); letting the script save the `.blend` (rejected); Claude's 45° beam option for the hedgehog (rejected, with my reason).

## Unresolved

- Whether anything was sent during the unguarded `install-addon` server run.
- What "minimal anonymous usage counts" includes in practice.
- How the colours look under the game's real lighting (only one light here).
- Why the hand edit moved 0.5993 m when I typed 0.6.

---

# FRICTIONAL — walker-TANK

How the design went, in order. **Retrospective note:** this log was put together on 2026-10-05 from my chat with Claude, the settings ComfyUI saved inside each output file, my screenshots and the commits. Claude organized it; the decisions and the reasons quoted are mine from that chat. Asset-log rows are in [ASSET-LOG.md](ASSET-LOG.md).

**Who is who:** *Me* = what I chose, ran, judged or changed. *Claude* = the AI assistant (plans, prompts, code, scripts, guide images, drafts). *Model* = the generative model that made the asset (SDXL Base 1.0, Stable Audio 3 Small).

---

## 2026-10-02 — choosing the game

- **Wanted:** a game I could keep building this semester.
- **Asked:** Claude to compare two ideas I had, a tank battle and a farm fruit-picking game, against the assignment rules.
- **Got:** Claude said the tank game had natural sound events and was easier to keep consistent, but hard to get 10 poses from a vehicle; the farm game had easy poses but no built-in way to fail.
- **Decided:** tank battle. Then I chose: clear all enemy tanks, oblique top-down view, realistic metal look, cover that breaks, a health bar, about 5 minutes per level, all four suggested pillars, one music loop that stops on pause, failure and the end.
- **Human / Claude / model:** I made each choice from options Claude listed. Claude wrote CONCEPT.md from my answers.
- **Trace:** CONCEPT.md; first design commit.

## 2026-10-02 — silhouette test changes the tank

- **Wanted:** the player to see which way the tank faces at game size.
- **Got:** Claude drew a box-model tank in 5 directions. At 64 px, **up and down looked the same**; only the barrel was different.
- **Decided:** I added a **front dozer blade** and a **rear storage box** to the design. The redrawn silhouette shows a wide bar at the front.
- **Human / Claude / model:** I chose the blade and the box. Claude drew the sketches with code (not a generative model).
- **Trace:** CHARACTER-SHEET.md (silhouette section); `design/character/silhouette.png`.

## 2026-10-02 — hull, first try: flat blocks

- **Wanted:** a realistic worn steel hull that keeps the same shape in all 5 directions.
- **Asked:** SDXL Base 1.0 img2img on Claude's box guide (v1), seed 846322750311363, 25 steps, cfg 7.0, prompt "realistic military tank hull without turret, …".
- **Got:** at denoise **0.55** and **0.70**, almost the same flat color blocks as the guide. At **0.80** some panel lines appeared, but **the dozer blade disappeared**.
- **Decided:** rejected all three. The problem was the guide, not the denoise: flat colors with black outlines read as a flat drawing.
- **Next:** Claude redrew the guide (v2) with shading, grain, road wheels and panel lines.
- **Human / Claude / model:** I ran the tests and changed only the denoise each time, so the results could be compared. Claude found the cause and made v2.
- **Trace:** ASSET-LOG G-01 to G-03; thumbnails REJ-01 to REJ-03.

## 2026-10-02 — hull, second try: it works

- **Asked:** same seed and prompt, v2 guide, denoise 0.55 and 0.65.
- **Got:** 0.55 gave worn olive paint, rust, wheels and a segmented blade, **with the shape kept**. 0.65 looked richer but **added a turret dome on the hull**.
- **Decided:** accepted 0.55 for all 5 directions; rejected 0.65 because the turret is a separate sprite, so the tank would have two turrets.
- **Got (5 directions):** all outlines matched the guides (IoU 0.99). The down hull was brighter and the down-right hull less worn.
- **Human / Claude / model:** I ran all 5 and uploaded them. Claude checked them, cut out the backgrounds and drafted the log; I reviewed it.
- **Mistake caught:** Claude's first cutout script dropped the dozer blade on the right hull (it is a separate piece). Found on the check sheet and fixed.
- **Trace:** ASSET-LOG G-04 to G-10; `design/asset-log/check_hull_v2.png`.

## 2026-10-02 — turret: square barrel vs round barrel

- **Got:** with the v2 guide, the right turret had a **square** barrel and the down-right one a **round** barrel.
- **Decided:** I asked to fix this **before** running the other directions. Claude suggested the round barrel (like the down-right one) and I agreed. Claude drew a v3 guide with a round barrel and muzzle.
- **Also:** twice I loaded one guide and saved under another direction's name, so I had to rename files.
- **Trace:** ASSET-LOG T-01, T-02; REJ-05, REJ-06.

## 2026-10-02 — turret denoise: 0.55, 0.60 or 0.75

- **Got:** 0.55 nearly lost the hatch. 0.60 gave a raised domed cupola. 0.75 gave a round turret with a gun mantle and muzzle brake.
- **Decided:** I said "0.60 looks better than 0.55", then "0.75 is even better". Claude pointed out that 0.75 **lost the white stripe**, changed the turret shape and the barrel color. I chose **0.60**.
- **Human / Claude / model:** the first preference (0.75) was mine; Claude raised the problems; the final choice (0.60) was mine.
- **Trace:** ASSET-LOG T-03 to T-05; REJ-07, REJ-08.

## 2026-10-02 to 2026-10-04 — the cupola only appeared on some turrets

- **Got:** at 0.60, the diagonal turrets had a cupola but up, right and down had flat tops. The down turret also lost the stripe and had a clamp on the barrel.
- **Decided:** I chose to **re-run up, right and down until they had a cupola**. Claude made a v3.1 guide with a bigger cupola and a stronger prompt. The stripe would be painted on every turret afterwards so it is the same everywhere.
- **Got:** down was still flat with the same seed. With random seeds one had a cupola but a light barrel. The one I finally kept was made with denoise 0.55 on the v3.1 guide, seed 499619143762383 (these settings are read from the file itself): cupola, dark barrel, no clamp.
- **Decided:** after that I said "never mind, I don't want to keep changing it". Up and right stay flat. At game size the difference is 1–2 px.
- **Still unresolved:** no cupola on up and right; the down turret uses a different denoise and seed.
- **Trace:** ASSET-LOG T-06 to T-12; REJ-09 to REJ-11; `design/asset-log/check_final_8dir.png`.

## 2026-10-04 — stripe and color fixes (edits)

- **Edits:** Claude's script painted the white stripe where the guide puts it on all 5 turrets, and matched the olive of all 10 sprites to the sheet color `#4B5320`.
- **Trace:** ASSET-LOG Edits; `design/asset-log/check_stripe_before_after.png`.

## 2026-10-05 — cannon sound: the template's settings were wrong

- **Wanted:** a deep, heavy cannon shot (pillar: every shot has weight).
- **Asked:** Stable Audio 3 Small-SFX, prompt "single heavy tank cannon shot, deep low boom with a sharp crack, …".
- **Got:** seven noisy bursts in 2 seconds, clipping, no decay. Claude read the settings saved in the FLAC file: 50 steps and cfg 7.0, which the template sets for the bigger Medium model.
- **Next:** I changed the sampler to 8 steps / cfg 1.0. The new shot was one clean low boom that fades out.
- **Trace:** ASSET-LOG A-01, A-02; `design/asset-log/audio/SFX-fire_waveforms.png`.

## 2026-10-05 — other sounds and music

- **Got:** cover hit, YunqiZ hit, victory and the music loop were usable on the first try. Claude checked each one's length, frequency spread and clipping. The music came out at exactly 70 BPM; Claude cut an 8-bar loop and I played the game with it.
- **Decided:** Claude warned that the cannon and the explosion are both almost all low frequency, so they sound alike and may be quiet on laptop speakers. I said "leave it, I'm short on time."
- **Still unresolved:** the cannon and explosion sounds.
- **Trace:** ASSET-LOG A-03 to A-07.

## 2026-10-05 — ground and cover

- **Got:** the three cover stages kept their shapes (IoU 0.96–0.997). The ground came out as bright cobblestones, not mud.
- **Decided:** in a game-size test the cover almost disappeared into the ground. The ground was edited (darker, softer, less contrast) instead of regenerated, to save time.
- **Trace:** ASSET-LOG E-01 to E-04; `design/asset-log/env/check_scene_v1.png` → `check_scene_v2.png`.

## 2026-10-05 — building and playing the slice

- **Human / Claude:** Claude wrote all the Godot code and the automated test. I set up the project, fixed the folder mix-up, reported errors, and played it.
- **Got:** one parse error in `enemy.gd` (fixed). The automated test passes 8/8.
- **My playtest:** no sound or music problems with sound on; readable with sound off. From my screenshots the health bar was hard to see, so it was changed to green / yellow / red.
- **Still unresolved (my notes):** the turret could turn faster, the hull turning could look smoother, and the enemy tanks should look different from YunqiZ.
- **Trace:** TEST-REPORT.md; `design/test/`.

## 2026-10-05 to 2026-10-07 — making the explainer film

- **Wanted:** the 4K explainer film with Brutalist's `godot-gamedev` skill in `walker` mode.
- **Asked:** Claude Code (in `brutalist.art`) to read the skill and build the film from my project, with a list of what the assignment requires. It checks the runtime, reads the code and documents, records real gameplay by driving the game itself, writes and voices the narration (local Kokoro), renders and exports.
- **Got / friction:**
  - My laptop battery was about to run out during the first gameplay recording. I had it stop the recording safely; the partial take could not be resumed (enemies move randomly), so it was recorded again from the start after I plugged in.
  - The render and the final export were stopped three times because the computer ran low on memory. I closed other programs; the last time, a leftover 8 GB `ffmpeg` from the killed export was still running, and Claude Code confirmed it was orphaned before re-running the export in the foreground.
  - The toolkit's quality check failed on 13 beats because the `@NikBearBrown` footer in one shared toolkit template (`GodotDesignFigure.tsx`) sat 3 px below the title-safe line at 4K.
- **Decided:** I allowed a local, uncommitted edit to that toolkit template (two numbers, matching its sibling template that already passed) and a re-render of the 13 beats, instead of rebuilding them on another layout (about 1.5 h more). My game was not changed and nothing was pushed to the toolkit.
- **Got:** a 4K film. Its own QC also pointed out that my committed ASSET-LOG was out of date (missing the environment rows), the HUD text has low contrast, and the mute and restart keys are not shown. I updated the documents afterwards; the film shows the commit it was built from.
- **Human / Claude / model:** Claude Code built the film end to end. I supplied the project and the requirements, made the battery, memory and toolkit decisions above, and watched and listened to the final film myself before accepting it. I watched and listened to the whole film and found no problems.
- **Trace:** `youtube/claude-liam-walker-tank-gamedev/` (BUILD-PROMPT, beat sheet, evidence, QC files).
