extends Node2D
## Frame-strip fixture for the `shoot` clip (CHANGE-BRIEF.md, "Frame strip"), and the `track_dust`
## cycle in the same capture. Preview only: instances the real scenes/main.tscn as the child "Main"
## and drives it from outside; it changes no game script.
##
## Windowed Movie Maker capture at --fixed-fps 30 (2 physics ticks per rendered frame at 60 Hz).
## Frame numbers are Engine.get_frames_drawn(), which equals the Movie Maker frame number
## (the same convention as previews/damage_smoke_preview.gd).
##
## What it drives:
## - Enemies: target = null, as in tests/test_pins.gd. They stay in physics (process_mode untouched);
##   enemy _think() then sets move_dir = ZERO and returns before any try_fire().
## - YunqiZ stays at the game's own spawn (main.gd SPAWN = 150, 610): real arena ground, about
##   130 px below the nearest cover block, which is outside the zoomed view.
## - Facing right: the hull only turns when the tank moves (tank.gd), so a short "move_right" tap
##   (SETUP_FROM..SETUP_TO) turns it right through the game's own code. The turret follows the real
##   mouse (player.gd), so the cursor is warped every physics tick to a point right of the turret.
## - Camera: main.camera zoom 4, centred on YunqiZ. main.gd _process() rewrites camera.offset every
##   frame (shake), so the preview moves camera.position instead; it follows YunqiZ.
## - Input is pressed and released in _physics_process(), which runs before the player's (parent
##   before child, and process_physics_priority -1), so the player's _think() sees "fire" on the
##   first physics tick of the trigger frame: press tick P = first tick of frame N, as the brief's
##   strip assumes (N startup, N+1 active, N+2 recovery, N+5 end).

const SETUP_FROM := 5        # move_right tap that turns the hull to face right
const SETUP_TO := 8          # released on this frame (held frames 5-7)
const TRIGGER_FRAME := 30    # "fire" pressed for one frame, released on the next
const MOVE_FROM := 60        # "move_right" held for MOVE_FRAMES frames
const MOVE_FRAMES := 40
const QUIT_FRAME := 110
const ZOOM := 4.0
const AIM_AHEAD := 60.0      # world px right of the turret pivot for the warped cursor

@onready var main = $Main

var _done := {}


func _ready() -> void:
	process_physics_priority = -1
	for e in main.enemies:
		e.target = null
	main.camera.zoom = Vector2(ZOOM, ZOOM)
	_follow()
	print("PREVIEW start frame %d, YunqiZ at %s" % [Engine.get_frames_drawn(), str(main.player.global_position)])


func _physics_process(_delta: float) -> void:
	var f := Engine.get_frames_drawn()
	_aim_right()
	if _once(f, "setup_press", SETUP_FROM):
		Input.action_press("move_right")
		_done["setup_from"] = f
	if _once(f, "setup_release", SETUP_TO):
		Input.action_release("move_right")
		print("SETUP move_right frames %d-%d (turns the hull right)" % [_done["setup_from"], f - 1])
	if _once(f, "fire_press", TRIGGER_FRAME):
		Input.action_press("fire")
		print("TRIGGER frame %d" % f)
	if _once(f, "fire_release", TRIGGER_FRAME + 1):
		Input.action_release("fire")
	if _once(f, "move_press", MOVE_FROM):
		Input.action_press("move_right")
		_done["move_from"] = f
	if _once(f, "move_release", MOVE_FROM + MOVE_FRAMES):
		Input.action_release("move_right")
		print("MOVE frames %d-%d" % [_done["move_from"], f - 1])


func _process(_delta: float) -> void:
	_follow()
	if Engine.get_frames_drawn() >= QUIT_FRAME and not _done.has("quit"):
		_done["quit"] = true
		print("QUIT frame %d" % Engine.get_frames_drawn())
		get_tree().quit()


## True once: on the first physics tick of frame `at` (or the first tick after it).
func _once(f: int, key: String, at: int) -> bool:
	if f >= at and not _done.has(key):
		_done[key] = true
		return true
	return false


func _follow() -> void:
	main.camera.position = main.player.global_position


## Real cursor, as in the A6 capture driver: Viewport.warp_mouse takes canvas coordinates after the
## camera, and player.gd reads it back through get_global_mouse_position() with the same transform.
func _aim_right() -> void:
	var vp := get_viewport()
	var pivot: Vector2 = main.player.global_position + main.player.TURRET_OFFSET
	vp.warp_mouse(vp.get_canvas_transform() * (pivot + Vector2(AIM_AHEAD, 0.0)))
