extends SceneTree
## A5 materials: checks CHANGE-BRIEF.md sections 4 and 5 (as revised 2026-10-27) on the files the
## headless dummy renderer can read: shader source text and compiled uniform list, the four
## ShaderMaterial .tres files, the .import settings, the hint PNG's stored pixels, and the
## structure of scenes/asset_room_3d.tscn and scenes/hint_experiment.tscn.
##   bash scripts/run-test.sh test_materials.gd 60
##
## What this does NOT prove: how anything looks (nothing is drawn headless), the measured grey
## values of the hint experiment, the brick look under the Sun, or shadows. "In view" is computed
## from Camera3D's transform and fov for a 1280x720 view (keep_height), not from a render.
## Expected to FAIL until the human acts: the hint PNG checks (until tools/make_hint_png.gd is run
## and the PNG imported), the hint materials and scene (they need the imported PNG), and CoverWall
## surface 0 (until Use External is set on M_Brick in cover_wall.glb's import).

const BRICK_SHADER := "res://shaders/brick_surface.gdshader"
const HINT_SHADER := "res://shaders/hint_experiment.gdshader"
const INTACT := "res://materials/cover_wall_intact.tres"
const DAMAGED := "res://materials/cover_wall_damaged.tres"
const HINT_SRGB := "res://materials/hint_srgb.tres"
const HINT_RAW := "res://materials/hint_raw.tres"
const DIFF := "res://assets/textures/brick/red_bricks_04_diff_1k.png"
const ROUGH := "res://assets/textures/brick/red_bricks_04_rough_1k.png"
const NOR := "res://assets/textures/brick/red_bricks_04_nor_gl_1k.png"
const GREY := "res://assets/hint/grey_3x1.png"
const GREYS := [64, 128, 192]
const ROOM := "res://scenes/asset_room_3d.tscn"
const HINT_SCENE := "res://scenes/hint_experiment.tscn"
const WALL_GLB_IMPORT := "res://assets/models/cover_wall.glb.import"
const VIEW := Vector2(1280, 720)
const EPS := 1e-4

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


# ---------------------------------------------------------------- shader source parsing

## Returns {"uniforms": {name: {type, hints[], default, group, line}}, "order": [names], "render_mode": [..]}.
func _parse_shader(src: String) -> Dictionary:
	var uni := {}
	var order := []
	var rmode := []
	var group := ""
	var re_u := RegEx.new()
	re_u.compile("^\\s*uniform\\s+(\\w+)\\s+(\\w+)\\s*(?::\\s*([^=;]+?))?\\s*(?:=\\s*([^;]+?))?\\s*;")
	var re_g := RegEx.new()
	re_g.compile("^\\s*group_uniforms\\s*([\\w.]*)\\s*;")
	var re_r := RegEx.new()
	re_r.compile("^\\s*render_mode\\s+([^;]+);")
	var lines := src.split("\n")
	for i in lines.size():
		var line: String = lines[i].split("//")[0]
		var mg := re_g.search(line)
		if mg:
			group = mg.get_string(1)
			continue
		var mr := re_r.search(line)
		if mr:
			for t in mr.get_string(1).split(","):
				rmode.append(t.strip_edges())
			continue
		var mu := re_u.search(line)
		if mu:
			var hints := []
			if mu.get_string(3) != "":
				for h in mu.get_string(3).split(","):
					hints.append(h.strip_edges())
			uni[mu.get_string(2)] = {"type": mu.get_string(1), "hints": hints,
				"default": mu.get_string(4).strip_edges(), "group": group, "line": i + 1}
			order.append(mu.get_string(2))
	return {"uniforms": uni, "order": order, "render_mode": rmode}


## The sampler read by `texture(<name>, ...)` on the line that assigns `target` (ALBEDO, ROUGHNESS).
func _sampler_for(src: String, target: String) -> Dictionary:
	var re := RegEx.new()
	re.compile("\\b" + target + "\\s*=\\s*texture\\s*\\(\\s*(\\w+)")
	var lines := src.split("\n")
	for i in lines.size():
		var m := re.search(lines[i].split("//")[0])
		if m:
			return {"name": m.get_string(1), "line": i + 1}
	return {}


