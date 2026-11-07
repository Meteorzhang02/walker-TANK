extends SceneTree
## Headless CPU price of Effects A and B (CHANGE-BRIEF.md, "Price predictions and budget").
## Run: ./scripts/run-test.sh cost_particles.gd realtime 300
##
## The cost, read once per frame in ms: Performance.TIME_PROCESS (the last frame's process step) and
## Performance.TIME_PHYSICS_PROCESS (the last physics step; physics ticks at its own rate, so on
## frames without a step the monitor repeats the last step's value). Neither includes the wait for
## the frame cap.
## Frame time = wall time between consecutive process_frame signals, in ms. It is kept for the report
## only: this headless run is capped at the display rate (6.9 ms, 144 Hz), so it reads flat.
## Each condition: 120 warm-up frames, then 600 measured frames. The four conditions run as one
## round, a b c d, and the round is repeated 3 times, so slow drift in the machine hits every
## condition alike.
##   (a) control: an empty Node2D as the only scene;
##   (b) res://scenes/main.tscn, both effects idle, as on load;
##   (c) main.tscn with Effect A at its peak, about 4 bursts alive at once;
##   (d) main.tscn with Effect B at its peak, the smoke on all 4 tanks emitting at amount_ratio 1.0.
## The COST line per condition pools the 3 x 600 frames (mean and sample standard deviation) of
## process and physics time; the FRAME line does the same for the capped frame time.
##
## Not a PASS/FAIL test: it always quits 0. run-test.sh turns a SCRIPT ERROR into exit 1.
## Headless uses a dummy renderer: nothing is drawn and no GPU particle process runs, so (d) prices
## only Effect B's CPU-side bookkeeping. Its GPU price is read in previews/price_scene.tscn.
##
## Cost-only setup writes (not gameplay, labelled where they happen): every enemy's target is set to
## null in (b), (c) and (d) alike, which freezes the AI (enemy.gd line 19: no movement, no fire) while
## the enemies and their smoke keep processing; (c) calls main.spawn_cover_burst(); (d) calls each
## tank's smoke.follow().

const SCENE := "res://scenes/main.tscn"
const BURST_SCENE := "res://effects/cover_hit_burst.tscn"
const WARMUP := 120
const FRAMES := 600
const ROUNDS := 3
const CONDITIONS := ["a_control", "b_game_idle", "c_effect_a_peak", "d_effect_b_peak"]
const METRICS := ["process", "physics", "frame"]

## (c): 4 fixed points on the top faces of 4 covers (main.gd COVERS[0..3], the fallback offset of R1).
const BURST_POINTS := [Vector2(320, 472), Vector2(300, 242), Vector2(560, 362), Vector2(820, 222)]
## (c): a burst lives about 0.77 s (Dust: lifetime 0.7, explosiveness 0.9). Two points every 0.35 s,
## alternating pairs, re-hit each point every 0.7 s and keep about 4 bursts alive at once.
const SPAWN_EVERY := 0.35
const BURSTS_PER_TICK := 2

var main
var samples := {}     # metric -> condition -> Array of per-frame values (ms), all rounds
var round_means := {} # metric -> condition -> Array of per-round means (ms)
var _tick := Callable()
var _spawn_left := 0.0
var _spawn_index := 0
var _alive_stats := []
var _alive := 0


func _initialize() -> void:
	for m in METRICS:
		samples[m] = {}
		round_means[m] = {}
		for c in CONDITIONS:
			samples[m][c] = []
			round_means[m][c] = []
	_run.call_deferred()


func _run() -> void:
	print("cost_particles: %d rounds x (%d warm-up + %d measured frames) per condition" % [ROUNDS, WARMUP, FRAMES])
	for r in ROUNDS:
		print("--- round %d" % (r + 1))
		# (a) control: an empty scene.
		var empty := Node2D.new()
		empty.name = "Empty"
		root.add_child(empty)
		await _measure("a_control", r)
		empty.queue_free()
		await process_frame

		main = load(SCENE).instantiate()
		root.add_child(main)
		await process_frame
		_alive = 0
		main.fx_layer.child_entered_tree.connect(_on_fx_child_entered)
		_freeze_enemy_ai()

		# (b) the game, both effects idle, as on load.
		await _measure("b_game_idle", r)

		# (c) Effect A at its peak.
		_spawn_left = 0.0
		_spawn_index = 0
		_tick = _tick_bursts
		await _run_for_seconds(1.0)  # reach the steady state of overlapping bursts before warm-up
		_alive_stats = []
		await _measure("c_effect_a_peak", r)
		_tick = Callable()
		_print_alive_stats()
		await _stop_bursts()

		# (d) Effect B at its peak.
		_smoke_peak()
		await _measure("d_effect_b_peak", r)
		await _stop_smoke()

		main.queue_free()
		main = null
		await process_frame
		await process_frame

	print("--- results (ms per frame, %d frames per condition)" % (ROUNDS * FRAMES))
	var means := {}
	var sds := {}
	for m in METRICS:
		means[m] = {}
		sds[m] = {}
		for c in CONDITIONS:
			var s: Array = samples[m][c]
			means[m][c] = _mean(s)
			sds[m][c] = _sd(s, means[m][c])
	for c in CONDITIONS:
		print("COST %s process %.4f sd %.4f physics %.4f sd %.4f" % [c, means.process[c], sds.process[c],
			means.physics[c], sds.physics[c]])
	_print_diff("b-a", "b_game_idle", "a_control", means)
	_print_diff("c-b", "c_effect_a_peak", "b_game_idle", means)
	_print_diff("d-b", "d_effect_b_peak", "b_game_idle", means)
	print("--- frame time, capped at the display rate (wait included), so flat across conditions")
	for c in CONDITIONS:
		print("FRAME %s mean %.4f sd %.4f" % [c, means.frame[c], sds.frame[c]])
	quit(0)


