# BUILD-PROMPT — how to rebuild this film

Run from `D:/CSYE7270/brutalist.art` (Windows, Git Bash, `PYTHONUTF8=1`). `REEL=D:/CSYE7270/assignment2/walker-TANK/youtube/claude-liam-walker-tank-a7-animation`.

1. `git -C D:/CSYE7270/assignment2/walker-TANK archive 4f88f1b -o $REEL/_scratch/walker-TANK-4f88f1b.tar`; extract to `_scratch/src`, and without `youtube/` to `_scratch/cap`.
2. Capture copy only: 4K window override and `[editor] movie_writer/fps=30` in `_scratch/cap/project.godot`; add `_scratch/cap/_film/a7_play.{gd,tscn}`; `godot --headless --path . --import`.
3. Captures (folders must exist; absolute paths): `godot --path . --write-movie $REEL/capture/godot/<s>/frame.png --fixed-fps 30 res://_film/a7_play.tscn -- --film=<s>` for s = hits, drive, death_s, death_a, death_r.
4. `python $REEL/scripts/make_evidence.py` → `python $REEL/scripts/make_sheet.py` → `python runtime/scripts/generate_audio_kokoro.py $REEL` → `python $REEL/scripts/pad_audio.py` → `python $REEL/scripts/bind_cues.py`.
5. Remotion beats one at a time: `python $REEL/scripts/remotion_win.py $REEL --only Bxx --force` (B00 B01 B02 B04 B05 B06 B08 B12 B13 B14 B15 B16 B17).
6. Capture beats: `python $REEL/scripts/make_media.py` (B03 B07 B09 B10 B11).
7. `python $REEL/scripts/build_evidence.py`; `./art godot-gamedev --check $REEL --game $REEL/_scratch/src`.
8. `ART_NO_DRAWTEXT=1 ./art run $REEL --height 1080`; inspect `_qc/`; then `ART_NO_DRAWTEXT=1 ./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape` in the foreground. Re-run step 7.