func _floats(s: String) -> Array:
	var re := RegEx.new()
	re.compile("(?<![\\w.])-?\\d+(?:\\.\\d+)?")  # not the 4 in vec4
	return re.search_all(s).map(func(m): return float(m.get_string()))


## The source default as a Godot value (float, Color, bool), or null if none / not understood.
func _default_value(u: Dictionary):
	var d: String = u.default
	if d == "":
		return null
	var f := _floats(d)
	match u.type:
		"float":
			return f[0] if f.size() == 1 else null
		"vec4":
			return Color(f[0], f[1], f[2], f[3]) if f.size() == 4 else null
		"bool":
			return d == "true"
	return null


func _same(a, b) -> bool:
	if a is Color and b is Color:
		return absf(a.r - b.r) <= EPS and absf(a.g - b.g) <= EPS and absf(a.b - b.b) <= EPS and absf(a.a - b.a) <= EPS
	if (a is float or a is int) and (b is float or b is int):
		return absf(float(a) - float(b)) <= EPS
	return a == b


## The value the shader receives: the material's parameter if set, otherwise the source default.
func _effective(mat: ShaderMaterial, uname: String, u: Dictionary):
	var v = mat.get_shader_parameter(uname)
	return _default_value(u) if v == null else v


func _tex_path(mat: ShaderMaterial, uname: String) -> String:
	var t = mat.get_shader_parameter(uname)
	return t.resource_path if t is Texture2D else "<%s>" % [t]


func _load_mat(path: String) -> ShaderMaterial:
	if not ResourceLoader.exists(path):
		return null
	var r = load(path)
	return r as ShaderMaterial


# ---------------------------------------------------------------- geometry helpers

func _meshes(n: Node, out: Array) -> Array:
	if n is MeshInstance3D and n.mesh != null:
		out.append(n)
	for c in n.get_children():
		_meshes(c, out)
	return out


func _world_aabb(n: Node) -> AABB:
	var box := AABB()
	var first := true
	for mi in _meshes(n, []):
		var w: AABB = mi.global_transform * mi.get_aabb()
		box = w if first else box.merge(w)
		first = false
	return box


func _corners(b: AABB) -> Array:
	var out := []
	for i in 8:
		out.append(b.get_endpoint(i))
	return out


## Every corner of `box` inside the camera frustum for a VIEW-sized view (keep_height).
## Returns the screen-space x range in pixels, or an empty array if any corner is outside.
func _in_view(cam: Camera3D, box: AABB) -> Array:
	var ty := tan(deg_to_rad(cam.fov) * 0.5)
	var tx := ty * VIEW.x / VIEW.y
	var inv := cam.global_transform.affine_inverse()
	var xs := []
	for p in _corners(box):
		var c: Vector3 = inv * p
		var depth := -c.z
		if depth <= cam.near or depth >= cam.far:
			return []
		var nx := c.x / depth / tx
		var ny := c.y / depth / ty
		if absf(nx) > 1.0 or absf(ny) > 1.0:
			return []
		xs.append((nx * 0.5 + 0.5) * VIEW.x)
	return [xs.min(), xs.max()]


func _import(path: String) -> ConfigFile:
	var cf := ConfigFile.new()
	return cf if cf.load(path) == OK else null


# ---------------------------------------------------------------- run

func _run() -> void:
	await _check_brick_shader_and_materials()
	_check_brick_imports()
	_check_hint_png()
	_check_hint_shader_and_materials()
	await _check_room()
	await _check_hint_scene()
	await _finish()


