extends GPUParticles2D
## Effect B root (CHANGE-BRIEF.md, Effect B): the health -> smoke mapping, observable rule 1.
## Sets only emitting and amount_ratio; every other particle setting lives in
## effects/damage_smoke.tscn. amount is never touched (rule 2: changing it restarts the system).

const THRESHOLD := 0.6
const RATIO_AT_THRESHOLD := 0.25


## health_ratio = health / max_health. A wreck (dead) smokes at full density.
func follow(health_ratio: float, dead: bool) -> void:
	var want := dead or health_ratio <= THRESHOLD
	if dead:
		amount_ratio = 1.0
	elif want:
		var t := clampf((THRESHOLD - health_ratio) / THRESHOLD, 0.0, 1.0)
		amount_ratio = RATIO_AT_THRESHOLD + (1.0 - RATIO_AT_THRESHOLD) * t
	# Assign only on a change, so a further hit never re-sets emitting on a running column.
	if emitting != want:
		emitting = want
