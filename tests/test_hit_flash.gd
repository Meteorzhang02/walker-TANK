extends SceneTree
## A5 hit flash: checks CHANGE-BRIEF.md section 2 rules 1-7 and the shader interface through the
## real main scene and game loop. Hits go through the game's damage path (a shell fired by
## try_fire(), or take_damage(damage, shooter) as shell.gd calls it); hit_amount is only read.
##   bash scripts/run-test.sh test_hit_flash.gd 30   (also 60 and 144)

const SHADER_PATH := "res://shaders/hit_flash.gdshader"
const D := 0.5
const EPS := 1e-4

var failures := 0
var passes := 0
var sampler: Sampler
var events := []  # {kind, idx}: idx is the index of the first sample taken after the signal
var main
var p
var flash_modulate := Color()


## Records hit_amount once per frame after the driver has run (high process_priority).
## Runs while paused. t is game time: the sum of the deltas of the unpaused frames before it.
class Sampler extends Node:
	var material: ShaderMaterial
	var samples := []
	var game_t := 0.0
	var dt := 0.0

	func _ready() -> void:
		process_mode = Node.PROCESS_MODE_ALWAYS
		process_priority = 1000

	func _process(delta: float) -> void:
		dt = delta
		var paused := get_tree().paused
		var v = material.get_shader_parameter("hit_amount") if material else null
		samples.append({"t": game_t, "v": v, "paused": paused})
		if not paused:
			game_t += delta


func _initialize() -> void:
	_run.call_deferred()


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if ok:
		passes += 1
	else:
		failures += 1


func _finish() -> void:
	print("RESULT: %d passed, %d failed" % [passes, failures])
	if main:
		main.queue_free()
	if sampler:
		sampler.queue_free()
	await process_frame
	quit(1 if failures > 0 else 0)


func _v(i: int) -> float:
	var v = sampler.samples[i].v
	return -1.0 if v == null else float(v)


func _now_t() -> float:
	return sampler.game_t


## Waits until `sec` of game time (unpaused) has passed since game time `from_t`.
func _wait_game(from_t: float, sec: float) -> void:
	var guard := 0
	while _now_t() - from_t < sec - 1e-9 and guard < 2000:
		await process_frame
		guard += 1


func _on_damaged(_t, _a) -> void:
	events.append({"kind": "damaged", "idx": sampler.samples.size()})
	flash_modulate = p.modulate


func _on_destroyed(_t) -> void:
	events.append({"kind": "destroyed", "idx": sampler.samples.size()})


func _hit() -> int:
	var idx: int = sampler.samples.size()
	# The way shell.gd calls it: body.take_damage(damage, shooter).
	p.take_damage(main.enemies[0].shell_damage, main.enemies[0])
	return idx


## From sample `s` (value 1.0): linear fall on game time, paused samples hold, first 0.0 at
## D +- one frame period, then 0.0 up to sample `end` (exclusive). With full = false the fade is
## cut short at `end` (retrigger / fatal hit) and only the shape up to there is checked.
func _check_fade(s: int, end: int, label: String, full := true) -> void:
	var lin := true
	var holds := true
	var n_paused := 0
	var zero_idx := -1
	for k in range(s + 1, end):
		var smp = sampler.samples[k]
		var v := _v(k)
		if smp.paused:
			n_paused += 1
			if absf(v - _v(k - 1)) > EPS:
				holds = false
			continue
		var expect := maxf(0.0, 1.0 - (smp.t - sampler.samples[s].t) / D)
		if expect < 1e-6:
			expect = 0.0
		if zero_idx < 0:
			if absf(v - expect) > EPS:
				lin = false
			if v == 0.0:
				zero_idx = k
	_check("%s: falls linearly on game time (1 - t/D)" % label, lin)
	if n_paused > 0:
		_check("%s: holds its value on all %d paused frames" % [label, n_paused], holds)
	if not full:
		_check("%s: still above 0.0 when cut short" % label, zero_idx < 0)
		return
	if zero_idx < 0:
		_check("%s: reaches 0.0" % label, false)
		return
	var dur: float = sampler.samples[zero_idx].t - sampler.samples[s].t
	var tol: float = sampler.dt + 1e-6
	_check("%s: reaches 0.0 after %.4f s game time (D = 0.5 +- %.4f)" % [label, dur, tol], absf(dur - D) <= tol)
	var stays := true
	for k in range(zero_idx, end):
		if _v(k) != 0.0:
			stays = false
	_check("%s: stays 0.0 for %d frames after" % [label, end - zero_idx], stays and end - zero_idx > 5)


func _parse_source_uniforms(src: String) -> Dictionary:
	var out := {}
	var re := RegEx.new()
	re.compile("uniform\\s+(\\w+)\\s+(\\w+)\\s*(?::\\s*([^=;]+?))?\\s*(?:=\\s*([^;]+?))?\\s*;")
	var lines := []
	for line in src.split("\n"):
		lines.append(line.split("//")[0])
	for m in re.search_all("\n".join(lines)):
		out[m.get_string(2)] = {"type": m.get_string(1), "hint": m.get_string(3).strip_edges(), "default": m.get_string(4).strip_edges()}
	return out