func _check_brick_shader_and_materials() -> void:
	print("--- brick_surface.gdshader")
	var shader: Shader = load(BRICK_SHADER) if ResourceLoader.exists(BRICK_SHADER) else null
	_check("brick shader loads: " + BRICK_SHADER, shader != null)
	if shader == null:
		return
	var src := FileAccess.get_file_as_string(BRICK_SHADER)
	var ps := _parse_shader(src)
	var uni: Dictionary = ps.uniforms
	_check("source: shader_type spatial", src.contains("shader_type spatial;"))
	var listed := {}
	for u in shader.get_shader_uniform_list():
		listed[u.name] = u
	_check("get_shader_uniform_list() is non-empty (compiled, %d entries)" % listed.size(), listed.size() > 0)
	var all_listed := true
	for n in uni:
		if not listed.has(n):
			all_listed = false
	_check("every source uniform is in the compiled uniform list (%s)" % [ps.order], all_listed and not uni.is_empty())

	var col := _sampler_for(src, "ALBEDO")
	var rough := _sampler_for(src, "ROUGHNESS")
	_check("source: ALBEDO is read from a sampler (%s, line %s)" % [col.get("name"), col.get("line")],
		not col.is_empty() and uni.has(col.name) and uni[col.name].type == "sampler2D")
	_check("source: ROUGHNESS is read from a sampler (%s, line %s)" % [rough.get("name"), rough.get("line")],
		not rough.is_empty() and uni.has(rough.name) and uni[rough.name].type == "sampler2D")
	if col.is_empty() or rough.is_empty() or not uni.has(col.name) or not uni.has(rough.name):
		return
	_check("source: colour sampler %s has source_color (line %d: %s)" % [col.name, uni[col.name].line, uni[col.name].hints],
		"source_color" in uni[col.name].hints)
	_check("source: roughness sampler %s has no source_color (line %d: %s)" % [rough.name, uni[rough.name].line, uni[rough.name].hints],
		not ("source_color" in uni[rough.name].hints))

	var params := []
	var groups := {}
	for n in ps.order:
		if uni[n].type != "sampler2D":
			params.append(n)
			if uni[n].group != "":
				groups[uni[n].group] = true
	_check("source: >= 4 non-sampler uniforms (%d: %s)" % [params.size(), params], params.size() >= 4)
	_check("source: non-sampler uniforms in >= 2 group_uniforms groups (%s)" % [groups.keys()], groups.size() >= 2)
	var defaults_ok := true
	for n in params:
		if _default_value(uni[n]) == null:
			defaults_ok = false
	_check("source: every non-sampler uniform has a readable default", defaults_ok)

	print("--- brick materials")
	var mi := _load_mat(INTACT)
	var md := _load_mat(DAMAGED)
	_check("intact loads as ShaderMaterial: " + INTACT, mi != null)
	_check("damaged loads as ShaderMaterial: " + DAMAGED, md != null)
	if mi == null or md == null:
		return
	_check("both use " + BRICK_SHADER + " (same Shader object)",
		mi.shader != null and mi.shader.resource_path == BRICK_SHADER and is_same(mi.shader, md.shader))
	for pair in [["intact", mi], ["damaged", md]]:
		var m: ShaderMaterial = pair[1]
		_check("%s: %s bound to %s (got %s)" % [pair[0], col.name, DIFF.get_file(), _tex_path(m, col.name)], _tex_path(m, col.name) == DIFF)
		_check("%s: %s bound to %s (got %s)" % [pair[0], rough.name, ROUGH.get_file(), _tex_path(m, rough.name)], _tex_path(m, rough.name) == ROUGH)
	var intact_defaults := true
	var diffs := []
	for n in params:
		var vi = _effective(mi, n, uni[n])
		var vd = _effective(md, n, uni[n])
		print("      %-16s intact %-24s damaged %s" % [n, vi, vd])
		if not _same(vi, _default_value(uni[n])):
			intact_defaults = false
		if not _same(vi, vd):
			diffs.append(n)
	_check("intact: every non-sampler value is the shader default", intact_defaults)
	_check("intact and damaged differ in >= 2 values (%s)" % [diffs], diffs.size() >= 2)
	if uni.has("albedo_tint") and uni.has("brightness"):
		_check("damaged: albedo_tint = Color(0.78, 0.72, 0.66, 1)", _same(_effective(md, "albedo_tint", uni.albedo_tint), Color(0.78, 0.72, 0.66, 1)))
		_check("damaged: brightness = 0.7", _same(_effective(md, "brightness", uni.brightness), 0.7))
	var others_default := true
	for n in params:
		if n in ["albedo_tint", "brightness"]:
			continue
		if not _same(_effective(md, n, uni[n]), _default_value(uni[n])):
			others_default = false
	_check("damaged: every other value is the shader default", others_default)


