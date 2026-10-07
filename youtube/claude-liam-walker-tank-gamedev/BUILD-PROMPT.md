# BUILD-PROMPT — rebuild this film end to end

Paste into Claude Code from `D:/CSYE7270/brutalist.art` (Windows: `PYTHONUTF8=1`, a `python3` shim, Godot 4.7.2
console exe at `D:/CSYE7270/Godot_v4.7.2-stable_win64.exe/`). No paid calls, no game edits, no push, no publish.

```text
Read skills/make/godot-gamedev/SKILL.md and everything it links. Rebuild the reel at
D:/CSYE7270/assignment2/walker-TANK/youtube/claude-liam-walker-tank-gamedev without touching the game:
1. Confirm the game is still commit 4616fc7 (recompute capture/source-manifest.txt; it must hash to
   52acbd54…). If it changed, stop: the source ledger and captures are stale.
2. Reuse capture/run-01.mp4 + run-01.wav (verify their SHA-256 in coverage.json). Only re-capture with
   capture/driver/ on an isolated copy if they are missing; a new take needs new narration (enemies are random).
3. python scripts/build_evidence.py (+ --test-panel --doc-panels --muted --healthbar); python scripts/make_sheet.py
4. python3 runtime/scripts/generate_audio_kokoro.py REEL; python scripts/pad_audio.py; python scripts/cut_clips.py;
   python scripts/bind_cues.py
5. python scripts/remotion_win.py REEL --only <each Remotion beat>   (Windows npx shim; inspect a pilot first)
6. python scripts/make_evidence.py; ./art godot-gamedev --check REEL --game D:/CSYE7270/assignment2/walker-TANK
7. ./art final REEL --height 2160 --fps 30 --out REEL/exports/landscape
8. Frame QC: sample every beat at 15/50/85 %, read the PNGs, listen to B17/B19/B21/B24 (game audio) and the outro
   (voice only). Record results in _qc/REPORT.md. Re-run the check. Report the MP4 path and SHA-256.
```
