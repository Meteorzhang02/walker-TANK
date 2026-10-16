# BUILD-PROMPT — rebuild this film end to end

Run in Claude Code from `D:/CSYE7270/brutalist.art` (Windows, Git Bash, `PYTHONUTF8=1`, `python3` shim → python):

> Rebuild the godot-gamedev walker film in `D:/CSYE7270/assignment2/walker-TANK-a3-film/claude-liam-walker-tank-a3-assets`
> for walker-TANK commit 9baa12c. Do not change the game, do not push, do not publish. Steps:
> 1. `git archive 9baa12c` into a scratch copy; `--headless --import`; re-run `tests/check_a3_assets.gd` with GNU
>    `timeout 120` → `capture/check-stdout.txt`; record `asset_room_3d.tscn` with Movie Maker (window override 3840×2160,
>    540 frames, 30 fps) → `capture/room.avi`, `room-run.mp4`.
> 2. `python scripts/make_evidence.py`; `python scripts/make_sheet.py`; `python3 runtime/scripts/generate_audio_kokoro.py REEL`;
>    `python scripts/pad_audio.py`; `python scripts/make_sheet.py`; `python scripts/bind_cues.py`; `python scripts/make_b07.py`.
> 3. Render each Remotion beat: `python REEL/scripts/remotion_win.py REEL --only Bxx` (one beat per call).
> 4. `python scripts/build_evidence.py`; `./art godot-gamedev --check REEL --game D:/CSYE7270/assignment2/walker-TANK`.
> 5. `./art run REEL --height 1080`, inspect `_qc/` frames, then in the foreground with memory monitoring:
>    `./art final REEL --height 2160 --fps 30 --out REEL/exports/landscape`. Report path + SHA-256.
