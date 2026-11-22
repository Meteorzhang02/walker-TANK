"""Author beat_sheet.json for claude-liam-walker-tank-a7-animation (film tooling).
Adapted from the A6 reel's make_sheet.py. Code excerpts are read verbatim, by line range, from the git-archive copy of
walker-TANK at revision 4f88f1b (_scratch/src). Figure images are embedded as data URIs. VIDEO beats point at
media/Bxx.mp4, built by scripts/make_media.py after the narration is measured. Measured audio fields are kept while the
narration is unchanged.
Run: python scripts/make_sheet.py
"""
import base64, io, json
from pathlib import Path
from PIL import Image

REEL = Path(__file__).resolve().parents[1]
GAME = REEL / "_scratch/src"          # git archive of walker-TANK 4f88f1b
REV = "4f88f1b"
TITLE = "Walker-TANK: Animation in Frames and Ticks"
SLUG = "claude-liam-walker-tank-a7-animation"
SRC = f"Source: walker-TANK revision {REV}"
KEEP = ("audio_file", "actual_duration_s", "tts_duration_s", "audio_pad", "render_duration_s", "build", "cue_times")


def excerpt(path, a, b):
    return "\n".join((GAME / path).read_text(encoding="utf-8").splitlines()[a - 1:b])


def line(path, n):
    return excerpt(path, n, n).strip()


def data_uri(rel, max_w=3400):
    im = Image.open(REEL / rel).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=93)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def composer(greeting, command, running, output, segment):
    return {"greeting": greeting, "topic": "GODOT · WALKER", "segment": segment, "command": command,
            "runningText": running, "folderLabel": "@NikBearBrown", "modelLabel": "Claude", "effortLabel": "High",
            "animateTyping": True, "largeText": True, "output": output}


def figure(title, status, image, cards, cue_spec, excerpt=""):
    return {"pattern": "GodotDesignFigure", "image_src": image, "cue_spec": cue_spec,
            "props": {"title": title, "status": status, "imageLabel": "", "excerpt": excerpt, "source": SRC,
                      "cards": [{"label": l, "text": t} for l, t in cards], "cues": [], "dense": False}}


def code(title, path, a, z, notes, cue_spec, label="Source notes — not Inspector values", size=30):
    return {"pattern": "GodotDevWorkbench", "code_src": (path, a, z), "cue_spec": cue_spec,
            "props": {"mode": "code", "title": title, "project": "walker-TANK",
                      "source": f"Godot editor reconstruction · {SRC} · {path} lines {a}–{z}",
                      "codeFontSize": size, "inspectorLabel": label,
                      "notes": [{"label": l, "value": v} for l, v in notes], "cues": [], "output": []}}


def video(source, provenance, *events):
    return {"type": "VIDEO", "class": "SHOW", "source": source, "show": show(*events), "provenance": provenance}


def show(*events):
    return [{"at": a, "event": e} for a, e in events]


MOTION, BAKE, TANK, BRIEF = ("animations/motion_clips.tres", "tools/bake_tank_clips.gd", "scripts/tank.gd",
                             "CHANGE-BRIEF.md")
PLAY = (f"Movie Maker 4K capture of the real scenes/main.tscn on a scratch copy of {REV}, driven by the film's "
        "_film/a7_play.gd with SCRIPTED INPUT (Input.action_press/release); enemies held (target = null)")

