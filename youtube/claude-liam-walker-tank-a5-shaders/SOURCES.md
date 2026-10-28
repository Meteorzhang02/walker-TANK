# SOURCES — claude-liam-walker-tank-a5-shaders

- **Game source revision:** walker-TANK `561d47d` (`git rev-parse --short HEAD`, clean working tree), Godot 4.7.2
  stable (as recorded by every log). Godot was **not** launched for this film.
- **Student's play recording:** `D:/CSYE7270/a5-evidence/play.mp4`, 1294×812, 30 fps, 30.37 s, H.264 + AAC,
  sha256 `f1581b13c128b52d5bf543bc2702e57e093062fbe0e8ffbb95b3b6547089eda2`. Used in B03: source frames 135–439
  (4.5–14.7 s), in order, scaled ×2.02 (Lanczos), placed on the cream page with the label "Screen recording of my play";
  its audio is not used. Built by `scripts/make_b03.py` → `media/B03.mp4`.
- **Scripted in-engine captures** (student's windowed runs of the Claude Code capture tools, 1280×720):
  `docs/a5/captures/hit_flash_{0.0,0.5,1.0,2.0}.png`, `hint_both.png`, `materials_side_by_side.png`,
  `sweep_brightness_{min,max}.png`, `sweep_uv_scale_{min,max}.png`, plus the CSVs `hit_flash_pixels.csv`,
  `hint_pixels.csv`, `materials_captures.csv`, `shader_edit_materials_captures.csv`. Hashes in `gamedev-evidence.json`.
  Cropped/scaled only (nearest-neighbour for pixel crops); markers and boxes are added and labelled.
- **Measured for the film:** three box means in `materials_side_by_side.png` (`scripts/make_evidence.py`,
  `capture/litwall-means.json`) and the hint background pixel (127). Read-only arithmetic on existing PNGs.
- **Texture:** Poly Haven *Red Bricks 04* (`red_bricks_04`), Rob Tuytel, CC0 — https://polyhaven.com/a/red_bricks_04
  (as recorded in the game's SOURCES.md and `assets/textures/brick/ATTRIBUTION.md`; not re-downloaded).
- **Documents read:** README.md, CHANGE-BRIEF.md (with Revisions), MATERIALS.md, LANGUAGE-NOTES.md, TEST-REPORT.md,
  FRICTIONAL.md, SOURCES.md, CLAUDE.md, the four shaders, `scripts/hit_flash_driver.gd`, the capture CSVs,
  `docs/a5/captures-output.txt`, `docs/a5/step2-output.txt`, the test logs in `logs/`.
- **Toolkit:** brutalist.art (`godot-gamedev`, walker mode) at its current local tree, including a pre-existing
  uncommitted edit to `runtime/remotion/src/scenes/GodotDesignFigure.tsx` (footer offsets) that was not made or changed
  by this build. Kokoro-82M `am_onyx` (local), faster-whisper `base.en` (local, cue timing only), Remotion, FFmpeg.
- **No** AI images, paid calls, uploads, or new engine captures.
- **Corrections applied while writing:** two quoted line numbers were first taken from a concatenated `cat -n`
  listing and were wrong (brief colour line is line 45, `PARAM` is driver line 12); fixed from `grep -n` before render.
