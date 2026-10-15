extends SceneTree
## Headless check of the three A3 .glb assets against CHANGE-BRIEF.md (sizes in Godot x, y, z;
## Blender's Z-up height becomes Godot's y). Each .glb is loaded, instantiated at the origin
## and measured by merging its MeshInstance3D global AABBs. Per asset it checks: size within
## 0.01 m of the brief, lowest y 0.00 +/-0.01, root node scale 1, 1, 1, and that y is the
## axis whose size matches the brief's height. Exit code 1 on any FAIL.
## The 0.01 m tolerance is tighter than the brief's own +/-0.1 m (+/-0.15 m for the hedgehog).
##
## What this does NOT prove:
## - how the assets look: shape details, colours, materials, lighting or shadows (headless
##   uses a dummy renderer, nothing is drawn);
## - triangle or object counts against the 60-triangle budget;
## - that the assets rest on the floor in scenes/asset_room_3d.tscn: the .glb is checked at
##   the origin, not at its placement in that scene, and nothing tests the scene's floor,
##   camera framing or light;
## - that a mesh is the right way round within its box (e.g. a crate turned 180 degrees about y
##   has the same AABB), or that child nodes have no hidden rotation that happens to keep
##   the box size.
## Run from the project folder (import the project first):
##   godot --headless --path . --fixed-fps 60 --script res://tests/check_a3_assets.gd

const TOL := 0.01
const ASSETS := {
	"cover_wall": Vector3(4.0, 1.8, 1.0),
	"ammo_crate": Vector3(1.24, 0.71, 0.84),
	"tank_hedgehog": Vector3(1.794, 1.400, 1.794),
}

var failures := 0


func _initialize() -> void:
	_run.call_deferred()


func _check(label: String, ok: bool) -> void:
	print(("PASS  " if ok else "FAIL  ") + label)
	if not ok:
		failures += 1


func _merged_aabb(node: Node, box: AABB, found: Array) -> AABB:
	if node is MeshInstance3D and node.mesh != null:
		var world: AABB = node.global_transform * node.get_aabb()
		box = world if found.is_empty() else box.merge(world)
		found.append(node)
	for child in node.get_children():
		box = _merged_aabb(child, box, found)
	return box


func _run() -> void:
	for asset_name in ASSETS:
		var want: Vector3 = ASSETS[asset_name]
		var path := "res://assets/models/%s.glb" % asset_name
		print("--- %s (%s)" % [asset_name, path])
		var scene: PackedScene = load(path)
		_check("%s loads as PackedScene" % asset_name, scene != null)
		if scene == null:
			continue
		var inst: Node3D = scene.instantiate()
		root.add_child(inst)
		await process_frame

		var meshes := []
		var box := _merged_aabb(inst, AABB(), meshes)
		_check("%s has mesh instances (%d)" % [asset_name, meshes.size()], not meshes.is_empty())
		if meshes.is_empty():
			inst.queue_free()
			continue
		var size := box.size
		var d := size - want
		print("      aabb position %s  end %s" % [box.position, box.end])
		_check("%s size %s vs brief %s (diff %.4f, %.4f, %.4f; tol %.2f)"
				% [asset_name, size, want, d.x, d.y, d.z, TOL],
				absf(d.x) <= TOL and absf(d.y) <= TOL and absf(d.z) <= TOL)
		_check("%s lowest y %.4f (want 0.00 +/-%.2f)" % [asset_name, box.position.y, TOL],
				absf(box.position.y) <= TOL)
		_check("%s root scale %s (want 1, 1, 1)" % [asset_name, inst.scale],
				inst.scale.is_equal_approx(Vector3.ONE))
		# Height axis: the axis whose size matches the brief height (want.y). Several axes can
		# match when sizes coincide, so this passes only if y matches.
		var height_axes := []
		for i in 3:
			if absf(size[i] - want.y) <= TOL:
				height_axes.append(["x", "y", "z"][i])
		_check("%s height (%.3f m) is on axis %s (want y)" % [asset_name, want.y, height_axes],
				"y" in height_axes)
		inst.queue_free()
		await process_frame

	print("RESULT: %s (%d failure(s))" % ["PASS" if failures == 0 else "FAIL", failures])
	quit(1 if failures > 0 else 0)
