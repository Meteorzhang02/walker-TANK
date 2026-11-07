extends SceneTree
## A6 Effect B config: loads effects/damage_smoke.tscn and reads every value in CHANGE-BRIEF.md's
## Effect B settings table back from the loaded node, its ParticleProcessMaterial, its
## CanvasItemMaterial and the GradientTexture1D / CurveTexture resources. Then it calls the root's
## follow() for the brief's observable rule 1 and checks emitting / amount_ratio, that amount stays
## 48 and that follow() changes no other stored property.
##   bash scripts/run-test.sh test_damage_smoke_config.gd 60
##
## What this does NOT prove: how the smoke looks (headless uses a dummy renderer and runs no GPU
## particle process), the turbulence waver, the unit of angle_min/max, or how sphere emission
## behaves with particle_flag_disable_z. Those are the frame strip and the human check.

const SCENE := "res://effects/damage_smoke.tscn"
const ROOT_SCRIPT := "res://effects/damage_smoke.gd"
const DOT := "res://effects/textures/soft_dot_32.png"
const EPS := 1e-4
const COLOR_EPS := 0.002  # the scene stores the hex colours as 6-digit decimals
const RATIO_EPS := 0.001  # the brief's tolerance for amount_ratio

## GPUParticles2D node properties (emission and draw groups of the brief's table).
var NODE_EXPECTED := {
	"amount": 48, "amount_ratio": 1.0, "one_shot": false, "emitting": false,
	"explosiveness": 0.0, "lifetime": 1.6, "preprocess": 0.0,
	"local_coords": false, "visibility_rect": Rect2(-200, -220, 400, 420),
	"use_fixed_seed": false,  # the effect scene never uses a fixed seed (the preview's instance does)
}

## ParticleProcessMaterial properties (emission shape and the process group).
var MAT_EXPECTED := {
	"particle_flag_disable_z": true,
	"emission_shape": ParticleProcessMaterial.EMISSION_SHAPE_SPHERE, "emission_sphere_radius": 6.0,
	"direction": Vector3(0, -1, 0), "spread": 20.0,
	"initial_velocity_min": 50.0, "initial_velocity_max": 80.0,  # R5
	"gravity": Vector3(0, -15, 0),
	"damping_min": 5.0, "damping_max": 8.0,
	"angle_min": 0.0, "angle_max": 360.0,
	"scale_min": 0.8, "scale_max": 1.2,
	"turbulence_enabled": true,
	"turbulence_noise_strength": 2.0, "turbulence_noise_scale": 4.0,
	"turbulence_influence_min": 0.1, "turbulence_influence_max": 0.2,
}

## scale_curve [[x, y], ...]; color_ramp [[offset, "#RRGGBB", alpha], ...].
const CURVE := [[0.0, 0.5], [1.0, 2.0]]
const RAMP := [[0.0, "#4A4A48", 0.0], [0.15, "#4A4A48", 0.7], [1.0, "#8A8A86", 0.0]]

## Rule 1: [label, health_ratio, dead, emitting, amount_ratio or null when not emitting].
const FOLLOW_CASES := [
	["h = 0.5", 0.5, false, true, 0.375],
	["h = 0.3", 0.3, false, true, 0.625],
	["h = 0.1", 0.1, false, true, 0.875],
	["h = 1.0 (condition ends)", 1.0, false, false, null],
	["h = 0.6 (threshold)", 0.6, false, true, 0.25],
	["dead (wreck)", 0.0, true, true, 1.0],
	["h = 1.0 after the wreck (respawn)", 1.0, false, false, null],
]

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
		TYPE_VECTOR2, TYPE_VECTOR3, TYPE_RECT2:
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
	var smoke := packed.instantiate()
	_check("root is GPUParticles2D (got %s)" % smoke.get_class(), smoke.get_class() == "GPUParticles2D")
	var script: Script = smoke.get_script()
	_check("root script is %s" % ROOT_SCRIPT, script != null and script.resource_path == ROOT_SCRIPT)
	_check("root has no child emitters (one emitter) (got %d children)" % smoke.get_child_count(), smoke.get_child_count() == 0)
	if smoke.get_class() != "GPUParticles2D":
		smoke.free()
		await _finish()
		return

	for key in NODE_EXPECTED:
		var got = smoke.get(key)
		_check("DamageSmoke.%s == %s (got %s)" % [key, NODE_EXPECTED[key], got], _same(got, NODE_EXPECTED[key]))

	var tex: Texture2D = smoke.texture
	_check("DamageSmoke.texture not null", tex != null)
	_check("DamageSmoke.texture is %s (got %s)" % [DOT, tex.resource_path if tex else "null"],
		tex != null and tex.resource_path == DOT)
	var cim: Material = smoke.material
	_check("DamageSmoke.material is CanvasItemMaterial (got %s)" % [cim.get_class() if cim else "null"],
		cim != null and cim.get_class() == "CanvasItemMaterial")
	_check("DamageSmoke.material.blend_mode == BLEND_MODE_MIX (got %s)" % [cim.get("blend_mode") if cim else "null"],
		cim != null and cim.get("blend_mode") == CanvasItemMaterial.BLEND_MODE_MIX)

	var pm: Material = smoke.process_material
	_check("DamageSmoke.process_material is ParticleProcessMaterial (got %s)" % [pm.get_class() if pm else "null"],
		pm != null and pm.get_class() == "ParticleProcessMaterial")
	if pm != null and pm.get_class() == "ParticleProcessMaterial":
		for key in MAT_EXPECTED:
			var got = pm.get(key)
			_check("process_material.%s == %s (got %s)" % [key, MAT_EXPECTED[key], got], _same(got, MAT_EXPECTED[key]))
		_check_curve(pm.get("scale_curve"))
		_check_ramp(pm.get("color_ramp"))

	root.add_child(smoke)
	await process_frame
	_check_follow(smoke)
	smoke.queue_free()
	await _finish()


