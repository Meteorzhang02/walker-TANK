# RIFF — gameplay commentary, grounded in run-01

Artifact: `capture/run-01.mp4` (scripted input; not a human playtest). Times are take seconds.

| Interval | Visible observation | Interpretation (source) | Narration (beat) | Next experiment |
|---|---|---|---|---|
| 0–5 s | Hull still, tiny shiver; turret sweeps with cursor | Idle wobble 0.2 px @ 12 rad/s (tank.gd 128) | B15 | Try idle at 1× zoom on a laptop: is the shiver visible? |
| 5–13 s | Eight drive legs; hull sprite changes per facing; enemy hits at 5.1 and 11.9 s | `_slot_for(move_dir)`; SLOT_FLIP mirrors | B15 | Count frames where the hull snaps between facings |
| 13–18 s | Wall cracked at 14.0 s, rubble at 16.8 s | HITS_TO_CRACK/BREAK (cover.gd) | B17 | Is two hits too fast to read the crack while under fire? |
| 18–20.5 s | Explosion, music cut, "respawning", back at spawn | main.gd 257–268 | B21 | Listen: is the explosion tail clear without music? |
| 24.3–27.1 s | Enemy wreck, PAUSED, resume | music position held (log) | B21 | — |
| 30–43 s | Smoke at 50 %, second kill + shake, flames at 25 %, red bar | tank.gd 195–198, main.gd 378 | B19 | Mute and check you can still tell health from the tank alone |
| 43–47 s | Second death and respawn | same as above | B23 | — |
| 47.3–55.6 s | Last kill, victory sting, VICTORY 3/3 0:45 | main.gd 271–280 | B24 (no narration) | Is the sting audible on laptop speakers? |

Hypotheses not tested: whether a human finds the enemies fair (the driver stands in the open on purpose), whether
the low-frequency cannon reads on small speakers, whether the fight is fun. A person must judge those.
