extends SceneTree
## A6 Effect A config: loads effects/cover_hit_burst.tscn and reads every value in CHANGE-BRIEF.md's
## Effect A settings table back from the loaded nodes and resources, emitter by emitter, by path.
##   bash scripts/run-test.sh test_cover_hit_burst_config.gd 60
##
## What this does NOT prove: how the burst looks (nothing is drawn headless), its timing phases,
## contrast or scale. Those are the frame strip and the human check in TEST-REPORT.md.
## The last block runs one instance in the tree for ~1.2 s of process frames to see that the root
## frees itself after Dust's `finished`; CPUParticles2D simulates on the CPU, so this runs headless.

const SCENE := "res://effects/cover_hit_burst.tscn"
const ROOT_SCRIPT := "res://effects/cover_hit_burst.gd"
const CHIP := "res://effects/textures/chip_6.png"
const DOT := "res://effects/textures/soft_dot_32.png"
const EPS := 1e-4
const COLOR_EPS := 0.002  # the scene stores the hex colours as 6-digit decimals

## The brief's settings table, one entry per emitter path.
## curve: [[x, y], ...] points; ramp: [[offset, "#RRGGBB", alpha], ...].
var EXPECTED := {
	"Flash": {
		"amount": 3, "one_shot": true, "explosiveness": 1.0, "lifetime": 0.12,
		"emission_shape": CPUParticles2D.EMISSION_SHAPE_POINT,
		"direction": Vector2(1, 0), "spread": 180.0,
		"initial_velocity_min": 0.0, "initial_velocity_max": 0.0,
		"gravity": Vector2(0, 0),
		"damping_min": 0.0, "damping_max": 0.0,
		"angular_velocity_min": 0.0, "angular_velocity_max": 0.0,
		"scale_amount_min": 1.6, "scale_amount_max": 2.0,
		"hue_variation_min": 0.0, "hue_variation_max": 0.0,
		"local_coords": false,
		"curve": [[0.0, 1.0], [1.0, 1.6]],
		"ramp": [[0.0, "#FFF4D0", 1.0], [1.0, "#FFF4D0", 0.0]],
		"texture": DOT,
		"blend": CanvasItemMaterial.BLEND_MODE_ADD,
	},
	"Debris": {
		"amount": 24, "one_shot": true, "explosiveness": 1.0, "lifetime": 0.6,
		"emission_shape": CPUParticles2D.EMISSION_SHAPE_SPHERE, "emission_sphere_radius": 4.0,
		"direction": Vector2(1, 0), "spread": 60.0,
		"initial_velocity_min": 180.0, "initial_velocity_max": 320.0,
		"gravity": Vector2(0, 0),
		"damping_min": 400.0, "damping_max": 600.0,
		"angular_velocity_min": -720.0, "angular_velocity_max": 720.0,
		"scale_amount_min": 0.6, "scale_amount_max": 1.2,
		"hue_variation_min": -0.03, "hue_variation_max": 0.03,
		"local_coords": false,
		"curve": [[0.0, 1.0], [1.0, 0.4]],
		"ramp": [[0.0, "#E8D8B0", 1.0], [0.3, "#B5523A", 1.0], [0.6, "#8E5040", 1.0], [1.0, "#8E5040", 0.0]],
		"texture": CHIP,
		"blend": null,
	},
	"Dust": {
		"amount": 10, "one_shot": true, "explosiveness": 0.9, "lifetime": 0.7,
		"emission_shape": CPUParticles2D.EMISSION_SHAPE_SPHERE, "emission_sphere_radius": 8.0,
		"direction": Vector2(1, 0), "spread": 180.0,
		"initial_velocity_min": 30.0, "initial_velocity_max": 70.0,
		"gravity": Vector2(0, 0),
		"damping_min": 60.0, "damping_max": 90.0,
		"angular_velocity_min": -60.0, "angular_velocity_max": 60.0,
		"scale_amount_min": 1.0, "scale_amount_max": 1.4,
		"hue_variation_min": 0.0, "hue_variation_max": 0.0,
		"local_coords": false,
		"curve": [[0.0, 0.6], [1.0, 1.8]],
		"ramp": [[0.0, "#CFC2A8", 0.6], [1.0, "#CFC2A8", 0.0]],
		"texture": DOT,
		"blend": null,
	},
}

## Keys of EXPECTED that are node properties read with get(); the rest are checked separately.
const SCALAR_KEYS := ["amount", "one_shot", "explosiveness", "lifetime", "emission_shape",
	"emission_sphere_radius", "direction", "spread", "initial_velocity_min", "initial_velocity_max",
	"gravity", "damping_min", "damping_max", "angular_velocity_min", "angular_velocity_max",
	"scale_amount_min", "scale_amount_max", "hue_variation_min", "hue_variation_max", "local_coords"]

var failures := 0
var passes := 0


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
	await process_frame
	quit(1 if failures > 0 else 0)


func _same(a, b) -> bool:
	if typeof(a) != typeof(b):
		return false
	match typeof(a):
		TYPE_FLOAT:
			return absf(a - b) < EPS
		TYPE_VECTOR2:
			return a.is_equal_approx(b)
		_:
			return a == b


func _same_color(a: Color, b: Color) -> bool:
	return absf(a.r - b.r) < COLOR_EPS and absf(a.g - b.g) < COLOR_EPS \
		and absf(a.b - b.b) < COLOR_EPS and absf(a.a - b.a) < COLOR_EPS


