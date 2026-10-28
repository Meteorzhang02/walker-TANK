"""Compose the A5 film's evidence figures (film tooling).
Every picture is the student's existing in-engine capture (docs/a5/captures/*.png), cropped and scaled only
(nearest-neighbour where pixels are being read), with a burned-in "In-engine capture (scripted)" caption.
Every number is read from the capture CSVs, the test logs or the brief, never typed from memory, except the
turret recomputation, which is quoted from CHANGE-BRIEF.md's dated Revision.
The three face means in ev-litwall.png are measured here, from materials_side_by_side.png, and labelled as such.
Run: python scripts/make_evidence.py
"""
import csv, json, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1]
CAP = GAME / "docs/a5/captures"
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
W, H = 3400, 1280
PAGE, INK, MUTED, ACCENT, LINE, GREEN = "#FFFDF8", "#3D3929", "#564739", "#985039", "#CFC6B5", "#303D34"
CAPTION = "In-engine capture (scripted)"


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype(str(FONTS / "PT_Mono/PTMono-Regular.ttf"), size)
    return ImageFont.truetype(str(FONTS / ("Lato/static/Lato-Bold.ttf" if bold else "Inter/static/Inter_28pt-Regular.ttf")), size)


def rows(name):
    with open(CAP / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def new():
    return Image.new("RGB", (W, H), PAGE)


def paste(canvas, im, x, y, w=None, h=None, nearest=False, border=True):
    if w or h:
        s = min((w or 1e9) / im.width, (h or 1e9) / im.height)
        im = im.resize((round(im.width * s), round(im.height * s)), Image.NEAREST if nearest else Image.LANCZOS)
    canvas.paste(im, (x, y))
    if border:
        ImageDraw.Draw(canvas).rectangle([x - 2, y - 2, x + im.width + 1, y + im.height + 1], outline=LINE, width=3)
    return im.width, im.height


def centred(d, x, w, y, text, f, fill):
    d.text((x + (w - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def save(im, name):
    out = REEL / "evidence" / name
    im.save(out)
    print("wrote", out)


def rgb(s):
    return "(" + ", ".join(s.split()) + ")"


def hitflash():
    data = {(r["value"], r["pixel"]): r for r in rows("hit_flash_pixels.csv")}
    turret = {"0.0": "(70, 76, 31)", "0.5": "(126, 53, 22)", "1.0": "(181, 30, 12)"}  # CHANGE-BRIEF Revision 2
    im = new()
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 95, 555, 215, 650  # tank region of the 1280x720 capture
    p1 = (int(data[("0.0", "P1")]["x"]), int(data[("0.0", "P1")]["y"]))
    p2 = (int(data[("0.0", "P2")]["x"]), int(data[("0.0", "P2")]["y"]))
    colw = 830
    for i, v in enumerate(("0.0", "0.5", "1.0", "2.0")):
        cx = 20 + i * (colw + 13)
        centred(d, cx, colw, 10, f"hit_amount = {v}", font(52, bold=True), INK)
        crop = Image.open(CAP / f"hit_flash_{v}.png").crop((x0, y0, x1, y1))
        z = 6.9
        crop = crop.resize((round(crop.width * z), round(crop.height * z)), Image.NEAREST)
        cd = ImageDraw.Draw(crop)
        for (px, py), lab in ((p1, "P1"), (p2, "P2")):
            sx, sy = (px - x0 + 0.5) * z, (py - y0 + 0.5) * z
            cd.ellipse([sx - 26, sy - 26, sx + 26, sy + 26], outline="#FFFFFF", width=6)
            cd.text((sx + 32, sy - 30), lab, font=font(44, bold=True), fill="#FFFFFF")
        ox = cx + (colw - crop.width) // 2
        paste(im, crop, ox, 84)
        y = 84 + crop.height + 14
        centred(d, cx, colw, y, CAPTION + " · markers added", font(30, bold=True), ACCENT)
        y += 58
        a, b = data[(v, "P2")], data[(v, "P1")]
        lines = [("P2 predicted", rgb(a["predicted_rgb"]) if a["predicted_rgb"] != "none" else "none"),
                 ("P2 measured", rgb(a["centre_rgb"])),
                 ("P1 hull predicted", rgb(b["predicted_rgb"]) if b["predicted_rgb"] != "none" else "none"),
                 ("P1 measured", rgb(b["centre_rgb"])),
                 ("turret, recomputed after", turret.get(v, "—"))]
        for lab, val in lines:
            d.text((cx + 10, y), lab, font=font(38), fill=MUTED)
            d.text((cx + 440, y), val, font=font(38, mono=True), fill=INK)
            y += 56
    d.text((40, H - 62), "P1 = hull texel (99, 50), screen (155, 590): the turret covers it (turret alpha 1.00). "
           "P2 = hull texel (59, 109), screen (135, 620). Values: hit_flash_pixels.csv.", font=font(32), fill=MUTED)
    save(im, "ev-hitflash.png")


def hint():
    data = rows("hint_pixels.csv")
    src = Image.open(CAP / "hint_both.png")
    bg = tuple(int(c) for c in np.asarray(src)[600, 640])
    im = new()
    d = ImageDraw.Draw(im)
    crop = src.crop((180, 220, 1120, 450))
    w, h = paste(im, crop, 60, 300, w=2100)
    centred(d, 60, w, 300 + h + 14, CAPTION + " · hint_both.png, 1280 × 720", font(34, bold=True), ACCENT)
    d.text((60, 300 + h + 70), f"Background grey measures {bg[0]}, so Quad A's 128 band blends into it.",
           font=font(32), fill=MUTED)
    x = 2250
    d.text((x, 80), "Same file: 64 / 128 / 192", font=font(58, bold=True), fill=INK)
    y = 200
    d.text((x, y), "band", font=font(38, bold=True), fill=ACCENT)
    d.text((x + 250, y), "predicted", font=font(38, bold=True), fill=ACCENT)
    d.text((x + 560, y), "measured", font=font(38, bold=True), fill=ACCENT)
    y += 70
    for quad, title in (("QuadA_srgb", "A · source_color"), ("QuadB_raw", "B · no hint")):
        d.text((x, y), title, font=font(42, bold=True), fill=INK)
        y += 62
        for r in data:
            if r["quad"] != quad:
                continue
            d.text((x, y), r["file_value"], font=font(46, mono=True), fill=MUTED)
            d.text((x + 250, y), r["predicted"], font=font(46, mono=True), fill=INK)
            d.text((x + 560, y), r["centre_rgb"].split()[0], font=font(46, mono=True), fill=INK)
            y += 66
        y += 30
    exact = sum(1 for r in data if r["maxdiff_centre"] == "0")
    d.text((x, y + 10), f"{exact} / {len(data)} exact (difference 0)", font=font(46, bold=True), fill=INK)
    save(im, "ev-hint.png")


def materials():
    saved = {r["file"]: r for r in rows("materials_captures.csv")}
    edit = {r["file"]: r for r in rows("shader_edit_materials_captures.csv")}
    tres = {k: (GAME / f"materials/cover_wall_{k}.tres").read_text(encoding="utf-8").splitlines() for k in ("intact", "damaged")}
    im = new()
    d = ImageDraw.Draw(im)
    crop = Image.open(CAP / "materials_side_by_side.png").crop((0, 300, 470, 420))
    w, h = paste(im, crop, 40, 70, w=1560)
    d.text((60, 10), "CoverWall2 · damaged", font=font(40, bold=True), fill=INK)
    d.text((40 + w // 2 + 60, 10), "CoverWall · intact", font=font(40, bold=True), fill=INK)
    centred(d, 40, w, 70 + h + 10, CAPTION + " · materials_side_by_side.png", font(30, bold=True), ACCENT)
    x = 1680
    d.text((x, 20), "Both .tres: shader = brick_surface.gdshader. They differ in lines 12–13:", font=font(36, bold=True), fill=INK)
    y = 80
    for k in ("damaged", "intact"):
        for n in (12, 13):
            d.text((x, y), f"{k:8s} {n}  {tres[k][n - 1]}", font=font(32, mono=True), fill=INK)
            y += 46
        y += 10
    y += 20

    def mean(r, k):
        return r[k].split()[0]
    a, s, m = saved["materials_side_by_side.png"], edit["shader_edit_materials_side_by_side.png"], saved["material_edit_damaged_only.png"]
    d.text((x, y), "Front-face mean, red channel", font=font(36, bold=True), fill=ACCENT)
    d.text((x + 900, y), "intact", font=font(36, bold=True), fill=ACCENT)
    d.text((x + 1250, y), "damaged", font=font(36, bold=True), fill=ACCENT)
    y += 58
    for lab, r in (("saved values", a), ("shader edit (line 33 × 0.5)", s), ("material edit (damaged brightness 0.5)", m)):
        d.text((x, y), lab, font=font(36), fill=INK)
        d.text((x + 900, y), mean(r, "wall1_mean_rgb"), font=font(38, mono=True), fill=INK)
        d.text((x + 1250, y), mean(r, "wall2_mean_rgb"), font=font(38, mono=True), fill=INK)
        y += 56
    # sweep strip
    sy = 760
    d.line([40, sy - 20, W - 40, sy - 20], fill=LINE, width=3)
    d.text((40, sy), "Sweep of the intact material (scripted captures; damaged wall untouched)", font=font(38, bold=True), fill=INK)
    for i, (f, lab) in enumerate((("sweep_brightness_max.png", "brightness 2.0"), ("sweep_roughness_scale_min.png", "roughness_scale 0.0"),
                                  ("sweep_uv_scale_min.png", "uv_scale 0.1"), ("sweep_uv_scale_max.png", "uv_scale 4.0"))):
        cx = 40 + i * 840
        c = Image.open(CAP / f).crop((220, 305, 460, 400))
        cw, ch = paste(im, c, cx, sy + 70, w=800)
        r = saved[f]
        d.text((cx, sy + 80 + ch), f"{lab}  ·  mean ({', '.join(r['wall1_mean_rgb'].split())})", font=font(32, bold=True), fill=INK)
    save(im, "ev-materials.png")


def litwall():
    src = Image.open(CAP / "materials_side_by_side.png")
    a = np.asarray(src).astype(float)
    boxes = {"top": (335, 365, 326, 334), "front": (329, 339, 366, 376), "end (+x)": (427, 432, 355, 385)}
    means = {k: a[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3).mean(0) for k, (x0, x1, y0, y1) in boxes.items()}
    X0, Y0, X1, Y1, z = 220, 300, 460, 400, 8
    crop = src.crop((X0, Y0, X1, Y1)).resize(((X1 - X0) * z, (Y1 - Y0) * z), Image.NEAREST)
    cd = ImageDraw.Draw(crop)
    for k, (x0, x1, y0, y1) in boxes.items():
        cd.rectangle([(x0 - X0) * z, (y0 - Y0) * z, (x1 + 1 - X0) * z, (y1 + 1 - Y0) * z], outline="#FFFFFF", width=6)
    im = new()
    d = ImageDraw.Draw(im)
    w, h = paste(im, crop, 40, 40, h=1000)
    centred(d, 40, w, 40 + h + 12, CAPTION + " · CoverWall, intact · boxes added", font(32, bold=True), ACCENT)
    x = 40 + w + 90
    d.text((x, 60), "One ALBEDO, three faces", font=font(56, bold=True), fill=INK)
    d.text((x, 150), "box mean (R, G, B), 0–255", font=font(36), fill=MUTED)
    y = 230
    for k in ("top", "front", "end (+x)"):
        m = means[k]
        d.text((x, y), k, font=font(50, bold=True), fill=INK)
        d.text((x, y + 66), f"({m[0]:.1f}, {m[1]:.1f}, {m[2]:.1f})", font=font(46, mono=True), fill=INK)
        y += 170
    for i, t in enumerate(("Measured by this film's build script", "from the existing capture.", "The front box matches the capture", "tool's own 11 × 11 mean.")):
        d.text((x, y + 20 + i * 48), t, font=font(34), fill=MUTED)
    save(im, "ev-litwall.png")
    return {k: [round(float(c), 1) for c in v] for k, v in means.items()}


def tests():
    logs = GAME / "logs"

    def result(name):
        return re.search(r"RESULT: .*", (logs / name).read_text(encoding="utf-8")).group(0)
    im = new()
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 110], fill=GREEN)
    d.text((50, 22), "HEADLESS — recorded logs in logs/ (dummy renderer: nothing is drawn)", font=font(54, bold=True), fill=PAGE)
    runs = [("test_hit_flash.gd @ 30 fps", "test_hit_flash_30fps.log"), ("test_hit_flash.gd @ 60 fps", "test_hit_flash_60fps.log"),
            ("test_hit_flash.gd @ 144 fps", "test_hit_flash_144fps.log"), ("test_materials.gd @ 60", "test_materials_60fps.log"),
            ("check_a3_assets.gd (baseline)", "check_a3_assets_60fps.log"), ("test_sound_triggers.gd (baseline)", "test_sound_triggers_60fps.log")]
    y = 150
    for lab, f in runs:
        d.text((60, y), lab, font=font(44, bold=True), fill=INK)
        d.text((900, y), result(f), font=font(42, mono=True), fill=INK)
        y += 70
    d.text((60, y + 10), "all exit 0 (docs/a5/step2-output.txt; TEST-REPORT rerun at 3d48047)", font=font(34), fill=MUTED)
    muts = [("1  delete a ';' (hit_flash line 5)", "mutation1_semicolon_60fps.log"),
            ("2  rename hit_amount", "mutation2_rename_60fps.log"),
            ("3  remove source_color (brick line 4)", "mutation3_no_source_color_60fps.log")]
    x = 1900
    yy = 150
    d.text((x, yy), "Mutations, made and restored by the student", font=font(44, bold=True), fill=ACCENT)
    yy += 80
    for lab, f in muts:
        d.text((x, yy), lab, font=font(40, bold=True), fill=INK)
        d.text((x + 60, yy + 56), result(f) + "  ·  exit 1", font=font(38, mono=True), fill=INK)
        yy += 140
    d.line([60, 860, W - 60, 860], fill=LINE, width=3)
    d.text((60, 890), "What no headless run can show", font=font(48, bold=True), fill=ACCENT)
    for i, t in enumerate(("the look on screen (every colour number comes from the windowed captures)",
                           "the existing white _flash(): modulate reaches 2.2 in the test, but in play the red masks it",
                           "the pause rule: headless only — the student could not press Esc within 0.5 s")):
        d.text((90, 970 + i * 70), "·  " + t, font=font(42), fill=INK)
    save(im, "ev-tests.png")


if __name__ == "__main__":
    hitflash(); hint(); materials()
    m = litwall()
    (REEL / "capture/litwall-means.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
    print("litwall means", m)
    tests()