BEATS = [
    # 1 · Walker opening: the game and both clips
    dict(beat_id="B00", act="ASK", pattern="ClaudeComposerAsk",
         role_note="walker B00. Illustrative reconstruction of a Walker prompt; not the original chat.",
         narration_text="Hola, this is Liam, in for Bear. Assignment Seven gave walker tank two animation clips. "
                        "The prompt is reconstructed.",
         show=show(("0.02", "composer; greeting 'Hola, Liam'"), ("0.15", "Walker prompt types in"),
                   ("0.7", "result lines: reconstruction label, both clips, revision")),
         props=composer("Hola, Liam",
                        "Please use Walker to convert my game design document about walker-TANK — a 2D top-down tank "
                        "game in Godot 4.7.2, Forward+ — into two animation clips: a track-dust cycle and a "
                        "committing shoot action.",
                        "reading the change brief…",
                        ["Illustrative reconstruction, not a transcript.",
                         "track_dust · cycle · MotionAnim  ·  shoot · committing action · FireAnim",
                         f"walker-TANK · revision {REV}"], "walker-TANK · A7")),
    dict(beat_id="B01", act="BLUF", pattern="BrutalistHesitantWriter", lead_silence_s=0.8,
         role_note="walker B01: misconception corrected — animation as decoration -> animation as timing.",
         qc={"sparse_by_design": True, "sparse_reason": "hesitant writer types line by line"},
         narration_text="Dust behind the tracks says: driving. A dip says: the shot went. This animation isn't "
                        "decoration. It's timing, counted in ticks.",
         show=show(("0.0", "typing starts in the lead silence"), ("0.5", "'Animation is decoration.'"),
                   ("0.7", "word struck, 'timing' typed")),
         props={"contextTitle": "What was built",
                "text": "Dust says: driving.\nA dip says: fired.\nAnimation is decoration.",
                "triggerWords": "decoration", "replacementWords": "timing",
                "fontSize": 62, "lineSpacing": 2.6, "align": "center", "seed": "7270-a7-animation", "mistakeRate": 1,
                "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 6, "ink": "#3D3929", "accent": "#D97757",
                "bg": "#FAF9F5"}),
    # 2 · Clip 1, the cycle: what a clip is, the sheet, the frame track
    dict(beat_id="B02", act="CYCLE",
         role_note="Code beat: animations/motion_clips.tres lines 3-17 (the track_dust Animation), verbatim.",
         narration_text="What is a clip? An Animation resource of keyed tracks. Track dust, the cycle, is in motion "
                        "clips: one frame track on Dust, four keys, a tenth of a second apart. Length point four, "
                        "loop linear, discrete updates, step point one.",
         show=show(("0.0", "verbatim sub_resource, 15 lines"), ("Animation resource", "line 3"),
                   ("frame track", "line 10"), ("four keys", "line 14"), ("loop linear", "line 5"),
                   ("discrete", "line 16")),
         **code("Clip 1 · track_dust, the Cycle", MOTION, 3, 17,
                [("the sprite it drives · tank.gd 78–79", f"{line(TANK, 78)}\n{line(TANK, 79)}"),
                 ("brief · cycle spec", "4 cells · 10 fps\nkeys 0, 0.1, 0.2, 0.3 s")],
                [{"phrase": "Animation resource", "line": 3, "label": "a clip = an Animation resource of keyed tracks"},
                 {"phrase": "frame track", "line": 10, "label": "one value track: DustMount/Dust:frame"},
                 {"phrase": "four keys", "line": 14, "label": "keys at 0 / 0.1 / 0.2 / 0.3 s → cells 0, 1, 2, 3"},
                 {"phrase": "loop linear", "line": 5, "label": "loop_mode = 1 (LOOP_LINEAR) · length 0.4 s"},
                 {"phrase": "discrete", "line": 16, "label": "update = 1 (UPDATE_DISCRETE) · step 0.1 s"}],
                size=22)),
    dict(beat_id="B03", act="CYCLE", kind="capture", qc={"full_bleed": False},
         role_note="Result beat: the sheet (64x16, 4 cells) enlarged, beside the dust playing behind the hull in a "
                   "scripted-input capture, with the runtime readout of Dust.frame.",
         narration_text="The sheet: sixty four by sixteen pixels, four cells in one row. Driven right by scripted "
                        "input, the track reads those cells, ten a second, just behind the hull.",
         shot=video("film-capture (scripted input)", PLAY + "; scenario 'drive', frames 30-64 in order, cropped",
                    ("0.0", "left: track_dust_sheet.png enlarged 16x, cells 0-3 numbered"),
                    ("0.0", "right: 'scripted input' capture, cropped on the tank; readout Dust.frame"))),
    # 3 · Clip 2, the committing action
    dict(beat_id="B04", act="SHOOT",
         role_note="Code beat: tools/bake_tank_clips.gd lines 60-73 (_make_shoot), verbatim; fire_clips.tres in notes.",
         narration_text="Shoot is a cutout rig, baked from code. This tool writes fire clips. Suspension, the parent "
                        "of hull and turret, dips two pixels and squashes on frame one. Thirty frames a second, step "
                        "one thirtieth, loop none.",
         show=show(("0.0", "verbatim _make_shoot, lines 60-73"), ("cut out", "line 60"), ("Suspension", "line 69"),
                   ("two pixels", "line 72"), ("squashes", "line 73"), ("loop none", "line 66")),
         **code("Clip 2 · shoot, the Committing Action", BAKE, 60, 73,
                [("lines 22, 24", "DOWN_POS (0, 2)\nSQUASH (1.04, 0.96)"),
                 ("→ fire_clips.tres", "scale track: lines 74–79\nsquash on frame 1")],
                [{"phrase": "cut out", "line": 60, "label": "built in code, saved with ResourceSaver to fire_clips.tres"},
                 {"phrase": "Suspension", "line": 69, "label": "track 0: Suspension:position (parent of hull + turret)"},
                 {"phrase": "two pixels", "line": 72, "label": "frame 1: DOWN_POS = (0, 2), ease-out after"},
                 {"phrase": "squashes", "line": 73, "label": "back at rest on frame 5; scale track (74–79): SQUASH (1.04, 0.96) on frame 1"},
                 {"phrase": "loop none", "line": 66, "label": "step 1/30 · LOOP_NONE · length frame 5"}], size=22)),
    dict(beat_id="B05", act="SHOOT",
         role_note="Result beat: the phase table beside the baked key times, and the student's frame strip v1 "
                   "(FIXTURE) at each boundary.",
         narration_text="The phase table beside the baked keys: startup one frame, active one, recovery three. "
                        "Startup is one frame because the student wanted firing crisp. The strip, a fixture: dip "
                        "and squash peak on N plus one, with the shell and muzzle flash, and rest by N plus five.",
         **figure("Feel in Frames: Phase Table, Keys, Strip",
                  "Phase table: CHANGE-BRIEF.md lines 75–80 · keys: animations/fire_clips.tres · FIXTURE STRIP: captures/shoot_strip_v1.png (student's capture)",
                  "evidence/ev-phase.png",
                  [("Startup", "1 frame · key 0.0000 s"), ("Active", "1 frame · key 0.0333 s · shell"),
                   ("Recovery", "3 frames · 0.0667 → 0.1667 s"), ("Strip (FIXTURE)", "peak N+1 · rest by N+5")],
                  [{"phrase": "start up", "card": 0}, {"phrase": "active", "card": 1},
                   {"phrase": "recovery", "card": 2}, {"phrase": "strip", "card": 3}])),
    # 4 · One authority, two clocks
    dict(beat_id="B06", act="AUTHORITY",
         role_note="Code beat: scripts/tank.gd lines 88-101 (Suspension above hull/turret; both AnimationPlayers on "
                   "the physics clock), verbatim; the brief's authority table in notes.",
         narration_text="One authority per animated node, from the brief's table. Dust frame: only MotionAnim. "
                        "Suspension: only FireAnim. Hull and turret position: only tank dot g d, every tick. That's "
                        "why Suspension sits above them. And both players run on the physics clock.",
         show=show(("0.0", "verbatim tank.gd 88-101"), ("Dust frame", "line 97"), ("Suspension only", "line 100"),
                   ("Hull", "line 88"), ("above", "line 92"), ("physics", "line 96")),
         **code("One Authority, Two Clocks", TANK, 88, 101,
                [("brief lines 41–44 · only writer", "Dust.frame: MotionAnim\nSuspension: FireAnim\nhull, turret: tank.gd"),
                 ("tank.gd 180–181", "hull/turret.position\nwritten every tick")],
                [{"phrase": "Dust frame", "line": 97, "label": "Dust.frame: written only by MotionAnim (motion_clips)"},
                 {"phrase": "Suspension only", "line": 100, "label": "Suspension position + scale: only FireAnim (fire_clips)"},
                 {"phrase": "Hull", "line": 88, "label": "hull, turret: position written by tank.gd every tick"},
                 {"phrase": "above", "line": 92, "label": "hull and turret are children of Suspension (lines 84–92)"},
                 {"phrase": "physics", "line": 96, "label": "ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS (both players, 96 + 102)"}],
                size=22)),
    dict(beat_id="B07", act="AUTHORITY", kind="capture", qc={"full_bleed": False},
         role_note="Result beat: scripted-input capture, drive -> stop -> fire at normal speed, runtime readout.",
         narration_text="In the running game, scripted input. Driving: MotionAnim plays track dust, and the dust "
                        "shows behind the hull. Stopped: the clip stops, the dust is gone. Then fire: the tank sits "
                        "down and springs back.",
         shot=video("film-capture (scripted input)", PLAY + "; scenario 'drive', frames 14-119 in order, normal speed",
                    ("0.0", "scripted input capture with runtime readout"),
                    ("Driving", "MOVING, track_dust, DustMount.visible true"), ("Stopped", "IDLE, stopped, hidden"),
                    ("fire", "FIRING, Suspension y 2.00 on N+1"))),
    dict(beat_id="B08", act="CLOCKS",
         role_note="Code beat: scripts/tank.gd lines 207-219 (_weapon_tick), verbatim.",
         narration_text="The second clock. The shell doesn't come from the clip. It comes from a physics tick "
                        "counter in weapon tick: on tick two, frame one, the shell, the muzzle flash and the sound. "
                        "On tick ten, ready again.",
         show=show(("0.0", "verbatim _weapon_tick"), ("counter", "line 210"), ("shell", "line 213"),
                   ("ready", "line 218")),
         **code("The Shell Comes from a Tick Counter", TANK, 207, 219,
                [("_ticks_for_frame · line 185", "frame × ticks/s ÷ 30"),
                 ("at 60 ticks/s", "frame 1 = tick 2\nframe 5 = tick 10")],
                [{"phrase": "counter", "line": 210, "label": "_fire_ticks: physics ticks since the press tick"},
                 {"phrase": "muzzle", "line": 213, "label": "tick 2 (frame 1): shell, muzzle FX, fire sound, fired"},
                 {"phrase": "ready", "line": 218, "label": "tick 10 (frame 5): weapon READY"}], size=28)),
    dict(beat_id="B09", act="CLOCKS", kind="capture", qc={"full_bleed": False},
         role_note="Result beat: one shot from the scripted-input capture, frames N-1..N+5 held (slowed), readout "
                   "beside the measured C1 numbers.",
         narration_text="Held frame by frame. The shell leaves on P plus two. The clip reaches frame one on P plus "
                        "three. One tick apart, zero point zero one six seven seconds, measured by check C1 at all "
                        "three rates.",
         shot=video("film-capture (scripted input), held frames", PLAY + "; scenario 'hits', frames 29-36, each held 24 frames",
                    ("0.0", "HELD FRAMES label; readout ticks since press and FireAnim position"),
                    ("C1", "side panel: P+2 shell, P+3 frame 1, 0.0167 s, 30/60/144"))),
    # 5 · State machine in play
    dict(beat_id="B10", act="STATES", kind="capture", qc={"full_bleed": False},
         role_note="Interrupts in play: scripted hits in startup, active and recovery; a second fire in FIRING.",
         narration_text="Interrupts, with scripted input and scripted hits. A hit in startup, in active, in "
                        "recovery: the shot still goes. A second fire during firing is ignored: no new shell.",
         shot=video("film-capture (scripted input + scripted hits)", PLAY + "; scenario 'hits', four shots, slowed by held frames",
                    ("0.0", "four labelled panels: hit tick 1, hit tick 2, hit tick 5, second press tick 4"))),
    dict(beat_id="B11", act="STATES", kind="capture", qc={"full_bleed": False},
         role_note="Deaths in play: take_damage(100000) on ticks 1, 2 and 5, one capture each.",
         narration_text="And a death in each phase. The tank dies, but the committed shot finishes: one shell, then "
                        "ready on tick ten.",
         shot=video("film-capture (scripted input + scripted deaths)", PLAY + "; scenarios death_s, death_a, death_r",
                    ("0.0", "three panels side by side, held frames"))),
    # 6 · What the read-backs proved
    dict(beat_id="B12", act="TESTS",
         role_note="Recorded headless results at 4f88f1b: readback 49, anim_states 34, edges 27, pins 11.",
         narration_text="The read-backs. Clip read back: forty nine checks. States: thirty four, at thirty, sixty and "
                        "one forty four. The new edge test: every boundary, with a hit, a death and a second fire, a "
                        "tick before, on and after: twenty seven, at all three. Pins: eleven. Only one, two and four "
                        "moved, two ticks, as predicted.",
         **figure("What the Read-backs Proved",
                  "HEADLESS · the student's recorded logs at 4f88f1b · nothing drawn",
                  "evidence/ev-tests.png",
                  [("Read-back", "49 / 49"), ("States", "34 / 34 at 30 · 60 · 144"),
                   ("Edges", "27 / 27 at 30 · 60 · 144"), ("Pins", "11 / 11 · PIN-1/2/4 +2 ticks")],
                  [{"phrase": "read back", "card": 0}, {"phrase": "States", "card": 1},
                   {"phrase": "edge", "card": 2}, {"phrase": "Pins", "card": 3}])),
    dict(beat_id="B13", act="TESTS",
         role_note="Mutations from logs/a7-mutations.txt, each in a git worktree; the C1 blind spot; headless limit.",
         narration_text="Mutations, each in a worktree. Frame renamed frames, loop flipped, a key on cell four: all "
                        "caught. An empty cache reimport passed, as expected: a baked rig has no importer. Continuous "
                        "track, shell on frame two: caught. The blind spot: C1 checks only the size of the gap, so a "
                        "flipped sign passed. And headless can't show whether motion reads.",
         **figure("Mutations and the Blind Spot",
                  "logs/a7-mutations.txt · each mutation in its own git worktree, control passes first · HEADLESS",
                  "evidence/ev-mutations.png",
                  [("Assignment list", "3 caught · reimport: pass"), ("Extra", "continuous · frame 2: caught"),
                   ("Blind spot", "C1 checks |shell − clip| only"), ("Headless", "can't show if it reads")],
                  [{"phrase": "Mutations", "card": 0}, {"phrase": "Continuous", "card": 1},
                   {"phrase": "blind spot", "card": 2}, {"phrase": "headless", "card": 3}])),
    # 7 · Strip readings
    dict(beat_id="B14", act="READINGS",
         role_note="Strip readings: v1 squash (Claude vs the student), dust strips v1-v3, TUNING.md revisions 1 and 2.",
         narration_text="Reading the strips. Claude measured the squash at about five percent: slight. The student "
                        "looked carefully, judged it clearly visible, and kept it. For dust, the student saw v2 "
                        "faintly; Claude found no dust pixels. V3 moved it thirty four pixels back, and it shows, in "
                        "all eight facings.",
         **figure("Reading the Strips",
                  "FIXTURE STRIPS (student's captures): shoot_strip_v1, dust_strip_v1–v3 · TUNING.md revisions 1, 2",
                  "evidence/ev-dust.png",
                  [("Squash v1", "Claude ≈ 5 %, slight"), ("The student", "clearly visible · kept"),
                   ("Dust v2", "faint? · 0 dust pixels"), ("Dust v3", "DUST_BEHIND 34 · all 8 facings")],
                  [{"phrase": "squash", "card": 0}, {"phrase": "carefully", "card": 1},
                   {"phrase": "no dust", "card": 2}, {"phrase": "eight", "card": 3}])),
    # 8 · Verdict -> Your Turn -> outro
    dict(beat_id="B15", act="VERDICT", pattern="ClaudeVerdictArtifact",
         role_note="Verdict: agent mistakes caught, uncertainty, next step, contributions, sheet source, revision.",
         narration_text="The verdict, at revision four f eight eight f one b. The student caught two failing tests "
                        "the agent never ran, an unrequested script, a dust guess hidden under the hull, and a parse "
                        "check that never loads the preview. Uncertain: at thirty f p s, second presses land on even "
                        "ticks only; and with reload forced to zero, a shot on P plus ten doesn't replay the clip, "
                        "which play can't reach. Next: replay shoot on every new shot.",
         show=show(("0.05", "verdict page"), ("0.12", "agent mistakes caught"), ("0.5", "uncertain"),
                   ("0.75", "next step"), ("0.85", "who did what, sheet source, revision")),
         props={"artifactTitle": "Verdict", "artifactHeading": f"walker-TANK A7 · revision {REV}",
                "brandLabel": "@NikBearBrown",
                "artifactLines": [
                    "Caught: the agent said test_hit_flash and test_cover_hit_burst_state would survive and didn't run them; both failed. Fixed: fired with the shell, aim on the press tick, the frozen enemy runs.",
                    "Also: an unrequested logs/_run_all.sh (deleted) · DUST_BEHIND 14 hid the dust · check_tools_parse never loads the preview.",
                    "Uncertain: at 30 fps a 2nd press lands on even ticks only (P+9, P+11 missed) · reload 0: a shot on P+10 doesn't replay shoot (unreachable: reload 48 > clip 10 ticks).",
                    "Next step: make shoot replay from its start whenever a new shot starts.",
                    "The student: design, every test, capture and human check · Claude Code: CLAUDE.md, pins, nodes, wiring, preview · Claude chat: sheet generator, bake tool, read-back, mutation and fix scripts, brief wording.",
                    "Sheet: made by code (tools/make_dust_sheet.gd), the student's own work, no third-party art."]}),
    dict(beat_id="B16", act="HANDOFF", pattern="ClaudeComposerAsk",
         role_note="HANDOFF: prompt read aloud; Liam signs off here.",
         narration_text="Your turn. Please use Walker to add one animation clip to my game. Write its phase table "
                        "first, predict one frame of the strip, then check it in play. Liam, in for Bear.",
         show=show(("0.02", "composer; greeting 'Your turn.'"), ("0.08", "prompt types while read aloud")),
         props=composer("Your turn.",
                        "Please use Walker to add one animation clip to my game. Write its phase table first, predict "
                        "one frame of the strip, then check it in play.",
                        "paste this into Claude…", [], "Your walker game")),
    dict(beat_id="B17", act="OUTRO", pattern="ClaudeTitleOutro", kind="outro_voice", tail_hold_s=1.0,
         role_note="OUTRO-LOCK: spoken, never scored; 1.0 s silent tail.",
         narration_text=f"{TITLE}. At Nik Bear Brown.",
         show=show(("0.0", "exact title, @NikBearBrown, slug-seeded mascot, no subline")),
         props={"title": TITLE, "slug": SLUG}),
]

