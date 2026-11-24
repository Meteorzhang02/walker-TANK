"""Author beat_sheet.json for walker-tank-a8-pitch (CSYE 7270 A8 pitch film).

Builders: show-tell (drawn Manim beats + one ShowTellCard) mixed with godot-waikthrough walker-mode real captures
(media/Bxx.mp4 built by scripts/make_media.py from capture/run-01.mp4). The compositor fills each slot by
precedence media/<beat>.mp4 > manim/<beat>.mp4, so both kinds sit in one sheet.

Identity (BUILD-PROMPT.md, graded): the narrator speaks as Yunqi Zhang, first person. No instructor name, persona,
channel or credit line: the stock bookends (composer cold open, verdict, Your Turn) are exempt and the outro is the
film's own Manim card (BOUT) with handle "Yunqi Zhang", because ClaudeTitleOutro hardcodes another handle.

Every claim comes from pitch/PROJECT-BRIEF.md (see FACTCHECK.md). Names are spelled phonetically in narration_text
for Kokoro (it has no pronunciation override); the written spellings are in `display_text`.
Measured audio fields are kept while the narration is unchanged.
Run: python scripts/make_sheet.py
"""
import json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
SLUG = "walker-tank-a8-pitch"
TITLE = "Walker-TANK: One Finished Level"
ME = "Yunqi Zhang"
CAP = "tag a7, game source 4f88f1b"
KEEP = ("audio_file", "actual_duration_s", "tts_duration_s", "audio_pad", "render_duration_s", "build", "cue_times")
SPARSE = ("show-tell style: one drawn scene on a cream stage per beat, minimal labels, the voice carries the "
          "explanation; only underfill and clustered are waived, edge-bleed, empty-frame and contrast still apply.")
PROV = (f"Godot 4.7.2 Movie Maker capture, native 3840x2160, of the real scenes/main.tscn on a scratch copy made with "
        f"git archive HEAD (3cc29f2; game source identical to 4f88f1b, {CAP}); scripted input by "
        f"scripts/capture_driver.gd (Input.action_press/release + mouse warp only); take run-01; frames in order, "
        f"no retime")


def show(*ev):
    return [{"at": a, "event": e} for a, e in ev]


def base(bid, act, narration, display=None, **extra):
    b = {"beat_id": bid, "act": act, "narration_text": narration, "voice": "am_onyx", "engine": "kokoro",
         "estimated_duration_s": round(len(narration.split()) / 2.6, 1)}
    if display:
        b["display_text"] = display
    b.update(extra)
    return b


def drawn(bid, act, narration, cls, intent, ev, constructed=True, display=None, sparse=True):
    b = base(bid, act, narration, display, lane="manim", proof_gate="SHOW",
             honesty=("constructed — does not exist yet" if constructed else "drawn from memory"),
             shot={"type": "GRAPHIC", "source": "own", "visual_intent": intent, "show": show(*ev),
                   "manim": {"class": cls}, "motion_claim": intent})
    if sparse:
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE}
    return b


def capture(bid, act, narration, intent, *ev, display=None):
    return base(bid, act, narration, display, lane="capture", proof_gate="SHOW", kind="capture",
                honesty=f"real capture, {CAP}",
                shot={"type": "VIDEO", "class": "SHOW", "source": "film-capture (scripted input)",
                      "visual_intent": intent, "show": show(*ev), "provenance": PROV,
                      "evidence_media": f"media/{bid}.mp4"},
                qc=capture_qc(bid))


def capture_qc(bid):
    """Gate V: gameplay fills the frame by design (edge-bleed is the footage, not overflow); text contrast is
    measured on the burned-in plaques, which hold all the essential text on these beats."""
    regions = [{"label": "capture label plaque", "box": [0.73, 0.03, 0.98, 0.127]}]
    if bid == "B04":
        regions.append({"label": "effect caption plaque", "box": [0.37, 0.853, 0.63, 0.92]})
    return {"full_bleed": True, "contrast_regions": regions,
            "contrast_reason": "Full-frame gameplay capture: the game's own colours are not text; the label and "
                               "caption plaques are dark boxes with white type, checked per region."}


