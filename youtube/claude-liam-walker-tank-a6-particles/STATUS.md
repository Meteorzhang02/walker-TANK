# STATUS — claude-liam-walker-tank-a6-particles

- **Final MP4:** `D:/CSYE7270/assignment2/claude-liam-walker-tank-a6-particles/exports/landscape/claude-liam-walker-tank-a6-particles.mp4`
- **Length:** 210.33 s (3:30) · 3840 × 2160 · 30 fps · 6309 frames · AAC 48 kHz · 43,473,424 bytes
- **SHA-256:** `42e9e9074983ac15453db15f2a8d15047bc123ff0d8e859f3c1aad371a2670d4`

| Quality check | Result |
|---|---|
| `./art godot-gamedev --check` before render | PASS: 82 files, 482 exclusions, 7 components, 4 exact excerpts, 4 code→result pairs |
| `./art godot-gamedev --check` at handoff (ledger refreshed) | PASS, same counts (`_qc/check-handoff.json`) |
| Review cut `./art run --height 1080` | exit 0, 210.7 s, 21/21 slots, beat-lint clean |
| GATE V (frame-level visual QC, review cut) | 42 frames, 0 BLOCKER, 0 MAJOR (`_qc/REPORT.md`) |
| GATE T (type lock), attempt 1 | FAIL: B06 and B10 bottom-strip text over 12 words (`_qc/TYPECHECK-attempt1.md`) |
| GATE T, attempt 2 | PASS (`TYPECHECK.md`) |
| Final export `./art final --height 2160 --fps 30` | exit 0 (attempt 2), 357 s, foreground; `verified.json` status `ready`, same SHA-256 |
| Full decode of the master (`ffmpeg -f null`) | no errors |
| Sound | mean −27.5 dB, max −4.2 dB; silences > 1.5 s only at the B00→B01 lead (1.9 s) and the outro's silent tail (1.6 s) |
| Visual inspection of the master | one frame per beat (`_qc/final-sheet.png`): code readable, every capture labelled FIXTURE or MY PLAY RECORDING, FPS patch present, outro locked |
| Voice | Kokoro `am_onyx`, local, $0.00 |
| walker-TANK untouched | `git status` clean at `2bc81f5`; only `git archive 41a6b8b` was run there |

The toolkit's auto-generated per-beat STATUS table is kept at `_qc/STATUS-toolkit-generated.md`.
