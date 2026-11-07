extends SceneTree
## Effect A state test (CHANGE-BRIEF.md, Effect A, "Observable rules" and "The evidence split").
## Drives YunqiZ with real input events through the real game loop; never calls the trigger
## (spawn_cover_burst) and, except in the labelled R1 section at the end, never calls take_hit().
## Run: bash scripts/run-test.sh test_cover_hit_burst_state.gd 60
##
## Test setup writes only: the enemy AI is frozen (as in test_hit_flash.gd, but with the bodies kept in
## the physics space), and enemy 0 is moved into
## YunqiZ's line of fire for the tank-hit phase and moved back. Time is counted in physics frames.

const BURST_SCENE := "res://effects/cover_hit_burst.tscn"
const SHELL_SCRIPT := "res://scripts/shell.gd"
const LIFE_MIN := 0.65  # s; Dust lifetime 0.7, explosiveness 0.9 adds up to 0.07 s, plus frame steps
const LIFE_MAX := 0.85
const POS_TOL := 2.0
const ANG_TOL := 0.01

var failures := 0
var passes := 0
var main
var p
var fired := 0
var last_shell = null
var last_shell_frame := 0
var bursts := []  # one Dictionary per burst that entered World/FX
var phase := "P0"
var _frame := 0


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


func _shells() -> Array:
	return main.fx_layer.get_children().filter(func(n): return n.get_script() != null and n.get_script().resource_path == SHELL_SCRIPT)


func _cover_at(pos: Vector2):
	for n in main.actors.get_children():
		if n.has_method("take_hit") and n.global_position.distance_to(pos) < 1.0:
			return n
	return null


## Observer only: records each burst as it enters World/FX, with the shells that have hit at that moment
## (the triggering shell is still valid; its queue_free is pending).
func _on_fx_child(n: Node) -> void:
	if n.scene_file_path != BURST_SCENE:
		return
	var hit_shells := []
	for s in _shells():
		if s.has_hit:
			hit_shells.append({"node": s, "pos": s.global_position + s.DRAW_OFFSET, "back": (-s.dir).angle()})
	var rec := {"idx": bursts.size() + 1, "node": n, "id": n.get_instance_id(), "frame": _frame, "exit": -1,
		"phase": phase, "shells": hit_shells, "placed": false, "r4": false}
	n.tree_exited.connect(func(): rec.exit = _frame)
	bursts.append(rec)


func _on_fired(_t) -> void:
	fired += 1
	var ss := _shells()
	last_shell = ss.back() if ss.size() > 0 else null
	last_shell_frame = _frame


## Per-frame checks for every gameplay burst: rule 2 once on its first frame, rule 4 once its shell is gone.
func _watch() -> void:
	for b in bursts:
		if b.phase == "R1":
			continue
		if not b.placed and is_instance_valid(b.node):
			b.placed = true
			_check_place(b)
		if not b.r4 and b.shells.size() == 1 and not is_instance_valid(b.shells[0].node):
			b.r4 = true
			var n = b.node
			var ok: bool = is_instance_valid(n) and n.is_inside_tree() and n.get_parent() == main.fx_layer \
				and n.get_node("Debris").emitting and n.get_node("Dust").emitting
			_check("rule 4: burst %d (%s) still in World/FX and emitting after its shell was freed" % [b.idx, b.phase], ok)


func _check_place(b: Dictionary) -> void:
	_check("rule 2: burst %d (%s) has exactly 1 hit shell at creation (got %d)" % [b.idx, b.phase, b.shells.size()], b.shells.size() == 1)
	if b.shells.size() != 1:
		return
	var n: Node2D = b.node
	var want: Dictionary = b.shells[0]
	var d: float = n.global_position.distance_to(want.pos)
	var a: float = absf(angle_difference(n.rotation, want.back))
	_check("rule 2: burst %d at the shell's drawn contact point %s (got %s, off %.3f px, tol %.1f)" % [b.idx, want.pos, n.global_position, d, POS_TOL], d <= POS_TOL)
	_check("rule 2: burst %d rotation %.4f == (-shell.dir).angle() %.4f (tol %.2f)" % [b.idx, n.rotation, want.back, ANG_TOL], a < ANG_TOL)


func _check_life(b: Dictionary) -> void:
	var secs := _secs(b.exit - b.frame)
	_check("burst %d (%s) freed itself %.3f s after it appeared (want %.2f-%.2f)" % [b.idx, b.phase, secs, LIFE_MIN, LIFE_MAX],
		b.exit >= 0 and secs >= LIFE_MIN and secs <= LIFE_MAX)


## Real mouse input: a motion event at the window point that shows `world_pos`.
## Window coordinates include the canvas_items stretch (the headless window is not 1280 x 720).
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


func _space(pressed: bool) -> void:
	_key(KEY_SPACE, pressed)


