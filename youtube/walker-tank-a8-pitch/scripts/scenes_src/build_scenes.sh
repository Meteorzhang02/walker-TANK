#!/bin/sh
# Rebuild scenes.py from the pasted show-tell kit (head + pacing, A8: 0.06 s slack in finish) and the film's scenes.
cd "$(dirname "$0")/../.." && { echo '"""scenes.py — walker-tank-a8-pitch drawn beats (show-tell kit pasted below, per the skill; not imported)."""'; cat scripts/scenes_src/_kit_head.txt scripts/scenes_src/_kit_pace.txt scripts/scenes_src/_scenes_body.py; } > scenes.py
