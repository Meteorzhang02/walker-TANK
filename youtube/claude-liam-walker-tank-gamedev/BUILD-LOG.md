# BUILD-LOG — claude-liam-walker-tank-gamedev

Skill: `godot-gamedev`, **walker** mode (bookends from ai-explainer; capture contract from godot-waikthrough).
Channel claude-liam (Liam in for Bear, Kokoro `am_onyx`). No paid calls. No game change. Nothing pushed or published.

## Environment (Windows 11, Chinese locale)
- `PYTHONUTF8=1` set; `~/bin/python3` shim → Python 3.12.1. ffmpeg/ffprobe in `~/bin`. Node 24.11. Remotion node_modules present.
- `./setup` aborts on its ElevenLabs lint of existing example reels in `brutalist.art/youtube/` (toolkit issue, not edited);
  its checks were run by hand: PIL, manim, faster_whisper, kokoro_onnx OK; Kokoro smoke −21.8 dB OK; no pdflatex (no math in this film).
- Godot is not on PATH: `D:/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe`.
- faster-whisper `base.en` was downloaded once from Hugging Face (free) for cue timing and narration checks.

## Decisions
1. Reel lives inside the game package (`walker-TANK/youtube/…`) as the skill specifies; `youtube/.gdignore` added so
   Godot never imports film files. The ledger lists the reel's own files as exclusions.
2. New scripted-input driver (CAPTURE.md), not the project's test (which calls handlers directly).
3. Game audio is kept: each gameplay beat's audio is the same interval of the engine's WAV, ducked under Liam;
   B24 is labeled GAME AUDIO ONLY with no narration (assignment requirement 4).
4. Sound tags on gameplay come from the game's own `audio.counts` requests in the log, not from listening.
5. Code change shown: the health-bar fill (main.gd 299/378), because a real "before" exists (the student's play-01 screenshot).
6. B03/B04 reuse intervals that appear again later; both carry a PREVIEW label.
7. Tank name spelled "Yoon-chee Zee" in narration (Kokoro reads "YunqiZ" as "Yunkisei").
8. `lead_silence_s` is not implemented by the runtime: B01's 0.8 s lead and B35's 1.0 s tail are silence padding
   (`scripts/pad_audio.py`), raw TTS kept in `mp3/raw/`.

## Failures and fixes (kept)
- Driver parse error (type inference on untyped values) → typed locals.
- First 4K attempt recorded 1280×720: Movie Maker uses the viewport size under canvas_items → window override in the copy.
- Running Remotion renders during the Movie Maker take slowed it ~5× → renders stopped until the take finished.
- 4K take interrupted at frame 841 (user, battery) → kept in `capture/_failed/attempt-4k-interrupted/`; full take re-recorded.
- Evidence panel type below the legibility floor → enlarged. Workbench notes column clipped its third note → notes shortened.
- B01 first line ran edge to edge → re-broken into four lines.
- "♪" glyph missing from Inter (tofu) → "sound:" text; tags collided with the GAME AUDIO label → label moved.
- alimiter shortened mixed beats (B21 11.44 s vs 12.0 s) → pad/trim after the limiter; whisper confirmed every
  mixed beat still contains its last words.
- Cue phrases whisper could not match (digits, "docstring") → nearby spoken words.

## Toolkit issues seen (brutalist.art; not changed here)
1. `remotion_scenes.py` runs bare `npx` (fails on Windows) → `scripts/remotion_win.py` shim.
2. `remotion_scenes.py` writes `runtime/remotion/_bench/consumers.json` (a toolkit file) on every render.
3. `./setup` aborts on the ElevenLabs lint before reporting readiness.
4. `godot-gamedev --check` inventories the whole game folder, so a reel stored inside it (as the skill prescribes)
   must list its own files as exclusions, regenerated before each check.
