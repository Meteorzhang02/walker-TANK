# COMPONENTS — what each part of walker-TANK does, and where the film shows it

Inventory: every authored file of commit 4616fc7 (187 files, `.uid` and `.godot/` excluded) is hashed and assigned in
`gamedev-evidence.json`. Exclusions: `.gitignore` and this film's own `youtube/` folder.

| Component | Files | What it does | Beats | Trade-off named |
|---|---|---|---|---|
| concept-and-plan | CONCEPT, STORYBOARD, CHANGE-BRIEF, README, storyboard sketches | Pillars, loop, event-to-sound map, predictions | B02–B04 | Panel 1 zoom and panel 8 illustration not built |
| character-sheet | CHARACTER-SHEET, design/character/* | Silhouette test → blade + box; 8 facings; collision circle | B05 | Circle ignores blade/barrel overhang (favours the player) |
| img2img-guides | design/guides/** (v1, v2, v3, v3.1, masks) | Code-drawn img2img inputs | B06–B08 | Guide shape controls output more than denoise does |
| raw-generations | assets/raw/**, assets/sprites/** | Raw model output with embedded metadata; edited full-size sprites | B09, B30 | T-12 log row disagrees with its file |
| sprite-tools | tools/cutout_hull.py, process_sprites.py, stripe_mask.py, prepare_game_assets.py | Cutout, stripe, colour match, resize | B10, B12 | Stale docstring in cutout_hull.py |
| asset-checks | design/asset-log/** | Check sheets, rejected thumbnails, waveforms | B06, B11, B13, B31 | IoU numbers are reported by the log, not re-measured in the film |
| game-textures | assets/game/** | 5 hull + 5 turret facings, cover ×3, ground | B13, B15, B30 | Textures at 0.1728 scale drawn at 0.5: soft when enlarged |
| tank | scripts/tank.gd, player.gd, enemy.gd | Facing slots, idle/moving wobble, recoil, damage look, die/reset, enemy AI | B14, B15, B18, B19 | Hull snaps between 8 facings |
| shell-and-cover | scripts/shell.gd, cover.gd | One hit per shell; cover 2 → cracked, 4 → broken | B16, B17 | Broken cover stops blocking: nowhere stays safe |
| game-loop | scripts/main.gd, scenes/main.tscn, project.godot | Arena/HUD built in code; failure/respawn; victory; pause; mute; health-bar colours | B20–B26 | Code-built scene: the saved .tscn shows one node |
| audio | scripts/audio.gd, assets/audio/**, tools/process_sfx.py, make_loop.py, analyze_sfx.py | Separate Music/SFX buses; request counter; loop cut at 8 bars | B17, B21, B24, B30 | Cannon and explosion both low-frequency |
| tests-and-playtest | tests/test_sound_triggers.gd, TEST-REPORT, design/test/*, gallery scene | Counts sound requests per event; human playtests | B27–B29 | Counts requests, not audible sound; calls handlers directly |
| provenance | ASSET-LOG, SOURCES, FRICTIONAL | Prompts, seeds, licences, decisions | B30–B32 | Environment rows missing |

Input → state → output trace shown in full: enemy shell → `take_damage()` → health 50 % → `_update_damage_look()` smoke
on → `damaged` signal → `_update_hud()` bar yellow → `SFX-player-hit` request (B18–B19, B25–B26).
Runtime tree: all game nodes are created in `_ready()` by main.gd; the saved `main.tscn` has one node, so no Scene-dock
tree was drawn (it would show only "Main").
