# TEST-REPORT — Assignment 3: three 3D assets

The Assignment 2 report has moved, unchanged, to `docs/a2/TEST-REPORT.md`.

**Versions:** Blender 5.2.2 LTS · MCP for Blender add-on 1.8 (protocol 13) · Godot 4.7.2 · Claude Code 2.1.299 (Opus 5.5) · Windows 11, RTX 3060 laptop.

**How to re-run the checks (Windows, Git Bash, from the repo root):**

```bash
# Blender: rebuild each asset from scratch and check it (exit 0 = pass)
"/d/blender/blender.exe" -b --factory-startup --python-exit-code 1 --python tools/blender/build_cover_wall.py
# (same for build_ammo_crate.py and build_tank_hedgehog.py)

# Godot: import, then the headless asset check (exit 0 = all pass, 1 = any FAIL, 124 = time limit hit)
GODOT="/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe"
"$GODOT" --headless --path . --import
timeout 120 "$GODOT" --headless --path . --script res://tests/check_a3_assets.gd --fixed-fps 60
```

The course commands are written for macOS. On Windows I use Git Bash's GNU `timeout` (coreutils 8.32), because Windows' own `timeout.exe` only waits and does not stop a program; and `--path .` because my Godot project is the repo root, not a `godot/` folder.

## Results

All sizes in metres. Blender is Z-up, Godot is Y-up, so a Blender (x, y, z) size appears in Godot as (x, z, y).

| Check | cover_wall | ammo_crate | tank_hedgehog |
|---|---|---|---|
| **Brief** (w × d × h) | 4.0 × 1.0 × 1.8 | 1.2 × 0.8 × 0.7 (±0.1) | about 1.9 × 1.9 × 1.4 (±0.15) |
| **Blender** (x × y × z; build-script check; my sidebar for cover_wall) | 4.0 × 1.0 × 1.8 | 1.24 × 0.84 × 0.71 | 1.794 × 1.794 × 1.400 |
| **Godot headless** (x × y × z) | 4.000032 × 1.8 × 1.0 | 1.24 × 0.71 × 0.84 | 1.794236 × 1.400074 × 1.794236 |
| Matches brief? | yes | yes, +0.04 / +0.04 / +0.01, inside ±0.1 | yes after the revision below; height exact |
| **Upright** (height on Godot Y) | PASS | PASS | PASS |
| **Root node scale** in Godot | 1, 1, 1 | 1, 1, 1 | 1, 1, 1 |
| **Lowest Y** in Godot (origin on floor) | 0.0000 | 0.0000 | 0.0000 (3 vertices at Blender Z = 0) |
| **Triangles** (budget 60) | 36 | 36 | 36 |
| **Background rebuild** in Blender | exit 0 | exit 0 | exit 0 |
| **Godot check** overall | 18 / 18 PASS, exit 0 | | |

Every number above comes from a script output I kept (Blender build-script runs, and `tests/check_a3_assets.gd`, commit `ee1c67a`).

## The check failing on purpose

A check that has never failed may be broken. Claude ran a scratch copy of `check_a3_assets.gd` whose only difference (confirmed with `diff`) was ammo_crate's expected height changed from 0.71 to 0.81. It printed two FAIL lines and `RESULT: FAIL (2 failure(s))` with **exit code 1**; the other 16 checks still passed. The real script and the assets were not changed.

## What the checks do and do not show

