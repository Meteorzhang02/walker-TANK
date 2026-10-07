# TEST-REPORT — walker-TANK

- **Source revision tested:** `4616fc7` (the same game source as the film)
- **Engine:** Godot v4.7.2.stable.official (ed1daf0bf), Windows
- **Tester:** me (Yunqi Zhang). No other playtesters; none are claimed.
- **Screenshots:** `design/test/`

## Results

| Check | Result | Evidence |
|---|---|---|
| Startup and controls | Runs from the editor (F5). Movement (WASD / arrows), mouse aim, fire (LMB / Space), pause (Esc / P), music mute (M), sound mute (N) and restart after victory (R) all work. **Fresh copy:** cloned `4616fc7` from GitHub into a new folder, imported it in Godot 4.7.2 and ran it: the game started and every sprite, sound and music file was present. | `play-01` to `play-05` |
| Character against the sheet | See the section below. | `gallery-yunqiz.png`, `design/asset-log/check_final_8dir.png` |
| Storyboard against the slice | Panels 2–8 covered; panel 1 not built. See the section below. | `play-01` to `play-05`, `play-06` |
| Sound events | With sound on, fire, cover hit, YunqiZ hit, explosion and victory each played once per occurrence, including holding fire and rapid presses (holding fire repeats at the 0.8 s reload rate, one sound per shell). Also covered by the automated check. | own playtest; `automated-test-result.png` |
| Music | The loop repeated without a click or gap. Pausing paused it and resuming continued from the same point; being destroyed cut it to silence (explosion tail only); respawning restarted it; victory stopped it before the victory sound. Behaves as CHANGE-BRIEF predicted. I also played full rounds with the music on and did not hear a click at the loop point. | own playtest |
| Muted play | With music and sound both off (M, N), a full round was playable and readable: muzzle flash and shell trails show firing, debris and the cover's cracked and broken stages show cover hits, the hit flash, health bar, smoke and fire show damage, the explosion and wreck show destruction, and the victory panel shows the end. | `play-05-muted.png` |
| Automated check | 8 / 8 pass (below). | `automated-test-result.png` |

## Automated check

`tests/test_sound_triggers.gd` drives the real game scene and counts how many times each event asks for a sound.

```bash
godot --headless --path . -s res://tests/test_sound_triggers.gd
```

(On my machine: `"/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe"` in place of `godot`; open the project in the editor once first so the assets are imported.)

Result:

```
PASS  10 fire presses in one frame -> 1 shell, 1 fire sound
PASS  fire again after reload -> 2nd fire sound
PASS  one shell touching cover twice -> 1 cover-hit sound
PASS  two shells in one frame -> 2 more cover-hit sounds, cover cracked
PASS  two hits within 0.3 s -> 1 hit sound, damage applied once
PASS  fatal hit -> 1 explosion, 0 hit sounds, dead
PASS  last enemy destroyed twice -> 1 victory sound
PASS  SFX muted -> enemy still damaged, cover still breaks
RESULT: 0 failed
```

Godot also prints ObjectDB leak warnings when the headless run exits. They come from quitting the engine, not from a failed check. Freeing the scene before quitting did not remove them; they are harmless and still printed. No assertion was removed or weakened.

## Character against the sheet

`design/test/gallery-yunqiz.png` (from `scenes/gallery.tscn`, F6). The first gallery screenshot (`gallery-yunqiz_v1-turret-bug.png`) showed every turret pointing the same way: the gallery used the player script, so the turrets followed the mouse. The gallery now uses the base tank script; the game itself was not affected. The gallery shows YunqiZ in all 8 facings at 2x game size, the idle, smoke, fire and destroyed states, the enemy tint, and the collision circle on each.

| Sheet pose | In the slice | Note |
|---|---|---|
| 1 Turnaround, 2 Silhouette | 5 generated facings + 3 mirrored, all present | Outlines match the guides (IoU 0.99 hull, 0.97–0.98 turret) |
| 3 Idle | Slight engine shake (code) | |
| 4 Moving | Track rumble wobble (code) | No separate track-rolling frames were generated |
| 5 Firing | Code muzzle flash | Not a generated overlay |
| 6 Recoil | Code offset of hull and turret | As planned |
| 7 Hit | Code white flash | As planned |
| 8 Light damage, 9 Heavy damage | Code smoke and fire particles at ≤60% and ≤30% health | Planned as generated overlays; made in code for time |
| 10 Destroyed | Darkened sprite + smoke | No separate generated wreck pose |
| 11 Victory | Not made | Victory screen uses the right-facing sprite instead |

