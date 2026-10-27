extends SceneTree
## tools/capture_hint.gd — Use It capture of the hint experiment (CHANGE-BRIEF.md section 4).
## Run by the human in a WINDOWED run (headless draws nothing):
##   "<godot console exe>" --path . --resolution 1280x720 --script res://tools/capture_hint.gd
## Loads scenes/hint_experiment.tscn, takes one capture (hint_both.png) and, for each quad and
## each of its three bands, projects the band centre with the scene camera and prints / writes the
## grey there (centre pixel and 3x3 mean) beside the prediction (hint_pixels.csv).
## Only the running instance is changed; no material or scene file is written.

const SCENE := "res://scenes/hint_experiment.tscn"
const OUT_DIR := "res://docs/a5/captures/"
const SETTLE_FRAMES := 60
const PARAM := &"use_srgb"
const BANDS := 3
# Brief section 4, by material file name: Quad A (source_color) and Quad B (no hint).
const PREDICTED := {"hint_srgb": [64, 128, 192], "hint_raw": [137, 188, 225]}
const TOLERANCE := 2

var _last_image: Image
var _last_save_err := OK


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
	var cam: Camera3D = scene.get_viewport().get_camera_3d()
	if cam == null:
		_fail("no current Camera3D")
		return

	var quads := []
	for n in scene.find_children("*", "MeshInstance3D", true, false):
		if n.mesh is QuadMesh:
			quads.append(n)
	quads.sort_custom(func(a, b): return a.global_position.x < b.global_position.x)
	if quads.size() != 2:
		_fail("expected 2 QuadMesh quads, found %d" % quads.size())
		return
	var mats := []
	for q in quads:
		var m := q.material_override as ShaderMaterial
		if m == null or not PREDICTED.has(m.resource_path.get_file().get_basename()):
			_fail("%s has no hint_srgb / hint_raw material_override" % q.name)
			return
		if (q.mesh as QuadMesh).orientation != PlaneMesh.FACE_Z:
			_fail("%s: QuadMesh orientation is not FACE_Z" % q.name)
			return
		mats.append(m)
	for i in 2:
		print("%s: %s, %s = %s, mesh size %s, centre_offset %s, global %s"
			% [quads[i].name, mats[i].resource_path, PARAM, mats[i].get_shader_parameter(PARAM),
			quads[i].mesh.size, quads[i].mesh.center_offset, quads[i].global_transform])

	# One capture of both quads. Nothing is changed: use_srgb is set to the value already saved.
	var path := OUT_DIR + "hint_both.png"
	print("--- capture")
	await capture(mats[0], PARAM, mats[0].get_shader_parameter(PARAM), path)
	print("  %s on %s after saving = %s" % [PARAM, mats[1].resource_path.get_file(), mats[1].get_shader_parameter(PARAM)])
	var img := _last_image
	var view_size: Vector2 = scene.get_viewport().get_visible_rect().size
	var scale := Vector2(img.get_size()) / view_size
	print("  image %dx%d format %d, visible rect %s, view->image scale %s" % [img.get_width(), img.get_height(), img.get_format(), view_size, scale])

	var csv := FileAccess.open(OUT_DIR + "hint_pixels.csv", FileAccess.WRITE)
	if csv == null:
		_fail("cannot write hint_pixels.csv")
		return
	csv.store_line("quad,material,band,file_value,world_x,world_y,world_z,view_x,view_y,x,y,centre_rgb,mean3x3_rgb,predicted,maxdiff_centre,maxdiff_mean,file")
	print("  %-11s %-9s %-4s %-5s %-12s %-12s %-18s %-5s %s" % ["quad", "material", "band", "file", "image x,y", "centre", "3x3 mean", "pred", "max|d| centre/mean"])
	var file_values := [64, 128, 192]
	var any_fail := _last_save_err != OK
	for i in 2:
		var q: MeshInstance3D = quads[i]
		var qm: QuadMesh = q.mesh
		var mname: String = mats[i].resource_path.get_file().get_basename()
		for b in BANDS:
			# Band b covers u in [b/3, (b+1)/3]; its centre is u = (b + 0.5) / 3, v = 0.5.
			# QuadMesh FACE_Z: u = 0 at local x = -size.x / 2, rising to the right; v = 0.5 at y = 0.
			var u := (float(b) + 0.5) / float(BANDS)
			var local := Vector3(-qm.size.x * 0.5 + u * qm.size.x, 0.0, 0.0) + qm.center_offset
			var world := q.global_transform * local
			if cam.is_position_behind(world):
				_fail("band centre %s is behind the camera" % world)
				return
			var vp := cam.unproject_position(world)
			var px := Vector2i(floori(vp.x * scale.x), floori(vp.y * scale.y))
			var centre := _rgb(img, px)
			var mean := _mean3(img, px)
			var pred: int = PREDICTED[mname][b]
			var dc := _maxdiff(centre, pred)
			var dm := _maxdiff(mean, pred)
			print("  %-11s %-9s %-4d %-5d %-12s %-12s %-18s %-5d %.0f / %.1f" % [q.name, mname, b, file_values[b],
				"%d,%d" % [px.x, px.y], _fmt(centre, 0), _fmt(mean, 1), pred, dc, dm])
			csv.store_line("%s,%s,%d,%d,%.4f,%.4f,%.4f,%.2f,%.2f,%d,%d,%s,%s,%d,%.0f,%.1f,%s" % [q.name, mname, b, file_values[b],
				world.x, world.y, world.z, vp.x, vp.y, px.x, px.y, _fmt(centre, 0), _fmt(mean, 1), pred, dc, dm, path.get_file()])
	csv.close()
	print("wrote %shint_pixels.csv (tolerance in the brief: +-%d)" % [OUT_DIR, TOLERANCE])
	await process_frame
	quit(1 if any_fail else 0)


func _rgb(img: Image, p: Vector2i) -> Array:
	var x := clampi(p.x, 0, img.get_width() - 1)
	var y := clampi(p.y, 0, img.get_height() - 1)
	var c := img.get_pixel(x, y)
	return [float(c.r8), float(c.g8), float(c.b8)]


func _mean3(img: Image, p: Vector2i) -> Array:
	var s := [0.0, 0.0, 0.0]
	for dy in range(-1, 2):
		for dx in range(-1, 2):
			var c := _rgb(img, p + Vector2i(dx, dy))
			for k in 3:
				s[k] += c[k]
	return [s[0] / 9.0, s[1] / 9.0, s[2] / 9.0]


## Largest channel difference from a grey prediction.
func _maxdiff(a: Array, grey: int) -> float:
	var m := 0.0
	for k in 3:
		m = maxf(m, absf(float(a[k]) - float(grey)))
	return m


func _fmt(a: Array, decimals: int) -> String:
	var f := "%." + str(decimals) + "f"
	return " ".join(PackedStringArray(a.map(func(v): return f % float(v))))
