# SOURCES — this film

## The game (source of every claim)
- walker-TANK, git commit `4616fc762d5b1b64c770cdc21d1662684cb13d46`, Godot 4.7.2.stable.official.ed1daf0bf.
- Source manifest hash (build_id): `52acbd5444813fc5a9357dad952d4378b879b141ae0f0b8996f42de396ef7f6f`
  (`capture/source-manifest.txt`). Every file's own SHA-256 is in `gamedev-evidence.json`.
- Assignment brief: `assignment2/02-generate-art-sound-music-for-your-game.txt` (quoted verbatim in B02).

## Native engine capture
- `capture/run-01.mp4` SHA-256 `0a14c8b657bcb455f25fd0e93fc8126274808257494eac5ff71a5572368fe6af`
  (1667 frames, 3840×2160, 30 fps; x264 crf 8 from the Movie Maker PNG sequence, PSNR ≈ 44 dB vs the PNGs).
- `capture/run-01.wav` SHA-256 `b7d5da722a74be989135a0cb9204cee3d1c7241e9ad86ac26eb7af25eeecaf81`
  (the engine's own mix, 55.567 s, 48 kHz stereo).
- Method, driver and calibration: CAPTURE.md. Input log: `capture/run-01-inputs.jsonl`.
- Runtime tree: not probed separately. main.gd builds every node in `_ready()`; the saved `main.tscn` is one node.

## Generative-model assets shown (made by the student, not for this film)
As recorded in the game's SOURCES.md / ASSET-LOG.md: Stable Diffusion XL Base 1.0 (CreativeML Open RAIL++-M) for the
hull, turret, cover and ground; Stable Audio 3 Small-SFX and Small-Music (Stability AI Community License; T5Gemma under
the Gemma Terms of Use) for the five SFX and the loop. All ran locally in ComfyUI v0.38.2. The licence wording is the
student's; ASSET-LOG marks the SDXL licence "to verify".

## Film tools (all free, local)
- Narration: Kokoro v1.0 ONNX, voice `am_onyx` (Liam, in for Bear). Cost $0.00.
- Cue timing and narration checks: faster-whisper `base.en` (downloaded once from Hugging Face; local inference).
- Remotion (brutalist.art `runtime/remotion`): ClaudeComposerAsk, BrutalistHesitantWriter, GodotDevWorkbench,
  GodotDesignFigure, ClaudeVerdictArtifact, ClaudeTitleOutro. Rendered through `runtime/scripts/remotion_scenes.py`
  via `scripts/remotion_win.py` (Windows `npx.cmd` shim; the toolkit script is unmodified).
- FFmpeg / ffprobe (gyan.dev build in `~/bin`), Pillow, NumPy for evidence panels and clip cuts.
- Fonts: Inter, PT Mono, EB Garamond (bundled in brutalist.art `runtime/fonts`).

## Not used
No paid API, no image/audio/video generation, no upstream web documentation fetched for this build (the Movie Maker
behaviour was taken from the toolkit's capture reference and observed directly). Nothing uploaded or published.
