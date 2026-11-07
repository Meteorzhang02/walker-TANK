extends SceneTree
## Effect B state test (CHANGE-BRIEF.md, Effect B, "Observable rules" and "The evidence split").
## Health changes only through the real game loop: real shells (YunqiZ's real Space input, or
## main.spawn_shell() as the game does) hitting real tanks, and main.gd's own respawn timer.
## Never calls follow(), take_damage(), die() or reset_full(), and never writes health.
## Run: bash scripts/run-test.sh test_damage_smoke_state.gd 60
##
## Test setup writes only (each labelled where it happens): the enemy AI is frozen (as in
## test_cover_hit_burst_state.gd), enemy 0 is moved into YunqiZ's line of fire and processes again
## with target = null (so its invulnerability timer runs but its AI holds still), and YunqiZ's
## smoke is hidden and shown again (rule 6).
##
## What this proves: the smoke node's state (type, scene, parent, position, emitting, amount_ratio,
## amount, can_process) follows health through the real game. What it cannot prove: anything drawn.
## Headless uses a dummy renderer that runs no GPU particle process, so whether particles are emitted,
## thinned by amount_ratio, fade after a stop, freeze on screen or vanish when hidden is a human check.

const SCENE := "res://effects/damage_smoke.tscn"
const GALLERY := "res://scenes/gallery.tscn"
const RATIO_EPS := 0.001
const AMOUNT := 48

var failures := 0
var passes := 0
var main
var p
var e0
var tanks := []
var smoke_ids := {}     # tank -> smoke instance id at load
var last_emitting := {} # tank -> smoke.emitting at the end of the previous step
var events := []        # one Dictionary per damaged / destroyed signal
var fired := 0
var _frame := 0
var _r2_frames := 0
var _r2_bad := {}


func _initialize() -> void:
	_run.call_deferred()


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if ok:
		passes += 1
	else:
		failures += 1


func _secs(frames: int) -> float:
	return float(frames) / float(Engine.physics_ticks_per_second)


func _ratio_for(h: float) -> float:
	# The brief's rule 1 formula, written out here so the test does not read it from the effect.
	return 0.25 + 0.75 * (0.6 - h) / 0.6


func _step() -> void:
	await physics_frame
	_frame += 1
	_watch()


func _physics_frames(n: int) -> void:
	for i in n:
		await _step()


func _wait_until(cond: Callable, max_frames: int) -> bool:
	for i in max_frames:
		if cond.call():
			return true
		await _step()
	return cond.call()


## Rule 2 on every frame: amount stays 48 and the smoke node is never replaced, on all 4 tanks.
func _watch() -> void:
	_r2_frames += 1
	for t in tanks:
		var s = t.smoke
		var ok: bool = is_instance_valid(s) and s.get_instance_id() == smoke_ids[t] and s.amount == AMOUNT
		if not ok and not _r2_bad.has(t):
			_r2_bad[t] = true
			print("FAIL  rule 2: %s smoke changed at frame %d (amount %s)" % [t.name, _frame, str(s.amount) if is_instance_valid(s) else "freed"])
			failures += 1
		last_emitting[t] = s.emitting if is_instance_valid(s) else false


## Observer only: the smoke state at the moment take_damage() / die() hands back to the shell.
func _record(t, kind: String) -> void:
	events.append({"tank": t, "kind": kind, "health": t.health, "emitting": t.smoke.emitting,
		"ratio": t.smoke.amount_ratio, "amount": t.smoke.amount, "before": last_emitting.get(t, false),
		"frame": _frame})


func _on_damaged(t, _amount) -> void:
	_record(t, "damaged")


func _on_destroyed(t) -> void:
	_record(t, "destroyed")


func _on_fired(_t) -> void:
	fired += 1


func _events_for(t) -> Array:
	return events.filter(func(ev): return ev.tank == t)


## Real mouse input: a motion event at the window point that shows `world_pos`.
func _aim_at(world_pos: Vector2) -> void:
	var vp: Viewport = main.get_viewport()
	var screen: Vector2 = vp.get_final_transform() * (vp.get_canvas_transform() * world_pos)
	var ev := InputEventMouseMotion.new()
	ev.position = screen
	ev.global_position = screen
	Input.parse_input_event(ev)


