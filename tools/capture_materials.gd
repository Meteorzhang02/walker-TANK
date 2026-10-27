extends SceneTree
## tools/capture_materials.gd — Use It captures of the brick materials (CHANGE-BRIEF.md section 5).
## Run by the human in a WINDOWED run (headless draws nothing):
##   "<godot console exe>" --path . --resolution 1280x720 --script res://tools/capture_materials.gd
##   ... --script res://tools/capture_materials.gd -- --tag=<name>   (prefix every file with <name>_)
## Loads scenes/asset_room_3d.tscn and captures, into docs/a5/captures/:
##   materials_side_by_side.png            both walls at their saved values
##   sweep_<uniform>_<min|default|max>.png  each non-sampler uniform of brick_surface.gdshader on the
##                                          intact material as loaded on CoverWall (range read from
##                                          the shader source); the saved value is restored after each
##   material_edit_damaged_only.png        brightness 0.5 on the damaged material only, then restored
## For every capture it prints and writes (materials_captures.csv) the mean RGB of a small box on
## the front face of each wall. Only the running instance is changed; no .tres is saved.

const SCENE := "res://scenes/asset_room_3d.tscn"
const OUT_DIR := "res://docs/a5/captures/"
const INTACT := "res://materials/cover_wall_intact.tres"
const DAMAGED := "res://materials/cover_wall_damaged.tres"
const SETTLE_FRAMES := 60
const BOX := 5  # half-size of the sampled box: (2 * BOX + 1) px square
const EDIT_BRIGHTNESS := 0.5

var _last_image: Image
var _last_save_err := OK
var _any_fail := false
var _prefix := ""
var _csv: FileAccess
var _cam: Camera3D
var _walls := []        # [[name, MeshInstance3D, world point on the front face of surface 0], ...]
var _view_size := Vector2.ZERO


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	print("ERROR: ", msg)
	quit(1)


## The assignment's capture function without a driver (nothing drives these materials), plus one
## process frame after setting the value and a read-back of the parameter after saving.
func capture(mat: ShaderMaterial, param: StringName, value: Variant, path: String) -> void:
	mat.set_shader_parameter(param, value)
	await process_frame
	await RenderingServer.frame_post_draw
	_last_image = current_scene.get_viewport().get_texture().get_image()
	_last_save_err = _last_image.save_png(path)
	print("  saved %s (err %d); %s after saving = %s (set %s)" % [path, _last_save_err, param, mat.get_shader_parameter(param), value])