func _check_brick_imports() -> void:
	print("--- brick .import settings (brief section 5 as revised)")
	# [path, compress/normal_map]: 0 Detect, 1 Enable, 2 Disabled.
	for e in [[DIFF, 2], [ROUGH, 2], [NOR, 1]]:
		var cf := _import(e[0] + ".import")
		_check("%s.import readable" % e[0].get_file(), cf != null)
		if cf == null:
			continue
		var mode = cf.get_value("params", "compress/mode", null)
		var nm = cf.get_value("params", "compress/normal_map", null)
		var mip = cf.get_value("params", "mipmaps/generate", null)
		var d3 = cf.get_value("params", "detect_3d/compress_to", null)
		_check("%s: compress/mode=%s normal_map=%s mipmaps=%s detect_3d/compress_to=%s (want 2, %d, true, 0)"
			% [e[0].get_file(), mode, nm, mip, d3, e[1]],
			mode == 2 and nm == e[1] and mip == true and d3 == 0)


func _check_hint_png() -> void:
	print("--- hint PNG")
	var exists := FileAccess.file_exists(GREY)
	_check("%s exists (run tools/make_hint_png.gd)" % GREY, exists)
	if exists:
		var img := Image.load_from_file(ProjectSettings.globalize_path(GREY))
		_check("PNG reads as an Image", img != null)
		if img != null:
			_check("PNG is 3x1 (got %dx%d)" % [img.get_width(), img.get_height()], img.get_width() == 3 and img.get_height() == 1)
			var got := []
			var ok := img.get_width() == 3 and img.get_height() == 1
			for x in mini(img.get_width(), 3):
				var c := img.get_pixel(x, 0)
				got.append([c.r8, c.g8, c.b8])
				if c.r8 != GREYS[x] or c.g8 != GREYS[x] or c.b8 != GREYS[x]:
					ok = false
			_check("PNG pixels left to right are grey 64/128/192 (got %s)" % [got], ok)
	var cf := _import(GREY + ".import")
	_check("%s.import exists (PNG imported in the editor)" % GREY.get_file(), cf != null)
	if cf != null:
		var mode = cf.get_value("params", "compress/mode", null)
		var mip = cf.get_value("params", "mipmaps/generate", null)
		var d3 = cf.get_value("params", "detect_3d/compress_to", null)
		_check("grey_3x1.png: compress/mode=%s mipmaps=%s detect_3d/compress_to=%s (want 0 Lossless, false, 0)" % [mode, mip, d3],
			mode == 0 and mip == false and d3 == 0)


func _check_hint_shader_and_materials() -> void:
	print("--- hint_experiment.gdshader")
	var shader: Shader = load(HINT_SHADER) if ResourceLoader.exists(HINT_SHADER) else null
	_check("hint shader loads: " + HINT_SHADER, shader != null)
	if shader == null:
		return
	var src := FileAccess.get_file_as_string(HINT_SHADER)
	var ps := _parse_shader(src)
	var uni: Dictionary = ps.uniforms
	_check("get_shader_uniform_list() is non-empty (compiled)", shader.get_shader_uniform_list().size() > 0)
	_check("source: shader_type spatial", src.contains("shader_type spatial;"))
	_check("source: render_mode unshaded (%s)" % [ps.render_mode], "unshaded" in ps.render_mode)
	var samplers := []
	var with_srgb := []
	var nearest := true
	var bools := []
	for n in ps.order:
		if uni[n].type == "sampler2D":
			samplers.append(n)
			if "source_color" in uni[n].hints:
				with_srgb.append(n)
			if not ("filter_nearest" in uni[n].hints):
				nearest = false
		elif uni[n].type == "bool":
			bools.append(n)
	var without := samplers.filter(func(s): return not (s in with_srgb))
	_check("source: two samplers, one with source_color (%s), one without (%s)" % [with_srgb, without],
		samplers.size() == 2 and with_srgb.size() == 1 and without.size() == 1)
	_check("source: both samplers filter_nearest", nearest and samplers.size() == 2)
	_check("source: one bool uniform picks the sampler (%s)" % [bools], bools.size() == 1)
	if bools.size() != 1:
		return
	var b: String = bools[0]

	print("--- hint materials")
	var ms := _load_mat(HINT_SRGB)
	var mr := _load_mat(HINT_RAW)
	_check("hint_srgb loads as ShaderMaterial (needs the imported PNG)", ms != null)
	_check("hint_raw loads as ShaderMaterial (needs the imported PNG)", mr != null)
	if ms == null or mr == null:
		return
	_check("both use " + HINT_SHADER + " (same Shader object)",
		ms.shader != null and ms.shader.resource_path == HINT_SHADER and is_same(ms.shader, mr.shader))
	var tex_ok := true
	for m in [ms, mr]:
		for s in samplers:
			if _tex_path(m, s) != GREY:
				tex_ok = false
	_check("both samplers in both materials bound to " + GREY, tex_ok)
	_check("hint_srgb: %s = true" % b, _effective(ms, b, uni[b]) == true)
	_check("hint_raw: %s = false" % b, _effective(mr, b, uni[b]) == false)


