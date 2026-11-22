# BUILD-LOG — claude-liam-walker-tank-a7-animation

## RESULT (unattended run, 2026-11-21)

- **Final MP4:** `D:/CSYE7270/assignment2/walker-TANK/youtube/claude-liam-walker-tank-a7-animation/exports/landscape/claude-liam-walker-tank-a7-animation.mp4`
- **Duration:** 230.87 s (3:51) · 3840×2160 H.264, 30 fps (6926 frames) + AAC 48 kHz · 40,340,374 bytes
- **SHA-256:** `11ec29ec023f1a55cd9971c324626f799d5395058627cfe2d8bac223bdaa026a` (matches `exports/landscape/claude-liam-walker-tank-a7-animation.verified.json`, status `ready`)
- **Title:** "Walker-TANK: Animation in Frames and Ticks"
- **Revision shown:** walker-TANK **4f88f1b** (B00 result line, every code/figure footer, every capture page, the verdict heading). Repo HEAD 4f88f1b; the only untracked/modified items in walker-TANK are the student's own (`captures/shoot*/`) plus this film folder.

## Revision change mid-run (the student's instruction)
The run started at **392d1c4** as the film prompt said. The student stopped it: 392d1c4 lacks the committed dust fix (DUST_BEHIND 14 hides the dust under the hull). Switched to **4f88f1b** for every capture and on screen. Redone: both scratch copies were rebuilt from `git archive 4f88f1b`. Only one capture had been attempted at 392d1c4 — a pilot whose film driver failed to parse, so it recorded the bare game; it was discarded before any use (log kept at `_qc/discarded-392d1c4/hits.log`; one orphaned Godot process from it was killed). Content updates applied: dust-in-8-facings removed from "uncertain" (now stated as checked, B14); `tests/test_anim_edges.gd` added (B12: 27 checks at 30/60/144); new uncertain items and next step on the verdict (B15).

## Quality-check results
| Check | Result |
|---|---|
| `./art godot-gamedev --check` before render | PASS — 63 source files, 603 exclusions, 7 components, 4 exact excerpts, 4 code→result pairs (`_qc/check-prerender.json`) |
| `./art godot-gamedev --check` at handoff (ledger refreshed) | PASS, same counts (`_qc/check-handoff.json`) |
| Review cut `./art run --height 1080`, attempt 1 | Gate V **FAIL**: 4 BLOCKER `edge-bleed` (B10 long label, B11 third panel past title-safe right edge) — `_qc/REPORT-attempt1.md`. Fixed in my compositor (shorter label, narrower panels) |
| Review cut, attempt 2 and 3 | Gate V 36 frames, 0 BLOCKER / 0 MAJOR (`_qc/REPORT.md`); 18/18 slots |
| GATE T, final attempt 1 | **FAIL**: B02, B06, B08 bottom-strip lines > 12 words (`_qc/TYPECHECK-attempt1.md`) |
| GATE T, final attempt 2 | **FAIL**: B08 strip flagged "ends truncated" (`_qc/TYPECHECK-attempt2.md`); reworded, then 13 words; reworded again |
| GATE T, attempt 3 | PASS (`TYPECHECK.md`) |
| Final export `./art final --height 2160 --fps 30` attempt 3 | EXPORT_EXIT=0, 22:30:34 → 22:36:55 (6 min 21 s), foreground |
| Full decode (`ffmpeg -f null`) | no errors |
| Sound | mean −27.6 dB, max −4.4 dB; silences > 1.5 s only the B00→B01 lead (1.9 s) and the outro's silent tail (1.6 s) |
| Visual inspection | 15–97 % frames of every beat during the build (`_qc/*-r.png`, `_qc/media-sheet.png`, `_qc/code-pilot*.png`) and one frame per beat of the master (`_qc/final-sheet.png`): code readable, every capture labelled SCRIPTED INPUT, held frames/half speed/loops labelled, FIXTURE strips labelled, readout labelled "reads only", outro locked |
| Memory | `_qc/memory-monitor.log`: no leftover ffmpeg before; during the 4K encode ffmpeg peaked at 8.2 GB and free RAM touched **16 MB** for a few seconds (22:34:04) but the export finished; no ffmpeg/Godot/node left afterwards |
| Voice | Kokoro `am_onyx`, local, $0.00 |

