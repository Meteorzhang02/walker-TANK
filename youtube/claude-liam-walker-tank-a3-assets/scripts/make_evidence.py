"""Compose the film's evidence figures (film tooling).
Student screenshots are placed unedited (scaled only) with a burned-in "Student's own screenshot" caption.
The headless table is rebuilt from capture/check-stdout.txt (recorded run) and CHANGE-BRIEF.md values.
Run: python scripts/make_evidence.py
"""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
GAME = Path(r"D:/CSYE7270/assignment2/walker-TANK")
SHOTS = Path(r"D:/CSYE7270/assignment2/a3-evidence")
FONTS = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts")
W, H = 3400, 1360
PAGE, INK, MUTED, ACCENT, LINE = "#FFFDF8", "#3D3929", "#564739", "#985039", "#CFC6B5"


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype(str(FONTS / "PT_Mono/PTMono-Regular.ttf"), size)
    return ImageFont.truetype(str(FONTS / ("Lato/static/Lato-Bold.ttf" if bold else "Inter/static/Inter_28pt-Regular.ttf")), size)


def place(canvas, path, box, caption):
    """Fit an unedited screenshot into box=(x, y, w, h) leaving room for a caption under it."""
    x, y, w, h = box
    cap_h = 64
    im = Image.open(path).convert("RGB")
    s = min(w / im.width, (h - cap_h) / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    ox = x + (w - im.width) // 2
    canvas.paste(im, (ox, y))
    d = ImageDraw.Draw(canvas)
    d.rectangle([ox - 2, y - 2, ox + im.width + 1, y + im.height + 1], outline=LINE, width=3)
    f = font(34, bold=True)
    tw = d.textlength(caption, font=f)
    d.text((x + (w - tw) / 2, y + im.height + 14), caption, font=f, fill=ACCENT)


def new():
    return Image.new("RGB", (W, H), PAGE)


def save(im, name):
    out = REEL / "evidence" / name
    im.save(out)
    print("wrote", out)


def text_block(d, x, y, rows, width):
    """rows: list of (title, body) drawn as a vertical list."""
    for title, body in rows:
        d.text((x, y), title, font=font(54, bold=True), fill=INK)
        y += 74
        for line in body:
            d.text((x, y), line, font=font(42), fill=MUTED)
            y += 58
        y += 40
    return y


def game_brief():
    im = new()
    place(im, GAME / "design/test/play-01-normal-combat.png", (40, 40, 1900, H - 80),
          "Student's own screenshot — the 2D game (Assignment 2 play test)")
    d = ImageDraw.Draw(im)
    x = 2020
    d.text((x, 60), "CHANGE-BRIEF.md — three 3D assets", font=font(46, bold=True), fill=ACCENT)
    text_block(d, x, 150, [
        ("cover_wall  4.0 × 1.0 × 1.8 m", ["Cover the player hides behind.", "Wider than the 3.4 m hull; turret fires over it."]),
        ("ammo_crate  1.2 × 0.8 × 0.7 m", ["Pickup that refills shells.", "A reason to leave cover."]),
        ("tank_hedgehog  ≈ 1.9 × 1.9 × 1.4 m", ["Steel obstacle: blocks tanks,", "not shells; never breaks."]),
    ], 1300)
    d.text((x, H - 110), "Written and committed before any asset was built.", font=font(36), fill=MUTED)
    save(im, "ev-game-brief.png")


def blender_mcp():
    im = new()
    place(im, SHOTS / "01-blender-window.png", (40, 40, 2500, H - 80), "Student's own screenshot — Blender 5.2.2 LTS")
    place(im, SHOTS / "02-mcp-panel.png", (2600, 40, 760, H - 80), "Student's own screenshot — MCP panel")
    save(im, "ev-blender-mcp.png")


def prompt_built():
    im = new()
    place(im, SHOTS / "03-prompt-plan-cover-wall.png", (40, 40, 1640, H - 80),
          "Student's own screenshot — Claude's plan for cover_wall")
    place(im, SHOTS / "03b-cover-wall-result.png", (1720, 40, 1640, H - 80),
          "Student's own screenshot — Claude's report of what it built")
    save(im, "ev-prompt-built.png")


def hand_edit():
    im = new()
    place(im, SHOTS / "05-hand-edit.png", (40, 20, 1900, 860), "Student's own screenshot — Edit Mode, block B selected")
    place(im, SHOTS / "06-sidebar-4m.png", (40, 900, 1900, 450), "Student's own screenshot — sidebar: 4 m")
    place(im, SHOTS / "06b-hand-edit-0.7mm-short.png", (1980, 20, 1380, H - 40),
          "Student's own screenshot — Claude's check")
    save(im, "ev-hand-edit.png")


def headless():
    out = (REEL / "capture/check-stdout.txt").read_text(encoding="utf-8")
    sizes = dict(re.findall(r"PASS  (\w+) size \(([^)]*)\)", out))
    lows = dict(re.findall(r"PASS  (\w+) lowest y ([0-9.]+)", out))
    passes = out.count("\nPASS  ")
    result = re.search(r"RESULT: .*", out).group(0)
    code = re.search(r"check_exit=(\d+)", out).group(1)
    im = new()
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 110], fill="#303D34")
    d.text((50, 22), "HEADLESS — Godot dummy renderer: sizes measured, nothing drawn", font=font(54, bold=True), fill="#FFFDF8")
    cols = [60, 760, 1640, 2620]
    heads = ["Asset", "Brief (w × d × h, m)", "Headless size (Godot x, y, z)", "Lowest y"]
    y = 170
    for cx, t in zip(cols, heads):
        d.text((cx, y), t, font=font(46, bold=True), fill=ACCENT)
    brief = {"cover_wall": "4.0 × 1.0 × 1.8", "ammo_crate": "1.2 × 0.8 × 0.7 ±0.1",
             "tank_hedgehog": "≈1.9 × 1.9 × 1.4 ±0.15"}
    y += 90
    for name in ("cover_wall", "ammo_crate", "tank_hedgehog"):
        d.line([60, y - 20, W - 60, y - 20], fill=LINE, width=3)
        d.text((cols[0], y), name, font=font(52, bold=True), fill=INK)
        d.text((cols[1], y), brief[name], font=font(48), fill=INK)
        d.text((cols[2], y), sizes[name], font=font(48, mono=True), fill=INK)
        d.text((cols[3], y), lows[name], font=font(48, mono=True), fill=INK)
        y += 150
    d.line([60, y - 20, W - 60, y - 20], fill=LINE, width=3)
    d.text((60, y + 20), f"{passes} / 18 PASS lines · {result} · exit code {code}", font=font(58, bold=True), fill=INK)
    d.text((60, y + 120), "Brief in Blender Z-up; Godot is Y-up, so height is the middle number. Checker tolerance 0.01 m.",
           font=font(40), fill=MUTED)
    d.text((60, y + 180), "Not checked: colours, lighting, shadows, triangle counts, the copies placed in asset_room_3d.tscn.",
           font=font(40), fill=MUTED)
    save(im, "ev-headless.png")


def claude_wrong():
    im = new()
    place(im, SHOTS / "04-hedgehog-options.png", (40, 40, 1500, H - 80),
          "Student's own screenshot — Claude's box check, before building")
    d = ImageDraw.Draw(im)
    text_block(d, 1640, 80, [
        ("1  The hedgehog brief was wrong", ["2.4 m beams → 1.559 m high: over the 1.4 ±0.15 m.",
                                             "Claude recommended turning each beam 45°.",
                                             "Student chose 2.125 m beams → 1.400 m."]),
        ("2  The join raised an error", ["AttributeError: 'NoneType' object has no",
                                         "attribute 'select_set' — re-run passed."]),
        ("3  A comment did not match its code", ["Comment: block B 0.1 m in from the front face.",
                                                 "Code: centred, 0.1 m in from both faces."]),
    ], 1700)
    save(im, "ev-claude-wrong.png")


if __name__ == "__main__":
    game_brief(); blender_mcp(); prompt_built(); hand_edit(); headless(); claude_wrong()
