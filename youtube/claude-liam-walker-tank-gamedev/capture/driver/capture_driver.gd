extends Node
## Scripted-input capture driver for walker-TANK (film capture only; lives in an isolated copy).
## It READS game state (positions, health, cover stage, audio request counts) to decide WHEN and
## WHERE to press, and it only WRITES input: Input.action_press/release for the game's own actions,
## InputEventKey for pause, and the real mouse cursor (Viewport.warp_mouse) for turret aim.
## It never sets positions, health, timers, collisions or calls game functions.
## Every phase asserts its result; timeouts and failed assertions quit with a nonzero code.

const MOVE := {"up": Vector2(0, -1), "down": Vector2(0, 1), "left": Vector2(-1, 0), "right": Vector2(1, 0)}
const DIRS8 := [Vector2(1, 0), Vector2(1, 1), Vector2(0, 1), Vector2(-1, 1), Vector2(-1, 0), Vector2(-1, -1), Vector2(0, -1), Vector2(1, -1)]
const SIN_E := 0.8192
const BARREL_LEN := 40.4
const TURRET_OFFSET := Vector2(0.0, -10.85)
const SHELL_SPEED := 460.0

var log_path := "user://capture-inputs.jsonl"
var main = null
var tick := 0
var phase := "boot"
var phase_tick := 0
var held := {}
var fire_held := false
var aim_world := Vector2(400, 300)
var log_file: FileAccess
var last_counts := {}
var last_hp := -1
var last_dead := false
var last_cover_stage := {}
var last_enemy_dead := {}
var deaths := 0
var kills := 0
var tour_leg := 0
var tour_left := 0.0
var paused_done := false
var victory_tick := -1
var timeout_ticks := 60 * 240
var fight_spot := Vector2.ZERO
var expose := false
var last_music := ""
var last_shot_tick := -1000
var tour_stop := 0.0

const TOUR := [["up", 0.6], ["up_right", 0.5], ["right", 0.4], ["down_right", 0.4], ["down", 0.5],
	["down_left", 0.5], ["left", 0.9], ["up_left", 0.5]]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	process_physics_priority = -100
	var args := OS.get_cmdline_user_args()
	for a in args:
		if a.begins_with("--log="):
			log_path = a.substr(6)
	log_file = FileAccess.open(log_path, FileAccess.WRITE)
	_log({"ev": "driver_start", "method": "scripted-input", "log": log_path})


func _log(d: Dictionary) -> void:
	d["tick"] = tick
	d["frame"] = Engine.get_frames_drawn()
	d["phase"] = phase
	log_file.store_line(JSON.stringify(d))
	log_file.flush()


func _fail(msg: String) -> void:
	_release_all()
	_log({"ev": "FAIL", "msg": msg})
	push_error("CAPTURE FAIL: " + msg)
	get_tree().quit(3)


func _press(action: String) -> void:
	if held.get(action, false):
		return
	held[action] = true
	Input.action_press(action)
	_log({"ev": "press", "action": action})


func _release(action: String) -> void:
	if not held.get(action, false):
		return
	held[action] = false
	Input.action_release(action)
	_log({"ev": "release", "action": action})


func _release_all() -> void:
	for a in held.keys():
		_release(a)


func _key(code: Key) -> void:
	for pressed in [true, false]:
		var ev := InputEventKey.new()
		ev.physical_keycode = code
		ev.keycode = code
		ev.pressed = pressed
		Input.parse_input_event(ev)
	_log({"ev": "key_tap", "key": OS.get_keycode_string(code)})


## Hold exactly the movement keys for one of 8 directions (or none).
func _move(dir_name: String) -> void:
	var want := {}
	if dir_name != "":
		for part in dir_name.split("_"):
			want["move_" + part] = true
	for a in ["move_up", "move_down", "move_left", "move_right"]:
		if want.get(a, false):
			_press(a)
		else:
			_release(a)


func _dir_name(v: Vector2) -> String:
	var best := ""
	var best_dot := -2.0
	var names := ["right", "down_right", "down", "down_left", "left", "up_left", "up", "up_right"]
	for i in 8:
		var d: Vector2 = DIRS8[i].normalized()
		var dd := d.dot(v.normalized())
		if dd > best_dot:
			best_dot = dd
			best = names[i]
	return best


func _shoot_when(ok: bool, gap_ticks: int) -> void:
	if fire_held and main.audio.count("fire") > int(last_counts.get("_fire_seen", 0)):
		last_counts["_fire_seen"] = main.audio.count("fire")
		last_shot_tick = tick
		_set_fire(false)
		return
	_set_fire(ok and tick - last_shot_tick >= gap_ticks)


func _set_fire(on: bool) -> void:
	if on and not fire_held:
		fire_held = true
		_press("fire")
	elif not on and fire_held:
		fire_held = false
		_release("fire")