## One real shot: press Space until YunqiZ fires, then release. Returns the new shell (or null).
func _shoot() -> Node:
	var f := fired
	_space(true)
	var ok := await _wait_until(func(): return fired > f, 60)
	_space(false)
	await _step()
	return last_shell if ok else null


## Clear path for a shell's remaining life: a 3 px circle cast along dir * speed * life, bodies only.
func _path_clear(s: Node) -> bool:
	var q := PhysicsShapeQueryParameters2D.new()
	var c := CircleShape2D.new()
	c.radius = 3.0
	q.shape = c
	q.transform = Transform2D(0.0, s.global_position)
	q.motion = s.dir * s.speed * s._life
	q.collision_mask = s.collision_mask
	q.collide_with_areas = false
	q.collide_with_bodies = true
	var r: PackedFloat32Array = main.get_world_2d().direct_space_state.cast_motion(q)
	print("      shell 5 path cast from %s along %s: %s" % [s.global_position, q.motion, r])
	return r.size() == 2 and r[0] >= 1.0


func _run() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	main.fx_layer.child_entered_tree.connect(_on_fx_child)
	await process_frame
	await _step()
	p = main.player
	# Test setup: freeze the enemy AI so no unplanned shells reach cover or YunqiZ. KEEP_ACTIVE keeps
	# their bodies in the physics space (the default, REMOVE, would take them out when disabled).
	for e in main.enemies:
		e.disable_mode = CollisionObject2D.DISABLE_MODE_KEEP_ACTIVE
		e.process_mode = Node.PROCESS_MODE_DISABLED
	p.fired.connect(_on_fired)
	var audio = main.audio
	var sound0: int = audio.count("cover_hit")
	var c1 = _cover_at(Vector2(620, 610))
	var c2 = _cover_at(Vector2(320, 480))
	var c3 = _cover_at(Vector2(1040, 370))
	_check("covers (620, 610), (320, 480), (1040, 370) found, all intact", c1 != null and c2 != null and c3 != null
		and c1.hits == 0 and c2.hits == 0 and c3.hits == 0)

	# --- P0: scene load.
	await _physics_frames(30)
	_check("rule 1: no burst on scene load (30 physics frames, got %d)" % bursts.size(), bursts.is_empty())

	# --- Input check: real mouse motion aims the turret.
	phase = "P1"
	var pivot: Vector2 = p.global_position + p.TURRET_OFFSET
	var aims := [["up", Vector2(0, -300), -PI / 2], ["right", Vector2(500, 0), 0.0]]
	for a in aims:
		_aim_at(pivot + a[1])
		await _physics_frames(3)
		print("      aim %s: mouse (global) %s, aim_angle %.4f" % [a[0], p.get_global_mouse_position(), p.aim_angle])
		_check("mouse motion aims YunqiZ %s (aim_angle %.4f, want %.4f +- 0.01)" % [a[0], p.aim_angle, a[2]],
			absf(angle_difference(p.aim_angle, a[2])) < 0.01)

	# --- Input check: a real Space press fires one shell along the aim.
	var s0 := _shells().size()
	var f0 := fired
	_space(true)
	await _physics_frames(2)
	var key_ok := Input.is_action_pressed("fire")
	_check("Space key event reaches the fire action", key_ok)
	if not key_ok:
		print("NOTE  falling back to Input.action_press(\"fire\")")
		Input.action_press("fire")
		await _physics_frames(2)
	await _physics_frames(4)
	if key_ok:
		_space(false)
	else:
		Input.action_release("fire")
	await _physics_frames(2)
	_check("fire action released", not Input.is_action_pressed("fire"))
	var new_shells := _shells().slice(s0)
	_check("one press -> exactly 1 fired signal (got %d)" % (fired - f0), fired - f0 == 1)
	_check("one press -> exactly 1 new shell in World/FX (got %d)" % new_shells.size(), new_shells.size() == 1)
	if new_shells.size() == 1:
		var s = new_shells[0]
		print("      shell dir %s, angle %.4f; shooter is YunqiZ: %s" % [s.dir, s.dir.angle(), s.shooter == p])
		_check("shell dir matches the aim (angle %.4f, want 0.0 +- 0.01)" % s.dir.angle(), absf(angle_difference(s.dir.angle(), 0.0)) < 0.01)
		_check("shell shooter is YunqiZ", s.shooter == p)

	# --- P1: four hits on one block (the input-check shell is hit 1), then a shell past the broken block.
	var ok := await _wait_until(func(): return c1.hits == 1, 120)
	_check("P1: the input-check shell hits cover (620, 610) (hits %d, bursts %d)" % [c1.hits, bursts.size()], ok and bursts.size() == 1)
	_space(true)
	ok = await _wait_until(func(): return fired >= 5, 240)
	_space(false)
	_check("P1: holding Space fires 4 more shells (5 in total, got %d)" % fired, ok and fired == 5)
	var s5 = last_shell
	var s5_born := last_shell_frame
	var s5_end := {"frame": -1, "has_hit": true}
	if is_instance_valid(s5):
		s5.tree_exiting.connect(func():
			s5_end.frame = _frame
			s5_end.has_hit = s5.has_hit)
	var path_checked := false
	for i in 200:
		if s5_end.frame >= 0:
			break
		if not path_checked and c1.stage == 2 and _frame - s5_born >= 30 and is_instance_valid(s5):
			path_checked = true
			_check("P1 precondition: with the block broken, shell 5's remaining path is clear", _path_clear(s5))
		await _step()
	_check("P1: 4 hits on cover (620, 610), stage 2 (hits %d, stage %d)" % [c1.hits, c1.stage], c1.hits == 4 and c1.stage == 2)
	_check("rule 1: four hits on one block -> 4 bursts (got %d)" % bursts.size(), bursts.size() == 4)
	_check("P1: the precondition check ran", path_checked)
	_check("rule 1: shell 5 expired without hitting anything (has_hit %s, freed after %d frames, want 118-123)"
		% [s5_end.has_hit, s5_end.frame - s5_born], s5_end.frame >= 0 and not s5_end.has_hit
		and s5_end.frame - s5_born >= 118 and s5_end.frame - s5_born <= 123)
	_check("rule 1: no burst from the expired shell or the broken block (bursts still %d)" % bursts.size(), bursts.size() == 4)
	await _wait_until(func(): return bursts.all(func(b): return b.exit >= 0), 60)
	for b in bursts:
		_check_life(b)

	# --- P2: a shell hits a tank.
	phase = "P2"
	var e0 = main.enemies[0]
	var e0_home: Vector2 = e0.global_position
	var ehp: int = e0.health
	e0.global_position = p.global_position + Vector2(0, -150)  # test setup: into YunqiZ's line of fire
	_aim_at(pivot + Vector2(0, -300))
	await _physics_frames(3)
	var nb := bursts.size()
	var s2 = await _shoot()
	var s2_end := {"frame": -1}
	if is_instance_valid(s2):
		s2.tree_exiting.connect(func(): s2_end.frame = _frame)
	await _wait_until(func(): return s2_end.frame >= 0, 120)
	await _physics_frames(2)
	_check("P2: YunqiZ's shell hit enemy 0 (health %d -> %d)" % [ehp, e0.health], e0.health == ehp - 25)
	_check("rule 1: no burst when a shell hits a tank (bursts %d -> %d)" % [nb, bursts.size()], bursts.size() == nb)
	e0.global_position = e0_home

	# --- P3: two hits on one block inside one lifetime (overlap).
	phase = "P3"
	_aim_at(c2.global_position + p.TURRET_OFFSET)
	await _physics_frames(3)
	nb = bursts.size()
	await _shoot()
	ok = await _wait_until(func(): return bursts.size() > nb, 90)
	_check("P3: YunqiZ's diagonal shell hits cover (320, 480) -> 1 burst", ok and bursts.size() == nb + 1)
	if ok:
		var b1: Dictionary = bursts[nb]
		# Second shell through the game's own spawn_shell(), 0.3 s of travel from the block's right face.
		var start := Vector2(c2.global_position.x + 36.3 + 3.0 + 0.3 * 460.0, c2.global_position.y)
		main.spawn_shell(main.enemies[1], start, Vector2.LEFT)
		ok = await _wait_until(func(): return bursts.size() > nb + 1, 60)
		_check("P3: the second shell (main.spawn_shell) hits the same block -> 2nd burst", ok)
		if ok:
			var b2: Dictionary = bursts[nb + 1]
			var n1 = b1.node
			var n2 = b2.node
			var both: bool = is_instance_valid(n1) and is_instance_valid(n2) and n1.is_inside_tree() and n2.is_inside_tree()
			_check("rule 3: the hits are %.3f s apart, inside one lifetime (< 0.7 s)" % _secs(b2.frame - b1.frame), _secs(b2.frame - b1.frame) < 0.7)
			_check("rule 3: 2 bursts alive at once", both)
			_check("rule 3: 2 different instances (ids %d, %d)" % [b1.id, b2.id], b1.id != b2.id)
			_check("rule 3: both under World/FX", both and n1.get_parent() == main.fx_layer and n2.get_parent() == main.fx_layer)
			_check("rule 3: the first burst is still emitting when the second arrives", both and n1.get_node("Dust").emitting)
			await _wait_until(func(): return b1.exit >= 0 and b2.exit >= 0, 90)
			_check_life(b1)
			_check_life(b2)
			_check("rule 3: first burst not restarted: freed %.3f s after the 2nd hit (a restart would be >= %.2f s)"
				% [_secs(b1.exit - b2.frame), LIFE_MIN], b1.exit >= 0 and _secs(b1.exit - b2.frame) < LIFE_MIN)
	_check("P3: cover (320, 480) took 2 hits and cracked (hits %d, stage %d)" % [c2.hits, c2.stage], c2.hits == 2 and c2.stage == 1)

	# --- P4: a burst alive at pause freezes and resumes.
	phase = "P4"
	await _physics_frames(30)
	nb = bursts.size()
	await _shoot()
	ok = await _wait_until(func(): return bursts.size() > nb, 90)
	_check("P4: third hit on cover (320, 480) -> 1 burst", ok and bursts.size() == nb + 1)
	if ok:
		var b: Dictionary = bursts[nb]
		var n = b.node
		await _physics_frames(12)
		_key(KEY_ESCAPE, true)
		_key(KEY_ESCAPE, false)
		ok = await _wait_until(func(): return paused, 10)
		var pause_frame := _frame
		_check("rule 5: Esc pauses the tree (tree paused %s, main.paused %s)" % [paused, main.paused], ok and main.paused)
		var frozen: bool = is_instance_valid(n) and not n.can_process()
		for c in ["Flash", "Debris", "Dust"]:
			frozen = frozen and not n.get_node(c).can_process()
		_check("rule 5: burst root and its 3 emitters can_process() false under pause", frozen)
		await _physics_frames(60)
		_check("rule 5: after %.2f s paused (longer than the 0.7 s life) the burst is still there and Dust still emitting" % _secs(60),
			b.exit < 0 and is_instance_valid(n) and n.get_node("Dust").emitting)
		_key(KEY_ESCAPE, true)
		_key(KEY_ESCAPE, false)
		ok = await _wait_until(func(): return not paused, 10)
		var unpause_frame := _frame
		_check("rule 5: Esc again unpauses", ok and not main.paused)
		await _wait_until(func(): return b.exit >= 0, 90)
		var before := _secs(pause_frame - b.frame)
		var after := _secs(b.exit - unpause_frame)
		_check("rule 5: resumed where it was: %.3f s before pause + %.3f s after = %.3f s (want %.2f-%.2f)"
			% [before, after, before + after, LIFE_MIN, LIFE_MAX], b.exit >= 0 and before + after >= LIFE_MIN and before + after <= LIFE_MAX)
		_check("rule 5: not restarted on unpause (%.3f s after unpause < %.2f s)" % [after, LIFE_MIN], b.exit >= 0 and after < LIFE_MIN)
	_check("P4: cover (320, 480) took its 3rd hit (hits %d)" % c2.hits, c2.hits == 3)

	# --- End totals (gameplay bursts only).
	phase = "end"
	var ids := {}
	for b in bursts:
		ids[b.id] = true
	_check("rule 1: %d bursts in total == cover hits past line 34 (%d + %d), want 7" % [bursts.size(), c1.hits, c2.hits],
		bursts.size() == c1.hits + c2.hits and bursts.size() == 7)
	_check("rule 1: cover_hit sounds over the run == bursts (%d == %d)" % [audio.count("cover_hit") - sound0, bursts.size()],
		audio.count("cover_hit") - sound0 == bursts.size())
	_check("rule 3: every burst a different instance (%d unique ids)" % ids.size(), ids.size() == bursts.size())
	_check("rule 2: placement checked on every burst", bursts.all(func(b): return b.placed))
	_check("rule 4: freed-parent check ran on every burst", bursts.all(func(b): return b.r4))
	_check("every burst has freed itself", bursts.all(func(b): return b.exit >= 0))

	# --- R1 fallback check: direct call, not a gameplay event (not counted in rule 1's totals).
	print("--- R1 fallback check: direct call, not a gameplay event")
	phase = "R1"
	_check("R1: cover (1040, 370) untouched by every earlier phase (hits %d)" % c3.hits, c3.hits == 0)
	nb = bursts.size()
	c3.take_hit()
	_check("R1: take_hit() with no shell -> 1 burst", bursts.size() == nb + 1)
	if bursts.size() == nb + 1:
		var n: Node2D = bursts[nb].node
		var want: Vector2 = c3.global_position + Vector2(0, -8)
		var d := n.global_position.distance_to(want)
		_check("R1: burst at cover + (0, -8) = %s (got %s, off %.3f px, tol %.1f)" % [want, n.global_position, d, POS_TOL], d <= POS_TOL)
		_check("R1: burst rotation %.4f == -PI/2 (tol %.2f)" % [n.rotation, ANG_TOL], absf(angle_difference(n.rotation, -PI / 2)) < ANG_TOL)
		_check("R1: burst under World/FX", n.get_parent() == main.fx_layer)

	print("RESULT: %d passed, %d failed" % [passes, failures])
	main.queue_free()
	await process_frame
	quit(1 if failures > 0 else 0)
