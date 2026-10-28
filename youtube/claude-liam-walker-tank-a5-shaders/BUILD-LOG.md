# BUILD-LOG — claude-liam-walker-tank-a5-shaders

## RESULT (unattended run, 2026-10-28)

- **Final MP4:** `D:/CSYE7270/assignment2/walker-TANK/youtube/claude-liam-walker-tank-a5-shaders/exports/landscape/claude-liam-walker-tank-a5-shaders.mp4`
- **Duration:** 185.17 s (3:05) · **Resolution:** 3840×2160, H.264, 30 fps (5555 frames) + AAC 48 kHz · **Size:** 26,600,157 bytes (25.4 MiB)
- **SHA-256:** `0e13fc655269689d179f19adf2a869a57c950927165d3c85a1fb14206a2d2a7c` (matches `claude-liam-walker-tank-a5-shaders.verified.json`, status `ready`)
- **Source revision shown on screen:** walker-TANK **`561d47d`** (B00 result line, every code/figure footer, verdict heading; working tree clean before and after)
- **Title:** "Walker-TANK: Shaders, Predicted and Measured"

### Quality-check results
| Check | Result |
|---|---|
| `./art godot-gamedev --check` (before render) | PASS — 59 source files, 3523 exclusions, 6 components, 3 exact excerpts, 3 code→result pairs |
| `./art godot-gamedev --check` (at handoff, ledger refreshed for the new export files) | PASS — 59 files, 3615 exclusions, 6 components, 3 excerpts, 3 pairs |
| Review cut `./art run --height 1080`, attempt 1 | **FAILED** (exit 2): toolkit review timecode `drawtext` passes an unescaped Windows font path (`fontfile=D:\…`); ffmpeg filter parse error. Toolkit bug, not edited. Log: `_qc/run-attempt1.log` |
| Review cut, attempt 2 (`ART_NO_DRAWTEXT=1`, toolkit's own switch; labels carry time ranges instead) | PASS: 185.4 s, 14/14 slots, beat-lint clean, Gate V 28 frames 0 BLOCKER / 0 MAJOR |
| GATE T (type lock), final attempt 1 | **FAIL** on B07: §8.6b bbox-overlap; the near-black wall in my "brightness 0.0" sweep crop was read as two overlapping text runs. My figure, not a shared template → fixed (crop swapped for `roughness_scale` 0.0). `_qc/TYPECHECK-attempt1.md`, `_qc/final-attempt1.log` |
| GATE T, final attempt 2 | PASS (TYPECHECK.md) |
| Gate V, final | 28 frames, 0 BLOCKER / 0 MAJOR (`_qc/REPORT.md`) |
| Final export `./art final --height 2160 --fps 30` attempt 2 | EXPORT_EXIT=0, 5 min 21 s, foreground; not killed |
| Full decode of the master | OK (`ffmpeg -f null`, no errors) |
| Sound | mean −27.6 dB, max −4.9 dB; silences > 1.5 s only B00 tail → B01 0.8 s lead (1.9 s) and the outro's 1.0 s silent tail (1.6 s) |
| Frame counts | every Remotion beat = its padded audio frames (±1) |
| Visual inspection (Read PNGs) | 15/50/85 % of every beat (`_qc/sheet-*.png`) and nine frames of the master (`_qc/final-sheet.png`): code readable, labels present, no clipping after fixes |
| Memory | `_qc/memory-monitor.log`: ffmpeg peaked at 8.4 GB, free RAM fell to 264 MB during the 4K encode, but it finished; no orphaned ffmpeg before or after |

**Estimated render time printed before the final:** about 4–5 minutes (A3's 218.6 s master took 4 min 47 s). Actual: 5 min 21 s.

### Decisions made without you
1. **"Exactly 8 beats" = your 8 sections.** The skill's walker bookends (composer, hesitant writer, verdict → Your Turn → outro) and its code-then-result contract (every code excerpt must be followed by a separate visible-result beat) need more than 8 beat-sheet entries. 14 beats map onto your 8 sections: §1 B00–B01, §2 B02–B03, §3 B04, §4 B05–B06, §5 B07, §6 B08–B09, §7 B10, §8 B11–B13.
2. **Length 3:05, not ~2:00.** First draft was 723 words (~4.5 min); cut once to 521 words. Going further would have dropped content you listed (§8 alone is 32 s because it states every required item). Recorded here, not hidden.
3. **Excerpt ranges.** B02 shows `hit_flash.gdshader` **lines 1–9** (your 1–8 plus the closing brace, since the narration says "the whole shader"). B05 shows the whole `hint_experiment.gdshader` (lines 1–14) with **lines 4–5 lit**. B08 shows `brick_surface.gdshader` lines 1–11; brick line 33 (`ALBEDO`) is shown verbatim on B09's excerpt strip.
4. **The brief's colour line and the driver line are in the code beat's notes panel:** "CHANGE-BRIEF.md line 45 = the same colour line as line 8" (string-compared by the script), and driver line 70 `material.set_shader_parameter(PARAM, v)` with line 12 `PARAM = "hit_amount"`.
5. **Generated-shader lines 7 and 19** are shown as verbatim prefixes ending "…" (the full lines overflow the notes panel), labelled "(excerpt)".
6. **§6 visible result.** The code→result contract needed a result after the brick-shader excerpt. I used your `materials_side_by_side.png`: three box means on the intact wall (top 87.5, front 73.4, end 60.8 red). **These means were measured by this film's script** from your existing PNG, labelled so on screen; the front box equals your capture tool's own 11×11 mean (73.4, 54.1, 37.7). No new capture.
7. **Sweep strip (§5):** brightness 2.0, roughness_scale 0.0, uv_scale 0.1, uv_scale 4.0. First version used brightness 0.0, swapped after GATE T (above). The narration says brick size visibly changes and that the look is still your call; TEST-REPORT lists those looks as human items. Note: at uv_scale 0.1 individual bricks are clearly visible, which is the opposite of the brief's "huge bricks" expectation. I did not judge it.
8. **Play recording (§2):** source 4.5–14.7 s, frames in order, scaled only, labelled "Screen recording of my play · not a scripted capture"; its own audio not used. I chose the start so the two real hits (≈6.65 s, ≈11.0 s) land on "A shell lands" / "Second hit". The Windows privacy pop-up in the first ~4 s is outside the clip.
9. **Labels:** every capture says "In-engine capture (scripted)"; markers/boxes are labelled "added"; code views say "Godot editor reconstruction"; the B00 prompt says "Illustrative reconstruction, not a transcript".
10. **Greeting** "Hola, Liam" (A3 used Hej). Your Turn prompt shortened to fit the time.
11. **"One next step"** = check the pause rule by hand in a windowed run (from TEST-REPORT §13 / FRICTIONAL *Unresolved*).
12. **Reel inside walker-TANK** as you asked. Its own files are therefore in the checker's inventory and are listed as exclusions (reason: this film's own folder). `build_evidence.py` must be re-run last before each check.
13. **Helpers** `remotion_win.py` (npx shim), `pad_audio.py` and `bind_cues.py` were *copied* from the A3 reel's `scripts/`; the A3 folder was only read.
14. Cue phrases moved to words Whisper actually heard ("Quad A" was heard as "quata"; numbers come out as digits).

### Failures and fixes (in order)
- Two line numbers first read from a concatenated `cat -n` listing were wrong (brief colour line 45, not 70; `PARAM` line 12, not 13). Fixed from `grep -n` before any render.
- B02 notes panel overflowed (third note clipped) → two notes. B08 last line clipped → code font 26. B05 last lines and third note clipped → font 23, notes merged. B01's third line was still typing at the cut → shortened to "Its numbers can be checked." (verified complete in the last frame).
- Review drawtext bug and GATE T B07 as in the table.

### Observed, not changed (shared toolkit)
- The toolkit's compile adds an "@NikBearBrown" channel-title overlay under the B00 composer, which already shows the @NikBearBrown folder chip (OUTRO-LOCK says one handle per beat). Same in the A3 film. Not edited.
- `runtime/remotion/src/scenes/GodotDesignFigure.tsx` and `runtime/remotion/package-lock.json` already had uncommitted modifications before this run; rendered as they are, not touched.
- `./art run`'s timecode `drawtext` cannot parse Windows paths (above).

### Limits (stated in the film or here)
- The film reuses only your existing captures and recording; Godot was not launched; no test was re-run. Test results are from your logs.
- The verifier checks hashes, line ranges and pairings, not whether the explanation is right. FACTCHECK.md maps every claim to its file.
- Some figure text (the per-pixel tables inside B04/B09) is small at 1080p viewing; the key numbers are repeated on the large cards.

### Scope kept
Written only inside this folder; nothing else in walker-TANK touched; no git command that writes; no toolkit file edited; nothing pushed, uploaded or published.

---

## Runtime
Windows 11 (Chinese locale), Git Bash, `PYTHONUTF8=1`, `python3` shim → Python 3.12.1, ffmpeg/ffprobe in `~/bin`, Node 24.11,
Remotion node_modules present, Kokoro `am_onyx` local, faster-whisper `base.en` local. 16 GB RAM (4.4 GB free at start). No orphaned
ffmpeg/node/Godot at start or after the export.

## Commands (in order)
`make_evidence.py` → `make_sheet.py` → `generate_audio_kokoro.py` (14 beats, $0.00) → `pad_audio.py` → `make_sheet.py` →
`bind_cues.py` → `make_b03.py` → `remotion_win.py --only Bxx --force` (one per beat) → `build_evidence.py` ×2 → `./art godot-gamedev --check` →
`./art run --height 1080` (×2) → `./art final --height 2160 --fps 30 --out exports/landscape` (×2) → `build_evidence.py` ×2 → check. See BUILD-PROMPT.md.
