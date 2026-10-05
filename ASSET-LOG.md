# ASSET-LOG — walker-TANK

One row per generation I kept or seriously considered. Rejected outputs are kept as thumbnails in `design/asset-log/rejected/`.

## Models and tools

| Tool | Version | Where it ran | License / terms |
|---|---|---|---|
| Stable Diffusion XL Base 1.0 (`sd_xl_base_1.0.safetensors`, Stability AI) | 1.0 | Local: Comfy Desktop, ComfyUI v0.38.2, Python 3.13.12, NVIDIA RTX 3060 Laptop GPU (6 GB) | CreativeML Open RAIL++-M (use allowed, with use-based restrictions). *To verify on the model's Hugging Face page.* |
| Stable Audio 3 Small-SFX (`stable_audio_3_small_sfx.safetensors`, Stability AI, ComfyUI repackage `Comfy-Org/stable-audio-3`) | 3.0 Small, post-trained | Local, same machine | Stability AI Community License; text encoder T5Gemma under the Gemma Terms of Use. Trained on licensed AudioSparx and CC-licensed Freesound audio. |
| Stable Audio 3 Small-Music (`stable_audio_3_small_music.safetensors`) | 3.0 Small, post-trained | Local, same machine | Same as Small-SFX |
| T5Gemma text encoder (`t5gemma_b_b_ul2.safetensors`) | — | Local | Gemma Terms of Use |
| ComfyUI | v0.38.2 | Local | GPL-3.0 |
| FFmpeg | system build | Claude's sandbox, for decoding and encoding audio | LGPL/GPL |

**Not generative-model output:** the img2img guide images in `design/guides/` (v1, v2, v3, v3.1), the stripe masks in `design/guides/stripe-mask/`, and every script in `tools/` were made by Claude. They are inputs and edit tools, not generated assets.

## Shared settings

Unless a row says otherwise, every hull generation below used:

- **Workflow:** ComfyUI template "SDXL1.0：文生图（简单）" (`image_sdxl_simple`), changed to img2img: Load Image → VAE Encode → KSampler `latent_image`.
- **Seed:** 846322750311363 (control after generate: fixed)
- **Sampler:** 25 steps, cfg 7.0, `dpmpp_2m`, scheduler `karras`
- **Size:** 1024 × 1024 (from the guide image)
- **Positive prompt:**
  > realistic military tank hull without turret, oblique top-down view, worn olive drab paint, chipped edges showing bare steel, wide front dozer blade, rear storage box, flat overcast diffuse lighting, game sprite, isolated on plain white background, no shadow, highly detailed
- **Negative prompt:**
  > turret, cannon, gun barrel, text, watermark, people, ground, scenery, cast shadow, blurry, cartoon, toy

## Generations — `CHAR-hull`

