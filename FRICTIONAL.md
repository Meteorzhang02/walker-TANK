# FRICTIONAL — walker-TANK

How the design went, in order. **Retrospective note:** this log was put together on 2026-10-05 from my chat with Claude, the settings ComfyUI saved inside each output file, my screenshots and the commits. Claude organized it; the decisions and the reasons quoted are mine from that chat. Asset-log rows are in [ASSET-LOG.md](ASSET-LOG.md).

**Who is who:** *Me* = what I chose, ran, judged or changed. *Claude* = the AI assistant (plans, prompts, code, scripts, guide images, drafts). *Model* = the generative model that made the asset (SDXL Base 1.0, Stable Audio 3 Small).

---

## 2026-10-02 — choosing the game

- **Wanted:** a game I could keep building this semester.
- **Asked:** Claude to compare two ideas I had, a tank battle and a farm fruit-picking game, against the assignment rules.
- **Got:** Claude said the tank game had natural sound events and was easier to keep consistent, but hard to get 10 poses from a vehicle; the farm game had easy poses but no built-in way to fail.
- **Decided:** tank battle. Then I chose: clear all enemy tanks, oblique top-down view, realistic metal look, cover that breaks, a health bar, about 5 minutes per level, all four suggested pillars, one music loop that stops on pause, failure and the end.
- **Human / Claude / model:** I made each choice from options Claude listed. Claude wrote CONCEPT.md from my answers.
- **Trace:** CONCEPT.md; first design commit.

## 2026-10-02 — silhouette test changes the tank

- **Wanted:** the player to see which way the tank faces at game size.
- **Got:** Claude drew a box-model tank in 5 directions. At 64 px, **up and down looked the same**; only the barrel was different.
- **Decided:** I added a **front dozer blade** and a **rear storage box** to the design. The redrawn silhouette shows a wide bar at the front.
- **Human / Claude / model:** I chose the blade and the box. Claude drew the sketches with code (not a generative model).
- **Trace:** CHARACTER-SHEET.md (silhouette section); `design/character/silhouette.png`.

## 2026-10-02 — hull, first try: flat blocks

- **Wanted:** a realistic worn steel hull that keeps the same shape in all 5 directions.
- **Asked:** SDXL Base 1.0 img2img on Claude's box guide (v1), seed 846322750311363, 25 steps, cfg 7.0, prompt "realistic military tank hull without turret, …".
- **Got:** at denoise **0.55** and **0.70**, almost the same flat color blocks as the guide. At **0.80** some panel lines appeared, but **the dozer blade disappeared**.
- **Decided:** rejected all three. The problem was the guide, not the denoise: flat colors with black outlines read as a flat drawing.
- **Next:** Claude redrew the guide (v2) with shading, grain, road wheels and panel lines.
- **Human / Claude / model:** I ran the tests and changed only the denoise each time, so the results could be compared. Claude found the cause and made v2.
- **Trace:** ASSET-LOG G-01 to G-03; thumbnails REJ-01 to REJ-03.

## 2026-10-02 — hull, second try: it works

- **Asked:** same seed and prompt, v2 guide, denoise 0.55 and 0.65.
- **Got:** 0.55 gave worn olive paint, rust, wheels and a segmented blade, **with the shape kept**. 0.65 looked richer but **added a turret dome on the hull**.
- **Decided:** accepted 0.55 for all 5 directions; rejected 0.65 because the turret is a separate sprite, so the tank would have two turrets.
- **Got (5 directions):** all outlines matched the guides (IoU 0.99). The down hull was brighter and the down-right hull less worn.
- **Human / Claude / model:** I ran all 5 and uploaded them. Claude checked them, cut out the backgrounds and drafted the log; I reviewed it.
- **Mistake caught:** Claude's first cutout script dropped the dozer blade on the right hull (it is a separate piece). Found on the check sheet and fixed.
- **Trace:** ASSET-LOG G-04 to G-10; `design/asset-log/check_hull_v2.png`.

## 2026-10-02 — turret: square barrel vs round barrel

- **Got:** with the v2 guide, the right turret had a **square** barrel and the down-right one a **round** barrel.
- **Decided:** I asked to fix this **before** running the other directions. Claude suggested the round barrel (like the down-right one) and I agreed. Claude drew a v3 guide with a round barrel and muzzle.
- **Also:** twice I loaded one guide and saved under another direction's name, so I had to rename files.
- **Trace:** ASSET-LOG T-01, T-02; REJ-05, REJ-06.

