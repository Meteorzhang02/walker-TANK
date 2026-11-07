"""Build the VIDEO beats (media/B02, B04, B08, B11, B12, B14, B17) for claude-liam-walker-tank-a6-particles (film tooling).
Each beat is a cream page (PIL) with real footage overlaid by ffmpeg, for exactly the beat's padded audio frame count.
Footage:
  - capture/godot/*: this film's 4K Movie Maker FIXTURE captures of walker-TANK preview scenes (scratch copy of 41a6b8b);
    frames in order, cropped/scaled only; a fixture clip shorter than its beat loops, and says so on screen.
  - D:/CSYE7270/a6-play.mp4: the student's own play recording (1280x720, 48 fps), frames in order from a stated start,
    shown at 30 fps by dropping frames (no speed change), scaled only. Its audio is not used.
  - captures/damage_smoke/r0, r1: the student's fixture strips at 41a6b8b (from _scratch/src), cropped and enlarged.
No footage is retimed, reordered, retouched or generated. The price capture's FPS label is covered by a labelled patch,
because under Movie Maker it shows offline render speed, not game FPS.
Run: python scripts/make_media.py [Bxx ...]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
CAPG = REEL / "capture/godot"
STRIPS = REEL / "_scratch/src/captures"
PLAY = Path(r"D:/CSYE7270/a6-play.mp4")
WORK = REEL / "capture/work"
WORK.mkdir(parents=True, exist_ok=True)
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
INK, SOFT, TERRA, DARK, PAGE, PAPER, LINE = "#3D3929", "#564739", "#985039", "#303D34", "#FAF9F5", "#FFFDF8", "#CFC6B5"
REV = "41a6b8b"


def font(kind, size):
    path = {"serif": FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf",
            "bold": FONTS / "Lato/static/Lato-Bold.ttf",
            "reg": FONTS / "Inter/static/Inter_28pt-Regular.ttf",
            "mono": Path(r"C:/Windows/Fonts/consola.ttf"),
            "cjk": Path(r"C:/Windows/Fonts/msyh.ttc")}[kind]
    return ImageFont.truetype(str(path), size)


def page(title, prov):
    im = Image.new("RGB", (3840, 2160), PAGE)
    d = ImageDraw.Draw(im)
    d.text((211, 70), title, font=font("serif", 112), fill=INK)
    d.text((211, 1990), prov, font=font("reg", 40), fill=SOFT)
    f = font("serif", 56)
    d.text((3840 - 211 - d.textlength("@NikBearBrown", font=f), 1975), "@NikBearBrown", font=f, fill=INK)
    return im, d


def pill(d, x, y, text, fill=DARK, size=46):
    f = font("bold", size)
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 56, y + size + 34], radius=14, fill=fill)
    d.text((x + 28, y + 14), text, font=f, fill=PAPER)
    return y + size + 34


def frame_box(d, x, y, w, h):
    d.rectangle([x - 5, y - 5, x + w + 4, y + h + 4], outline=LINE, width=6)


def lines(d, x, y, items, size=48, gap=18, kind="reg", fill=INK):
    for it in items:
        k, txt = (it if isinstance(it, tuple) else (kind, it))
        f = font(k, size)
        d.text((x, y), txt, font=f, fill=fill if k != "serif" else SOFT)
        y += size + gap
    return y


def frames_of(bid):
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    return next(b for b in sheet["beats"] if b["beat_id"] == bid)["audio_pad"]["frames"]


def run(cmd):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + cmd, check=True)


def seq_clip(name, src, start, count, crop, w, h):
    """Fixture PNG sequence -> intermediate clip (frames start..start+count-1 in order; crop x,y,cw,ch; scale w x h)."""
    out = WORK / f"{name}.mp4"
    cx, cy, cw, ch = crop
    run(["-framerate", "30", "-start_number", str(start), "-i", str(CAPG / src / "frame%08d.png"),
         "-frames:v", str(count), "-vf", f"crop={cw}:{ch}:{cx}:{cy},scale={w}:{h}:flags=lanczos,format=yuv420p",
         "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-r", "30", str(out)])
    return out


def play_clip(name, start, nframes, w, h):
    """The student's play recording from `start` s, frames in order, 48 -> 30 fps by dropping frames, scaled only."""
    out = WORK / f"{name}.mp4"
    run(["-ss", f"{start:.3f}", "-i", str(PLAY), "-an", "-vf", f"fps=30,scale={w}:{h}:flags=lanczos,format=yuv420p",
         "-frames:v", str(nframes), "-c:v", "libx264", "-crf", "12", "-preset", "medium", str(out)])
    return out


