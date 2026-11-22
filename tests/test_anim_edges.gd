extends SceneTree
## A7 edge tests for the `shoot` phase boundaries (CHANGE-BRIEF phase table, interrupts table,
## Revisions 2026-11-21 "shot captured on the press tick" and "FIRING guard").
## Drives the real scenes/main.tscn through the real loop, as tests/test_anim_states.gd does.
## Firing goes only through Input.parse_input_event; take_damage() and the reload_left = 0.0 write
## are the only direct calls into the game.
## Run: bash scripts/run-test.sh test_anim_edges.gd 60     (also 30, 144)
##
## Tick convention (same as test_anim_states.gd). The script resumes on physics_frame at the start
## of tick k, before the nodes run tick k; a snapshot taken at resume k shows the result of tick k-1.
## The press tick P is the first tick the player's weapon is FIRING, detected from the game, because
## the input latency differs between --fixed-fps values. rel = tick - P. A call scheduled for rel r
## is made at the resume just before tick P + r runs ("injected on P + r").
##
## The boundaries are derived from tank.gd's SHOOT_FPS, SHOOT_ACTIVE_FRAME, SHOOT_END_FRAME and
## Engine.physics_ticks_per_second, not hard-coded:
##   startup -> active    = ticks(SHOOT_ACTIVE_FRAME)
##   active -> recovery   = ticks(SHOOT_ACTIVE_FRAME + 1)   (the active phase is one frame)
##   recovery -> end      = ticks(SHOOT_END_FRAME)
##
## Second "fire" press (case c). The first press is injected at resume 0 and released at the first
## resume where Input reports it held. The second press is injected at resume r, r ticks after the
## first injection, so with the same latency it is seen on P + r; it is released at the first resume
## after its injection where Input reports it held. The tick the game actually polls it ("seen") is
## read from Input.is_action_pressed("fire") at each resume and printed: at --fixed-fps 30 input is
## flushed once per two physics ticks, so some target ticks are not reachable and the press lands
## on a neighbour (or merges with the first press). The expectation is computed from the held ticks
## the game saw: the second shot starts on the first held tick >= P + end boundary, or not at all.

const TOTAL := 36            # resumes per scenario; rel reaches ~33, less than the 48-tick reload

var passed := 0
var failed := 0
var shell_script: Script
var B_ACTIVE: int            # startup -> active (shell tick)
var B_RECOVERY: int          # active -> recovery
var B_END: int               # recovery -> end (weapon READY)
var FIRING: int
var READY: int


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
	await physics_frame


## One scenario. opts:
##   release_first (bool)  release the first press at the first resume it is seen held (else held all window)
##   second_resume (int)   absolute resume at which a second "fire" press is injected (-1 = none)
##   force_reload0 (bool)  reload_left = 0.0 at every resume k > 0 (as test_anim_states.gd G1)
##   actions {rel: Callable}
##   force_after_action (bool) reload_left = 0.0 at every resume from the action's resume on
## Returns {snaps, held (tick -> bool), press_tick}.
func _scenario(main: Node, opts: Dictionary) -> Dictionary:
	var p = main.player
	var audio = main.audio
	var fire_anim: AnimationPlayer = p.get_node("FireAnim")
	var shell_ids := []
	var muzzle_ids := []
	var sounds0: int = audio.count("fire")
	var snaps := []
	var held := {}
	var press_tick := -1
	var pending_release := false
	var second_resume: int = opts.get("second_resume", -1)
	var actions: Dictionary = opts.get("actions", {})
	var force_from_k := 1 if opts.get("force_reload0", false) else 1 << 30
	for k in TOTAL:
		await physics_frame
		for n in main.fx_layer.get_children():
			var id: int = n.get_instance_id()
			if n.get_script() == shell_script and not shell_ids.has(id):
				shell_ids.append(id)
			elif n is CPUParticles2D and not muzzle_ids.has(id):
				muzzle_ids.append(id)
		if press_tick < 0 and k > 0 and p._weapon == FIRING:
			press_tick = k - 1
		snaps.append({
			"tick": k - 1, "shells": shell_ids.size(), "muzzles": muzzle_ids.size(),
			"sounds": audio.count("fire") - sounds0, "weapon": p._weapon,
			"fire_playing": fire_anim.is_playing(),
			"fire_pos": fire_anim.current_animation_position if fire_anim.is_playing() else -1.0,
			"dead": p.is_dead, "health": p.health,
			"reload_full": is_equal_approx(p.reload_left, p.reload_time),
		})
		# The fire state the player polls on tick k (input is flushed before the physics ticks).
		var is_held := Input.is_action_pressed("fire")
		held[k] = is_held
		if k == 0:
			_inject("fire", true)
			pending_release = opts.get("release_first", false)
		else:
			if pending_release and is_held:
				_inject("fire", false)
				pending_release = false
			if k == second_resume:
				_inject("fire", true)
				pending_release = true
		if press_tick >= 0 and actions.has(k - press_tick):
			actions[k - press_tick].call()
			if opts.get("force_after_action", false):
				force_from_k = k
		if k >= force_from_k:
			p.reload_left = 0.0
	_inject("fire", false)
	for s in snaps:
		s["rel"] = s["tick"] - press_tick if press_tick >= 0 else -999
	return {"snaps": snaps, "held": held, "press_tick": press_tick}


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


