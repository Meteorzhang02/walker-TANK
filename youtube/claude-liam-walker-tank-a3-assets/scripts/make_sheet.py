"""Author beat_sheet.json for claude-liam-walker-tank-a3-assets (film tooling).
Code excerpts are read verbatim from the isolated copy of commit 9baa12c by line range (the checker compares
them with the live game folder, which is the same commit); evidence images are embedded as data URIs.
Measured audio fields are preserved when a beat's narration is unchanged.
Run from anywhere: python scripts/make_sheet.py
"""
import base64, io, json
from pathlib import Path
from PIL import Image

REEL = Path(__file__).resolve().parents[1]
GAME = Path(r"D:/CSYE7270/assignment2/walker-TANK")
TITLE = "Walker-TANK: Three Assets, One Hand Edit"
SLUG = "claude-liam-walker-tank-a3-assets"
SRC = "Source: walker-TANK commit 9baa12c"
KEEP = ("audio_file", "actual_duration_s", "tts_duration_s", "audio_pad", "render_duration_s", "build", "cue_times")


def excerpt(path, a, b):
    return "\n".join((GAME / path).read_text(encoding="utf-8").splitlines()[a - 1:b])


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


def figure(title, status, image, cards, cue_spec):
    return {"pattern": "GodotDesignFigure", "image_src": image, "cue_spec": cue_spec,
            "props": {"title": title, "status": status, "imageLabel": "", "excerpt": "", "source": SRC,
                      "cards": [{"label": l, "text": t} for l, t in cards], "cues": [], "dense": False}}


def code(title, path, a, z, notes, cue_spec):
    return {"pattern": "GodotDevWorkbench", "code_src": (path, a, z), "cue_spec": cue_spec,
            "props": {"mode": "code", "title": title, "project": "walker-TANK",
                      "source": f"Godot editor reconstruction · {SRC} · {path} lines {a}–{z}",
                      "codeFontSize": 30, "inspectorLabel": "Source notes — not Inspector values",
                      "notes": [{"label": l, "value": v} for l, v in notes], "cues": [], "output": []}}


def show(*events):
    return [{"at": a, "event": e} for a, e in events]


