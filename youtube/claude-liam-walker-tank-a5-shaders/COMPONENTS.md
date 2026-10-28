# COMPONENTS — what the A5 film explains (scope: Assignment 5 only)

| Component | Files | Beats | Explained |
|---|---|---|---|
| a5-hit-flash | shaders/hit_flash.gdshader, scripts/hit_flash_driver.gd, CHANGE-BRIEF.md, tools/capture_hit_flash.gd, hit_flash_* captures + CSV | B02–B04 | fragment() per pixel, state only through hit_amount, the colour line, the driver; play; P1/P2 predicted vs measured, the turret revision, no clamp at 2.0 |
| a5-hint | shaders/hint_experiment.gdshader, materials/hint_*.tres, scenes/hint_experiment.tscn, tools/make_hint_png.gd, tools/capture_hint.gd, assets/hint/grey_3x1.png(+.import), hint capture + CSV | B05, B06 | one file, two samplers; colour vs data; 6/6 exact |
| a5-materials | shaders/brick_surface.gdshader, materials/cover_wall_*.tres, scenes/asset_room_3d.tscn, tools/capture_materials.gd, MATERIALS.md, brick diff/rough maps + ATTRIBUTION, materials captures + CSVs | B06, B07, B09 | one shader, two materials; shader edit vs material edit; sweep; ALBEDO lit on three faces |
| a5-language | shaders/standard_generated.gdshader, LANGUAGE-NOTES.md, shaders/brick_surface.gdshader | B08, B09 | shader_type, hints, ALBEDO; generated lines 7/19 vs brick 4/9 |
| a5-tests | tests/test_hit_flash.gd, tests/test_materials.gd, scripts/run-test.sh, TEST-REPORT.md, docs/a5/step2-output.txt, logs (9) | B10 | results, mutations, limits |
| a5-record | FRICTIONAL.md, SOURCES.md, README.md, CLAUDE.md, project.godot, docs/a5/captures-output.txt | B00, B11 | mistakes caught, contributions, texture source, revision |

Input → state → output trace: shell hit → `damaged` → driver `_set_amount(1.0)` → line 70 `set_shader_parameter`
→ uniform `hit_amount` (line 3) → colour line (line 8) per pixel → red YunqiZ in play (B03) and the measured pixels
(B04). Trade-off named: a shared material means hull and turret always agree, which is also why P1 was read off the
turret, not the hull.

Excluded (reasons per file in gamedev-evidence.json): A2/A3 runtime and assets, earlier films' reel folders, this
reel's own folder, other captures/logs/tools not shown, Claude Code session transcripts.
