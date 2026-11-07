# SOURCES — claude-liam-walker-tank-a6-particles

## Game source
- **walker-TANK, commit `41a6b8b`** (2026-11-06 23:38 −0500). Game source (effects, scripts) last changed at **`96d38be`** (Effect B r1).
- Read through a read-only `git -C walker-TANK archive 41a6b8b`, extracted twice outside the repo:
  - `_scratch/src/` — pristine; the checker's `--game` and the source of every code excerpt and strip frame.
  - `_scratch/cap/` — capture copy (see below). The archive has LF line endings, so file bytes differ from the CRLF working tree; content is the commit.
- Nothing in `D:/CSYE7270/assignment2/walker-TANK` was written; the only git command run there was the archive.

## Footage and images shown

| Beat | Media | What it is | Label on screen |
|---|---|---|---|
| B02, B04, B14 | `capture/godot/burst_single/`, `capture/godot/smoke/` | New 4K Movie Maker captures of `previews/cover_hit_burst_preview.tscn` (60 frames) and `previews/damage_smoke_preview.tscn` (170 frames), 30 fps, RTX 3060 | FIXTURE · cropped/enlarged · loops |
| B08 (right) | `capture/godot/burst_retrigger/` | Same burst preview with its own `retrigger` export set to true (second burst at frame 16) | FIXTURE · retrigger on · loops |
| B17 | `capture/godot/price/` | `previews/price_scene.tscn`, 450 frames; scripted key events: key 1 at frame 30, key 3 at frame 240 | FIXTURE · scripted key events; FPS label covered and explained |
| B08, B11, B12 | `D:/CSYE7270/a6-play.mp4` (SHA-256 `484cd2d9489ae9f00e6c0d674237a2f012da2374f08393aa64954c93ae1dd53a`, 1280×720, 48 fps, 49.69 s) | The student's own play recording; from 12.8 s, 29.0 s and 39.4 s, frames in order, shown at 30 fps by dropping frames, scaled only, audio unused | MY PLAY RECORDING · not a fixture |
| B05, B07, B09, B11 | `captures/cover_hit_burst/r0, r1` and `captures/damage_smoke/r0, r1` at 41a6b8b | The student's fixture strips, shown as captured, cropped and enlarged only | FIXTURE STRIP |
| B15, B16 | `evidence/ev-tests.png`, `evidence/ev-prices.png` | Tables typed from TEST-REPORT.md and the price logs | HEADLESS / WINDOWED, with log names |

Capture logs (Godot's own output, incl. the startup line "Using Device #0: NVIDIA - NVIDIA GeForce RTX 3060 Laptop GPU" and each preview's print lines) are in `capture/godot/*.log`. The burst positions in the new captures match the student's `logs/capture_cover_hit_burst_r1.log` exactly: (600.7, 349.15), rotation −3.1416; the smoke preview printed amount_ratio 0.3750 / 0.8750 at frames 10 / 60, as in r1.

### The capture copy (`_scratch/cap/`, never in the repo)
Godot 4.7.2 (`Godot_v4.7.2-stable_win64_console.exe`) with `--write-movie … --fixed-fps 30 --quit-after N`. Changes to the copy only:
- `project.godot`: `window/size/window_width_override=3840`, `window_height_override=2160` (stretch `canvas_items` unchanged, so the 1280×720 game renders 3× at 4K), `editor/movie_writer/fps=30`, and one autoload:
- `_film_capture_driver.gd`: sets the burst preview's own `retrigger` export (`-- --film=retrigger`) and sends real `InputEventKey` press/release pairs through `Input.parse_input_event` to the price scene (`-- --film=price`). It writes no game state.
No game script, scene or setting was edited.

## Numbers and quotes
Every number and quote is from the sources of truth at 41a6b8b; see FACTCHECK.md for the beat-by-beat mapping.

## Fonts, voice, tools
- Narration: Kokoro `am_onyx`, local, $0.00. Cue timing: faster-whisper `base.en`, local.
- Fonts: the toolkit's EB Garamond / Lato / Inter; Consolas and Microsoft YaHei (Windows) for code and the Chinese quotes.
- Rendering: brutalist.art Remotion scenes via `runtime/scripts/remotion_scenes.py` (through the copied Windows npx shim); ffmpeg for VIDEO beats.
- No paid API, no generated media, no upload.

## Textures named in the film
`effects/textures/chip_6.png` and `soft_dot_32.png`, drawn by code (`tools/make_particle_textures.gd`), per walker-TANK SOURCES.md and `effects/textures/CREDITS.md`.