## 2026-10-02 — turret denoise: 0.55, 0.60 or 0.75

- **Got:** 0.55 nearly lost the hatch. 0.60 gave a raised domed cupola. 0.75 gave a round turret with a gun mantle and muzzle brake.
- **Decided:** I said "0.60 looks better than 0.55", then "0.75 is even better". Claude pointed out that 0.75 **lost the white stripe**, changed the turret shape and the barrel color. I chose **0.60**.
- **Human / Claude / model:** the first preference (0.75) was mine; Claude raised the problems; the final choice (0.60) was mine.
- **Trace:** ASSET-LOG T-03 to T-05; REJ-07, REJ-08.

## 2026-10-02 to 2026-10-04 — the cupola only appeared on some turrets

- **Got:** at 0.60, the diagonal turrets had a cupola but up, right and down had flat tops. The down turret also lost the stripe and had a clamp on the barrel.
- **Decided:** I chose to **re-run up, right and down until they had a cupola**. Claude made a v3.1 guide with a bigger cupola and a stronger prompt. The stripe would be painted on every turret afterwards so it is the same everywhere.
- **Got:** down was still flat with the same seed. With random seeds one had a cupola but a light barrel. The one I finally kept was made with denoise 0.55 on the v3.1 guide, seed 499619143762383 (these settings are read from the file itself): cupola, dark barrel, no clamp.
- **Decided:** after that I said "never mind, I don't want to keep changing it". Up and right stay flat. At game size the difference is 1–2 px.
- **Still unresolved:** no cupola on up and right; the down turret uses a different denoise and seed.
- **Trace:** ASSET-LOG T-06 to T-12; REJ-09 to REJ-11; `design/asset-log/check_final_8dir.png`.

## 2026-10-04 — stripe and color fixes (edits)

- **Edits:** Claude's script painted the white stripe where the guide puts it on all 5 turrets, and matched the olive of all 10 sprites to the sheet color `#4B5320`.
- **Trace:** ASSET-LOG Edits; `design/asset-log/check_stripe_before_after.png`.

## 2026-10-05 — cannon sound: the template's settings were wrong

- **Wanted:** a deep, heavy cannon shot (pillar: every shot has weight).
- **Asked:** Stable Audio 3 Small-SFX, prompt "single heavy tank cannon shot, deep low boom with a sharp crack, …".
- **Got:** seven noisy bursts in 2 seconds, clipping, no decay. Claude read the settings saved in the FLAC file: 50 steps and cfg 7.0, which the template sets for the bigger Medium model.
- **Next:** I changed the sampler to 8 steps / cfg 1.0. The new shot was one clean low boom that fades out.
- **Trace:** ASSET-LOG A-01, A-02; `design/asset-log/audio/SFX-fire_waveforms.png`.

## 2026-10-05 — other sounds and music

- **Got:** cover hit, YunqiZ hit, victory and the music loop were usable on the first try. Claude checked each one's length, frequency spread and clipping. The music came out at exactly 70 BPM; Claude cut an 8-bar loop and I played the game with it.
- **Decided:** Claude warned that the cannon and the explosion are both almost all low frequency, so they sound alike and may be quiet on laptop speakers. I said "leave it, I'm short on time."
- **Still unresolved:** the cannon and explosion sounds.
- **Trace:** ASSET-LOG A-03 to A-07.

## 2026-10-05 — ground and cover

- **Got:** the three cover stages kept their shapes (IoU 0.96–0.997). The ground came out as bright cobblestones, not mud.
- **Decided:** in a game-size test the cover almost disappeared into the ground. The ground was edited (darker, softer, less contrast) instead of regenerated, to save time.
- **Trace:** ASSET-LOG E-01 to E-04; `design/asset-log/env/check_scene_v1.png` → `check_scene_v2.png`.

## 2026-10-05 — building and playing the slice

- **Human / Claude:** Claude wrote all the Godot code and the automated test. I set up the project, fixed the folder mix-up, reported errors, and played it.
- **Got:** one parse error in `enemy.gd` (fixed). The automated test passes 8/8.
- **My playtest:** no sound or music problems with sound on; readable with sound off. From my screenshots the health bar was hard to see, so it was changed to green / yellow / red.
- **Still unresolved (my notes):** the turret could turn faster, the hull turning could look smoother, and the enemy tanks should look different from YunqiZ.
- **Trace:** TEST-REPORT.md; `design/test/`.
