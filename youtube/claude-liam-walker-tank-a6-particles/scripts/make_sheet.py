"""Author beat_sheet.json for claude-liam-walker-tank-a6-particles (film tooling).
Adapted from the A5 reel's make_sheet.py. Code excerpts are read verbatim, by line range, from the git-archive copy of
walker-TANK at commit 41a6b8b (_scratch/src). Figure images are embedded as data URIs. VIDEO beats point at media/Bxx.mp4,
built by scripts/make_media.py after the narration is measured. Measured audio fields are kept while narration is unchanged.
Run: python scripts/make_sheet.py
"""
import base64, io, json
from pathlib import Path
from PIL import Image

REEL = Path(__file__).resolve().parents[1]
GAME = REEL / "_scratch/src"          # git archive of walker-TANK 41a6b8b
REV, GAME_REV = "41a6b8b", "96d38be"
TITLE = "Walker-TANK: Particles, Strips and the Game"
SLUG = "claude-liam-walker-tank-a6-particles"
SRC = f"Source: walker-TANK commit {REV} (game source last changed at {GAME_REV})"
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


SMOKE, BURST, GEN, COVER = ("effects/damage_smoke.tscn", "effects/cover_hit_burst.tscn",
                            "shaders/particles_generated.gdshader", "scripts/cover.gd")
PLAY = "D:/CSYE7270/a6-play.mp4 (the student's own play recording, 1280×720, 48 fps)"
FIX = "Movie Maker 4K fixture capture of a walker-TANK preview scene, made by this film on a scratch copy of 41a6b8b"

