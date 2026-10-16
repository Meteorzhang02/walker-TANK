# BUILD-LOG — claude-liam-walker-tank-a3-assets

Skill `godot-gamedev`, walker mode; channel claude-liam (Kokoro `am_onyx`). No paid calls, no game change, nothing
pushed or published. Built 2026-10-15 for the CSYE7270 Assignment 3 deadline (short, plain film by request).

## Runtime check (Windows 11, Chinese locale)
- `PYTHONUTF8=1` set; `~/bin/python3` shim → Python 3.12.1; ffmpeg/ffprobe in `~/bin`; Node 24.11; Remotion
  node_modules present; Kokoro model files present; `kokoro_onnx`, `faster_whisper` import OK.
- `./setup` / `./art doctor` still abort on the ElevenLabs lint of example reels in `brutalist.art/youtube/` before
  reporting readiness (toolkit issue, not edited). Checks run by hand instead; Kokoro generated all 14 beats.
- Godot not on PATH: `D:/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe` (4.7.2.stable.official.ed1daf0bf).
- Blender not needed (screenshots + recorded results; no rebuild).

## Decisions
1. Reel outside the walker-TANK Git repo (user request), so no `.gdignore` and no change to the game tree.
2. Scope: A3 only. 26 A3 files in the ledger; 3231 A2/film files excluded with reasons.
3. Running scene captured from an isolated `git archive 9baa12c` copy; only a window-size override and MJPEG quality
   differ in the copy's project.godot.
4. Headless check re-run on that copy (18/18, exit 0). FAIL path not re-run; the student's recorded proof is cited.
5. The B04 prompt text is not in the supplied screenshots: shown as "Claude's plan" + "Claude's report", not quoted.
6. Narration tightened once (first measure ~3:50) to fit the short-film request; final ~3:39.
7. Reused tooling from the A2 film reel: `remotion_win.py` (npx shim), `pad_audio.py`, `bind_cues.py`.

## Failures and fixes
- `remotion_scenes.py --only` accepts one beat; the first batch call failed with a usage error (exit 2) → one call per beat.
- PIL font paths (Inter has no Bold in runtime/fonts) → Lato Bold for emphasis.
- First 450-frame capture was shorter than B07's 15.4 s narration → re-recorded 540 frames (no hold).
- Whisper wrote numbers as digits; cue phrases moved to nearby words.
- B11 said "approved each call"; FRICTIONAL.md says a few calls ran in auto mode → corrected, audio regenerated.
- Final export attempt 1 (foreground, 4 min 47 s) was REFUSED by Gate V: B07 (full-frame engine footage) flagged
  edge-bleed + low whole-frame contrast by the flat-card heuristics (`_qc/GATE-V-attempt1.md`). Free RAM fell to
  51 MB during it, but the refusal was the gate, not a crash. Fix: B07 declares `qc.full_bleed` and two labelled
  `contrast_regions` (its burned-in text banners) with a written `contrast_reason`. No media changed.
- Final export attempt 2: EXPORT_EXIT=0, Gate V 0 BLOCKER / 0 MAJOR, GATE T PASS, 14/14 slots, 218.57 s,
  3840×2160 h264 30 fps + AAC 48 kHz, full decode OK, mean −27.8 dB / max −5.4 dB, no silence > 2 s.
  sha256 b91f985d83d7ffed36f941aef078ee3efa676d958c6f58b1ad84931d95c98d8c (matches the `.verified.json` receipt).
- Observed in the master: in the last second of the locked ClaudeTitleOutro, the mascot's jump animation briefly
  overlaps the @NikBearBrown handle. Locked toolkit component; not changed.
- `./art godot-gamedev --check` PASS at handoff; walker-TANK still at 9baa12c with a clean working tree.
