extends Node2D
## GPU-time fixture for the Visual Profiler (CHANGE-BRIEF.md, "Price predictions and budget").
## Price-only setup, not gameplay: loads the game scene, freezes the enemy AI as
## tests/cost_particles.gd does, and drives the effects at their peak through the game's own calls.
## Keys: 0 = both effects off, 1 = Effect A at its peak, 2 = Effect B at its peak, 3 = both.
## Changes no game script.

const SCENE := preload("res://scenes/main.tscn")
const MODE_NAMES := ["0: both effects off", "1: Effect A peak (about 4 bursts)", "2: Effect B peak (4 tanks, ratio 1.0)", "3: both"]

## Effect A, as in cost_particles.gd (c): two of 4 fixed cover-top points every 0.35 s, alternating.
const BURST_POINTS := [Vector2(320, 472), Vector2(300, 242), Vector2(560, 362), Vector2(820, 222)]
const SPAWN_EVERY := 0.35
const BURSTS_PER_TICK := 2

var main
var mode := 0
var label: Label
var _spawn_left := 0.0
var _spawn_index := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	main = SCENE.instantiate()
	add_child(main)
	# Price-only setup: target = null makes each enemy's _think() hold still and never fire
	# (enemy.gd line 19). The enemies keep processing, so their smoke runs.
	for e in main.enemies:
		e.target = null
	var ui := CanvasLayer.new()
	ui.layer = 11
	add_child(ui)
	label = Label.new()
	label.position = Vector2(16, 40)
	label.add_theme_font_size_override("font_size", 20)
	label.add_theme_color_override("font_outline_color", Color(0, 0, 0))
	label.add_theme_constant_override("outline_size", 6)
	ui.add_child(label)
	_set_mode(0)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_0, KEY_KP_0: _set_mode(0)
			KEY_1, KEY_KP_1: _set_mode(1)
			KEY_2, KEY_KP_2: _set_mode(2)
			KEY_3, KEY_KP_3: _set_mode(3)
			KEY_F9: _toggle_vsync()


func _set_mode(m: int) -> void:
	mode = m
	_spawn_left = 0.0
	# Effect B: h = 0 (alive) through follow() gives emitting and amount_ratio 1.0; h = 1 stops it
	# and leaves the column in the air to fade. Health is not written.
	var smoke_on := mode == 2 or mode == 3
	for t in [main.player] + main.enemies:
		t.smoke.follow(0.0 if smoke_on else 1.0, false)


func _process(delta: float) -> void:
	if (mode == 1 or mode == 3) and not get_tree().paused:
		_spawn_left -= delta
		if _spawn_left <= 0.0:
			_spawn_left += SPAWN_EVERY
			for i in BURSTS_PER_TICK:
				main.spawn_cover_burst(null, BURST_POINTS[_spawn_index % BURST_POINTS.size()])
				_spawn_index += 1
	label.text = "Price mode %s\nFPS %d" % [MODE_NAMES[mode], Engine.get_frames_per_second()]


## Debug key for the FPS comparison only (A6 Use It): F9 toggles vsync in this window.
## Not a project-setting change; the game itself has no such key.
func _toggle_vsync() -> void:
	var off := DisplayServer.window_get_vsync_mode() == DisplayServer.VSYNC_DISABLED
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if off else DisplayServer.VSYNC_DISABLED)
	print("PRICE vsync now: %s" % ("on" if off else "off"))
