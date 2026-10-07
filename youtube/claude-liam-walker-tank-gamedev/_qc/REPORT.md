# Gate V — visual QC report

Frames sampled: 72  ·  BLOCKER: 0  ·  MAJOR: 0

Regional text-contrast checks (all declared regions required): B03, B04, B15, B17, B19, B21, B23, B24. Whole-frame dimming/scene color is not text contrast; empty-frame, fill and declared safe-area checks remain active. Visual content review remains required.

Clean — no BLOCKER/MAJOR defects. ✓
---

## Manual review (agent, not a human sign-off): 2026-10-07

Master `exports/landscape/claude-liam-walker-tank-gamedev.mp4`: 3840×2160, 30 fps, H.264 + AAC 48 kHz stereo,
611.433 s, SHA-256 `b13a75400f8405be572142c3ab1c4565d49f980c2c82b4a6851c6b8d074fd150` (matches `.verified.json`).
Frames read: every beat at 15/50/85 % of the master (`_qc/master/`, `_qc/master-sheet-0..2.png`).

| Check | Result |
|---|---|
| Gameplay is the native 4K engine render, no retint/retime | PASS: `treatment: none`; no retime/slow/center-cut notices in `_final.log`; each clip = exact frame range (clips.json) |
| Frame alignment | PASS: VICTORY at B24 clip frame 6 (take 1426), PAUSED at B21 clip frame 199 (take 739) |
| Sound sync | PASS: B21 player shot at +0.10 s in both take and master; B24 victory onset +0.25 s (expected ≈ 0.20 s) |
| GAME AUDIO ONLY segment (B24) | PASS: labeled on screen; master level −23.7 dB = take −21.7 dB − 2 dB; correlation with the take 0.71 (AAC) |
| Narrated gameplay audio | Game audio ducked under Liam (side-chain). Effects under speech are audible but ~6 dB quieter than in the raw take (e.g. B21 explosion) |
| Code readable, verbatim, labeled reconstruction | PASS: 10 excerpts, gamedev check PASS; B16/B20 at the 23 px floor (smallest), still inside the panel |
| Walker bookend order | PASS: B00 composer (reconstruction labeled) → B01 writer ("finished" → "started") → body → B33 verdict → B34 Your Turn (Liam signs off) → B35 outro |
| Outro lock | PASS: exact title, @NikBearBrown, one mascot, no subline; spoken title + "At Nik Bear Brown"; last 0.9 s digital silence; no jingle |
| Captions | none burned in (none requested) |
| Loudness | −24.2 LUFS integrated, LRA 7.1 LU, true peak −1.5 dBFS: quiet for YouTube; not normalized (a publishing decision) |

Findings about the game itself (not altered): the HUD's white default labels measure 0.15–0.30 regional contrast on the
busy ground (control hints at 70 % opacity are the weakest). Readable in the frames reviewed, but a candidate fix for the student.

Human review still required: watch and listen to the whole film. This report is not a human sign-off.
