# SOURCES — walker-TANK

## What the project started from

An **empty Godot 4 project**. No code or assets were copied from walker-jumpman or from my Assignment 1 project; only the `walker-` naming convention is reused. The full asset log, with every prompt, seed and setting, is in **[ASSET-LOG.md](ASSET-LOG.md)**; rejected-output thumbnails are in `design/asset-log/rejected/`.

## Generative models (assets)

| Model | Used for | Where it ran | Terms |
|---|---|---|---|
| Stable Diffusion XL Base 1.0 (`sd_xl_base_1.0.safetensors`, Stability AI) | YunqiZ hull and turret sprites (img2img), cover (img2img), ground (text-to-image) | Local: Comfy Desktop, ComfyUI v0.38.2, NVIDIA RTX 3060 Laptop GPU (6 GB) | CreativeML Open RAIL++-M |
| Stable Audio 3 Small-SFX (`stable_audio_3_small_sfx.safetensors`, Stability AI; ComfyUI repackage `Comfy-Org/stable-audio-3`) | SFX-fire, SFX-cover-hit, SFX-player-hit, SFX-explode | Local, same machine | Stability AI Community License; T5Gemma text encoder under the Gemma Terms of Use. Training data: licensed AudioSparx and CC-licensed Freesound audio. |
| Stable Audio 3 Small-Music (`stable_audio_3_small_music.safetensors`) | SFX-victory, MUS-battle-loop | Local, same machine | As above |

No paid generation services were used. No artist names, brands, copyrighted characters or existing music were used in prompts or as references.

## AI assistant (not a generative-model asset source)

**Claude (Anthropic), in claude.ai.** What it contributed:

- **Design documents:** proposed options and drafted wording for CONCEPT, CHARACTER-SHEET, STORYBOARD and CHANGE-BRIEF from my choices; each document ends with an authorship note.
- **Code-drawn images (not generated assets):** planning sketches in `design/character/` and `design/storyboard/`, and every img2img guide image in `design/guides/` (v1, v2, v3, v3.1, cover) and the stripe masks.
- **Prompts:** drafted every image and audio prompt; I ran them and chose results.
- **Edit and check scripts in `tools/`:** cutout, stripe painting, olive color match, ground calming and tiling, audio trimming, loop cutting, analysis, and resizing to game textures.
- **Game code:** wrote all GDScript in `scripts/` and the automated test in `tests/`, and fixed the errors I reported from Godot.
- **Logs and reports:** drafted ASSET-LOG, TEST-REPORT, SOURCES and README from the real files, metadata and my reports.
- **Film:** built by **Claude Code** with the course-provided **Brutalist** toolkit (`godot-gamedev` skill, `walker` mode): gameplay capture, narration script, local Kokoro `am_onyx` voice (no paid TTS), Remotion render. Its records are in `youtube/claude-liam-walker-tank-gamedev/`. One shared toolkit template was edited locally (footer 3 px) with my approval; see FRICTIONAL.

## What I did

- I picked the game (tank battle), how it plays, the look, the four pillars, the tank's name and its dozer blade and storage box, and how big the slice should be.
- I installed ComfyUI and ran every image and sound generation myself on my laptop.
- I looked at every result and decided what to keep or throw away, for example: turret denoise 0.60 instead of 0.55 or 0.75, a round barrel, re-running turrets to get a cupola and then stopping, keeping the cannon and explosion sounds, and editing the ground instead of making a new one.
- I set up the Godot project, reported the errors, played the game with sound on and with sound off, took all the screenshots, and ran the automated test.
- I read and checked these documents.

## Tools

| Tool | Version | Use | License |
|---|---|---|---|
| Godot Engine | 4.7.2 stable (official) | Game engine | MIT |
| Comfy Desktop / ComfyUI | ComfyUI v0.38.2 | Running the generative models locally | GPL-3.0 |
| FFmpeg | system build in Claude's sandbox | Decoding FLAC, writing WAV and OGG | LGPL/GPL |
| Python with NumPy, SciPy, Pillow; Chromium (Playwright) | in Claude's sandbox | Edit scripts; rendering the SVG guides to PNG | BSD / MIT-style |
| Git, GitHub | — | Version control | — |

**Code-made effects (not generated assets):** muzzle flash, shell trails, impact, debris, explosion, smoke and fire are Godot `CPUParticles2D` in `scripts/main.gd` and `scripts/tank.gd`; the hit flash, recoil and track wobble are code. Enemy tanks reuse the YunqiZ sprites with a grey tint in code.

**Fonts and UI:** Godot's default theme and font.

## Collaborators

None.
