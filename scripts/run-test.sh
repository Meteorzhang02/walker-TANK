#!/usr/bin/env bash
# scripts/run-test.sh <test-file.gd> <fps|realtime> [timeout-seconds]
# Assignment 6 wrapper. Same as the course version, except --path . because
# walker-TANK keeps project.godot at the repository root (not in godot/).
set -o pipefail
mkdir -p logs
GODOT="${GODOT:-/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe}"
if [ "$2" = "realtime" ]; then
	fps_args=(); tag="realtime"
else
	fps_args=(--fixed-fps "$2"); tag="${2}fps"
fi
log="logs/$(basename "$1" .gd)_${tag}.log"
timeout "${3:-120}" "$GODOT" --headless "${fps_args[@]}" --path . --script "res://tests/$1" 2>&1 | tee "$log"
status=$?
if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi
exit $status