| # | Asset ID | Guide image | Denoise | Outcome and reason | Edits | Where used |
|---|---|---|---|---|---|---|
| G-01 | `CHAR-hull` right | `guide_hull_right.png` (v1) | 0.55 | **Rejected.** Output almost identical to the guide: flat color blocks, no metal texture. Fails the art direction (realistic, worn steel). | — | Thumbnail `REJ-01` |
| G-02 | `CHAR-hull` right | `guide_hull_right.png` (v1) | 0.80 | **Rejected.** Some panel detail appears, but the dozer blade is lost and the shape drifts. Breaks the character sheet's front-marker rule. | — | Thumbnail `REJ-03` |
| G-03 | `CHAR-hull` right | `guide_hull_right.png` (v1) | 0.70 | **Rejected.** Still flat color blocks, only slight color variation. | — | Thumbnail `REJ-02` |
| G-04 | `CHAR-hull` right | `guide2_hull_right.png` (v2) | 0.55 | **Accepted** as the look for all directions. Worn olive paint, rust and grime, panel lines, road wheels; dozer blade, storage box, facing and angle all kept. Same settings re-run as G-06. | — | Became G-06 |
| G-05 | `CHAR-hull` right | `guide2_hull_right.png` (v2) | 0.65 | **Rejected.** Richer texture, but the model added a turret dome on the hull despite the negative prompt. Breaks the layering strategy (turret is a separate sprite) and would show two turrets. | — | Thumbnail `REJ-04` |
| G-06 | `CHAR-hull` right | `guide2_hull_right.png` (v2) | 0.55 | **Accepted, edited.** Outline matches guide (IoU 0.99). Most weathered of the five. Small pseudo-text markings on the deck; unreadable at game size. | Background removed; colour matched | `CHAR-hull_right.png`; panels 2–7 |
| G-07 | `CHAR-hull` up | `guide2_hull_up.png` (v2) | 0.55 | **Accepted, edited.** Outline matches (IoU 0.99). Blade at front, storage box at rear, readable at 64 px. Small label plate on rear; unreadable at game size. | Background removed; colour matched | `CHAR-hull_up.png` (not mirrored); panels 2–7 |
| G-08 | `CHAR-hull` up-right | `guide2_hull_up-right.png` (v2) | 0.55 | **Accepted, edited, with a note.** Outline matches (IoU 0.99). The model added a raised wedge and a cap-like part on the deck; with the turret on top, part of the wedge still shows beside it. Acceptable for now; candidate for a hand edit. | Background removed; colour matched | `CHAR-hull_up_right.png` (mirrored at runtime for up-left); panels 2–7 |
| G-09 | `CHAR-hull` down-right | `guide2_hull_down-right.png` (v2) | 0.55 | **Accepted, edited, with a note.** Outline matches (IoU 0.99). Cleaner and less worn than the other four, so wear level is not fully consistent. | Background removed; colour matched | `CHAR-hull_down_right.png` (mirrored for down-left); panels 2–7 |
| G-10 | `CHAR-hull` down | `guide2_hull_down.png` (v2) | 0.55 | **Accepted, edited, with a note.** Outline matches (IoU 0.99). About 15–20% brighter olive than the right-facing hull. | Background removed; colour matched | `CHAR-hull_down.png`; panels 2–7 |

*G-06 to G-10 assume the shared settings above with denoise 0.55; confirm against the ComfyUI workflow saved in each PNG.*

## Checks on the accepted hulls

Check sheet: `design/asset-log/check_hull_v2.png` (cutout · guide outline overlay · turret guide on top · 64 px on mud ground with silhouette).

- **Proportion drift (CHANGE-BRIEF case 1):** all five outlines match their guides with IoU 0.991–0.993. Pass.
- **Turret alignment (case 2):** the turret guide placed at the fixed pivot offset sits correctly on all five hulls. Pass, except the extra wedge on up-right (G-08) shows beside the turret.
- **Up/down readability (case 3):** at 64 px the wide blade marks the front in every direction; up and down silhouettes are distinct. Pass.
- **Disappearing against the ground (case 5):** on a mud-brown test ground the olive hull separates clearly. Pass for the hull; the white identification stripe is on the turret and still to be tested.
- **Detail at game size (case 6):** wear and panel lines blur at 64 px, but the blade, storage box and tracks keep the shape readable. Pass.
- **Color consistency:** before the colour match, mean olive (RGB) by direction was up 73/79/35, up-right 69/74/31, right 67/70/32, down-right 72/79/35, down 81/83/41; the down hull was noticeably brighter. **Resolved** by the color-match edit (see Edits).

## Generations — `CHAR-turret`

Turrets use the shared settings above except for the prompt, the guide and the denoise.

- **Positive prompt (T-01 to T-08):**
  > realistic military tank turret only, oblique top-down view, worn olive drab paint, chipped edges showing bare steel, white identification stripe painted around the turret sides, round commander hatch on top, long straight gun barrel, flat overcast diffuse lighting, game sprite, isolated on plain white background, no shadow, highly detailed

  From the v3 guides on, the barrel phrase became *long straight round cylindrical gun barrel with muzzle opening* and *raised round commander hatch*. For the v3.1 guide (T-09, T-10) the hatch phrase became *(large domed round commander cupola on top:1.3)*.
