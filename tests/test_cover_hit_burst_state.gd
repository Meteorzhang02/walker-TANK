extends SceneTree
## Effect A state test (CHANGE-BRIEF.md, Effect A, "Observable rules" and "The evidence split").
## Drives YunqiZ with real input events through the real game loop; never calls the trigger.
## Run: bash scripts/run-test.sh test_cover_hit_burst_state.gd 60
##
## Step 3a: setup and the input check only.

const BURST_SCENE := "res://effects/cover_hit_burst.tscn"
const SHELL_SCRIPT := "res://scripts/shell.gd"

var failures := 0
var passes := 0
var main
var p
var fired := 0
var bursts := []  # one entry per burst that entered World/FX: {node, frame, shells}
var _frame := 0


func _initialize() -> void:
	_run.call_deferred()


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if ok:
		passes += 1
	else:
		failures += 1


func _physics_frames(n: int) -> void:
	for i in n:
		await physics_frame
		_frame += 1


func _shells() -> Array:
	return main.fx_layer.get_children().filter(func(n): return n.get_script() != null and n.get_script().resource_path == SHELL_SCRIPT)


## Observer only: records each burst as it enters World/FX, with the shells that have hit at that moment
## (the triggering shell is still valid; its queue_free is pending).
func _on_fx_child(n: Node) -> void:
	if n.scene_file_path != BURST_SCENE:
		return
	var hit_shells := []
	for s in _shells():
		if s.has_hit:
			hit_shells.append({"pos": s.global_position + s.DRAW_OFFSET, "back": (-s.dir).angle()})
	bursts.append({"node": n, "frame": _frame, "shells": hit_shells})


## Real mouse input: a motion event at the window point that shows `world_pos`.
## Window coordinates include the canvas_items stretch (the headless window is not 1280 x 720).
func _aim_at(world_pos: Vector2) -> void:
	var vp: Viewport = main.get_viewport()
	var screen: Vector2 = vp.get_final_transform() * (vp.get_canvas_transform() * world_pos)
	var ev := InputEventMouseMotion.new()
	ev.position = screen
	ev.global_position = screen
	Input.parse_input_event(ev)


func _space(pressed: bool) -> void:
	var ev := InputEventKey.new()
	ev.keycode = KEY_SPACE
	ev.physical_keycode = KEY_SPACE
	ev.pressed = pressed
	Input.parse_input_event(ev)


func _run() -> void:
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await _physics_frames(1)
	p = main.player
	# Test setup: freeze the enemy AI so no unplanned shells reach cover or YunqiZ (their bodies stay).
	for e in main.enemies:
		e.process_mode = Node.PROCESS_MODE_DISABLED
	main.fx_layer.child_entered_tree.connect(_on_fx_child)
	p.fired.connect(func(_t): fired += 1)

	# --- Input check: real mouse motion aims the turret.
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

	print("RESULT: %d passed, %d failed" % [passes, failures])
	main.queue_free()
	await process_frame
	quit(1 if failures > 0 else 0)
