# COMPONENTS — claude-liam-walker-tank-a7-animation (walker-TANK 4f88f1b, A7 only)

| Component | Where it lives | Data in | Key lines | What changes | What the player sees | Beats |
|---|---|---|---|---|---|---|
| track_dust (cycle) | `animations/motion_clips.tres`, MotionAnim built in `tank.gd` 93–98 | `track_dust_sheet.png` 64×16, hframes 4 | tres 3–17; tank.gd 75–82, 189–202 | `Dust.frame` 0→3 every 0.1 s, looped, while MOVING | pale puffs just behind the hull while driving; gone when stopped | B02 B03 B07 |
| shoot (committing action) | `tools/bake_tank_clips.gd` → `animations/fire_clips.tres`, FireAnim (tank.gd 99–104) | phase table (brief 75–80) | bake 59–80; tres keys | `Suspension` position (0,2) and scale (1.04,0.96) on frame 1, rest by frame 5 | the tank sits down on the shot and springs back | B04 B05 B07 |
| One authority | brief 39–45; tank.gd 83–92, 180–181 | — | Suspension above hull/turret | each animated property has one writer | dip and wobble/recoil do not fight | B06 |
| Two clocks | tank.gd 96, 102, 207–219 | physics ticks | `_weapon_tick()` tick counter | shell P+2, clip frame 1 P+3 | shell leaves one tick before the dip shows | B08 B09 |
| State machine + interrupts | tank.gd 160–238 | input, take_damage | weapon tick before the `is_dead` return; FIRING guard line 229 | hits/deaths don't stop a committed shot; 2nd fire ignored | the shot always goes once pressed | B10 B11 |
| Tests and mutations | `tests/test_clip_readback.gd`, `test_anim_states.gd`, `test_anim_edges.gd`, `test_pins.gd`; `logs/` | — | C1 `absi(d)` (test_anim_states.gd 334) | — | (headless: nothing drawn) | B12 B13 |
| Readings and tuning | `TUNING.md`, `captures/*strip*` | strips | DUST_BEHIND 14 → 34 (tank.gd 24) | dust out from under the hull | dust visible in all 8 facings | B14 |

Trade-offs: a frame track on an AnimationPlayer so the read-back sees it (an AnimatedSprite2D would escape it), at the cost of a second player; a baked .tres instead of an imported rig — no importer can overwrite its loop mode (M7), but edits need a re-bake; the shell from a tick counter, not a method track — gameplay never waits on the clip, at the cost of a 1-tick visual lag.
