# TUNING — Assignment 7

## Revision 1 — `track_dust` made readable: paler colour, 2x size (2026-11-21)

**What I saw (v1, in play at normal speed, before Claude read anything):** the track dust is not obvious. My first quick answer was that it was visible; looking again while driving, I can barely see it. The arena ground is brown cobble, and the dust is a brown between mud and brick, so it blends in. It is also small: a 16 x 16 cell against a hull about 50 px wide at game size. This is brief prediction 2 (dust disappears on the ground), and it happened on the ordinary ground, not only on the lightest stretch.

**Change:**
- `tools/make_dust_sheet.gd`: colour `Color(0.48, 0.42, 0.34)` → `Color(0.86, 0.80, 0.66)` (pale sand), peak alpha 0.85 → 1.0. Same cells, same grid, same frame order, same 10 fps.
- `scripts/tank.gd` `_ready()`: `Dust.scale = Vector2(2, 2)`, set once at creation. It is not animated, so `MotionAnim` stays the only writer of `Dust.frame`.

**Prediction, written before the change:** in the dust strip (frames 70–75 of the capture, while driving right) the puffs stand out from the cobble as light patches about twice as large as in v1; in play I can see them at normal speed. Timing, loop and seam do not change, so every test passes unchanged (the read-back checks keys, grid and slicing, not colour or scale).

**The shot:** on a second, careful look at strip v1 the squash on N+1 reads clearly, so `shoot` is not changed.

**Result (v2, `captures/dust_strip_v2.png`):** my look: not very obvious, but I think I can see it. Claude then measured the strip: no pale-sand pixel in any of the 6 frames (only a few hull highlights), while the ground moves between frames, so the tank is driving and the clip is playing. The colour and size change did not fix it. Revision 2 tests why.

## Revision 2 — `track_dust` moved out from under the hull (2026-11-21)

**Cause, from the v2 measurement:** `DUST_BEHIND` is 14 px (the agent's guess, marked as a human check). The hull is about 50 px long at game size, so its rear is about 25 px behind the centre. `DustMount` is drawn before `Suspension`, under the hull, so dust centred 14 px back sits entirely under the hull.

**Change:** `scripts/tank.gd` `DUST_BEHIND` 14.0 → 34.0, so the dust's centre is about 9 px behind the rear of the hull and its front edge tucks just under the tracks. Colour and size stay as revision 1.

**Prediction, written before the change:** pale puffs appear just behind the rear of the hull in every frame of the dust strip (left of the hull while driving right), and in play I can see the dust at normal speed. Every test passes unchanged.

**Result (v3, `captures/dust_strip_v3.png`):** my look: much more obvious; pale puffs sit just behind the rear of the hull in all 6 frames and change from frame to frame, and in play I can see the dust at normal speed. As predicted. I then drove in all 8 facings (right, left, up, down and the four diagonals): the dust is behind the rear of the hull in every one. All tests unchanged: readback 49/0, anim_states 34/0, pins 11/0.
