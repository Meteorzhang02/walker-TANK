# BUILD-LOG — claude-liam-walker-tank-a6-particles

## RESULT (unattended run, 2026-11-06/07)

- **Final MP4:** `D:/CSYE7270/assignment2/claude-liam-walker-tank-a6-particles/exports/landscape/claude-liam-walker-tank-a6-particles.mp4`
- **Length:** 210.33 s (3:30) · 3840×2160 H.264, 30 fps (6309 frames) + AAC 48 kHz · 43,473,424 bytes
- **SHA-256:** `42e9e9074983ac15453db15f2a8d15047bc123ff0d8e859f3c1aad371a2670d4` (matches `exports/landscape/claude-liam-walker-tank-a6-particles.verified.json`, status `ready`)
- **Title:** "Walker-TANK: Particles, Strips and the Game"
- **Revision shown:** repo `41a6b8b`, game source last changed at `96d38be`. walker-TANK's HEAD was `2bc81f5` (the film prompt), working tree clean before and after.

Quality-check results: see STATUS.md.

## Decisions made without you

1. **Film folder:** `D:/CSYE7270/assignment2/claude-liam-walker-tank-a6-particles/`, a sibling of walker-TANK. The skill's default (`<game>/youtube/…`) would have written into walker-TANK, which your limits forbid; the toolkit folder is ruled out by its CLAUDE.md (rule 3).
2. **Scratch copies inside the film folder** (`_scratch/`): your limits allow writes only in brutalist.art and the film folder, so "outside the repo" = here. Two extractions of `git archive 41a6b8b`: `src/` (pristine; checker `--game` and excerpt source) and `cap/` (captures). The archive has LF endings, so byte hashes differ from your CRLF working tree; the content is the commit.
3. **Capture-copy changes beyond the 4K override:** `editor/movie_writer/fps=30` and one autoload, `_film_capture_driver.gd`, which (a) sets the burst preview's own `retrigger` export, and (b) sends real key-press/release events (`Input.parse_input_event`, as your `price_measure.gd` does) to the price scene: key 1 at frame 30, key 3 at frame 240. It writes no game state. Logged in SOURCES.md and labelled "scripted key events" on screen.
4. **Captures made:** burst single (60 frames), burst with retrigger (60), smoke (170), price modes 1 → 3 (450). The burst position (600.7, 349.15, rotation −π) and the smoke ratios (0.375 / 0.875) printed by Godot match your r1 capture logs exactly.
5. **Price capture FPS label:** under Movie Maker it read "FPS 1" (offline rendering speed). Showing that next to "143–144" would mislead, so it is covered by a terracotta patch that says why; the 143–144 figure is from your windowed runs.
6. **21 sheet beats for your 8 sections.** The walker bookends and the code→result contract need more than 8 entries: §1 B00–B02, §2 B03–B04, §3 B05–B08, §4 B09–B12, §5 B13–B14, §6 B15, §7 B16–B17, §8 B18–B20.
7. **Length 3:30, not ~3:00.** The first draft was 696 words, about 4:28. I cut it once to 567 words, which gives 210 s. Cutting further would have dropped spoken items from your list. Every item is stated on screen in full, and the narration speaks the core of each one.
8. **"Three hits on one wall" (B08):** checked frame by frame in your recording. Bursts at ≈ 13.3, 14.2 and 15.1 s land on the same wall, which shows as cracked after the third. I did not claim several tanks. TEST-REPORT says that check was not done separately, and the screen says so too.
9. **Play-recording segments:** 12.8 s on (B08), 29.0 s on (B11, the smoke rising), 39.4 s on (B12, paused 40–43 s with the smoke frozen). Frames are in order, 48 → 30 fps by dropping frames, scaled only, audio unused.
10. **Loops:** fixture clips shorter than their beat loop, and each loop is labelled "loops". The play recording never loops.
11. **Code beats:** B03 `damage_smoke.tscn` 47–58 (node: emission and draw; process lines 30/32 in the notes), B06 `cover_hit_burst.tscn` 24–26 (R3 ramp), B10 `damage_smoke.tscn` 28–34 (R5), B13 `particles_generated.gdshader` 443–447. Line 232 appears verbatim in B13's bottom strip and as an excerpt in its notes. Two non-contiguous lines cannot share one excerpt.
12. **Narrator wording:** Liam says "the student". Your own words appear on screen as quotes, in Chinese with an English translation from TUNING.md. "My play recording" labels your footage, as you asked.
13. **Next step on the verdict:** "lower B's turbulence influence, or lighten its base colour" (your wording). Narration says "lower B's turbulence".
14. **Helpers copied** (not edited in place) from your A5 reel: `pad_audio.py`, `bind_cues.py`, `remotion_win.py`. `make_sheet.py` and `build_evidence.py` are adapted copies. `make_evidence.py`, `make_media.py` and the capture driver are new.
15. **`ART_NO_DRAWTEXT=1`** was used for `./art run` and `./art final`. It is the toolkit's own switch, used because of the Windows drawtext path bug recorded in the A5 log.

