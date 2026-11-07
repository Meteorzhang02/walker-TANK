# TUNING — Assignment 6

All strips are **fixture captures**. Each is a preview scene rendered by Movie Maker at 30 fps, with a fixed seed set on the preview's own instance only. Setup: Godot 4.7.2, Forward+, NVIDIA GeForce RTX 3060 Laptop GPU, 1280 × 720.

Each revision below records five things:
- what I saw in the running game;
- Claude's reading of the strip before the change;
- the change itself, which I approved;
- Claude's prediction for the new strip, and its comparison of the new strip with that prediction;
- my verdict in the running game.

## 2026-11-06 — Effect A, r0 (first strip, before any tuning)

**Strip:** `captures/cover_hit_burst/r0/` — frames 10, 12, 15, 20, 30, 50 (fixture).

**Capture log:** `logs/capture_cover_hit_burst_r0.log`. It shows the device NVIDIA RTX 3060 Laptop, and one burst at frame 10 at (600.7, 349.15), rotation −π (pointing back out of the left face).

**My first look** (preview window, 1280 × 720, before any Claude read the strip), in my own words:

> 闪光看得见，正好。砖块主要往左侧飞，也不错。看得清，大小合适。大概一两秒没有了。

(English: The flash is visible and about right. The chips fly mainly to the left, which is good. It is readable and the size is right. It is gone after about one or two seconds.)

**My second look** (preview window, after viewing my own strip, before any Claude reading):

> 看得清。

(English: The chips are readable against the ground.)

Checked against the strip: the burst is gone by frame 50 (1.33 s) and only faint dust is left at frame 30 (0.67 s), so my "one or two seconds" overestimated the duration (brief R2.4).

**In the running game** (main scene, 1280 × 720, NVIDIA RTX 3060, 2026-11-06; Effect A wired in at d2d50fc). I played for a few minutes and shot at cover.