func _run() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--tag="):
			_prefix = a.trim_prefix("--tag=").strip_edges() + "_"
	if _prefix == "_":
		_fail("--tag= needs a name")
		return
	var err := DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	if err != OK:
		_fail("cannot create %s (%d)" % [OUT_DIR, err])
		return
	err = change_scene_to_file(SCENE)
	if err != OK:
		_fail("change_scene_to_file(%s) returned %d" % [SCENE, err])
		return
	for i in SETTLE_FRAMES:
		await process_frame
	var scene: Node = current_scene
	if scene == null:
		_fail("scene did not load")
		return
	_cam = scene.get_viewport().get_camera_3d()
	if _cam == null:
		_fail("no current Camera3D")
		return
	_view_size = scene.get_viewport().get_visible_rect().size

	var mi1 := _mesh_of(scene.get_node_or_null("CoverWall"))
	var mi2 := _mesh_of(scene.get_node_or_null("CoverWall2"))
	if mi1 == null or mi2 == null:
		_fail("CoverWall / CoverWall2 or their MeshInstance3D not found")
		return
	var intact := mi1.get_active_material(0) as ShaderMaterial
	var damaged := mi2.get_active_material(0) as ShaderMaterial
	print("CoverWall  surface 0: %s" % [intact.resource_path if intact else null])
	print("CoverWall2 surface 0: %s" % [damaged.resource_path if damaged else null])
	if intact == null or intact.resource_path != INTACT:
		_fail("CoverWall surface 0 is not %s" % INTACT)
		return
	if damaged == null or damaged.resource_path != DAMAGED or is_same(intact, damaged):
		_fail("CoverWall2 surface 0 is not %s" % DAMAGED)
		return
	for pair in [["CoverWall", mi1], ["CoverWall2", mi2]]:
		var p = _front_point(pair[1])
		if p == null:
			_fail("%s: front-face point not visible" % pair[0])
			return
		_walls.append([pair[0], pair[1], p])
		print("%s: sample point %s -> view %s" % [pair[0], p, _cam.unproject_position(p)])

	var shader_path := intact.shader.resource_path
	var uniforms := _non_sampler_uniforms(FileAccess.get_file_as_string(shader_path))
	if uniforms.is_empty():
		_fail("no non-sampler uniforms parsed from %s" % shader_path)
		return
	print("non-sampler uniforms in %s:" % shader_path)
	for u in uniforms:
		print("  %-16s %-6s min %-22s default %-22s max %s" % [u.name, u.type, u.min, u.default, u.max])

	_csv = FileAccess.open(OUT_DIR + _prefix + "materials_captures.csv", FileAccess.WRITE)
	if _csv == null:
		_fail("cannot write materials_captures.csv")
		return
	_csv.store_line("tag,file,material,uniform,step,value,param_after,note,wall1_x,wall1_y,wall1_mean_rgb,wall2_x,wall2_y,wall2_mean_rgb")
	print("box: %dx%d px mean around the projected front-face point of each wall" % [2 * BOX + 1, 2 * BOX + 1])

	# 1. Side by side at the saved values (brightness is set to the value it already has).
	print("--- side by side")
	await _shot(intact, "intact", &"brightness", intact.get_shader_parameter("brightness"), "materials_side_by_side.png", "both walls at their saved values", "saved")

	# 2. Interface sweep on the intact material.
	for u in uniforms:
		var saved = intact.get_shader_parameter(u.name)
		if saved == null:
			saved = u.default
		print("--- sweep %s (saved %s, source default %s)" % [u.name, saved, u.default])
		var note := ""
		if _same(u.default, u.max):
			note = "default and maximum coincide"
		elif _same(u.default, u.min):
			note = "default and minimum coincide"
		if not _same(saved, u.default):
			note += ("; " if note != "" else "") + "saved value differs from the source default"
		for step in ["min", "default", "max"]:
			await _shot(intact, "intact", StringName(u.name), u[step], "sweep_%s_%s.png" % [u.name, step], note, step)
		intact.set_shader_parameter(u.name, saved)
		print("  restored %s = %s" % [u.name, intact.get_shader_parameter(u.name)])

	# 3. Material edit on the damaged material only.
	print("--- material edit (damaged only)")
	var saved_b = damaged.get_shader_parameter("brightness")
	await _shot(damaged, "damaged", &"brightness", EDIT_BRIGHTNESS, "material_edit_damaged_only.png",
		"intact brightness during this capture = %s" % [intact.get_shader_parameter("brightness")], "edit")
	damaged.set_shader_parameter("brightness", saved_b)
	print("  restored damaged brightness = %s" % [damaged.get_shader_parameter("brightness")])

	_csv.close()
	print("wrote %s%smaterials_captures.csv" % [OUT_DIR, _prefix])
	await process_frame
	quit(1 if _any_fail else 0)


## One capture plus the two wall boxes, printed and written to the CSV.
func _shot(mat: ShaderMaterial, mat_name: String, param: StringName, value: Variant, file: String, note: String, step: String) -> void:
	var path := OUT_DIR + _prefix + file
	await capture(mat, param, value, path)
	if _last_save_err != OK:
		_any_fail = true
	var after = mat.get_shader_parameter(param)
	if not _same(after, value):
		print("  WARNING: %s reads %s after the capture, set %s" % [param, after, value])
		_any_fail = true
	var img := _last_image
	var scale := Vector2(img.get_size()) / _view_size
	var cols := []
	var line := "  "
	for w in _walls:
		var vp := _cam.unproject_position(w[2])
		var px := Vector2i(floori(vp.x * scale.x), floori(vp.y * scale.y))
		var mean := _box_mean(img, px)
		cols.append("%d,%d,%s" % [px.x, px.y, _fmt(mean)])
		line += "%s box @%d,%d mean (%s)   " % [w[0], px.x, px.y, _fmt(mean)]
	print(line + ("[%s]" % note if note != "" else ""))
	_csv.store_line("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % [_prefix.trim_suffix("_"), path.get_file(), mat_name, param, step,
		_val(value), _val(after), note.replace(",", ";"), cols[0], cols[1]])


