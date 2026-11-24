# TYPECHECK.md — GATE T

Reel: `walker-tank-a8-pitch`  |  Checked: 2026-11-24T09:48  |  Overall: PASS  |  Beats checked: 14  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| BIDEA | bookend | light | min-size §8.1: min text-run height 66px >= floor 41px | PASS | — |
| B01 | capture | — | no video | SKIP | — |
| B02 | manim | light | min-size §8.1: min text-run height 121px >= floor 41px | PASS | — |
| B03 | manim | light | min-size §8.1: min text-run height 85px >= floor 41px | PASS | — |
| B04 | capture | — | no video | SKIP | — |
| B05 | manim | light | min-size §8.1: min text-run height 68px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B06 | card | light | no-wordy-card §8.5: no prose payload found | PASS | — |
| B07 | manim | light | min-size §8.1: min text-run height 68px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B08 | manim | light | min-size §8.1: min text-run height 121px >= floor 41px | PASS | — |
| B09 | manim | light | min-size §8.1: min text-run height 75px >= floor 41px | PASS | — |
| B10 | manim | light | min-size §8.1: min text-run height 225px >= floor 41px | PASS | — |
| B11 | manim | light | min-size §8.1: min text-run height 72px >= floor 41px (individual-char fallback at 2×) | PASS | — |
| B12 | capture | — | no video | SKIP | — |
| BOUT | manim | light | min-size §8.1: min text-run height 43px >= floor 41px | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 1 | 0 |
| min-size §8.1 | 11 | 0 |
| overflow §8.2 | 11 | 0 |
| contrast §8.3 | 11 | 0 |
| contrast-local §8.3b | 11 | 0 |
| bbox-overlap §8.6b | 11 | 0 |
| card-clip §8.13 | 11 | 0 |
| kerning §8.4 | 9 | 0 |
| redundancy §8.10 (advisory) | 1 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
