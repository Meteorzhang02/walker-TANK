#!/usr/bin/env bash
# A7 Step 6 mutations (mine, with Claude chat). Each mutation runs in its own git worktree at HEAD:
# import, control run (must pass), apply one edit, check it applied, run the test that should catch it.
REPO="$(pwd)"
GODOT="${GODOT:-/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe}"
OUT="$REPO/logs/a7-mutations.txt"
: > "$OUT"

run_mut () {   # id  file  sed-expr  test  fps  description
  local id="$1" file="$2" expr="$3" test="$4" fps="$5" desc="$6"
  local wt="$REPO/../walker-mut-$id"
  git worktree remove --force "$wt" 2>/dev/null
  git worktree add --detach "$wt" HEAD > /dev/null 2>&1
  cd "$wt"
  "$GODOT" --headless --path . --import > /dev/null 2>&1
  bash scripts/run-test.sh "$test" "$fps" > /dev/null 2>&1; local ctrl=$?
  sed -i "$expr" "$file"
  local changed; changed=$(git diff --numstat | awk '{s+=$1} END {print s+0}')
  bash scripts/run-test.sh "$test" "$fps" > /dev/null 2>&1; local code=$?
  local log="logs/$(basename "$test" .gd)_${fps}fps.log"
  cp "$log" "$REPO/logs/mutation_${id}_$(basename "$test" .gd)_${fps}fps.log"
  {
    echo "======== $id: $desc"
    echo "file: $file | lines changed: $changed | control exit=$ctrl | mutated exit=$code"
    git diff -U0 | grep -E '^[-+][^-+]'
    grep -E "FAIL|RESULT|readback:|SCRIPT ERROR" "$log" | head -6
    if [ "$ctrl" = 0 ] && [ "$changed" = 1 ] && [ "$code" != 0 ]; then echo "VERDICT: caught"; else echo "VERDICT: NOT caught or invalid run"; fi
  } | tee -a "$OUT"
  cd "$REPO"
  git worktree remove --force "$wt"
}

run_mut M1 animations/motion_clips.tres 's#DustMount/Dust:frame#DustMount/Dustt:frame#' test_clip_readback.gd 60 "track_dust track path points at a node that does not exist"
run_mut M2 animations/motion_clips.tres 's/^loop_mode = 1/loop_mode = 0/' test_clip_readback.gd 60 "track_dust loop mode flipped to LOOP_NONE (brief prediction 1)"
run_mut M3 animations/motion_clips.tres 's/"update": 1,/"update": 0,/' test_clip_readback.gd 60 "track_dust frame track set to continuous updates"
run_mut M4 scripts/tank.gd 's/^const SHOOT_ACTIVE_FRAME := 1/const SHOOT_ACTIVE_FRAME := 2/' test_anim_states.gd 60 "shell moved from frame 1 to frame 2"
run_mut M4b scripts/tank.gd 's/^const SHOOT_ACTIVE_FRAME := 1/const SHOOT_ACTIVE_FRAME := 2/' test_pins.gd 60 "same mutation, against the pins"
git worktree list