BEATS = [
    dict(beat_id="B00", act="ASK", pattern="ClaudeComposerAsk",
         role_note="COLD OPEN + walker B00. Illustrative reconstruction of a Walker prompt; not the original chat.",
         narration_text='Hej, this is Liam, in for Bear. Walker tank is a 2D, top down tank game. For Assignment Three, the student built three simple 3D assets with Claude through the Blender MCP, and showed them in Godot. The prompt on screen is a reconstruction.',
         show=show(("0.02", "composer on cream; greeting 'Hej, Liam'"), ("0.15", "Walker prompt types in"),
                   ("0.7", "result lines land; first labels the prompt a reconstruction")),
         props=composer("Hej, Liam",
                        "Please use Walker to convert my game design document about walker-TANK — a 2D top-down tank "
                        "battle on a ruined brick battlefield — into three simple 3D assets built in Blender through "
                        "the MCP, checked against my brief and shown in a Godot 3D scene.",
                        "reading the change brief…",
                        ["Illustrative reconstruction, not a transcript.",
                         "Built: cover_wall, ammo_crate, tank_hedgehog.",
                         "Godot 4.7.2 · commit 9baa12c."], "walker-TANK · A3")),
    dict(beat_id="B01", act="BLUF", pattern="BrutalistHesitantWriter", lead_silence_s=0.8,
         role_note="walker B01: misconception corrected — the checks prove they look right -> measure right.",
         qc={"sparse_by_design": True, "sparse_reason": "hesitant writer types line by line"},
         narration_text="Three 3D assets for a 2D tank game. Claude built them in Blender, and the student checked "
                        "them. But the checks prove they measure right, not that they look right. So we'll watch "
                        "both: the numbers, and the running scene.",
         show=show(("0.0", "typing starts in the lead silence"), ("0.5", "'The checks prove they look right.'"),
                   ("0.7", "'look' struck in terracotta, 'measure' typed")),
         props={"contextTitle": "What was built",
                "text": "Three 3D assets for a 2D tank game.\nClaude built them in Blender.\nThe checks prove they look right.",
                "triggerWords": "look", "replacementWords": "measure", "fontSize": 66, "lineSpacing": 2.6,
                "align": "center", "seed": "7270-a3-assets", "mistakeRate": 2, "hesitateWithin": 0,
                "hesitateBetween": 1, "charMs": 8, "ink": "#3D3929", "accent": "#D97757", "bg": "#FAF9F5"}),
    dict(beat_id="B02", act="SETUP",
         role_note="Requirement 1: the game and the three assets with the reason for each (CHANGE-BRIEF.md).",
         narration_text='The game stays 2D. The brief, written before anything was built, asks for three pieces of its battlefield: a brick cover wall, wide enough to hide the whole hull; an ammo crate, a pickup that pulls you out of cover; and a tank hedgehog, steel that blocks tanks but not shells.',
         show=show(("0.0", "student's game screenshot beside the brief's three rows"), ("cover wall", "card 0"),
                   ("ammo crate", "card 1"), ("hedgehog", "card 2")),
         **figure("The Game and Its Three Assets",
                  "STUDENT'S OWN SCREENSHOT · walker-TANK, 2D top-down · brief from CHANGE-BRIEF.md",
                  "evidence/ev-game-brief.png",
                  [("cover_wall", "hide behind it"), ("ammo_crate", "refill shells"), ("tank_hedgehog", "blocks tanks")],
                  [{"phrase": "cover wall", "card": 0}, {"phrase": "ammo crate", "card": 1},
                   {"phrase": "hedgehog", "card": 2}])),
    dict(beat_id="B03", act="BLENDER",
         role_note="Requirement 2a: the student's Blender window and the MCP panel with libraries/generators off.",
         narration_text="The student's own Blender session. In the MCP panel: connected on port nine eight seven six, every asset library and AI generator off. Four outside facing tools were also denied in settings. So every shape comes from cubes, built by code.",
         show=show(("0.0", "Blender window + MCP panel, student's screenshots"), ("connected", "card 0"),
                   ("asset library", "card 1"), ("denied", "card 2")),
         **figure("The Student's Blender Session",
                  "STUDENT'S OWN SCREENSHOTS · Blender 5.2.2 LTS · MCP for Blender add-on 1.8",
                  "evidence/ev-blender-mcp.png",
                  [("MCP", "connected, port 9876"), ("Libraries + generators", "all off"),
                   ("Denied tools", "4 in settings")],
                  [{"phrase": "connected", "card": 0}, {"phrase": "asset library", "card": 1},
                   {"phrase": "denied", "card": 2}])),
    dict(beat_id="B04", act="BLENDER",
         role_note="Requirement 2b: one prompt to Claude and what it built (cover_wall). Prompt wording itself is not in the screenshots.",
         narration_text='One request, for the cover wall. Claude came back with a seven step plan and two questions: the top block sizes, and whether to join three cubes into one. The student chose to join. Result: four by one by one point eight metres, thirty-six triangles.',
         show=show(("0.0", "Claude's plan (left) and its report of the result (right)"), ("two questions", "card 0"),
                   ("join", "card 1"), ("thirty", "card 2")),
         **figure("One Request, One Asset",
                  "STUDENT'S OWN SCREENSHOTS · Claude Code session, cover_wall",
                  "evidence/ev-prompt-built.png",
                  [("Claude asked", "2 decisions"), ("Student chose", "join into one mesh"),
                   ("Built", "4.0 × 1.0 × 1.8 m, 36 tris")],
                  [{"phrase": "two questions", "card": 0}, {"phrase": "chose", "card": 1},
                   {"phrase": "triangles", "card": 2}])),
    dict(beat_id="B05", act="HAND EDIT",
         role_note="Requirement 2c: the student's hand edit, +0.6 m in Edit Mode, then 0.7 mm short.",
         narration_text="Then the student's hand edit. In Edit Mode, block B moves plus zero point six metres. The sidebar reads four metres, so it looked flush. Claude's read only check says it moved zero point five nine nine three, zero point seven millimetres short. The sidebar rounds.",
         show=show(("0.0", "Edit Mode, sidebar 4 m, Claude's check — student's screenshots"),
                   ("Edit Mode", "card 0"), ("sidebar", "card 1"), ("millimetres", "card 2")),
         **figure("The Student's Hand Edit",
                  "STUDENT'S OWN SCREENSHOTS · cover_wall, Edit Mode",
                  "evidence/ev-hand-edit.png",
                  [("Moved", "block B, G X 0.6"), ("Sidebar showed", "4 m — rounded"),
                   ("Actually moved", "0.5993 m: 0.7 mm short")],
                  [{"phrase": "Edit Mode", "card": 0}, {"phrase": "sidebar reads", "card": 1},
                   {"phrase": "short", "card": 2}])),
    dict(beat_id="B06", act="GODOT",
         role_note="Code beat: scenes/asset_room_3d.tscn lines 35-51, verbatim.",
         narration_text="Into Godot. The three exported GLB files are instanced into one 3D scene, side by side "
                        "along X, each at scale one. The grey box is not an asset. It's the size of the player's "
                        "tank hull, there only for scale, and its label says so.",
         show=show(("0.0", "verbatim .tscn excerpt with line numbers"), ("three", "line 35 lit"),
                   ("grey box", "line 44 lit"), ("label", "line 50 lit")),
         **code("The 3D Scene", "scenes/asset_room_3d.tscn", 35, 51,
                [("Floor", "40 × 40 m plane"), ("Light", "one DirectionalLight3D"), ("Camera", "fixed, (0, 8, 16)")],
                [{"phrase": "three", "line": 35, "label": "a .glb instanced as a scene"},
                 {"phrase": "not an asset", "line": 44, "label": "hull-sized box, not an asset"},
                 {"phrase": "label", "line": 50, "label": "says NOT an asset"}])),
    dict(beat_id="B07", act="GODOT", kind="capture",
         qc={"full_bleed": True,
             "contrast_regions": [{"label": "RUNNING GODOT SCENE banner", "box": [0.06, 0.055, 0.5, 0.1]},
                                  {"label": "capture provenance banner", "box": [0.06, 0.897, 0.62, 0.937]}],
             "contrast_reason": "Native engine footage fills the frame by design (dark floor on grey sky); the only "
                                "essential text is the two burned-in label banners, white on dark green."},
         role_note="Result beat: native 4K Movie Maker capture of the running asset_room_3d.tscn (isolated copy of 9baa12c).",
         narration_text="And here it is, running. Wall, crate, hedgehog, then the hull box. Beside the hull, the wall "
                        "is wider than the tank is deep, the crate is small enough to drive over, and the hedgehog "
                        "sits below the hull. The camera is fixed, so nothing moves. Notice the dark faces: one "
                        "light, no fill.",
         shot={"type": "VIDEO", "class": "SHOW", "source": "godot-movie-maker", "evidence_media": "media/B07.mp4",
               "show": show(("0.0", "running scene, labelled RUNNING GODOT SCENE")),
               "provenance": "capture/room-run.mp4 (Movie Maker, 3840x2160, 30 fps) + burned label; see SOURCES.md"}),
    dict(beat_id="B08", act="CHECK",
         role_note="Code beat: tests/check_a3_assets.gd lines 22-27, verbatim.",
         narration_text="The headless check. These are the brief's sizes, turned to Godot's Y up axes, with a "
                        "tolerance of one centimetre, tighter than the brief's own ten. For each file it measures "
                        "the box, the lowest point, the root scale, and which axis holds the height.",
         show=show(("0.0", "verbatim check excerpt"), ("tolerance", "line 22 lit"), ("brief's sizes", "line 24 lit"),
                   ("height", "line 26 lit")),
         **code("The Headless Check", "tests/check_a3_assets.gd", 22, 27,
                [("Runs", "headless, dummy renderer"), ("Measures", "merged mesh AABB"), ("Exit", "1 on any FAIL")],
                [{"phrase": "sizes", "line": 23, "label": "brief sizes in Godot x, y, z"},
                 {"phrase": "up axis", "line": 24, "label": "height 1.8 is the y value"},
                 {"phrase": "tolerance", "line": 22, "label": "TOL = 0.01 m"}])),
    dict(beat_id="B09", act="CHECK",
         role_note="Result beat: headless numbers beside the brief, re-run on an isolated copy of 9baa12c.",
         narration_text='Re-run on a clean copy of this commit: eighteen of eighteen pass, exit code zero. The student also made it fail on purpose, once, to prove it can. But headless means nothing was drawn: no colours, no shadows, not the copies in the scene.',
         show=show(("0.0", "brief vs headless table, labelled HEADLESS"), ("eighteen", "card 0"),
                   ("on purpose", "card 1"), ("nothing was drawn", "card 2")),
         **figure("Result: Headless Numbers Beside the Brief",
                  "HEADLESS · recorded output, re-run by Claude on an isolated copy of 9baa12c",
                  "evidence/ev-headless.png",
                  [("Result", "18 / 18 PASS, exit 0"), ("FAIL path", "proven once: exit 1"),
                   ("Headless", "nothing drawn")],
                  [{"phrase": "pass", "card": 0}, {"phrase": "on purpose", "card": 1},
                   {"phrase": "nothing", "card": 2}])),
    dict(beat_id="B10", act="ERRORS",
         role_note="Requirement 4: what Claude got wrong (TEST-REPORT, FRICTIONAL A3 §3, §5).",
         narration_text="What Claude got wrong. Its brief's two point four metre beams make the hedgehog one point five five nine metres high, over tolerance. It caught that before building; the student chose two point one two five metre beams. Plus a join error, and a comment that didn't match its code.",
         show=show(("0.0", "Claude's box check screenshot + three errors"), ("five five nine", "card 0"),
                   ("AttributeError", "card 1"), ("comment", "card 2")),
         **figure("What Claude Got Wrong",
                  "STUDENT'S OWN SCREENSHOT · Claude's bounding-box check, before building",
                  "evidence/ev-claude-wrong.png",
                  [("Brief", "1.559 m → 2.125 m beams"), ("Join", "AttributeError"), ("Comment", "≠ its code")],
                  [{"phrase": "beams", "card": 0}, {"phrase": "join", "card": 1},
                   {"phrase": "comment", "card": 2}])),
    dict(beat_id="B11", act="VERDICT", pattern="ClaudeVerdictArtifact",
         role_note="Verdict: checked, uncertain, next step, human/AI contributions, source revision.",
         narration_text="Verdict. Checked: size, origin, scale and height axis, eighteen of eighteen, fail path proven, plus the student's own look at colours and floor contact. Uncertain: colours under the game's real lighting, and why the edit moved zero point five nine nine three. Next step: check the copies placed in the scene. Claude proposed the brief and wrote the code; the student made the decisions and the hand edit, and approved the code calls, except a few that auto mode ran. Source revision: nine B A A one two C.",
         show=show(("0.05", "verdict page"), ("0.2", "checked lines"), ("0.6", "uncertain / next / who / revision")),
         props={"artifactTitle": "Verdict", "artifactHeading": "walker-TANK A3, commit 9baa12c.",
                "brandLabel": "@NikBearBrown",
                "artifactLines": ["Checked (headless): size, origin, scale, height axis — 18/18, FAIL path proven.",
                                  "Checked by eye (student): colours, floor contact, no missing faces.",
                                  "Uncertain: colours under real game lighting; why the edit moved 0.5993 m.",
                                  "Next step: extend the check to the copies placed in the scene.",
                                  "AI: brief + all code. Human: decisions, hand edit, approvals (a few calls ran in auto mode)."]}),
    dict(beat_id="B12", act="HANDOFF", pattern="ClaudeComposerAsk",
         role_note="HANDOFF: prompt read aloud verbatim and discussed; Liam signs off here.",
         narration_text="Your turn. Here's the prompt. Please use Walker to add one 3D asset to my game. First write "
                        "its brief with size, origin and triangle budget. Then compute its bounding box before "
                        "building, and stop if it misses my tolerance. After it's built, add it to my headless check, "
                        "and predict the numbers before you run it. The point is the order: brief, prediction, build, "
                        "check. Watch where Claude's numbers and yours disagree. Liam, in for Bear.",
         show=show(("0.02", "composer; greeting 'Your turn.'"), ("0.08", "prompt types while read aloud")),
         props=composer("Your turn.",
                        "Please use Walker to add one 3D asset to my game. First write its brief with size, origin "
                        "and triangle budget. Then compute its bounding box before building, and stop if it misses "
                        "my tolerance. After it's built, add it to my headless check and predict the numbers before "
                        "you run it.",
                        "paste this into Claude…", [], "Your walker game")),
    dict(beat_id="B13", act="OUTRO", pattern="ClaudeTitleOutro", kind="outro_voice", tail_hold_s=1.0,
         role_note="OUTRO-LOCK: spoken, never scored; 1.0 s silent tail.",
         narration_text=f"{TITLE}. At Nik Bear Brown.",
         show=show(("0.0", "exact title, @NikBearBrown, slug-seeded mascot, no subline")),
         props={"title": TITLE, "slug": SLUG}),
]


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
            pr = prev.get("shot", {}).get("remotion") or {}
            if "rendered" in pr and b["shot"].get("remotion", {}).get("props") == {**pr.get("props", {})}:
                b["shot"]["remotion"]["rendered"] = pr["rendered"]
        if "cue_spec" in spec:
            b["cue_spec"] = spec["cue_spec"]
            if "cue_times" in b:
                b["shot"]["remotion"]["props"]["cues"] = b["cue_times"]
        dur = b.get("actual_duration_s")
        if dur and "remotion" in b["shot"]:
            b["shot"]["remotion"]["props"]["durationSeconds"] = dur
        beats.append(b)
    meta = {"title": TITLE, "slug": SLUG, "topic": "GODOT · WALKER · GAMEDEV", "kind": "gamedev", "mode": "walker",
            "brand": "claude-liam", "audience": "CSYE7270 students building small games with Walker + Claude Code",
            "register": "Teardown", "engine": "kokoro", "voice": "am_onyx", "voice_kokoro": "am_onyx",
            "palette": "claude", "style_preset": "claude", "ground": "#FAF9F5", "aspect_ratio": "16:9",
            "fit": "contain", "captions": False, "channel": "@NikBearBrown", "channel_title": "@NikBearBrown",
            "folderLabel": "@NikBearBrown", "greeting": "Hej, Liam", "persona": "Liam (in for Bear)",
            "presenter": "Liam (in for Bear)", "in_for_bear": True, "fps": 30,
            "teaching_contract": "code-then-result-v1",
            "game": {"name": "walker-TANK", "path": "D:/CSYE7270/assignment2/walker-TANK",
                     "revision": "9baa12c", "engine": "Godot 4.7.2.stable.official.ed1daf0bf"},
            "note": "godot-gamedev walker mode, assignment-focused short film (A3 only). No paid API, no upload, no game change."}
    if sp.exists():
        prev_meta = json.loads(sp.read_text(encoding="utf-8")).get("metadata", {})
        if "build" in prev_meta:
            meta["build"] = prev_meta["build"]
    sp.write_text(json.dumps({"metadata": meta, "beats": beats}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", sp, len(beats), "beats")


if __name__ == "__main__":
    build()