## Decisions made without you
1. **Captures are scripted play, not fixtures.** New film driver `_film/a7_play.gd` (capture copy only) instances the real `scenes/main.tscn` and presses the game's own actions. Every capture page says SCRIPTED INPUT. Hits and deaths are scripted `take_damage()` calls on stated ticks (as your test does) and are labelled so. Enemies are held (`target = null`) as in your pins/preview.
2. **Runtime readout.** The driver draws a dark panel with motion/weapon state, `Dust.frame`, ticks since press, FireAnim position, `Suspension.y`, shells, health, and an event log. It reads state and writes none; it is labelled "film driver, reads only". It is what makes "dust plays/stops" and "shot continues" checkable on screen.
3. **Held frames.** B09 holds each of frames 84–91 for 1.6 s; B10 holds each frame 5×; B11 4×; B07 plays at half speed (each frame 2×). All labelled. Frames always in order.
4. **B09 uses the uninterrupted shot** from the drive capture (N = frame 85), not shot 1 of the hits capture (which carries a hit flash).
5. **The 1-tick gap is not visible in a 30 fps capture** (P+2 and P+3 are the same frame N+1). The film shows C1's measured numbers beside the held frames and says "measured by check C1".
6. **Second fire (B10):** in play the reload also blocks the press; the page says the FIRING guard alone is isolated only by test G1.
7. **Excerpts ≤ 15 lines** (the workbench shows 15 and does not scroll): motion_clips.tres 3–17, bake_tank_clips.gd 60–73 (the scale track lines 74–79 are named in the notes), tank.gd 88–101 (line 96 wraps; line 102 is named in the cue label), tank.gd 207–219.
8. **"Claude measured the squash at about 5 %"** is not in the repo; it is shown as "the student's account; not in the repo" (B14 figure, FACTCHECK).
9. **TEST-REPORT.md has no A7 section** at 4f88f1b; test numbers come from `logs/` and commit messages, and B12 says so.
10. **Length 3:51** (685 words), within "about 3–4 minutes". One trim pass (B12, B13, B15).
11. **18 beats** for your 7 sections: §1 B00–B05, §2 B02/B06/B08/B05, §3 B03, §4 B05, §5 B07/B10/B11, §6 B12–B13, §7 B14–B15; Your Turn B16; outro B17.
12. **Helpers copied** from the A6 reel (`pad_audio.py`, `bind_cues.py`, `remotion_win.py`); `make_sheet.py`, `make_evidence.py`, `make_media.py`, `build_evidence.py` adapted. `ART_NO_DRAWTEXT=1` for `./art run`/`final` (the toolkit's own switch; Windows drawtext font-path bug from the A5 log).

## Failures and fixes (in order)
- First pilot (at 392d1c4) never ran the driver: GDScript could not infer types from a dictionary lookup (`var t := {…}[mode]`). Fixed with explicit types; that capture was discarded anyway (revision change).
- My first compositor crops used coordinates read off a down-scaled contact sheet (3× off): B03 showed only ground. Re-measured on 4K frames and fixed.
- Lato Bold has no "→" glyph (rendered as a box in B10 labels): replaced with ":".
- Workbench clipped code beyond 15 lines and B02 at font 28 showed 12 lines: ranges narrowed and B02 font 22.
- Whisper heard "cut out", "start up", "motion anem": cue phrases changed to words it hears.
- Verdict card overlapped the @NikBearBrown label: lines shortened.
- Gate V and GATE T failures: see the table.

## Observed, not changed (shared toolkit)
- `runtime/remotion/src/scenes/GodotDesignFigure.tsx` and `package-lock.json` had uncommitted edits before this run; rendered as they are, not touched.
- `remotion_scenes.py` exits 2 after some successful renders even when it prints "ok"; each clip was checked by probing and looking at frames.
- `./art run`/`final` regenerate `STATUS.md`, `ToDo.md`, `todo.json`; kept as generated.
- Comment drift in your repo (not shown): `tools/make_dust_sheet.gd` line 11 still says "muddy brown" beside the pale-sand colour.

## Scope kept
- **No toolkit file edited.** Writes in brutalist.art: only the renderer's own git-ignored usage ledger.
- In walker-TANK: wrote only inside this new film folder. Git commands run there: `archive` (392d1c4, then 4f88f1b) and read-only `log`/`diff`/`show`/`status`/`cat-file`. No add/commit/push/checkout/reset/stash. No Godot run touched the repo; captures used `_scratch/cap`.
- No paid call, no generated media, no upload, nothing pushed or published.
- Disk: `capture/godot/` holds 1.9 GB of 4K PNG frames (evidence; deletable once you accept the film); `_scratch/` 316 MB.

## Runtime
Windows 11 (Chinese locale), Git Bash, `PYTHONUTF8=1`, Python 3.12, ffmpeg, Node (Remotion), Godot 4.7.2 console build on the RTX 3060 Laptop (Vulkan Forward+), Kokoro `am_onyx`, faster-whisper `base.en` (local).
