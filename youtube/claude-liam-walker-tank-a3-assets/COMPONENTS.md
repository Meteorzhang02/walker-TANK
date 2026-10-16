# COMPONENTS — what the A3 film explains (scope: Assignment 3 only)

| Component | Files | Beats | Explained |
|---|---|---|---|
| a3-brief | CHANGE-BRIEF.md, project.godot, design/test/play-01-normal-combat.png | B02, B10 | the 2D game, the three assets and why the game needs each; the dated hedgehog revision |
| a3-blender | .claude/settings.json, BLENDER-NOTES.md, tools/blender/*.py, design/blender/*.blend, blender-window.png | B03–B05 | MCP setup with libraries/generators off and 4 tools denied; one request → plan → built cover_wall; the hand edit and its 0.7 mm |
| a3-scene | scenes/asset_room_3d.tscn, assets/models/*.glb (+ .import), design/godot/asset_room_3d.png | B06, B07 | three instances at scale 1, the hull-size reference box; the running scene |
| a3-check | tests/check_a3_assets.gd, TEST-REPORT.md | B08, B09 | brief sizes in Godot axes, 0.01 m tolerance, what it measures; 18/18 and its limits |
| a3-record | FRICTIONAL.md, SOURCES.md, README.md | B10, B11 | Claude's errors, uncertainties, next step, human/AI split, revision |

Input → state → output trace: brief size (CHANGE-BRIEF) → `ASSETS` constant (B08, line 24–26) → measured AABB in the
headless run (B09) → PASS/FAIL and exit code. Trade-off named: the 0.01 m tolerance is strict, but the check measures
each .glb at the origin, so it cannot see the copies placed in the scene or anything visual.

Excluded (3231 files, reasons in gamedev-evidence.json): the A2 2D game runtime and assets (unchanged by A3, covered by
the A2 film), the A2 film's own reel folder, `.blend1` backups, `.claude/settings.local.json`.