func _check_curve(ct: Texture2D) -> void:
	_check("process_material.scale_curve is CurveTexture (got %s)" % [ct.get_class() if ct else "null"],
		ct != null and ct.get_class() == "CurveTexture")
	if ct == null or ct.get_class() != "CurveTexture":
		return
	var c: Curve = ct.get("curve")
	_check("scale_curve.curve not null", c != null)
	if c == null:
		return
	_check("scale_curve has %d points (got %d)" % [CURVE.size(), c.point_count], c.point_count == CURVE.size())
	for i in mini(CURVE.size(), c.point_count):
		var want := Vector2(CURVE[i][0], CURVE[i][1])
		var got := c.get_point_position(i)
		_check("scale_curve point %d == %s (got %s)" % [i, want, got], got.is_equal_approx(want))
		# sample() is what the texture bakes; it catches a value clamped by the curve's max_value.
		var s := c.sample(want.x)
		_check("scale_curve.sample(%s) == %s (got %s)" % [want.x, want.y, s], absf(s - want.y) < EPS)
	var mid: float = (CURVE[0][1] + CURVE[1][1]) * 0.5
	var s_mid := c.sample(0.5)
	_check("scale_curve is linear: sample(0.5) == %s (got %s)" % [mid, s_mid], absf(s_mid - mid) < 1e-3)


func _check_ramp(gt: Texture2D) -> void:
	_check("process_material.color_ramp is GradientTexture1D (got %s)" % [gt.get_class() if gt else "null"],
		gt != null and gt.get_class() == "GradientTexture1D")
	if gt == null or gt.get_class() != "GradientTexture1D":
		return
	var g: Gradient = gt.get("gradient")
	_check("color_ramp.gradient not null", g != null)
	if g == null:
		return
	_check("color_ramp has %d points (got %d)" % [RAMP.size(), g.get_point_count()], g.get_point_count() == RAMP.size())
	for i in mini(RAMP.size(), g.get_point_count()):
		var want_off: float = RAMP[i][0]
		var want := Color.html(RAMP[i][1])
		want.a = RAMP[i][2]
		var off := g.get_offset(i)
		var col := g.get_color(i)
		_check("color_ramp point %d offset == %s (got %s)" % [i, want_off, off], absf(off - want_off) < EPS)
		_check("color_ramp point %d == %s a%s (got %s)" % [i, RAMP[i][1], RAMP[i][2], col], _same_color(col, want))


## Every stored property of the node and its process material, except the two follow() may set.
func _snapshot(smoke: GPUParticles2D) -> Dictionary:
	var snap := {}
	for obj in [smoke, smoke.process_material]:
		for prop in obj.get_property_list():
			if not (prop["usage"] & PROPERTY_USAGE_STORAGE):
				continue
			var n: String = prop["name"]
			if obj == smoke and n in ["emitting", "amount_ratio"]:
				continue
			snap["%s.%s" % [obj.get_class(), n]] = obj.get(n)
	return snap


func _check_follow(smoke: GPUParticles2D) -> void:
	_check("root has follow()", smoke.has_method("follow"))
	if not smoke.has_method("follow"):
		return
	var before := _snapshot(smoke)
	for c in FOLLOW_CASES:
		smoke.follow(c[1], c[2])
		_check("follow(%s): emitting == %s (got %s)" % [c[0], c[3], smoke.emitting], smoke.emitting == c[3])
		if c[4] != null:
			_check("follow(%s): amount_ratio == %s (got %.4f)" % [c[0], c[4], smoke.amount_ratio],
				absf(smoke.amount_ratio - c[4]) < RATIO_EPS)
		_check("follow(%s): amount still 48 (got %d)" % [c[0], smoke.amount], smoke.amount == 48)
	var after := _snapshot(smoke)
	var changed := []
	for k in before:
		if not after.has(k) or not _same(after[k], before[k]):
			changed.append(k)
	_check("follow() changed no stored property besides emitting / amount_ratio (%d compared; changed: %s)" % [before.size(), changed],
		changed.is_empty() and after.size() == before.size())
