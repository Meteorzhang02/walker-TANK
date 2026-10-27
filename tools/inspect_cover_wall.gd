extends SceneTree
## tools/inspect_cover_wall.gd — prints cover_wall.glb's mesh surfaces, material names and UV ranges.
## Run: <godot_console.exe> --path . --script res://tools/inspect_cover_wall.gd


func _initialize() -> void:
	var ps: PackedScene = load("res://assets/models/cover_wall.glb")
	if ps == null:
		print("ERROR: could not load cover_wall.glb")
		quit(1)
		return
	var root := ps.instantiate()
	_walk(root, 0)
	root.free()
	quit(0)


func _walk(n: Node, depth: int) -> void:
	print("  ".repeat(depth), n.name, " (", n.get_class(), ")")
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		var m := mi.mesh
		print("  ".repeat(depth), "  mesh surfaces = ", m.get_surface_count(), "  aabb = ", m.get_aabb())
		for i in m.get_surface_count():
			var mat := m.surface_get_material(i)
			var mat_name := "null"
			if mat:
				mat_name = "%s (%s)" % [mat.resource_name, mat.get_class()]
				if mat is BaseMaterial3D:
					mat_name += " albedo=%s" % [(mat as BaseMaterial3D).albedo_color]
			var arr := m.surface_get_arrays(i)
			var verts = arr[Mesh.ARRAY_VERTEX] if arr.size() > 0 else null
			var uv = arr[Mesh.ARRAY_TEX_UV] if arr.size() > 0 else null
			var uv_info := "none"
			if uv != null and uv.size() > 0:
				var mn := Vector2(INF, INF)
				var mx := Vector2(-INF, -INF)
				for v in uv:
					mn.x = min(mn.x, v.x); mn.y = min(mn.y, v.y)
					mx.x = max(mx.x, v.x); mx.y = max(mx.y, v.y)
				uv_info = "%d uvs, min %s, max %s" % [uv.size(), mn, mx]
			var nverts = verts.size() if verts != null else -1
			print("  ".repeat(depth), "  surface ", i, ": material = ", mat_name, ", verts = ", nverts, ", uv = ", uv_info)
	for c in n.get_children():
		_walk(c, depth + 1)
