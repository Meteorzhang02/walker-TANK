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

## Who did what

- **Claude:** proposed the assets and numbers, wrote all the Blender code and the build scripts, ran the checks, and drafted these notes from my screenshots.
- **Me:** accepted the assets, made the join and save decisions, chose 2.125 m beams over Claude's recommendation, made the hand edit and its correction, switched to manual mode and read each code call before approving (and refused an unseen script until I had read it), added the deny rules, caught the telemetry issue, asked for the FAIL path to be proved, kept `.blend1` and `settings.local.json` out of Git, and looked at each asset in Blender and Godot myself.
- **Accepted:** the stripe made 0.83 m to avoid z-fighting; the operator-free join.
- **Rejected or changed:** the chapter's `claude mcp add` command order (changed); auto mode (rejected); letting the script save the `.blend` (rejected); Claude's 45° beam option for the hedgehog (rejected, with my reason).

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
