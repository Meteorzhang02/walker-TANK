# pitch/ — Assignment 8: final project pitch

Yunqi Zhang · CSYE 7270 · walker-TANK

## The film

- Title: Walker-TANK: One Finished Level
- Length: 3:24 (204.2 s) · 3840×2160, 30 fps
- Link: https://drive.google.com/file/d/1I6AzXCEPSMpIs7GAvjICcg8sZFiCSAtv/view?usp=sharing (Google Drive, anyone with the link can view)
- SHA-256: `32d99d49b3885756d7c14d09198842c15784082cc4c5a403fd01b3583998c9f8`
- Gameplay captured from tag a7, game source 4f88f1b, scripted input, Godot 4.7.2 Movie Maker.
- The mp4 is not in Git. Check a download with `sha256sum` against the hash above.

I watched the whole film myself on 2026-11-24. I found no problems: the narrator speaks as me, only YunqiZ is said to flash red, the comparable is named from memory with no art from it, and every planned item is said with "will" and labelled constructed.

## Files here

| File | What it is |
|---|---|
| PROJECT-BRIEF.md | The seven answers, Exists today and Will exist |
| BUILD-PROMPT.md | The prompt I gave Claude Code in brutalist.art |
| beat_sheet.json | The film's beats, copied from the Brutalist build |
| GATE-REPORT.md | Gate results from the final render |
| SOURCES.md | Tools, voice, game and comparable named in the film |
| FRICTIONAL.md | Dated log of what went wrong and what I changed |

## How the film was made

Brutalist (`show-tell` drawn beats and `godot-waikthrough` gameplay beats in one beat sheet), Kokoro voice am_onyx, local only, no paid API, no upload by the toolkit.
The narrator speaks as me. No instructor name, persona or channel is used.
Drawn beats are labelled "constructed — does not exist yet"; gameplay beats are labelled "REAL CAPTURE · scripted input / tag a7, game source 4f88f1b".

## Gates

All gates passed on the final render: toolkit gates F, L, A, W, B (strict), V (0 blockers, 0 majors) and T; render integrity "ready" and a full decode with no errors; outro, fact check (24 rows), banned-card and walkthrough checks. SHAPE was skipped (finance films only).
Declared, not waived: B01 and B04 are full-frame gameplay, marked full-bleed for Gate V, with contrast checked on their label plaques.
Warnings only: the compiler asks for the stock opener and ClaudeTitleOutro, which hardcode the instructor's persona and channel, so the film uses its own opener and title card.
Known issue: audio is −24.8 LUFS, quieter than the usual −14 for online video; no gate measures loudness, so I left it.
The capture was recorded from a git archive of 3cc29f2, whose game files are identical to 4f88f1b; the a7 tag commit is e4e5d5f.

## What the capture corrected

The brief first said "a hit tank flashes red". The capture showed only YunqiZ flashes red; enemy tanks flash white. I corrected the brief and the narration.
The claim that each shot plays a firing animation was dropped, because I could not confirm it in play.
