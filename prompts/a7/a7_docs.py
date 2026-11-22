# A7 documentation (mine, drafted with Claude chat from this run's records).
# Appends the A7 sections; refuses to run twice. Run from the repository root.
import io

def read(p):
    return open(p, encoding="utf-8").read()

def write(p, s):
    open(p, "w", encoding="utf-8", newline="\n").write(s)

def append(p, marker, text):
    s = read(p)
    assert marker not in s, f"{p}: A7 section already present"
    write(p, s.rstrip("\n") + "\n\n" + text.strip("\n") + "\n")
    print("appended", p)

README = """
## Assignment 7 — animation

- **Added:** two animation clips on every tank, each driven by `scripts/tank.gd`'s state machine.
  - `track_dust`, the **cycle**: a 4-cell dust sheet (`assets/game/fx/track_dust_sheet.png`, made by `tools/make_dust_sheet.gd`) on a Sprite2D frame track in `animations/motion_clips.tres`, played by `MotionAnim` while the tank moves; 10 fps, looping.
  - `shoot`, the **committing action**: a cutout rig (`Suspension`, the new parent of hull and turret) baked by `tools/bake_tank_clips.gd` into `animations/fire_clips.tres`, played by `FireAnim` on each shot; 30 fps, startup 1 / active 1 / recovery 3 frames. The shell, muzzle flash and fire sound now come on frame 1 (2 physics ticks after the press), with the aim captured on the press.
- **Preview:** `previews/shoot_preview.tscn` (4× zoom, scripted input) for Movie Maker frame strips.
- **Run:** open the project in Godot 4.7.2 and press F5, or `"$GODOT" --path .`. Controls are unchanged (move with the movement keys, aim with the mouse, fire with Space).
- **Tests (Git Bash, repository root):** `bash scripts/run-test.sh <test> <fps>` for `test_clip_readback.gd 60`, `test_anim_states.gd 30|60|144`, `test_anim_edges.gd 30|60|144`, `test_pins.gd 60`, and every earlier suite in its mode (CLAUDE.md). Results: `TEST-REPORT.md`; tuning: `TUNING.md`.
- **Known limitations:** with the reload forced to 0 (tests only), a shot starting as the previous one ends does not replay `shoot`; unreachable in play (reload 48 ticks, clip 10). The shell leaves 1 physics tick before the clip reaches its frame-1 dip (not visible at 30 fps). Interrupts per phase are covered by the edge tests and the film's scripted captures, not by hand-timed play.

### Film (A7)

- **Watch:** [FILL_FILM_URL] — `claude-liam-walker-tank-a7-animation.mp4`
- **Length / size:** 3:51 (230.87 s), 3840×2160 landscape, 30 fps, 40,340,374 bytes
- **SHA-256:** `11ec29ec023f1a55cd9971c324626f799d5395058627cfe2d8bac223bdaa026a`
- **Revision shown:** `4f88f1b`. Later commits add documentation and film records only.
- Records (no media): `youtube/claude-liam-walker-tank-a7-animation/`; prompt: `prompts/a7/film-prompt.txt`.
- **My check:** I watched the whole final film and listened to the narration: "视频没有问题" (the video has no problems).
"""

