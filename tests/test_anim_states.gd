extends SceneTree
## A7 state-machine tests: motion machine, weapon machine, interrupts, authority, two-clocks measurement.
## Drives the real scenes/main.tscn through the real loop. Moving and firing go only through
## Input.parse_input_event; take_damage() is called for hit and death cases (as test_hit_flash.gd does).
## Run: bash scripts/run-test.sh test_anim_states.gd 60     (also 30, 144)
##
## Tick convention. The script resumes on physics_frame at the start of tick k, before the nodes
## run tick k; a snapshot taken at resume k shows the result of tick k-1. Input injected at resume 0
## reaches the game some ticks later: 1 tick at --fixed-fps 60 and 144 (test_pins PIN-0), 2 ticks at
## --fixed-fps 30 (two physics ticks per frame, input is flushed once per frame). So the latency is
## not assumed: the press tick P of each scenario is the first tick the game acted on the injected
## action (first FIRING for fire, first non-zero move_dir for a move), and rel = tick - P.
## A call scheduled for rel r is made at the resume just before tick P + r runs.
## The expected numbers below (shell on tick 2, READY on tick 10) are the brief's, written out here
## on purpose and not read from tank.gd.

const HOLD := 20           # action held from resume 0, released at resume HOLD (less than the 48-tick reload)
const TOTAL := 34
const SHELL_REL := 2       # brief: shell, muzzle FX and fire sound on physics tick 2 after the press
const READY_REL := 10      # brief: weapon back to READY on physics tick 10 after the press
const CLOCK_RUNS := 5

var passed := 0
var failed := 0
var shell_script: Script


func _initialize() -> void:
	_run.call_deferred()


func _check(label: String, ok: bool, detail: String = "") -> void:
	print("%s  %s%s" % ["PASS" if ok else "FAIL", label, ("  | " + detail) if detail != "" else ""])
	if ok:
		passed += 1
	else:
		failed += 1


func _info(text: String) -> void:
	print("INFO  " + text)


func _inject(action: String, pressed: bool) -> void:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = pressed
	ev.strength = 1.0
	Input.parse_input_event(ev)


func _new_game() -> Node:
	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await physics_frame
	for e in main.enemies:
		e.target = null          # still and silent, still in physics
	for i in 5:
		await physics_frame
	return main


func _free_game(main: Node) -> void:
	main.queue_free()
	await process_frame
	await physics_frame


## Runs one scenario and returns one snapshot per resume. opts: move, fire, force_reload0,
## actions {rel: Callable} (rel counted from the press tick P, see the header).
func _scenario(main: Node, opts: Dictionary) -> Array:
	var anchor_fire: bool = opts.get("fire", false)
	var press_tick := -1         # absolute tick index of P, known once its snapshot is seen
	var p = main.player
	var audio = main.audio
	var fire_anim: AnimationPlayer = p.get_node("FireAnim")
	var motion_anim: AnimationPlayer = p.get_node("MotionAnim")
	var dust_mount: Node2D = p.get_node("DustMount")
	var shell_ids := []
	var muzzle_ids := []
	var sounds0: int = audio.count("fire")
	var snaps := []
	for k in TOTAL:
		await physics_frame
		for n in main.fx_layer.get_children():
			var id: int = n.get_instance_id()
			if n.get_script() == shell_script and not shell_ids.has(id):
				shell_ids.append(id)
			elif n is CPUParticles2D and not muzzle_ids.has(id):
				muzzle_ids.append(id)
		if press_tick < 0 and k > 0:
			var acted: bool = (p._weapon == p.Weapon.FIRING) if anchor_fire else (p.move_dir != Vector2.ZERO)
			if acted:
				press_tick = k - 1
		snaps.append({
			"k": k, "tick": k - 1, "move_dir": p.move_dir,
			"shells": shell_ids.size(), "muzzles": muzzle_ids.size(),
			"sounds": audio.count("fire") - sounds0,
			"weapon": p._weapon, "motion": p._motion,
			"fire_clip": fire_anim.current_animation, "fire_playing": fire_anim.is_playing(),
			"fire_pos": fire_anim.current_animation_position if fire_anim.is_playing() else -1.0,
			"move_clip": motion_anim.current_animation, "move_playing": motion_anim.is_playing(),
			"dust_visible": dust_mount.visible, "dead": p.is_dead, "health": p.health,
			"reload_full": is_equal_approx(p.reload_left, p.reload_time), "reload_zero": p.reload_left == 0.0,
		})
		if k == 0:
			if opts.get("move", false):
				_inject("move_right", true)
			if opts.get("fire", false):
				_inject("fire", true)
		elif k == HOLD:
			if opts.get("move", false):
				_inject("move_right", false)
			if opts.get("fire", false):
				_inject("fire", false)
		if opts.get("force_reload0", false) and k > 0:
			p.reload_left = 0.0   # isolates the FIRING guard from the reload timer
		# Resume k runs just before tick k, i.e. rel k - P.
		if press_tick >= 0 and opts.has("actions") and opts["actions"].has(k - press_tick):
			opts["actions"][k - press_tick].call()
	for s in snaps:
		s["rel"] = s["tick"] - press_tick if press_tick >= 0 else -999
	_info("  scenario %s: press tick P seen %d tick(s) after the injection" % [
		str(opts.keys().filter(func(x): return x != "actions")), press_tick])
	return snaps