func _check_room() -> void:
	print("--- asset_room_3d.tscn")
	var ps: PackedScene = load(ROOM)
	_check("asset_room_3d.tscn loads", ps != null)
	if ps == null:
		return
	var room: Node3D = ps.instantiate()
	root.add_child(room)
	await process_frame
	var w1 = room.get_node_or_null("CoverWall")
	var w2 = room.get_node_or_null("CoverWall2")
	var cam: Camera3D = room.get_node_or_null("Camera3D")
	_check("CoverWall exists", w1 != null)
	_check("CoverWall2 exists", w2 != null)
	if w1 == null or w2 == null or cam == null:
		room.queue_free()
		await process_frame
		return
	_check("CoverWall2 instances cover_wall.glb", w2.scene_file_path == "res://assets/models/cover_wall.glb")
	var m1: Array = _meshes(w1, [])
	var m2: Array = _meshes(w2, [])
	_check("each wall has one MeshInstance3D with 2 surfaces",
		m1.size() == 1 and m2.size() == 1 and m1[0].mesh.get_surface_count() == 2 and m2[0].mesh.get_surface_count() == 2)
	if m1.size() != 1 or m2.size() != 1:
		room.queue_free()
		await process_frame
		return
	var mi1: MeshInstance3D = m1[0]
	var mi2: MeshInstance3D = m2[0]

	var ov2 = mi2.get_surface_override_material(0)
	_check("CoverWall2 surface 0 override is cover_wall_damaged.tres (got %s)" % [ov2.resource_path if ov2 else null],
		ov2 != null and ov2.resource_path == DAMAGED)
	var a1 = mi1.get_active_material(0)
	_check("CoverWall surface 0 has no override (material comes from the import)", mi1.get_surface_override_material(0) == null)
	_check("CoverWall surface 0 resolves to cover_wall_intact.tres (got %s) [needs Use External]" % [a1.resource_path if a1 else null],
		a1 != null and a1.resource_path == INTACT)
	var cf := _import(WALL_GLB_IMPORT)
	var ext_path := ""
	if cf != null:
		var subs = cf.get_value("params", "_subresources", {})
		var mb = subs.get("materials", {}).get("M_Brick", {}) if subs is Dictionary else {}
		if mb is Dictionary and mb.get("use_external/enabled", false) == true:
			ext_path = str(mb.get("use_external/path", ""))
			if ext_path.begins_with("uid://"):
				var id := ResourceUID.text_to_id(ext_path)
				ext_path = ResourceUID.get_id_path(id) if ResourceUID.has_id(id) else ext_path
	_check("cover_wall.glb.import: M_Brick use_external/enabled, use_external/path -> %s (got '%s')" % [INTACT, ext_path], ext_path == INTACT)
	for pair in [["CoverWall", mi1], ["CoverWall2", mi2]]:
		var mi: MeshInstance3D = pair[1]
		var a = mi.get_active_material(1)
		_check("%s surface 1 is the imported M_BrickDark (got %s), no override" % [pair[0], a.resource_name if a else null],
			a is StandardMaterial3D and a.resource_name == "M_BrickDark" and mi.get_surface_override_material(1) == null)

	# Placement: on the floor, no overlap, both walls fully in view.
	var b1 := _world_aabb(w1)
	var b2 := _world_aabb(w2)
	print("      CoverWall  aabb %s .. %s" % [b1.position, b1.end])
	print("      CoverWall2 aabb %s .. %s" % [b2.position, b2.end])
	var floor_node = room.get_node_or_null("Floor")
	var floor_box: AABB = _world_aabb(floor_node) if floor_node else AABB()
	_check("CoverWall2 stands on the floor (lowest y %.4f, floor y %.4f; inside the floor's x/z)" % [b2.position.y, floor_box.position.y],
		floor_node != null and absf(b2.position.y - floor_box.end.y) <= 0.01
		and b2.position.x >= floor_box.position.x and b2.end.x <= floor_box.end.x
		and b2.position.z >= floor_box.position.z and b2.end.z <= floor_box.end.z)
	var hits := []
	for n in room.get_children():
		if n == w2 or n == floor_node or not (n is Node3D) or _meshes(n, []).is_empty():
			continue
		if b2.intersects(_world_aabb(n)):
			hits.append(n.name)
	_check("CoverWall2 overlaps no other node (overlaps: %s)" % [hits], hits.is_empty())
	for pair in [["CoverWall", b1], ["CoverWall2", b2]]:
		var r := _in_view(cam, pair[1])
		_check("%s fully in view of Camera3D at 1280x720 (screen x %s)" % [pair[0], r], not r.is_empty())
	room.queue_free()
	await process_frame


