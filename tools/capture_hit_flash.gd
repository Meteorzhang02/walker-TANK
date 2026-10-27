extends SceneTree
## tools/capture_hit_flash.gd — Use It captures of the hit flash (CHANGE-BRIEF.md section 3).
## Run by the human in a WINDOWED run (headless draws nothing):
##   "<godot console exe>" --path . --resolution 1280x720 --script res://tools/capture_hit_flash.gd
## Loads scenes/main.tscn, freezes the three enemies, turns YunqiZ's controls off, sets the hull
## and turret to slot 0 (hull_right.png, flip_h false) and stops YunqiZ's physics so the idle
## wobble cannot move the hull between captures. Then it captures hit_amount 0.0 / 0.5 / 1.0 / 2.0
## into docs/a5/captures/ and prints / writes the colour at P1 and P2 (hit_flash_pixels.csv).
## Only the running instance is changed; no game file is written.

const SCENE := "res://scenes/main.tscn"
const OUT_DIR := "res://docs/a5/captures/"
const SETTLE_FRAMES := 30
const PARAM := &"hit_amount"
const VALUES := [0.0, 0.5, 1.0, 2.0]
const PIXEL_NAMES := ["P1", "P2"]
const TEXELS := {"P1": Vector2i(99, 50), "P2": Vector2i(59, 109)}  # texels of hull_right.png
const SOURCE := {"P1": [87, 97, 40], "P2": [16, 16, 16]}           # brief section 3
# Predictions per value, brief section 3. 2.0 has none (brief section 7, the hint_range question).
const PREDICTED := [
	{"P1": [87, 97, 40], "P2": [16, 16, 16]},
	{"P1": [137, 68, 28], "P2": [88, 11, 11]},
	{"P1": [188, 39, 16], "P2": [159, 6, 6]},
	{},
]
const TOLERANCE := 2

var _last_image: Image
var _last_save_err := OK


func _initialize() -> void:
	_run.call_deferred()


func _fail(msg: String) -> void:
	print("ERROR: ", msg)
	quit(1)


## The assignment's capture function, plus one process frame after setting the value so the
## value is in the frame that is drawn, and a read-back of the parameter after saving.
## The driver only uses _process (hit_flash_driver.gd line 57), so set_physics_process is not needed.
func capture(driver: Node, mat: ShaderMaterial, param: StringName, value: float, path: String) -> void:
	driver.set_process(false)
	mat.set_shader_parameter(param, value)
	await process_frame
	await RenderingServer.frame_post_draw
	_last_image = driver.get_viewport().get_texture().get_image()
	_last_save_err = _last_image.save_png(path)
	print("  saved %s (err %d); %s after saving = %s (set %s)" % [path, _last_save_err, param, mat.get_shader_parameter(param), value])
	driver.set_process(true)


