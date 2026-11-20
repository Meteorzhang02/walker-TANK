# tools/bake_tank_clips.gd — bakes the A7 clips from CHANGE-BRIEF.md into committed resources.
# Run:  "$GODOT" --headless --path . --script res://tools/bake_tank_clips.gd
# Output: res://animations/motion_clips.tres (track_dust) for MotionAnim,
#         res://animations/fire_clips.tres (shoot) for FireAnim.
# Track paths are relative to each AnimationPlayer's root_node "..", i.e. the tank.
# Never build clips at runtime: tank.gd only loads these files.
extends SceneTree

# --- track_dust (cycle) — "Cycle spec" ---
const DUST_FPS := 10.0
const DUST_CELLS: Array[int] = [0, 1, 2, 3]
const DUST_PATH := "DustMount/Dust:frame"

# --- shoot (committing action) — "Phase table" ---
const FPS := 30.0
const STARTUP := 1
const ACTIVE := 1
const RECOVERY := 3
const POS_PATH := "Suspension:position"
const SCALE_PATH := "Suspension:scale"
const REST_POS := Vector2(0, 0)
const DOWN_POS := Vector2(0, 2)          # tank sits down 2 px
const REST_SCALE := Vector2(1, 1)
const SQUASH := Vector2(1.04, 0.96)


func _init() -> void:
	DirAccess.make_dir_recursive_absolute("res://animations")
	var ok := true
	var motion := AnimationLibrary.new()
	motion.add_animation("track_dust", _make_dust())
	ok = _save(motion, "res://animations/motion_clips.tres") and ok
	var fire := AnimationLibrary.new()
	fire.add_animation("shoot", _make_shoot())
	ok = _save(fire, "res://animations/fire_clips.tres") and ok
	quit(0 if ok else 1)


func _save(lib: AnimationLibrary, path: String) -> bool:
	var err := ResourceSaver.save(lib, path)
	print("bake: %s -> %s" % [path, error_string(err)])
	return err == OK


func _make_dust() -> Animation:
	var clip := Animation.new()
	var interval := 1.0 / DUST_FPS
	clip.length = DUST_CELLS.size() * interval   # last key to length = one interval
	clip.step = interval
	clip.loop_mode = Animation.LOOP_LINEAR
	var t := clip.add_track(Animation.TYPE_VALUE)
	clip.track_set_path(t, DUST_PATH)
	clip.value_track_set_update_mode(t, Animation.UPDATE_DISCRETE)
	for i in DUST_CELLS.size():
		clip.track_insert_key(t, i * interval, DUST_CELLS[i])
	return clip


func _make_shoot() -> Animation:
	var clip := Animation.new()
	var active_on := STARTUP                      # frame 1
	var recovery_on := STARTUP + ACTIVE           # frame 2
	var end_on := STARTUP + ACTIVE + RECOVERY     # frame 5
	clip.length = end_on / FPS
	clip.step = 1.0 / FPS
	clip.loop_mode = Animation.LOOP_NONE
	# A key's transition shapes the segment after it: 1.0 linear, 0.5 ease-out.
	var p := clip.add_track(Animation.TYPE_VALUE)
	clip.track_set_path(p, POS_PATH)
	clip.value_track_set_update_mode(p, Animation.UPDATE_CONTINUOUS)
	clip.track_insert_key(p, 0.0, REST_POS, 1.0)
	clip.track_insert_key(p, active_on / FPS, DOWN_POS, 0.5)
	clip.track_insert_key(p, end_on / FPS, REST_POS, 1.0)
	var s := clip.add_track(Animation.TYPE_VALUE)
	clip.track_set_path(s, SCALE_PATH)
	clip.value_track_set_update_mode(s, Animation.UPDATE_CONTINUOUS)
	clip.track_insert_key(s, 0.0, REST_SCALE, 1.0)
	clip.track_insert_key(s, active_on / FPS, SQUASH, 1.0)
	clip.track_insert_key(s, recovery_on / FPS, REST_SCALE, 1.0)
	return clip