OUTPUT = {"B02": ["Seam: last key 0.3 s, length 0.4 s, no repeated cell"],
          "B08": ["Measured by check C1: shell P+2, clip frame 1 P+3."],
          "B06": ["tank.gd writes hull/turret every tick; FireAnim gets Suspension"]}
for _spec in BEATS:
    _spec["output"] = OUTPUT.get(_spec["beat_id"], [])


def build():
    sp = REEL / "beat_sheet.json"
    old = {b["beat_id"]: b for b in json.loads(sp.read_text(encoding="utf-8"))["beats"]} if sp.exists() else {}
    beats = []
    for spec in BEATS:
        b = {k: v for k, v in spec.items() if k not in ("code_src", "image_src", "cue_spec", "props", "pattern", "show", "output")}
        b.update(voice="am_onyx", engine="kokoro")
        if "pattern" in spec:
            b["pattern"] = spec["pattern"]
            props = json.loads(json.dumps(spec["props"]))
            shot = {"type": "GRAPHIC", "class": "SHOW", "source": "remotion", "show": spec.get("show", [])}
            if "code_src" in spec:
                path, a, z = spec["code_src"]
                props.update(code=excerpt(path, a, z), path=f"res://{path}", startLine=a)
            if "image_src" in spec:
                props["image"] = data_uri(spec["image_src"])
                shot["evidence_media"] = spec["image_src"]
            if spec.get("output"):
                props["output"] = spec["output"]
            shot["remotion"] = {"pattern": spec["pattern"], "props": props}
            b["shot"] = shot
        else:
            b["shot"]["evidence_media"] = f"media/{b['beat_id']}.mp4"
        prev = old.get(b["beat_id"])
        if prev and prev.get("narration_text") == b["narration_text"]:
            for k in KEEP:
                if k in prev:
                    b[k] = prev[k]
        if "cue_spec" in spec:
            b["cue_spec"] = spec["cue_spec"]
            if "cue_times" in b:
                b["shot"]["remotion"]["props"]["cues"] = b["cue_times"]
        dur = b.get("actual_duration_s")
        if dur and "remotion" in b["shot"]:
            b["shot"]["remotion"]["props"]["durationSeconds"] = dur
        beats.append(b)
    meta = {"title": TITLE, "slug": SLUG, "topic": "GODOT · WALKER · GAMEDEV", "kind": "gamedev", "mode": "walker",
            "brand": "claude-liam", "audience": "CSYE7270 students adding animation clips to small games with Walker + Claude Code",
            "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
            "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9",
            "fit": "contain", "captions": False, "channel": "@NikBearBrown", "channel_title": "@NikBearBrown",
            "folderLabel": "@NikBearBrown", "greeting": "Hola, Liam", "persona": "Liam (in for Bear)",
            "presenter": "Liam (in for Bear)", "in_for_bear": True, "fps": 30,
            "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-TANK", "path": "D:/CSYE7270/assignment2/walker-TANK",
                     "revision": REV, "game_source_revision": REV,
                     "checked_copy": f"_scratch/src (git archive {REV})",
                     "engine": "Godot 4.7.2.stable.official.ed1daf0bf"},
            "note": "godot-gamedev walker mode, assignment-focused film (A7 animation only). New 4K scripted-input "
                    "captures on a scratch copy only; the student's own fixture strips; no paid API, no upload, no game change."}
    if sp.exists():
        prev_meta = json.loads(sp.read_text(encoding="utf-8")).get("metadata", {})
        if "build" in prev_meta:
            meta["build"] = prev_meta["build"]
    sp.write_text(json.dumps({"metadata": meta, "beats": beats}, ensure_ascii=False, indent=1), encoding="utf-8")
    words = sum(len(b["narration_text"].split()) for b in beats)
    print("wrote", sp, len(beats), "beats;", words, "words")


if __name__ == "__main__":
    build()
