"""Bind on-screen highlights to the narration's own words (film tooling).
Transcribes each beat's padded narration with faster-whisper (word timestamps, local, free), finds the first
occurrence of each cue phrase, and writes cue_times into the beat (seconds from the beat start).
GodotDevWorkbench cues: {at, line, label}; GodotDesignFigure cues: {at, card}.
A phrase that cannot be found is an error: no guessed timings.
Run: python scripts/bind_cues.py [BEAT ...]
"""
import json, re, sys
from pathlib import Path
from faster_whisper import WhisperModel

REEL = Path(__file__).resolve().parents[1]


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def words_of(model, path):
    segs, _ = model.transcribe(str(path), word_timestamps=True, language="en")
    out = []
    for s in segs:
        for w in s.words:
            for piece in re.split(r"[-\s]+", w.word.strip()):
                if norm(piece):
                    out.append((norm(piece), w.start))
    return out


NUM = {"sixty": ["60", "sixty"], "thirty": ["30", "thirty"], "two": ["2", "two"], "zero": ["0", "zero"],
       "eight": ["8", "eight"], "five": ["5", "five"], "seven": ["7", "seven"], "six": ["6", "six"],
       "thousand": ["thousand", "2000", "000"], "sixtyfour": ["64", "sixtyfour"]}


def find(words, phrase):
    target = [norm(p) for p in re.split(r"[-\s]+", phrase) if norm(p)]
    for i in range(len(words)):
        ok = True
        for j, t in enumerate(target):
            if i + j >= len(words):
                ok = False; break
            w = words[i + j][0]
            alts = NUM.get(t, [t])
            if not any(w == a or w.startswith(a) for a in alts):
                ok = False; break
        if ok:
            return words[i][1]
    joined = "".join(t for t in target)
    for i in range(len(words)):  # whisper may merge tokens, e.g. "sixty-four" -> "64"
        if words[i][0] in NUM.get(joined, [joined]):
            return words[i][1]
    return None


def main(only):
    sp = REEL / "beat_sheet.json"
    sheet = json.loads(sp.read_text(encoding="utf-8"))
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    bad = []
    for b in sheet["beats"]:
        if "cue_spec" not in b or not b.get("audio_file"):
            continue
        if only and b["beat_id"] not in only:
            continue
        words = words_of(model, REEL / b["audio_file"])
        times = []
        for c in b["cue_spec"]:
            t = find(words, c["phrase"])
            if t is None:
                bad.append((b["beat_id"], c["phrase"], " ".join(w for w, _ in words)))
                continue
            entry = {"at": round(max(0.0, t - 0.15), 2)}
            entry.update({k: v for k, v in c.items() if k != "phrase"})
            times.append(entry)
        b["cue_times"] = times
        rem = b.get("shot", {}).get("remotion", {})
        if rem.get("props") is not None:
            rem["props"]["cues"] = times
        print(b["beat_id"], [(c["phrase"], x["at"]) for c, x in zip(b["cue_spec"], times)])
    sp.write_text(json.dumps(sheet, ensure_ascii=False, indent=1), encoding="utf-8")
    if bad:
        for bid, ph, ws in bad:
            print(f"MISSING {bid}: '{ph}' not heard in: {ws}")
        sys.exit(1)


if __name__ == "__main__":
    main(set(sys.argv[1:]))