- **Negative prompt:**
  > hull, tracks, wheels, dozer blade, text, numbers, watermark, people, ground, scenery, cast shadow, blurry, cartoon, toy, bent barrel

  From the v3 guides on, *square barrel* was added.

| # | Direction | Guide | Denoise / seed | Outcome and reason | Edits | Where used |
|---|---|---|---|---|---|---|
| T-01 | down-right | v2 | 0.55 / fixed | **Superseded.** Round barrel and stripe looked good, but the guide still had a box barrel, so other directions came out square. Redone on the v3 guide for consistency. | — | Thumbnail `REJ-06` |
| T-02 | right | v2 | 0.55 / fixed | **Rejected.** Square, flat-ended barrel; does not match the round barrel of T-01. Led to the v3 guide with a round barrel. | — | Thumbnail `REJ-05` |
| T-03 | right | v3 | 0.55 / fixed | **Superseded.** Round barrel and muzzle collar came out, but the hatch was almost gone. Compared with 0.60, which gave a raised cupola. | — | Thumbnail `REJ-07` |
| T-04 | down-right | v3 | 0.60 / fixed | **Accepted, edited.** Raised domed cupola, straight round barrel, stripe partly kept. This comparison set the turret denoise at 0.60. | Stripe; cutout; olive color match | `CHAR-turret_down_right.png` (mirrored for down-left) |
| T-05 | down-right | v3 | 0.75 / fixed | **Rejected.** Most detailed (round turret, mantlet, muzzle brake), but the white stripe disappeared, the turret turned round and no longer followed the guide, and the barrel changed color. Rejected for consistency across directions and player readability. | — | Thumbnail `REJ-08` |
| T-06 | right | v3 | 0.60 / fixed | **Accepted, edited, known issue.** Round barrel with muzzle collar, stripe kept; flat top without a cupola. | Stripe; cutout; olive color match | `CHAR-turret_right.png` (mirrored for left) |
| T-07 | up | v3 | 0.60 / fixed | **Accepted, edited, known issue.** Straight barrel, square turret; flat top with a small hatch, no cupola. | Stripe; cutout; olive color match | `CHAR-turret_up.png` |
| T-08 | up-right | v3 | 0.60 | **Accepted, edited.** Domed cupola. Seen alone, the model drew track-like ribs around the turret edge; on the hull they read as turret-ring detail. Took several attempts; some earlier files under this prefix were actually down-right turrets saved with the wrong prefix. *Exact attempt count and seed to confirm.* | Stripe; cutout; olive color match | `CHAR-turret_up_right.png` (mirrored for up-left) |
| T-09 | down | v3 | 0.60 / fixed | **Rejected.** No cupola, stripe gone, an extra clamp on the barrel. | — | Thumbnail `REJ-09` |
| T-10 | down | v3.1 | 0.60 / fixed | **Rejected.** Even with the larger cupola in the guide, the top came out flat; the barrel clamp came back. | — | Thumbnail `REJ-10` |
| T-11 | down | v3.1 | 0.60 / randomized | **Rejected.** Clear cupola, but the barrel came out light steel, unlike the dark barrel in every other direction. | — | Thumbnail `REJ-11` |
| T-12 | down | v3.1 | 0.60 / randomized | **Accepted, edited.** Clear domed cupola, dark round barrel matching the other directions, visible bore, no clamp. *Seed was randomized and not recorded* (the seed shown in the KSampler after a randomized run is the next seed, not the one used). File `CHAR-turret_down_00009_.png`. | Stripe; cutout; olive color match | `CHAR-turret_down.png` |

*T-04, T-06, T-07 and T-08 assume denoise 0.60 with the fixed seed; confirm against the workflow saved in each PNG.*

### Decisions on the turret

- **Denoise 0.60 for all turrets** (hull stays at 0.55): 0.55 lost the hatch, 0.75 lost the stripe and the guide's shape. 0.60 kept shape, stripe position and barrel while adding a cupola.
- **Round barrel**: chosen from T-01; the v3 guide was redrawn with a round barrel and muzzle so every direction follows it.
- **Stopped re-rolling for the cupola**: after T-12, up and right still have a flat top. At 64 px the difference is about 1–2 px (see `check_final_8dir.png`), so further attempts were not worth the time. Logged as a known issue.