**Collision:** the circle (r = 16.6 px) matches the plan; the dozer blade, storage box, hull corners and barrel extend past it, as the sheet says. **Known mismatch:** the up and right turrets have no cupola (see ASSET-LOG).

## Storyboard against the slice

| Panel | In-engine screenshot | Differences |
|---|---|---|
| 1 Opening top-down zoom | — | **Not built.** The slice starts in the gameplay view. |
| 2 Fire from cover | `play-01-normal-combat.png` (shells in flight) | Same oblique view, no zoom difference; muzzle flash is a code particle. |
| 3 Cover breaking | `play-02-cover-destroyed-victory.png` (broken covers with rubble) | Broken cover no longer blocks, as designed. |
| 4 Enemy destroyed | `play-02`, `play-03` (dark enemy wrecks) | No camera close-up; screen shake is used instead. Explosion is a code particle. |
| 5 Taking damage | `play-03-victory-player-burning.png` (YunqiZ burning) | Smoke and fire are code particles. |
| 6 Failure | `play-06-destroyed.png` ("YunqiZ destroyed - respawning", empty health bar, wreck) | No close-up; music cut to silence as planned. |
| 7 Respawn | `play-07-respawn.png` (back at the spawn point, full green health bar) | Wrecks stay on the map, as planned. |
| 8 Victory screen | `play-02`, `play-03` | No low-angle illustration (pose 11 not made); right-facing sprite instead. |
| (Pause) | `play-04-paused.png` | — |

**Enemy tanks:** the storyboard showed separate enemy designs; the slice uses the YunqiZ sprites tinted grey in code. In the screenshots the enemies still read close to YunqiZ's olive, and are told apart mainly by YunqiZ's white stripe and the grey cast. Logged as a known issue.

## Inspect-and-revise cycles

Each was driven by an observation and is recorded in ASSET-LOG.md or FRICTIONAL.md.

1. **Silhouette test → design change:** up and down facings looked the same at 64 px; added a front dozer blade and rear storage box, then redid the silhouette test.
2. **Flat guide → v2 guide:** img2img on the v1 box guide gave flat color blocks at 0.55 and 0.70 and lost the blade at 0.80; the guide was redrawn with gradients, grain and structure (v2), which gave realistic hulls at 0.55 with the shape kept.
3. **Square barrel → v3 guide:** the right turret came out with a square barrel and the down-right one with a round barrel; the turret guide was redrawn with a round barrel and muzzle.
4. **Cutout removed the blade:** the first cutout kept only the largest piece and dropped the separate dozer blade on the right hull; caught on the check sheet and fixed.
5. **Cannon sound → sampler settings:** the first `SFX-fire` was seven noisy bursts with clipping; the FLAC metadata showed the template's 50 steps / cfg 7.0 (meant for the Medium model); changed to 8 steps / cfg 1.0 and regenerated.
6. **Busy ground → calmed ground:** in the game-scale scene test the cover almost disappeared into the raw ground; the ground was blurred, lowered in contrast and darkened, and the test repeated (`check_scene_v1.png` → `check_scene_v2.png`).
7. **Gallery bug:** the first gallery screenshot showed all turrets aimed at the mouse; fixed in the gallery script and re-captured.
8. **Playtest → health bar:** in my screenshots the default grey health bar was hard to read on the dark ground; it now fills green / yellow / red by health.

## Code problems found while testing

- `enemy.gd` failed to parse in Godot 4.7 (type inference on an untyped target). Fixed by typing the variable.
- The first project copy was unzipped into a separate folder and Godot could not write to it; moved into the `walker-TANK` repository.

## My playtest notes and what is still uncertain

- No sound or music faults found with sound on; the slice was readable muted.
- **Turret turning** could feel more responsive, and **hull turning** more natural (it snaps between the 8 facings).
- **Enemy tanks** should look different from YunqiZ, not only tinted.
- **HUD text** (labels at the top and the control hint at the bottom) has fairly low contrast against the ground; readable, but a candidate fix. Found by the film's QC.
- The explainer film's gameplay is scripted input driven by the capture tool, labelled in the film as not a human playtest; my own playtest is the one described above.
- Not tested: other people playing; laptop speakers for the low-frequency cannon and explosion (ASSET-LOG known issue); difficulty balance.
