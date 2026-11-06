extends SceneTree
## Probe, not a PASS/FAIL test: asks this Godot build which particle properties and signals exist.
## Written by Claude (chat) for Assignment 6, run by me through scripts/run-test.sh.

func _init() -> void:
	var checks := {
		"CPUParticles2D": ["amount_ratio", "use_fixed_seed", "seed", "initial_velocity_min", "scale_amount_min", "scale_amount_curve", "damping_min", "gravity", "initial_velocity", "scale_amount", "scale_amount_random"],
		"GPUParticles2D": ["amount_ratio", "use_fixed_seed", "seed", "visibility_rect", "preprocess", "local_coords", "process_material", "texture"],
		"ParticleProcessMaterial": ["turbulence_enabled", "turbulence_noise_strength", "turbulence_noise_scale", "turbulence_influence_min", "turbulence_influence_max", "scale_min", "scale_curve", "color_ramp", "angle_min", "damping_min", "gravity", "particle_flag_disable_z", "initial_velocity_min", "initial_velocity"],
	}
	for cls in checks:
		var names := {}
		for p in ClassDB.class_get_property_list(cls):
			names[p.name] = true
		for n in checks[cls]:
			print("PROBE %s.%s: %s" % [cls, n, "yes" if names.has(n) else "NO"])
	for cls in ["CPUParticles2D", "GPUParticles2D"]:
		print("PROBE %s signal finished: %s" % [cls, "yes" if ClassDB.class_has_signal(cls, "finished") else "NO"])
	print("PROBE ParticlesMaterial class exists: %s" % ("yes" if ClassDB.class_exists("ParticlesMaterial") else "NO"))
	quit(0)
