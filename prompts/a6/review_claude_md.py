# Applies my review edits to CLAUDE.md (Assignment 6, Step 1 review).
# Each edit finds exactly one line by its start; it stops with an error if a line is missing or repeated.
import sys

p = "CLAUDE.md"
L = open(p, encoding="utf-8").read().split("\n")


def idx(prefix):
    hits = [i for i, l in enumerate(L) if l.startswith(prefix)]
    if len(hits) != 1:
        sys.exit("STOP: %r found %d times" % (prefix, len(hits)))
    return hits[0]


i = idx("- Not sure for 4.7.2")
L[i:i + 1] = [
    "- Checked in this build by `tests/probe_particle_props.gd` (`logs/probe_particle_props_60fps.log`, 2026-11-06):",
    "  `CPUParticles2D` has `use_fixed_seed`, `seed`, the `finished` signal, the `_min`/`_max` pairs and `scale_amount_curve`,",
    "  and has **no** `amount_ratio`, `initial_velocity`, `scale_amount` or `scale_amount_random`.",
    "  `GPUParticles2D` has `amount_ratio`, `use_fixed_seed`, `seed`, `visibility_rect`, `preprocess` and `finished`.",
    "  `ParticleProcessMaterial` has the brief's `turbulence_*` names, `scale_min`/`max`, `scale_curve`, `angle_min` and",
    "  `particle_flag_disable_z`. The class `ParticlesMaterial` does not exist.",
    "- Trap: `ParticleProcessMaterial` *does* list a property called `initial_velocity` beside `initial_velocity_min`/`max`,",
    "  so a Godot 3 name there may not be rejected. Always set and read back the `_min`/`_max` pair.",
    "- Still unchecked: the unit of `angle_min`/`max` (degrees assumed) and 2D sphere emission on `ParticleProcessMaterial`;",
    "  the config test and the frame strip check them.",
]

removed = [
    "- `tests/test_sound_triggers.gd` line 94",
    "- The brief says `spawn_fx`",
    "- Brief line numbers checked",
    "- `scenes/gallery.tscn` will also",
    "- The property names and availability",
]
first = idx(removed[0])
for pre in removed:
    del L[idx(pre)]
L.insert(first, "- Resolved in `CHANGE-BRIEF.md` revision R1 (2026-11-06): the shell-less `take_hit()` in "
                "`test_sound_triggers.gd` line 94 (fallback position and rotation), the debris gravity (0, 160) at "
                "`main.gd` line 191, the two line references, and the gallery smoke. Property names: see *Godot 4 names*.")

i = idx("- Headless does report shader parse errors")
L[i + 1:i + 1] = [
    "- A headless run uses a dummy renderer: it draws no particles and runs no GPU particle process. Node state",
    "  (emitting, one_shot, amount_ratio, visibility, instance counts) is observable; the look is not.",
    "- A GPU effect's headless CPU price is near zero by construction.",
    "- Frame strips come from a windowed Movie Maker run, which I start.",
]

open(p, "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("CLAUDE.md now %d lines" % len(L))
