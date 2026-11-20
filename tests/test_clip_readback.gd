# tests/test_clip_readback.gd — A7 read-back for track_dust and shoot against CHANGE-BRIEF.md.
# Run:  ./scripts/run-test.sh test_clip_readback.gd 60
# Proves the clips are STRUCTURED as the brief says. It draws nothing, so it
# proves nothing about whether the motion reads (frame strip and play do that).
extends SceneTree

const TANK_SCRIPT := "res://scripts/tank.gd"

const DUST_FPS := 10.0
const DUST_CELLS: Array[int] = [0, 1, 2, 3]
const DUST_HFRAMES := 4
const DUST_VFRAMES := 1

const FPS := 30.0
const SHOOT_END_FRAME := 5
const POS_KEY_FRAMES: Array[int] = [0, 1, 5]
const SCALE_KEY_FRAMES: Array[int] = [0, 1, 2]

var passed := 0
var failed := 0


func _init() -> void:
	_run.call_deferred()


func check(label: String, ok: bool) -> void:
	if ok:
		passed += 1
		print("PASS  ", label)
	else:
		failed += 1
		print("FAIL  ", label)


func _run() -> void:
	var script := load(TANK_SCRIPT) as GDScript
	check("tank.gd loads", script != null)
	if script == null:
		_finish(null)
		return
	var tank: Node = script.new()
	root.add_child(tank)          # _ready() builds the nodes
	await process_frame

	var motion := tank.get_node_or_null("MotionAnim") as AnimationPlayer
	var fire := tank.get_node_or_null("FireAnim") as AnimationPlayer
	check("MotionAnim is an AnimationPlayer", motion != null)
	check("FireAnim is an AnimationPlayer", fire != null)
	for player in [motion, fire]:
		if player == null:
			continue
		var problems := track_problems(player)
		for p in problems:
			print("      ", p)
		check("%s: every track resolves (%d problems)" % [player.name, problems.size()], problems.is_empty())
		check("%s: callback_mode_process is PHYSICS" % player.name,
			player.callback_mode_process == AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS)
		check("%s: autoplay empty" % player.name, player.autoplay == "")

	var dust := tank.get_node_or_null("DustMount/Dust") as Sprite2D
	check("DustMount/Dust is a Sprite2D", dust != null)
	if dust != null:
		check("dust sheet loaded", dust.texture != null)
		check("dust sliced %dx%d" % [DUST_HFRAMES, DUST_VFRAMES],
			dust.hframes == DUST_HFRAMES and dust.vframes == DUST_VFRAMES)
	if motion != null:
		_check_dust(motion, dust)
	if fire != null:
		_check_shoot(fire)
	_finish(tank)


func _check_dust(player: AnimationPlayer, sprite: Sprite2D) -> void:
	check("track_dust exists", player.has_animation("track_dust"))
	if not player.has_animation("track_dust"):
		return
	var clip := player.get_animation("track_dust")
	var interval := 1.0 / DUST_FPS
	var tol := 0.5 * interval
	check("track_dust loops LINEAR", clip.loop_mode == Animation.LOOP_LINEAR)
	check("track_dust step = 0.1", is_equal_approx(clip.step, interval))
	check("track_dust length = 0.4", absf(clip.length - DUST_CELLS.size() * interval) < tol)
	check("track_dust has 1 track", clip.get_track_count() == 1)
	if clip.get_track_count() < 1:
		return
	var t := 0
	check("track_dust track is a value track", clip.track_get_type(t) == Animation.TYPE_VALUE)
	if clip.track_get_type(t) == Animation.TYPE_VALUE:
		check("track_dust discrete", clip.value_track_get_update_mode(t) == Animation.UPDATE_DISCRETE)
	var n := clip.track_get_key_count(t)
	check("track_dust key count = %d" % DUST_CELLS.size(), n == DUST_CELLS.size())
	for k in mini(n, DUST_CELLS.size()):
		var v := int(clip.track_get_key_value(t, k))
		check("track_dust key %d at %.1f s" % [k, k * interval], absf(clip.track_get_key_time(t, k) - k * interval) < tol)
		check("track_dust key %d = cell %d" % [k, DUST_CELLS[k]], v == DUST_CELLS[k])
		if sprite != null:
			check("track_dust key %d inside the sheet" % k, v >= 0 and v < sprite.hframes * sprite.vframes)
	if n >= 2:
		check("seam: no duplicate across the wrap",
			clip.track_get_key_value(t, n - 1) != clip.track_get_key_value(t, 0))
		check("seam: last key to length = one interval",
			absf((clip.length - clip.track_get_key_time(t, n - 1)) - interval) < tol)


