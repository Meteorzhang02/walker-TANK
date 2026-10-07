"""Cut gameplay beats from the native 4K take and mix their audio (film tooling).
For each gameplay beat in clips.json: copy an exact run of frames [start, start+n) from capture/run-01.mp4
(no retime, no speed change, no crop), burn a small disclosure label and logged sound-event tags, and
build the beat's audio from the same interval of the game's own recorded mix (capture/run-01.wav):
  narrated beats: Kokoro narration (0.3 s lead, silence-padded to n frames) over the game audio, with the
                  game audio side-chain ducked by the narration (it returns between phrases);
  game_only beat: the game audio alone, unchanged except a fixed -2 dB gain (no ducking, no narration).
Montage beats (B04) list several intervals; each is a real, unretimed interval joined by hard cuts.
Run: python scripts/cut_clips.py [BEAT ...]
"""
import json, math, shutil, subprocess, sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
TAKE = REEL / "capture/run-01.mp4"
WAV = REEL / "capture/run-01.wav"
FONT = "D\\:/CSYE7270/brutalist.art/runtime/fonts/Inter/static/Inter_28pt-Medium.ttf"
TAGS = {"fire": "SFX-fire  (YunqiZ)", "enemy_fire": "SFX-fire  (enemy, -6 dB)", "cover_hit": "SFX-cover-hit",
        "player_hit": "SFX-player-hit", "enemy_hit": "SFX-player-hit  (enemy, -8 dB)", "explode": "SFX-explode",
        "victory": "SFX-victory"}
LABEL = "SCRIPTED INPUT · NOT A HUMAN PLAYTEST · Godot 4.7.2 Movie Maker, native 3840x2160"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(" ".join(map(str, cmd))[:400] + "\n" + r.stderr[-1500:])
    return r


def probe(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]).stdout.strip())


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