## Checks on the final sprites

- `design/asset-log/check_turret_v3.png`: turrets against the v3 guide outline, on the hull, and at 64 px. Turret outlines match their guides with IoU 0.97–0.98; barrel length and angle hold in all five.
- `design/asset-log/check_stripe_before_after.png`: each turret before and after the stripe edit.
- `design/asset-log/check_final_8dir.png`: hull + turret in all 8 directions (3 mirrored) and at 64 px on mud. The olive matches across hull and turret, the white stripe reads in every direction, and the dozer blade marks the front.

**Known issues:** no cupola on the up and right turrets; small pseudo-text on the right hull and a label plate on the up hull (unreadable at game size); slightly less wear on the down-right hull; a raised wedge on the up-right hull partly shows beside the turret.

## Edits

All edits are made by scripts in `tools/` (written by Claude) from the raw outputs in `assets/raw/`.

1. **Cutout (all 10 sprites):** `tools/cutout_hull.py`. Flood-fills near-white background from the image border, keeps every part larger than 2,000 px (so the separate dozer blade stays), drops VAE edge specks, clears pure-white background trapped between parts, feathers the edge by about 1 px, and removes the white halo on edge pixels.
2. **Identification stripe (5 turrets):** `tools/process_sprites.py`, with masks from `tools/stripe_mask.py` (saved in `design/guides/stripe-mask/`). The model kept the stripe weakly or not at all depending on direction, so the stripe is painted on every turret in off-white `#E8E6DF` exactly where the v3 guide puts it (the barrel still covers it where it should), with the generated shading kept underneath. Result: same position, width and color in every direction.
3. **Olive color match (all 10 sprites):** `tools/process_sprites.py`. One per-channel gain per sprite pulls the mean olive paint to the character-sheet main color `#4B5320`, applied only to olive pixels (weighted by how green they are), so steel, tracks, barrel and stripe are unchanged. Gains stayed within 0.80–1.15 per channel; afterwards every sprite's olive mean is about 73–76 / 80–82 / 31–34.

No pixels of the tank were otherwise repainted.

**Design change:** the character sheet planned a white stripe *and number*. The number was dropped (prompts ask for no numbers), which also removes the mirrored-digit risk in CHANGE-BRIEF case 4.

## Generations — audio

**Workflow:** ComfyUI template "Stable Audio 3.0 Medium Base" with the checkpoint switched to the Small models. `use_reprompt` = false, so the prompt below is exactly what the model received (no Qwen expansion). All settings and seeds below are read from the metadata ComfyUI writes into each FLAC file (the seed shown in the UI after a run is the next seed, not the one used). Sampler: `lcm`, scheduler `simple`, denoise 1.0. Output format FLAC (lossless; the save node offers no WAV).