BEATS = [
    # 1 · Walker opening
    dict(beat_id="B00", act="ASK", pattern="ClaudeComposerAsk",
         role_note="walker B00. Illustrative reconstruction of a Walker prompt; not the original chat.",
         narration_text="Hola, this is Liam, in for Bear. Assignment Six gave walker tank two particle effects. "
                        "The prompt on screen is a reconstruction.",
         show=show(("0.02", "composer; greeting 'Hola, Liam'"), ("0.15", "Walker prompt types in"),
                   ("0.7", "result lines: reconstruction label, both effects, revision")),
         props=composer("Hola, Liam",
                        "Please use Walker to convert my game design document about walker-TANK — a 2D top-down tank "
                        "battle — into two particle effects: a burst where a shell hits cover, and damage smoke that "
                        "follows each tank's health.",
                        "reading the change brief…",
                        ["Illustrative reconstruction, not a transcript.",
                         "A: cover hit burst · 3 × CPUParticles2D · B: damage smoke · GPUParticles2D",
                         f"walker-TANK · commit {REV}"], "walker-TANK · A6")),
    dict(beat_id="B01", act="BLUF", pattern="BrutalistHesitantWriter", lead_silence_s=0.8,
         role_note="walker B01: misconception corrected — particles as decoration -> each effect carries one message.",
         qc={"sparse_by_design": True, "sparse_reason": "hesitant writer types line by line"},
         narration_text="A shell hits a wall. A tank gets hurt. Particles aren't decoration here. Each effect carries "
                        "one message.",
         show=show(("0.0", "typing starts in the lead silence"), ("0.5", "'Particles are decoration.'"),
                   ("0.7", "word struck, 'messages' typed")),
         props={"contextTitle": "What was built",
                "text": "A shell hits a wall.\nA hurt tank smokes.\nParticles are decoration.",
                "triggerWords": "decoration", "replacementWords": "messages",
                "fontSize": 62, "lineSpacing": 2.6, "align": "center", "seed": "7270-a6-particles", "mistakeRate": 1,
                "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 6, "ink": "#3D3929", "accent": "#D97757",
                "bg": "#FAF9F5"}),
    dict(beat_id="B02", act="EFFECTS", kind="capture", qc={"full_bleed": False},
         role_note="Both effects as 4K fixture captures, side by side, with their jobs, events and conditions.",
         narration_text="Effect A, the cover hit burst, says: your shell landed on that wall, right there. Three CPU "
                        "emitters, fired from take hit, line forty. Effect B, damage smoke, says: this tank is badly "
                        "hurt, and how badly.",
         shot=video("film-fixture-capture", FIX + "; burst_single (60 frames) and smoke (170 frames); see SOURCES.md",
                    ("0.0", "two labelled FIXTURE panels: A (burst, loops) and B (smoke)"),
                    ("Effect A", "A's job, event cover.gd take_hit() line 40"),
                    ("Effect B", "B's job, condition h <= 0.6, amount_ratio follows health, wreck 1.0"))),
    # 2 · Three parts of a particle system
    dict(beat_id="B03", act="PARTS",
         role_note="Code beat: effects/damage_smoke.tscn lines 47-58 (the GPUParticles2D node), verbatim; process lines 30-32 and draw lines 4/7 in notes.",
         narration_text="Every particle system has three parts. Emission: amount forty eight, lifetime one point six. "
                        "Process: initial velocity, and gravity up the screen, which Godot turns into shader lines. "
                        "Draw: a soft dot texture, blend mix, and a visibility rect.",
         show=show(("0.0", "verbatim node block, 12 lines"), ("Emission", "line 50 lit"), ("lifetime", "line 54"),
                   ("Process", "line 52, notes: lines 30/32 -> shader 232, 412/425"), ("Draw", "line 53"),
                   ("visibility", "line 58")),
         **code("Emission, Process, Draw", SMOKE, 47, 58,
                [("process · lines 30, 32", f"{line(SMOKE, 30)}\n{line(SMOKE, 32)}\n→ shader 232, 412 / 425"),
                 ("draw · lines 4, 7", "soft_dot_32.png\n" + line(SMOKE, 7) + " (MIX)")],
                [{"phrase": "Emission", "line": 50, "label": "emission: amount = 48"},
                 {"phrase": "lifetime", "line": 54, "label": "emission: lifetime = 1.6"},
                 {"phrase": "Process", "line": 52, "label": "process: the ParticleProcessMaterial"},
                 {"phrase": "Draw", "line": 53, "label": "draw: texture soft_dot_32.png"},
                 {"phrase": "visibility", "line": 58, "label": "draw: visibility_rect"}], size=24)),
    dict(beat_id="B04", act="PARTS", kind="capture", qc={"full_bleed": False},
         role_note="Result beat: the smoke preview as a 4K fixture on the RTX 3060, plus the recorded headless price.",
         narration_text="Here it runs on the GPU, in a fixture. Headless, it costs about nothing, because the dummy "
                        "renderer runs no GPU particle process. GPU time there reads zero.",
         shot=video("film-fixture-capture", FIX + "; smoke, frames 0-169 in order; headless numbers from logs/price_measure_realtime.log",
                    ("0.0", "FIXTURE smoke capture, side panel: headless B -0.009 ms, render_gpu 0.000"))),
    # 3 · Effect A
    dict(beat_id="B05", act="EFFECT A",
         role_note="Effect A intent block, r0 strip (fixture, as captured), the student's first look and game verdict.",
         narration_text="Effect A's intent: gone in about point seven seconds. Here's the r0 strip, a fixture. The "
                        "student's first look: readable. And in the game, nothing to change.",
         **figure("Effect A: Intent, Strip, First Look",
                  "FIXTURE STRIP r0 (student's capture) · intent from CHANGE-BRIEF.md · quotes from TUNING.md",
                  "evidence/ev-a-intent.png",
                  [("Intent", "≈ 0.7 s · flash, fan, fade"), ("r0 strip", "frames 10–50 · fixture"),
                   ("First look", "readable, size right"), ("In the game", "nothing to change")],
                  [{"phrase": "intent", "card": 0}, {"phrase": "strip", "card": 1},
                   {"phrase": "first look", "card": 2}, {"phrase": "in the game", "card": 3}])),
    dict(beat_id="B06", act="EFFECT A",
         role_note="Code beat: effects/cover_hit_burst.tscn lines 24-26 (Debris colour ramp after R3), verbatim.",
         narration_text="So A's revision was strip driven. Claude saw the chips vanish by frame twenty: their last "
                        "colour, five A three A two E, had about the ground's value. R3 adds an opaque brown stop at point six, "
                        "and predicts visible chips at frame twenty.",
         show=show(("0.0", "verbatim Gradient_debris, 3 lines"), ("last", "line 26 lit"), ("R3", "line 25 lit")),
         **code("Effect A: The Revision (R3)", BURST, 24, 26,
                [("was (r0)", "#E8D8B0 a1 @0 → #B5523A a1 @0.3\n→ #5A3A2E a0 @1"),
                 ("now (R3)", "… → #8E5040 a1 @0.6 → #8E5040 a0 @1")],
                [{"phrase": "last", "line": 26, "label": "colours: the last stop was #5A3A2E, about the ground's value"},
                 {"phrase": "R3", "line": 25, "label": "offsets: R3 adds a stop at 0.6 (#8E5040, opaque)"}], size=26)),
    dict(beat_id="B07", act="EFFECT A",
         role_note="Result beat: r0 vs r1 frame 20 (the student's fixture strips), Claude's comparison, the verdict.",
         narration_text="Frame twenty, before and after. Claude: partly held, the chips are faint. The student kept "
                        "r1, and declined Claude's next lever, chip size.",
         **figure("Effect A: Frame 20, r0 and r1",
                  "FIXTURE STRIPS r0 / r1 (student's captures, same seed) · enlarged 3× · comparison and verdict from TUNING.md",
                  "evidence/ev-a-frame20.png",
                  [("r0", "chips gone into the ground"), ("r1", "faint chips, ~80 px out"),
                   ("Claude", "prediction partly held"), ("Verdict", "kept r1, lever declined")],
                  [{"phrase": "before", "card": 0}, {"phrase": "after", "card": 1},
                   {"phrase": "partly", "card": 2}, {"phrase": "kept", "card": 3}])),
    dict(beat_id="B08", act="EFFECT A", kind="capture", qc={"full_bleed": False},
         role_note="Effect A in play: the student's own recording (repeated hits on one wall), beside the retrigger fixture.",
         narration_text="In the student's play recording: three hits on one wall, each its own burst. On the right, a "
                        "fixture with retrigger on. The second burst doesn't restart the first.",
         shot=video("student-screen-recording + film-fixture-capture",
                    PLAY + ", from 12.0 s, frames in order; and the burst_retrigger fixture (loops)",
                    ("0.0", "left: 'my play recording'; right: FIXTURE retrigger"),
                    ("three hits", "hits at about 13.3, 14.3 and 15.0 s on one wall"))),
    # 4 · Effect B
    dict(beat_id="B09", act="EFFECT B",
         role_note="Effect B intent block, turbulence (the feature A doesn't use), r0 strip, the in-game observation.",
         narration_text="Effect B should rise as a wavering column, using turbulence, which A doesn't use. The r0 "
                        "strip. But in the game, the student saw a lump on the turret.",
         **figure("Effect B: Intent, Turbulence, a Lump",
                  "FIXTURE STRIP r0 (student's capture) · intent from CHANGE-BRIEF.md · observation from TUNING.md",
                  "evidence/ev-b-intent.png",
                  [("Intent", "a rising, wavering column"), ("Only in B", "turbulence (GPU-only)"),
                   ("r0 strip", "frames 10–165 · fixture"), ("In the game", "一团 · a lump")],
                  [{"phrase": "column", "card": 0}, {"phrase": "turbulence", "card": 1},
                   {"phrase": "strip", "card": 2}, {"phrase": "lump", "card": 3}])),
    dict(beat_id="B10", act="EFFECT B",
         role_note="Code beat: effects/damage_smoke.tscn lines 28-34 (process: direction to damping), verbatim; R5 in notes.",
         narration_text="Claude's reading: the brief's own values carry a puff only about fifty nine pixels. So R5 "
                        "raises initial velocity from twenty and forty, to fifty and eighty, predicting a thin column.",
         show=show(("0.0", "verbatim process lines 28-34"), ("fifty nine", "line 32 lit"), ("initial velocity", "line 30 lit"),
                   ("eighty", "line 31 lit")),
         **code("Effect B: The Revision (R5)", SMOKE, 28, 34,
                [("Claude's reading of r0 (session 7a)", "20–40 px/s, gravity −15, damping 5–8:\na mean puff rises only ~59 px in 1.6 s"),
                 ("R5 (brief revision)", "initial_velocity_min / max\n20 / 40 → 50 / 80 px/s")],
                [{"phrase": "fifty nine", "line": 32, "label": "gravity (0, −15): buoyancy, weak against damping"},
                 {"phrase": "initial velocity", "line": 30, "label": "R5: initial_velocity_min 20 → 50"},
                 {"phrase": "eighty", "line": 31, "label": "R5: initial_velocity_max 40 → 80"}], size=30)),
    dict(beat_id="B11", act="EFFECT B", kind="capture", qc={"full_bleed": False},
         role_note="Result beat: r0/r1 frames 58 and 140 (student's fixture strips) beside the student's play recording of the smoke.",
         narration_text="Frames fifty eight and one forty, before and after. Claude: prediction failed, still a lump. "
                        "In the game, the student saw it rise, and kept it. Here the student overruled Claude's "
                        "reading of the strip.",
         shot=video("student-fixture-strips + student-screen-recording",
                    "captures/damage_smoke/r0, r1 frames 58 and 140 (fixture); " + PLAY + ", from 29.0 s, frames in order",
                    ("0.0", "left: 2×2 FIXTURE stills; right: 'my play recording' with smoke rising"),
                    ("prediction failed", "Claude's comparison label"), ("overruled", "verdict label"))),
    dict(beat_id="B12", act="EFFECT B", kind="capture", qc={"full_bleed": False},
         role_note="Start, stop and pause: state-test results and the student's game checks, over the pause in the play recording.",
         narration_text="Start, stop and pause passed the state test at thirty, sixty and one forty four frames per "
                        "second. In the game: denser per hit, a trail, frozen under pause, and a smoking wreck.",
         shot=video("student-screen-recording", PLAY + ", from 39.4 s, frames in order (paused 40-43 s, smoke frozen)",
                    ("0.0", "left: 'my play recording' with pause; right: state results and game checks"))),
    # 5 · The generated process shader
    dict(beat_id="B13", act="SHADER",
         role_note="Code beat: shaders/particles_generated.gdshader lines 443-447, verbatim; line 232 in the notes.",
         narration_text="The generated process shader. Line two thirty two picks each start speed between fifty and "
                        "eighty. Line four forty seven is turbulence: every step, the velocity turns ten to twenty "
                        "percent toward the noise.",
         show=show(("0.0", "verbatim lines 443-447; line 232 in the notes"), ("two thirty two", "notes panel: line 232 <-> 50/80"),
                   ("four forty seven", "line 447 lit"), ("noise", "line 443 lit")),
         **code("The Generated Process Shader", GEN, 443, 447,
                [("line 232 ↔ min / max 50 / 80 (R5)",
                  "mix(initial_linear_velocity_min,\ninitial_linear_velocity_max, …)"),
                 ("line 447 ↔ influence 0.1 / 0.2", "10–20 % per step")],
                [{"phrase": "four forty seven", "line": 447, "label": "line 447: blend 10–20 % toward the noise, every step"},
                 {"phrase": "noise", "line": 443, "label": "line 443: the noise direction at the particle's position"}],
                label="Source lines (verbatim) beside the brief settings", size=26)),
    dict(beat_id="B14", act="SHADER", kind="capture", qc={"full_bleed": False},
         role_note="Result beat: the smoke fixture enlarged on the turret, puffs wandering instead of rising.",
         narration_text="After about a second, little of the upward heading is left. That's the lump. Confirmed from "
                        "the code, not yet by a turbulence off strip.",
         shot=video("film-fixture-capture", FIX + "; smoke, frames 60-169 in order, cropped on the turret, enlarged",
                    ("0.0", "FIXTURE, enlarged: puffs wander around the turret"))),
    # 6 · Tests
    dict(beat_id="B15", act="TESTS",
         role_note="Recorded headless results (TEST-REPORT.md, logs/), mutations, overlap, and the headless limit.",
         narration_text="Tests. Config: one twenty eight, and seventy six. A Godot three property name: exit one, "
                        "though Godot ignored it silently. A damping drift: exit one. State: eighty two and eighty "
                        "one. Headless can't show anything drawn.",
         **figure("What the Tests Proved",
                  "HEADLESS · recorded logs and the student's own exit codes · nothing drawn",
                  "evidence/ev-tests.png",
                  [("Config", "128/128 · 76/76"), ("Mutations", "2 × exit 1"),
                   ("State", "82 · 81 at 30/60/144"), ("Headless", "can't show drawing")],
                  [{"phrase": "Config", "card": 0}, {"phrase": "Godot three", "card": 1},
                   {"phrase": "State", "card": 2}, {"phrase": "drawn", "card": 3}])),
    # 7 · Prices
    dict(beat_id="B16", act="PRICES",
         role_note="Prices against the budget, from logs/price_measure_realtime.log and _windowed.log.",
         narration_text="Prices. Headless CPU: A, plus point zero seven four milliseconds, budget point five. B, about "
                        "zero. GPU time on the RTX 3060: A, plus point zero two three. B, plus point zero seven seven. "
                        "All inside budget.",
         **figure("Prices Against the Budget",
                  "MEASURED · price_measure.gd (Claude chat), run by the student · medians · two mode-0 runs as drift",
                  "evidence/ev-prices.png",
                  [("CPU · A", "+0.074 ms (≤ 0.5)"), ("CPU · B", "−0.009 ≈ 0"),
                   ("GPU · A / B", "+0.023 / +0.077"), ("Drift", "0.020 / 0.005")],
                  [{"phrase": "Headless", "card": 0}, {"phrase": "about zero", "card": 1},
                   {"phrase": "GPU", "card": 2}, {"phrase": "budget", "card": 3}])),
    dict(beat_id="B17", act="PRICES", kind="capture", qc={"full_bleed": False},
         role_note="The price scene as a 4K fixture, modes switched by scripted key events (1, then 3); the agent's cost-script mistake.",
         narration_text="The agent's first cost script read six point nine milliseconds everywhere, even the empty "
                        "scene. That's one over one forty four: it measured itself, and the control caught it. FPS read "
                        "one forty three to one forty four in every mode, and one forty three with vsync off. Capped.",
         shot=video("film-fixture-capture", FIX + "; price_scene, key 1 at frame 30 and key 3 at frame 240, frames in order",
                    ("0.0", "FIXTURE price scene, mode 1 then mode 3; FPS label covered and explained"))),
    # 8 · Verdict -> Your Turn -> outro
    dict(beat_id="B18", act="VERDICT", pattern="ClaudeVerdictArtifact",
         role_note="Verdict: mistakes caught both ways, the overruled reading, uncertainty, next step, contributions, textures, revision.",
         narration_text="The verdict, at commit four one a six b eight b. The student caught the cost script measuring "
                        "itself, a false claim that R5 was uncommitted, exit codes the agent could only infer, and "
                        "tests that froze enemies. The agent caught three problems in the brief. Turbulence is confirmed "
                        "from code only. Claude Code built, Claude chat drafted, and the student ran and judged it all. "
                        "Next: lower B's turbulence.",
         show=show(("0.05", "verdict page"), ("0.12", "caught by the student"), ("0.45", "caught by the agent"),
                   ("0.6", "uncertain"), ("0.75", "who did what"), ("0.9", "next step, textures, revision")),
         props={"artifactTitle": "Verdict", "artifactHeading": f"walker-TANK A6 · repo {REV} · game source {GAME_REV}",
                "brandLabel": "@NikBearBrown",
                "artifactLines": [
                    "Caught by the student: cost script measuring itself · \"R5 uncommitted\" (it was 96d38be) · exit codes the agent could only infer · tests that froze enemies (no bodies, stopped timers), fixed in tests only.",
                    "Caught by the agent in the brief: old debris gravity (0, 160) · the null-shell test break · 0.94 vs 0.875.",
                    "Strip reading overruled: Effect B r1 (\"prediction failed\"); in the game it rises — kept.",
                    "Uncertain: turbulence as the cause is confirmed from code, not by a turbulence-off strip · leak counts vary.",
                    "Next step: lower B's turbulence influence, or lighten its base colour.",
                    "Claude Code: effects, tests, previews · Claude chat: brief, scripts, documents · the student: approved every step, ran every test and capture, made every verdict.",
                    "Textures: chip_6.png, soft_dot_32.png, drawn by code · no downloaded or AI textures."]}),
    dict(beat_id="B19", act="HANDOFF", pattern="ClaudeComposerAsk",
         role_note="HANDOFF: prompt read aloud and discussed; Liam signs off here.",
         narration_text="Your turn. Please use Walker to add one particle effect to my game. Write its job first, and "
                        "predict one frame of a fixture strip. Then check it in the running game. Your own eyes decide. "
                        "Liam, in for Bear.",
         show=show(("0.02", "composer; greeting 'Your turn.'"), ("0.08", "prompt types while read aloud")),
         props=composer("Your turn.",
                        "Please use Walker to add one particle effect to my game. Write its job, predict one frame of a "
                        "fixture strip, then check it in the running game.",
                        "paste this into Claude…", [], "Your walker game")),
    dict(beat_id="B20", act="OUTRO", pattern="ClaudeTitleOutro", kind="outro_voice", tail_hold_s=1.0,
         role_note="OUTRO-LOCK: spoken, never scored; 1.0 s silent tail.",
         narration_text=f"{TITLE}. At Nik Bear Brown.",
         show=show(("0.0", "exact title, @NikBearBrown, slug-seeded mascot, no subline")),
         props={"title": TITLE, "slug": SLUG}),
]