func _first(snaps: Array, key: String, value, from_rel: int = -99) -> int:
	for s in snaps:
		if s["rel"] >= from_rel and s[key] == value:
			return s["rel"]
	return -999


## Relative ticks at which the cumulative count of `key` rose.
func _rises(snaps: Array, key: String) -> Array:
	var out := []
	var prev := 0
	for s in snaps:
		for i in s[key] - prev:
			out.append(s["rel"])
		prev = s[key]
	return out


func _all(snaps: Array, from_rel: int, to_rel: int, key: String, value) -> bool:
	for s in snaps:
		if s["rel"] >= from_rel and s["rel"] <= to_rel and s[key] != value:
			return false
	return true


func _run() -> void:
	shell_script = load("res://scripts/shell.gd")
	var Tank = load("res://scripts/tank.gd")
	var FIRING: int = Tank.Weapon.FIRING
	var READY: int = Tank.Weapon.READY
	var MOVING: int = Tank.Motion.MOVING
	var IDLE: int = Tank.Motion.IDLE
	_info("physics ticks per second = %d, max_fps = %d" % [Engine.physics_ticks_per_second, Engine.max_fps])

	# ---- 1. Structure: nodes, clips, autoplay, for the player and every enemy ----
	var main = await _new_game()
	var p = main.player
	var tanks: Array = [p]
	tanks.append_array(main.enemies)
	var structure_ok := true
	var detail := ""
	for t in tanks:
		var motion_anim = t.get_node_or_null("MotionAnim")
		var fire_anim = t.get_node_or_null("FireAnim")
		if motion_anim == null or fire_anim == null or t.get_node_or_null("Suspension") == null \
				or t.get_node_or_null("DustMount/Dust") == null:
			structure_ok = false
			detail += " %s: missing node;" % t.name
			continue
		if not motion_anim.has_animation("track_dust") or not fire_anim.has_animation("shoot"):
			structure_ok = false
			detail += " %s: clip missing;" % t.name
		if motion_anim.autoplay != "" or fire_anim.autoplay != "":
			structure_ok = false
			detail += " %s: autoplay set;" % t.name
		if motion_anim.is_playing() or fire_anim.is_playing():
			structure_ok = false
			detail += " %s: playing at start;" % t.name
		if t.get_node("DustMount").visible or t._motion != IDLE or t._weapon != READY:
			structure_ok = false
			detail += " %s: not idle/ready at start;" % t.name
	_check("S1 player and %d enemies have Suspension, DustMount/Dust, both players with their clip, autoplay empty, idle at start" % main.enemies.size(),
		structure_ok, detail)
	_check("S1b hull and turret are children of Suspension", p.hull.get_parent() == p.get_node("Suspension") and p.turret.get_parent() == p.get_node("Suspension"))
	await _free_game(main)

	# ---- 2. Motion machine ----
	main = await _new_game()
	var snaps: Array = await _scenario(main, {"move": true})
	var first_move: int = -999
	var first_idle_after: int = -999
	var dir_on: int = -999
	var dir_off: int = -999
	for s in snaps:
		if first_move == -999 and s["motion"] == MOVING:
			first_move = s["k"]
		if first_move != -999 and first_idle_after == -999 and s["motion"] == IDLE:
			first_idle_after = s["k"]
		if dir_on == -999 and s["move_dir"] != Vector2.ZERO:
			dir_on = s["k"]
		if dir_on != -999 and dir_off == -999 and s["move_dir"] == Vector2.ZERO:
			dir_off = s["k"]
	_check("M1 IDLE at rest before the press (every tick before move_dir turns non-zero)", _all(snaps, -99, -1, "motion", IDLE) and _all(snaps, -99, -1, "dust_visible", false) and _all(snaps, -99, -1, "move_playing", false))
	_check("M2 MOVING on the same tick move_dir turns non-zero", first_move == dir_on and dir_on > 0, "motion=%d move_dir=%d" % [first_move, dir_on])
	var moving_ok := true
	for s in snaps:
		if s["k"] >= first_move and s["k"] < first_idle_after:
			if not (s["move_playing"] and s["move_clip"] == "track_dust" and s["dust_visible"] and s["motion"] == MOVING):
				moving_ok = false
	_check("M3 while MOVING: track_dust playing every tick and dust visible", moving_ok)
	_check("M4 back to IDLE on the same tick move_dir returns to zero (release injected at resume %d)" % HOLD, first_idle_after == dir_off and dir_off > HOLD, "motion=%d move_dir=%d" % [first_idle_after, dir_off])
	var idle_ok := true
	for s in snaps:
		if s["k"] >= first_idle_after and (s["move_playing"] or s["dust_visible"] or s["motion"] != IDLE):
			idle_ok = false
	_check("M5 after release: MotionAnim stopped, dust hidden", idle_ok)
	_check("M6 FireAnim never ran during a pure move", _all(snaps, -99, 99, "fire_playing", false) and _all(snaps, -99, 99, "weapon", READY))
	await _free_game(main)

	# ---- 3. Weapon machine at rest, fire held ----
	main = await _new_game()
	snaps = await _scenario(main, {"fire": true})
	var shell_rises := _rises(snaps, "shells")
	var sound_rises := _rises(snaps, "sounds")
	var muzzle_rises := _rises(snaps, "muzzles")
	_check("W1 press tick (first FIRING): reload starts on it (0.8 s) and not before; shoot starts on it",
		_first(snaps, "reload_full", true) == 0 and _all(snaps, -99, -1, "reload_zero", true) and _first(snaps, "fire_clip", "shoot") == 0,
		"reload first=%d shoot first=%d" % [_first(snaps, "reload_full", true), _first(snaps, "fire_clip", "shoot")])
	_check("W2 no shell, muzzle FX or fire sound on ticks 0 and 1", _all(snaps, 0, SHELL_REL - 1, "shells", 0) and _all(snaps, 0, SHELL_REL - 1, "muzzles", 0) and _all(snaps, 0, SHELL_REL - 1, "sounds", 0))
	_check("W3 shell appears on tick 2 and only once", shell_rises.slice(0, 2) == [SHELL_REL] and _all(snaps, SHELL_REL, READY_REL + 5, "shells", 1), str(shell_rises))
	_check("W4 fire sound appears on tick 2, once", sound_rises == [SHELL_REL], str(sound_rises))
	_check("W5 muzzle FX appears on tick 2", muzzle_rises.size() > 0 and muzzle_rises[0] == SHELL_REL, str(muzzle_rises))
	_check("W6 weapon FIRING through tick 9", _all(snaps, 0, READY_REL - 1, "weapon", FIRING))
	_check("W7 weapon back to READY on tick 10", _first(snaps, "weapon", READY, 3) == READY_REL, "first=%d" % _first(snaps, "weapon", READY, 3))
	_check("W8 FireAnim plays shoot on ticks 0-8", _all(snaps, 0, 8, "fire_clip", "shoot") and _all(snaps, 0, 8, "fire_playing", true))
	_check("W9 FireAnim finished by tick 11", _all(snaps, 11, 99, "fire_playing", false))
	_check("W10 MotionAnim idle and dust hidden the whole time (no movement)", _all(snaps, -99, 99, "move_playing", false) and _all(snaps, -99, 99, "dust_visible", false))
	_check("W11 no second shell while held through the 48-tick reload (only the held-fire ticks seen)", shell_rises.size() == 1, str(shell_rises))
	await _free_game(main)

	# ---- 4. FIRING guard: reload forced to 0 every tick, fire held ----
	main = await _new_game()
	snaps = await _scenario(main, {"fire": true, "force_reload0": true})
	shell_rises = _rises(snaps, "shells")
	var pos_monotonic := true
	var prev_pos := -1.0
	for s in snaps:
		if s["rel"] >= 0 and s["rel"] <= 8:
			if s["fire_pos"] < prev_pos:
				pos_monotonic = false
			prev_pos = s["fire_pos"]
	_check("G1 reload at 0 every tick: shells on ticks [2, 12] only (a press during FIRING is ignored, the second shot starts on READY)", shell_rises.slice(0, 2) == [SHELL_REL, READY_REL + SHELL_REL] and shell_rises.size() == 2, str(shell_rises))
	_check("G2 shoot never restarted during FIRING (position non-decreasing on ticks 0-8)", pos_monotonic)
	_check("G3 weapon FIRING on every tick 0-19 (back-to-back shots)", _all(snaps, 0, 19, "weapon", FIRING))
	await _free_game(main)

	# ---- 5. Fire while moving ----
	main = await _new_game()
	snaps = await _scenario(main, {"fire": true, "move": true})
	var mf_ok := true
	for s in snaps:
		if s["rel"] >= 0 and s["k"] <= HOLD:
			if not (s["move_playing"] and s["move_clip"] == "track_dust" and s["dust_visible"]):
				mf_ok = false
	_check("F1 firing while driving: track_dust keeps playing and the dust stays visible", mf_ok)
	_check("F2 shell still on tick 2 while moving", _rises(snaps, "shells").slice(0, 1) == [SHELL_REL], str(_rises(snaps, "shells")))
	await _free_game(main)

	# ---- 6. Interrupts: hit and death in startup, active, recovery ----
	for case in [["startup", 1], ["active", 2], ["recovery", 5]]:
		var label: String = case[0]
		var r: int = case[1]
		main = await _new_game()
		var pl = main.player
		snaps = await _scenario(main, {"fire": true, "actions": {r: func(): pl.take_damage(10)}})
		_check("H-%s hit on tick %d: shot continues (shell tick 2, FIRING to tick 9, READY tick 10)" % [label, r],
			snaps[-1]["health"] < snaps[0]["health"] and not snaps[-1]["dead"] \
				and _rises(snaps, "shells").slice(0, 1) == [SHELL_REL] and _all(snaps, 0, READY_REL - 1, "weapon", FIRING) and _first(snaps, "weapon", READY, 3) == READY_REL,
			"health %d->%d shells=%s ready=%d" % [snaps[0]["health"], snaps[-1]["health"], str(_rises(snaps, "shells")), _first(snaps, "weapon", READY, 3)])
		await _free_game(main)

		main = await _new_game()
		pl = main.player
		snaps = await _scenario(main, {"fire": true, "actions": {r: func(): pl.take_damage(100000)}})
		var dead_seen: bool = snaps[-1]["dead"]
		_check("D-%s death on tick %d: shell still on tick 2 (once), sound once, FIRING to tick 9, READY tick 10" % [label, r],
			dead_seen and _rises(snaps, "shells") == [SHELL_REL] and _rises(snaps, "sounds") == [SHELL_REL] and _all(snaps, 0, READY_REL - 1, "weapon", FIRING) and _first(snaps, "weapon", READY, 3) == READY_REL,
			"dead=%s shells=%s sounds=%s ready=%d" % [str(dead_seen), str(_rises(snaps, "shells")), str(_rises(snaps, "sounds")), _first(snaps, "weapon", READY, 3)])
		await _free_game(main)

	# ---- 7. Death while moving: leaves MOVING, dust hidden ----
	main = await _new_game()
	var pl2 = main.player
	var r_kill := 8              # killed just before rel tick 8 of the drive
	snaps = await _scenario(main, {"move": true, "actions": {r_kill: func(): pl2.take_damage(100000)}})
	var s_before: Dictionary = snaps.filter(func(s): return s["rel"] == r_kill - 1)[0]
	var s_after: Dictionary = snaps.filter(func(s): return s["rel"] == r_kill)[0]
	_check("X1 before the kill: MOVING, dust visible, track_dust playing", s_before["motion"] == MOVING and s_before["dust_visible"] and s_before["move_playing"])
	var after_ok := true
	for s in snaps:
		if s["rel"] >= r_kill and (s["motion"] != IDLE or s["dust_visible"] or s["move_playing"]):
			after_ok = false
	_check("X2 on the tick of death: IDLE, dust hidden, MotionAnim stopped, stays so (move_right still held)", s_after["dead"] and after_ok)
	await _free_game(main)

	# ---- 8. Two clocks: FireAnim position against the tick the shell spawns on ----
	_info("two-clocks: FireAnim.current_animation_position after each tick, press tick = rel 0; frame 1 = %.4f s" % (1.0 / 30.0))
	var diffs := []
	for run in CLOCK_RUNS:
		main = await _new_game()
		snaps = await _scenario(main, {"fire": true})
		var anim_rel := -999
		var line := ""
		for s in snaps:
			if s["rel"] >= 0 and s["rel"] <= 6:
				line += " rel%d=%.4f" % [s["rel"], s["fire_pos"]]
			if anim_rel == -999 and s["rel"] >= 0 and s["fire_pos"] >= 1.0 / 30.0 - 0.0001:
				anim_rel = s["rel"]
		var shell_rel2: int = _rises(snaps, "shells")[0] if _rises(snaps, "shells").size() > 0 else -999
		var diff: int = shell_rel2 - anim_rel
		diffs.append(diff)
		_info("run %d:%s | animation reaches frame 1 at rel %d, shell at rel %d, shell - anim = %d tick(s)" % [run, line, anim_rel, shell_rel2, diff])
		await _free_game(main)
	var worst := 0
	for d in diffs:
		worst = maxi(worst, absi(d))
	_info("CLOCKS physics_ticks_per_second=%d: largest |shell tick - animation frame-1 tick| over %d runs = %d tick(s) = %.4f s; per run %s" % [
		Engine.physics_ticks_per_second, CLOCK_RUNS, worst, worst / float(Engine.physics_ticks_per_second), str(diffs)])
	_check("C1 two-clocks disagreement <= 1 physics tick (brief prediction)", worst <= 1, "worst=%d" % worst)
	_check("C2 the same number in every run", diffs.count(diffs[0]) == diffs.size(), str(diffs))

	print("RESULT: %d passed, %d failed" % [passed, failed])
	quit(1 if failed > 0 else 0)