| # | Asset ID | Model | Steps / cfg | Seed | Duration | Prompt | Outcome and reason | Edits |
|---|---|---|---|---|---|---|---|---|
| A-01 | `SFX-fire` | Small-SFX | 50 / 7.0 | 639358157117823 | 2.0 s | single heavy tank cannon shot, deep low boom with a sharp crack, short metallic ring, close distance, dry outdoor recording, no music | **Rejected.** Seven separate bursts in 2 s, little low end (about 6% below 200 Hz), a noise plateau that never decays, 335 clipped samples. Cause: the template's 50 steps / cfg 7.0 are meant for the Medium model; the post-trained Small model is meant for about 8 steps / cfg 1.0. | — |
| A-02 | `SFX-fire` | Small-SFX | 8 / 1.0 | 262736776156513 | 2.0 s | same as A-01 | **Accepted, edited.** One clean shot, about 77% of the energy below 200 Hz, natural decay to silence. | Trimmed to 1.42 s, 30 ms fade-out, peak −1 dBFS, WAV |
| A-03 | `SFX-cover-hit` | Small-SFX | 8 / 1.0 | 761466301926287 | 1.5 s | shell impact on a brick wall, bricks and stones cracking, crumbling and falling, short burst of debris, close distance, dry outdoor recording, no music | **Accepted, edited.** Single bright crumbling impact, mid and high frequencies, gone within 0.5 s (good for a frequent sound). | Trimmed to 0.95 s, fade, peak −1 dBFS, WAV |
| A-04 | `SFX-player-hit` | Small-SFX | 8 / 1.0 | 133954354425645 | 1.0 s | heavy metal impact on thick steel armor plate, sharp short clang with a dull thud, close distance, dry recording, no music | **Accepted, edited.** Metallic clang with a low thud, even spread across low, mid and high bands, fast decay. | Fade, peak −1 dBFS, WAV (1.12 s) |
| A-05 | `SFX-explode` | Small-SFX | 8 / 1.0 | 49468606960129 | 4.0 s | large tank explosion, deep powerful boom followed by a long rumbling fading tail and falling debris, outdoor, no music | **Accepted, edited, known issue.** Long rumbling tail as asked, but 99% of the energy is below about 320 Hz; no high-frequency debris. | Fade, peak −1 dBFS, WAV (4.09 s) |
| A-06 | `SFX-victory` | Small-Music | 8 / 1.0 | 773409015664764 | 4.0 s | short restrained military victory sting, solemn low brass chord swelling and resolving, single soft snare roll, slow, somber, no vocals | **Accepted, edited.** Low brass and snare in the 80–800 Hz range, swells and dies away within about 2 s; restrained, as the storyboard asks. | Fade, peak −1 dBFS, WAV (4.09 s) |
| A-07 | `MUS-battle-loop` | Small-Music | 8 / 1.0 | 328515072202867 | 45 s | slow tense military ambient loop, 70 BPM, 4/4, low war drums and deep percussion, sustained dark bass drone, sparse low strings, grim and steady, no lead melody, no vocals | **Accepted, edited.** Detected tempo 70 BPM (2-bar phrases repeat every 6.86 s), steady level from 0 to 42 s, fade-out in the last 3 s. | Loop cut (see Edits), OGG Vorbis |

**Known issue (A-02, A-05):** the cannon shot and the explosion are both almost all low frequency, so they sound alike apart from length, and laptop speakers reproduce little below about 200 Hz, so both may be quiet there. Regenerating with "sharp crack / debris / shrapnel" in the prompt was considered and deferred for time.

### Audio edits

- **One-shot sounds (A-02 to A-06):** `tools/process_sfx.py` (written by Claude). Cuts leading silence (keeps 5 ms before the onset), cuts the tail once the level stays below −60 dB relative to the peak, applies a 30 ms fade-out, normalises the peak to −1 dBFS, writes 16-bit 44.1 kHz WAV.
- **Music loop (A-07):** `tools/make_loop.py` (written by Claude). Loop length is exactly 8 bars at 70 BPM (27.429 s). The start point is searched in 5–14 s for the best match between the audio after the start and after the end; best start 13.253 s, end 40.682 s (match score 0.98, before the fade-out). The last 150 ms are blended with the audio that leads into the start point (equal-power crossfade), so the end flows into the start; peak −1 dBFS; OGG Vorbis q6. `assets/audio/music/MUS-battle-loop_3x_preview.ogg` plays the loop three times in a row for the listening check.
- Checks: `design/asset-log/audio/SFX-fire_waveforms.png` (A-01 vs A-02), `SFX_all_waveforms.png` (the four combat sounds and their frequency bands), `MUS-battle-loop_seam.png` (where the loop was cut and the waveform across the loop point).
- **Listening check (to do by me):** play the 3x preview on headphones at least three times and confirm no click or jump at the loop point.


## Who decided

I ran every generation in ComfyUI and made these decisions: turret denoise 0.60 (over 0.55 and 0.75), round barrel over square, re-running the straight turrets for a cupola, picking T-12 for `down`, and stopping before re-rolling `up` and `right`. Claude rendered the guide images and stripe masks, analysed and edited the audio files, wrote the cutout, stripe, color-match and check scripts, ran the checks, and drafted the outcomes and reasons in this log. I reviewed and confirmed the outcomes on: ________.
