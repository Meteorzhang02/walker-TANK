"""Build the gameplay beats media/B01.mp4, media/B04.mp4, media/B12.mp4 for walker-tank-a8-pitch (film tooling).

Footage: capture/run-01.mp4 (Godot 4.7.2 Movie Maker, native 3840x2160 @ 30 fps, PNG sequence encoded with x264
crf 8; see CAPTURE.md), a scripted-input take of the real scenes/main.tscn on a git-archive copy of walker-TANK
HEAD 3cc29f2 (game source identical to 4f88f1b, tag a7). Frames are used in order at normal speed: never retimed,
reordered, retouched or generated. B04 joins four in-order intervals of the one take and crops each 1.5x around
the logged event; the caption says so. Every frame carries the capture label. Clips are silent: the narration is the
only audio (game audio muted, documented in CAPTURE.md).

Interval choice is read from capture/run-01-inputs.jsonl (logged frame = Engine.get_frames_drawn() = movie frame;
checked in CAPTURE.md). Each beat runs exactly its padded audio frame count. clips.json records every range.
Run: python scripts/make_media.py [B01 B04 B12]
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REEL = Path(__file__).resolve().parents[1]
RUN = REEL / "capture/run-01.mp4"
LOG = REEL / "capture/run-01-inputs.jsonl"
WORK = REEL / "capture/work"
WORK.mkdir(parents=True, exist_ok=True)
FONT = Path(r"D:/CSYE7270/brutalist.art/runtime/fonts/Lato/static/Lato-Bold.ttf")
W, H, FPS, SCALE = 3840, 2160, 30, 3          # logical game canvas 1280x720 rendered at x3
CAP_LINES = ("REAL CAPTURE · scripted input", "tag a7, game source 4f88f1b")


def sheet():
    return json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))


def frames_of(bid):
    b = next(x for x in sheet()["beats"] if x["beat_id"] == bid)
    return b["audio_pad"]["frames"], b


def events():
    return [json.loads(l) for l in LOG.read_text(encoding="utf-8").splitlines() if l.strip()]


def plaque(lines, size, anchor, path):
    """Transparent 4K overlay with a dark rounded plaque holding white text lines."""
    f = ImageFont.truetype(str(FONT), size)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    widths = [d.textlength(t, font=f) for t in lines]
    lh = int(size * 1.25)
    bw, bh = int(max(widths)) + 2 * 48, lh * len(lines) + 2 * 30
    x, y = anchor(bw, bh)
    d.rounded_rectangle([x, y, x + bw, y + bh], radius=24, fill=(30, 27, 24, 225))
    for i, t in enumerate(lines):
        d.text((x + 48, y + 30 + i * lh), t, font=f, fill=(250, 249, 245, 255))
    im.save(path)
    return path


def cap_overlay():
    return plaque(CAP_LINES, 64, lambda bw, bh: (W - bw - 60, 60), WORK / "cap_label.png")


def caption_overlay(text, name):
    return plaque([text], 72, lambda bw, bh: ((W - bw) // 2, H - bh - 170), WORK / f"{name}.png")


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def segment(start, n, out, crop_center=None, caption=None):
    """Frames [start, start+n) of run-01, optional 1.5x crop around a logical point, labels burned in."""
    vf = f"select='between(n\\,{start}\\,{start + n - 1})',setpts=N/{FPS}/TB"
    if crop_center is not None:
        cw, ch = W * 2 // 3, H * 2 // 3
        cx = min(max(int(crop_center[0] * SCALE) - cw // 2, 0), W - cw)
        cy = min(max(int(crop_center[1] * SCALE) - ch // 2, 0), H - ch)
        vf += f",crop={cw}:{ch}:{cx}:{cy},scale={W}:{H}:flags=lanczos"
    inputs = ["-i", str(RUN), "-i", str(cap_overlay())]
    chain = f"[0:v]{vf}[v0];[v0][1:v]overlay=0:0[v1]"
    last = "v1"
    if caption:
        inputs += ["-i", str(caption_overlay(caption, out.stem))]
        chain += f";[v1][2:v]overlay=0:0[v2]"
        last = "v2"
    ff(inputs + ["-filter_complex", chain, "-map", f"[{last}]", "-frames:v", str(n), "-an", "-r", str(FPS),
                 "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(out)])
    return {"start_frame": start, "frames": n, "crop_center_logical": crop_center, "caption": caption}


def nframes(p):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                               "stream=nb_read_frames", "-of", "csv=p=0", str(p)], capture_output=True, text=True,
                              check=True).stdout.strip())


def concat(parts, out):
    lst = WORK / f"{out.stem}_concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
    ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])


def cut_at(b, phrase, n, lead=0.2):
    t = b["narration_text"]
    lead_s = b["audio_pad"]["lead_s"]
    tts = b["tts_duration_s"]
    return int(round((lead_s + tts * t.index(phrase) / len(t) - lead) * FPS))


def build_b01(ev, clips):
    n, b = frames_of("B01")
    out = REEL / "media/B01.mp4"
    clips["B01"] = [segment(0, n, out)]


def build_b04(ev, clips):
    n, b = frames_of("B04")
    c1 = cut_at(b, "Yoon-chee Zee flashes", n)
    c2 = cut_at(b, "A damaged tank", n)
    c3 = cut_at(b, "and a wreck", n)
    lens = [c1, c2 - c1, c3 - c2, n - c3]
    burst = next(e for e in ev if e["ev"] == "cover_burst" and e["phase"] == "break_cover")
    # red flash: first hit on YunqiZ during the fight while it is alive
    flash = next(e for e in ev if e["ev"] == "player_flash_start" and e["phase"] == "fight")
    ppos = min((e for e in ev if e["ev"] == "aim_check"), key=lambda e: abs(e["frame"] - flash["frame"]))["pos"]
    smoke = next(e for e in ev if e["ev"] == "enemy_smoke" and e["emitting"] and not e["dead"])
    spos = [e for e in ev if e["ev"] == "enemy_health" and e["enemy"] == smoke["enemy"] and e["frame"] <= smoke["frame"]][-1]["pos"]
    death = next(e for e in ev if e["ev"] == "enemy_destroyed" and e["enemy"] == smoke["enemy"])
    wreck = next(e for e in ev if e["ev"] == "enemy_destroyed")
    victory = next(e["frame"] for e in ev if e["ev"] == "phase_start" and e["phase"] == "victory_hold")
    plan = [
        (max(0, burst["frame"] - lens[0] // 2), lens[0], burst["pos"], "debris bursts from the hit point · 1.5× crop"),
        (max(0, flash["frame"] - 12), lens[1], ppos, "YunqiZ flashes red · 1.5× crop"),
        (max(0, min(smoke["frame"] - 6, death["frame"] - lens[2] - 3)), lens[2], spos, "a damaged tank smokes · 1.5× crop"),
        (min(wreck["frame"] + 45, victory - lens[3] - 5), lens[3], wreck["pos"], "a wreck keeps smoking · 1.5× crop"),
    ]
    parts, rec = [], []
    for i, (s, k, pos, cap) in enumerate(plan):
        p = WORK / f"B04_{i}.mp4"
        rec.append(segment(s, k, p, crop_center=pos, caption=cap))
        parts.append(p)
    out = REEL / "media/B04.mp4"
    concat(parts, out)
    clips["B04"] = rec


def build_b12(ev, clips):
    n, b = frames_of("B12")
    victory = next(e["frame"] for e in ev if e["ev"] == "phase_start" and e["phase"] == "victory_hold")
    start = victory - n - 15                      # ends before the victory panel (the brief lists win screens as "will exist")
    raw = WORK / "B12_left.mp4"
    clips["B12"] = [segment(start, n, raw)]
    drawn = REEL / "manim/B12.mp4"                 # Manim B12_Close, rendered at 4K by art/manim
    out = REEL / "media/B12.mp4"
    # left panel of B12_Close: centre (-3.25, 0.2) units, 6.2 x 3.49 units -> pixels, inset 6 px for the outline
    pw, ph = 1662, 934
    px, py = 212, 561
    ff(["-i", str(drawn), "-i", str(raw), "-filter_complex",
        f"[1:v]scale={pw}:{ph}:flags=lanczos[g];[0:v][g]overlay={px}:{py}[v]", "-map", "[v]", "-frames:v", str(n),
        "-an", "-r", str(FPS), "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", str(out)])


def main(only):
    ev = events()
    cp = REEL / "clips.json"
    clips = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
    for bid, fn in (("B01", build_b01), ("B04", build_b04), ("B12", build_b12)):
        if only and bid not in only:
            continue
        fn(ev, clips)
        want, _ = frames_of(bid)
        got = nframes(REEL / f"media/{bid}.mp4")
        print(f"{bid}: {got} frames (want {want})", "OK" if got == want else "MISMATCH")
        if got != want:
            sys.exit(2)
    clips["_source"] = {"capture": "capture/run-01.mp4", "fps": FPS, "note": "frame ranges are run-01 frame numbers"}
    cp.write_text(json.dumps(clips, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