func _warp_aim() -> void:
	var vp := get_viewport()
	vp.warp_mouse(vp.get_canvas_transform() * aim_world)


## Point the aim so the shell line (which starts at the muzzle) passes through `target`.
func _aim_at(target: Vector2) -> void:
	var p = main.player
	var ppos: Vector2 = p.global_position
	var pivot: Vector2 = ppos + TURRET_OFFSET
	var d: Vector2 = (target - ppos).normalized()
	for i in 4:
		var ground := Vector2(d.x, d.y / SIN_E).normalized()
		var muzzle: Vector2 = ppos + Vector2(ground.x, ground.y * SIN_E) * BARREL_LEN
		d = (target - muzzle).normalized()
	aim_world = pivot + d * 220.0


func _lead(e) -> Vector2:
	var p = main.player
	var t := 0.0
	var ppos: Vector2 = p.global_position
	var epos: Vector2 = e.global_position
	var evel: Vector2 = e.velocity
	var pos: Vector2 = epos
	for i in 4:
		t = ppos.distance_to(pos) / SHELL_SPEED
		pos = epos + evel * t
	return pos


func _clear_line(from: Vector2, to: Vector2, target) -> bool:
	var q := PhysicsRayQueryParameters2D.create(from, to, 1 | 2, [main.player.get_rid()])
	var hit: Dictionary = main.player.get_world_2d().direct_space_state.intersect_ray(q)
	return hit.is_empty() or hit.collider == target


func _living_enemies() -> Array:
	return main.enemies.filter(func(e): return not e.is_dead)


func _observe() -> void:
	var a = main.audio
	for k in a.counts:
		var c: int = a.counts[k]
		if c != int(last_counts.get(k, 0)):
			_log({"ev": "sound_request", "key": k, "count": c})
			last_counts[k] = c
	var ms := "paused" if a.music.stream_paused else ("playing" if a.music.playing else "stopped")
	if ms != last_music:
		_log({"ev": "music_state", "state": ms, "pos_s": a.music.get_playback_position()})
		last_music = ms
	var p = main.player
	if p.health != last_hp:
		_log({"ev": "player_health", "hp": p.health, "smoke": p.smoke.emitting, "flames": p.flames.emitting})
		last_hp = p.health
	if p.is_dead != last_dead:
		if p.is_dead:
			deaths += 1
		_log({"ev": "player_dead" if p.is_dead else "player_respawned", "deaths": deaths,
			"pos": [p.global_position.x, p.global_position.y], "music_playing": a.music.playing})
		last_dead = p.is_dead
	for c in main.actors.get_children():
		if c.has_method("take_hit"):
			var key := str(c.position)
			if int(last_cover_stage.get(key, 0)) != c.stage or not last_cover_stage.has(key):
				if last_cover_stage.has(key) or c.stage != 0:
					_log({"ev": "cover_stage", "cover": [c.position.x, c.position.y], "stage": c.stage, "hits": c.hits})
				last_cover_stage[key] = c.stage
	for i in main.enemies.size():
		var e = main.enemies[i]
		if e.is_dead and not last_enemy_dead.get(i, false):
			kills += 1
			_log({"ev": "enemy_destroyed", "enemy": i, "kills": kills, "pos": [e.global_position.x, e.global_position.y]})
			last_enemy_dead[i] = true


func _go(new_phase: String) -> void:
	_log({"ev": "phase_end", "next": new_phase})
	phase = new_phase
	phase_tick = 0
	_log({"ev": "phase_start"})


func _physics_process(delta: float) -> void:
	if main == null:
		var s = get_tree().current_scene
		if s != null and s.name == "Main" and s.player != null:
			main = s
			_log({"ev": "attached", "viewport": [get_viewport().get_visible_rect().size.x, get_viewport().get_visible_rect().size.y],
				"window": [get_window().size.x, get_window().size.y]})
			aim_world = main.player.global_position + Vector2.RIGHT.rotated(-0.6) * 220.0
			_go("intro")
		return
	tick += 1
	phase_tick += 1
	_observe()
	if tick > timeout_ticks:
		_fail("timeout in phase " + phase)
		return
	match phase:
		"intro":
			_intro()
		"tour":
			_tour(delta)
		"break_cover":
			_break_cover()
		"fight":
			_fight()
		"pause":
			_pause()
		"victory_hold":
			_victory_hold()
	_warp_aim()
	if phase_tick % 30 == 0:
		var p = main.player
		_log({"ev": "aim_check", "aim_world": [aim_world.x, aim_world.y],
			"mouse_world": [p.get_global_mouse_position().x, p.get_global_mouse_position().y],
			"pos": [p.global_position.x, p.global_position.y], "hp": p.health})


