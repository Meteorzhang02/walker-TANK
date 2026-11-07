"""Write gamedev-evidence.json for the A6 film (film tooling; adapted from the A5 reel's build_evidence.py).
--game is _scratch/src: the git archive of walker-TANK at 41a6b8b (the revision the film shows), extracted outside the
repo. It is inventoried the way verify_gamedev.py does (no .godot/, .git/, *.uid). Files the A6 film explains are
associated with components; every other file is an exclusion with its reason. This reel is not inside the game folder.
Run: python scripts/build_evidence.py
"""
import hashlib, json
from pathlib import Path

REEL = Path(__file__).resolve().parents[1]
GAME = REEL / "_scratch/src"
CA, CB = "captures/cover_hit_burst/", "captures/damage_smoke/"
STRIP_A = [f"{CA}{r}/frame{n:08d}.png" for r in ("r0", "r1") for n in (10, 12, 15, 20, 30, 50)]
STRIP_B = [f"{CB}{r}/frame{n:08d}.png" for r in ("r0", "r1") for n in (10, 25, 58, 90, 112, 140, 165)]

COMPONENTS = {
    "a6-effect-a": ("Effect A, cover hit burst: 3 x CPUParticles2D (Flash, Debris, Dust) under one Node2D that frees itself on "
                    "Dust.finished; fired from cover.gd take_hit() line 40 via main.gd spawn_cover_burst(); the intent block, "
                    "r0/r1 fixture strips, R3 (Debris colour_ramp, strip-driven), Claude's reading/prediction/comparison, the "
                    "student's verdict, the retrigger preview and the student's play recording.",
                    ["B02", "B05", "B06", "B07", "B08"],
                    ["effects/cover_hit_burst.tscn", "effects/cover_hit_burst.gd", "scripts/cover.gd", "scripts/main.gd",
                     "previews/cover_hit_burst_preview.gd", "previews/cover_hit_burst_preview.tscn",
                     "logs/capture_cover_hit_burst_r0.log", "logs/capture_cover_hit_burst_r1.log", "TUNING.md"] + STRIP_A),
    "a6-effect-b": ("Effect B, damage smoke: GPUParticles2D + ParticleProcessMaterial; follow() maps health/max_health to "
                    "emitting and amount_ratio (on at <= 0.6, wreck 1.0), called from tank.gd; emission/process/draw settings; "
                    "turbulence; r0/r1 strips; R5 (initial velocity 20/40 -> 50/80) driven by the in-game lump; the strip "
                    "reading the student overruled; start/stop/pause.",
                    ["B02", "B03", "B04", "B09", "B10", "B11", "B12"],
                    ["effects/damage_smoke.tscn", "effects/damage_smoke.gd", "scripts/tank.gd",
                     "previews/damage_smoke_preview.gd", "previews/damage_smoke_preview.tscn",
                     "logs/capture_damage_smoke_r0.log", "logs/capture_damage_smoke_r1.log", "TUNING.md"] + STRIP_B),
    "a6-textures": ("The two particle textures, drawn by code (tools/make_particle_textures.gd): chip_6.png and soft_dot_32.png, "
                    "with their import settings and credits; no downloaded or AI textures.",
                    ["B03", "B18"],
                    ["effects/textures/chip_6.png", "effects/textures/chip_6.png.import", "effects/textures/soft_dot_32.png",
                     "effects/textures/soft_dot_32.png.import", "effects/textures/CREDITS.md", "tools/make_particle_textures.gd"]),
    "a6-process-shader": ("Godot's generated process shader from B's ParticleProcessMaterial: line 232 (start speed between "
                          "initial_velocity_min/max = 50/80) and line 447 (turbulence blends velocity 10-20 % toward the noise "
                          "direction every step), which explains the lump; LANGUAGE-NOTES A6.",
                          ["B03", "B13", "B14"],
                          ["shaders/particles_generated.gdshader", "LANGUAGE-NOTES.md", "effects/damage_smoke.tscn"]),
    "a6-tests": ("Headless tests and their limits: config 128/128 and 76/76; two mutations, each exit 1 (Godot 3 name "
                 "ignored silently); state 82 and 81 at 30/60/144 incl. two hits 0.317 s apart; the property probe; nothing "
                 "drawn is proven headless.",
                 ["B12", "B15"],
                 ["tests/test_cover_hit_burst_config.gd", "tests/test_cover_hit_burst_state.gd",
                  "tests/test_damage_smoke_config.gd", "tests/test_damage_smoke_state.gd", "tests/probe_particle_props.gd",
                  "scripts/run-test.sh", "TEST-REPORT.md",
                  "logs/test_cover_hit_burst_config_60fps.log", "logs/test_damage_smoke_config_60fps.log",
                  "logs/test_cover_hit_burst_state_30fps.log", "logs/test_cover_hit_burst_state_60fps.log",
                  "logs/test_cover_hit_burst_state_144fps.log", "logs/test_damage_smoke_state_30fps.log",
                  "logs/test_damage_smoke_state_60fps.log", "logs/test_damage_smoke_state_144fps.log",
                  "logs/a6_mutation1_godot3_name_60fps.log", "logs/a6_mutation2_value_drift_60fps.log",
                  "logs/probe_particle_props_60fps.log"]),
    "a6-prices": ("Prices against the budget: price_measure.gd medians headless (A +0.074 ms, B -0.009) and windowed GPU on the "
                  "RTX 3060 (A +0.023, B +0.077), drift 0.020/0.005; the agent's cost_particles.gd reading 6.90 ms everywhere "
                  "(1/144 s); the price scene (keys 0-3, F9 vsync); FPS 143-144, capped.",
                  ["B04", "B16", "B17"],
                  ["tests/price_measure.gd", "tests/cost_particles.gd", "previews/price_scene.gd", "previews/price_scene.tscn",
                   "logs/price_measure_realtime.log", "logs/price_measure_windowed.log", "logs/price_measure_after_f9.log",
                   "logs/cost_particles_realtime.log", "TEST-REPORT.md"]),
    "a6-record": ("The record: the brief and revisions R1-R5, agent mistakes the student caught, problems the agent caught in "
                  "the brief, contributions, the source revision.",
                  ["B00", "B18"],
                  ["CHANGE-BRIEF.md", "FRICTIONAL.md", "SOURCES.md", "README.md", "CLAUDE.md", "project.godot"]),
}