func _floats(s: String) -> Array:
	var re := RegEx.new()
	re.compile("(?<![\\w.])-?\\d+(?:\\.\\d+)?")  # not the 4 in vec4
	return re.search_all(s).map(func(m): return float(m.get_string()))


func _same_floats(a: Array, b: Array) -> bool:
	if a.size() != b.size():
		return false
	for i in a.size():
		if absf(a[i] - b[i]) > 1e-6:
			return false
	return true


func _run() -> void:
	# --- Interface: the shader exists, compiles to the declared uniforms, defaults match the brief.
	var shader_ok := ResourceLoader.exists(SHADER_PATH)
	_check("shader file exists: " + SHADER_PATH, shader_ok)
	var shader: Shader = load(SHADER_PATH) if shader_ok else null
	_check("shader loads as a Shader resource", shader != null)
	if shader == null:
		await _finish()
		return
	var ulist := {}
	for u in shader.get_shader_uniform_list():
		ulist[u.name] = u
		print("      uniform: %s" % u)
	_check("get_shader_uniform_list() is non-empty (shader compiled)", ulist.size() > 0)
	_check("hit_amount: float with hint_range", ulist.has("hit_amount") and ulist.hit_amount.type == TYPE_FLOAT and ulist.hit_amount.hint == PROPERTY_HINT_RANGE)
	_check("flash_color: vec4 source_color (reported as Color)", ulist.has("flash_color") and ulist.flash_color.type == TYPE_COLOR)
	_check("flash_strength: float with hint_range", ulist.has("flash_strength") and ulist.flash_strength.type == TYPE_FLOAT and ulist.flash_strength.hint == PROPERTY_HINT_RANGE)

	var src := FileAccess.get_file_as_string(SHADER_PATH)
	var su := _parse_source_uniforms(src)
	_check("source: shader_type canvas_item", src.contains("shader_type canvas_item;"))
	_check("source: hit_amount float hint_range(0.0, 1.0) = 0.0",
		su.has("hit_amount") and su.hit_amount.type == "float" and su.hit_amount.hint.begins_with("hint_range")
		and _same_floats(_floats(su.hit_amount.hint), [0.0, 1.0]) and _same_floats(_floats(su.hit_amount.default), [0.0]))
	_check("source: flash_color vec4 source_color = vec4(1.0, 0.0, 0.0, 1.0)",
		su.has("flash_color") and su.flash_color.type == "vec4" and su.flash_color.hint == "source_color"
		and _same_floats(_floats(su.flash_color.default), [1.0, 0.0, 0.0, 1.0]))
	_check("source: flash_strength float hint_range(0.0, 1.0) = 0.6",
		su.has("flash_strength") and su.flash_strength.type == "float" and su.flash_strength.hint.begins_with("hint_range")
		and _same_floats(_floats(su.flash_strength.hint), [0.0, 1.0]) and _same_floats(_floats(su.flash_strength.default), [0.6]))

	# --- Real main scene and game loop.
	main = load("res://scenes/main.tscn").instantiate()
	root.add_child(main)
	await process_frame
	await physics_frame
	p = main.player
	# Test setup: freeze the enemy AI so no unplanned shells reach YunqiZ (their nodes stay intact).
	for e in main.enemies:
		e.process_mode = Node.PROCESS_MODE_DISABLED

	var driver = p.get_node_or_null("HitFlashDriver")
	_check("driver node exists under YunqiZ", driver != null)
	if driver == null:
		await _finish()
		return
	for pn in driver.SET_PARAMS:
		_check("shader declares every uniform the driver sets: " + pn, ulist.has(pn))

	# Rule 7: one shared ShaderMaterial on YunqiZ, none on the enemies.
	var mat = p.hull.material
	_check("rule 7: hull has a ShaderMaterial using " + SHADER_PATH, mat is ShaderMaterial and mat.shader == shader)
	_check("rule 7: hull and turret return the same material object", mat != null and is_same(p.hull.material, p.turret.material))
	var enemy_clean := true
	for e in main.enemies:
		for s in [e.hull, e.turret]:
			if s.material is ShaderMaterial:
				enemy_clean = false
	_check("rule 7: no enemy sprite has a ShaderMaterial", enemy_clean)

	sampler = Sampler.new()
	sampler.material = mat
	root.add_child(sampler)
	p.damaged.connect(_on_damaged)
	p.destroyed.connect(_on_destroyed)
	await _wait_game(_now_t(), 0.1)
	_check("hit_amount is 0.0 before any hit", _v(sampler.samples.size() - 1) == 0.0)

	# --- Phase 1: a real shell from the game's firing code. Rules 1, 2, 4.
	var e0 = main.enemies[0]
	e0.global_position = p.global_position + Vector2(110, 0)
	e0.aim_angle = PI
	e0.reload_left = 0.0
	_check("enemy try_fire() spawns a shell toward YunqiZ", e0.try_fire())
	var t0 := _now_t()
	while events.is_empty() and _now_t() - t0 < 1.0:
		await process_frame
	_check("the shell hits YunqiZ (damaged emitted, health 75)", events.size() == 1 and p.health == 75)
	if events.is_empty():
		await _finish()
		return
	var h1: int = events[0].idx
	await _wait_game(_now_t(), D + 0.4)
	_check("existing white _flash() still runs (modulate 2.2 at the signal)", flash_modulate.is_equal_approx(Color(2.2, 2.2, 2.2)))
	_check("rule 1: first sampled frame after the shell hit is 1.0", _v(h1) == 1.0)
	_check_fade(h1, sampler.samples.size(), "rule 2 (shell hit)")

	# --- Phase 2: hit, pause mid-fade (rule 5), retrigger at 0.4 s (rule 3), fatal hit mid-fade (rule 6).
	var h2 := _hit()
	var h2_t := _now_t()
	_check("phase 2 hit lands (health 50)", p.health == 50)
	await _wait_game(h2_t, 0.2)
	var before_pause := _v(sampler.samples.size() - 1)
	main._set_paused(true)
	for i in 12:
		await process_frame
	main._set_paused(false)
	await process_frame
	await process_frame
	var resumed := _v(sampler.samples.size() - 1)
	_check("rule 5: value before pause is mid-fade (%.4f)" % before_pause, before_pause > 0.0 and before_pause < 1.0)
	_check("rule 5: value decreases again after unpause (%.4f -> %.4f)" % [before_pause, resumed], resumed < before_pause - EPS)
	await _wait_game(h2_t, 0.4)
	var r2 := _hit()
	var r2_t := _now_t()
	_check("rule 3: retrigger at %.3f s lands (invuln over, health 25)" % (r2_t - h2_t), p.health == 25 and r2_t - h2_t > 0.3 and r2_t - h2_t < 0.5)
	await process_frame
	await process_frame
	_check("rule 3: value just before the retrigger was mid-fade (%.4f)" % _v(r2 - 1), _v(r2 - 1) > 0.0 and _v(r2 - 1) < 1.0)
	_check("rule 3: first sampled frame after the retrigger is 1.0", _v(r2) == 1.0)
	var paused_n := 0
	for k in range(h2, r2):
		if sampler.samples[k].paused:
			paused_n += 1
	_check("rule 5: %d paused frames recorded during the fade" % paused_n, paused_n >= 12)
	_check_fade(h2, r2, "rule 2/5 (fade with pause, before retrigger)", false)

	await _wait_game(r2_t, 0.4)
	var before_fatal := _v(sampler.samples.size() - 1)
	var f := _hit()
	_check("rule 6: fatal hit -> destroyed emitted, damaged not", p.is_dead and events[-1].kind == "destroyed")
	await process_frame
	await process_frame
	_check("rule 6: value mid-fade before the fatal hit (%.4f)" % before_fatal, before_fatal > 0.0)
	_check("rule 6: first sampled frame after the fatal hit is 0.0", _v(f) == 0.0)
	_check_fade(r2, f, "rule 3 (fade after retrigger, until fatal hit)", false)

	# Respawn through main's own path (_on_player_destroyed -> reset_full(SPAWN) after 2 s).
	var dt0 := _now_t()
	while p.is_dead and _now_t() - dt0 < 3.0:
		await process_frame
	await process_frame
	_check("YunqiZ respawned via reset_full() (health %d)" % p.health, not p.is_dead and p.health == p.max_health)
	var zero_dead := true
	for k in range(f, sampler.samples.size()):
		if _v(k) != 0.0:
			zero_dead = false
	_check("rule 6: 0.0 on every frame from destroyed through reset_full()", zero_dead)

	# --- Phase 3: after respawn (invuln 1.0 s), hit then retrigger at 0.45 s, full fade from the retrigger.
	await _wait_game(_now_t(), 1.1)
	var h3 := _hit()
	var h3_t := _now_t()
	_check("phase 3 hit lands after respawn (health 75)", p.health == 75)
	await _wait_game(h3_t, 0.45)
	var r3 := _hit()
	_check("rule 3: second retrigger lands (health 50)", p.health == 50)
	await _wait_game(_now_t(), D + 0.4)
	_check("rule 1: first sampled frame after the phase 3 hit is 1.0", _v(h3) == 1.0)
	_check("rule 3: value before the retrigger was mid-fade (%.4f)" % _v(r3 - 1), _v(r3 - 1) > 0.0 and _v(r3 - 1) < 1.0)
	_check("rule 3: restarts at 1.0", _v(r3) == 1.0)
	_check_fade(r3, sampler.samples.size(), "rule 2/3 (full fade from retrigger)")

	# Rule 7 again at the end, and the gameplay-facing state the driver must not touch.
	enemy_clean = true
	for e in main.enemies:
		for s in [e.hull, e.turret]:
			if s.material != null:
				enemy_clean = false
	_check("rule 7: enemy sprites still have no material at the end", enemy_clean)
	_check("rule 7: hull and turret still share one material", is_same(p.hull.material, p.turret.material) and is_same(p.hull.material, mat))
	print("      frame period %.5f s, %d samples" % [sampler.dt, sampler.samples.size()])
	await _finish()