def sound_events(offset):
    """Movie frame of each logged sound request (log frame + offset)."""
    ev = []
    for line in (REEL / "capture/run-01-inputs.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if d["ev"] == "sound_request":
            ev.append((d["frame"] + offset, d["key"]))
    return ev


def drawtext_filters(start, n, events, extra_label=None):
    f = [f"drawtext=fontfile='{FONT}':text='{esc(LABEL)}':fontsize=44:fontcolor=white@0.95:"
         f"box=1:boxcolor=black@0.82:boxborderw=14:x=w-tw-70:y=h-th-46"]
    if extra_label:
        f.append(f"drawtext=fontfile='{FONT}':text='{esc(extra_label)}':fontsize=64:fontcolor=white:"
                 f"box=1:boxcolor=0x985039@0.92:boxborderw=22:x=(w-tw)/2:y=h-th-190")
    # stack simultaneous tags: each tag shows for 1.2 s from its frame
    shown = [(fr, k) for fr, k in events if start - 36 < fr < start + n]
    lane_free = []  # frame at which each lane becomes free
    for i, (fr, k) in enumerate(shown):
        t0 = (fr - start) / FPS
        t1 = t0 + 1.2
        lane = next((j for j, f in enumerate(lane_free) if f <= fr), len(lane_free))
        if lane == len(lane_free):
            lane_free.append(0)
        lane_free[lane] = fr + 37
        y = 40 + 92 * lane
        f.append(f"drawtext=fontfile='{FONT}':text='{esc('sound: ' + TAGS.get(k, k))}':fontsize=54:fontcolor=white:"
                 f"box=1:boxcolor=black@0.6:boxborderw=16:x=(w-tw)/2+300:y={y}:enable='between(t,{max(0, t0):.3f},{t1:.3f})'")
    return ",".join(f)


def cut_video(bid, segments, offset, extra_labels):
    events = sound_events(offset)
    parts = []
    for i, (start, n) in enumerate(segments):
        part = REEL / f"capture/_parts/{bid}-{i}.mp4"
        part.parent.mkdir(exist_ok=True)
        vf = f"select='between(n\\,{start}\\,{start + n - 1})',setpts=N/{FPS}/TB," + drawtext_filters(start, n, events, extra_labels[i] if extra_labels else None)
        run(["ffmpeg", "-v", "error", "-y", "-i", str(TAKE), "-vf", vf, "-frames:v", str(n), "-an", "-r", str(FPS),
             "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", str(part)])
        parts.append(part)
    out = REEL / f"media/{bid}.mp4"
    if len(parts) == 1:
        shutil.copy2(parts[0], out)
    else:
        lst = REEL / f"capture/_parts/{bid}.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


def cut_audio(bid, segments, beat, total):
    game = REEL / f"capture/_parts/{bid}-game.wav"
    if len(segments) == 1:
        s, n = segments[0]
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s / FPS:.6f}", "-t", f"{n / FPS:.6f}", "-i", str(WAV),
             "-ar", "48000", "-ac", "2", str(game)])
    else:
        pieces = []
        for i, (s, n) in enumerate(segments):
            pp = REEL / f"capture/_parts/{bid}-game-{i}.wav"
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s / FPS:.6f}", "-t", f"{n / FPS:.6f}", "-i", str(WAV),
                 "-ar", "48000", "-ac", "2", str(pp)])
            pieces.append(pp)
        lst = REEL / f"capture/_parts/{bid}-game.txt"
        lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in pieces))
        run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(game)])
    out = REEL / f"mp3/beat-{bid}.mp3"
    if beat.get("audio_policy") == "game_only":
        run(["ffmpeg", "-v", "error", "-y", "-i", str(game), "-af", f"volume=-2dB,apad,atrim=0:{total:.6f}",
             "-ar", "48000", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "256k", str(out)])
        return out, None
    raw = REEL / "mp3/raw" / f"beat-{bid}.mp3"
    if not raw.exists():
        shutil.copy2(out, raw)
    tts = probe(raw)
    lead = 0.3
    if lead + tts > total + 1e-6:
        raise SystemExit(f"{bid}: narration {tts:.2f}s + lead does not fit {total:.2f}s of footage; lengthen the interval")
    nar = REEL / f"capture/_parts/{bid}-nar.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", f"adelay={int(lead * 1000)}:all=1,apad,atrim=0:{total:.6f}",
         "-ar", "48000", "-ac", "2", str(nar)])
    # game audio at -4 dB, ducked by up to ~12 dB while Liam speaks; narration on top; limiter guards the sum
    fc = ("[1:a]volume=-4dB[g];[0:a]asplit=2[n1][n2];"
          "[g][n1]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=350:makeup=1[gd];"
          "[gd][n2]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95,apad,atrim=0:" + f"{total:.6f}" + "[m]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(nar), "-i", str(game), "-filter_complex", fc, "-map", "[m]",
         "-t", f"{total:.6f}", "-ar", "48000", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "256k", str(out)])
    return out, {"lead_s": lead, "tts_s": round(tts, 3), "raw": f"mp3/raw/beat-{bid}.mp3"}


def main(only):
    cfg = json.loads((REEL / "clips.json").read_text(encoding="utf-8"))
    sp = REEL / "beat_sheet.json"
    sheet = json.loads(sp.read_text(encoding="utf-8"))
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if bid not in cfg["beats"] or (only and bid not in only):
            continue
        c = cfg["beats"][bid]
        segs = [tuple(s) for s in c["segments"]]
        n = sum(x[1] for x in segs)
        total = n / FPS
        cut_video(bid, segs, cfg["log_frame_offset"], c.get("labels"))
        out, info = cut_audio(bid, segs, b, total)
        b["audio_file"] = f"mp3/beat-{bid}.mp3"
        b["actual_duration_s"] = total
        b["game_audio"] = {"source": "capture/run-01.wav", "segments_frames": segs,
                           "mix": "game_only, -2 dB, no narration" if info is None else
                           "narration (0.3 s lead) over game audio at -4 dB, side-chain ducked by the narration; alimiter 0.95",
                           **(info or {})}
        b["shot"]["evidence_media"] = f"media/{bid}.mp4"
        b["shot"]["capture"]["frames"] = segs
        print(f"{bid}: {segs} -> {n} frames ({total:.3f}s); mp4 {probe(REEL / f'media/{bid}.mp4'):.3f}s, mp3 {probe(out):.3f}s")
    sp.write_text(json.dumps(sheet, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