func _run() -> void:
	var packed := load(SCENE) as PackedScene
	_check("scene loads: %s" % SCENE, packed != null)
	if packed == null:
		await _finish()
		return
	var scene := packed.instantiate()
	_check("root is Node2D (got %s)" % scene.get_class(), scene.get_class() == "Node2D")
	var script: Script = scene.get_script()
	_check("root script is %s" % ROOT_SCRIPT, script != null and script.resource_path == ROOT_SCRIPT)
	var names := []
	for c in scene.get_children():
		names.append(String(c.name))
	_check("root children are exactly [Flash, Debris, Dust] (got %s)" % [names], names == ["Flash", "Debris", "Dust"])

	for path in EXPECTED:
		var e: Dictionary = EXPECTED[path]
		var p := scene.get_node_or_null(path)
		_check("%s exists and is CPUParticles2D" % path, p != null and p.get_class() == "CPUParticles2D")
		if p == null or p.get_class() != "CPUParticles2D":
			continue
		for key in SCALAR_KEYS:
			if not e.has(key):
				continue
			var got = p.get(key)
			_check("%s.%s == %s (got %s)" % [path, key, e[key], got], _same(got, e[key]))
		# The effect scene never uses a fixed seed (the preview's instance does).
		_check("%s.use_fixed_seed == false in the effect scene" % path, p.get("use_fixed_seed") == false)
		# Not in the brief's table: the instanced burst must fire on its own when added to the tree.
		_check("%s.emitting == true in the scene file (fires when instanced)" % path, p.emitting == true)
		_check_curve(path, p.scale_amount_curve, e["curve"])
		_check_ramp(path, p.color_ramp, e["ramp"])
		var tex: Texture2D = p.texture
		_check("%s.texture not null" % path, tex != null)
		_check("%s.texture is %s (got %s)" % [path, e["texture"], tex.resource_path if tex else "null"],
			tex != null and tex.resource_path == e["texture"])
		if e["blend"] == null:
			_check("%s.material is null (mix) (got %s)" % [path, p.material], p.material == null)
		else:
			var m: Material = p.material
			_check("%s.material is CanvasItemMaterial (got %s)" % [path, m.get_class() if m else "null"],
				m != null and m.get_class() == "CanvasItemMaterial")
			_check("%s.material.blend_mode == BLEND_MODE_ADD (got %s)" % [path, m.get("blend_mode") if m else "null"],
				m != null and m.get("blend_mode") == e["blend"])

	await _check_self_free(packed)
	scene.free()
	await _finish()


func _check_curve(path: String, c: Curve, pts: Array) -> void:
	_check("%s.scale_amount_curve not null" % path, c != null)
	if c == null:
		return
	_check("%s.scale_amount_curve has %d points (got %d)" % [path, pts.size(), c.point_count], c.point_count == pts.size())
	for i in mini(pts.size(), c.point_count):
		var want := Vector2(pts[i][0], pts[i][1])
		var got := c.get_point_position(i)
		_check("%s.scale_amount_curve point %d == %s (got %s)" % [path, i, want, got], got.is_equal_approx(want))
		# sample() is what the emitter reads; it catches a value clamped by the curve's max_value.
		var s := c.sample(want.x)
		_check("%s.scale_amount_curve.sample(%s) == %s (got %s)" % [path, want.x, want.y, s], absf(s - want.y) < EPS)
	if pts.size() == 2:
		var mid: float = (pts[0][1] + pts[1][1]) * 0.5
		var s_mid := c.sample(0.5)
		_check("%s.scale_amount_curve is linear: sample(0.5) == %s (got %s)" % [path, mid, s_mid], absf(s_mid - mid) < 1e-3)


func _check_ramp(path: String, g: Gradient, pts: Array) -> void:
	_check("%s.color_ramp not null" % path, g != null)
	if g == null:
		return
	_check("%s.color_ramp has %d points (got %d)" % [path, pts.size(), g.get_point_count()], g.get_point_count() == pts.size())
	for i in mini(pts.size(), g.get_point_count()):
		var want_off: float = pts[i][0]
		var want := Color.html(pts[i][1])
		want.a = pts[i][2]
		var off := g.get_offset(i)
		var col := g.get_color(i)
		_check("%s.color_ramp point %d offset == %s (got %s)" % [path, i, want_off, off], absf(off - want_off) < EPS)
		_check("%s.color_ramp point %d == %s a%s (got %s)" % [path, i, pts[i][1], pts[i][2], col], _same_color(col, want))


## Behaviour of the root script: alive while Dust is still emitting/alive, freed after Dust finishes.
func _check_self_free(packed: PackedScene) -> void:
	var burst := packed.instantiate()
	root.add_child(burst)
	var frames := 0
	var alive_at_06 := false
	# Run up to 1.5 s of process frames. Dust's last particle dies at <= 0.1 * 0.7 + 0.7 = 0.77 s.
	var t := 0.0
	while is_instance_valid(burst) and t < 1.5:
		var dt: float = await _frame_dt()
		t += dt
		frames += 1
		if t >= 0.6 and t < 0.65 and is_instance_valid(burst):
			alive_at_06 = true
	_check("burst root still in the tree at 0.6 s", alive_at_06)
	_check("burst root freed itself after Dust finished (at %.3f s, %d frames)" % [t, frames], not is_instance_valid(burst))
	_check("burst root freed no earlier than Dust's lifetime 0.7 s (at %.3f s)" % t, t >= 0.7)


## Under --fixed-fps every process frame advances the game clock by exactly 1 / fps.
func _frame_dt() -> float:
	await process_frame
	return root.get_process_delta_time()
