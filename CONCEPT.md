# CONCEPT — walker-TANK

## The game in two sentences

The player commands a lone tank on a ruined battlefield and must destroy every enemy tank on the map. They survive by hiding behind destructible cover and choosing the right moment to leave it and fire.

## Core loop

- **Repeated action:** move between pieces of cover, peek out, aim, and fire at enemy tanks.
- **Decision each time:** which cover to use, when to risk leaving it to take a shot, and when to relocate because the current cover is about to break.
- **Risk:** cover is destroyed by gunfire, so staying hidden too long removes protection; leaving cover exposes the tank to damage. The player has a health bar, and the run fails when it reaches zero.
- **Win condition:** all enemy tanks on the map are destroyed.
- **Target length of a full level:** about 5 minutes. (The Assignment 2 asset slice is a small proof scene, not a full level.)

## Design pillars

| Pillar | Visual or sound choice that honors it |
|---|---|
| **Cold steel battlefield** — a grim, serious, oppressive war mood | Desaturated grey, brown and dark green palette under flat overcast light; low, slow music built on drums and bass. |
| **Cover is not permanent** — nowhere is safe for long; the battlefield gets torn apart | Each cover piece has intact, cracked and broken stages; a stone/brick crumble sound when cover is hit. |
| **Every shot has weight** — firing and hitting should feel heavy | Recoil motion and muzzle flash on the tank when firing; a deep, heavy cannon sound; slight camera shake on impact. |
| **Damage is information** — the tank's appearance tells you how much health is left | The tank visibly changes from intact to smoking to burning as health drops, readable even with sound muted. |

## Art direction

Realistic, metallic style seen from an oblique top-down view (slight 3D depth), because a heavy, worn, physical look serves the grim mood and makes every hit and every damaged surface feel real. Readability at on-screen size comes before surface detail.

Reference notes (in words):

- Worn olive-drab paint with bare steel showing at chipped edges.
- Flat, diffuse overcast light with no strong sunlight.
- A ruined town of mud and broken brick.

## Audio direction

Sound should make the player feel the weight of the machine and the danger of exposure: heavy, low cannon fire, sharp impacts, and crumbling cover. The music is a single low, slow loop that plays throughout play.

- **During play:** the same loop plays continuously without changing.
- **Pause:** music stops.
- **Failure (tank destroyed):** music stops; only the explosion and its fading tail remain.
- **End of the slice / level complete:** music stops.

## Authorship note

Claude proposed the candidate pillars, the visual/sound choices for each pillar, and the reference notes as options. I chose the game, the core mode (clear all enemies), the view, the art style, the cover mechanic, the health bar, the session length, the four pillars, and the music behavior, and accepted the suggested wording.