# Tightened narration (second pass, for the ~3-minute request); replaces the first-draft lines above.
NARRATION = {
    "B00": "Hola, this is Liam, in for Bear. Assignment Six gave walker tank two particle effects. The prompt is "
           "reconstructed.",
    "B01": "A shell hits a wall. A tank gets hurt. Particles aren't decoration. Each one carries a message.",
    "B02": "Effect A, the cover hit burst: your shell landed on that wall, right there. It fires from take hit, line "
           "forty. Effect B, damage smoke: this tank is badly hurt, and how badly.",
    "B03": "Three parts. Emission: amount forty eight, lifetime one point six. Process: velocity and gravity, which "
           "become shader lines. Draw: a soft dot texture, blend mix, a visibility rect.",
    "B04": "Here it runs on the GPU, in a fixture. Headless, it costs about nothing: the dummy renderer runs no GPU "
           "particles.",
    "B05": "Effect A's intent: gone in point seven seconds. The r0 strip, a fixture. The student's first look: "
           "readable. In the game: nothing to change.",
    "B06": "So A's revision was strip driven. Claude saw the chips vanish by frame twenty: their last colour had about "
           "the ground's value. R3 adds an opaque brown stop, and predicts visible chips.",
    "B07": "Frame twenty, before and after. Claude: partly held, faint chips. The student kept r1, and declined the "
           "next lever.",
    "B08": "In the student's play recording, three hits on one wall, three bursts. On the right, a fixture with "
           "retrigger: the second burst doesn't restart the first.",
    "B09": "Effect B should rise as a wavering column, with turbulence, which A lacks. Its r0 strip. But in the game, "
           "the student saw a lump on the turret.",
    "B10": "Claude's reading: these values carry a puff only about fifty nine pixels. R5 raises initial velocity to "
           "fifty and eighty, predicting a thin column.",
    "B11": "Frames fifty eight and one forty, before and after. Claude: prediction failed, still a lump. In the game, "
           "the student saw it rise, and overruled the strip.",
    "B12": "Start, stop and pause pass the state test at all three rates. In the game: denser per hit, a trail, "
           "frozen under pause, a smoking wreck.",
    "B13": "The generated shader. Line two thirty two picks each start speed, fifty to eighty. Line four forty seven "
           "is turbulence: every step, velocity turns ten to twenty percent toward the noise.",
    "B14": "After a second, the upward heading is gone. That's the lump: confirmed from the code, not yet by a strip.",
    "B15": "Tests. Config: one twenty eight, and seventy six. A Godot three name: exit one, while Godot stayed silent. "
           "A damping drift: exit one. State: eighty two and eighty one. None of it sees drawing.",
    "B16": "Prices. Headless CPU: A adds point zero seven four milliseconds; B, about zero. GPU on the RTX 3060: A, "
           "point zero two three; B, point zero seven seven. All inside budget.",
    "B17": "The agent's first cost script read six point nine milliseconds everywhere, even the empty scene: one frame "
           "at one forty four hertz. The control caught it. FPS read one forty three to one forty four. Capped.",
    "B18": "The verdict, at commit four one a six b eight b. The student caught a cost script measuring itself, a false "
           "uncommitted claim, inferred exit codes, and frozen test enemies. The agent caught three problems in the "
           "brief. Claude Code built, Claude chat drafted, the student judged. Next: lower B's turbulence.",
    "B19": "Your turn. Please use Walker to add one particle effect to my game. Write its job, predict one frame, then "
           "check it in the running game. Liam, in for Bear.",
}
CUES = {
    "B06": [{"phrase": "last", "line": 26, "label": "colours: the last stop was #5A3A2E, about the ground's value"},
            {"phrase": "opaque", "line": 25, "label": "offsets: R3 adds a stop at 0.6 (#8E5040, opaque)"}],
    "B10": [{"phrase": "puff", "line": 32, "label": "gravity (0, −15): buoyancy, weak against damping 5–8"},
            {"phrase": "initial velocity", "line": 30, "label": "R5: initial_velocity_min 20 → 50"},
            {"phrase": "80", "line": 31, "label": "R5: initial_velocity_max 40 → 80"}],
    "B13": [{"phrase": "447", "line": 447, "label": "line 447: blend 10–20 % toward the noise, every step"},
            {"phrase": "noise", "line": 443, "label": "line 443: the noise direction at the particle's position"}],
    "B15": [{"phrase": "Config", "card": 0}, {"phrase": "godot 3", "card": 1},
            {"phrase": "State", "card": 2}, {"phrase": "drawing", "card": 3}],
}
for _spec in BEATS:
    _spec["narration_text"] = NARRATION.get(_spec["beat_id"], _spec["narration_text"])
    _spec["output"] = {"B13": ["line 232: " + line(GEN, 232)],
                       "B06": ["Prediction, frame 20: ~20 opaque red-brown chips, 50–60 px out"],
                       "B10": ["Prediction: thin column, y ≈ 270–290 at frame 58; detached by 140"],
                       }.get(_spec["beat_id"], [])
    if _spec["beat_id"] in CUES:
        _spec["cue_spec"] = CUES[_spec["beat_id"]]


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
            "brand": "claude-liam", "audience": "CSYE7270 students adding particle effects to small games with Walker + Claude Code",
            "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
            "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9",
            "fit": "contain", "captions": False, "channel": "@NikBearBrown", "channel_title": "@NikBearBrown",
            "folderLabel": "@NikBearBrown", "greeting": "Hola, Liam", "persona": "Liam (in for Bear)",
            "presenter": "Liam (in for Bear)", "in_for_bear": True, "fps": 30,
            "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-TANK", "path": "D:/CSYE7270/assignment2/walker-TANK",
                     "revision": REV, "game_source_revision": GAME_REV,
                     "checked_copy": "_scratch/src (git archive 41a6b8b)",
                     "engine": "Godot 4.7.2.stable.official.ed1daf0bf"},
            "note": "godot-gamedev walker mode, assignment-focused film (A6 particles only). New 4K fixture captures on a "
                    "scratch copy only; the student's own play recording; no paid API, no upload, no game change."}
    if sp.exists():
        prev_meta = json.loads(sp.read_text(encoding="utf-8")).get("metadata", {})
        if "build" in prev_meta:
            meta["build"] = prev_meta["build"]
    sp.write_text(json.dumps({"metadata": meta, "beats": beats}, ensure_ascii=False, indent=1), encoding="utf-8")
    words = sum(len(b["narration_text"].split()) for b in beats)
    print("wrote", sp, len(beats), "beats;", words, "words")


if __name__ == "__main__":
    build()
