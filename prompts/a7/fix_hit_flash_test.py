# A7 test edit (mine, with Claude chat): test_hit_flash.gd freezes every enemy (line 205, DISABLED).
# The shell now leaves on the shooter's own physics tick (brief: frame 1, 2 ticks after the press),
# so e0 must run for the shot. Let e0 run (target = null keeps it still, see test_pins PIN-6)
# from the press until the hit, then freeze it again. Nothing else in the file changes.
p = "tests/test_hit_flash.gd"
src = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in src else "\n"
lines = src.split(nl)

def idx(stripped):
    hits = [i for i, l in enumerate(lines) if l.strip() == stripped]
    assert len(hits) == 1, f"{stripped!r}: {len(hits)} matches"
    return hits[0]

def indent(i):
    return lines[i][: len(lines[i]) - len(lines[i].lstrip())]

i = idx("e0.reload_left = 0.0")
ind = indent(i)
lines[i + 1 : i + 1] = [
    ind + "# A7: the shell now leaves on e0's own physics tick, 2 ticks after the press, so e0 runs for",
    ind + "# this shot. target = null keeps it still (test_pins PIN-6); it is frozen again after the hit.",
    ind + "e0.target = null",
    ind + "e0.process_mode = Node.PROCESS_MODE_INHERIT",
]
i = idx("while events.is_empty() and _now_t() - t0 < 1.0:")
assert lines[i + 1].strip() == "await process_frame", "await line after the while"
lines[i + 2 : i + 2] = [indent(i) + "e0.process_mode = Node.PROCESS_MODE_DISABLED"]

open(p, "w", encoding="utf-8", newline="").write(nl.join(lines))
print("test_hit_flash.gd patched")
