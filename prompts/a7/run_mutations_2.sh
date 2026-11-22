#!/usr/bin/env bash
# A7 Step 6, the assignment's own mutation list (mine, with Claude chat). Same method as run_mutations.sh.
REPO="$(pwd)"
GODOT="${GODOT:-/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe}"
OUT="$REPO/logs/a7-mutations.txt"
run_mut () {
  local id="$1" file="$2" expr="$3" test="$4" fps="$5" desc="$6"
  local wt="$REPO/../walker-mut-$id"
  git worktree remove --force "$wt" 2>/dev/null
  git worktree add --detach "$wt" HEAD > /dev/null 2>&1
  cd "$wt"
  "$GODOT" --headless --path . --import > /dev/null 2>&1
  bash scripts/run-test.sh "$test" "$fps" > /dev/null 2>&1; local ctrl=$?
  if [ -n "$expr" ]; then sed -i "$expr" "$file"; fi
  local changed; changed=$(git diff --numstat -- "$file" | awk '{s+=$1} END {print s+0}')
  bash scripts/run-test.sh "$test" "$fps" > /dev/null 2>&1; local code=$?
  local log="logs/$(basename "$test" .gd)_${fps}fps.log"
  cp "$log" "$REPO/logs/mutation_${id}_$(basename "$test" .gd)_${fps}fps.log"
  {
    echo "======== $id: $desc"
    echo "file: $file | lines changed: $changed | control exit=$ctrl | mutated exit=$code"
    git diff -U0 -- "$file" | grep -E '^[-+][^-+]'
    grep -E "FAIL|readback:|RESULT" "$log" | head -6
  } 2>/dev/null | tee -a "$OUT"
  cd "$REPO"; git worktree remove --force "$wt"
}
run_mut M5 animations/motion_clips.tres 's#DustMount/Dust:frame#DustMount/Dust:frames#' test_clip_readback.gd 60 "OFFICIAL 1: track subname renamed (property frame -> frames)"
run_mut M6 animations/motion_clips.tres 's/"values": \[0, 1, 2, 3\]/"values": [0, 1, 2, 4]/' test_clip_readback.gd 60 "OFFICIAL 3: last key set to cell 4 = hframes * vframes, past the sheet"
run_mut M7 "" "" test_clip_readback.gd 60 "OFFICIAL 4: rig from an empty cache (fresh worktree: no .godot, --import, read-back). Expected to PASS: the rig is baked to a committed .tres, no importer holds its loop mode"
git worktree list
