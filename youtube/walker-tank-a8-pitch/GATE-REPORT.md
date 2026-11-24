# GATE REPORT — walker-tank-a8-pitch

Final master, 2026-11-24. Built with brutalist.art (`show-tell` beats + `godot-waikthrough` capture). Logs are in `_qc/`.

## The film
- File: `youtube/walker-tank-a8-pitch/walker-tank-a8-pitch.mp4` (git-ignored by `.gitignore:30 *.mp4`). It was rendered to `brutalist.art/renders/` and copied byte for byte.
- SHA-256: `32d99d49b3885756d7c14d09198842c15784082cc4c5a403fd01b3583998c9f8`
- 204.2 s (3:24) · 3840×2160 · 30 fps · 6,126 frames · H.264 + AAC 48 kHz stereo · 33.6 MB
- Capture: `capture/run-01.mp4`, labelled on screen "tag a7, game source 4f88f1b". The scratch copy came from `git archive HEAD` at `3cc29f2`, whose game files are identical to 4f88f1b. The a7 tag commit is `e4e5d5f`.
- Voice: Kokoro `am_onyx`, local. No paid API was used, and nothing was uploaded.

## Gates
| Gate | What it checks | Result |
|---|---|---|
| F | paperwork present | PASS |
| L | beat-mix lint | PASS |
| SHAPE | finance chart shape | skip (not a finance reel) |
| A | static scene pre-flight, all 10 Manim scenes | PASS |
| W | WCAG contrast, margins, text overlap | PASS (every scene clean) |
| B | Manim layout audit, strict (warnings block) | PASS |
| V | frame-level visual QC on the compiled cut (`_qc/run-5.log`, `_qc/REPORT.md`) | PASS — 28 frames, 0 BLOCKER, 0 MAJOR |
| T | type check, final pre-gate (`TYPECHECK.md`) | PASS |
| render integrity | compile.py verification: full decode, `walker-tank-a8-pitch.verified.json` status `ready`, input hashes | PASS |
| full decode | `ffmpeg -v error -f null` on the copied master | PASS (no errors) |
| bookend_check | outro title/handle/subline | PASS |
| factcheck_check | 24 rows, every claim-bearing beat covered | PASS |
| banned_card_check | | PASS |
| godot-waikthrough verify | coverage.json evidence (5 implemented, 3 planned) | PASS |
| instructor-name scan | "Bear", "NikBearBrown", "in_for_bear" across reel text, .gd, .py, .json, .md; mp4 tags | none found |
| length | 2:00–4:00 | 3:24 PASS |

Audio: integrated −24.8 LUFS, LRA 6.2 LU, true peak −4.7 dBFS. The last 3 s carry the spoken title, so there is no silent tail.

## Advisory (no gate fails)
compile.py's skin lint warns:
- `BIDEA: COLD OPEN LAW wants ClaudeComposerAsk`
- `BOUT: OUTRO LAW wants ClaudeTitleOutro`

Both are warnings only. ClaudeTitleOutro hardcodes the instructor's channel handle, and BUILD-PROMPT forbids instructor credits, so the film keeps its own opener and outro. No hard gate required the Bear outro or opener.

## Failures found and fixed on the way
1. **The first 4K review render was killed for low memory**, by the system rather than by a gate. Reran the review pass at 1080 (QC only). The final rendered at 2160 without trouble.
2. **Gate V failed: 8 BLOCKER, 4 MAJOR.**
   - B01/B04 full-frame gameplay counted as "edge-bleed" and "low contrast". Fixed by declaring `qc.full_bleed` per beat and checking contrast on the burned-in label and caption plaques (`qc.contrast_regions`, with a written reason). Nothing in the footage changed.
   - B11 blocks and the B12 left panel sat about 10 px past the left title-safe edge. Moved right; the B12 capture overlay moved with the panel (px 171 → 212).
3. **Gate T failed on 4 beats:**
   - B02 and B09: a dark tank icon inside an ink-outlined screen or laptop read as two stacked labels. Screen and laptop outlines are now grey (DIM), and every scene using them was re-rendered.
   - B08: the terracotta flag read as accent-colour text. Now pale terracotta.
   - BOUT: the hyphen in "Walker-TANK" was 36 px against a 41 px floor. Title raised from 72 to 86 pt.
4. Visual review, not a gate: in B02 the box's top corner touched the "battle" label. The box is smaller and the row raised.

## Effects named in the narration — on screen
All four were checked in the 4K take (`CAPTURE.md`, `_qc/effects/b04_sheet.png`): debris from the hit cover, YunqiZ's red flash, a damaged tank smoking, and a smoking wreck. No narration change was needed, and nothing was drawn into a gameplay beat.
