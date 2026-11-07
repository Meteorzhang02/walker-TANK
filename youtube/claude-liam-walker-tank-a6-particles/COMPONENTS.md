# COMPONENTS — what this film explains (walker-TANK A6, commit 41a6b8b)

Ledger: `gamedev-evidence.json` (7 components, 82 source files, 482 exclusions with reasons, 4 exact excerpts, 4 code→result pairs).

| Component | Files (main) | Beats | Mechanism | Design choice / trade-off |
|---|---|---|---|---|
| Effect A — cover hit burst | `effects/cover_hit_burst.tscn/.gd`, `scripts/cover.gd` l.40, `main.gd` `spawn_cover_burst()` | B02, B05–B08 | `take_hit()` → a new burst instance in `World/FX` at the shell's drawn contact point, rotated back out of the wall; Flash (ADD), Debris (24 chips, damping 400–600, gravity 0), Dust; root frees itself on Dust.finished | CPU node: no GPU-only feature needed, and it gets a non-zero headless price; overlap retrigger (new instance per hit) never restarts an earlier burst |
| Effect B — damage smoke | `effects/damage_smoke.tscn/.gd`, `scripts/tank.gd` | B02–B04, B09–B12 | `follow(h, dead)` sets only `emitting` and `amount_ratio` (0.25 + 0.75·(0.6−h)/0.6; wreck 1.0); `amount` stays 48 | GPU node for turbulence and `amount_ratio`; priced on GPU time because headless reads ≈ 0 |
| Textures | `effects/textures/*`, `tools/make_particle_textures.gd` | B03, B18 | 6 px chip and 32 px radial dot, drawn by code | no sourced or AI textures |
| Generated process shader | `shaders/particles_generated.gdshader`, `LANGUAGE-NOTES.md` | B03, B13, B14 | l.232 start speed mix(min,max); l.412/425 gravity into velocity; l.447 turbulence blends velocity 10–20 % toward noise each step | explains the lump; the game still uses the ParticleProcessMaterial |
| Tests | `tests/test_*_{config,state}.gd`, probe, logs | B12, B15 | read-back of every setting; real input through the real loop; two mutations | headless proves logic, never drawing |
| Prices | `tests/price_measure.gd`, `tests/cost_particles.gd`, `previews/price_scene.*`, price logs | B04, B16, B17 | medians per phase, empty control, two mode-0 runs as drift | FPS with vsync (and with vsync off, capped) hides the cost; GPU time shows it |
| Record | CHANGE-BRIEF (R1–R5), FRICTIONAL, SOURCES, README, CLAUDE.md, project.godot | B00, B18 | who caught what, who did what | — |

**Input → state → output trace (B02 → B08 → B15):** Space key → shell → `cover.gd take_hit()` passes `stage < 2` → line 40 `spawn_cover_burst(_shell, …)` → burst instance in `World/FX` at the contact point → three emitters fire → visible burst in the play recording; the state test checks the same chain headless (7 bursts = 7 cover hits = 7 sounds).
