"""Write gamedev-evidence.json for the A5 film (film tooling).
Inventories the game folder the way verify_gamedev.py does (no .godot/, .git/, *.uid). Files the A5 film explains
are associated with components; every other file is listed as an exclusion with its reason.
This reel lives inside the game folder, so its own files are in the inventory too: re-run this script last, right
before each `./art godot-gamedev --check`.
Run: python scripts/build_evidence.py
"""
import hashlib, json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = REEL.parents[1]
CAP = "docs/a5/captures/"

COMPONENTS = {
    "a5-hit-flash": ("2D hit flash: hit_flash.gdshader (canvas_item; fragment() per pixel; game state only via the uniform "
                     "hit_amount; the colour line, also CHANGE-BRIEF.md line 45), the driver that sets hit_amount "
                     "(line 70; 1.0 on damaged, linear fade over 0.5 s), the student's play recording, and the scripted "
                     "captures at 0.0/0.5/1.0/2.0 with P1/P2 predicted vs measured (P2 exact; P1 under the turret, "
                     "recomputed in the dated Revision; 2.0 -> (255,0,0), no clamp).",
                     ["B02", "B03", "B04"],
                     ["shaders/hit_flash.gdshader", "scripts/hit_flash_driver.gd", "CHANGE-BRIEF.md",
                      "tools/capture_hit_flash.gd", CAP + "hit_flash_0.0.png", CAP + "hit_flash_0.5.png",
                      CAP + "hit_flash_1.0.png", CAP + "hit_flash_2.0.png", CAP + "hit_flash_pixels.csv"]),
    "a5-hint": ("Texture as information: hint_experiment.gdshader lines 4-5 bind one 64/128/192 PNG with and without "
                "source_color; hint_both.png measured 64/128/192 and 137/188/225 as predicted, 6/6 exact.",
                ["B05", "B06"],
                ["shaders/hint_experiment.gdshader", "materials/hint_srgb.tres", "materials/hint_raw.tres",
                 "scenes/hint_experiment.tscn", "tools/make_hint_png.gd", "tools/capture_hint.gd",
                 "assets/hint/grey_3x1.png", "assets/hint/grey_3x1.png.import", CAP + "hint_both.png", CAP + "hint_pixels.csv"]),
    "a5-materials": ("One brick_surface shader, two .tres materials on two cover_wall instances; the shader edit darkened "
                     "both walls, the material edit changed only the damaged wall (CSV means); a sweep of brightness and "
                     "uv_scale ends; ALBEDO lit on three faces of the intact wall (means measured from the capture).",
                     ["B06", "B07", "B09"],
                     ["shaders/brick_surface.gdshader", "materials/cover_wall_intact.tres", "materials/cover_wall_damaged.tres",
                      "scenes/asset_room_3d.tscn", "tools/capture_materials.gd", "MATERIALS.md",
                      "assets/textures/brick/red_bricks_04_diff_1k.png", "assets/textures/brick/red_bricks_04_rough_1k.png",
                      "assets/textures/brick/ATTRIBUTION.md", CAP + "materials_side_by_side.png",
                      CAP + "material_edit_damaged_only.png", CAP + "materials_captures.csv",
                      CAP + "shader_edit_materials_side_by_side.png", CAP + "shader_edit_materials_captures.csv",
                      CAP + "sweep_brightness_max.png", CAP + "sweep_roughness_scale_min.png",
                      CAP + "sweep_uv_scale_min.png", CAP + "sweep_uv_scale_max.png"]),
    "a5-language": ("The Godot shading language: shader_type (brick line 1), hints (hint_range, source_color), the "
                    "built-in ALBEDO (line 33), and Godot's generated StandardMaterial3D shader (line 7 colour, line 19 "
                    "data) beside the student's brick lines 4 and 9; LANGUAGE-NOTES answers.",
                    ["B08", "B09"],
                    ["shaders/standard_generated.gdshader", "LANGUAGE-NOTES.md", "shaders/brick_surface.gdshader"]),
    "a5-tests": ("Headless tests and their limits: test_hit_flash 50/50 at 30/60/144 fps, test_materials 76/76, baselines "
                 "18/18 and 8/8, three mutations each exit 1; what headless cannot show.",
                 ["B10"],
                 ["tests/test_hit_flash.gd", "tests/test_materials.gd", "scripts/run-test.sh", "TEST-REPORT.md",
                  "docs/a5/step2-output.txt", "logs/test_hit_flash_30fps.log", "logs/test_hit_flash_60fps.log",
                  "logs/test_hit_flash_144fps.log", "logs/test_materials_60fps.log", "logs/check_a3_assets_60fps.log",
                  "logs/test_sound_triggers_60fps.log", "logs/mutation1_semicolon_60fps.log",
                  "logs/mutation2_rename_60fps.log", "logs/mutation3_no_source_color_60fps.log"]),
    "a5-record": ("The record: agent mistakes the student caught (CLAUDE.md scope, Use External key names, probe file in "
                  "logs/), human and AI contributions, the texture source and licence, the source revision.",
                  ["B00", "B11"],
                  ["FRICTIONAL.md", "SOURCES.md", "README.md", "CLAUDE.md", "project.godot", "docs/a5/captures-output.txt"]),
}

