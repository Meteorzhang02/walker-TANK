# ASSET-LOG — walker-TANK

One row per generation I kept or seriously considered. Rejected outputs are kept as thumbnails in `design/asset-log/rejected/`.

## Models and tools

| Tool | Version | Where it ran | License / terms |
|---|---|---|---|
| Stable Diffusion XL Base 1.0 (`sd_xl_base_1.0.safetensors`, Stability AI) | 1.0 | Local: Comfy Desktop, ComfyUI v0.38.2, Python 3.13.12, NVIDIA RTX 3060 Laptop GPU (6 GB) | CreativeML Open RAIL++-M (use allowed, with use-based restrictions). *To verify on the model's Hugging Face page.* |
| ComfyUI | v0.38.2 | Local | GPL-3.0 |

**Not generative-model output:** the img2img guide images in `design/guides/` and the cutout script `tools/cutout_hull.py` were written by Claude. They are inputs and edit tools, not generated assets.

## Shared settings

Unless a row says otherwise, every generation below used:

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
| G-06 | `CHAR-hull` right | `guide2_hull_right.png` (v2) | 0.55 | **Accepted, edited.** Outline matches guide (IoU 0.99). Most weathered of the five. Small pseudo-text markings on the deck; unreadable at game size. | Background removed (cutout) | `CHAR-hull_right.png`; panels 2–7 |
| G-07 | `CHAR-hull` up | `guide2_hull_up.png` (v2) | 0.55 | **Accepted, edited.** Outline matches (IoU 0.99). Blade at front, storage box at rear, readable at 64 px. Small label plate on rear; unreadable at game size. | Background removed | `CHAR-hull_up.png` (not mirrored); panels 2–7 |
| G-08 | `CHAR-hull` up-right | `guide2_hull_up-right.png` (v2) | 0.55 | **Accepted, edited, with a note.** Outline matches (IoU 0.99). The model added a raised wedge and a cap-like part on the deck; with the turret on top, part of the wedge still shows beside it. Acceptable for now; candidate for a hand edit. | Background removed | `CHAR-hull_up_right.png` (mirrored at runtime for up-left); panels 2–7 |
| G-09 | `CHAR-hull` down-right | `guide2_hull_down-right.png` (v2) | 0.55 | **Accepted, edited, with a note.** Outline matches (IoU 0.99). Cleaner and less worn than the other four, so wear level is not fully consistent. | Background removed | `CHAR-hull_down_right.png` (mirrored for down-left); panels 2–7 |
| G-10 | `CHAR-hull` down | `guide2_hull_down.png` (v2) | 0.55 | **Accepted, edited, with a note.** Outline matches (IoU 0.99). About 15–20% brighter olive than the right-facing hull. | Background removed | `CHAR-hull_down.png`; panels 2–7 |

*G-06 to G-10 assume the shared settings above with denoise 0.55; confirm against the ComfyUI workflow saved in each PNG.*

## Checks on the accepted hulls

Check sheet: `design/asset-log/check_hull_v2.png` (cutout · guide outline overlay · turret guide on top · 64 px on mud ground with silhouette).

- **Proportion drift (CHANGE-BRIEF case 1):** all five outlines match their guides with IoU 0.991–0.993. Pass.
- **Turret alignment (case 2):** the turret guide placed at the fixed pivot offset sits correctly on all five hulls. Pass, except the extra wedge on up-right (G-08) shows beside the turret.
- **Up/down readability (case 3):** at 64 px the wide blade marks the front in every direction; up and down silhouettes are distinct. Pass.
- **Disappearing against the ground (case 5):** on a mud-brown test ground the olive hull separates clearly. Pass for the hull; the white identification stripe is on the turret and still to be tested.
- **Detail at game size (case 6):** wear and panel lines blur at 64 px, but the blade, storage box and tracks keep the shape readable. Pass.
- **Color consistency:** mean olive (RGB) by direction: up 73/79/35, up-right 69/74/31, right 67/70/32, down-right 72/79/35, down 81/83/41. The down hull is noticeably brighter. Open: a small color match across the five would fix this (would be recorded as an edit).

## Edits

- **Cutout (G-06 to G-10):** `tools/cutout_hull.py` (written by Claude). Flood-fills near-white background from the image border, keeps every part larger than 2,000 px so the separate dozer blade is kept, drops VAE edge specks, clears pure-white background trapped between the blade and the hull, feathers the edge by about 1 px, and removes the white halo on edge pixels. No pixels of the tank were repainted.

## Who decided

Generations were run by me in ComfyUI. Claude rendered the guide images, wrote the cutout and check scripts, ran the checks, and drafted the outcomes and reasons in this log from the check sheet. I reviewed and confirmed the outcomes on: ________.
