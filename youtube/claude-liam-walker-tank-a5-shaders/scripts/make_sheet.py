"""Author beat_sheet.json for claude-liam-walker-tank-a5-shaders (film tooling).
Code excerpts are read verbatim from the walker-TANK working tree (commit 561d47d, clean) by line range; evidence
images are embedded as data URIs. Measured audio fields are preserved when a beat's narration is unchanged.
Run: python scripts/make_sheet.py
"""
import base64, io, json, subprocess
from pathlib import Path
from PIL import Image

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1]
REV = subprocess.run(["git", "-C", str(GAME), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
TITLE = "Walker-TANK: Shaders, Predicted and Measured"
SLUG = "claude-liam-walker-tank-a5-shaders"
SRC = f"Source: walker-TANK commit {REV}"
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


def clip(text, last):
    """A verbatim prefix of a source line, through `last`, marked as an excerpt."""
    return text[:text.index(last) + len(last)] + ", …"


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


def show(*events):
    return [{"at": a, "event": e} for a, e in events]


HF, DRV, HINT, BRICK, GEN = ("shaders/hit_flash.gdshader", "scripts/hit_flash_driver.gd", "shaders/hint_experiment.gdshader",
                             "shaders/brick_surface.gdshader", "shaders/standard_generated.gdshader")

BEATS = [
    # 1 · Walker opening / summary
    dict(beat_id="B00", act="ASK", pattern="ClaudeComposerAsk",
         role_note="COLD OPEN + walker B00. Illustrative reconstruction of a Walker prompt; not the original chat.",
         narration_text="Hola, this is Liam, in for Bear. Walker tank is a 2D, top down tank game. For Assignment Five it "
                        "got a hit flash shader and two brick materials. The prompt on screen is a reconstruction.",
         show=show(("0.02", "composer on cream; greeting 'Hola, Liam'"), ("0.15", "Walker prompt types in"),
                   ("0.7", "result lines: reconstruction label, the state, the 3D object, the revision")),
         props=composer("Hola, Liam",
                        "Please use Walker to convert my game design document about walker-TANK — a 2D top-down tank "
                        "battle — into a red hit flash shader for my tank YunqiZ and two brick materials for the "
                        "cover_wall in my 3D asset room, with predicted pixel values I can check in the engine.",
                        "reading the change brief…",
                        ["Illustrative reconstruction, not a transcript.",
                         "State: YunqiZ just took a non-fatal hit — red, fading over 0.5 s.",
                         f"3D: cover_wall in scenes/asset_room_3d.tscn, two walls · commit {REV}."], "walker-TANK · A5")),
    dict(beat_id="B01", act="BLUF", pattern="BrutalistHesitantWriter", lead_silence_s=0.8,
         role_note="walker B01: misconception corrected — a shader is a setting -> a program run for every pixel.",
         qc={"sparse_by_design": True, "sparse_reason": "hesitant writer types line by line"},
         narration_text="When YunqiZ takes a non-fatal hit, it flashes red for half a second. A shader isn't a setting "
                        "on the tank. It's a small program, run for every pixel. So we'll check its predictions "
                        "against the engine.",
         show=show(("0.0", "typing starts in the lead silence"), ("0.45", "'A shader is a setting on the tank.'"),
                   ("0.65", "phrase struck in terracotta, 'a program run for every pixel' typed")),
         props={"contextTitle": "What was built",
                "text": "YunqiZ takes a hit and flashes red.\nA shader is a setting on the tank.\nIts numbers can be checked.",
                "triggerWords": "a setting on the tank", "replacementWords": "a program run for every pixel",
                "fontSize": 62, "lineSpacing": 2.6, "align": "center", "seed": "7270-a5-shaders", "mistakeRate": 2,
                "hesitateWithin": 0, "hesitateBetween": 1, "charMs": 8, "ink": "#3D3929", "accent": "#D97757",
                "bg": "#FAF9F5"}),
    # 2 · What a shader does
    dict(beat_id="B02", act="SHADER",
         role_note="Code beat: shaders/hit_flash.gdshader lines 1-9, verbatim (the whole file; the colour line is line 8).",
         narration_text="The whole hit flash shader, typed by the student. Fragment runs once for every pixel, and it "
                        "can't see the game. Game state arrives only through one uniform: hit amount. Line eight, the "
                        "colour line from the brief, mixes toward red by hit amount times zero point six. The driver "
                        "sets it on each hit.",
         show=show(("0.0", "verbatim shader, 9 lines"), ("every pixel", "line 7 lit"), ("one uniform", "line 3 lit"),
                   ("Line eight", "line 8 lit"), ("driver", "driver line 70 in the notes panel")),
         **code("What a Shader Does", HF, 1, 9,
                [("CHANGE-BRIEF.md line 45", "the same colour line as line 8, written before the shader"
                  if line("CHANGE-BRIEF.md", 45) == line(HF, 8) else line("CHANGE-BRIEF.md", 45)),
                 ("hit_flash_driver.gd line 70 (Claude Code)", line(DRV, 70) + "\nline 12: PARAM = \"hit_amount\"")],
                [{"phrase": "every pixel", "line": 7, "label": "fragment(): runs once per pixel"},
                 {"phrase": "one uniform", "line": 3, "label": "the only game state: uniform hit_amount"},
                 {"phrase": "Line eight", "line": 8, "label": "the colour line, as in CHANGE-BRIEF.md"}])),
    dict(beat_id="B03", act="SHADER", kind="capture",
         qc={"full_bleed": False},
         role_note="Result beat: the student's own screen recording of play (a5-evidence/play.mp4), 30 fps, not retimed.",
         narration_text="This is a screen recording of the student's play. Watch YunqiZ on the left. A shell lands, the "
                        "tank turns red, and the red is gone in about half a second. Second hit, the same flash, now "
                        "over the fire of low health. The enemy tanks never turn red.",
         shot={"type": "VIDEO", "class": "SHOW", "source": "student-screen-recording", "evidence_media": "media/B03.mp4",
               "show": show(("0.0", "recording, labelled 'Screen recording of my play'"),
                            ("A shell lands", "first hit at source 6.65 s: red, fading"),
                            ("Second hit", "second hit at source 11.0 s, with fire")),
               "provenance": "D:/CSYE7270/a5-evidence/play.mp4 from 4.5 s, frames in order, scaled only; see SOURCES.md"}),
    # 3 · Predicted vs measured
    dict(beat_id="B04", act="MEASURE",
         role_note="Hit flash P1/P2 predicted vs measured at 0.0/0.5/1.0/2.0 (hit_flash_pixels.csv; brief Revision 2).",
         narration_text="Now scripted in-engine captures, at four values of hit amount. The track pixel, P2, matched "
                        "every prediction exactly. The olive pixel, P1, missed by up to twenty one, because the turret "
                        "covers it. A dated revision recomputed the turret's values, and they match within one. At "
                        "two, both pixels go pure red. Hint range doesn't clamp.",
         show=show(("0.0", "four labelled captures with P1/P2 markers and their numbers"), ("track pixel", "card 0"),
                   ("turret covers", "card 1"), ("revision", "card 2"), ("pure red", "card 3")),
         **figure("Predicted vs Measured",
                  "IN-ENGINE CAPTURE (SCRIPTED) · tools/capture_hit_flash.gd, run windowed by the student · driver stopped",
                  "evidence/ev-hitflash.png",
                  [("P2 · track", "exact at 0, 0.5, 1.0"), ("P1 · under the turret", "off by 21 / 15 / 8"),
                   ("Turret, recomputed", "within 1 · dated revision"), ("hit_amount = 2.0", "(255, 0, 0): no clamp")],
                  [{"phrase": "track pixel", "card": 0}, {"phrase": "turret covers", "card": 1},
                   {"phrase": "revision", "card": 2}, {"phrase": "pure red", "card": 3}])),
    # 4 · Why a texture is information
    dict(beat_id="B05", act="TEXTURE",
         role_note="Code beat: shaders/hint_experiment.gdshader lines 1-14 (whole file), lines 4-5 lit.",
         narration_text="Why is a texture information? The hint experiment binds one grey file to two samplers. Line "
                        "four says source colour: decode these numbers as colour. Line five says nothing: use the "
                        "stored numbers as data. The student predicted both quads by hand.",
         show=show(("0.0", "verbatim shader, 14 lines"), ("Line four", "line 4 lit"), ("Line five", "line 5 lit")),
         **code("Why a Texture Is Information", HINT, 1, 14,
                [("assets/hint/grey_3x1.png", "3 × 1 greys: 64 / 128 / 192"),
                 ("hint_srgb.tres / hint_raw.tres line 12",
                  line("materials/hint_srgb.tres", 12).split("/")[-1] + "\n"
                  + line("materials/hint_raw.tres", 12).split("/")[-1])],
                [{"phrase": "Line four", "line": 4, "label": "source_color: the numbers are colour"},
                 {"phrase": "Line five", "line": 5, "label": "no hint: the numbers are data"}], size=23)),
    dict(beat_id="B06", act="TEXTURE",
         role_note="Result beat: hint_both.png with hint_pixels.csv, predictions from CHANGE-BRIEF §4.",
         narration_text="Scripted capture. Quad A shows the file's own sixty four, one twenty eight, one ninety two. "
                        "Quad B is brighter: one thirty seven, one eighty eight, two twenty five. Six of six, exact. "
                        "The brick shader follows the same rule. Line four, the colour map, has source colour. Line "
                        "nine, roughness data, has none.",
         show=show(("0.0", "labelled capture and predicted/measured table"), ("Quad A", "card 0"),
                   ("Quad B", "card 1"), ("Line four", "card 2"), ("Line nine", "card 3")),
         **figure("Result: One File, Two Readings",
                  "IN-ENGINE CAPTURE (SCRIPTED) · tools/capture_hint.gd, run windowed by the student · Linear tonemap, unshaded",
                  "evidence/ev-hint.png",
                  [("Quad A · source_color", "64 / 128 / 192"), ("Quad B · no hint", "137 / 188 / 225"),
                   ("brick line 4", "colour map: source_color"), ("brick line 9", "roughness data: none")],
                  [{"phrase": "own values", "card": 0}, {"phrase": "Quad B", "card": 1},
                   {"phrase": "Line four", "card": 2}, {"phrase": "Line nine", "card": 3}])),
    # 5 · Material vs shader
    dict(beat_id="B07", act="MATERIAL",
         role_note="One shader, two .tres; shader edit vs material edit (CSV numbers); sweep strip of 4 captures.",
         narration_text="One brick shader, two materials. The damaged one changes just two values: a dusty tint, and "
                        "brightness zero point seven. When the student halved albedo in the shader, both walls got "
                        "darker. Changing only the damaged material's brightness changed only that wall. Then a quick "
                        "sweep. Brick size visibly changes, but the look is still the student's call.",
         show=show(("0.0", "side-by-side capture, .tres lines 12-13, edit numbers, sweep strip"),
                   ("two materials", "card 0"), ("both walls", "card 1"), ("only that wall", "card 2"), ("sweep", "card 3")),
         **figure("How a Material Differs from a Shader",
                  "IN-ENGINE CAPTURES (SCRIPTED) · tools/capture_materials.gd · shader edit made and restored by the student",
                  "evidence/ev-materials.png",
                  [("One shader", "two .tres materials"), ("Shader edit", "both walls darker"),
                   ("Material edit", "damaged wall only"), ("Sweep", "brightness, roughness, uv_scale")],
                  [{"phrase": "two materials", "card": 0}, {"phrase": "both walls", "card": 1},
                   {"phrase": "only that wall", "card": 2}, {"phrase": "sweep", "card": 3}])),
    # 6 · The Godot shading language
    dict(beat_id="B08", act="LANGUAGE",
         role_note="Code beat: shaders/brick_surface.gdshader lines 1-11; generated lines 7 and 19 and brick line 33 in notes.",
         narration_text="The Godot shading language. Line one, shader type spatial, makes this a lit 3D shader. Hints "
                        "shape the Inspector: hint range sets each slider's ends. Godot's own generated shader agrees: "
                        "its line seven gives the albedo source colour, like line four here. Its line nineteen, the "
                        "normal map, has none, like line nine.",
         show=show(("0.0", "verbatim brick shader lines 1-11; notes: generated lines 7, 19 and brick line 33"),
                   ("shader type", "line 1 lit"), ("hint range", "line 6 lit"), ("line seven", "line 4 lit"),
                   ("line nineteen", "line 9 lit")),
         **code("The Godot Shading Language", BRICK, 1, 11,
                [("standard_generated.gdshader line 7 (excerpt)", clip(line(GEN, 7), "source_color")),
                 ("standard_generated.gdshader line 19 (excerpt)", clip(line(GEN, 19), "hint_roughness_normal"))],
                [{"phrase": "shader type", "line": 1, "label": "shader_type spatial: 3D, goes through lighting"},
                 {"phrase": "hint range", "line": 6, "label": "hint_range: the Inspector slider's ends"},
                 {"phrase": "marks color", "line": 4, "label": "colour, like generated line 7"},
                 {"phrase": "19", "line": 9, "label": "data, like generated line 19"}],
                label="Source lines (verbatim excerpts) — not Inspector values", size=26)),
    dict(beat_id="B09", act="LANGUAGE",
         role_note="Result beat: one ALBEDO lit on three faces; box means measured by make_evidence.py from materials_side_by_side.png.",
         narration_text="And this is ALBEDO, line thirty three, after Godot lights it. One brick texture, three faces: "
                        "the top at eighty seven, the front at seventy three, the shaded end at sixty one. The 2D flash "
                        "had no light, which is why its numbers were exact arithmetic.",
         show=show(("0.0", "zoomed capture of CoverWall with three boxes and their means"), ("top", "card 0"),
                   ("front", "card 1"), ("shaded end", "card 2")),
         **figure("Result: ALBEDO, Lit",
                  "IN-ENGINE CAPTURE (SCRIPTED) · box means measured by this film's script",
                  "evidence/ev-litwall.png",
                  [("top", "red 87.5"), ("front", "red 73.4"), ("end (+x)", "red 60.8")],
                  [{"phrase": "top", "card": 0}, {"phrase": "front", "card": 1}, {"phrase": "shaded end", "card": 2}],
                  excerpt="brick_surface.gdshader line 33: " + line(BRICK, 33))),
    # 7 · Tests and limits
    dict(beat_id="B10", act="TESTS",
         role_note="Recorded headless results (logs/), mutations (step2-output.txt, commit 1718cdd), and the limits.",
         narration_text="The tests are headless. The flash test passed fifty of fifty at thirty, sixty and one forty "
                        "four frames per second. Materials, seventy six of seventy six, and both baselines still pass. "
                        "Three deliberate breaks each exit one. What headless can't show: the look, the white flash "
                        "hidden under the red, and the pause rule, never checked by hand.",
         show=show(("0.0", "HEADLESS log table, mutations, limits list"), ("fifty", "card 0"), ("seventy", "card 1"),
                   ("baselines", "card 2"), ("breaks", "card 3")),
         **figure("Tests and Limits",
                  "HEADLESS · recorded logs (rerun at 3d48047; mutation 3 at 1718cdd) · nothing drawn",
                  "evidence/ev-tests.png",
                  [("hit flash", "50/50 at 30, 60, 144 fps"), ("materials", "76/76"),
                   ("baselines", "18/18 · 8/8"), ("mutations", "3 × exit 1")],
                  [{"phrase": "50", "card": 0}, {"phrase": "76", "card": 1},
                   {"phrase": "baselines", "card": 2}, {"phrase": "breaks", "card": 3}])),
    # 8 · Verdict -> Your Turn -> outro
    dict(beat_id="B11", act="VERDICT", pattern="ClaudeVerdictArtifact",
         role_note="Verdict: what held, agent mistakes caught, contributions, texture source, one next step, revision.",
         narration_text="The verdict, at commit five six one d four seven d. The predictions held, except one pixel on "
                        "the wrong layer, and that is recorded. The student caught three agent mistakes: a CLAUDE dot "
                        "M D scope too narrow, wrong Use External key names in the materials test, and a probe script "
                        "left in logs. The student typed all three shaders from Claude chat's suggestions, and wrote "
                        "the language notes in Chinese, then had them translated. Claude Code wrote the driver, tests, "
                        "materials, tools and document drafts. Bricks: Poly Haven, Rob Tuytel, C C zero. Next step: "
                        "check the pause rule by hand.",
         show=show(("0.05", "verdict page"), ("0.15", "held"), ("0.3", "mistakes caught"), ("0.55", "who did what"),
                   ("0.85", "texture, next step")),
         props={"artifactTitle": "Verdict", "artifactHeading": f"walker-TANK A5, commit {REV}.",
                "brandLabel": "@NikBearBrown",
                "artifactLines": ["Held: P2 exact, hint bands 6/6, both edits as predicted; P1 missed (turret layer), revised and dated.",
                                  "Agent mistakes caught: CLAUDE.md scope too narrow · Use External key names in test_materials · a probe script left in logs/.",
                                  "Student: typed all three shaders from Claude chat's suggestions; LANGUAGE-NOTES answers written in Chinese, translated.",
                                  "Claude Code: the driver, tests, materials, tools and document drafts.",
                                  "Texture: Poly Haven red_bricks_04, Rob Tuytel, CC0.",
                                  "Next step: check the pause rule by hand in a windowed run."]}),
    dict(beat_id="B12", act="HANDOFF", pattern="ClaudeComposerAsk",
         role_note="HANDOFF: prompt read aloud verbatim and discussed; Liam signs off here.",
         narration_text="Your turn. Please use Walker to add one shader effect to my game. First write the state it "
                        "shows, and predict two pixel values by hand, on the final drawn layer. Then write a headless "
                        "test, and give me a windowed capture tool so I can measure the real pixels. The order is the "
                        "point: predict, then measure, because headless never draws. Liam, in for Bear.",
         show=show(("0.02", "composer; greeting 'Your turn.'"), ("0.08", "prompt types while read aloud")),
         props=composer("Your turn.",
                        "Please use Walker to add one shader effect to my game. Predict two pixel values by hand, on "
                        "the final drawn layer. Then write a headless test, and a windowed capture tool to measure them.",
                        "paste this into Claude…", [], "Your walker game")),
    dict(beat_id="B13", act="OUTRO", pattern="ClaudeTitleOutro", kind="outro_voice", tail_hold_s=1.0,
         role_note="OUTRO-LOCK: spoken, never scored; 1.0 s silent tail.",
         narration_text=f"{TITLE}. At Nik Bear Brown.",
         show=show(("0.0", "exact title, @NikBearBrown, slug-seeded mascot, no subline")),
         props={"title": TITLE, "slug": SLUG}),
]


# Tightened narration (second pass, for the ~2-minute request); replaces the first-draft lines above.
NARRATION = {
    "B00": "Hola, this is Liam, in for Bear. Walker tank is a 2D, top down tank game, and Assignment Five gave it "
           "shaders. The prompt on screen is a reconstruction.",
    "B01": "YunqiZ takes a hit and flashes red. A shader isn't a setting on the tank. It's a program, run for every "
           "pixel. And its numbers can be checked.",
    "B02": "The whole shader, typed by the student. Fragment runs for every pixel and can't see the game. State arrives "
           "through one uniform: hit amount. Line eight, the brief's colour line, mixes toward red. The driver sets it.",
    "B03": "The student's screen recording of play. A shell lands, YunqiZ turns red, and it fades in about half a "
           "second. Second hit, same flash. The enemies never turn red.",
    "B04": "Scripted captures, at four values. The track pixel, P2, matched exactly. The olive pixel, P1, missed, "
           "because the turret covers it. Recomputed for the turret, the revision matches within one. At two, pure "
           "red: hint range doesn't clamp.",
    "B05": "Why is a texture information? One grey file, two samplers. Line four says source colour: these numbers are "
           "colour. Line five says nothing: they're data.",
    "B06": "Quad A shows the file's own values. Quad B is brighter, exactly as predicted: six of six. The brick shader "
           "uses the same rule. Line four, colour. Line nine, roughness data.",
    "B07": "One shader, two materials, differing in two values. Editing the shader darkened both walls. Editing the "
           "damaged material changed only that wall. And a quick sweep: brick size visibly changes, but the look is "
           "still the student's call.",
    "B08": "Line one, shader type spatial: a lit 3D shader. Hint range sets the Inspector slider's ends. Godot's own "
           "generated shader agrees: its line seven marks colour, like line four, and its line nineteen, data, like "
           "line nine.",
    "B09": "That's ALBEDO, after lighting. One texture, three faces: top eighty seven, front seventy three, shaded end "
           "sixty one. The 2D flash had no light, so its numbers were exact.",
    "B10": "All headless. Fifty of fifty at thirty, sixty and one forty four frames per second. Seventy six of seventy "
           "six. Both baselines still pass. Three deliberate breaks, each exit one. Headless can't show the look, the "
           "white flash under the red, or the pause rule by hand.",
    "B11": "The verdict, at commit five six one d four seven d. The predictions held, except one pixel on the wrong "
           "layer. Agent mistakes the student caught: a CLAUDE dot M D scope too narrow, wrong Use External key names "
           "in the materials test, and a probe script left in logs. The student typed all three shaders from Claude "
           "chat's suggestions, and wrote the language notes in Chinese, translated. Claude Code wrote the driver, "
           "tests, materials, tools and document drafts. Bricks: Poly Haven, Rob Tuytel, C C zero. Next step: check "
           "the pause rule by hand.",
    "B12": "Your turn. Please use Walker to add one shader effect to my game. Predict two pixel values by hand, on the "
           "final drawn layer. Then write a headless test, and a windowed capture tool to measure them. Predict first, "
           "then measure, because headless never draws. Liam, in for Bear.",
}
for _spec in BEATS:
    _spec["narration_text"] = NARRATION.get(_spec["beat_id"], _spec["narration_text"])


def build():
    sp = REEL / "beat_sheet.json"
    old = {b["beat_id"]: b for b in json.loads(sp.read_text(encoding="utf-8"))["beats"]} if sp.exists() else {}
    beats = []
    for spec in BEATS:
        b = {k: v for k, v in spec.items() if k not in ("code_src", "image_src", "cue_spec", "props", "pattern", "show")}
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
            shot["remotion"] = {"pattern": spec["pattern"], "props": props}
            b["shot"] = shot
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
            "brand": "claude-liam", "audience": "CSYE7270 students adding shaders to small games with Walker + Claude Code",
            "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
            "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9",
            "fit": "contain", "captions": False, "channel": "@NikBearBrown", "channel_title": "@NikBearBrown",
            "folderLabel": "@NikBearBrown", "greeting": "Hola, Liam", "persona": "Liam (in for Bear)",
            "presenter": "Liam (in for Bear)", "in_for_bear": True, "fps": 30,
            "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-TANK", "path": "D:/CSYE7270/assignment2/walker-TANK",
                     "revision": REV, "engine": "Godot 4.7.2.stable.official.ed1daf0bf"},
            "note": "godot-gamedev walker mode, assignment-focused short film (A5 shaders only). Existing captures only; "
                    "no Godot launched, no paid API, no upload, no game change."}
    if sp.exists():
        prev_meta = json.loads(sp.read_text(encoding="utf-8")).get("metadata", {})
        if "build" in prev_meta:
            meta["build"] = prev_meta["build"]
    sp.write_text(json.dumps({"metadata": meta, "beats": beats}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", sp, len(beats), "beats; revision", REV)


if __name__ == "__main__":
    build()
