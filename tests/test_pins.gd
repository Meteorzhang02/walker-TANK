extends SceneTree
## A7 Step 2 pins: what the game does NOW, before any clip is wired.
## Drives the real scenes/main.tscn through the real loop; input only via Input.parse_input_event.
## Run: bash scripts/run-test.sh test_pins.gd 60
##
## Tick convention. The script resumes on physics_frame, which fires at the start of physics tick i,
## before the nodes run tick i. Input injected at resume i is therefore seen by tick i. State read at
## resume i is the result of tick i-1, so an observed change is credited to tick i-1.
## Ticks are printed relative to the tick "fire" is injected (press tick = 0).

const FIRE_TICK := 40      # drive right ticks 0-29, release at 30, idle 30-39, press fire at 40
const MOVE_TICKS := 30
const HOLD_TICKS := 120
const TAIL_TICKS := 12
# Input.parse_input_event is buffered: an action injected at the start of tick i is seen by the game
# on tick i+1 (measured, PIN-0). "Press tick" below means the tick the game first sees the press,
# i.e. FIRE_TICK + INPUT_LATENCY, which is the tick try_fire() runs on.
const INPUT_LATENCY := 1

var passed := 0
var failed := 0


func _initialize() -> void:
	_run.call_deferred()


func _pin(name: String, measured, expected) -> void:
	var ok: bool = measured == expected
	print("%s  %s | measured=%s expected=%s" % ["PASS" if ok else "FAIL", name, str(measured), str(expected)])
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


func _shell_ids(fx_layer: Node, shell_script: Script) -> Array:
	var ids := []
	for n in fx_layer.get_children():
		if n.get_script() == shell_script:
			ids.append(n.get_instance_id())
	return ids


func _run() -> void:
	var main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await physics_frame
	var player = main.player
	var audio = main.audio
	var shell_script: Script = load("res://scripts/shell.gd")

	# Keep the enemies still and silent without removing anything from physics: target = null makes
	# enemy _think() return with move_dir = ZERO before any fire call.
	var enemy_start := []
	for e in main.enemies:
		e.target = null
		enemy_start.append(e.global_position)

	# Settle a few ticks so the first scripted tick starts from a quiet game.
	for i in 5:
		await physics_frame
	_info("start: player at %s, reload_left=%s, move_dir=%s, fire sounds so far=%d" % [
		str(player.global_position), str(player.reload_left), str(player.move_dir), audio.count("fire")])

	var events := []              # [relative tick, label]
	var shell_ticks := []         # relative ticks a new shell was first seen
	var sound_ticks := []         # relative ticks the fire sound count rose
	var seen_ids := _shell_ids(main.fx_layer, shell_script)
	var all_from_player := true
	var prev_moving: bool = player.move_dir != Vector2.ZERO
	var prev_sounds: int = audio.count("fire")
	var press_physics_frame := -1
	var first_shell_physics_frame := -1
	var injected_visible := false
	var move_start_abs := -1
	var total := FIRE_TICK + HOLD_TICKS + TAIL_TICKS

	for i in total:
		await physics_frame            # start of tick i
		var abs_tick: int = i - 1                  # tick i-1 produced what we read now
		var effect_tick: int = abs_tick - FIRE_TICK - INPUT_LATENCY   # relative to the press tick
		if i > 0:
			var moving: bool = player.move_dir != Vector2.ZERO
			if moving != prev_moving:
				if moving and move_start_abs < 0:
					move_start_abs = abs_tick
				events.append([effect_tick, "move_start" if moving else "move_stop"])
				prev_moving = moving
			for n in main.fx_layer.get_children():
				if n.get_script() == shell_script and not seen_ids.has(n.get_instance_id()):
					seen_ids.append(n.get_instance_id())
					events.append([effect_tick, "shell"])
					shell_ticks.append(effect_tick)
					if n.shooter != player:
						all_from_player = false
					if first_shell_physics_frame < 0:
						first_shell_physics_frame = Engine.get_physics_frames()
			var sounds: int = audio.count("fire")
			if sounds != prev_sounds:
				for k in sounds - prev_sounds:
					sound_ticks.append(effect_tick)
				prev_sounds = sounds
		# Injection for tick i.
		if i == 0:
			_inject("move_right", true)
		elif i == MOVE_TICKS:
			_inject("move_right", false)
		elif i == FIRE_TICK:
			_inject("fire", true)
			press_physics_frame = Engine.get_physics_frames()
			injected_visible = Input.is_action_pressed("fire")
		elif i == FIRE_TICK + HOLD_TICKS:
			_inject("fire", false)

	# Expected reload interval from the code's own arithmetic: reload_left = 0.8 is set on the shot
	# tick; each later tick subtracts delta first, and try_fire needs reload_left <= 0.
	var delta := 1.0 / float(Engine.physics_ticks_per_second)
	var r := 0.8
	var expected_reload := 0
	while r > 0.0:
		r = maxf(0.0, r - delta)
		expected_reload += 1

	print("---- measured sequence (tick relative to the fire press; move ticks are negative) ----")
	for ev in events:
		print("  tick %4d  %s" % [ev[0], ev[1]])
	_info("fire sound ticks: %s" % str(sound_ticks))
	_info("Engine.get_physics_frames at press injection=%d, when first shell was seen=%d" % [
		press_physics_frame, first_shell_physics_frame])
	_info("nominal reload: 0.8 s * 60 = 48 ticks; arithmetic of the code (float, delta=1/60) gives %d" % expected_reload)
	print("---- pins ----")

	_pin("PIN-0 input latency: ticks from injecting move_right (tick 0) to the tick the game acts on it",
		move_start_abs, INPUT_LATENCY)
	_pin("PIN-0b Input.is_action_pressed is still false right after parse_input_event (buffered)",
		injected_visible, false)
	var expected_events := [
		[-FIRE_TICK, "move_start"],
		[-(FIRE_TICK - MOVE_TICKS), "move_stop"],
		[0, "shell"],
		[expected_reload, "shell"],
		[2 * expected_reload, "shell"],
	]
	_pin("PIN-1 sequence of move_dir changes and shells", str(events), str(expected_events))
	_pin("PIN-2 first shell tick vs press [PREDICTED TO CHANGE by A7 brief: +2 ticks]",
		shell_ticks[0] if shell_ticks.size() > 0 else -999, 0)
	var interval: int = (shell_ticks[1] - shell_ticks[0]) if shell_ticks.size() > 1 else -999
	_pin("PIN-3 reload interval, ticks between shell 1 and 2 while fire held", interval, expected_reload)
	_pin("PIN-3b shells during the 120-tick hold", shell_ticks.size(), 3)
	_pin("PIN-4 fire sound tick vs press [PREDICTED TO CHANGE by A7 brief: +2 ticks]; observed through audio.count(\"fire\"), no script edited",
		sound_ticks[0] if sound_ticks.size() > 0 else -999, 0)
	_pin("PIN-4b fire sound requests over the run (one per shell)", sound_ticks.size(), shell_ticks.size())
	_pin("PIN-5 every shell belongs to the player", all_from_player, true)
	var enemies_still := true
	for k in main.enemies.size():
		if main.enemies[k].global_position != enemy_start[k] or main.enemies[k].move_dir != Vector2.ZERO:
			enemies_still = false
	_pin("PIN-6 enemies did not move (target = null)", enemies_still, true)
	_pin("PIN-7 player stayed alive", player.is_dead, false)

	print("RESULT: %d passed, %d failed" % [passed, failed])
	quit(1 if failed > 0 else 0)
