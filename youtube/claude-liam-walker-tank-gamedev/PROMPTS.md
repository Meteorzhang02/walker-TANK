# PROMPTS — every prompt that appears in this film

## B00 — cold-open composer (illustrative reconstruction, not a transcript)
Labeled on screen ("Illustrative reconstruction, not a transcript.") and aloud. It describes this game's actual
idea from CONCEPT.md; it is not claimed to be the student's historical chat.

> Please use Walker to convert my game design document about walker-TANK — a top-down tank battle where my tank,
> YunqiZ, hides behind brick cover that breaks under fire and destroys three enemy tanks — into a small playable
> Godot asset slice that uses my generated art, sound effects and music.

## B09 — the real SDXL prompt for the traced asset (read from the output file)
Read from the ComfyUI `prompt` metadata inside `assets/raw/hull/CHAR-hull_right_00001_.png`
(also saved as `evidence/raw-output-metadata.json`). Identical to ASSET-LOG.md "Shared settings".

- Positive: `realistic military tank hull without turret, oblique top-down view, worn olive drab paint, chipped edges showing bare steel, wide front dozer blade, rear storage box, flat overcast diffuse lighting, game sprite, isolated on plain white background, no shadow, highly detailed`
- Negative: `turret, cannon, gun barrel, text, watermark, people, ground, scenery, cast shadow, blurry, cartoon, toy`
- `sd_xl_base_1.0.safetensors`, guide `guide2_hull_right.png`, seed 846322750311363, 25 steps, cfg 7.0, dpmpp_2m / karras, denoise 0.55.

## B34 — Your Turn (suggested prompt; read aloud verbatim, then discussed)
> Please use Walker to add one new sound event to my walker-TANK slice: a short click when the 0.8-second reload
> finishes. First add it to my event-to-sound map and predict how many clicks ten seconds of held fire should give.
> Then extend tests/test_sound_triggers.gd to count it, and only then edit the game code.

Why this prompt: it is one bounded change, and it forces the order the slice used for its five existing sounds
(map → prediction → automated count → code), so the viewer checks a number before trusting their ears.

## Prompts NOT used
No paid generation, no image/audio/video model was called for this film. Narration is local Kokoro `am_onyx`.
