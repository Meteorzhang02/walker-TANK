#!/usr/bin/env bash
# scripts/run-test.sh <test-file.gd> <fps>
# Windows/Git Bash version: project.godot is at the repo root, so --path .
set -o pipefail
GODOT="/d/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe"
mkdir -p logs
log="logs/$(basename "$1" .gd)_${2}fps.log"
timeout 120 "$GODOT" --headless --path . --script "res://tests/$1" --fixed-fps "$2" 2>&1 | tee "$log"
status=$?
if grep -qE "SHADER ERROR|SCRIPT ERROR" "$log"; then status=1; fi
exit $status
