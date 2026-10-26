# CHANGE-BRIEF — Assignment 3: three 3D assets for walker-TANK

Written and committed **before** any asset was built. This original is kept as written; later changes go in the *Revisions* section at the end, never by editing the predictions above it.

## Context

walker-TANK is a 2D, oblique top-down tank game on a ruined brick battlefield (see CONCEPT.md). The game itself stays 2D for now. This assignment adds a small Godot 3D scene, `scenes/asset_room_3d.tscn`, with a floor, one light, a camera and the three assets side by side at game scale. Assignments 4 and 5 reuse it.

**Scale reference.** All sizes are in metres (1 Blender unit = 1 m = 1 Godot 3D unit; no conversion). They are justified against YunqiZ, the player's tank, which I size as a medium tank: **hull 6.0 m long × 3.4 m wide × 1.6 m high, 2.4 m to the top of the turret**. The 3D scene includes a plain grey box of the hull size, labelled "scale reference, not an asset", so the three assets can be judged beside the tank.

**Common rules for all three.** Built in Blender from basic shapes only (cube, cylinder), at most six shapes, flat colour materials (Principled BSDF base colour only), no textures, no bevels, no modifiers left unapplied. Blender is Z-up. Each asset is built around the world origin, with its base on the floor (Z = 0), in its own `.blend` file, and exported as `.glb` with +Y Up on.

## Asset 1 — `cover_wall` (broken brick cover)

- **What it is in the game:** the destructible cover the player hides behind (pillar: *cover is not permanent*). In the 3D scene it is the intact stage.
- **Where it appears:** scattered across the battlefield between the player and the enemy tanks.
- **Size:** **4.0 m wide × 1.0 m deep × 1.8 m high.** Wider than the tank (3.4 m) so the whole hull can hide behind it head-on; taller than the hull (1.6 m) but lower than the turret top (2.4 m), so the turret can fire over it.
- **Origin:** centre of the underside, so it sits on the floor where it is placed.
- **Look:** one main brick block 4.0 × 1.0 × 1.5 m, with two smaller blocks of uneven size on top to make a broken, ragged top edge (highest point 1.8 m). 3 cubes. Main block brick red-brown `#8B4A3A`, top blocks darker `#6E3B2E`.
- **Budget:** **≤ 60 triangles** (3 cubes × 12 = 36 expected).

## Asset 2 — `ammo_crate` (shell pickup)

- **What it is in the game:** a pickup that refills the tank's shells (planned for a later assignment; it gives the player a reason to leave cover).
- **Where it appears:** in exposed spots between pieces of cover.
- **Size:** **1.2 m wide × 0.8 m deep × 0.7 m high.** About a third of the tank's width, small enough that the tank clearly drives over it to collect it, large enough to read from the top-down camera.
- **Origin:** centre of the underside.
- **Look:** body cube 1.2 × 0.8 × 0.6 m, a slightly larger lid 1.24 × 0.84 × 0.1 m on top, and a thin off-white stripe across the lid. 3 cubes. Body olive `#4B5320` (the tank's main colour, so it reads as "ours"), lid darker olive `#3D441A`, stripe off-white `#E8E6DF` (the tank's identification-stripe colour).
- **Budget:** **≤ 60 triangles** (36 expected).

## Asset 3 — `tank_hedgehog` (anti-tank obstacle)

- **What it is in the game:** a steel obstacle that blocks tank movement but, unlike cover, does not stop shells and never breaks. It forces route choices.
- **Where it appears:** in rows across roads and gaps between ruins.
- **Size:** **about 1.9 m wide × 1.9 m deep × 1.4 m high.** Lower than the tank hull, so it does not hide the tank, but clearly a barrier at hull scale.
- **Origin:** centre of the underside, at floor level, with the three lowest beam ends touching Z = 0.
- **Look:** three steel beams, 2.4 m long with a 0.15 × 0.15 m section, crossing at their centres at right angles to each other, tilted so the group stands on three beam ends (the classic "Czech hedgehog"). 3 cubes. Rusty dark steel `#5A4A3F`.
- **Budget:** **≤ 60 triangles** (36 expected).

## Why these triangle budgets

Every asset is made of cubes only, so 36 triangles each is enough. I set **60 per asset** (well under the course limit of 500) because the game is seen from a high top-down camera where extra geometry would not be visible, and because a low limit makes it obvious if Claude builds more than I asked for.

## Predicted failure cases and how I will check each

1. **An asset arrives lying on its side or upside down** (Blender is Z-up, Godot is Y-up). *Check:* the headless Godot script prints the bounding-box size; the height must be on the Y axis and match the brief. I also look at it in the 3D scene.
2. **Scale or rotation not applied, so the Godot node scale is not 1, 1, 1 or the asset is 10× or 0.1× too large.** The hedgehog is most at risk because its beams are rotated. *Check:* in Blender the sidebar (N) must show scale 1, 1, 1 and rotation 0, 0, 0 after applying; in Godot the check script prints the node scale and the bounding box, which must be within ±0.1 m of the brief (±0.15 m for the hedgehog).
3. **Origin in the middle of the object, so it floats or sinks.** *Check:* the check script prints the lowest Y of the bounding box, which must be 0.00 (±0.01); I place each asset on the floor in the scene and look at it from the side.
4. **Claude builds more than asked** (bevels, extra parts, high segment counts). *Check:* Blender's Scene Statistics must show ≤ 60 triangles per asset and no more than the listed number of objects.
5. **A colour does not survive the export** (asset appears white or grey in Godot). *Check:* compare each part's colour in Godot with the hex values above.
6. **The MCP server will not connect on Windows.** *Check:* `get_scene_info` must return the scene. If it does not connect within the two-hour time box, I will log every step and error in FRICTIONAL.md and use the script route.

## Revisions

*(none yet — later corrections are added here with the date and the evidence that caused them)*

### 2026-10-15 — Asset 3 `tank_hedgehog`: beam length 2.4 m → 2.125 m

- **Change:** each of the three beams is **2.125 m** long instead of 2.4 m. Section (0.15 × 0.15 m), count (3), arrangement (mutually perpendicular, crossing at their centres, standing on three beam ends, plain orientation with each beam's section aligned to the other two beams), colour and budget are unchanged.
- **Evidence:** computed before building. With 2.4 m beams in that arrangement, rotated so the group stands on three ends and yawed so the footprint is square, the bounding box is **2.011 × 2.011 × 1.559 m**. The height is 0.159 m over the brief's 1.4 m, **0.009 m outside the ±0.15 m tolerance**. The original numbers used the beam centrelines (end-centre height 2.4/√3 = 1.386 m) and left out the 0.15 m section, which adds about 0.17 m of height. With 2.125 m beams the bounding box is **1.794 × 1.794 × 1.400 m** (height = (L + 0.3)/√3).
- **Unchanged:** the overall size target, **about 1.9 × 1.9 × 1.4 m (±0.15 m)**, stays as written above. The game design depends on it (lower than the 1.6 m hull, clearly a barrier at hull scale); the beam length was only a construction detail.

## Authorship note

I asked Claude to propose three assets that fit walker-TANK and to draft this brief. Claude proposed the three assets, the tank reference size, the dimensions, colours, budgets and failure cases. I chose to use these three assets after looking at Blender's window, and accepted the numbers. Colours reuse the palette from my Assignment 2 character sheet.
