"""Author beat_sheet.json for claude-liam-walker-tank-gamedev from beats.py (film tooling).
Code excerpts are read verbatim from the game by line range; evidence images are embedded as data
URIs; measured audio fields are preserved when a beat's narration is unchanged.
Run from the reel folder: python scripts/make_sheet.py
"""
import base64, hashlib, io, json, sys
from pathlib import Path
from PIL import Image

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1]
sys.path.insert(0, str(REEL / "scripts"))
import beats as B  # noqa: E402

KEEP = ("audio_file", "actual_duration_s", "tts_duration_s", "audio_pad", "render_duration_s", "build",
        "game_audio", "cue_times")


def excerpt(path, a, b):
    lines = (GAME / path).read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[a - 1:b])


def data_uri(rel, max_w=3300):
    im = Image.open(REEL / rel).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=93)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build():
    old = {}
    sp = REEL / "beat_sheet.json"
    if sp.exists():
        for b in json.loads(sp.read_text(encoding="utf-8"))["beats"]:
            old[b["beat_id"]] = b
    beats = []
    for spec in B.BEATS:
        b = {k: v for k, v in spec.items() if k not in ("code_src", "image_src", "cue_spec", "props")}
        b.setdefault("voice", "am_onyx")
        b.setdefault("engine", "kokoro")
        shot = b.setdefault("shot", {})
        if "props" in spec:
            props = json.loads(json.dumps(spec["props"]))
            if "code_src" in spec:
                path, a, z = spec["code_src"]
                props["code"] = excerpt(path, a, z)
                props["path"] = f"res://{path}" if not path.startswith(("tools/", "design/")) else path
                props["startLine"] = a
            if "image_src" in spec:
                props["image"] = data_uri(spec["image_src"]) if (REEL / spec["image_src"]).exists() else ""
                shot["evidence_media"] = spec["image_src"]
            shot.setdefault("remotion", {})["pattern"] = spec["pattern"]
            shot["remotion"]["props"] = props
        prev = old.get(b["beat_id"])
        if prev and prev.get("narration_text") == b.get("narration_text"):
            for k in KEEP:
                if k in prev:
                    b[k] = prev[k]
            pr = (prev.get("shot", {}).get("remotion") or {})
            if "rendered" in pr and shot.get("remotion", {}).get("props") == pr.get("props"):
                shot["remotion"]["rendered"] = pr["rendered"]
        if "cue_spec" in spec:
            b["cue_spec"] = spec["cue_spec"]
            if "cue_times" in b and "remotion" in shot:
                shot["remotion"]["props"]["cues"] = b["cue_times"]
        dur = b.get("actual_duration_s")
        if dur and "remotion" in shot:
            shot["remotion"]["props"]["durationSeconds"] = dur
        beats.append(b)
    qcr = REEL / "qc-regions.json"
    if qcr.exists():
        for b in beats:
            q = json.loads(qcr.read_text(encoding="utf-8")).get(b["beat_id"])
            if q:
                b["qc"] = q
    sheet = {"metadata": B.METADATA, "beats": beats}
    sp.write_text(json.dumps(sheet, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {sp.name}: {len(beats)} beats")


if __name__ == "__main__":
    build()