func _first(snaps: Array, key: String, value, from_rel: int) -> int:
	for s in snaps:
		if s["rel"] >= from_rel and s[key] == value:
			return s["rel"]
	return -999


## Relative ticks on which a shot started (try_fire set the reload to full on that tick).
func _starts(snaps: Array) -> Array:
	var out := []
	for s in snaps:
		if s["rel"] >= 0 and s["reload_full"]:
			out.append(s["rel"])
	return out


func _ticks(frame: int, fps: float) -> int:
	return int(round(frame * Engine.physics_ticks_per_second / fps))


func _run() -> void:
	shell_script = load("res://scripts/shell.gd")
	var Tank = load("res://scripts/tank.gd")
	FIRING = Tank.Weapon.FIRING
	READY = Tank.Weapon.READY
	var fps: float = Tank.SHOOT_FPS
	B_ACTIVE = _ticks(Tank.SHOOT_ACTIVE_FRAME, fps)
	B_RECOVERY = _ticks(Tank.SHOOT_ACTIVE_FRAME + 1, fps)
	B_END = _ticks(Tank.SHOOT_END_FRAME, fps)
	_info("physics ticks per second = %d, max_fps = %d; SHOOT_FPS=%.1f ACTIVE_FRAME=%d END_FRAME=%d" % [
		Engine.physics_ticks_per_second, Engine.max_fps, fps, Tank.SHOOT_ACTIVE_FRAME, Tank.SHOOT_END_FRAME])
	_info("boundaries: startup->active P+%d, active->recovery P+%d, recovery->end P+%d" % [B_ACTIVE, B_RECOVERY, B_END])

	var boundaries := [["startup->active", B_ACTIVE], ["active->recovery", B_RECOVERY], ["recovery->end", B_END]]

	# ---- a) hit (non-fatal, the way shell.gd calls it) ----
	for b in boundaries:
		for off in [-1, 0, 1]:
			var r: int = b[1] + off
			var main = await _new_game()
			var pl = main.player
			var src = main.enemies[0]
			var amount: int = src.shell_damage
			var res: Dictionary = await _scenario(main, {"actions": {r: func(): pl.take_damage(amount, src)}})
			var snaps: Array = res["snaps"]
			var hit_rel := -999
			for s in snaps:
				if s["rel"] >= 0 and s["health"] < snaps[0]["health"]:
					hit_rel = s["rel"]
					break
			var shells := _rises(snaps, "shells")
			var ready_rel := _first(snaps, "weapon", READY, 1)
			var ok: bool = res["press_tick"] >= 0 and hit_rel == r and not snaps[-1]["dead"] \
				and snaps[-1]["health"] < snaps[0]["health"] and shells == [B_ACTIVE] \
				and _all(snaps, 0, B_END - 1, "weapon", FIRING) and ready_rel == B_END
			_check("a-hit   %-16s injected P+%-2d | hit seen rel %d, shells %s, READY rel %d, health %d->%d | expect shell [%d] once, READY %d, health lower" % [
				b[0], r, hit_rel, str(shells), ready_rel, snaps[0]["health"], snaps[-1]["health"], B_ACTIVE, B_END], ok,
				"" if res["press_tick"] >= 0 else "press tick not found")
			await _free_game(main)

	# ---- b) death (fatal); fire held the whole window. From the death on, reload_left is held at
	# 0.0 so only is_dead can stop a new shot. ----
	for b in boundaries:
		for off in [-1, 0, 1]:
			var r: int = b[1] + off
			var main = await _new_game()
			var pl = main.player
			var res: Dictionary = await _scenario(main, {"force_after_action": true,
				"actions": {r: func(): pl.take_damage(100000)}})
			var snaps: Array = res["snaps"]
			var dead_rel := _first(snaps, "dead", true, 0)
			var shells := _rises(snaps, "shells")
			var sounds := _rises(snaps, "sounds")
			var starts := _starts(snaps)
			var ready_rel := _first(snaps, "weapon", READY, 1)
			var ok: bool = res["press_tick"] >= 0 and dead_rel == r and shells == [B_ACTIVE] and sounds == [B_ACTIVE] \
				and _all(snaps, 0, B_END - 1, "weapon", FIRING) and ready_rel == B_END \
				and _all(snaps, B_END, 999, "weapon", READY) and starts == [0]
			_check("b-death %-16s injected P+%-2d | dead seen rel %d, shells %s, sounds %s, READY rel %d, starts %s | expect shell [%d] once, READY %d and stays, no new start (fire held, reload 0)" % [
				b[0], r, dead_rel, str(shells), str(sounds), ready_rel, str(starts), B_ACTIVE, B_END], ok,
				"" if res["press_tick"] >= 0 else "press tick not found")
			await _free_game(main)

	# ---- c) second "fire" press, reload held at 0.0, so only the FIRING guard decides ----
	for b in boundaries:
		for off in [-1, 0, 1]:
			var r: int = b[1] + off
			var main = await _new_game()
			var res: Dictionary = await _scenario(main, {"release_first": true, "second_resume": r, "force_reload0": true})
			var snaps: Array = res["snaps"]
			var P: int = res["press_tick"]
			var held: Dictionary = res["held"]
			var held_rel := []
			for t in held:
				if held[t]:
					held_rel.append(t - P)
			# First tick after the injection on which the game polled "fire" held.
			var seen := -999
			for t in held:
				if t > r and held[t]:
					seen = t - P
					break
			# Expectation from the held ticks: a new shot on the first held tick >= B_END.
			var exp_start := -999
			for t in held:
				if held[t] and t - P >= B_END and t - P + B_ACTIVE <= snaps[-1]["rel"]:
					exp_start = t - P
					break
			var exp_shells := [B_ACTIVE] if exp_start == -999 else [B_ACTIVE, exp_start + B_ACTIVE]
			var exp_starts := [0] if exp_start == -999 else [0, exp_start]
			var shells := _rises(snaps, "shells")
			var starts := _starts(snaps)
			var end_first := -999
			for s in snaps:
				if s["rel"] >= 1 and (s["weapon"] == READY or s["reload_full"]):
					end_first = s["rel"]
					break
			var pos_ok := true
			var prev := -1.0
			for s in snaps:
				if s["rel"] >= 0 and s["rel"] <= B_END - 1:
					if not s["fire_playing"] or s["fire_pos"] < prev:
						pos_ok = false
					prev = s["fire_pos"]
			var rule := "in FIRING: no shell, no restart" if seen != -999 and seen < B_END else "seen on/after end: new shot"
			if seen != -999 and seen <= 0:
				rule = "merged with the first press"
			var ok: bool = P >= 0 and shells == exp_shells and starts == exp_starts and end_first == B_END \
				and _all(snaps, 0, B_END - 1, "weapon", FIRING) and pos_ok
			var ready_rel := _first(snaps, "weapon", READY, 1)
			_check("c-fire  %-16s injected P+%-2d | seen rel %d (held rels %s), shells %s, starts %s, first shot ends rel %d, READY rel %d | expect (%s) shells %s, starts %s, first shot ends %d" % [
				b[0], r, seen, str(held_rel), str(shells), str(starts), end_first, ready_rel, rule, str(exp_shells), str(exp_starts), B_END], ok,
				"" if pos_ok else "shoot restarted or stopped during FIRING")
			if exp_start != -999:
				var line := ""
				for s in snaps:
					if s["rel"] >= exp_start - 1 and s["rel"] <= exp_start + 2:
						line += " rel%d=%.4f" % [s["rel"], s["fire_pos"]]
				_info("  FireAnim position around the second start:%s" % line)
			await _free_game(main)

	print("RESULT: %d passed, %d failed" % [passed, failed])
	quit(1 if failed > 0 else 0)