REASONS = [
    ("youtube/", "Earlier films' reel folders (A2, A3, A5), preserved and not part of this A6 film."),
    (".claude/", "Local Claude Code settings; not read for the film."),
    ("prompts/", "Claude Code prompts for A6 (and earlier); cited through FRICTIONAL.md and SOURCES.md, not shown."),
    ("docs/", "Earlier assignments' documents (A5 report and captures), outside this A6 film."),
    ("logs/", "Other run logs (A5 suites, reimports, tool parse check): baselines only, not shown in this film."),
    ("tests/", "Earlier suites (A5, A2/A3 checks), reported only as unchanged baselines in TEST-REPORT.md."),
    ("tools/", "Other tools (A2/A3/A5 asset processing and capture), not part of A6."),
    ("shaders/", "A5 shaders, unchanged by A6."),
    ("materials/", "A5 materials, unchanged by A6."),
    ("scripts/", "Game scripts A6 does not change (player, enemy, shell, audio, gallery, hit flash driver)."),
    ("scenes/", "Game scenes, unchanged by A6 (the effects are instanced from code)."),
    ("assets/", "A2/A3/A5 art and audio; the effects play over the A2 ground and cover but these files are unchanged."),
    ("design/", "A2 design material, outside this A6 film."),
    ("", "Assignment 2/3/5 documents and settings unchanged by A6 and covered by the earlier films."),
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
    files = [{"path": f, "sha256": sha(GAME / f), "role": "A6 source or evidence", "component_ids": cids}
             for f, cids in sorted(owner.items())]
    exclusions = [{"path": f, "reason": next(r for pre, r in REASONS if f.startswith(pre))} for f in inv if f not in owner]
    sheet = json.loads((REEL / "beat_sheet.json").read_text(encoding="utf-8"))
    beats = {b["beat_id"]: b for b in sheet["beats"]}
    excerpts = []
    for bid in ("B03", "B06", "B10", "B13"):
        p = beats[bid]["shot"]["remotion"]["props"]
        n = p["code"].count("\n") + 1
        excerpts.append({"beat_id": bid, "path": p["path"].removeprefix("res://"), "start_line": p["startLine"],
                         "end_line": p["startLine"] + n - 1, "text": p["code"]})

    def media(rel):
        return {"path": rel, "sha256": sha(REEL / rel)}
    pairs = [
        {"code_beat": "B03", "result_beat": "B04",
         "observation": "The GPUParticles2D node whose emission (amount 48, lifetime 1.6), process material and draw settings "
                        "(soft_dot_32.png, MIX, visibility_rect) were just read runs on the RTX 3060 in the 4K fixture: a "
                        "column of soft grey puffs from the turret, emitting from frame 10; beside it the recorded headless "
                        "price (B -0.009 ms, render_gpu 0.000).",
         "media": media("media/B04.mp4")},
        {"code_beat": "B06", "result_beat": "B07",
         "observation": "Frame 20 of the student's r0 and r1 fixture strips (same seed): with the R3 stop (#8E5040 opaque at "
                        "0.6) faint red-brown chips are visible left of the wall where r0 shows almost none; Claude: partly "
                        "held; the student kept r1.",
         "media": media("evidence/ev-a-frame20.png")},
        {"code_beat": "B10", "result_beat": "B11",
         "observation": "After R5 (initial velocity 50/80) the r1 stills at frames 58 and 140 still show a compact lump only "
                        "slightly higher than r0 (Claude: prediction failed), while the student's play recording from 29 s "
                        "shows the smoke rising from YunqiZ as a column: the reading the student overruled.",
         "media": media("media/B11.mp4")},
        {"code_beat": "B13", "result_beat": "B14",
         "observation": "In the 4K fixture, enlarged on the turret, the puffs drift around the turret rather than climbing "
                        "away, consistent with line 447 turning each velocity 10-20 % toward the noise every step "
                        "(confirmed from the code, not by a turbulence-off strip).",
         "media": media("media/B14.mp4")},
    ]
    data = {"schema_version": 1, "teaching_contract": "code-then-result-v1",
            "game_revision": sheet["metadata"]["game"]["revision"],
            "game_source_revision": sheet["metadata"]["game"]["game_source_revision"],
            "scope_note": "Assignment-focused film: only Assignment 6 files are explained; other files are excluded with "
                          "reasons. --game is the git archive of 41a6b8b in _scratch/src (LF line endings, as committed). "
                          "The play recording and the film's own fixture captures live outside the game (SOURCES.md).",
            "files": files,
            "components": [{"id": cid, "explanation": e, "beat_ids": b, "files": f} for cid, (e, b, f) in COMPONENTS.items()],
            "excerpts": excerpts, "exclusions": exclusions, "code_result_pairs": pairs}
    (REEL / "gamedev-evidence.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(files), "files,", len(exclusions), "exclusions")


if __name__ == "__main__":
    main()