def compose(bid, pg, overlays):
    """overlays: [(clip, x, y, loop)] over the page, for exactly the beat's frames."""
    n = frames_of(bid)
    pgp = WORK / f"{bid}-page.png"
    pg.save(pgp)
    args = ["-loop", "1", "-framerate", "30", "-i", str(pgp)]
    for clip, _, _, loop in overlays:
        args += (["-stream_loop", "-1"] if loop else []) + ["-i", str(clip)]
    chain, last = [], "[0:v]"
    for i, (_, x, y, loop) in enumerate(overlays, start=1):
        tag = f"[v{i}]"
        chain.append(f"{last}[{i}:v]overlay={x}:{y}:eof_action=repeat{tag}")
        last = tag
    chain.append(f"{last}format=yuv420p[out]")
    run(args + ["-filter_complex", ";".join(chain), "-map", "[out]", "-an", "-r", "30", "-frames:v", str(n),
                "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-threads", "4", str(REEL / f"media/{bid}.mp4")])
    print(bid, n, "frames")


# ---------------------------------------------------------------------------------------------------------------- beats
def B02():
    pg, d = page("Two Effects, Two Jobs",
                 f"FIXTURE captures: walker-TANK previews at {REV}, Movie Maker 30 fps, 3840 × 2160, RTX 3060 · cropped to the effect (1.7×), frames in order")
    W, H = 1640, 922
    pill(d, 211, 260, "A · FIXTURE · cover_hit_burst_preview · loops")
    pill(d, 1989, 260, "B · FIXTURE · damage_smoke_preview")
    frame_box(d, 211, 360, W, H); frame_box(d, 1989, 360, W, H)
    lines(d, 211, 1320, [("bold", "Job: “your shell landed on that wall, right there”"),
                         "3 × CPUParticles2D: Flash, Debris, Dust",
                         ("mono", "event: cover.gd take_hit() → line 40"),
                         ("mono", "world.spawn_cover_burst(_shell, …)")], size=46)
    lines(d, 1989, 1320, [("bold", "Job: “this tank is badly hurt, and how badly”"),
                          "GPUParticles2D + ParticleProcessMaterial",
                          "on when health / max_health ≤ 0.6; amount_ratio follows health",
                          "a wreck smokes at 1.0 · preview: h 0.5 → 0.1 → 1.0"], size=46)
    a = seq_clip("B02-burst", "burst_single", 0, 60, (1322, 777, 960, 540), W, H)
    b = seq_clip("B02-smoke", "smoke", 0, 170, (1320, 700, 960, 540), W, H)
    compose("B02", pg, [(a, 211, 360, True), (b, 1989, 360, True)])


def B04():
    pg, d = page("Here It Runs, There It Costs Nothing",
                 f"FIXTURE: damage_smoke_preview at {REV}, Movie Maker 4K, RTX 3060 · loops · headless numbers: logs/price_measure_realtime.log")
    W, H = 2400, 1350
    pill(d, 211, 260, "FIXTURE · damage_smoke_preview · 4K Movie Maker on the RTX 3060 · cropped · loops")
    frame_box(d, 211, 360, W, H)
    x = 2720
    pill(d, x, 360, "HEADLESS · recorded", fill=TERRA)
    lines(d, x, 480, [("serif", "Effect B, price mode 2"), ("serif", "minus mode 0 (medians):"),
                      ("bold", "process −0.009 ms ≈ 0"), ("bold", "render_gpu 0.000"), "",
                      "The dummy renderer runs", "no GPU particle process.", "Headless sees only the",
                      "node's CPU bookkeeping."], size=52, gap=22)
    a = seq_clip("B04-smoke", "smoke", 0, 170, (840, 420, 1920, 1080), W, H)
    compose("B04", pg, [(a, 211, 360, True)])


