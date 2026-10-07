"""Write gamedev-evidence.json (schema 1, teaching_contract code-then-result-v1) for this reel.
Inventories every authored file under the game folder (except .godot/, .git/ and *.uid), hashes it,
assigns a role and component, records the verbatim excerpts from the beat sheet, and pairs each code
beat with the visible result beat that follows it. The reel itself lives inside the game folder
(youtube/), so its files are listed as exclusions with that reason. Run before every check.
"""
import fnmatch, hashlib, json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# (component id, explanation, beats, [(glob, role)])
COMPONENTS = [
    ("concept-and-plan", "One-page concept with core loop and the four pillars, the storyboard, and the change brief "
     "(asset list, event-to-sound map, music behaviour, predicted failures). Shown as the assignment frame and the pillar grid.",
     ["B02", "B03", "B04"],
     [("CONCEPT.md", "concept document"), ("STORYBOARD.md", "storyboard"), ("CHANGE-BRIEF.md", "plan and predictions"),
      ("README.md", "project readme"), ("design/storyboard/*", "storyboard sketches (code-drawn by Claude)")]),
    ("character-sheet", "The YunqiZ character sheet: silhouette test, facings, poses, collision circle, palette, "
     "consistency rules. The silhouette test added the dozer blade and storage box.",
     ["B05"],
     [("CHARACTER-SHEET.md", "character sheet"), ("design/character/*", "planning sketches and their generator (Claude)")]),
    ("img2img-guides", "Code-drawn img2img guide images (v1 flat, v2 shaded, v3/v3.1 turret) and stripe masks. "
     "The v1 guide produced flat results; draw_guides_v2.py's per-face gradients fixed it.",
     ["B06", "B07", "B08"],
     [("design/guides/*", "img2img guide image or generator (Claude, code-drawn)"),
      ("design/.gdignore", "keeps design/ out of the Godot import")]),
    ("raw-generations", "Raw generative-model outputs kept as evidence, with ComfyUI metadata embedded in each PNG/FLAC, "
     "and the cut-out sprites before resizing. Not loaded by the game.",
     ["B09", "B30"],
     [("assets/raw/*", "raw model output (SDXL / Stable Audio 3)"), ("assets/sprites/*", "edited full-size sprite (cutout, stripe, colour match)")]),
    ("sprite-tools", "Claude-written edit scripts: cutout (keep every part of 2,000 px or more), stripe painting, olive colour match, "
     "resizing to game textures.",
     ["B10", "B12"],
     [("tools/cutout_hull.py", "edit script: background cutout"), ("tools/process_sprites.py", "edit script: stripe + colour match"),
      ("tools/stripe_mask.py", "edit script: stripe masks"), ("tools/prepare_game_assets.py", "edit script: resize to game textures"),
      ("tools/.gdignore", "keeps tools/ out of the Godot import")]),
    ("asset-checks", "The student's check sheets and rejected-output thumbnails: hull and turret checks, the eight-facing sheet, "
     "the rejected contact sheets, and the audio waveform checks.",
     ["B06", "B11", "B13", "B31"],
     [("design/asset-log/*", "check sheet or rejected thumbnail")]),
    ("game-textures", "The in-game textures the slice loads: five hull and five turret facings, three cover stages, the ground tile, "
     "with their Godot import settings.",
     ["B13", "B15", "B30"],
     [("assets/game/*", "in-game texture or its import settings")]),
    ("tank", "Base tank (tank.gd): facing slots from movement and aim, idle/moving wobble, recoil, damage look, die/reset; "
     "player input (player.gd); enemy wander-aim-fire AI with grey tint (enemy.gd).",
     ["B14", "B15", "B18", "B19"],
     [("scripts/tank.gd", "runtime: base tank"), ("scripts/player.gd", "runtime: player input"), ("scripts/enemy.gd", "runtime: enemy AI")]),
    ("shell-and-cover", "Shells travel on the ground plane, hit once (has_hit); cover cracks after 2 hits, breaks after 4 and stops blocking.",
     ["B16", "B17"],
     [("scripts/shell.gd", "runtime: shell"), ("scripts/cover.gd", "runtime: destructible cover")]),
    ("game-loop", "main.gd builds the arena, input map, HUD and effects in code; handles failure/respawn, victory, pause and mute; "
     "the health-bar colour revision. main.tscn is a single node with this script.",
     ["B20", "B21", "B22", "B23", "B25", "B26"],
     [("scripts/main.gd", "runtime: arena, HUD, game flow"), ("scenes/main.tscn", "main scene (one node + script)"),
      ("project.godot", "project config: main scene, 1280x720 canvas_items")]),
    ("audio", "audio.gd plays every SFX and the music loop on separate Music/SFX buses and counts each request; the five WAV SFX, "
     "the OGG loop (and its 3x listening preview), import settings, and the Claude-written trimming/loop/analysis scripts.",
     ["B17", "B21", "B30"],
     [("scripts/audio.gd", "runtime: sound and music"), ("assets/audio/*", "game audio asset or import settings"),
      ("tools/process_sfx.py", "edit script: SFX trim/fade/normalise"), ("tools/make_loop.py", "edit script: bar-aligned loop cut"),
      ("tools/analyze_sfx.py", "analysis script: SFX bands")]),
    ("tests-and-playtest", "The automated sound-trigger check, the test report, the student's playtest screenshots, and the "
     "test gallery scene used for the character-against-sheet check.",
     ["B27", "B28", "B29"],
     [("tests/test_sound_triggers.gd", "automated check"), ("TEST-REPORT.md", "test report"), ("design/test/*", "playtest/test screenshot"),
      ("scripts/gallery.gd", "test gallery script"), ("scenes/gallery.tscn", "test gallery scene")]),
    ("provenance", "Asset log (every prompt, seed, setting, outcome), sources and licences, and the dated Frictional log of decisions.",
     ["B30", "B31", "B32"],
     [("ASSET-LOG.md", "asset log"), ("SOURCES.md", "sources and licences"), ("FRICTIONAL.md", "design log")]),
]
OBS = {
    "B08": "v2 guide shows per-face light-to-dark shading, wheels and panel lines; v1 is flat fills with outlines.",
    "B11": "Check sheet row 1: right-facing hull cutout keeps its separate dozer blade (the >=2000 px parts rule).",
    "B13": "All eight facings share the matched olive; three are flip_h mirrors; stripe reads in every facing.",
    "B15": "run-01 0-13 s: idle hull shiver with turret following the cursor, then eight drive legs with the hull sprite changing per facing.",
    "B17": "run-01 13-18 s: the near-left wall shows cracked after hit 2 (frame 420) and broken rubble after hit 4 (frame 505), one cover-hit sound each.",
    "B19": "run-01 30-43 s: hit to 50 % at frame 975 starts smoke; hit to 25 % at frame 1207 adds flames; bar yellow then red.",
    "B21": "run-01 18-30 s: death at frame 554 stops the music (log music_state stopped), respawn message, respawn at frame 614 restarts music.",
    "B23": "run-01 43-47 s: second death at frame 1320 and respawn at frame 1380; the last kill follows in B24 (victory sound once, frame 1426).",
    "B26": "Before: default grey fill in the student's screenshot. After: run-01 frames show green at 100 %, yellow at 50 %, red at 25 %.",
    "B28": "Recorded run: 8 PASS, RESULT 0 failed, exit 0, followed by ObjectDB leak and resources-in-use warnings.",
}
EXCLUDE = [("youtube/*", "this film's own build folder (reel output inside the game package), not game source"),
           (".gitignore", "repository ignore rules; not part of the playable slice")]


