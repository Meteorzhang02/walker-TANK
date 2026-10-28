# RIFF — observations vs interpretation

| Artifact + range | Visible observation | Interpretation (source) | Narration | Next experiment |
|---|---|---|---|---|
| play.mp4 4.5–14.7 s (B03) | YunqiZ (left) turns fully red at ≈6.65 s, back to olive by ≈7.15 s; again at ≈11.0 s with fire already on the hull; enemies never red; the Godot run bar and window title are visible (editor run) | driver sets 1.0 then fades over 0.5 s (driver header; TEST-REPORT §3: 0.5000 s); fire = A2 low-health effect (README A2) | "A shell lands, YunqiZ turns red, and it fades in about half a second." | a frame-stepped capture to time the fade on screen |
| hit_flash_0.0–2.0.png (B04) | tank greener → redder; 2.0 flat red | colour line + no clamp (CSV) | "At two, pure red" | choose named pixels on the final drawn layer |
| hint_both.png (B06) | Quad A's middle band is the same grey as the background; B is lighter throughout | background measures 127; source_color decode/encode cancels (brief §4) | "Quad B is brighter, exactly as predicted" | sample a mid-grey on a contrasting background |
| sweep captures (B07) | brightness 2.0 lighter, roughness_scale 0.0 slightly darker; uv_scale 0.1 shows individual bricks, 4.0 a fine repeating grid | look judgement pending (TEST-REPORT human items 3–6) | "brick size visibly changes, but the look is still the student's call" | the student's own by-eye notes for each end |
| materials_side_by_side.png (B09) | intact wall: top lightest, front middle, +x end darkest | spatial shader lit by the single Sun (MATERIALS §4 N·L ordering top > front > end) | "One texture, three faces" | add a fill light in a copy and re-measure |

Observed in the student's own recording and scripted captures; no playtest by the film builder. The recording's first
seconds also show a Windows privacy-indicator pop-up at the window's bottom right (OS overlay, outside the clip used).
