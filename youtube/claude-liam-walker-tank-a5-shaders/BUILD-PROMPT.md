# BUILD-PROMPT — rebuild this film end to end

Run in Claude Code from `D:/CSYE7270/brutalist.art` (Windows, Git Bash, `PYTHONUTF8=1`, `python3` shim → python):

> Rebuild the godot-gamedev walker film in
> `D:/CSYE7270/assignment2/walker-TANK/youtube/claude-liam-walker-tank-a5-shaders` for walker-TANK commit 561d47d.
> Do not launch Godot, do not change the game, no git in walker-TANK, do not push, do not publish. Steps (REEL = that folder):
> 1. `python REEL/scripts/make_evidence.py` (figures from docs/a5/captures, logs, brief).
> 2. `python REEL/scripts/make_sheet.py`; `python3 runtime/scripts/generate_audio_kokoro.py REEL`;
>    `python REEL/scripts/pad_audio.py`; `python REEL/scripts/make_sheet.py`; `python REEL/scripts/bind_cues.py`;
>    `python REEL/scripts/make_b03.py` (play recording, from 4.5 s, not retimed).
> 3. Render each Remotion beat: `python REEL/scripts/remotion_win.py REEL --only Bxx --force` (one beat per call).
> 4. `python REEL/scripts/build_evidence.py`; `./art godot-gamedev --check REEL --game D:/CSYE7270/assignment2/walker-TANK`.
> 5. Check for orphaned ffmpeg; `./art run REEL --height 1080`, inspect `_qc/` frames; then in the foreground with memory
>    monitoring: `./art final REEL --height 2160 --fps 30 --out REEL/exports/landscape`. Re-run step 4's check.
>    Report path, duration, size and SHA-256 (match the `.verified.json` receipt).