def inventory():
    return sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*")
                  if p.is_file() and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts) and p.suffix != ".uid")


def main():
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}
    order = [b["beat_id"] for b in sheet["beats"]]
    files, exclusions, comps = [], [], {c[0]: {"id": c[0], "explanation": c[1], "beat_ids": c[2], "files": []} for c in COMPONENTS}
    unassigned = []
    for rel in inventory():
        ex = next((r for g, r in EXCLUDE if fnmatch.fnmatch(rel, g)), None)
        if ex:
            exclusions.append({"path": rel, "reason": ex}); continue
        hit = None
        for cid, _, _, pats in COMPONENTS:
            for g, role in pats:
                if fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel, g.rstrip("*") + "**") or (g.endswith("/*") and rel.startswith(g[:-1])):
                    hit = (cid, role); break
            if hit:
                break
        if not hit:
            unassigned.append(rel); continue
        files.append({"path": rel, "sha256": sha(GAME / rel), "role": hit[1], "component_ids": [hit[0]]})
        comps[hit[0]]["files"].append(rel)
    if unassigned:
        raise SystemExit("unassigned files: " + ", ".join(unassigned))
    excerpts, pairs = [], []
    for b in sheet["beats"]:
        rem = b.get("shot", {}).get("remotion", {})
        if rem.get("pattern") == "GodotDevWorkbench" and rem.get("props", {}).get("code"):
            p = rem["props"]
            path = p["path"].replace("res://", "")
            end = p["startLine"] + p["code"].count("\n")
            excerpts.append({"beat_id": b["beat_id"], "path": path, "start_line": p["startLine"], "end_line": end, "text": p["code"]})
            nxt = beats[order[order.index(b["beat_id"]) + 1]]
            media = nxt.get("shot", {}).get("evidence_media")
            pairs.append({"code_beat": b["beat_id"], "result_beat": nxt["beat_id"], "observation": OBS.get(nxt["beat_id"], ""),
                          "media": {"path": media, "sha256": sha(REEL / media) if media and (REEL / media).exists() else ""}})
    out = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
           "game": {"name": "walker-TANK", "revision": sheet["metadata"]["game"]["revision"], "engine": sheet["metadata"]["game"]["engine"]},
           "files": files, "components": [c for c in comps.values()], "excerpts": excerpts, "exclusions": exclusions,
           "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"files {len(files)} · exclusions {len(exclusions)} · components {len(comps)} · excerpts {len(excerpts)} · pairs {len(pairs)}")


if __name__ == "__main__":
    main()
