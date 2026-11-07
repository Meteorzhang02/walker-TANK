# BUILD-PROMPT — how to rebuild this film

Run from `D:/CSYE7270/brutalist.art` (Windows, Git Bash, `PYTHONUTF8=1`). `REEL=D:/CSYE7270/assignment2/claude-liam-walker-tank-a6-particles`.

1. Source copies (read-only on the repo): `git -C D:/CSYE7270/assignment2/walker-TANK archive 41a6b8b > $REEL/_scratch/walker-TANK-41a6b8b.tar`; extract into `_scratch/src` (pristine) and `_scratch/cap` (capture copy).
2. Capture copy only: append the 4K window override, `[autoload] FilmCaptureDriver`, `[editor] movie_writer/fps=30` to `_scratch/cap/project.godot`; add `_scratch/cap/_film_capture_driver.gd`; `godot --headless --path . --import`.
3. Captures (output folders must exist first; use absolute output paths):
   `godot --path . --write-movie $REEL/capture/godot/<name>/frame.png --fixed-fps 30 --quit-after N <scene> [-- --film=retrigger|price]`
   for burst_single (60), burst_retrigger (60), smoke (170), price (450).
4. `python $REEL/scripts/make_evidence.py` → `python $REEL/scripts/make_sheet.py` → `python runtime/scripts/generate_audio_kokoro.py $REEL` → `python $REEL/scripts/pad_audio.py` → `python $REEL/scripts/bind_cues.py`.
5. Remotion beats, one per call: `python $REEL/scripts/remotion_win.py $REEL --only Bxx --force` (B00 B01 B03 B05 B06 B07 B09 B10 B13 B15 B16 B18 B19 B20).
6. VIDEO beats: `python $REEL/scripts/make_media.py` (B02 B04 B08 B11 B12 B14 B17).
7. `python $REEL/scripts/build_evidence.py`; `./art godot-gamedev --check $REEL --game $REEL/_scratch/src`.
8. `ART_NO_DRAWTEXT=1 ./art run $REEL --height 1080`; inspect `_qc/`; then `./art final $REEL --height 2160 --fps 30 --out $REEL/exports/landscape` in the foreground. Re-run step 7.