func _key(code: Key, pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = code
	ev.physical_keycode = code
	ev.pressed = pressed
	Input.parse_input_event(ev)


func _esc() -> void:
	_key(KEY_ESCAPE, true)
	_key(KEY_ESCAPE, false)


## One enemy shell into YunqiZ through the game's own spawn_shell(), once invulnerability has run out.
## Returns the event it caused, or {} if none arrived.
func _hit_player() -> Dictionary:
	await _wait_until(func(): return p.invuln_left <= 0.0, 120)
	var n := events.size()
	main.spawn_shell(main.enemies[1], p.global_position + Vector2(80, 0), Vector2.LEFT)
	var ok := await _wait_until(func(): return events.size() > n, 60)
	return events[n] if ok else {}


func _check_event(ev: Dictionary, who: String, want_health: int, want_emitting: bool, want_ratio: float, rule: String) -> void:
	if ev.is_empty():
		_check("%s: shell hit %s (no damaged/destroyed signal)" % [rule, who], false)
		return
	_check("%s: %s health %d after the hit (want %d)" % [rule, who, ev.health, want_health], ev.health == want_health)
	_check("%s: %s smoke emitting %s on return from the hit (want %s)" % [rule, who, ev.emitting, want_emitting], ev.emitting == want_emitting)
	if want_ratio >= 0.0:
		_check("%s: %s amount_ratio %.4f (want %.4f +- %.3f)" % [rule, who, ev.ratio, want_ratio, RATIO_EPS], absf(ev.ratio - want_ratio) <= RATIO_EPS)
	_check("rule 2: %s amount still %d at the hit (got %d)" % [who, AMOUNT, ev.amount], ev.amount == AMOUNT)


func _run() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	p = main.player
	e0 = main.enemies[0]
	tanks = [p] + main.enemies
	for t in tanks:
		smoke_ids[t] = t.smoke.get_instance_id() if is_instance_valid(t.smoke) else 0
		t.damaged.connect(_on_damaged)
		t.destroyed.connect(_on_destroyed)
	p.fired.connect(_on_fired)
	# Test setup: freeze the enemy AI so no unplanned shells reach YunqiZ. KEEP_ACTIVE keeps their
	# bodies in the physics space so shells still hit them.
	for e in main.enemies:
		e.disable_mode = CollisionObject2D.DISABLE_MODE_KEEP_ACTIVE
		e.process_mode = Node.PROCESS_MODE_DISABLED

	# --- S0: structure and scene load (rule 7).
	for t in tanks:
		var s = t.smoke
		var gpu: Array = t.get_children().filter(func(n): return n is GPUParticles2D)
		var cpu: Array = t.get_children().filter(func(n): return n is CPUParticles2D)
		_check("%s: smoke is a GPUParticles2D instance of %s (got %s, %s)" % [t.name, SCENE, s.get_class(), s.scene_file_path],
			s is GPUParticles2D and s.scene_file_path == SCENE)
		_check("%s: smoke is the tank's child at TURRET_OFFSET %s (got %s)" % [t.name, t.TURRET_OFFSET, s.position],
			s.get_parent() == t and s.position == t.TURRET_OFFSET)
		_check("%s: one GPUParticles2D (smoke) and one CPUParticles2D (flames) under the tank (got %d, %d)" % [t.name, gpu.size(), cpu.size()],
			gpu.size() == 1 and cpu.size() == 1 and gpu[0] == s and cpu[0] == t.flames)
		_check("%s: smoke amount %d, local_coords false" % [t.name, s.amount], s.amount == AMOUNT and not s.local_coords)
	var emitting_at_load := 0
	for i in 30:
		await _step()
		for t in tanks:
			if t.smoke.emitting:
				emitting_at_load += 1
	_check("rule 7: no smoke emitting on any of the first 30 physics frames (%d tank-frames emitting)" % emitting_at_load, emitting_at_load == 0)
	_check("rule 7: every tank at full health after load", tanks.all(func(t): return t.health == t.max_health))

	# --- S1: YunqiZ destroys enemy 0 by real input; the enemy table of rule 1, and a wreck.
	print("--- S1: enemy 0 (max_health 75) hit by YunqiZ's real shells")
	var e_home: Vector2 = e0.global_position
	e0.global_position = p.global_position + Vector2(0, -150)  # test setup: into YunqiZ's line of fire
	# Test setup: enemy 0 must process, or its invuln_left (counted down in _physics_process) stays at
	# 0.3 after the first hit and blocks every later shell. target = null makes its _think() hold still
	# and never fire (enemy.gd line 19). A dead tank's _physics_process returns before _think anyway.
	e0.target = null
	e0.process_mode = Node.PROCESS_MODE_INHERIT
	_aim_at(p.global_position + p.TURRET_OFFSET + Vector2(0, -300))
	await _physics_frames(3)
	_key(KEY_SPACE, true)
	var ok := await _wait_until(func(): return e0.is_dead, 300)
	_key(KEY_SPACE, false)
	await _physics_frames(2)
	print("      enemy 0 moved from %s; YunqiZ fired %d shells" % [e_home, fired])
	_check("S1: enemy 0 destroyed by YunqiZ's shells", ok)
	var ee := _events_for(e0)
	_check("S1: 3 hits on enemy 0 (got %d events)" % ee.size(), ee.size() == 3)
	if ee.size() == 3:
		_check_event(ee[0], "enemy 0", 50, false, -1.0, "rule 1 (h 0.667, none)")
		_check_event(ee[1], "enemy 0", 25, true, _ratio_for(25.0 / 75.0), "rule 1 (h 0.333)")
		_check("rule 3: enemy 0 smoke was not emitting the frame before the threshold hit", not ee[1].before)
		_check("S1: the fatal hit is the destroyed signal", ee[2].kind == "destroyed")
		_check_event(ee[2], "enemy 0 (wreck)", 0, true, 1.0, "rule 1 (dead)")
	await _step()
	_check("rule 3: enemy 0 smoke still emitting on the next frame", e0.smoke.emitting)

	# --- S2: YunqiZ hit by enemy shells through main.spawn_shell(); rules 1 and 3.
	print("--- S2: YunqiZ (max_health 100) hit by enemy shells")
	var ev := await _hit_player()
	_check_event(ev, "YunqiZ", 75, false, -1.0, "rule 1 (h 0.75, none)")
	ev = await _hit_player()
	_check_event(ev, "YunqiZ", 50, true, 0.375, "rule 1 (h 0.5)")
	_check("rule 3: YunqiZ smoke was not emitting the frame before the threshold hit", not ev.is_empty() and not ev.before)
	await _step()
	_check("rule 3: YunqiZ smoke still emitting on the next frame", p.smoke.emitting)

	# --- S3: hidden (rule 6).
	print("--- S3: YunqiZ's smoke hidden")
	var em0: bool = p.smoke.emitting
	var r0: float = p.smoke.amount_ratio
	p.smoke.visible = false  # test-only write (rule 6)
	_check("rule 6: hiding changes neither emitting nor amount_ratio (%s, %.4f -> %s, %.4f)" % [em0, r0, p.smoke.emitting, p.smoke.amount_ratio],
		p.smoke.emitting == em0 and p.smoke.amount_ratio == r0)
	await _physics_frames(5)
	_check("rule 6: still unchanged 5 frames later", p.smoke.emitting == em0 and p.smoke.amount_ratio == r0)
	ev = await _hit_player()
	_check("rule 6: smoke still hidden at the hit", not p.smoke.visible and not p.smoke.is_visible_in_tree())
	_check_event(ev, "YunqiZ (smoke hidden)", 25, true, 0.6875, "rule 6 + rule 1 (h 0.25)")
	p.smoke.visible = true  # test-only write: shown again
	_check("rule 6: showing again changes neither emitting nor amount_ratio", p.smoke.emitting and absf(p.smoke.amount_ratio - 0.6875) <= RATIO_EPS)

	# --- S4: paused (rule 5).
	print("--- S4: Esc pause with YunqiZ at 25 HP and enemy 0 a wreck")
	_check("rule 5 precondition: YunqiZ's and the wreck's smoke can_process() before pause",
		p.smoke.can_process() and e0.smoke.can_process())
	var snap := {}
	for t in tanks:
		snap[t] = [t.smoke.emitting, t.smoke.amount_ratio, t.smoke.amount, t.health]
	_esc()
	ok = await _wait_until(func(): return paused, 10)
	_check("rule 5: Esc pauses the tree (tree paused %s, main.paused %s)" % [paused, main.paused], ok and main.paused)
	_check("rule 5: YunqiZ's smoke can_process() false under pause", not p.smoke.can_process())
	_check("rule 5: the wreck's smoke can_process() false under pause", not e0.smoke.can_process())
	await _physics_frames(60)
	var same := true
	for t in tanks:
		if [t.smoke.emitting, t.smoke.amount_ratio, t.smoke.amount, t.health] != snap[t]:
			same = false
			print("      %s changed under pause: %s -> %s" % [t.name, snap[t], [t.smoke.emitting, t.smoke.amount_ratio, t.smoke.amount, t.health]])
	_check("rule 5: emitting, amount_ratio, amount and health unchanged on all 4 tanks over %.2f s paused" % _secs(60), same)
	_esc()
	ok = await _wait_until(func(): return not paused, 10)
	_check("rule 5: Esc again unpauses", ok and not main.paused)
	_check("rule 5: smoke can_process() again after unpause, still emitting", p.smoke.can_process() and e0.smoke.can_process()
		and p.smoke.emitting and e0.smoke.emitting)

	# --- S5: YunqiZ destroyed, then main.gd's own respawn (rules 1 dead, 4).
	print("--- S5: fatal hit on YunqiZ, then the real respawn")
	ev = await _hit_player()
	_check("S5: the fatal hit is the destroyed signal", not ev.is_empty() and ev.kind == "destroyed")
	_check_event(ev, "YunqiZ (dead)", 0, true, 1.0, "rule 1 (dead)")
	var death_frame := _frame
	var dead_frames := 0
	var dead_not_emitting := 0
	for i in 240:
		if not p.is_dead:
			break
		dead_frames += 1
		if not p.smoke.emitting:
			dead_not_emitting += 1
		await _step()
	_check("S5: YunqiZ respawned by main.gd %.2f s after death (want about 2.0)" % _secs(_frame - death_frame),
		not p.is_dead and _secs(_frame - death_frame) >= 1.9 and _secs(_frame - death_frame) <= 2.2)
	_check("rule 1: YunqiZ's smoke emitting on every dead frame (%d of %d not emitting)" % [dead_not_emitting, dead_frames],
		dead_frames > 0 and dead_not_emitting == 0)
	_check("rule 4: emitting false on the first frame after the respawn", not p.smoke.emitting)
	_check("rule 4: same smoke node, still in the tree and visible (left to fade, not freed or replaced)",
		is_instance_valid(p.smoke) and p.smoke.get_instance_id() == smoke_ids[p] and p.smoke.is_inside_tree() and p.smoke.visible)
	_check("S5: respawn restored health %d (read, not written)" % p.health, p.health == p.max_health)
	print("NOTE  after respawn amount_ratio is %.4f (R4.2: left as it was; not asserted)" % p.smoke.amount_ratio)
	await _physics_frames(10)
	_check("rule 4: YunqiZ's smoke still off 10 frames after the respawn", not p.smoke.emitting)
	_check("rule 4: the wreck keeps smoking after YunqiZ's respawn (emitting %s, ratio %.4f)" % [e0.smoke.emitting, e0.smoke.amount_ratio],
		e0.is_dead and is_instance_valid(e0) and e0.is_inside_tree() and e0.smoke.emitting and absf(e0.smoke.amount_ratio - 1.0) <= RATIO_EPS)
	var others_off: bool = main.enemies.slice(1).all(func(e): return not e.smoke.emitting and e.health == e.max_health)
	_check("rules 1, 7: enemies 1 and 2 untouched, not smoking", others_off)

	# --- Rule 2 summary and the health sequence.
	_check("rule 2: amount %d and the same smoke node on all 4 tanks for all %d frames" % [AMOUNT, _r2_frames], _r2_bad.is_empty())
	var ph := _events_for(p).map(func(x): return x.health)
	var eh := _events_for(e0).map(func(x): return x.health)
	_check("health only changed by the shells: YunqiZ %s (want [75, 50, 25, 0]), enemy 0 %s (want [50, 25, 0])" % [ph, eh],
		ph == [75, 50, 25, 0] and eh == [50, 25, 0])

	main.queue_free()
	await process_frame
	await process_frame

	# --- G: the gallery builds tanks from tank.gd and enemy.gd (R1.4). Its own code sets the health.
	print("--- G: scenes/gallery.tscn")
	var g = load(GALLERY).instantiate()
	root.add_child(g)
	await process_frame
	await process_frame
	var gt: Array = g.get_children().filter(func(n): return n is CharacterBody2D)
	_check("G: gallery loaded with 13 tanks (got %d)" % gt.size(), gt.size() == 13)
	_check("G: every gallery tank has a damage_smoke instance",
		gt.all(func(t): return t.smoke is GPUParticles2D and t.smoke.scene_file_path == SCENE and t.smoke.amount == AMOUNT))
	var want := {Vector2(40, 175): [false, -1.0], Vector2(150, 175): [true, _ratio_for(0.55)],
		Vector2(260, 175): [true, _ratio_for(0.20)], Vector2(370, 175): [true, 1.0], Vector2(480, 175): [false, -1.0]}
	for pos in want:
		var found: Array = gt.filter(func(t): return t.position == pos)
		if found.size() != 1:
			_check("G: state tank at %s found" % pos, false)
			continue
		var t = found[0]
		var w: Array = want[pos]
		var r_ok: bool = w[1] < 0.0 or absf(t.smoke.amount_ratio - w[1]) <= RATIO_EPS
		_check("G: tank at %s (health %d) smoke emitting %s, ratio %.4f (want %s, %s)" % [pos, t.health, t.smoke.emitting, t.smoke.amount_ratio, w[0], "-" if w[1] < 0.0 else "%.4f" % w[1]],
			t.smoke.emitting == w[0] and r_ok)
	var facings_off: bool = gt.filter(func(t): return t.position.y == 55.0).all(func(t): return not t.smoke.emitting)
	_check("G: the 8 facing tanks are not smoking", facings_off)
	g.queue_free()
	await process_frame

	print("RESULT: %d passed, %d failed" % [passes, failures])
	quit(1 if failures > 0 else 0)