## Idle at the spawn: no keys held; the cursor sweeps slowly so the turret turns while the hull rests.
func _intro() -> void:
	var p = main.player
	var ang := -0.6 + 0.9 * sin(phase_tick / 60.0 * 1.1)
	aim_world = p.global_position + TURRET_OFFSET + Vector2.RIGHT.rotated(ang) * 220.0
	if phase_tick >= 60 * 5:
		_go("tour")
		tour_leg = 0
		tour_left = TOUR[0][1]


## Drive one short leg in each of the 8 facings (keys only); the turret keeps aiming ahead-right.
func _tour(delta: float) -> void:
	var p = main.player
	aim_world = p.global_position + TURRET_OFFSET + Vector2(220, -60)
	if tour_stop > 0.0:
		_move("")
		tour_stop -= delta
		if tour_stop <= 0.0:
			tour_leg += 1
			if tour_leg >= TOUR.size():
				_go("break_cover")
				return
			tour_left = TOUR[tour_leg][1]
		return
	_move(TOUR[tour_leg][0])
	tour_left -= delta
	if tour_left <= 0.0:
		_move("")
		tour_stop = 0.5


## Shoot the nearest intact cover until it is broken (2 hits cracked, 4 hits broken).
func _break_cover() -> void:
	var p = main.player
	var best = null
	for c in main.actors.get_children():
		if c.has_method("take_hit") and (best == null or p.global_position.distance_to(c.position) < p.global_position.distance_to(best.position)):
			best = c
	if best.stage >= 2:
		_set_fire(false)
		if phase_tick > 60 * 9:
			_fail("cover never broke")
		_go("fight")
		return
	_aim_at(best.position)
	var aimed: float = absf(wrapf(p.aim_angle - (aim_world - (p.global_position + TURRET_OFFSET)).angle(), -PI, PI))
	_shoot_when(aimed < 0.05, 84)
	if phase_tick > 60 * 12:
		_fail("break_cover timeout")


## Engage: pick the nearest living enemy with a clear shell line, lead it, fire. Hold position in the
## open (no hiding) so the enemies' return fire lands; reposition when no enemy is in line.
func _fight() -> void:
	var p = main.player
	if main.level_won:
		_set_fire(false)
		_move("")
		victory_tick = tick
		_go("victory_hold")
		return
	if p.is_dead:
		_set_fire(false)
		_move("")
		return
	if kills >= 1 and not paused_done and p.health > 0 and phase_tick > 60:
		_set_fire(false)
		_move("")
		_go("pause")
		return
	var target = null
	var target_pt := Vector2.ZERO
	var best_d := 1e9
	for e in _living_enemies():
		var pt := _lead(e)
		var d: float = p.global_position.distance_to(e.global_position)
		if d < best_d and _clear_line(p.muzzle_position(), pt, e) and _clear_line(p.global_position, e.global_position, e):
			best_d = d
			target = e
			target_pt = pt
	if target == null:
		# No clear line: drive toward the nearest living enemy's side of the arena.
		var near = null
		for e in _living_enemies():
			if near == null or p.global_position.distance_to(e.global_position) < p.global_position.distance_to(near.global_position):
				near = e
		if near == null:
			_move("")
			return
		_aim_at(near.global_position)
		_set_fire(false)
		var to: Vector2 = near.global_position - p.global_position
		var side := Vector2(-to.y, to.x).normalized() * (1.0 if (tick / 240) % 2 == 0 else -1.0)
		_move(_dir_name(to.normalized() * 0.6 + side))
		return
	_move("")
	_aim_at(target_pt)
	var aimed: float = absf(wrapf(p.aim_angle - (aim_world - (p.global_position + TURRET_OFFSET)).angle(), -PI, PI))
	_shoot_when(aimed < 0.04 and best_d < 760.0, 96)


## Pause for 2.5 s (Esc), then resume (Esc).
func _pause() -> void:
	if phase_tick == 20:
		_key(KEY_ESCAPE)
	if phase_tick == 20 + 150:
		_key(KEY_ESCAPE)
	if phase_tick == 20 + 150 + 20:
		if main.paused:
			_fail("did not resume")
			return
		paused_done = true
		_go("fight")


## Hold on the victory panel while the victory sound plays out, then quit cleanly.
func _victory_hold() -> void:
	if phase_tick >= 60 * 8:
		var ok: bool = main.level_won and deaths >= 1 and kills == main.enemies.size() and main.audio.count("victory") == 1
		_log({"ev": "assert_end", "ok": ok, "deaths": deaths, "kills": kills, "counts": main.audio.counts})
		_release_all()
		if not ok:
			_fail("end assertions failed")
			return
		_log({"ev": "DONE"})
		get_tree().quit(0)
