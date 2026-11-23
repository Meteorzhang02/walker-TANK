# BUILD-PROMPT — A8 final project pitch film

The prompt I gave Claude Code in D:/CSYE7270/brutalist.art, written with help from Claude chat.

---

Build a 2 to 4 minute pitch film for my final project, CSYE 7270 Assignment 8.

## Sources

- The brief is D:/CSYE7270/assignment2/walker-TANK/pitch/PROJECT-BRIEF.md. Every claim in the film must come from it. Do not add claims.
- The game is D:/CSYE7270/assignment2/walker-TANK, Godot 4.7.2 at D:/CSYE7270/Godot_v4.7.2-stable_win64.exe/Godot_v4.7.2-stable_win64_console.exe. Game source is unchanged since 4f88f1b (tag a7).
- Capture from a scratch copy made with `git archive HEAD`, as in the A7 film. Do not change the game repo.

## Builders

Use the `show-tell` builder for the pitch beats and real gameplay captures from `godot-waikthrough` (walker mode) for the beats that show what exists today.
Before building, tell me in two or three lines whether one film can mix these two. If it cannot, use `godot-waikthrough` with drawn beats where the brief needs them, and say which.

## Voice and identity (graded)

- Kokoro local voice; no paid API; no upload.
- The narrator speaks as me, Yunqi Zhang, a CSYE 7270 student, in the first person.
- Do not use the instructor's name, persona, channel or credit line anywhere: no "Bear", no "in for Bear", no "@NikBearBrown", no `in_for_bear: true`. Set greeting, persona, presenter, channel and credit fields to me or leave them empty.
- No other game's logo, icon, screenshot or art. *全民坦克大战* is named in narration only.

## Honesty rules (graded)

- What exists today is said in the past or present tense and shown with real capture, each capture labelled with its revision.
- What does not exist yet is said with "will" and drawn, each drawing labelled "constructed — does not exist yet".
- Do not claim a firing animation plays in the main game; I have not confirmed it.
- *全民坦克大战* features are from my memory; the narration says "as I remember it".
- Every number names its machine: the a6 GPU costs (+0.023 ms, +0.077 ms) were measured on an NVIDIA RTX 3060 Laptop GPU.
- No player quotes, no players, sales, market or reviewer claims.

## Beats (about 11, about 15 seconds each)

1. Who I am and what this film is: a pitch for my final project.
2. Q1, what it is: walker-TANK now. Real capture: YunqiZ driving among brick cover and enemy tanks.
3. Q1, finished form: title screen, one level, win or lose screen, a Windows build. Constructed.
4. Q2, the comparable: *全民坦克大战* on 7k7k, 2D; as I remember it, cover did not break, firing had no effect, a destroyed tank did not smoke. Drawn, no art from that game, labelled "from memory".
5. Q2, walker-TANK's answer. Real capture: a shell hits brick cover and debris bursts from the hit point; a hit tank flashes red; a damaged tank smokes; a wreck keeps smoking.
6. Q3, who and the first sixty seconds: a hiring manager for a gameplay programmer unzips, double-clicks, sees controls, plays within a minute. Constructed.
7. Q4, what it proves: shaders (a5), particles (a6), animation and state tests (a7), profiling (a6, RTX 3060 Laptop), test habits. Show the real files and test output.
8. Q5, in, out, first: in and out lists; first is an exported .exe played to a win from a clean folder, recorded in TEST-REPORT.md.
9. Q6, the risk: never exported; tested on one RTX 3060 machine; Forward+ needs Vulkan or Direct3D 12; fallback is the Compatibility renderer with each effect rechecked; web export not chosen.
10. Q7, why: skills shown with evidence versus skills new to me (export, running on a machine I do not control, finishing a full loop).
11. Close: exists today versus will exist, spoken outro.

## Output

- Film folder: walker-TANK/youtube/walker-tank-a8-pitch/. The mp4 stays out of Git.
- Run every quality gate, including render integrity. Do not hand me a film that fails a gate; fix and rerender, and tell me what failed.
- Copy beat_sheet.json and the gate report into walker-TANK/pitch/.
- Tell me the mp4 path, its length, its SHA-256, the capture revision, and each gate result.
