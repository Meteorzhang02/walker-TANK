# TYPECHECK.md — GATE T

Reel: `claude-liam-walker-tank-a7-animation`  |  Checked: 2026-11-21T22:24  |  Overall: **FAIL**  |  Beats checked: 18  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

> **§8.7–§8.9 PLACEHOLDER / TRUNCATION — GATE BLOCKED:**
> Every item below must be fixed before `./art run` or `./art final`.
> Labels must be authored short phrases (2–5 words). Subs must add something real
> (≤8 words) or be omitted. 'see narration' and truncated strings must not reach
> a rendered surface.

> - §8.9 [B08/output[0]] text ends truncated: 'Check C1: shell P+2 · clip frame 1 P+3 · 0.0167 s'

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 57px >= floor 41px | PASS | — |
| B02 | ? | light | no-wordy-card §8.5: pull-quote (11 words ≤ 12) | PASS | — |
| B03 | ? | — | no video | SKIP | — |
| B04 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B05 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B06 | ? | light | no-wordy-card §8.5: pull-quote (8 words ≤ 12) | PASS | — |
| B07 | ? | — | no video | SKIP | — |
| B08 | ? | light | no-wordy-card §8.5: pull-quote (12 words ≤ 12) | PASS | — |
| B09 | ? | — | no video | SKIP | — |
| B10 | ? | — | no video | SKIP | — |
| B11 | ? | — | no video | SKIP | — |
| B12 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B13 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B14 | ? | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B15 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeVerdictArtifact) — §8.1 hachure/crossbar fragment… | PASS | — |
| B16 | ? | light | min-size §8.1: hand-drawn pattern (ClaudeComposerAsk) — §8.1 hachure/crossbar fragments ar… | PASS | — |
| B17 | ? | light | min-size §8.1: min text-run height 49px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

### SWEEP GATES §8.7–§8.12b (placeholder / truncation / code-card)

- **§8.9 [B08/output[0]] text ends truncated: 'Check C1: shell P+2 · clip frame 1 P+3 · 0.0167 s'**

**Fix:** §8.7–§8.9: rewrite flagged labels/subs to authored words. §8.12: replace prose-comment code beat with FormACard or ClaudeVerdictArtifact. §8.12b: give ClaudeCodeBeat a real filename title (e.g. 'analysis.py').

---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 8 | 0 |
| min-size §8.1 | 13 | 0 |
| overflow §8.2 | 13 | 0 |
| contrast §8.3 | 13 | 0 |
| contrast-local §8.3b | 13 | 0 |
| bbox-overlap §8.6b | 13 | 0 |
| card-clip §8.13 | 13 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
