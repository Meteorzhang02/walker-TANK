# Character sheet — YunqiZ

- **Concept in one sentence:** YunqiZ is a worn, heavy olive-drab tank with a front dozer blade, a rear storage box, and a white identification stripe and number, built to read as solid, battered steel on a grim battlefield.
- **Main controllable object:** the player's tank (hull + independently rotating turret).
- **View:** oblique top-down (slight 3D depth).
- **Planned on-screen size:** about 64 px across the hull in a 1920×1080 viewport (to be confirmed by the silhouette test).

## Silhouette test

- File: `design/character/silhouette.png`
- The tank filled solid black at its actual on-screen size, in all five generated directions, placed on a mid-grey background.
- Pass condition: the direction the hull faces and the direction the barrel points can both be read at game size.
- **First result:** with a plain box hull, the up and down facings were almost identical at 64 px; only the short visible piece of barrel told them apart.
- **Revision:** added a wide **front dozer blade** and a narrower **rear storage box** that hangs off the back. In the redrawn silhouette the wide bar sits at the front and the narrower block at the rear, so up and down can be told apart without relying on the barrel.

## Facing / orientation

- **8 directions** for both hull and turret: up, up-right, right, down-right, down, down-left, left, up-left.
- **Generated (5):** up, up-right, right, down-right, down.
- **Mirrored at runtime (3):** up-left, left, down-left (horizontal flip of the matching right-side image).
- Up and down are never mirrored, because the oblique view shows different surfaces from above and below.
- The **hull** follows movement input; the **turret** follows the aim input independently.
- **Front and rear markers:** the dozer blade is always at the front of the hull and is wider than the hull; the storage box is always at the rear and narrower than the hull. These two shapes are what tell the player which way the hull faces.
- Note: because the identification number is mirrored on flipped directions, the number is drawn on a symmetric white stripe or kept on a surface that does not show on the mirrored side, so flipped frames do not show reversed digits. (To verify during generation.)

## Layering strategy

To keep frames consistent and the number of generations manageable:

- Hull and turret are generated as **separate sprites**, five directions each.
- Damage states and effects (smoke, fire, muzzle flash, hit flash) are **separate overlay sprites** drawn on top of the base tank, so the tank's shape and colors never change between states.
- The **victory** and **destroyed** poses are made in **one direction only**, because the player is not steering at those moments.

## Reference

- File: `design/character/turnaround.png`
- The five generated directions side by side at the same height, with a height bar.
- Every later pose and frame is checked against this reference.

## Poses (11)

| # | Pose | Game state it serves | Loop / single | Directions |
|---|---|---|---|---|
| 1 | Turnaround reference | Locks proportions for all other poses | — | 5 generated |
| 2 | Silhouette at game size | Proves the shape reads before detail | — | 5 generated |
| 3 | Idle (engine idle, slight shake) | No movement input | Loop | All 8 (base sprite) |
| 4 | Moving (tracks rolling) | Movement input held | Loop | All 8 |
| 5 | Firing (muzzle flash) | Fire pressed | Single | Overlay, follows turret |
| 6 | Recoil (hull jolts back) | Right after firing | Single | All 8 |
| 7 | Hit (brief flash) | Tank takes damage | Single | Overlay |
| 8 | Light damage (smoking) | Health at medium level | Loop | Overlay |
| 9 | Heavy damage (burning) | Health at low level | Loop | Overlay |
| 10 | Destroyed (wreck after explosion) | Health reaches zero (failure) | Single | 1 direction |
| 11 | Victory (hatch open, flag raised) | All enemies destroyed (completion) | Single, then hold | 1 direction |

Poses 8 and 9 serve the pillar **"Damage is information"**: the player can read remaining health from the tank's appearance, even with sound muted.

## Collision overlay

- File: `design/character/collision.png`
- **Planned shape:** a circle centered on the hull, with a radius of about half the hull width, drawn over each pose at the same scale.
- **Why a circle:** the hull turns in 8 directions, and a circle stays the same in every direction, so the collision never jumps when the tank turns.
- **Art beyond the shape:** the front and rear corners of the hull, the dozer blade, the storage box and the barrel extend past the circle. Shots that only touch the barrel or a corner do not count as hits. This is fair because it slightly favors the player rather than punishing them for art they cannot see as solid, and enemy tanks use the same rule.

## Palette

| Role | Hex |
|---|---|
| Main paint (olive drab) | `#4B5320` |
| Dark steel / shadow | `#2F3234` |
| Worn edge / bare steel | `#7D8084` |
| Tracks / deepest shadow | `#1E1F1F` |
| Identification stripe and number (off-white) | `#E8E6DF` |

- **Checked against the environment:** to be checked once the environment palette (mud, broken brick) is set. The off-white stripe is the main contrast element and must stay visible on every background tile.

## Consistency rules

Every frame of YunqiZ must keep the following identical:

- Hull length-to-width proportions and turret size relative to the hull.
- The dozer blade's width (wider than the hull) and the storage box's size and position at the rear.
- Barrel length and the turret's pivot point.
- Position, width and shape of the white identification stripe and number.
- Outline weight and the light direction (diffuse light from the top-left).
- Palette: no new colors on the base tank; smoke, fire and flashes appear only in overlays.

## Authorship note

Claude proposed the pose list, the layering strategy, the circular collision shape, the palette hex values, the consistency rules and the planned on-screen size. I chose the tank's name, 8 directions, the independently rotating turret, the white identification stripe and number, the front dozer blade and the rear storage box (after the first silhouette test showed up and down looked the same), and accepted the pose list.

The three planning images (`silhouette.png`, `turnaround.png`, `collision.png`) are rough code-drawn sketches made by Claude from a simple box model of the tank (`design/character/draw_sketches.py`). They are planning references only and are not generative-model assets.