## Cost-only setup, the same in (b), (c) and (d): target = null makes each enemy's _think() hold
## still and never fire (enemy.gd line 19). The enemies keep processing, so their smoke runs too.
func _freeze_enemy_ai() -> void:
	for e in main.enemies:
		e.target = null


func _measure(cond: String, r: int) -> void:
	for i in WARMUP:
		await _frame()
	var vals := {"process": [], "physics": [], "frame": []}
	var last := Time.get_ticks_usec()
	for i in FRAMES:
		await _frame()
		var now := Time.get_ticks_usec()
		vals.frame.append((now - last) / 1000.0)
		last = now
		# Both monitors are in seconds and hold the last completed step.
		vals.process.append(Performance.get_monitor(Performance.TIME_PROCESS) * 1000.0)
		vals.physics.append(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0)
	var line := "RUN %s round %d" % [cond, r + 1]
	for m in METRICS:
		var a: Array = vals[m]
		var mean := _mean(a)
		samples[m][cond].append_array(a)
		round_means[m][cond].append(mean)
		line += " %s %.4f sd %.4f" % [m + (" (capped)" if m == "frame" else ""), mean, _sd(a, mean)]
	print(line)


## One frame; the active cost-only driver (if any) runs on it.
func _frame() -> void:
	await process_frame
	if _tick.is_valid():
		_tick.call(root.get_process_delta_time())


func _run_for_seconds(secs: float) -> void:
	var t := 0.0
	while t < secs:
		await _frame()
		t += root.get_process_delta_time()


## Cost-only setup for (c), not a gameplay test: bursts through the game's own spawner with no
## shell, so they use the fallback point and aim (R1.2). No cover, shell or tank is touched.
func _tick_bursts(delta: float) -> void:
	_spawn_left -= delta
	if _spawn_left <= 0.0:
		_spawn_left += SPAWN_EVERY
		for i in BURSTS_PER_TICK:
			main.spawn_cover_burst(null, BURST_POINTS[_spawn_index % BURST_POINTS.size()])
			_spawn_index += 1
	_alive_stats.append(_alive)


## Observer only: a counter kept by signals, so counting the bursts adds next to nothing to (c).
func _on_fx_child_entered(n: Node) -> void:
	if n.scene_file_path == BURST_SCENE:
		_alive += 1
		n.tree_exiting.connect(func(): _alive -= 1)


func _bursts_alive() -> int:
	return _alive


func _print_alive_stats() -> void:
	if _alive_stats.is_empty():
		return
	var lo: int = _alive_stats.min()
	var hi: int = _alive_stats.max()
	print("      bursts alive over the measured frames: min %d, mean %.2f, max %d" % [lo, _mean(_alive_stats), hi])


## Stop Effect A: no new bursts; the alive ones finish and free themselves.
func _stop_bursts() -> void:
	var t := 0.0
	while _bursts_alive() > 0 and t < 3.0:
		await _frame()
		t += root.get_process_delta_time()
	for n in main.fx_layer.get_children():
		if n.scene_file_path == BURST_SCENE:
			n.queue_free()
	await process_frame


func _tanks() -> Array:
	return [main.player] + main.enemies


## Cost-only setup for (d), not a gameplay test: h = 0 (alive) through follow(), the mapping tank.gd
## uses, gives emitting true and amount_ratio 1.0 on all 4 tanks. Health is not written.
func _smoke_peak() -> void:
	var ok := 0
	for t in _tanks():
		t.smoke.follow(0.0, false)
		if t.smoke.emitting and is_equal_approx(t.smoke.amount_ratio, 1.0):
			ok += 1
	print("      smoke emitting at amount_ratio 1.0 on %d of %d tanks" % [ok, _tanks().size()])


## Stop Effect B: h = 1 through follow() stops emission; the column in the air fades over 1.6 s.
func _stop_smoke() -> void:
	for t in _tanks():
		t.smoke.follow(1.0, false)
	await _run_for_seconds(1.7)


func _print_diff(label: String, hi: String, lo: String, means: Dictionary) -> void:
	var line := "COST diff %s" % label
	for m in ["process", "physics"]:
		var per_round := []
		for r in ROUNDS:
			per_round.append(round_means[m][hi][r] - round_means[m][lo][r])
		line += " %s %.4f (per round %s)" % [m, means[m][hi] - means[m][lo],
			", ".join(per_round.map(func(x): return "%.4f" % x))]
	print(line)


func _mean(a: Array) -> float:
	if a.is_empty():
		return 0.0
	var s := 0.0
	for x in a:
		s += x
	return s / a.size()


func _sd(a: Array, m: float) -> float:
	if a.size() < 2:
		return 0.0
	var s := 0.0
	for x in a:
		s += (x - m) * (x - m)
	return sqrt(s / (a.size() - 1))
