# CAPTURE — how the gameplay was recorded

## Build identity
- Game: `walker-TANK/` (`project.godot`, main scene `res://scenes/main.tscn`), git commit
  `4616fc762d5b1b64c770cdc21d1662684cb13d46` (working tree clean apart from this untracked `youtube/` folder).
- Engine: `Godot_v4.7.2-stable_win64_console.exe --version` → `4.7.2.stable.official.ed1daf0bf`
  (Vulkan Forward+, NVIDIA GeForce RTX 3060 Laptop GPU), Windows 11 (Chinese locale).
- `build_id` = SHA-256 of `capture/source-manifest.txt` =
  `52acbd5444813fc5a9357dad952d4378b879b141ae0f0b8996f42de396ef7f6f`: a sorted `sha256  path` list of every
  git-tracked file except `*.uid` (188 files). Recompute the same way to check staleness.
- The original game folder was **not modified**. The game writes no saves.

## Isolated capture copy (Claude's scratchpad, not the game folder)
The copy was made with `tar` from the working tree (no `.git`, no `youtube/`), imported once with
`--headless --import`. Byte comparison against every tracked file: identical except `project.godot`, which
differs only by:
1. `window/size/window_width_override=3840` and `window_height_override=2160`. Godot's Movie Maker records
   the project's viewport size under `canvas_items` stretch, so without this the first attempt recorded
   1280×720 even with `--resolution 3840x2160` (attempt kept in `capture/_failed/`, not used). The logical
   game canvas is still 1280×720 (`canvas_items`), rendered natively at ×3.
2. `[autoload] CaptureDriver="*res://walkthrough/capture_driver.gd"` (the driver, copied here as
   `capture/driver/capture_driver.gd`; the full capture `project.godot` is `capture/driver/capture-project.godot`).

## Input method: scripted input, not a human playtest
- The driver **writes only input**: `Input.action_press/release` on the game's own actions (`move_*`, `fire`),
  `Input.parse_input_event` key events (Esc for pause), and the real mouse cursor via `Viewport.warp_mouse`
  for turret aim. `player.gd` reads `get_global_mouse_position()`, i.e. the real cursor; the driver warps it
  every physics tick before the player script runs (`process_physics_priority = -100`).
- It **reads** positions, velocities, health, cover stage, `level_won` and `audio.counts` to decide when and
  where to press (leading moving targets, a ray query for line of sight). It never sets positions, health,
  timers or collisions, and never calls a game function. The project's test script calls handlers directly,
  so it was **not** used for footage.
- Phases: idle 5 s → eight short drive legs (one per facing, 0.5 s stop after each) → shoot the nearest cover
  until broken → fight in the open (no hiding, so return fire lands) → one Esc pause/resume after the first
  kill → fight to victory → hold 8 s on the victory panel → quit. Every phase asserts its result; the end
  assertion requires victory, at least one death, three kills and exactly one victory sound request, else exit 3.
- Aim check: every 30 ticks the log compares the aim point with the game's `get_global_mouse_position()`.
- The enemies use `randomize()`: every take plays differently. Two 1280×720 rehearsals (AVI, discarded)
  tuned pacing only; the film uses the single native-4K take `run-01`.
- Logs: `capture/run-01-inputs.jsonl` (every press/release/key tap, every logged game event with physics tick
  and `Engine.get_frames_drawn()`), `capture/run-01-stdout.txt`.

## Recording
- Godot Movie Maker: `--write-movie capture/_frames/run01.png --fixed-fps 30 --quit-after 9000`, PNG
  sequence + WAV, physics 60 Hz (2 ticks per frame). Offline rendering: says nothing about real-time FPS.
- Encoded losslessly-visually to `capture/run-01.mp4` (x264 `-crf 8 -preset slow`, yuv420p, every frame).
  The PNG frames are kept (see Hashes); nothing was deleted.
- Game audio: the Movie Maker WAV is the engine's own mix (Music + SFX buses) and is kept as
  `capture/run-01.wav`. Nothing was added, replaced or re-timed.

## The take (run-01)
- Recorded 2026-10-06 17:09–18:08: `1667 frames at 30 FPS (movie length 00:00:55:17), recorded in 00:59:17`, exit 0.
  End assertion `ok: true`: 3 kills, 2 deaths, victory, sound requests {fire 17, enemy_fire 22, cover_hit 7,
  player_hit 6, enemy_hit 6, explode 5, victory 1}. Log ends with `DONE`.
- Aim: 114 checks, maximum distance between the intended aim point and the game's mouse position 0.95 px.
- Stale-frame guard: logged `frames_drawn − tick/2` stays within 0–0.5 for the whole take (no repeated/stalled frames).
- An earlier 4K take was **interrupted at frame 841** at the user's request (battery). It is kept, unused, in
  `capture/_failed/attempt-4k-interrupted/`; the 720p attempt is in `capture/_failed/`.

## Calibration (measured)
- Movie frame = logged `Engine.get_frames_drawn()` (offset 0). Checked twice: the PAUSED label first appears in PNG
  frame 739, the logged music pause; the VICTORY panel first appears in PNG frame 1426, the logged last kill.
- Clips were re-checked after cutting: VICTORY appears at B24 clip frame 6 (= 1420 + 6), PAUSED at B21 clip frame 199 (= 540 + 199).

## Hashes
- `capture/run-01.mp4` `0a14c8b657bcb455f25fd0e93fc8126274808257494eac5ff71a5572368fe6af` (3840×2160, 1667 frames)
- `capture/run-01.wav` `b7d5da722a74be989135a0cb9204cee3d1c7241e9ad86ac26eb7af25eeecaf81` (55.567 s, 48 kHz, mean −16.8 dB, peak 0.0 dB)
- Encode check: PSNR 44.1–44.2 dB at frames 100, 900, 1600 against the source PNGs.
- The PNG frames (`capture/_frames/`) are kept until the user decides to remove them.

## Clips and audio
- `clips.json` lists each beat's exact frame range. `media/Bxx.mp4` = those frames only (no retime, crop or speed
  change) + the disclosure label + logged sound tags. B03/B04 are labeled PREVIEW intervals shown again later.
- Beat audio = the same interval of `run-01.wav`. Narrated beats: Kokoro narration (0.3 s lead) over the game audio
  at −4 dB, side-chain ducked by the narration, limiter at 0.95, padded to the clip's frame count. B24: the game audio
  alone at −2 dB, no narration. Untouched TTS is kept in `mp3/raw/`.
- Not driven in this take: the mute keys (M/N) and restart (R). They are implemented but have no film evidence.
