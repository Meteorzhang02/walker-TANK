# SOURCES — walker-TANK

## Assignment 3 — 3D assets

**Starting point:** my own walker-TANK repository from Assignment 2 (tag/commit submitted for A2). Assignment 3 adds a 3D asset room; the 2D game is unchanged.

**Tools and versions**

- Blender 5.2.2 LTS (blender.org), Windows 11.
- MCP for Blender, the community project named in the syllabus: Python server run with `uvx mcp-for-blender`, Blender add-on 1.8 (protocol 13). Its asset libraries (Poly Haven, Sketchfab, Poly Pizza) and generators (Hyper3D Rodin, Hunyuan3D, Tripo) were **off** throughout; `generate_3d`, `search_assets`, `import_asset` and `record_trajectory_feedback` are denied in `.claude/settings.json`.
- uv 0.13.0 (Astral), installed with its PowerShell installer.
- Claude Code 2.1.292, auto-updated to 2.1.299 during the work; model Opus 5.5, through my Northeastern access.
- Godot 4.7.2 stable (Windows build).
- Git for Windows' Git Bash, including GNU coreutils `timeout` 8.32, used for the headless time limit.

**Assets:** all three assets (cover_wall, ammo_crate, tank_hedgehog) were built from Blender cubes by code that Claude ran through the MCP at my direction, plus one hand edit of my own on cover_wall. No downloaded, purchased or AI-generated models, textures or materials were used.

**Colours:** flat Principled BSDF base colours chosen in the brief. The olive `#4B5320` and off-white `#E8E6DF` reuse the palette of my Assignment 2 character sheet; the brick and steel colours were proposed by Claude in the brief and accepted by me.

**What AI contributed and what I decided**

- *Brief:* Claude proposed the three assets, the tank reference size, all dimensions, colours, budgets and failure cases at my request; I accepted them. The hedgehog revision (2.4 m → 2.125 m beams) was my choice; Claude computed the evidence and recommended a different fix, which I rejected.
- *Blender code:* Claude wrote and ran all build code (`tools/blender/build_*.py`) and the exporter (`tools/blender/export_glb.py`). I read each `execute_blender_code` call before approving it (except a few that ran in auto mode before I noticed; see FRICTIONAL.md), decided the join and save questions, accepted the 0.83 m stripe, and made the hand edit on cover_wall myself.
- *Godot:* Claude wrote `scenes/asset_room_3d.tscn` and `tests/check_a3_assets.gd`. I asked for the FAIL path to be proved and did the visual checks in the Godot editor myself.
- *Documents:* Claude drafted BLENDER-NOTES.md, CHANGE-BRIEF.md, TEST-REPORT.md and the A3 part of FRICTIONAL.md from my screenshots and terminal output; I checked them against what happened and corrected them.
- *Film:* [to add after the film is made: script, beat sheet, visuals, narration voice]

**Collaborators:** none.

---

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
