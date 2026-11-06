extends Node2D
## Frame-strip fixture for Effect A (CHANGE-BRIEF.md, Effect A "The frame strip"). Preview only:
## changes no game script. One real cover block (scripts/cover.gd, world = null, never hit) on the
## real ground tile, camera at (640, 360), zoom 1. The burst sits where a shell flying right
## (dir (1, 0)) touches the block's left face, drawn at shell.gd's DRAW_OFFSET, rotated to
## (-dir).angle() = PI, as main.gd's spawn_cover_burst() will place it.
## Frame numbers are Engine.get_frames_drawn(), which equals the Movie Maker frame number.

const BURST := preload("res://effects/cover_hit_burst.tscn")
const COVER_HALF_WIDTH := 36.3  # cover.gd: RectangleShape2D 72.6 x 22
const SHELL_RADIUS := 3.0  # shell.gd: CircleShape2D radius
const DRAW_OFFSET := Vector2(0.0, -10.85)  # shell.gd line 5
const SHELL_DIR := Vector2(1, 0)
const FIRST_FRAME := 10
const RETRIGGER_FRAME := 16

## Second burst at frame 16 (0.2 s later, inside one lifetime), for the overlap read.
@export var retrigger := false
## Fixed seed for this preview's instances only; the effect scene never sets one.
@export var fixed_seed := 7

@onready var cover: Node2D = $Cover
@onready var fx: Node2D = $FX

var _fired := {}


func _process(_delta: float) -> void:
	var f := Engine.get_frames_drawn()
	if f >= FIRST_FRAME and not _fired.has(FIRST_FRAME):
		_fired[FIRST_FRAME] = true
		_spawn(fixed_seed, f)
	if retrigger and f >= RETRIGGER_FRAME and not _fired.has(RETRIGGER_FRAME):
		_fired[RETRIGGER_FRAME] = true
		_spawn(fixed_seed + 1, f)


func _spawn(seed_value: int, frame: int) -> void:
	var contact := cover.global_position + Vector2(-COVER_HALF_WIDTH - SHELL_RADIUS, 0.0)
	var burst := BURST.instantiate()
	burst.global_position = contact + DRAW_OFFSET
	burst.rotation = (-SHELL_DIR).angle()
	var emitters := []
	for c in burst.get_children():
		if c is CPUParticles2D:
			c.use_fixed_seed = true
			c.seed = seed_value
			emitters.append(c)
	fx.add_child(burst)
	for e in emitters:
		e.restart()  # restart after the seed is set, so the seed is used for this emission
	print("preview: burst (seed %d) at frame %d, position %s, rotation %.4f" % [seed_value, frame, burst.global_position, burst.rotation])
