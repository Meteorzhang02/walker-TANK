# A7 re-pin (mine, with Claude chat). Only the pins the brief named change: PIN-1, PIN-2, PIN-4
# move +2 ticks because the shell, muzzle FX and fire sound now come on frame 1 (brief phase table).
# PIN-3 (reload 48 ticks) and every other pin are unchanged.
p = "tests/test_pins.gd"
src = open(p, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in src else "\n"
lines = src.split(nl)

def idx(stripped):
    hits = [i for i, l in enumerate(lines) if l.strip() == stripped]
    assert len(hits) == 1, f"{stripped!r}: {len(hits)} matches"
    return hits[0]

def indent(i):
    return lines[i][: len(lines[i]) - len(lines[i].lstrip())]

def swap(old, new):
    i = idx(old); lines[i] = indent(i) + new

i = idx("const INPUT_LATENCY := 1")
lines[i + 1 : i + 1] = [
    "# A7 re-pin: the brief's phase table puts the shell, muzzle FX and fire sound on frame 1 at",
    "# 30 fps = 2 physics ticks at 60 Hz. Before A7 this was 0 (the first pins commit).",
    "const SHOT_DELAY_TICKS := 2",
]
swap('[0, "shell"],', '[SHOT_DELAY_TICKS, "shell"],')
swap('[expected_reload, "shell"],', '[SHOT_DELAY_TICKS + expected_reload, "shell"],')
swap('[2 * expected_reload, "shell"],', '[SHOT_DELAY_TICKS + 2 * expected_reload, "shell"],')
swap("shell_ticks[0] if shell_ticks.size() > 0 else -999, 0)",
     "shell_ticks[0] if shell_ticks.size() > 0 else -999, SHOT_DELAY_TICKS)")
swap("sound_ticks[0] if sound_ticks.size() > 0 else -999, 0)",
     "sound_ticks[0] if sound_ticks.size() > 0 else -999, SHOT_DELAY_TICKS)")
old_tag = "[PREDICTED TO CHANGE by A7 brief: +2 ticks]"
new_tag = "[RE-PINNED A7: shell on frame 1 = +2 ticks]"
n = sum(l.count(old_tag) for l in lines)
assert n == 2, f"tag found {n} times"
lines = [l.replace(old_tag, new_tag) for l in lines]

open(p, "w", encoding="utf-8", newline="").write(nl.join(lines))
print("test_pins.gd re-pinned")