BEATS = [
    base("BIDEA", "who I am",
         "Hello. I'm Yoon-chee Jahng, a C S Y E seventy-two seventy student. This film is a pitch for my final "
         "project. The plan isn't to make Walker Tank bigger. It's to finish one level of it.",
         "Hello. I'm Yunqi Zhang, a CSYE 7270 student. This film is a pitch for my final project. The plan isn't "
         "to make walker-TANK bigger. It's to finish one level of it.",
         lane="bookend", proof_gate="SHOW", lead_silence_s=0.8,
         qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer opener: the correction is the motion."},
         shot={"type": "REMOTION", "source": "own",
               "show": show((0.0, "types 'My final project: walker-TANK, but bigger'"),
                            (0.75, "'but bigger' backspaced, 'one finished level' typed")),
               "remotion": {"pattern": "BrutalistHesitantWriter",
                            "props": {"text": "My final project:\nwalker-TANK, but bigger",
                                      "triggerWords": "but bigger", "replacementWords": "one finished level",
                                      "contextTitle": "", "banner": "",
                                      "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1,
                                      "mistakeRate": 1, "jitter": 20, "seed": SLUG}}},
         motion_claim="The writer types the naive plan (bigger) and corrects it to the real one (one finished level)."),

    capture("B01", "Q1 · what it is",
            "What is it? Walker Tank is a 2D top-down tank game. You drive Yoon-chee Zee through a ruined brick "
            "battlefield, against three enemy tanks. This is the game as it exists today, recorded at the A7 tag, "
            "and driven by a script, not by a player.",
            "Intro + drive legs of run-01: YunqiZ among brick cover, three enemy tanks advancing.",
            ("0.0", "YunqiZ idles at spawn, turret sweeping; enemies advance"), ("0.5", "drive legs among cover")),

    drawn("B02", "Q1 · finished form",
          "When the project is done, it will be a Windows desktop build of one finished level: a title screen, the "
          "battle, and a win or lose screen, plus a test report that a stranger can rerun with one command. None "
          "of that exists yet.",
          "B02_FinishedForm",
          "Three screens arrive in a row (title, battle, win or lose) and slide into a box labelled Windows build; a "
          "test-report page drops beside it with a check.",
          [(0.1, "title screen"), (0.3, "battle"), (0.45, "win / lose"), (0.65, "into the Windows build"),
           (0.8, "test report + check")]),

    drawn("B03", "Q2 · the comparable",
          "Why would anyone care? I played a 2D browser tank game on seven K seven K, called Chwan-min Tahn-kuh "
          "Dah-jahn. As I remember it, cover could not be destroyed, firing had no effect, and a destroyed tank did "
          "not smoke. This is drawn from my memory, with no art from that game.",
          "B03_FromMemory",
          "A generic drawn tank fires at a drawn wall; the shell stops and the wall is unchanged; a second tank goes "
          "grey with no smoke. Label: from memory.",
          [(0.3, "shell hits wall; wall unchanged"), (0.6, "destroyed tank, no smoke")],
          constructed=False,
          display="Why would anyone care? I played a 2D browser tank game on 7k7k, called 全民坦克大战. As I "
                  "remember it, cover could not be destroyed, firing had no effect, and a destroyed tank did not "
                  "smoke. This is drawn from my memory, with no art from that game."),

    capture("B04", "Q2 · walker-TANK's answer",
            "Walker Tank answers each one. A shell hits the brick cover, and debris bursts from the hit point. "
            "Yoon-chee Zee flashes red when it's hit. A damaged tank smokes, and a wreck keeps smoking. These are "
            "four moments from one recorded take.",
            "Four intervals of run-01, in order: cover-hit burst at the hit point; YunqiZ hit flash (red, A5 shader); "
            "a damaged enemy smoking; an enemy wreck smoking.",
            ("0.05", "cover burst"), ("0.3", "YunqiZ red flash"), ("0.55", "damaged enemy smokes"),
            ("0.75", "wreck keeps smoking"),
            display="walker-TANK answers each one. A shell hits the brick cover, and debris bursts from the hit "
                    "point. YunqiZ flashes red when it's hit. A damaged tank smokes, and a wreck keeps smoking. "
                    "These are four moments from one recorded take."),

    drawn("B05", "Q3 · the first sixty seconds",
          "Who opens it? A hiring manager or a lead engineer, hiring a gameplay programmer. In the first sixty "
          "seconds, they will unzip the build, double-click the exe, see the title screen with the controls on it, "
          "press start, and be driving within a minute, without reading anything.",
          "B05_FirstMinute",
          "A zip opens into a folder; a cursor double-clicks the exe; a title screen with a controls strip; Start; "
          "a small drawn tank drives; a clock dial sweeps to 60 s.",
          [(0.2, "zip opens"), (0.4, "double-click"), (0.55, "title + controls"), (0.75, "driving"),
           (0.85, "clock reaches 60")]),

    base("B06", "Q4 · what it proves",
         "What does it prove? Shaders, from A5. Particles, the cover burst and the damage smoke, from A6. Animation "
         "clips with pinned state tests, from A7. These tests passed again today, headless. And profiling: plus "
         "zero point zero two three and plus zero point zero seven seven milliseconds of GPU time, measured in A6 "
         "on an NVIDIA RTX thirty-sixty Laptop GPU.",
         "What does it prove? Shaders, from a5. Particles, the cover burst and the damage smoke, from a6. Animation "
         "clips with pinned state tests, from a7. These tests passed again today, headless. And profiling: +0.023 "
         "and +0.077 milliseconds of GPU time, measured in a6 on an NVIDIA RTX 3060 Laptop GPU.",
         lane="card", proof_gate="SHOW",
         honesty=f"real test output, rerun 2026-11-23 on a clean git-archive copy ({CAP}); GPU figures from "
                 f"docs/a6/TEST-REPORT-a6.md lines 215-216",
         shot={"type": "REMOTION", "source": "own",
               "show": show((0.0, "report rows land"), (0.15, "lens on shaders row"), (0.35, "particles"),
                            (0.55, "animation"), (0.8, "GPU cost row")),
               "remotion": {"pattern": "ShowTellCard", "props": {
                   "kind": "focus", "heading": CAP,
                   "items": [
                       {"label": "a5 hit flash test", "value": "50 passed"},
                       {"label": "a6 cover burst test", "value": "82 passed"},
                       {"label": "a6 damage smoke test", "value": "81 passed"},
                       {"label": "a7 anim state test", "value": "34 passed"},
                       {"label": "a6 GPU · RTX 3060 Laptop", "value": "+0.023/+0.077 ms"}],
                   "focus": 4, "cues": []}}},
         why_card="The idea is a set of real numbers (test counts and measured GPU cost); the lens moving row to row "
                  "is the claim: each skill, then its evidence."),

    drawn("B07", "Q5 · in and out",
          "What's in? One level, a title screen, win and lose screens, the effects that already exist, a Windows "
          "export, and a test report you can rerun. What's out? Multiplayer, a save system, and a second level.",
          "B07_InOut",
          "Two trays: items drop into IN one by one; three items slide toward OUT and are crossed off.",
          [(0.1, "IN tray fills"), (0.6, "OUT tray: three crossed")]),

    drawn("B08", "Q5 · first",
          "First, I will export the current game to a Windows exe, and play it from a clean folder to a win. I'll "
          "know it ran from a capture of that run and a log file, recorded in TEST-REPORT dot M D, with the commit it "
          "was built from.",
          "B08_FirstStep",
          "An exe drops into an empty folder; a drawn screen reaches a win flag; a capture frame and a log page "
          "file into a report page tagged with a commit.",
          [(0.15, "exe into clean folder"), (0.45, "win"), (0.7, "capture + log into report"), (0.88, "commit tag")],
          display="First, I will export the current game to a Windows exe, and play it from a clean folder to a win. "
                  "I'll know it ran from a capture of that run and a log file, recorded in TEST-REPORT.md, with the "
                  "commit it was built from."),

    drawn("B09", "Q6 · the risk",
          "What could make it fail? The game has never been exported. Every test so far ran in the editor or headless, "
          "on one machine with an RTX thirty-sixty. Forward plus needs a GPU that supports Vulkan or Direct-3D "
          "twelve, so the build may fail or look wrong on a reviewer's laptop with integrated graphics.",
          "B09_Risk",
          "One laptop labelled RTX 3060 with a check; a second laptop with integrated graphics; the build box slides "
          "across and a question mark rises over the second screen.",
          [(0.2, "one machine"), (0.6, "second laptop, integrated GPU"), (0.85, "question mark")],
          display="What could make it fail? The game has never been exported. Every test so far ran in the editor or "
                  "headless, on one machine with an RTX 3060. Forward+ needs a GPU that supports Vulkan or Direct3D "
                  "12, so the build may fail or look wrong on a reviewer's laptop with integrated graphics."),

    drawn("B10", "Q6 · the plan",
          "So I will export in the first week, and run the build on a second machine. If it fails, I'll switch to "
          "the Compatibility renderer, recheck each shader and particle effect, and log what changed. I'm not "
          "choosing a web export, because it runs only on Compatibility.",
          "B10_Fallback",
          "A switch flips from Forward+ to Compatibility; effect tiles get checks one by one beside a log page; a "
          "web tile is crossed out.",
          [(0.25, "second machine"), (0.45, "switch to Compatibility"), (0.65, "effects rechecked + log"),
           (0.85, "web export crossed")]),

    drawn("B11", "Q7 · why",
          "Why this project? It's a mix of showing off and learning. Shaders, particles, animation, profiling and "
          "testing are shown, with evidence, at tags A5, A6 and A7. Exporting, running on a machine I don't "
          "control, and finishing a game from title screen to end screen are new to me. A recruiter can't judge "
          "parts. They can judge a finished level.",
          "B11_Why",
          "Left shelf: five evidence blocks tagged a5/a6/a7 (shown). Right: three open outlines (new to me), "
          "labelled constructed. The parts slide together into one finished-level box.",
          [(0.25, "shown, with tags"), (0.55, "new to me"), (0.85, "parts become one level")]),

    base("B12", "close",
         "So, today: a battlefield where cover breaks, Yoon-chee Zee flashes red, and damage smokes. What will exist: "
         "one finished level, in a Windows build, with a test report you can rerun. That's my final project. "
         "Thanks for watching.",
         "So, today: a battlefield where cover breaks, YunqiZ flashes red, and damage smokes. What will exist: one "
         "finished level, in a Windows build, with a test report you can rerun. That's my final project. Thanks for "
         "watching.",
         lane="capture", proof_gate="SHOW", kind="capture",
         honesty=f"left: real capture, {CAP}; right: constructed — does not exist yet",
         qc={"full_bleed": False},
         shot={"type": "VIDEO", "class": "SHOW", "source": "film-capture + own drawing",
               "visual_intent": "Split frame: left 'exists today' plays a real run-01 interval (labelled); right "
                                "'will exist' is the B02 drawing's finished build (labelled constructed).",
               "show": show((0.0, "left: real capture"), (0.45, "right: constructed build")),
               "provenance": PROV + "; right half rendered by scenes.py B12_Close (Manim)",
               "evidence_media": "media/B12.mp4", "manim": {"class": "B12_Close"}}),

    base("BOUT", "outro",
         "Walker Tank: One Finished Level. Yoon-chee Jahng.",
         f"{TITLE}. {ME}.",
         lane="manim", proof_gate="SHOW", kind="outro_voice", tail_silence_s=1.0,
         qc={"sparse_by_design": True, "sparse_reason": "Title card: title and name on a cream stage."},
         shot={"type": "GRAPHIC", "source": "own", "visual_intent": "Title restated, my name beneath; spoken, no music.",
               "show": show((0.0, "title"), (0.3, "name")), "manim": {"class": "BOUT_Title"},
               "remotion": {"props": {"title": TITLE, "handle": ME, "subline": ""}}},
         role_note="Own outro: ClaudeTitleOutro hardcodes another channel's handle, which BUILD-PROMPT.md forbids. "
                   "Spoken, never scored: title then my name, 1.0 s silent tail."),
]

