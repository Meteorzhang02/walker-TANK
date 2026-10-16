# SOURCES — claude-liam-walker-tank-a3-assets

**Film:** "Walker-TANK: Three Assets, One Hand Edit" — godot-gamedev, walker mode, claude-liam (Liam in for Bear,
local Kokoro `am_onyx`). Built by Claude Code (Opus 5.5) with the brutalist.art toolkit. No paid calls, no upload,
no publication, no Git push. The game was not changed.

## Game source
- Repository `D:/CSYE7270/assignment2/walker-TANK`, revision **9baa12c** (`9baa12c1011baf18a179feb9f2e2537e1111a942`),
  working tree clean when inspected. The reel is kept **outside** that repository.
- Engine: `Godot_v4.7.2-stable_win64_console.exe --version` → `4.7.2.stable.official.ed1daf0bf` (Vulkan Forward+, RTX 3060 Laptop).
- Documents used: CHANGE-BRIEF.md, TEST-REPORT.md, FRICTIONAL.md (Assignment 3 part only, lines 1–85), SOURCES.md,
  BLENDER-NOTES.md, README.md, `.claude/settings.json`, `scenes/asset_room_3d.tscn`, `tests/check_a3_assets.gd`.

## Isolated copy (not the game folder)
`git archive 9baa12c | tar -x` into Claude's scratchpad (`iso-9baa12c`), `youtube/` removed, then
`--headless --path . --import` (exit 0, `capture/import-stdout.txt`).

## Headless check (re-run)
`timeout 120 godot --headless --path . --script res://tests/check_a3_assets.gd --fixed-fps 60` →
18 PASS lines, `RESULT: PASS (0 failure(s))`, exit 0. Full output: `capture/check-stdout.txt`
(sha256 `b27b6fd4…8d3d27`). The FAIL-path proof shown in the film is the student's recorded run (TEST-REPORT.md,
`08b-fail-path-proven.png`); it was not re-run for the film.

## Running-scene capture (B07)
- `godot --path . --write-movie _cap/room.avi --fixed-fps 30 --quit-after 540 res://scenes/asset_room_3d.tscn`
  (exit 0; 540 frames, 3840×2160 MJPEG). The copy's `project.godot` differs from the original only by
  `window/size/window_width_override=3840`, `window_height_override=2160` and `[editor] movie_writer/mjpeg_quality=0.95`
  (`capture/project.godot.original` vs `capture/capture-project.godot`). The scene file itself is unchanged.
- `capture/room.avi` sha256 `1e753af0…a2364a76`; x264 crf 10 → `capture/room-run.mp4` sha256 `67fb4f8b…bd443d529`.
- `media/B07.mp4` = frames 30–491 of that take, in order (no hold, no retiming), with a burned label
  ("RUNNING GODOT SCENE …", "Movie Maker capture, isolated copy of commit 9baa12c · fixed camera, the scene has no motion")
  and the @NikBearBrown corner bug; sha256 `efaeb6fd…af2527408`. The scene has no script or animation, so frames do not change.
- An earlier 450-frame take of the same scene was replaced because B07's narration measured 15.4 s.

## Student's own screenshots (labelled "Student's own screenshot" on screen)
From `D:/CSYE7270/assignment2/a3-evidence/`, placed unedited (scaled only) by `scripts/make_evidence.py`:

| File | Beat |
|---|---|
| 01-blender-window.png | B03 |
| 02-mcp-panel.png | B03 |
| 03-prompt-plan-cover-wall.png | B04 |
| 03b-cover-wall-result.png | B04 |
| 04-hedgehog-options.png | B10 |
| 05-hand-edit.png | B05 |
| 06-sidebar-4m.png | B05 |
| 06b-hand-edit-0.7mm-short.png | B05 |
| walker-TANK/design/test/play-01-normal-combat.png (A2) | B02 |

Full sha256:
```
c9087a23f682b5b48db2384d38093108d4c3fc3367e71ed366812d61c28b9887  01-blender-window.png
60a64dfff79dc183eb4ab4adb21e86f22f57c6114eb5d63a7516188fcf4bbaf6  02-mcp-panel.png
bca8c9a8fed303a71f00266e42aeb313e2af01d6a5a84674a77df595765d274d  03-prompt-plan-cover-wall.png
517d2816989cdc3c63c88922edacad762f1d1c35746f3cab27c64ff44ee55402  03b-cover-wall-result.png
e5b1289fb4f3bf3dc97a9af557fd802f702d25111c8b207472e525aab7679c5a  04-hedgehog-options.png
331f6d75f5f8a125cedbd383361e877cd460e413481123e81c120a747554540a  05-hand-edit.png
4dda399f19a1ee08477638d970acf95bdb5c3415ec4529af7696e74437fe4463  06-sidebar-4m.png
c62b22ef3de96d8fecda401247d89db3789ebd1d41d44fb601e05b47df50774e  06b-hand-edit-0.7mm-short.png
90a4e39eec2c23424ef28f2513eaddc5106ceb1f7370413add7d1b082a4b4813  play-01-normal-combat.png
```
Not used: 02b (consulted for the "off" values), 07-godot-top.png, 08-check-pass.png, 08b-fail-path-proven.png
(consulted; the film shows the re-run output instead).

## Rebuilt figure
`evidence/ev-headless.png` is a table typeset by `scripts/make_evidence.py` from `capture/check-stdout.txt` and the
brief's values; labelled HEADLESS and "recorded output".

## Reconstructions
- B00 Walker prompt: illustrative reconstruction (labelled), not the original chat.
- B06/B08 code panels: "Godot editor reconstruction", verbatim lines from hashed files (see gamedev-evidence.json).

## Voice, fonts, toolkit
Kokoro-82M (`kokoro-onnx`, Apache-2.0), voice `am_onyx`, local. faster-whisper `base.en` (local) for cue timing.
Fonts from `brutalist.art/runtime/fonts` (Inter, Lato, EB Garamond, PT Mono; OFL). Toolkit components:
ClaudeComposerAsk, BrutalistHesitantWriter, GodotDesignFigure, GodotDevWorkbench, ClaudeVerdictArtifact, ClaudeTitleOutro.
