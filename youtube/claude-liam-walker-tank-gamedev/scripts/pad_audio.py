"""Silence-only padding of measured Kokoro narration (film tooling).
The untouched TTS is kept in mp3/raw/. Lead/tail silence is added and the total is rounded UP to whole
30 fps frames; actual_duration_s is set to that exact frame count / 30. Never trims or retimes speech.
B01: 0.8 s lead (EXECUTIVE-SUMMARY LAW); B35: 1.0 s silent tail (OUTRO-LOCK); others 0.25 s / 0.45 s.
Gameplay beats are conformed later by mix_gameplay.py to their clip length instead.
Run: python scripts/pad_audio.py [BEAT ...]
"""
import json, math, shutil, subprocess, sys
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
FPS = 30
LEAD = {"B01": 0.8, "B35": 0.0}
TAIL = {"B35": 1.0}


def probe(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout.strip())


def main(only):
    sp = REEL / "beat_sheet.json"
    sheet = json.loads(sp.read_text(encoding="utf-8"))
    (REEL / "mp3/raw").mkdir(parents=True, exist_ok=True)
    for b in sheet["beats"]:
        bid = b["beat_id"]
        if only and bid not in only:
            continue
        if b.get("kind") == "gameplay" or not b.get("audio_file"):
            continue
        cur = REEL / b["audio_file"]
        raw = REEL / "mp3/raw" / cur.name
        if b.get("audio_pad") and raw.exists() and b["audio_pad"].get("tts_sha_src") == "raw":
            src = raw  # re-pad from the untouched TTS
        else:
            shutil.copy2(cur, raw)
            src = raw
        tts = probe(src)
        lead = LEAD.get(bid, 0.25)
        tail = TAIL.get(bid, 0.45)
        frames = math.ceil((lead + tts + tail) * FPS - 1e-9)
        total = frames / FPS
        tmp = cur.with_suffix(".pad.mp3")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                        f"adelay={int(round(lead * 1000))}:all=1,apad,atrim=0:{total:.6f}",
                        "-ar", "24000", "-ac", "1", "-c:a", "libmp3lame", "-b:a", "160k", str(tmp)], check=True)
        tmp.replace(cur)
        b["tts_duration_s"] = round(tts, 3)
        b["audio_pad"] = {"lead_s": lead, "tail_s": round(total - lead - tts, 3), "frames": frames,
                          "raw": f"mp3/raw/{cur.name}", "method": "ffmpeg adelay+apad+atrim (silence only)", "tts_sha_src": "raw"}
        b["actual_duration_s"] = total
        print(f"{bid}: tts {tts:.3f}s -> {frames} frames ({total:.3f}s), mp3 probe {probe(cur):.3f}s")
    sp.write_text(json.dumps(sheet, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(set(sys.argv[1:]))
