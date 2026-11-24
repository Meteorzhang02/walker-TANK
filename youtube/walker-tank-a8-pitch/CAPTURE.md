# CAPTURE — how the gameplay was recorded

On-screen label on every gameplay frame: **REAL CAPTURE · scripted input / tag a7, game source 4f88f1b**.

## Build identity
- Game: `walker-TANK` (`project.godot` at the repo root, main scene `res://scenes/main.tscn`).
- Scratch copy made with `git archive HEAD` (HEAD = `3cc29f2`), as BUILD-PROMPT.md asks. `git diff --name-only 4f88f1b HEAD`
  touches no game file (only docs, pitch/, prompts/, captures/shoot_r0 frames, youtube/), so the game source is
  identical to **4f88f1b**. The **a7 tag** is commit `e4e5d5f` (docs on top of 4f88f1b); hence the label wording.
- `build_id` = SHA-256 of `capture/source-manifest.txt` (sorted `sha256  path` of every file in `git archive HEAD`
  except `*.uid`, 718 files) = `718a209b8cc983d503b42b417ff06baa9f1862fc4a6abefae5df9818732f53c9`.
- Engine: `Godot_v4.7.2-stable_win64_console.exe --version` → `4.7.2.stable.official.ed1daf0bf`; Vulkan Forward+ on the
  NVIDIA GeForce RTX 3060 Laptop GPU; Windows 11.
- The walker-TANK repository was not modified. No Godot run touched it.

## Capture copy (`_scratch/src`, git-ignored)
Byte-identical to the archive except `project.godot`, which gains (copy kept as `scripts/capture-project.godot`):
1. `window/size/window_width_override=3840`, `window_height_override=2160` so Movie Maker records native 4K
   (logical canvas stays 1280×720 under `canvas_items`, rendered ×3).
2. `[autoload] CaptureDriver="*res://walkthrough/capture_driver.gd"` = `scripts/capture_driver.gd`.
Tests for B06 ran in a separate clean archive (`_scratch/test`) with no driver.

## Input method: scripted input, not a human playtest
`scripts/capture_driver.gd` is the gamedev reel's driver, adapted (no pause phase, shorter drive tour, extra read-only
logs of the effects the narration names). It **writes only input**: `Input.action_press/release` on the game's own
actions and the real cursor via `Viewport.warp_mouse`. It **reads** positions, health, cover stage, smoke state, the
hit-flash shader's `hit_amount` and audio counts to decide when to press and to log evidence. It never sets game
state or calls game functions. Enemies use `randomize()`, so the take is one unrepeatable run.
Phases: idle 4 s → four drive legs → shoot the nearest cover until broken → fight in the open → hold 3 s → quit.

## The take (run-01)
- 2026-11-23 11:43:38 → 12:23:53, `--write-movie capture/_frames/run01.png --fixed-fps 30 --quit-after 9000`,
  exit 0. 1,104 frames (36.8 s). End assertion `ok: true`: 3 kills, 2 deaths (YunqiZ respawned twice), victory.
- A 1280×720 AVI pilot (`capture/_pilot/`) checked the driver first; it is not used in the film.
- Movie Maker is offline rendering: it says nothing about real-time FPS.
- Logged frame = `Engine.get_frames_drawn()` = movie frame. Checked by eye: the cover burst logged at frame 258 and
  YunqiZ's red flash logged at 308 are on screen in those frames (`_qc/effects/b04_sheet.png`).

## Effects named in the narration — checked on screen (BUILD-PROMPT rule)
| Narration | run-01 frames | Seen |
|---|---|---|
| debris bursts from the hit point | burst at 258 and 302 (B04 segment 1, 178–338) | yes — brick-coloured debris and dust at the hit point |
| YunqiZ flashes red | 308, 345 (segment 2, 296–361) | yes — hull and turret red |
| a damaged tank smokes | enemy 2 smoke from 459 (segment 3, 453–490) | yes — grey smoke over the live enemy |
| a wreck keeps smoking | enemy 2 destroyed 515; wreck 560–698 (segment 4) | yes — dark wreck with smoke |
Nothing was drawn or faked in a gameplay beat. The A5 red flash is on YunqiZ only; enemies flash white — the
narration says "YunqiZ flashes red", not "a hit tank".

## Clips (`clips.json`, built by `scripts/make_media.py`)
- B01: frames 0–440, full frame (includes YunqiZ's first death and respawn message at 381).
- B04: four in-order intervals of the one take, each cropped 1.5× around the logged event and captioned so.
- B12: frames 591–997 scaled into the left panel of the drawn close; it ends before the victory panel, because the
  brief lists win/lose screens as "will exist".
- Frames are never retimed, reordered or retouched. Every clip runs exactly its beat's padded audio frame count.
- **Game audio muted:** narration is the only sound; the take's WAV is kept as `capture/run-01.wav`.

## Hashes
- `capture/run-01.mp4` `2116476a25d73378539e88bccc283dbaa9e45db18353a89c87e6295e1afed60f` (3840×2160, 1,104 frames, x264 crf 8)
- `capture/run-01.wav` `f2da5003207ecb1cec15061d1eee4cef4974c9fe12d7deec360eeb2d90cb056b`
- `capture/run-01-inputs.jsonl` `40b8f00b59064543e169ed32872ee385229001c5fbc3f826e42b7c2738a8f2d2`
- PNG frames kept in `capture/_frames/` (git-ignored) until you decide to delete them.
