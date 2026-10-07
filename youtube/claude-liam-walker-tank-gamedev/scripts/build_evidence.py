"""Build the still evidence panels for the film from the game's own files (film tooling, not game code).
Every panel only arranges and labels existing files; no pixel of a source image is repainted.
Run: python scripts/build_evidence.py   (from the reel folder)
"""
import json, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1]
OUT = REEL / "evidence"
OUT.mkdir(exist_ok=True)
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
MED = str(FONTS / "Inter/static/Inter_28pt-Medium.ttf")
REG = str(FONTS / "Inter/static/Inter_28pt-Regular.ttf")
MONO = str(FONTS / "PT_Mono/PTMono-Regular.ttf")
INK = (61, 57, 41)
SOFT = (110, 100, 84)
RUST = (152, 80, 57)
PAPER = (255, 253, 248)
W, H = 3300, 1200


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(im, box_w, box_h, bg=None):
    im = im.convert("RGBA")
    s = min(box_w / im.width, box_h / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    if bg is not None:
        base = Image.new("RGBA", im.size, bg)
        base.alpha_composite(im)
        im = base
    return im


def panel_row(items, path, label_size=62, sub_size=52, gap=60, top=30, img_h=880, bg=PAPER, arrows=False):
    """items: list of (image, title, subtitle). Equal-width columns, labels under each image."""
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    n = len(items)
    col_w = (W - gap * (n + 1)) // n
    for i, (im, title, sub) in enumerate(items):
        x0 = gap + i * (col_w + gap)
        t = fit(im, col_w, img_h)
        canvas.paste(t, (x0 + (col_w - t.width) // 2, top + (img_h - t.height) // 2), t)
        d.text((x0 + col_w // 2, top + img_h + 30), title, font=font(MED, label_size), fill=INK, anchor="ma")
        if sub:
            d.text((x0 + col_w // 2, top + img_h + 30 + label_size + 18), sub, font=font(REG, sub_size), fill=SOFT, anchor="ma")
        if arrows and i < n - 1:
            ax = x0 + col_w + gap // 2
            ay = top + img_h // 2
            d.polygon([(ax - 18, ay - 26), (ax + 18, ay), (ax - 18, ay + 26)], fill=RUST)
    canvas.save(path)
    return path


def g(rel):
    return Image.open(GAME / rel)


def checker(size, sq=24):
    a = np.indices(size[::-1]).sum(axis=0) // sq % 2
    c = np.where(a[..., None] == 0, 232, 205).astype(np.uint8)
    return Image.fromarray(np.repeat(c, 3, axis=2), "RGB").convert("RGBA")


def on_checker(im):
    im = im.convert("RGBA")
    base = checker(im.size)
    base.alpha_composite(im)
    return base


def wav_image(rel, w=900, h=220, color=(46, 88, 150)):
    with wave.open(str(GAME / rel)) as wf:
        n = wf.getnframes(); ch = wf.getnchannels(); sw = wf.getsampwidth(); sr = wf.getframerate()
        raw = np.frombuffer(wf.readframes(n), dtype=np.int16 if sw == 2 else np.int32).astype(np.float32)
    x = raw.reshape(-1, ch).mean(axis=1)
    x /= max(1.0, np.abs(x).max())
    im = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(im)
    per = max(1, len(x) // w)
    for i in range(w):
        seg = x[i * per:(i + 1) * per]
        if len(seg) == 0:
            break
        lo, hi = seg.min(), seg.max()
        d.line([(i, h / 2 - hi * h * 0.45), (i, h / 2 - lo * h * 0.45)], fill=color)
    return im, len(x) / sr


def build():
    made = {}
    # 1. Character sheet: the silhouette test as drawn (Claude, code-drawn planning image).
    made["silhouette"] = panel_row([(g("design/character/silhouette.png"),
        "design/character/silhouette.png", "box model in black at about 64 px, then enlarged 2.5x")],
        OUT / "ev-silhouette.png", img_h=1000, top=20)
    # 2. v1 guide and the three rejected v1 results (the student's own thumbnails, unedited).
    made["v1_rejects"] = panel_row([
        (g("design/guides/guide_hull_right.png"), "v1 guide (code-drawn)", "design/guides/guide_hull_right.png"),
        (g("design/asset-log/rejected/REJ-01_CHAR-hull_right_v1_d055.png"), "REJ-01 · denoise 0.55", "flat colour blocks"),
        (g("design/asset-log/rejected/REJ-02_CHAR-hull_right_v1_d070.png"), "REJ-02 · denoise 0.70", "still flat"),
        (g("design/asset-log/rejected/REJ-03_CHAR-hull_right_v1_d080.png"), "REJ-03 · denoise 0.80", "panels appear, blade lost"),
    ], OUT / "ev-v1-rejects.png", img_h=880, arrows=True)
    # 3. v1 guide beside the v2 guide that draw_guides_v2.py produced.
    made["v1_v2"] = panel_row([
        (g("design/guides/guide_hull_right.png"), "v1 guide", "flat fills, black outlines"),
        (g("design/guides/v2/guide2_hull_right.png"), "v2 guide", "gradients, grain, road wheels, panel lines"),
    ], OUT / "ev-v1-v2-guides.png", img_h=900, arrows=True)
    # 4. v2 guide -> raw SDXL output, with the settings read back from the output file itself.
    raw = GAME / "assets/raw/hull/CHAR-hull_right_00001_.png"
    meta = json.loads(Image.open(raw).info["prompt"])
    ks = next(n["inputs"] for n in meta.values() if n["class_type"] == "KSampler")
    texts = [n["inputs"]["text"] for n in meta.values() if n["class_type"] == "CLIPTextEncode"]
    ckpt = next(n["inputs"]["ckpt_name"] for n in meta.values() if n["class_type"] == "CheckpointLoaderSimple")
    guide = next(n["inputs"]["image"] for n in meta.values() if n["class_type"] == "LoadImage")
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    for i, (im, title) in enumerate([(g("design/guides/v2/guide2_hull_right.png"), ("input guide", guide)),
                                     (Image.open(raw), ("raw SDXL output", "CHAR-hull_right_00001_.png"))]):
        x0 = 40 + i * 820
        t = fit(im, 560, 560)
        canvas.paste(t, (x0 + (760 - t.width) // 2, 140), t)
        d.text((x0 + 380, 830), title[0], font=font(MED, 54), fill=INK, anchor="ma")
        d.text((x0 + 380, 900), title[1], font=font(REG, 46), fill=SOFT, anchor="ma")
    d.polygon([(788, 390), (822, 420), (788, 450)], fill=RUST)
    x = 1700
    d.text((x, 40), "Read from the output PNG's own metadata", font=font(MED, 56), fill=RUST)
    rows = [("model", ckpt), ("guide", guide), ("seed", str(ks["seed"])),
            ("steps / cfg", f'{ks["steps"]} / {ks["cfg"]}'), ("sampler", f'{ks["sampler_name"]} · {ks["scheduler"]}'),
            ("denoise", str(ks["denoise"]))]
    y = 135
    for k, v in rows:
        d.text((x, y), k, font=font(REG, 48), fill=SOFT)
        d.text((x + 330, y), v, font=font(MONO, 50), fill=INK)
        y += 70
    y += 25
    d.text((x, y), "positive prompt", font=font(REG, 48), fill=SOFT); y += 66
    words = texts[0].split(); line = ""
    for wd in words:
        if d.textlength(line + " " + wd, font=font(REG, 46)) > W - x - 40:
            d.text((x, y), line.strip(), font=font(REG, 46), fill=INK); y += 58; line = ""
        line += " " + wd
    d.text((x, y), line.strip(), font=font(REG, 46), fill=INK)
    canvas.save(OUT / "ev-raw-output.png")
    made["raw_output"] = OUT / "ev-raw-output.png"
    (OUT / "raw-output-metadata.json").write_text(json.dumps({"file": "assets/raw/hull/CHAR-hull_right_00001_.png",
        "ckpt": ckpt, "guide": guide, "ksampler": ks, "prompts": texts}, indent=1), encoding="utf-8")
    # 5/6. The student's own check sheets, unchanged (placed on paper).
    made["check_hull"] = panel_row([(g("design/asset-log/check_hull_v2.png"), "design/asset-log/check_hull_v2.png",
        "rows: cutout · red = v2 guide outline · + turret guide · 64 px on mud + silhouette")], OUT / "ev-check-hull-v2.png", img_h=1000, top=10)
    made["final8"] = panel_row([(g("design/asset-log/check_final_8dir.png"), "design/asset-log/check_final_8dir.png",
        "hull + turret, stripe painted, olive matched to #4B5320; bottom row at 64 px")], OUT / "ev-final-8dir.png", img_h=900, top=60)
    # 7. Which model made which asset (the real files, grouped by their source in ASSET-LOG/SOURCES).
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    d.text((60, 20), "Stable Diffusion XL Base 1.0 (local ComfyUI)", font=font(MED, 58), fill=RUST)
    x = 60
    for rel in ["assets/game/yunqiz/hull_right.png", "assets/game/yunqiz/hull_up.png", "assets/game/yunqiz/turret_right.png",
                "assets/game/yunqiz/turret_down.png", "assets/game/env/cover_intact.png", "assets/game/env/cover_cracked.png",
                "assets/game/env/cover_broken.png", "assets/game/env/ground_tile.png"]:
        t = fit(on_checker(g(rel)) if "ground" not in rel else g(rel), 330, 330)
        canvas.paste(t, (x, 105), t)
        d.text((x + 165, 445), Path(rel).stem, font=font(REG, 42), fill=SOFT, anchor="ma")
        x += 400
    d.text((60, 525), "Stable Audio 3 Small-SFX", font=font(MED, 58), fill=RUST)
    d.text((1700, 525), "Stable Audio 3 Small-Music", font=font(MED, 58), fill=RUST)
    pos = [(60, 615), (860, 615), (60, 900), (860, 900)]
    for (px, py), rel in zip(pos, ["assets/audio/sfx/SFX-fire.wav", "assets/audio/sfx/SFX-cover-hit.wav",
                                   "assets/audio/sfx/SFX-player-hit.wav", "assets/audio/sfx/SFX-explode.wav"]):
        im, dur = wav_image(rel, 720, 170)
        canvas.paste(im, (px, py + 64))
        d.text((px, py), f"{Path(rel).stem} · {dur:.2f} s", font=font(REG, 46), fill=INK)
    im, dur = wav_image("assets/audio/sfx/SFX-victory.wav", 1500, 150)
    canvas.paste(im, (1700, 680)); d.text((1700, 615), f"SFX-victory · {dur:.2f} s", font=font(REG, 46), fill=INK)
    d.text((1700, 850), "MUS-battle-loop · 8 bars, 70 BPM, 27.43 s", font=font(REG, 46), fill=INK)
    d.text((1700, 950), "Code, not a model: muzzle flash, smoke, fire,", font=font(REG, 44), fill=SOFT)
    d.text((1700, 1010), "explosion, hit flash, recoil, enemy grey tint.", font=font(REG, 44), fill=SOFT)
    d.text((1700, 1070), "Claude, code-drawn: guides, masks, sketches.", font=font(REG, 44), fill=SOFT)
    canvas.save(OUT / "ev-models.png"); made["models"] = OUT / "ev-models.png"
    # 8. A decision on record: turret denoise 0.75 (REJ-08) against the accepted 0.60 down-right turret.
    made["decision"] = panel_row([
        (on_checker(g("assets/sprites/yunqiz/turret/CHAR-turret_down_right.png")), "accepted · T-04 · denoise 0.60", "cupola, stripe, guide shape kept"),
        (g("design/asset-log/rejected/REJ-08_CHAR-turret_down-right_v3_d075_no-stripe.png"), "rejected · T-05 · denoise 0.75", "most detail, but stripe gone, shape drifts"),
    ], OUT / "ev-turret-decision.png", img_h=880)
    return made


if __name__ == "__main__":
    for k, v in build().items():
        print(k, v)


def test_output_panel():
    """Recorded stdout of tests/test_sound_triggers.gd, verbatim, typeset as a terminal view."""
    lines = (REEL / "tests/test-run-01-stdout.txt").read_text(encoding="utf-8").splitlines()
    lines = [l for l in lines if l.strip()]
    canvas = Image.new("RGB", (W, H), (32, 37, 49))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, 96], fill=(52, 61, 77))
    d.text((40, 22), "Recorded output · isolated copy of commit 4616fc7 · exit code 0", font=font(MED, 48), fill=(237, 241, 247))
    d.text((40, 128), "$ godot --headless --path . -s res://tests/test_sound_triggers.gd", font=font(MONO, 50), fill=(139, 199, 243))
    y = 205
    for l in lines:
        col = (174, 231, 209) if l.startswith("PASS") else (236, 224, 161) if l.startswith(("WARNING", "ERROR", "   at")) else (237, 241, 247)
        d.text((40, y), l, font=font(MONO, 52 if not l.startswith("   at") else 44), fill=col)
        y += 66 if not l.startswith("   at") else 56
    canvas.save(OUT / "ev-test-output.png")
    return OUT / "ev-test-output.png"


if __name__ == "__main__" and "--test-panel" in sys.argv:
    print(test_output_panel())


def text_panel(path, columns, title_size=58, body_size=48, line_gap=18):
    """columns: list of (heading, [lines]). Plain typeset text panel (verbatim quotes are marked by the caller)."""
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    n = len(columns); gap = 80
    col_w = (W - gap * (n + 1)) // n
    for i, (head, lines) in enumerate(columns):
        x = gap + i * (col_w + gap); y = 40
        d.text((x, y), head, font=font(MED, title_size), fill=RUST); y += title_size + 34
        for ln in lines:
            style = REG
            if ln.startswith("**"):
                style, ln = MED, ln[2:]
            words = ln.split(" "); cur = ""
            for wd in words:
                if d.textlength((cur + " " + wd).strip(), font=font(style, body_size)) > col_w:
                    d.text((x, y), cur.strip(), font=font(style, body_size), fill=INK); y += body_size + 12; cur = ""
                cur += " " + wd
            d.text((x, y), cur.strip(), font=font(style, body_size), fill=INK); y += body_size + 12 + line_gap
    canvas.save(path)
    return path


def doc_panels():
    out = {}
    out["assignment"] = text_panel(OUT / "ev-assignment.png", [
        ("Assignment 2 brief: minimum in the running slice", [
            "**Art",
            "Your main character's in-game appearance in at least two states (sprite frames, a sprite sheet, or a 3D model) and at least one environment asset (background, tiles, prop, or hazard).",
            "**Sound effects",
            "At least four events from your game's core loop, each with its own sound.",
            "**Music",
            "At least one loop that plays during the slice and repeats without an audible click or gap.",
        ]),
    ], title_size=72, body_size=70, line_gap=44)
    out["gaps"] = text_panel(OUT / "ev-gaps.png", [
        ("Logs disagree: the kept down turret", [
            "**ASSET-LOG.md, row T-12",
            "denoise 0.60, seed randomized and not recorded",
            "**The file's own metadata (CHAR-turret_down_00009_.png)",
            "denoise 0.55, seed 499619143762383, guide guide31_turret_down.png",
            "**FRICTIONAL.md",
            "denoise 0.55, seed 499619143762383 (agrees with the file)",
        ]),
        ("Referenced, but not in commit 4616fc7", [
            "ASSET-LOG rows E-01 to E-04 (cover, ground)",
            "design/test/gallery-yunqiz.png",
            "design/asset-log/env/check_scene_v1.png, v2",
            "TEST-REPORT: revision still \"[commit SHA]\"",
            "TEST-REPORT: fresh-copy run still \"to do\"",
        ]),
    ], title_size=62, body_size=58, line_gap=34)
    return out


if __name__ == "__main__" and "--doc-panels" in sys.argv:
    for k, v in doc_panels().items():
        print(k, v)


def muted_panel():
    return panel_row([(g("design/test/play-05-muted.png"), "design/test/play-05-muted.png",
                       "the student's own muted playtest: Music OFF (M), Sound OFF (N)")], OUT / "ev-muted.png", img_h=1000, top=10)


if __name__ == "__main__" and "--muted" in sys.argv:
    print(muted_panel())


def healthbar_panel():
    """Before: the student's screenshot (default grey fill). After: three frames of run-01 (frames 100, 380, 450)."""
    canvas = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(canvas)
    before = g("design/test/play-01-normal-combat.png").convert("RGB").crop((0, 86, 450, 122))
    before = before.resize((before.width * 1320 // 450, before.height * 1320 // 450), Image.LANCZOS)
    d.text((60, 40), "Before · design/test/play-01-normal-combat.png (student's screenshot)", font=font(MED, 52), fill=RUST)
    canvas.paste(before, (60, 120))
    d.text((60, 270), "After · run-01, this take (frames 100, 380, 450), native 4K", font=font(MED, 52), fill=RUST)
    y = 350
    for n, hp, col in [(100, "100 %", "green"), (380, "50 %", "yellow"), (450, "25 %", "red")]:
        fr = Image.open(REEL / f"capture/_frames/run01{n:08d}.png").convert("RGB").crop((0, 0, 1320, 120))
        canvas.paste(fr, (60, y))
        d.text((1440, y + 30), f"health {hp} → {col}", font=font(REG, 56), fill=INK)
        y += 190
    d.text((60, y + 20), "scripts/main.gd line 378 sets the fill colour from health / max_health.", font=font(REG, 48), fill=SOFT)
    canvas.save(OUT / "ev-healthbar.png")
    return OUT / "ev-healthbar.png"


if __name__ == "__main__" and "--healthbar" in sys.argv:
    print(healthbar_panel())