- **The Blender build scripts** show that each asset can be rebuilt from nothing with the stated size, origin, applied transforms, triangle count and material slot *names*. They do not check colour values, and they say nothing about the asset after export.
- **The tank_hedgehog script's "apply rotation" step tested nothing.** The beams' rotation was already baked into the mesh during the join, so the bake step found identity transforms (it printed `identity: True`). The result is correct, but that step never had a real rotation to apply.
- **The Godot check** measures each `.glb` on its own, instantiated at the origin: size, lowest Y, root scale and the height axis, to 0.01 m. It does **not** check the copies placed in `asset_room_3d.tscn`, whether they rest on the floor there, colours, lighting, shadows, or whether the shapes read as what they are. Headless Godot uses a dummy renderer, so none of that is visible to it.
- **Hidden faces:** each asset is made of overlapping boxes, so faces inside the asset (the crate lid's underside, the wall's block bottoms, the hedgehog's crossing) still count towards the 36 triangles. They are never visible, so I left them.

## Problems found and what I changed

1. **tank_hedgehog's brief was wrong (evidence-based revision).** I asked Claude to work out the bounding box *before* building. With the brief's 2.4 m beams it came to 2.011 × 2.011 × **1.559** m, 0.009 m over the height tolerance, because the brief's numbers used the beam centrelines and left out the 0.15 m section. Claude recommended turning each beam 45° to fit. I chose instead to shorten the beams to **2.125 m**, because the overall size is what the game design depends on (lower than the 1.6 m hull, a barrier at hull scale), while the beam length was only a construction detail and was the number that was wrong. Result: 1.794 × 1.794 × 1.400 m. The change is recorded under *Revisions* in `CHANGE-BRIEF.md`; the original text is unchanged.
2. **ammo_crate's brief size left out the lid.** The brief lists the body size, but the lid overhangs by 0.02 m on each side and the stripe adds 0.01 m, so the real box is 1.24 × 0.84 × 0.71 m. Inside the ±0.1 m tolerance, so I kept it; the build script checks both the exact size and the brief tolerance.
3. **ammo_crate z-fighting avoided.** Claude noticed before building that a stripe exactly as deep as the lid (0.84 m) would share the lid's front and back faces and could flicker. I accepted its suggestion to make the stripe 0.83 m deep. The overall size did not change.
4. **My hand edit on cover_wall was 0.7 mm short.** I moved block B +0.6 m in Edit Mode. My sidebar then showed 4 m wide and I thought it was flush. Claude's read-only background inspection showed it had moved 0.5993 m, 0.7 mm short: **the sidebar rounds, so it could not show that error.** My correction (G X 0.0007, computed from a 4-decimal printout that was itself rounded) overshot by 0.032 mm. That is inside the build check's 0.1 mm tolerance and far below anything visible, so I stopped there. Lesson: to place something exactly, type the coordinate into the sidebar instead of nudging with G; and decide the tolerance first, then stop when inside it.

## HUMAN CHECK: look

*My own observations in the Godot editor (`scenes/asset_room_3d.tscn`), with the grey 6.0 × 1.6 × 3.4 m box standing in for the YunqiZ hull. Screenshot: `design/godot/asset_room_3d.png`.*

- **From the top** (the game's camera direction): the ammo crate's off-white stripe is the most readable feature in the scene, which is what the brief wanted. The hedgehog reads as three crossing beams. The wall's shadow shows its broken top, higher on the left.
- **Floor contact:** every asset casts a shadow that meets its base; none of them floats. (This is the check the headless script cannot do for the scene copies.)
- **Scale:** next to the hull box, the wall is wider than the hull is deep and lower than the turret would be, the crate is small enough to drive over, and the hedgehog is clearly lower than the hull. All three look in proportion.
- **From behind and below:** I switched the editor to the rear and bottom views for each asset. I saw no missing faces and no wrong colours; I found no problems to fix.
- **Not resolved:** with one light and no ambient fill, faces turned away from the light are very dark. The brief asked for one light; whether the game's real lighting suits these colours is not tested here.

## Brief failure cases, predicted vs. what happened

| # | Predicted | What happened |
|---|---|---|
| 1 | Lying on its side (Z-up vs Y-up) | Did not happen; height is on Godot Y for all three |
| 2 | Scale or rotation not applied | Did not happen; scale 1, 1, 1 in Blender and Godot. Building from mesh data meant scale was never non-1 |
| 3 | Origin in the middle, floats or sinks | Did not happen; lowest Y 0.0000 in Godot |
| 4 | Claude builds more than asked | Did not happen; 36 triangles each, 3 boxes each |
| 5 | Colours lost on export | Did not happen; colours visible in the Godot screenshot (checked by eye, not measured) |
| 6 | MCP will not connect on Windows | Connected, after one failed command (see FRICTIONAL.md) |

Not predicted: the hedgehog's brief size being wrong, the crate's lid overhang, and a Blender error (`AttributeError ... 'select_set'`) during cover_wall's join.
