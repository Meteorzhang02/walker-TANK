"""Build the VIDEO beats (media/B03, B07, B09, B10, B11) for claude-liam-walker-tank-a7-animation (film tooling).
Adapted from the A6 reel's make_media.py (same page, fonts, overlay method).
Each beat is a cream page (PIL) with real footage overlaid by ffmpeg, for exactly the beat's padded audio frame count.
Footage: capture/godot/<scenario>/frame%08d.png — this film's 4K Movie Maker captures of the real scenes/main.tscn on a
scratch copy of walker-TANK 4f88f1b, driven by _film/a7_play.gd with SCRIPTED INPUT (and scripted take_damage calls in
the hit/death scenarios). Frames are always in order and only cropped/scaled. Where a beat holds frames (each frame
repeated k times = slowed), or loops a short clip, the page says so. Nothing is retouched, reordered or generated.
Run: python scripts/make_media.py [Bxx ...]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
CAPG = REEL / "capture/godot"
SRC = REEL / "_scratch/src"
WORK = REEL / "capture/work"
WORK.mkdir(parents=True, exist_ok=True)
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
INK, SOFT, TERRA, DARK, PAGE, PAPER, LINE = "#3D3929", "#564739", "#985039", "#303D34", "#FAF9F5", "#FFFDF8", "#CFC6B5"
REV = "4f88f1b"
WIDE = (0, 180, 3328, 2052)     # tank, shell path and the runtime readout
SI = "SCRIPTED INPUT"


def font(kind, size):
    path = {"serif": FONTS / "EB_Garamond/static/EBGaramond-Regular.ttf",
            "bold": FONTS / "Lato/static/Lato-Bold.ttf",
            "reg": FONTS / "Inter/static/Inter_28pt-Regular.ttf",
            "mono": Path(r"C:/Windows/Fonts/consola.ttf")}[kind]
    return ImageFont.truetype(str(path), size)


def page(title, prov):
    im = Image.new("RGB", (3840, 2160), PAGE)
    d = ImageDraw.Draw(im)
    d.text((211, 70), title, font=font("serif", 112), fill=INK)
    d.text((211, 1990), prov, font=font("reg", 30), fill=SOFT)
    f = font("serif", 56)
    d.text((3840 - 211 - d.textlength("@NikBearBrown", font=f), 1975), "@NikBearBrown", font=f, fill=INK)
    return im, d


def pill(d, x, y, text, fill=DARK, size=44):
    f = font("bold", size)
    w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 56, y + size + 34], radius=14, fill=fill)
    d.text((x + 28, y + 14), text, font=f, fill=PAPER)
    return y + size + 34


def frame_box(d, x, y, w, h):
    d.rectangle([x - 5, y - 5, x + w + 4, y + h + 4], outline=LINE, width=6)


def lines(d, x, y, items, size=48, gap=18):
    for it in items:
        k, txt = it if isinstance(it, tuple) else ("reg", it)
        d.text((x, y), txt, font=font("bold" if k == "terra" else k, size), fill=SOFT if k == "serif" else (TERRA if k == "terra" else INK))
        y += size + gap
    return y


def frames_of(bid):
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    return next(b for b in sheet["beats"] if b["beat_id"] == bid)["audio_pad"]["frames"]


def run(cmd):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + cmd, check=True)


def seq_clip(name, scen, frames, crop, w, h, hold=1):
    """Capture frames (a list, in order) -> clip; each frame repeated `hold` times; crop (x0,y0,x1,y1); scale w x h."""
    lst = WORK / f"{name}.txt"
    with lst.open("w", encoding="utf-8") as f:
        for n in frames:
            p = (CAPG / scen / f"frame{n:08d}.png").as_posix()
            f.write(f"file '{p}'\nduration {hold / 30:.6f}\n")
        f.write(f"file '{(CAPG / scen / f'frame{frames[-1]:08d}.png').as_posix()}'\n")
    x0, y0, x1, y1 = crop
    out = WORK / f"{name}.mp4"
    run(["-f", "concat", "-safe", "0", "-i", str(lst), "-vf",
         f"crop={x1 - x0}:{y1 - y0}:{x0}:{y0},scale={w}:{h}:flags=lanczos,fps=30,format=yuv420p",
         "-frames:v", str(len(frames) * hold), "-c:v", "libx264", "-crf", "12", "-preset", "medium", str(out)])
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


PROV = f"Movie Maker 4K · scenes/main.tscn on a scratch copy of {REV} · film driver _film/a7_play.gd · enemies held"


# ---------------------------------------------------------------------------------------------------------------- beats
def B03():
    pg, d = page("The Sheet and the Track That Reads It",
                 "Left: track_dust_sheet.png, 20× nearest, dark backing · right: " + PROV + " · frames 22–64, loops")
    sheet = Image.open(SRC / "assets/game/fx/track_dust_sheet.png").convert("RGBA")
    big = sheet.resize((64 * 20, 16 * 20), Image.NEAREST)
    back = Image.new("RGBA", big.size, (58, 47, 39, 255))
    back.alpha_composite(big)
    x0, y0 = 211, 470
    pill(d, x0, 300, "track_dust_sheet.png · 64 × 16 px")
    pg.paste(back.convert("RGB"), (x0, y0))
    frame_box(d, x0, y0, big.width, big.height)
    for c in range(4):
        cx = x0 + c * 320
        if c:
            d.line([cx, y0, cx, y0 + 320], fill=TERRA, width=4)
        d.text((cx + 120, y0 + 340), f"cell {c}", font=font("bold", 48), fill=INK)
    lines(d, x0, 900, ["16 × 16 cells · hframes 4 · vframes 1",
                       ("mono", "keys 0 / 0.1 / 0.2 / 0.3 s → cells 0, 1, 2, 3"),
                       "each cell: four puffs one life stage apart,", "so cell 3 → cell 0 continues the emission",
                       ("serif", "generated by tools/make_dust_sheet.gd · the student's own work"),
                       ("serif", "no third-party art (ATTRIBUTION.md)")], size=46)
    W, H = 1920, 1080
    xr = 1700
    pill(d, xr, 300, f"{SI} · move_right held · loops", fill=TERRA)
    frame_box(d, xr, 400, W, H)
    a = seq_clip("B03-close", "drive", list(range(22, 65)), (900, 680, 2180, 1400), W, H)
    frame_box(d, xr, 1540, 1920, 180)
    b = seq_clip("B03-readout", "drive", list(range(22, 65)), (40, 1405, 2120, 1600), 1920, 180)
    d.text((xr, 1750), "runtime readout: Dust.frame cycles 0 → 3 while MOVING (film driver, reads only)",
           font=font("reg", 38), fill=SOFT)
    compose("B03", pg, [(a, xr, 400, True), (b, xr, 1540, True)])


def B07():
    pg, d = page("In Play: Drive, Stop, Fire",
                 PROV + " · frames 14–119 in order, each held 2× (half speed) · loops")
    W, H = 2560, 1440
    pill(d, 211, 260, f"{SI} · half speed (each frame held 2×) · loops", fill=TERRA)
    frame_box(d, 211, 380, W, H)
    x = 2900
    lines(d, x, 400, [("bold", "frames 20–64"), "move_right held:", "MOVING · track_dust plays",
                      "DustMount visible", "",
                      ("bold", "frame 65 on"), "released: IDLE", "MotionAnim stopped,", "dust hidden", "",
                      ("bold", "frame 85 = N"), "fire pressed: FIRING", "N+1: Suspension y 2.00,", "shell + flash"],
          size=44, gap=14)
    a = seq_clip("B07-drive", "drive", list(range(14, 120)), WIDE, W, H, hold=2)
    compose("B07", pg, [(a, 211, 380, True)])


def B09():
    pg, d = page("Two Clocks, One Tick Apart",
                 PROV + " · scenario 'drive', frames 84–91 in order, each HELD 48 frames")
    W, H = 2560, 1440
    pill(d, 211, 260, f"{SI} · HELD FRAMES: each capture frame held 1.6 s", fill=TERRA)
    frame_box(d, 211, 380, W, H)
    x = 2900
    lines(d, x, 400, [("bold", "frame 85 = N"), "press tick P = its first tick", "2 physics ticks per frame", "",
                      ("bold", "Check C1 (5 runs each,"), ("bold", "30 · 60 · 144):"),
                      ("mono", "P+2  shell spawns"), ("mono", "P+3  clip at frame 1"),
                      ("mono", "      (0.0333 s)"), "", ("terra", "1 tick = 0.0167 s"),
                      ("serif", "the shell leaves one tick"), ("serif", "before the dip shows")], size=44, gap=14)
    a = seq_clip("B09-held", "drive", list(range(84, 92)), WIDE, W, H, hold=48)
    compose("B09", pg, [(a, 211, 380, False)])


def B10():
    pg, d = page("Interrupts in Each Phase",
                 f"Movie Maker 4K · scratch copy of {REV} · 'hits': scripted take_damage(10) · N−1…N+6 held 5×, loops · 2nd press is also inside the reload; guard alone: test G1")
    W, H = 1352, 760
    pos = [(211, 250), (2277, 250), (211, 1110), (2277, 1110)]
    shots = [(30, "hit on tick 1 · STARTUP: shot goes"), (60, "hit on tick 2 · ACTIVE: shot goes"),
             (90, "hit on tick 5 · RECOVERY: shot goes"), (120, "2nd fire on tick 4 · ignored")]
    ov = []
    for i, ((n, lab), (x, y)) in enumerate(zip(shots, pos)):
        pill(d, x, y, f"{SI} · {lab}", fill=TERRA if i == 3 else DARK, size=40)
        frame_box(d, x, y + 84, W, H)
        ov.append((seq_clip(f"B10-{n}", "hits", list(range(n - 1, n + 7)), WIDE, W, H, hold=5), x, y + 84, True))
    compose("B10", pg, ov)


def B11():
    pg, d = page("A Death in Each Phase: the Shot Finishes",
                 PROV + " · scripted take_damage(100000) · frames 29–40, each held 4× · loops")
    W, H = 1080, 658
    crop = (0, 560, 2200, 1900)
    ov = []
    for i, (scen, lab) in enumerate((("death_s", "death on tick 1 · STARTUP"), ("death_a", "death on tick 2 · ACTIVE"),
                                     ("death_r", "death on tick 5 · RECOVERY"))):
        x = 211 + i * (W + 59)
        pill(d, x, 300, f"{SI} · {lab}", size=38)
        frame_box(d, x, 400, W, H)
        ov.append((seq_clip(f"B11-{scen}", scen, list(range(29, 41)), crop, W, H, hold=4), x, 400, True))
    lines(d, 211, 1200, ["Each: one shell + muzzle flash + sound on tick 2, weapon READY on tick 10, no new shot.",
                         ("serif", "The weapon tick runs before the is_dead return (tank.gd lines 164–168).")], size=46)
    compose("B11", pg, ov)


ALL = {"B03": B03, "B07": B07, "B09": B09, "B10": B10, "B11": B11}

if __name__ == "__main__":
    for bid in (sys.argv[1:] or ALL):
        ALL[bid]()