meta = {
    "slug": SLUG, "title": TITLE, "topic": "CSYE 7270 · A8 PITCH", "skill": "show-tell",
    "style_preset": "show-tell", "builders": ["show-tell", "godot-waikthrough (walker mode, captures only)"],
    "channel": ME, "channel_title": ME, "folderLabel": ME, "greeting": "Hello", "persona": f"{ME} (CSYE 7270 student)",
    "presenter": ME, "credit": ME, "voice": "am_onyx", "voice_kokoro": "am_onyx", "engine": "kokoro",
    "clock": "narration", "palette": "claude", "register": "Teardown", "fps": 30, "aspect_ratio": "16:9",
    "width": 3840, "height": 2160, "caption_policy": "none", "captions": False,
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": "Pitch film (BUILD-PROMPT.md): opens on the hesitant writer as Yunqi Zhang; the brief's "
                             "close beat replaces verdict and Your Turn; the outro is the film's own spoken title card "
                             "with handle Yunqi Zhang (no instructor name, persona, channel or credit line).",
    "audience": "CSYE 7270 reviewers of the A8 final-project pitch",
    "source_doc": "walker-TANK/pitch/PROJECT-BRIEF.md (every claim); game walker-TANK tag a7, game source 4f88f1b",
    "game": {"name": "walker-TANK", "path": "D:/CSYE7270/assignment2/walker-TANK", "capture_label": CAP,
             "tag_a7_commit": "e4e5d5f", "game_source_revision": "4f88f1b", "archive_of": "HEAD 3cc29f2",
             "engine": "Godot 4.7.2.stable.official.ed1daf0bf"},
    "playlist": "", "chapter_number": 0, "tags": ["walker-TANK", "Godot", "CSYE 7270", "pitch"],
}


