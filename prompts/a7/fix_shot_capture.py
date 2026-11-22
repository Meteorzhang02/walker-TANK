# A7 fix (mine, with Claude chat): capture the muzzle position and aim on the press tick, and emit
# `fired` with the shell on the active tick. Fixes test_hit_flash (AI re-aimed during startup) and
# test_cover_hit_burst_state (fired arrived 2 ticks before its shell). Matches lines by content.
p = "scripts/tank.gd"
src = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in src else "\n"
lines = src.split(nl)

def idx(stripped):
    hits = [i for i, l in enumerate(lines) if l.strip() == stripped]
    assert len(hits) == 1, f"{stripped!r}: {len(hits)} matches"
    return hits[0]

def indent(i):
    return lines[i][: len(lines[i]) - len(lines[i].lstrip())]

# 1. Two new state vars after _fire_ticks.
i = [k for k, l in enumerate(lines) if l.startswith("var _fire_ticks := 0")]
assert len(i) == 1, "var _fire_ticks line"
lines[i[0] + 1 : i[0] + 1] = [
    "var _shot_pos := Vector2.ZERO    # muzzle position captured on the press tick",
    "var _shot_dir := Vector2.ZERO    # aim captured on the press tick",
]

# 2. try_fire(): capture on the press tick; fired.emit moves to the active tick.
i = idx("_fire_ticks = 0")
ind = indent(i)
lines[i + 1 : i + 1] = [ind + "_shot_pos = muzzle_position()", ind + "_shot_dir = aim_vec()"]
i = idx("fired.emit(self)")
del lines[i]

# 3. _weapon_tick(): spawn from the captured values, then emit fired with the shell.
i = idx("var pos := muzzle_position()")
lines[i] = indent(i) + "var pos := _shot_pos"
i = idx("world.spawn_shell(self, pos, aim_vec())")
lines[i] = indent(i) + "world.spawn_shell(self, pos, _shot_dir)"
i = idx("_play_fire_sound()")
lines[i + 1 : i + 1] = [indent(i) + "fired.emit(self)"]

open(p, "w", encoding="utf-8", newline="").write(nl.join(lines))
print("tank.gd patched")