func _check_shoot(player: AnimationPlayer) -> void:
	check("shoot exists", player.has_animation("shoot"))
	if not player.has_animation("shoot"):
		return
	var clip := player.get_animation("shoot")
	var tol := 0.5 / FPS
	check("shoot does not loop", clip.loop_mode == Animation.LOOP_NONE)
	check("shoot step = 1/30", is_equal_approx(clip.step, 1.0 / FPS))
	check("shoot length = frame %d" % SHOOT_END_FRAME, absf(clip.length - SHOOT_END_FRAME / FPS) < tol)
	check("shoot has 2 tracks", clip.get_track_count() == 2)
	for t in clip.get_track_count():
		var path := clip.track_get_path(t)
		var prop := String(path.get_concatenated_subnames())
		check("shoot track %d is on Suspension" % t, String(path.get_concatenated_names()) == "Suspension")
		var expected: Array[int] = []
		if prop == "position":
			expected = POS_KEY_FRAMES
		elif prop == "scale":
			expected = SCALE_KEY_FRAMES
		else:
			check("shoot track %d (%s) is in the brief" % [t, prop], false)
			continue
		var n := clip.track_get_key_count(t)
		check("shoot %s key count = %d" % [prop, expected.size()], n == expected.size())
		for k in mini(n, expected.size()):
			check("shoot %s key on frame %d" % [prop, expected[k]],
				absf(clip.track_get_key_time(t, k) - expected[k] / FPS) < tol)


# From the assignment: every track resolves to a real node, and to a real
# property, bone or blend shape where the track names one.
static func track_problems(player: AnimationPlayer) -> Array[String]:
	var problems: Array[String] = []
	var root := player.get_node_or_null(player.root_node)
	if root == null:
		problems.append("root_node %s resolves to nothing" % player.root_node)
		return problems
	for clip_name in player.get_animation_list():
		var clip := player.get_animation(clip_name)
		for t in clip.get_track_count():
			var path := clip.track_get_path(t)
			var node := root.get_node_or_null(NodePath(path.get_concatenated_names()))
			if node == null:
				problems.append("%s track %d: no node at %s" % [clip_name, t, path])
				continue
			if path.get_subname_count() == 0:
				continue
			var sub := path.get_subname(0)
			match clip.track_get_type(t):
				Animation.TYPE_POSITION_3D, Animation.TYPE_ROTATION_3D, Animation.TYPE_SCALE_3D:
					var skeleton := node as Skeleton3D
					if skeleton == null or skeleton.find_bone(sub) == -1:
						problems.append("%s track %d: no bone %s on %s" % [clip_name, t, sub, node.name])
				Animation.TYPE_BLEND_SHAPE:
					var mesh := node as MeshInstance3D
					if mesh == null or mesh.find_blend_shape_by_name(sub) == -1:
						problems.append("%s track %d: no blend shape %s on %s" % [clip_name, t, sub, node.name])
				_:
					if not (sub in node):
						problems.append("%s track %d: %s has no property %s" % [clip_name, t, node.name, sub])
	return problems


func _finish(tank: Node) -> void:
	print("readback: %d passed, %d failed" % [passed, failed])
	if tank != null:
		tank.queue_free()
		await process_frame
	quit(1 if failed > 0 else 0)