def B08():
    pg, d = page("Effect A in Play",
                 "Left: D:/CSYE7270/a6-play.mp4 from 12.8 s, frames in order, 48 → 30 fps, scaled · right: FIXTURE, retrigger on (scratch copy)")
    W, H = 2400, 1350
    pill(d, 211, 260, "MY PLAY RECORDING · not a fixture", fill=TERRA)
    frame_box(d, 211, 360, W, H)
    x, w2, h2 = 2720, 910, 512
    pill(d, x, 260, "FIXTURE · retrigger on · loops")
    frame_box(d, x, 360, w2, h2)
    lines(d, x, 920, ["second burst at frame 16,", "0.2 s after the first:", "two bursts alive at once.", "",
                      ("serif", "In the recording: hits at"), ("serif", "≈ 13.3, 14.2, 15.1 s on one"),
                      ("serif", "wall, each its own burst."),
                      ("serif", "Rapid hits from several tanks:"), ("serif", "not checked separately.")], size=44, gap=16)
    a = play_clip("B08-play", 12.8, frames_of("B08"), W, H)
    b = seq_clip("B08-retrigger", "burst_retrigger", 0, 60, (1260, 690, 1280, 720), w2, h2)
    compose("B08", pg, [(a, 211, 360, False), (b, x, 360, True)])