func _mesh_of(n: Node) -> MeshInstance3D:
	if n == null:
		return null
	if n is MeshInstance3D:
		return n as MeshInstance3D
	var found := n.find_children("*", "MeshInstance3D", true, false)
	return found[0] as MeshInstance3D if found.size() == 1 else null


## Centre of the camera-facing (+Z, the camera is at z = 16) face of surface 0's own vertex box, in
## world space: surface 0 is M_Brick, the wall body; the cap and base (surface 1) are left out.
func _front_point(mi: MeshInstance3D):
	var verts: PackedVector3Array = mi.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	if verts.is_empty():
		return null
	var box := AABB(verts[0], Vector3.ZERO)
	for v in verts:
		box = box.expand(v)
	var c := box.get_center()
	var p := mi.global_transform * Vector3(c.x, c.y, box.end.z)
	if _cam.is_position_behind(p):
		return null
	var vp := _cam.unproject_position(p)
	if vp.x < BOX or vp.y < BOX or vp.x > _view_size.x - BOX or vp.y > _view_size.y - BOX:
		return null
	return p


## Reads every non-sampler uniform from the shader source: name, type, source default, and the
## sweep minimum / maximum (hint_range for floats; black / white for source_color vec4).
func _non_sampler_uniforms(src: String) -> Array:
	var out := []
	var re := RegEx.new()
	re.compile("^\\s*uniform\\s+(\\w+)\\s+(\\w+)\\s*(?::\\s*([^=;]+?))?\\s*(?:=\\s*([^;]+?))?\\s*;")
	var re_range := RegEx.new()
	re_range.compile("hint_range\\s*\\(\\s*(-?[\\d.]+)\\s*,\\s*(-?[\\d.]+)")
	var re_num := RegEx.new()
	re_num.compile("(?<![\\w.])-?\\d+(?:\\.\\d+)?")
	for line in src.split("\n"):
		var m := re.search(line.split("//")[0])
		if m == null or m.get_string(1).begins_with("sampler"):
			continue
		var type := m.get_string(1)
		var hints := m.get_string(3)
		var nums := re_num.search_all(m.get_string(4)).map(func(x): return float(x.get_string()))
		var u := {"name": m.get_string(2), "type": type}
		if type == "float":
			var r := re_range.search(hints)
			if r == null or nums.size() != 1:
				print("  WARNING: %s has no hint_range or default; not swept" % u.name)
				continue
			u.min = float(r.get_string(1))
			u.max = float(r.get_string(2))
			u.default = nums[0]
		elif type == "vec4" and hints.contains("source_color") and nums.size() == 4:
			u.min = Color(0, 0, 0, 1)
			u.max = Color(1, 1, 1, 1)
			u.default = Color(nums[0], nums[1], nums[2], nums[3])
		else:
			print("  WARNING: %s (%s) has no sweep range; not swept" % [u.name, type])
			continue
		out.append(u)
	return out


func _box_mean(img: Image, p: Vector2i) -> Array:
	var s := [0.0, 0.0, 0.0]
	var n := 0
	for dy in range(-BOX, BOX + 1):
		for dx in range(-BOX, BOX + 1):
			var x := clampi(p.x + dx, 0, img.get_width() - 1)
			var y := clampi(p.y + dy, 0, img.get_height() - 1)
			var c := img.get_pixel(x, y)
			s[0] += c.r8
			s[1] += c.g8
			s[2] += c.b8
			n += 1
	return [s[0] / n, s[1] / n, s[2] / n]


func _same(a, b) -> bool:
	if a is Color and b is Color:
		return a.is_equal_approx(b)
	if (a is float or a is int) and (b is float or b is int):
		return absf(float(a) - float(b)) <= 1e-4
	return a == b


func _val(v) -> String:
	if v is Color:
		return "%.3f %.3f %.3f %.3f" % [v.r, v.g, v.b, v.a]
	return str(v)


func _fmt(a: Array) -> String:
	return "%.1f %.1f %.1f" % [a[0], a[1], a[2]]
