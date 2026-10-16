"""Write gamedev-evidence.json for the A3 film (film tooling).
Inventories the game folder the way verify_gamedev.py does (no .godot/, .git/, *.uid). Files the A3 film explains
are associated with components; every other file is listed as an exclusion with its reason.
Run after make_sheet.py and media are final: python scripts/build_evidence.py
"""
import hashlib, json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = Path(r"D:/CSYE7270/assignment2/walker-TANK")

COMPONENTS = {
    "a3-brief": ("The game and its three assets: CHANGE-BRIEF.md sizes, roles, budgets, and the dated hedgehog revision "
                 "(2.4 m beams -> 2.125 m). project.godot identifies the 2D game; play-01 is the student's own game screenshot.",
                 ["B02", "B10"],
                 ["CHANGE-BRIEF.md", "project.godot", "design/test/play-01-normal-combat.png"]),
    "a3-blender": ("Blender MCP build: the student's Blender session, denied MCP tools, the build scripts Claude wrote and "
                   "ran (including the hand-edit step 7 in build_cover_wall.py), the exporter and the .blend files.",
                   ["B03", "B04", "B05"],
                   [".claude/settings.json", "BLENDER-NOTES.md", "design/blender/blender-window.png",
                    "tools/blender/build_cover_wall.py", "tools/blender/build_ammo_crate.py",
                    "tools/blender/build_tank_hedgehog.py", "tools/blender/export_glb.py",
                    "design/blender/cover_wall.blend", "design/blender/ammo_crate.blend",
                    "design/blender/tank_hedgehog.blend"]),
    "a3-scene": ("The Godot 3D asset room: three .glb instances at scale 1 along X, the hull-size reference box with its "
                 "NOT-an-asset label, one light, a fixed camera. Shown as source, then running (Movie Maker capture).",
                 ["B06", "B07"],
                 ["scenes/asset_room_3d.tscn", "assets/models/cover_wall.glb", "assets/models/cover_wall.glb.import",
                  "assets/models/ammo_crate.glb", "assets/models/ammo_crate.glb.import",
                  "assets/models/tank_hedgehog.glb", "assets/models/tank_hedgehog.glb.import",
                  "design/godot/asset_room_3d.png"]),
    "a3-check": ("Headless check: brief sizes in Godot axes, 0.01 m tolerance, size/lowest-y/root-scale/height-axis per "
                 ".glb; 18/18 PASS, exit 0, re-run on an isolated copy; its stated limits (nothing drawn).",
                 ["B08", "B09"],
                 ["tests/check_a3_assets.gd", "TEST-REPORT.md"]),
    "a3-record": ("What Claude got wrong, what remains uncertain, human and AI contributions and the source revision, "
                  "from FRICTIONAL.md (Assignment 3 part), SOURCES.md and README.md.",
                  ["B10", "B11"],
                  ["FRICTIONAL.md", "SOURCES.md", "README.md"]),
}

A2 = "Assignment 2 2D game material, unchanged by Assignment 3 and explained in the A2 film; outside this short A3 film's scope."
REASONS = [
    ("youtube/", "The Assignment 2 film's own reel folder (generated film records/media), not game source."),
    (".claude/settings.local.json", "Personal local permissions file kept out of Git; not read for the film."),
    ("design/blender/", "Blender auto-backup (.blend1), gitignored; not an asset source."),
    ("docs/a2/", A2), ("scripts/", A2 + " (runtime GDScript of the 2D game)"),
    ("scenes/", A2), ("tests/", A2), ("assets/", A2), ("tools/", A2 + " (A2 image/audio processing tools)"),
    ("design/", A2), ("", A2),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    inv = sorted(p.relative_to(GAME).as_posix() for p in GAME.rglob("*")
                 if p.is_file() and not any(x in (".godot", ".git") for x in p.relative_to(GAME).parts)
                 and p.suffix != ".uid")
    owner = {}
    for cid, (_, _, files) in COMPONENTS.items():
        for f in files:
            assert f in inv, f
            owner.setdefault(f, []).append(cid)
    files = [{"path": f, "sha256": sha(GAME / f), "role": "A3 source", "component_ids": cids}
             for f, cids in sorted(owner.items())]
    exclusions = []
    for f in inv:
        if f in owner:
            continue
        reason = next(r for pre, r in REASONS if f.startswith(pre))
        exclusions.append({"path": f, "reason": reason})
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}
    excerpts = []
    for bid in ("B06", "B08"):
        p = beats[bid]["shot"]["remotion"]["props"]
        n = p["code"].count("\n") + 1
        excerpts.append({"beat_id": bid, "path": p["path"].removeprefix("res://"), "start_line": p["startLine"],
                         "end_line": p["startLine"] + n - 1, "text": p["code"]})
    pairs = [
        {"code_beat": "B06", "result_beat": "B07",
         "observation": "The running scene shows the three .glb instances side by side along X and the grey hull-size box "
                        "with its 'NOT an asset' label, as the .tscn lines place them; fixed camera, no motion.",
         "media": {"path": "media/B07.mp4", "sha256": sha(REEL / "media/B07.mp4")}},
        {"code_beat": "B08", "result_beat": "B09",
         "observation": "Recorded headless output: each measured size matches the brief values in lines 24-26 within "
                        "TOL; 18/18 PASS, RESULT: PASS, exit code 0.",
         "media": {"path": "evidence/ev-headless.png", "sha256": sha(REEL / "evidence/ev-headless.png")}},
    ]
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1", "game_revision": "9baa12c",
            "scope_note": "Assignment-focused short film: only Assignment 3 files are explained; A2 files are excluded "
                          "with reasons (the A2 film covers them).",
            "files": files,
            "components": [{"id": cid, "explanation": e, "beat_ids": b, "files": f}
                           for cid, (e, b, f) in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(files), "files,", len(exclusions), "exclusions")


if __name__ == "__main__":
    main()
