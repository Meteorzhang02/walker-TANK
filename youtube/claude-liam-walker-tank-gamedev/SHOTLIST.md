# SHOTLIST — claude-liam-walker-tank-gamedev

"run-01 a–b s" = real interval of the native 4K take, never retimed. Code beats are Godot editor reconstructions
of verbatim excerpts; each is followed by its visible result.

| Beat | Act | Visual | Audio |
|---|---|---|---|
| B00 | Ask | ClaudeComposerAsk, reconstructed Walker prompt (labeled) | Liam |
| B01 | BLUF | BrutalistHesitantWriter: "finished" → "started" | Liam (0.8 s lead) |
| B02 | Setup | Brief's minimum table, verbatim + setup cards | Liam |
| B03 | Concept | PREVIEW run-01 27.7–42.7 s | Liam over ducked game audio |
| B04 | Pillars | PREVIEW montage: 0–5.6, 14.7–17.1, 37.3–40.5, 40.8–44.2 s, pillar names verbatim | Liam over game audio |
| B05 | Sheet | silhouette.png | Liam |
| B06 | Generate | v1 guide + REJ-01/02/03 | Liam |
| B07 → B08 | Code → result | draw_guides_v2.py 14–20 → v1 vs v2 guide | Liam |
| B09 | Raw | v2 guide → raw SDXL output + metadata + prompt | Liam |
| B10 → B11 | Code → result | cutout_hull.py 18–23 → check_hull_v2.png | Liam |
| B12 → B13 | Code → result | process_sprites.py 30–37 → check_final_8dir.png | Liam |
| B14 → B15 | Code → result | tank.gd 123–131 → run-01 0–13 s (idle, 8 facings) | Liam + game |
| B16 → B17 | Code → result | cover.gd 33–45 → run-01 13–18 s (crack, break) | Liam + game |
| B18 → B19 | Code → result | tank.gd 195–198 → run-01 30–43 s (smoke, flames) | Liam + game |
| B20 → B21 | Code → result | main.gd 257–268 → run-01 18–30 s (death, respawn, pause) | Liam + game |
| B22 → B23 | Code → result | main.gd 271–280 → run-01 43–47.3 s (second death) | Liam + game |
| B24 | Game audio | run-01 47.3–55.6 s, last kill + victory, labeled GAME AUDIO ONLY | game audio only |
| B25 → B26 | Code → result | main.gd 373–379 → before/after health bar | Liam |
| B27 → B28 | Code → result | test_sound_triggers.gd 39–49 → recorded test output | Liam |
| B29 | Limits | play-05-muted.png | Liam |
| B30 | Models | real assets by model | Liam |
| B31 | Who | accepted 0.60 vs rejected 0.75 turret | Liam |
| B32 | Uncertain | logs vs files | Liam |
| B33 | Verdict | ClaudeVerdictArtifact | Liam |
| B34 | Your Turn | ClaudeComposerAsk, prompt read aloud | Liam (signs off) |
| B35 | Outro | ClaudeTitleOutro, spoken title + "At Nik Bear Brown", 1 s silent tail | Liam only, no jingle |

Every gameplay frame carries the corner label "SCRIPTED INPUT · NOT A HUMAN PLAYTEST · Godot 4.7.2 Movie Maker, native
3840x2160" and, for 1.2 s at each logged sound request, a "sound: SFX-…" tag (enemy shots/hits marked with their dB offset).
