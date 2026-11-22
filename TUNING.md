# TUNING — Assignment 7

## Revision 1 — `track_dust` made readable: paler colour, 2x size (2026-11-21)

**What I saw (v1, in play at normal speed, before Claude read anything):** the track dust is not obvious. My first quick answer was that it was visible; looking again while driving, I can barely see it. The arena ground is brown cobble, and the dust is a brown between mud and brick, so it blends in. It is also small: a 16 x 16 cell against a hull about 50 px wide at game size. This is brief prediction 2 (dust disappears on the ground), and it happened on the ordinary ground, not only on the lightest stretch.

**Change:**
- `tools/make_dust_sheet.gd`: colour `Color(0.48, 0.42, 0.34)` → `Color(0.86, 0.80, 0.66)` (pale sand), peak alpha 0.85 → 1.0. Same cells, same grid, same frame order, same 10 fps.
- `scripts/tank.gd` `_ready()`: `Dust.scale = Vector2(2, 2)`, set once at creation. It is not animated, so `MotionAnim` stays the only writer of `Dust.frame`.

**Prediction, written before the change:** in the dust strip (frames 70–75 of the capture, while driving right) the puffs stand out from the cobble as light patches about twice as large as in v1; in play I can see them at normal speed. Timing, loop and seam do not change, so every test passes unchanged (the read-back checks keys, grid and slicing, not colour or scale).

**The shot:** on a second, careful look at strip v1 the squash on N+1 reads clearly, so `shoot` is not changed.

**Result:** <after v2>