OWN = "This film's own reel folder (generated beat sheet, audio, renders and records), not game source."
REASONS = [
    ("youtube/claude-liam-walker-tank-a5-shaders/", OWN),
    ("youtube/", "Earlier films' reel folders (A2, A3), preserved and not part of this A5 film."),
    (".claude/", "Local Claude Code settings; not read for the film."),
    (CAP + "shader_edit_", "Further shader-edit captures; the film uses the side-by-side capture and the CSV numbers only."),
    (CAP, "Further scripted captures (albedo_tint and roughness_scale sweeps, default steps) not shown in this short film."),
    ("docs/a5/sessions/", "Claude Code prompts and transcripts; cited through FRICTIONAL.md and SOURCES.md, not shown."),
    ("docs/a5/", "A5 working outputs and raw notes; facts are taken from the finished documents that cite them."),
    ("logs/", "Other run logs (reimports, tool parse check), not shown in this film."),
    ("tests/", "Other tests (A2/A3 or the capture-tool parse check), reported only as results."),
    ("tools/", "Other tools (A2/A3 asset processing, cover_wall inspection), not explained in this A5 film."),
    ("shaders/", "Shader file outside the film's excerpts."),
    ("materials/", "Material outside the film's scope."),
    ("assets/textures/brick/", "Brick map or import sidecar not shown (normal map only in the Step 4 scratch scene)."),
    ("scenes/", "Other scenes (the 2D game, the Step 4 scratch scene), unchanged by the film's components."),
    ("", "Assignment 2/3 material unchanged by A5 and covered by the earlier films; outside this short A5 film."),
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
    files = [{"path": f, "sha256": sha(GAME / f), "role": "A5 source or evidence", "component_ids": cids}
             for f, cids in sorted(owner.items())]
    exclusions = [{"path": f, "reason": next(r for pre, r in REASONS if f.startswith(pre))} for f in inv if f not in owner]
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}
    excerpts = []
    for bid in ("B02", "B05", "B08"):
        p = beats[bid]["shot"]["remotion"]["props"]
        n = p["code"].count("\n") + 1
        excerpts.append({"beat_id": bid, "path": p["path"].removeprefix("res://"), "start_line": p["startLine"],
                         "end_line": p["startLine"] + n - 1, "text": p["code"]})

    def media(rel):
        return {"path": rel, "sha256": sha(REEL / rel)}
    pairs = [
        {"code_beat": "B02", "result_beat": "B03",
         "observation": "In the student's play recording (source 4.5-14.7 s, not retimed) YunqiZ turns red when a shell "
                        "hits (source 6.65 s) and the red fades in about half a second; a second hit (11.0 s) flashes "
                        "again; no enemy tank turns red.",
         "media": media("media/B03.mp4")},
        {"code_beat": "B05", "result_beat": "B06",
         "observation": "Scripted in-engine capture: Quad A (line 4, source_color) shows 64/128/192, Quad B (line 5, no "
                        "hint) shows 137/188/225, matching the hand predictions 6/6 (hint_pixels.csv).",
         "media": media("evidence/ev-hint.png")},
        {"code_beat": "B08", "result_beat": "B09",
         "observation": "Scripted in-engine capture of the spatial shader's ALBEDO (line 33) after lighting: one brick "
                        "texture gives red means 87.5 (top), 73.4 (front), 60.8 (+x end), measured from "
                        "materials_side_by_side.png by make_evidence.py.",
         "media": media("evidence/ev-litwall.png")},
    ]
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
            "game_revision": sheet["metadata"]["game"]["revision"],
            "scope_note": "Assignment-focused short film: only Assignment 5 files are explained; other files are excluded "
                          "with reasons. The student's play recording lives outside the game folder (SOURCES.md).",
            "files": files,
            "components": [{"id": cid, "explanation": e, "beat_ids": b, "files": f} for cid, (e, b, f) in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(files), "files,", len(exclusions), "exclusions")


if __name__ == "__main__":
    main()