def main():
    sp = REEL / "beat_sheet.json"
    old = {}
    if sp.exists():
        for b in json.loads(sp.read_text(encoding="utf-8"))["beats"]:
            old[b["beat_id"]] = b
    for b in BEATS:
        o = old.get(b["beat_id"])
        if o and o.get("narration_text") == b["narration_text"]:
            for k in KEEP:
                if k in o:
                    b[k] = o[k]
        if b["beat_id"] == "B06":
            # lens moves on the spoken words (character share), kept out of GATE T's 45-55 % window
            n = b["narration_text"]
            cues = []
            for ph in ("Particles", "the damage smoke", "Animation", "And profiling"):
                c = round(n.index(ph) / len(n), 3)
                if 0.42 < c < 0.58:
                    c = 0.42 if c < 0.5 else 0.58
                cues.append(c)
            b["shot"]["remotion"]["props"]["cues"] = cues
        if b["shot"]["type"] == "REMOTION" and b.get("actual_duration_s"):
            b["shot"]["remotion"]["props"]["durationSeconds"] = b["actual_duration_s"]
    sp.write_text(json.dumps({"metadata": meta, "beats": BEATS}, ensure_ascii=False, indent=1), encoding="utf-8")
    words = sum(len(b["narration_text"].split()) for b in BEATS)
    print(len(BEATS), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")


if __name__ == "__main__":
    main()
