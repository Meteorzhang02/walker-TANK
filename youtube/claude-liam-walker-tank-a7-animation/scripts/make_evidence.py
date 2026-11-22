"""Build the still figures (evidence/ev-*.png) for claude-liam-walker-tank-a7-animation (film tooling).
Adapted from the A6 reel's make_evidence.py (same page size, fonts and type scale).
Frame strips are the student's own FIXTURE captures from walker-TANK/captures/ at revision 4f88f1b (read from the
git-archive copy in _scratch/src); they are cropped and enlarged only, never retouched. Every number and quote is
copied from CHANGE-BRIEF.md / TUNING.md / animations/*.tres / logs/ at 4f88f1b, or from the student's film prompt
where the repo has no record (marked so on the figure); see FACTCHECK.md.
Run: python scripts/make_evidence.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
SRC = REEL / "_scratch/src"
CAP = SRC / "captures"
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
OUT = REEL / "evidence"
OUT.mkdir(exist_ok=True)
FS = 1.2
INK, SOFT, TERRA, DARK, PAPER, LINE, GOOD = "#3D3929", "#564739", "#985039", "#303D34", "#FFFDF8", "#CFC6B5", "#3F6B47"


def font(kind, size):
    path = {"serif": FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf",
            "bold": FONTS / "Lato/static/Lato-Bold.ttf",
            "reg": FONTS / "Inter/static/Inter_28pt-Regular.ttf",
            "mono": Path(r"C:/Windows/Fonts/consola.ttf")}[kind]
    return ImageFont.truetype(str(path), round(size * FS))


def tag(d, xy, text, size=30, fill=DARK):
    f = font("bold", size)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + 36, y + round(size * FS) + 22], radius=10, fill=fill)
    d.text((x + 18, y + 9), text, font=f, fill=PAPER)
    return w + 36


def table(d, x, y, rows, widths, size=32, head=True, lh=None, kinds=None):
    lh = lh or round(size * FS) + 24
    for i, row in enumerate(rows):
        cx = x
        for j, cell in enumerate(row):
            k = "bold" if (head and i == 0) else (kinds[j] if kinds else "reg")
            d.text((cx, y), cell, font=font(k, size), fill=TERRA if (head and i == 0) else INK)
            cx += widths[j]
        y += lh
        if head and i == 0:
            d.line([x, y - 10, x + sum(widths) - 20, y - 10], fill=LINE, width=3)
    return y


def strip_tile(path, k, crop=None):
    """Tile k (0-5) of a student strip: 640x360 tiles below a 28 px label bar."""
    im = Image.open(path).convert("RGB")
    tw = im.width // 6
    t = im.crop((k * tw, 28, (k + 1) * tw, im.height))
    return t.crop(crop) if crop else t


def ev_phase():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    d.text((40, 20), "Phase table (CHANGE-BRIEF.md 75–80)", font=font("serif", 50), fill=INK)
    table(d, 40, 100, [["Phase", "Frames", "Begins", "Key time"],
                       ["Startup", "1", "frame 0", "0.0000 s"],
                       ["Active", "1", "frame 1", "0.0333 s"],
                       ["Recovery", "3", "frame 2", "0.0667 s"],
                       ["(end)", "—", "frame 5", "0.1667 s"]], [300, 200, 230, 260], size=34)
    d.text((1700, 20), "Baked keys (animations/fire_clips.tres)", font=font("serif", 50), fill=INK)
    table(d, 1700, 100, [["Track", "times (s)", "values"],
                         ["Suspension:position", "0 · 0.0333 · 0.1667", "(0,0) (0,2) (0,0)"],
                         ["Suspension:scale", "0 · 0.0333 · 0.0667", "(1,1) (1.04,0.96) (1,1)"],
                         ["step / loop", "1/30 (default)", "LOOP_NONE (default)"]],
          [480, 430, 560], size=27, kinds=["mono", "mono", "mono"])
    d.text((1700, 440), "fire_clips.tres writes no step/loop line: both are Godot defaults; read-back: PASS.",
           font=font("reg", 24), fill=SOFT)
    tag(d, (40, 540), "FIXTURE STRIP · captures/shoot_strip_v1.png · the student's capture · tiles cropped, enlarged 1.5×")
    labels = ["N · startup", "N+1 · active", "N+2 · recovery", "N+5 · end"]
    x = 40
    for lab, k in zip(labels, (0, 1, 2, 5)):
        t = strip_tile(CAP / "shoot_strip_v1.png", k, (120, 60, 600, 300))
        t = t.resize((round(t.width * 1.5), round(t.height * 1.5)), Image.LANCZOS)
        page.paste(t, (x, 640))
        d.rectangle([x - 2, 638, x + t.width + 1, 640 + t.height + 1], outline=TERRA if k == 1 else LINE, width=5)
        d.text((x + 6, 640 + t.height + 10), lab, font=font("bold", 30), fill=TERRA if k == 1 else INK)
        x += t.width + 50
    page.save(OUT / "ev-phase.png")


def ev_tests():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    d.text((40, 20), "Recorded headless results at 4f88f1b (logs/)", font=font("serif", 54), fill=INK)
    y = table(d, 40, 120, [["Suite", "Result", "Rates (--fixed-fps)", "What it reads"],
                           ["test_clip_readback.gd", "49 passed, 0 failed", "60", "keys, step, loop, discrete, range, seam, callback mode"],
                           ["test_anim_states.gd", "34 passed, 0 failed", "30 · 60 · 144", "state table, interrupts, C1 two clocks"],
                           ["test_anim_edges.gd (new)", "27 passed, 0 failed", "30 · 60 · 144", "P+2 / P+4 / P+10 × hit, death, 2nd fire × before, on, after"],
                           ["test_pins.gd", "11 passed, 0 failed", "60", "behaviour pinned before the wiring"]],
              [640, 520, 440, 1500], size=30)
    d.line([40, y + 10, 3140, y + 10], fill=LINE, width=3)
    d.text((40, y + 40), "Re-pinned: PIN-1, PIN-2, PIN-4 (shell and fire sound) +2 ticks = frame 1 at 60 Hz — the only pins that",
           font=font("reg", 34), fill=INK)
    d.text((40, y + 100), "changed, as CHANGE-BRIEF.md line 127 predicted. PIN-3 reload 48 ticks and every other pin unchanged.",
           font=font("reg", 34), fill=INK)
    d.text((40, y + 190), "Two clocks, check C1, 5 runs at each rate:  shell P+2 · FireAnim reaches frame 1 on P+3 · 1 tick = 0.0167 s",
           font=font("mono", 30), fill=TERRA)
    d.text((40, y + 260), "TEST-REPORT.md has no A7 section at 4f88f1b: these numbers come from the logs and commit messages.",
           font=font("serif", 36), fill=SOFT)
    page.save(OUT / "ev-tests.png")


def ev_mutations():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    d.text((40, 20), "Mutations (logs/a7-mutations.txt) · one line each · its own git worktree · control exit 0 first",
           font=font("serif", 46), fill=INK)
    y = table(d, 40, 110, [["", "Mutation", "Caught by", "Verdict"],
                           ["M5", "subname  Dust:frame → Dust:frames", "track_problems (read-back)", "caught"],
                           ["M2", "loop_mode 1 → 0 (brief prediction 1)", "\"track_dust loops LINEAR\"", "caught"],
                           ["M6", "last key → cell 4 (past the sheet)", "frame-range check", "caught"],
                           ["M7", "rig from an empty cache (--import)", "49/0: baked .tres, no importer", "passed, as expected"],
                           ["M3", "frame track continuous (extra)", "\"track_dust discrete\"", "caught"],
                           ["M4", "shell on frame 2 (extra)", "anim_states 11 fails; PIN-1/2/4", "caught"]],
              [120, 1060, 1100, 600], size=30)
    d.line([40, y + 6, 3140, y + 6], fill=LINE, width=3)
    tag(d, (40, y + 40), "BLIND SPOT", fill=TERRA)
    d.text((340, y + 40), "Under M4, C1 still PASSED: shell − clip went from −1 to +1 tick; C1 checks |shell − clip| ≤ 1 only.",
           font=font("reg", 32), fill=INK)
    d.text((40, y + 130), "No headless run can show whether the motion reads: that is the strip and the student's eyes.",
           font=font("serif", 40), fill=SOFT)
    page.save(OUT / "ev-mutations.png")


def ev_dust():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    d.text((40, 16), "Dust strips (the student's FIXTURE captures, frame 70 of each, cropped on the tank, 1.9×)",
           font=font("serif", 44), fill=INK)
    x = 40
    notes = {"v1": "v1 · brown, small", "v2": "v2 · pale, 2× · 0 dust px", "v3": "v3 · DUST_BEHIND 34"}
    for v in ("v1", "v2", "v3"):
        t = strip_tile(CAP / f"dust_strip_{v}.png", 0, (60, 60, 440, 300))
        t = t.resize((round(t.width * 1.9), round(t.height * 1.9)), Image.LANCZOS)
        page.paste(t, (x, 110))
        d.rectangle([x - 2, 108, x + t.width + 1, 110 + t.height + 1], outline=TERRA if v == "v3" else LINE, width=5)
        d.text((x + 6, 110 + t.height + 10), notes[v], font=font("bold", 30), fill=TERRA if v == "v3" else INK)
        x += t.width + 60
    y = 720
    d.text((40, y), "Squash, strip v1 frame N+1", font=font("bold", 34), fill=TERRA)
    d.text((40, y + 60), "Claude: about 5 %, slight (the student's account; not in the repo)", font=font("reg", 30), fill=INK)
    d.text((40, y + 115), "The student, careful look: reads clearly — shoot kept (TUNING.md line 13)", font=font("reg", 30), fill=INK)
    d.text((1640, y), "Dust (TUNING.md revisions 1 and 2)", font=font("bold", 34), fill=TERRA)
    d.text((1640, y + 60), "v2: the student \"I think I can see it\"; Claude: no pale-sand pixel", font=font("reg", 30), fill=INK)
    d.text((1640, y + 115), "cause: DUST_BEHIND 14 put the dust under the hull (rear ≈ 25 px)", font=font("reg", 30), fill=INK)
    d.text((1640, y + 170), "v3: 34 px — visible in all 6 frames, in play, in all 8 facings", font=font("reg", 30), fill=INK)
    page.save(OUT / "ev-dust.png")


if __name__ == "__main__":
    ev_phase(); ev_tests(); ev_mutations(); ev_dust()
    print("wrote", sorted(p.name for p in OUT.glob("ev-*.png")))