- **Four hits on one wall until it broke** — checked. Every hit was visible.
- **Firing while moving** — checked. The chips read against the ground.
- **Chips go back toward the shooter** — not checked separately.
- **Pause right after a hit** — not checked here (to be checked with Effect B's edge checks).
- **My verdict:**

  > 游戏一切都正常。真的没有想改的地方。

  (English: Everything works in the game. There is nothing I want changed.)

So **no revision of Effect A is driven by something I observed in the running game**. The revision below (r1) comes from Claude's reading of the r0 strip. My verdict in the running game decides whether it is kept or rejected.

## 2026-11-06 — Effect A, r1 (Debris color_ramp; brief R3) — kept

**Driven by:** Claude's reading of the r0 strip, not by something I saw in the running game. In the game I found nothing I wanted changed (r0, above).

**Claude's reading of r0** (session 4a, read-only). Its crop-and-enlarge script was denied, so every size and colour below is an estimate by eye.
- Frames 10–15 match the intent.
- At frame 20 (0.33 s) the chips have almost vanished. The last ramp stop, #5A3A2E, has about the same value as the ground, and the fade starts at 0.3 of life, inside the outward phase.
- It named this the difference that matters most: the chips are the only layer that shows the wall losing material, and in which direction.

**Change** (proposed by Claude, approved by me; brief R3; session 4b). Debris `color_ramp`:
- from `#E8D8B0 a1 @0 → #B5523A a1 @0.3 → #5A3A2E a0 @1`
- to `#E8D8B0 a1 @0 → #B5523A a1 @0.3 → #8E5040 a1 @0.6 → #8E5040 a0 @1`

One setting; the particle count and the cost are unchanged. Config test 128/128 and state test 82/82, both rerun by me.

**Claude's prediction:**
- frames 10, 12, 15, 30 and 50 unchanged;
- frame 20: about 20 opaque red-brown chips, 50–60 px out.

**r1 strip:** `captures/cover_hit_burst/r1/` (fixture, same seed and frames as r0).

**Claude's comparison** (session 4c):
- Held for frames 10, 12, 15, 30 and 50.
- Partly held at frame 20. The chips are now visible, red-brown and smaller, but fainter and sparser than predicted (it was sure of 10–15, not 20).
- They reach about 80 px, not 50–60. Those far chips were already there in r0 but invisible, so its r0 reach of about 50 px was a limit of visibility, not of travel.
- Frame 20 now matches the brief's frame-20 row on everything a still frame can show, but weakly.
- It named chip size as the next lever (the Debris `scale_amount_curve` end, 0.4).

**My check of r1 frame 20:** small red-brown chips are visible to the left of the wall, faint, where r0 showed almost nothing.

**My verdict in the running game:**

> 保留就行，一切正常。因为不是纯 3D 游戏，目前状态不用纠结。

(English: Keep it; everything works. This isn't a full 3D game, so the current state doesn't need more fussing.)

**Decision:** r1 is kept and R3 stands. I chose not to take the next lever (chip size).

## 2026-11-06 — Effect B, r0 (first strip, before any tuning)

**Strip:** `captures/damage_smoke/r0/` — frames 10, 25, 58, 90, 112, 140, 165 (fixture).
- The preview drives `follow()`: h = 0.5 at frame 10, h = 0.1 at frame 60 (ratio 0.875), h = 1.0 at frame 110.
- Capture log: `logs/capture_damage_smoke_r0.log`.

**My first look** (preview window, 1280 × 720, before any Claude read the strip), in my own words:

> 变浓了，是从炮塔冒出来的，看得清，大小可以，慢慢散。

(English: It gets denser, it comes out of the turret, it reads clearly, the size is fine, and it disperses slowly.)

These are four of the brief's checks, each judged by eye in the preview:
- **Density step** (rules 1–2): denser after h drops to 0.1.
- **Origin** (`TURRET_OFFSET`): it comes out of the turret.
- **Contrast and scale:** it reads clearly, and the size is fine.
- **Stop:** it is not cut off; the column disperses slowly.

**Effect B in the running game** (main scene, 1280 × 720; Godot's startup line: "Using Device #0: NVIDIA - NVIDIA GeForce RTX 3060 Laptop GPU"; 2026-11-06, Effect B wired in at 7009248). I took hits until I was smoking, then checked each item. My answers, one word each, as I gave them:

| Check | My answer | What it shows |
|---|---|---|
| 1. Scene load: is any tank smoking? | 没有冒烟 (no smoke) | rule 7 |
| 2. Standing still: a rising column or a lump on the turret? | **一团 (a lump)** | **differs from the intent: a column about 2–3 hull lengths tall** |
| 3. Another hit, down to 25: denser? | 有 (yes) | rules 1–2 |
| 4. Driving while smoking: a trail behind? | 拖烟条 (it leaves a trail of smoke) | `local_coords` false |
| 5. Driving to the screen edge: does the smoke vanish all at once? | 不会 (no) | `visibility_rect` is large enough |
| 6. Pause while smoking (and Effect A's chips right after a hit) | 对 (yes) | rule 5 for B. My one-word answer covers both parts of the question. |
| 7. A destroyed enemy: does the wreck keep smoking? | 会 (yes) | rule 4 |

**Observation that drives Effect B's tuning (from check 2):** standing still, the smoke sits on the turret as a lump instead of rising into a column. My preview look said "大小可以" (the size is fine). In the running game I saw that it does not rise.

## 2026-11-06 — Effect B, r1 (initial velocity 20/40 → 50/80; brief R5) — kept

**Driven by:** what I saw in the running game. Standing still, the smoke sat on the turret as a lump instead of rising into a column (check 2, above).

**Claude's reading of r0** (session 7a, read-only, estimates by eye):
- Frames 10, 90, 112 and 165 match the brief.
- Frames 25, 58 and 140 show a round haze about 30 px across on the turret, not a column, and at 140 it has not detached.
- Its kinematics from the brief's own values: a mean puff rises only about 59 px over 1.6 s, and only the first ~35 px are visible, because alpha falls from 0.15 of life and the puffs grow faster than they rise. So my intent and my settings disagreed.
- It also found that the base colour #4A4A48 has about the ground's value (R2.2).

**Change** (proposed by Claude, approved by me; brief R5; session 7b). `initial_velocity_min / max` changed from 20 / 40 to 50 / 80 px/s. One setting; particle count, lifetime and cost unchanged. Config 76/76 and state 81/81, rerun by me with exit 0 (the agent could not see the exit codes again).

**Claude's prediction:**
- a thin column up to about y ≈ 270–290 at frame 58;
- detached from the tank at frame 140;
- two named risks: a cone instead of a column, and turbulence scrambling the rise.

**r1 strip:** `captures/damage_smoke/r1/` (fixture, same seed and frames).

**Claude's comparison** (session 7c):
- **Prediction failed** for frames 25, 58, 140 and the length at 90. The stills still show a lump reaching about 30–35 px, only 5–10 px more than r0.
- Held for 10, 112 and 165, the density step, and no gap after frame 60.
- The cone did not happen.
- Turbulence is now its leading explanation, but unconfirmed: each step pulls velocity 10–20 % toward the noise direction, and `noise_scale` 4.0 is fine. It proposed a check strip with turbulence off on the preview only.
- It also said the R5 change was still uncommitted. That was wrong: I had committed it (96d38be) between sessions, and it did not check.

**Second reading, of r1 frames 58 and 140** (Claude in chat, from the frames I uploaded): the smoke sits a little higher above the turret than in r0, but is still compact in a still frame.

**My verdict in the running game:**

> 是柱子，保留，往上升，比直直的一个柱子更好。

(English: It is a column now; keep it. It rises, and a wavering column is better than a dead-straight one.)

**The strip and my eyes disagree.**
- The fixture is a standing tank with a fixed seed, read one still frame at a time, where the rise does not show.
- In the moving game I see the smoke rise.
- By the assignment's rule, Claude's description of a frame is a claim, and my own look decides.
- The turbulence hypothesis was not tested; it stays open in TEST-REPORT.

**Decision:** r1 is kept and R5 stands.
