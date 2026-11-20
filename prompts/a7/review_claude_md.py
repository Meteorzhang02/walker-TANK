# My review edits to the agent's CLAUDE.md draft (A7 Step 1). Each edit matches one line by its start.
p = "CLAUDE.md"
lines = open(p, encoding="utf-8", newline="").read().split("\n")

def find(prefix):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, f"{prefix!r}: {len(hits)} matches"
    return hits[0]

def replace(prefix, new):
    i = find(prefix); lines[i:i+1] = new; print("replaced:", prefix[:50])

def insert_after(prefix, new):
    i = find(prefix); lines[i+1:i+1] = new; print("inserted after:", prefix[:50])

# 1. Restore the Headless facts section.
replace("- Headless uses a dummy renderer", [
    "",
    "## Headless facts",
    "",
    "- A headless run uses a dummy renderer: it draws nothing. Tests prove node state, properties and timing, never what the screen shows. Every look is a human check recorded in `TEST-REPORT.md`.",
    "- Headless does report shader parse errors: a deleted semicolon in `shaders/hit_flash.gdshader` printed `SHADER ERROR` and exited 1 (`logs/mutation1_semicolon_60fps.log`).",
    "- Headless `realtime` runs are paced at about 1/144 s, so frame time prices nothing; GPU render time reads 0 headless (`tests/price_measure.gd`).",
])

# 2. track_problems() is a test helper, not an engine name.
replace("- Not checked in this build:", [
    "- `track_problems()` is a helper in `tests/test_clip_readback.gd`, taken from the assignment; it is not an engine name.",
    "- Not yet checked in this build: `AnimationPlayer.autoplay`, `AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS`, `Animation.step`, `value_track_set_update_mode()`. `tests/test_clip_readback.gd` reads each one back; until it passes, say so instead of guessing.",
])

# 3. A5/A6 code that touches the tank.
insert_after("- **Scenes the clips appear in:**", [
    "- **A5/A6 code on the tank:** `scripts/hit_flash_driver.gd` is attached to YunqiZ only (`main.gd` line 79) and drives the ShaderMaterial shared by `hull` and `turret`. `tank.gd` instances `effects/damage_smoke.tscn` as `smoke` (A6). `smoke` and `flames` stay direct children of the tank; only `hull` and `turret` move under `Suspension`.",
])

# 4. Baseline results for the two tests without counts.
replace("bash scripts/run-test.sh check_a3_assets.gd 60", ["bash scripts/run-test.sh check_a3_assets.gd 60                    # PASS (0 failures)"])
replace("bash scripts/run-test.sh test_sound_triggers.gd 60", ["bash scripts/run-test.sh test_sound_triggers.gd 60                 # RESULT: 0 failed"])

open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("CLAUDE.md now", len(lines), "lines")

# 5. Unconfirmed: resolve the smoke question, reword the weapon-tick note (second pass).
lines = open(p, encoding="utf-8", newline="").read().split("\n")
replace("- Whether `smoke` and `flames`", [])
replace("- The brief says the weapon tick runs", [
    "- The weapon tick that runs before the `is_dead` return (brief) does not exist yet; it is added in the wiring step. Today the return is at `tank.gd` lines 120–121.",
])
open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("CLAUDE.md now", len(lines), "lines")