def B11():
    pg, d = page("Effect B: The Strip Said Lump, the Game Said Column",
                 "Left: captures/damage_smoke/r0, r1 (student's fixture strips at 41a6b8b), enlarged 2.5× · right: a6-play.mp4 from 29.0 s, frames in order")
    pill(d, 211, 260, "FIXTURE STRIPS · same seed · stills")
    cell = 600
    for r, run_ in enumerate(("r0", "r1")):
        for c, n in enumerate((58, 140)):
            im = Image.open(STRIPS / f"damage_smoke/{run_}/frame{n:08d}.png").convert("RGB").crop((480, 220, 720, 460))
            im = im.resize((cell, cell), Image.LANCZOS)
            x, y = 330 + c * (cell + 30), 420 + r * (cell + 30)
            pg.paste(im, (x, y)); frame_box(d, x, y, cell, cell)
            if r == 0:
                d.text((x + 10, 368), f"frame {n}", font=font("bold", 40), fill=INK)
        d.text((220, 420 + r * (cell + 30) + cell // 2 - 30), run_, font=font("bold", 56), fill=INK)
    lines(d, 211, 1700, [("bold", "Claude (session 7c): “prediction failed”"),
                         "still a lump, only 5–10 px higher"], size=46)
    W, H = 1998, 1124
    x = 1629
    pill(d, x, 260, "MY PLAY RECORDING · not a fixture", fill=TERRA)
    frame_box(d, x, 420, W, H)
    d.text((x, 1600), "In the game: 是柱子，保留，往上升", font=font("cjk", 50), fill=INK)
    lines(d, x, 1680, [("serif", "“It's a column; keep it. It rises.” The student overruled"),
                       ("serif", "the strip reading: a still frame can't show a rise.")], size=50, gap=8)
    a = play_clip("B11-play", 29.0, frames_of("B11"), W, H)
    compose("B11", pg, [(a, x, 420, False)])


def B12():
    pg, d = page("Start, Stop and Pause",
                 "Left: D:/CSYE7270/a6-play.mp4 from 39.4 s, frames in order, 48 → 30 fps · right: TEST-REPORT.md and TUNING.md (state test, game checks)")
    W, H = 2200, 1238
    pill(d, 211, 260, "MY PLAY RECORDING · paused 40–43 s, then resumed", fill=TERRA)
    frame_box(d, 211, 360, W, H)
    x = 2540
    pill(d, x, 260, "HEADLESS · state test 81/81 at 30, 60, 144")
    y = lines(d, x, 380, ["load: no smoke (rule 7)", "threshold hit: on (rule 3)", "respawn: off on the first",
                          "  frame after (rule 4)", "wreck: still smoking at 1.0", "paused: nothing changes (5)"],
              size=44, gap=14)
    pill(d, x, y + 30, "IN THE GAME · the student's checks", fill=TERRA)
    y = y + 140
    for zh, en in (("有", "denser on a further hit"), ("拖烟条", "a trail while driving"),
                   ("对", "frozen under pause"), ("会", "the wreck keeps smoking")):
        d.text((x, y), zh, font=font("cjk", 44), fill=INK)
        d.text((x + 190, y + 2), en, font=font("reg", 44), fill=INK)
        y += 66
    lines(d, x, y + 10, [("serif", "Stop on respawn: headless only,"), ("serif", "not checked by eye.")], size=44, gap=6)
    a = play_clip("B12-play", 39.4, frames_of("B12"), W, H)
    compose("B12", pg, [(a, 211, 360, False)])


def B14():
    pg, d = page("That's the Lump",
                 f"FIXTURE: damage_smoke_preview at {REV}, Movie Maker 4K, frames 30–169 in order, cropped on the turret and enlarged 1.5× · loops")
    W, H = 2400, 1350
    pill(d, 211, 260, "FIXTURE · enlarged on the turret · loops")
    frame_box(d, 211, 360, W, H)
    x = 2720
    lines(d, x, 380, [("serif", "Line 447, every step:"), ("mono", "v = mix(v, noise·|v|, 0.1–0.2)"), "",
                      "share of the upward", "heading left ≈ 0.85ⁿ:", "≈ 0.38 after 0.2 s,", "< 0.01 after 1 s",
                      ("serif", "(LANGUAGE-NOTES.md)"), "",
                      ("bold", "Confirmed from the code,"), ("bold", "not by a turbulence-off"), ("bold", "strip.")],
          size=46, gap=16)
    a = seq_clip("B14-smoke", "smoke", 30, 140, (1160, 520, 1600, 900), W, H)
    compose("B14", pg, [(a, 211, 360, True)])


def B17():
    pg, d = page("The Price Scene, and the Script That Measured Itself",
                 f"FIXTURE: previews/price_scene.tscn at {REV}, Movie Maker 4K · scripted key events (key 1 at frame 30, key 3 at frame 240) · frames in order")
    W, H = 2400, 1350
    pill(d, 211, 260, "FIXTURE · scripted key events: mode 1, then mode 3")
    frame_box(d, 211, 360, W, H)
    x = 2720
    lines(d, x, 380, [("serif", "Agent's first cost script"), ("bold", "6.90 ms in every case,"), ("bold", "empty scene included"),
                      "= 1/144 s: it measured", "the frame pacing.", "The empty control", "caught it.", "",
                      ("serif", "FPS (windowed runs):"), ("bold", "143–144 in every mode;"), ("bold", "143 with vsync off"),
                      "capped at the 144 Hz", "refresh: shows nothing"], size=46, gap=14)
    a = seq_clip("B17-price", "price", 0, 450, (0, 0, 3840, 2160), W, H)
    # Patch over the price scene's FPS label (offline Movie Maker speed, not game FPS); the patch says so.
    patch = Image.new("RGB", (1130, 92), "#985039")
    pd = ImageDraw.Draw(patch)
    pd.text((18, 18), "FPS label covered: Movie Maker renders offline", font=font("bold", 44), fill=PAPER)
    pp = WORK / "B17-patch.png"
    patch.save(pp)
    sx = W / 3840
    px, py = 211 + round(30 * sx), 360 + round(222 * sx)
    pclip = WORK / "B17-patch.mp4"
    run(["-loop", "1", "-framerate", "30", "-i", str(pp), "-frames:v", "1", "-c:v", "libx264", "-pix_fmt", "yuv444p", str(pclip)])
    compose("B17", pg, [(a, 211, 360, False), (pclip, px, py, False)])


ALL = {"B02": B02, "B04": B04, "B08": B08, "B11": B11, "B12": B12, "B14": B14, "B17": B17}

if __name__ == "__main__":
    for bid in (sys.argv[1:] or ALL):
        ALL[bid]()