## Failures and fixes (in order)
- The first three capture runs wrote nothing: Movie Maker needs an existing output folder, and the first try also used a relative path. Fixed: absolute paths and pre-made folders. The driver had already fired correctly.
- libx264 rejected odd frame sizes (909×511, 2000×1125). Fixed with even sizes; the aspect change is 0.1 %.
- Workbench notes overflowed on B03, B06, B10 and B13, and B03's last code line was clipped. Fixed: notes shortened, predictions moved to the bottom strip, B03 code font 24.
- The hesitant writer was still typing when B01 ended. Fixed: shorter text, `charMs` 6, `mistakeRate` 1. Verified on the last frame.
- Figures had small type and the sixth strip frame was clipped. Fixed: type ×1.2, tighter crops, re-checked.
- The verdict card overlapped the @NikBearBrown label. Fixed by shortening the lines.
- Whisper writes numbers as digits, so the cue phrases were changed to "447", "80" and "godot 3".
- **GATE T attempt 1 FAIL** (`_qc/TYPECHECK-attempt1.md`): the B06 and B10 prediction strips had more than 12 words. Shortened; attempt 2 PASS.

## Observed, not changed (shared toolkit)
- The compile adds an "@NikBearBrown" overlay under the B00 composer, which already has the folder chip. It was the same in the A5 film.
- `runtime/remotion/src/scenes/GodotDesignFigure.tsx` and `package-lock.json` already had uncommitted edits before this run. They were rendered as they are and not touched.
- `./art run` / `./art final` regenerate `STATUS.md`. Their version is kept at `_qc/STATUS-toolkit-generated.md`, and STATUS.md is replaced by the one you asked for.

## Limits
- No test was re-run; every test, price and verdict is from your logs and documents.
- Gate V (42 frames) ran on the review cut. `./art final` ran GATE T only. I inspected the master myself (`_qc/final-sheet.png`, every beat).
- The checker verifies hashes, line ranges and pairings, not whether the explanation is right. FACTCHECK.md maps every claim to its source.
- Disk: `capture/` holds 3.4 GB of 4K PNG frames, kept as evidence. They can be deleted once you accept the film; `capture/work/` holds the intermediates.

## Scope kept
Writes were limited to this folder, plus one file in brutalist.art that the toolkit's own renderer writes automatically: the git-ignored usage ledger `runtime/remotion/_bench/consumers.json`. I edited no toolkit file. In walker-TANK the only git command was `archive 41a6b8b`. No Godot run touched the repo, no paid call or generated media was used, and nothing was uploaded or pushed.

## Runtime
Windows 11, Git Bash, `PYTHONUTF8=1`, Python 3.12, ffmpeg, Node (Remotion), Godot 4.7.2 console build on the RTX 3060 (Vulkan Forward+), Kokoro `am_onyx` (local, $0.00), faster-whisper `base.en` (local). Final export: 357 s in the foreground; no stray ffmpeg/Godot/node processes afterwards.
