"""Build the still figures (evidence/ev-*.png) for claude-liam-walker-tank-a6-particles (film tooling).
Frame strips are the student's own fixture captures from walker-TANK/captures/ at commit 41a6b8b (read from the
git-archive copy in _scratch/src); they are cropped to the effect and enlarged only, never retouched. Every number
and quote is copied from TUNING.md / TEST-REPORT.md / CHANGE-BRIEF.md / the price logs at 41a6b8b (see FACTCHECK.md).
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
FS = 1.2  # type scale: figures are shown at about 0.55x in the 4K frame

INK, SOFT, TERRA, DARK, PAPER, LINE = "#3D3929", "#564739", "#985039", "#303D34", "#FFFDF8", "#CFC6B5"


def font(kind, size):
    path = {"serif": FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf",
            "bold": FONTS / "Lato/static/Lato-Bold.ttf",
            "reg": FONTS / "Inter/static/Inter_28pt-Regular.ttf",
            "mono": Path(r"C:/Windows/Fonts/consola.ttf"),
            "cjk": Path(r"C:/Windows/Fonts/msyh.ttc")}[kind]
    return ImageFont.truetype(str(path), round(size * FS))


def tag(d, xy, text, size=34, fill=DARK):
    f = font("bold", size)
    w = d.textlength(text, font=f)
    x, y = xy
    d.rounded_rectangle([x, y, x + w + 36, y + round(size * FS) + 22], radius=10, fill=fill)
    d.text((x + 18, y + 9), text, font=f, fill=PAPER)
    return w + 36


def crop(path, box, scale):
    im = Image.open(path).convert("RGB").crop(box)
    return im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)


def strip(d, page, frames, path_fmt, box, scale, x0, y0, gap=18, label_fn=None):
    x = x0
    for n in frames:
        im = crop(path_fmt.format(n=n), box, scale)
        page.paste(im, (x, y0))
        d.rectangle([x - 2, y0 - 2, x + im.width + 1, y0 + im.height + 1], outline=LINE, width=3)
        d.text((x + 6, y0 + im.height + 8), label_fn(n) if label_fn else f"frame {n}", font=font("reg", 34), fill=INK)
        x += im.width + gap
    return x


def table(d, x, y, rows, widths, size=32, head=True, lh=None):
    lh = lh or size + 22
    for i, row in enumerate(rows):
        cx = x
        for j, cell in enumerate(row):
            f = font("bold" if (head and i == 0) else "reg", size)
            d.text((cx, y), cell, font=f, fill=INK if not (head and i == 0) else TERRA)
            cx += widths[j]
        y += lh
        if head and i == 0:
            d.line([x, y - 8, x + sum(widths) - 20, y - 8], fill=LINE, width=3)
    return y


def quote(d, x, y, zh, en, w=None):
    d.rectangle([x, y, x + 8, y + 112], fill=TERRA)
    d.text((x + 28, y), zh, font=font("cjk", 38), fill=INK)
    d.text((x + 28, y + 58), en, font=font("serif", 40), fill=SOFT)


# ---------------------------------------------------------------- B05: Effect A intent + r0 strip + first look
def ev_a_intent():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    d.text((40, 24), "Intent (CHANGE-BRIEF.md, Effect A)", font=font("serif", 54), fill=INK)
    table(d, 40, 110, [["Time", "Phase", "What happens"],
                       ["0–0.07 s", "impact", "pale flash, brightest on frame one"],
                       ["0.07–0.3 s", "outward", "chips fly back out in a fan, braking hard"],
                       ["0.3–0.7 s", "dissipation", "chips stop, darken, fade; dust thins"]],
          [230, 230, 760], size=32)
    d.text((40, 360), "gravity (0, 0) on all three emitters: top-down, chips brake, they don't fall", font=font("reg", 30), fill=SOFT)
    d.text((1330, 24), "My first look (preview window, before any Claude reading)", font=font("serif", 54), fill=INK)
    quote(d, 1330, 110, "闪光看得见，正好。砖块主要往左侧飞，也不错。看得清，大小合适。", "Flash about right; chips fly mainly left; readable; size right.")
    quote(d, 1330, 270, "游戏一切都正常。真的没有想改的地方。", "In the running game: everything works; nothing to change.")
    tag(d, (40, 470), "FIXTURE CAPTURE · captures/cover_hit_burst/r0/ · Movie Maker 30 fps, fixed seed · cropped and enlarged 1.95×")
    strip(d, page, [10, 12, 15, 20, 30, 50], str(CAP / "cover_hit_burst/r0/frame{n:08d}.png"),
          (470, 255, 730, 445), 1.95, 40, 560, gap=12,
          label_fn=lambda n: f"frame {n} · {(n - 10) / 30:.2f} s")
    page.save(OUT / "ev-a-intent.png")


# ---------------------------------------------------------------- B07: r0 vs r1 frame 20
def ev_a_frame20():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    for i, r in enumerate(("r0", "r1")):
        im = crop(CAP / f"cover_hit_burst/{r}/frame00000020.png", (430, 250, 790, 460), 3.0)
        x = 40 + i * (im.width + 40)
        page.paste(im, (x, 110))
        d.rectangle([x - 2, 108, x + im.width + 1, 110 + im.height + 1], outline=LINE, width=3)
        tag(d, (x, 24), f"FIXTURE · {r} · frame 20 (0.33 s) · enlarged 3×")
        d.text((x, 110 + im.height + 14), "before R3: last stop #5A3A2E a0" if r == "r0" else "after R3: + #8E5040 a1 @0.6",
               font=font("reg", 34), fill=INK)
    x = 40 + 2 * (1080 + 40) + 10
    d.text((x, 30), "Claude's comparison (session 4c)", font=font("serif", 50), fill=INK)
    y = 110
    for line in ["Frames 10, 12, 15, 30, 50: held.", "Frame 20: partly held —", "chips visible, red-brown, smaller,",
                 "but fainter and sparser than", "predicted; they reach ~80 px,", "not 50–60.",
                 "Next lever named: chip size", "(scale_amount_curve end, 0.4)."]:
        d.text((x, y), line, font=font("reg", 34), fill=INK)
        y += 52
    d.text((x, y + 30), "My verdict in the running game", font=font("serif", 50), fill=INK)
    d.text((x, y + 110), "保留就行，一切正常。", font=font("cjk", 38), fill=INK)
    d.text((x, y + 165), "不是纯 3D 游戏，目前状态不用纠结。", font=font("cjk", 38), fill=INK)
    d.text((x, y + 225), "Keep it. Not a full 3D game:", font=font("serif", 40), fill=SOFT)
    d.text((x, y + 275), "no more fussing. Lever declined.", font=font("serif", 40), fill=SOFT)
    page.save(OUT / "ev-a-frame20.png")


# ---------------------------------------------------------------- B09: Effect B intent + turbulence + r0 strip
def ev_b_intent():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    d.text((40, 24), "Intent (CHANGE-BRIEF.md, Effect B)", font=font("serif", 54), fill=INK)
    table(d, 40, 110, [["Phase", "What happens"],
                       ["Start", "first wisps rise 0–0.3 s after the threshold hit"],
                       ["Build", "the column fills over one 1.6 s lifetime"],
                       ["Steady", "a continuous, wavering column, denser per hit"],
                       ["Stop", "emission ends; the column drifts off, never cut"]],
          [200, 1000], size=31, lh=50)
    d.text((40, 375), "Scale: a standing tank's column about 2–3 hull lengths tall", font=font("reg", 30), fill=SOFT)
    d.text((1330, 24), "The feature Effect A doesn't use", font=font("serif", 54), fill=INK)
    d.text((1330, 105), "turbulence (GPU-only):  turbulence_enabled = true · noise_strength 2.0 ·", font=font("mono", 32), fill=INK)
    d.text((1330, 150), "noise_scale 4.0 · influence_min / max 0.1 / 0.2   (damage_smoke.tscn 41–45)", font=font("mono", 32), fill=INK)
    d.text((1330, 225), "In the running game, standing still (check 2):", font=font("serif", 46), fill=INK)
    quote(d, 1330, 295, "一团", "a lump on the turret, not a rising column")
    tag(d, (40, 470), "FIXTURE CAPTURE · captures/damage_smoke/r0/ · h 0.5 at frame 10, 0.1 at 60, 1.0 at 110 · cropped, enlarged 2×")
    strip(d, page, [10, 25, 58, 90, 112, 140, 165], str(CAP / "damage_smoke/r0/frame{n:08d}.png"),
          (495, 230, 705, 470), 2.0, 40, 560, gap=19)
    page.save(OUT / "ev-b-intent.png")


# ---------------------------------------------------------------- B15: tests
def ev_tests():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    tag(d, (40, 24), "HEADLESS · recorded logs at 41a6b8b · exit codes from the student's own runs · nothing drawn")
    y = table(d, 40, 120, [["Configuration (60 fps)", "Result"],
                           ["test_cover_hit_burst_config.gd", "128 / 128 · exit 0"],
                           ["test_damage_smoke_config.gd", "76 / 76 · exit 0"]], [1180, 520], size=44, lh=74)
    y = table(d, 40, y + 30, [["Mutation (Effect A)", "Result"],
                              ["Debris initial_velocity_min → initial_velocity", "exit 1 · Godot: no warning"],
                              ["Debris damping_min 400 → 300", "exit 1"]], [1180, 520], size=44, lh=74)
    y = table(d, 40, y + 30, [["State (real loop, real input)", "30 fps", "60 fps", "144 fps"],
                              ["test_cover_hit_burst_state.gd", "82", "82", "82"],
                              ["test_damage_smoke_state.gd", "81", "81", "81"]], [1180, 170, 170, 170], size=44, lh=74)
    x = 1990
    d.text((x, 120), "Two events inside one lifetime", font=font("serif", 50), fill=INK)
    for i, t in enumerate(["two hits 0.317 s apart → 2 bursts alive", "the first freed itself 0.750 s after its own",
                           "start: not restarted"]):
        d.text((x, 200 + i * 56), t, font=font("reg", 38), fill=INK)
    d.text((x, 400), "What no headless run can show", font=font("serif", 50), fill=INK)
    for i, t in enumerate(["anything drawn: the dummy renderer runs no GPU", "particle process — that a particle is emitted,",
                           "the column thinning, the fade after a stop, the", "frozen look, turbulence, the trail."]):
        d.text((x, 480 + i * 56), t, font=font("reg", 38), fill=INK)
    d.text((x, 730), "Test-only setup writes (labelled in the tests)", font=font("serif", 44), fill=INK)
    for i, t in enumerate(["frozen enemy AI · enemy 0 moved into the line of fire", "· visible = false"]):
        d.text((x, 800 + i * 50), t, font=font("reg", 32), fill=SOFT)
    d.text((40, 1130), "Sources: TEST-REPORT.md; logs/test_*_{30,60,144}fps.log; logs/a6_mutation1_godot3_name_60fps.log; "
                       "logs/a6_mutation2_value_drift_60fps.log", font=font("reg", 28), fill=SOFT)
    page.save(OUT / "ev-tests.png")


# ---------------------------------------------------------------- B16: prices
def ev_prices():
    page = Image.new("RGB", (3200, 1200), PAPER)
    d = ImageDraw.Draw(page)
    tag(d, (40, 24), "HEADLESS CPU · price_measure_realtime.log · medians")
    y = table(d, 40, 120, [["Case", "median ms", "diff", "budget"],
                           ["empty control", "0.128", "", ""],
                           ["mode 0 · effects off", "0.181", "", ""],
                           ["mode 1 · A peak", "0.255", "+0.074", "≤ 0.5 ✓"],
                           ["mode 2 · B peak", "0.172", "−0.009 ≈ 0", "GPU node"],
                           ["mode 0 again", "0.201", "+0.020 drift", ""]], [500, 300, 300, 230], size=44, lh=74)
    d.text((40, y + 10), "headless render_gpu reads 0.000 in every case", font=font("reg", 32), fill=SOFT)
    x = 1680
    tag(d, (x, 24), "WINDOWED · RTX 3060 Laptop GPU · logs/price_measure_windowed.log", fill=TERRA)
    y2 = table(d, x, 120, [["Case", "GPU ms", "diff", "budget"],
                           ["mode 0 · effects off", "0.276", "", ""],
                           ["mode 1 · A peak", "0.299", "+0.023", "≤ 0.2 ✓"],
                           ["mode 2 · B peak", "0.353", "+0.077", "≤ 0.3 ✓"],
                           ["mode 0 again", "0.281", "+0.005 drift", ""]], [560, 240, 300, 220], size=44, lh=74)
    d.text((x, y2 + 10), "FPS label: 143–144 in every mode (vsync on); 143 with vsync off (F9) — capped",
           font=font("reg", 32), fill=SOFT)
    d.text((40, 960), "Agent's first cost script: 6.90 ms in every case, the empty scene included = 1/144 s.",
           font=font("reg", 38), fill=INK)
    d.text((40, 1030), "It measured the frame pacing, not the effects; the empty control caught it.",
           font=font("reg", 38), fill=INK)
    d.text((40, 1140), "Sources: TEST-REPORT.md (Headless CPU price, GPU price); FRICTIONAL.md Step 7", font=font("reg", 28), fill=SOFT)
    page.save(OUT / "ev-prices.png")


if __name__ == "__main__":
    for fn in (ev_a_intent, ev_a_frame20, ev_b_intent, ev_tests, ev_prices):
        fn()
        print("wrote", fn.__name__)