func _run() -> void:
	var err := DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	if err != OK:
		_fail("cannot create %s (%d)" % [OUT_DIR, err])
		return
	err = change_scene_to_file(SCENE)
	if err != OK:
		_fail("change_scene_to_file(%s) returned %d" % [SCENE, err])
		return
	for i in 10:
		await process_frame
		if current_scene != null:
			break
	var main = current_scene
	if main == null or main.get("player") == null or main.get("enemies") == null:
		_fail("main scene did not load or has no player / enemies")
		return

	# Freeze the enemies at once (their first shot is 1.5-3 s after spawn, enemy.gd line 15).
	for e in main.enemies:
		e.process_mode = Node.PROCESS_MODE_DISABLED
	print("froze %d enemies (PROCESS_MODE_DISABLED)" % main.enemies.size())

	var player = main.player
	player.controls_enabled = false
	for i in 3:
		await physics_frame  # _think now sets move_dir = ZERO, so the hull texture stays put
	player.aim_angle = 0.0
	var slot: int = player._slot_for(Vector2.RIGHT)
	player._set_sprite(player.hull, player._hull_tex, slot)
	player._set_sprite(player.turret, player._turret_tex, slot)
	for i in SETTLE_FRAMES:
		await process_frame
	player.set_physics_process(false)  # stops the idle wobble (tank.gd lines 128-131)

	# Wait until nothing is flashing: modulate back at tint.
	var waited := 0
	while not player.modulate.is_equal_approx(player.tint) and waited < 240:
		await process_frame
		waited += 1
	await process_frame

	var hull: Sprite2D = player.hull
	var turret: Sprite2D = player.turret
	var hull_path: String = hull.texture.resource_path if hull.texture else "<none>"
	var turret_path: String = turret.texture.resource_path if turret.texture else "<none>"
	print("player: slot %d, hull %s flip_h %s, turret %s flip_h %s" % [slot, hull_path, hull.flip_h, turret_path, turret.flip_h])
	print("player: modulate %s, tint %s, is_dead %s, health %d" % [player.modulate, player.tint, player.is_dead, player.health])
	if slot != 0 or not hull_path.ends_with("/hull_right.png") or hull.flip_h:
		_fail("hull is not slot 0 / hull_right.png / flip_h false")
		return
	if not player.modulate.is_equal_approx(player.tint) or not player.tint.is_equal_approx(Color(1, 1, 1)):
		_fail("player modulate is not tint (1, 1, 1)")
		return

	var driver: Node = player.get_node_or_null("HitFlashDriver")
	if driver == null:
		_fail("no HitFlashDriver under the player")
		return
	var mat := driver.get("material") as ShaderMaterial
	if mat == null or not is_same(hull.material, mat) or not is_same(turret.material, mat):
		_fail("hull and turret do not share the driver's ShaderMaterial")
		return
	print("driver: active %s, %s = %s, shader %s" % [driver.get("_active"), PARAM, mat.get_shader_parameter(PARAM), mat.shader.resource_path])
	if driver.get("_active"):
		_fail("the driver is still fading")
		return

	var hull_img: Image = hull.texture.get_image()
	var turret_img: Image = turret.texture.get_image()
	if hull_img.is_compressed():
		hull_img.decompress()
	if turret_img.is_compressed():
		turret_img.decompress()
	var view_size: Vector2 = main.get_viewport().get_visible_rect().size
	print("hull texture %s, hull transform with canvas %s, visible rect %s" % [hull.texture.get_size(), hull.get_global_transform_with_canvas(), view_size])
	for n in PIXEL_NAMES:
		var c := hull_img.get_pixelv(TEXELS[n])
		print("  %s texel %s in the imported hull_right.png: (%d, %d, %d) a %d; brief source %s"
			% [n, TEXELS[n], c.r8, c.g8, c.b8, c.a8, SOURCE[n]])

	var csv := FileAccess.open(OUT_DIR + "hit_flash_pixels.csv", FileAccess.WRITE)
	if csv == null:
		_fail("cannot write hit_flash_pixels.csv")
		return
	csv.store_line("value,pixel,texel,view_x,view_y,x,y,centre_rgb,mean3x3_rgb,predicted_rgb,maxdiff_centre,maxdiff_mean,turret_alpha_max_3x3,param_after,file")

	var any_fail := false
	for vi in VALUES.size():
		var value: float = VALUES[vi]
		var path := OUT_DIR + "hit_flash_%.1f.png" % value
		print("--- %s = %.1f" % [PARAM, value])
		await capture(driver, mat, PARAM, value, path)
		if _last_save_err != OK:
			any_fail = true
		var img := _last_image
		var scale := Vector2(img.get_size()) / view_size
		var param_after = mat.get_shader_parameter(PARAM)
		print("  image %dx%d format %d, view->image scale %s" % [img.get_width(), img.get_height(), img.get_format(), scale])
		print("  %-3s %-10s %-12s %-15s %-21s %-15s %s" % ["px", "texel", "image x,y", "centre", "3x3 mean", "predicted", "max|d| centre/mean   turret a"])
		for n in PIXEL_NAMES:
			var vp := _texel_to_view(hull, TEXELS[n])
			var px := Vector2i(floori(vp.x * scale.x), floori(vp.y * scale.y))
			var centre := _rgb(img, px)
			var mean := _mean3(img, px)
			var pred: Array = PREDICTED[vi].get(n, [])
			var d_c := "-"
			var d_m := "-"
			if not pred.is_empty():
				var dc := _maxdiff(centre, pred)
				var dm := _maxdiff(mean, pred)
				d_c = "%.0f" % dc
				d_m = "%.1f" % dm
			var cover := 0.0
			for dy in range(-1, 2):
				for dx in range(-1, 2):
					var q := (Vector2(px + Vector2i(dx, dy)) + Vector2(0.5, 0.5)) / scale
					cover = maxf(cover, _alpha_at(turret, turret_img, q))
			print("  %-3s %-10s %-12s %-15s %-21s %-15s %s / %s   %.2f%s" % [n, TEXELS[n], "%d,%d" % [px.x, px.y],
				_fmt(centre, 0), _fmt(mean, 1), _fmt(pred, 0) if not pred.is_empty() else "none", d_c, d_m, cover,
				"  (turret covers this pixel)" if cover > 0.0 else ""])
			csv.store_line("%.1f,%s,%d %d,%.2f,%.2f,%d,%d,%s,%s,%s,%s,%s,%.3f,%s,%s" % [value, n, TEXELS[n].x, TEXELS[n].y,
				vp.x, vp.y, px.x, px.y, _fmt(centre, 0), _fmt(mean, 1), _fmt(pred, 0) if not pred.is_empty() else "none",
				d_c, d_m, cover, param_after, path.get_file()])

	csv.close()
	mat.set_shader_parameter(PARAM, 0.0)
	print("wrote %shit_flash_pixels.csv (tolerance in the brief: +-%d per channel)" % [OUT_DIR, TOLERANCE])
	await process_frame
	quit(1 if any_fail else 0)


## Viewport position of the centre of `texel`, using the Sprite2D's own drawing rule:
## dest rect = (offset - size/2 if centered, size); flip_h / flip_v mirror the source rect.
func _texel_to_view(s: Sprite2D, texel: Vector2i) -> Vector2:
	var size := s.texture.get_size()
	var t := Vector2(texel) + Vector2(0.5, 0.5)
	if s.flip_h:
		t.x = size.x - t.x
	if s.flip_v:
		t.y = size.y - t.y
	var local := t + s.offset
	if s.centered:
		local -= size / 2.0
	return s.get_global_transform_with_canvas() * local


## Alpha of the sprite's texel drawn at viewport point `vp` (0 if outside its texture).
func _alpha_at(s: Sprite2D, img: Image, vp: Vector2) -> float:
	var size := s.texture.get_size()
	var t := s.get_global_transform_with_canvas().affine_inverse() * vp - s.offset
	if s.centered:
		t += size / 2.0
	if s.flip_h:
		t.x = size.x - t.x
	if s.flip_v:
		t.y = size.y - t.y
	var ti := Vector2i(floori(t.x), floori(t.y))
	if ti.x < 0 or ti.y < 0 or ti.x >= img.get_width() or ti.y >= img.get_height():
		return 0.0
	return img.get_pixelv(ti).a


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


func _maxdiff(a: Array, b: Array) -> float:
	var m := 0.0
	for k in 3:
		m = maxf(m, absf(float(a[k]) - float(b[k])))
	return m


func _fmt(a: Array, decimals: int) -> String:
	var f := "%." + str(decimals) + "f"
	return " ".join(PackedStringArray(a.map(func(v): return f % float(v))))