FRICTIONAL = """
## Assignment 7 — animation

- **Login and account.** Step 1's first session failed before any work (`OAuth session expired`); I logged in again and reran it as session-1b. The first Step 5 run hit an individual spend limit after 22 turns because I was on the wrong account; I switched to my Northeastern account and reran the same prompt, which overwrote that log, and the rerun picked up the half-finished edits.
- **Permissions.** Several sessions had a Bash command refused because it did not match the allowed pattern; in Step 3 that meant the agent ran no tests and wrote an unrequested `logs/_run_all.sh`, which I deleted and ran the suites myself.
- **The agent did not run the suites it called safe.** Its plan said `test_hit_flash` and `test_cover_hit_burst_state` would survive; my full run found both failing. Fixes in TEST-REPORT.md.
- **A suggestion from Claude chat was wrong.** Reading the aim on frame 1 let the enemy AI re-aim during startup; reversed to capture the aim on the press tick.
- **Input latency.** `Input.parse_input_event` is buffered: 1 tick at 60/144, 2 ticks at `--fixed-fps 30`. The first pin run failed 4 of 10 and the first 30 fps state run failed 20 of 34 until the tests took the press tick from the game.
- **Floats and defaults.** Saved key times are 32-bit floats (`0.033333335`); `step` and `loop_mode` at their defaults are not written to the `.tres` at all.
- **A check that checked nothing.** I asked for `check_tools_parse.gd` to check the preview; it only loads three fixed tool scripts, and the agent said so.
- **My own quick answers.** I first said the dust was visible and the squash slight; looking again, the dust was not visible and the squash was clear. TUNING.md records both turns.
- **The dust fix nearly missed the film.** I launched the film at `392d1c4` before committing `DUST_BEHIND = 34`; `git status` showed the uncommitted file, I committed it and told the running film to switch to `4f88f1b` and redo its captures. Only one capture had started, and it had failed.
- **Film memory.** The 4K export peaked at 8.2 GB for ffmpeg, free RAM fell to 16 MB for a few seconds, and it still finished.
- **Changed games since Assignment 2:** no.
"""

SOURCES = """
## Assignment 7 — animation

- **Dust sheet:** `assets/game/fx/track_dust_sheet.png`, generated by `tools/make_dust_sheet.gd` (written by Claude in claude.ai chat, run by me). My own work; no third-party art. Credits: `assets/game/fx/ATTRIBUTION.md`.
- **Claude Code** (`claude -p`, prompts and transcripts in `prompts/a7/`): CLAUDE.md draft (session-1b), pins (2), node setup (3), wiring plan and implementation (5a, 5b), edge tests (6e), preview scene (7a).
- **Claude in claude.ai chat:** the bake tool, the sheet generator, the read-back test, the mutation, fix, re-pin, strip and measurement scripts in `prompts/a7/`; the brief's structure, wording and answers to its seven questions from my notes (provenance stated in CHANGE-BRIEF.md); strip measurements; these document drafts.
- **Me:** every design decision (clips, phase table, interrupts, tuning changes), every test run and capture, every human check, the review of CLAUDE.md and of each diff.
- **Film:** `claude-liam-walker-tank-a7-animation.mp4`, made by Claude Code in auto mode with the course-provided Brutalist toolkit, `godot-gamedev` skill, walker modifier, from revision `4f88f1b`; local narration; no paid media generation. Records: `youtube/claude-liam-walker-tank-a7-animation/`. I watched the whole final film: "视频没有问题" (the video has no problems).
"""

HEADLESS = [
    "- A headless run advances clips and reads their structure (tracks, keys, `step`, `loop_mode`, `current_animation`); it draws nothing, so it never shows whether motion reads.",
    "- Key times are saved as 32-bit floats (`0.033333335` in `animations/fire_clips.tres`): compare with half a frame period, never `==`.",
    "- `value_track_get_update_mode()` is asked only of value tracks (`tests/test_clip_readback.gd`).",
    "- `Input.parse_input_event` is buffered: the game sees an injected action 1 tick later at 60/144 and 2 ticks later at `--fixed-fps 30` (`tests/test_pins.gd` PIN-0, `tests/test_anim_states.gd`).",
    "- Frame strips come from a windowed Movie Maker run of `previews/shoot_preview.tscn`, which I start; it moves the real mouse.",
]

append("README.md", "## Assignment 7 — animation", README)
append("FRICTIONAL.md", "## Assignment 7 — animation", FRICTIONAL)
append("SOURCES.md", "## Assignment 7 — animation", SOURCES)

lines = read("CLAUDE.md").split("\n")
h = [i for i, l in enumerate(lines) if l.strip() == "## Headless facts"]
assert len(h) == 1, "Headless facts heading"
assert not any("32-bit floats" in l for l in lines), "CLAUDE.md already has the A7 lines"
nxt = next(i for i in range(h[0] + 1, len(lines)) if lines[i].startswith("## "))
while lines[nxt - 1].strip() == "":
    nxt -= 1
lines[nxt:nxt] = HEADLESS
write("CLAUDE.md", "\n".join(lines))
print("CLAUDE.md: 5 headless facts added")