func _check_hint_scene() -> void:
	print("--- hint_experiment.tscn")
	var ps: PackedScene = load(HINT_SCENE) if ResourceLoader.exists(HINT_SCENE) else null
	_check("hint_experiment.tscn loads (needs the imported PNG)", ps != null)
	if ps == null:
		return
	var scene: Node3D = ps.instantiate()
	root.add_child(scene)
	await process_frame
	var cams: Array = scene.find_children("*", "Camera3D", true, false)
	_check("one Camera3D", cams.size() == 1)
	var envs: Array = scene.find_children("*", "WorldEnvironment", true, false)
	_check("one WorldEnvironment with an Environment", envs.size() == 1 and envs[0].environment != null)
	if envs.size() == 1 and envs[0].environment != null:
		var env: Environment = envs[0].environment
		_check("tonemap Linear (%d), exposure 1.0 (%.3f)" % [env.tonemap_mode, env.tonemap_exposure],
			env.tonemap_mode == Environment.TONE_MAPPER_LINEAR and absf(env.tonemap_exposure - 1.0) <= EPS)
		_check("glow, fog, volumetric fog, SSAO, SSR, SDFGI, adjustments all off",
			not env.glow_enabled and not env.fog_enabled and not env.volumetric_fog_enabled and not env.ssao_enabled
			and not env.ssr_enabled and not env.sdfgi_enabled and not env.adjustment_enabled)
		_check("background is a colour, mid grey (%s)" % [env.background_color],
			env.background_mode == Environment.BG_COLOR and _same(env.background_color, Color(0.5, 0.5, 0.5, 1)))
	var quads := []
	for mi in _meshes(scene, []):
		if mi.mesh is QuadMesh:
			quads.append(mi)
	quads.sort_custom(func(a, b): return a.global_position.x < b.global_position.x)
	_check("two QuadMesh quads (%d)" % quads.size(), quads.size() == 2)
	if quads.size() != 2 or cams.size() != 1:
		scene.queue_free()
		await process_frame
		return
	var want := [HINT_SRGB, HINT_RAW]
	for i in 2:
		var q: MeshInstance3D = quads[i]
		var m = q.material_override
		_check("%s quad uses %s (got %s)" % [["left", "right"][i], want[i].get_file(), m.resource_path if m else null],
			m != null and m.resource_path == want[i])
		var r := _in_view(cams[0] as Camera3D, _world_aabb(q))
		var band: float = (r[1] - r[0]) / 3.0 if not r.is_empty() else 0.0
		_check("%s quad fully in view, each band %.0f px wide at 1280x720 (want >= 50)" % [q.name, band], band >= 50.0)
		var label_ok := false
		var labels: Array = q.find_children("*", "Label3D", true, false)
		for l in labels:
			if l.text.contains(want[i].get_file().get_basename()) and l.position.y > 0.0:
				label_ok = true
		_check("%s has a Label3D above it naming %s" % [q.name, want[i].get_file().get_basename()], label_ok)
	scene.queue_free()
	await process_frame
