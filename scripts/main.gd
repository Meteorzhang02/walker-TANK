extends Node2D
## walker-TANK asset slice: one arena, destructible cover, three enemy tanks that move and fire.
## Destroy all three to win. If YunqiZ is destroyed it respawns at the spawn point; destroyed
## enemies stay destroyed (their wrecks remain).

const PlayerScript := preload("res://scripts/player.gd")
const EnemyScript := preload("res://scripts/enemy.gd")
const ShellScript := preload("res://scripts/shell.gd")
const CoverScript := preload("res://scripts/cover.gd")
const AudioScript := preload("res://scripts/audio.gd")

const SPAWN := Vector2(150, 610)
const ENEMY_SPAWNS := [Vector2(1120, 140), Vector2(1090, 580), Vector2(660, 130)]
const COVERS := [Vector2(320, 480), Vector2(300, 250), Vector2(560, 370), Vector2(820, 230),
	Vector2(860, 500), Vector2(620, 610), Vector2(1040, 370)]
const ENEMY_TINT := Color(0.58, 0.6, 0.66)

var audio
var world: Node2D
var actors: Node2D
var fx_layer: Node2D
var camera: Camera2D
var player
var enemies := []
var remaining := 0
var level_won := false
var paused := false
var _shake := 0.0
var _elapsed := 0.0

var health_bar: ProgressBar
var _hp_fill: StyleBoxFlat
var enemies_label: Label
var message: Label
var pause_label: Label
var victory_panel: PanelContainer
var victory_stats: Label
var music_btn: Button
var sfx_btn: Button


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_setup_input()
	audio = AudioScript.new()
	audio.name = "Audio"
	add_child(audio)
	world = Node2D.new()
	world.name = "World"
	world.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(world)
	_build_ground()
	actors = Node2D.new()
	actors.name = "Actors"
	actors.y_sort_enabled = true
	world.add_child(actors)
	fx_layer = Node2D.new()
	fx_layer.name = "FX"
	fx_layer.z_index = 20
	world.add_child(fx_layer)
	camera = Camera2D.new()
	camera.position = Vector2(640, 360)
	world.add_child(camera)
	camera.make_current()
	_build_bounds()
	for p in COVERS:
		var c = CoverScript.new()
		c.world = self
		c.position = p
		actors.add_child(c)
	player = PlayerScript.new()
	player.world = self
	player.team = "player"
	player.position = SPAWN
	player.aim_angle = -0.6
	actors.add_child(player)
	player.destroyed.connect(_on_player_destroyed)
	player.damaged.connect(_on_player_damaged)
	for p in ENEMY_SPAWNS:
		var e = EnemyScript.new()
		e.world = self
		e.team = "enemy"
		e.tint = ENEMY_TINT
		e.max_health = 75
		e.speed = 70.0
		e.reload_time = 1.8
		e.position = p
		e.aim_angle = PI
		e.target = player
		actors.add_child(e)
		e.destroyed.connect(_on_enemy_destroyed)
		enemies.append(e)
	remaining = enemies.size()
	_build_ui()
	_update_hud()
	audio.music_start()


func _setup_input() -> void:
	_add_keys("move_left", [KEY_A, KEY_LEFT])
	_add_keys("move_right", [KEY_D, KEY_RIGHT])
	_add_keys("move_up", [KEY_W, KEY_UP])
	_add_keys("move_down", [KEY_S, KEY_DOWN])
	_add_keys("fire", [KEY_SPACE])
	if InputMap.action_get_events("fire").size() == 1:
		var mb := InputEventMouseButton.new()
		mb.button_index = MOUSE_BUTTON_LEFT
		InputMap.action_add_event("fire", mb)
	_add_keys("pause", [KEY_ESCAPE, KEY_P])
	_add_keys("mute_music", [KEY_M])
	_add_keys("mute_sfx", [KEY_N])
	_add_keys("restart", [KEY_R])


func _add_keys(action: String, keys: Array) -> void:
	if InputMap.has_action(action):
		return
	InputMap.add_action(action)
	for k in keys:
		var ev := InputEventKey.new()
		ev.physical_keycode = k
		InputMap.action_add_event(action, ev)


func _build_ground() -> void:
	var tr := TextureRect.new()
	tr.texture = load("res://assets/game/env/ground_tile.png")
	tr.stretch_mode = TextureRect.STRETCH_TILE
	tr.position = Vector2(-60, -60)
	tr.size = Vector2(1400, 840)
	tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tr.z_index = -10
	world.add_child(tr)


func _build_bounds() -> void:
	var b := StaticBody2D.new()
	b.collision_layer = 1
	for r in [Rect2(-40, -40, 1360, 70), Rect2(-40, 690, 1360, 70), Rect2(-40, -40, 70, 800), Rect2(1250, -40, 70, 800)]:
		var s := CollisionShape2D.new()
		var rs := RectangleShape2D.new()
		rs.size = r.size
		s.shape = rs
		s.position = r.position + r.size / 2.0
		b.add_child(s)
	world.add_child(b)


func spawn_shell(shooter: Node, pos: Vector2, dir: Vector2) -> void:
	var s = ShellScript.new()
	s.shooter = shooter
	s.world = self
	s.dir = dir
	s.damage = shooter.shell_damage
	s.position = pos
	fx_layer.add_child(s)


## Code-made particle effects (not generated assets): muzzle flash, impact, debris, explosion.
func spawn_fx(kind: String, pos: Vector2) -> void:
	var p := CPUParticles2D.new()
	p.one_shot = true
	p.explosiveness = 1.0
	p.local_coords = false
	p.position = pos
	p.spread = 180.0
	var g := Gradient.new()
	match kind:
		"muzzle":
			p.amount = 12
			p.lifetime = 0.15
			p.initial_velocity_min = 40.0
			p.initial_velocity_max = 110.0
			p.scale_amount_min = 2.0
			p.scale_amount_max = 4.0
			g.set_color(0, Color(1, 0.95, 0.6, 1))
			g.set_color(1, Color(1, 0.4, 0.1, 0))
		"impact":
			p.amount = 8
			p.lifetime = 0.3
			p.initial_velocity_min = 30.0
			p.initial_velocity_max = 70.0
			p.scale_amount_min = 2.0
			p.scale_amount_max = 3.0
			g.set_color(0, Color(1, 0.8, 0.5, 1))
			g.set_color(1, Color(0.4, 0.4, 0.4, 0))
		"debris":
			p.amount = 14
			p.lifetime = 0.6
			p.gravity = Vector2(0, 160)
			p.initial_velocity_min = 40.0
			p.initial_velocity_max = 110.0
			p.scale_amount_min = 2.0
			p.scale_amount_max = 4.0
			g.set_color(0, Color(0.55, 0.38, 0.3, 1))
			g.set_color(1, Color(0.35, 0.28, 0.22, 0))
		_:
			p.amount = 46
			p.lifetime = 0.9
			p.initial_velocity_min = 40.0
			p.initial_velocity_max = 170.0
			p.damping_min = 60.0
			p.damping_max = 120.0
			p.scale_amount_min = 4.0
			p.scale_amount_max = 9.0
			g.set_color(0, Color(1, 0.75, 0.25, 1))
			g.add_point(0.35, Color(0.9, 0.3, 0.05, 0.9))
			g.set_color(g.get_point_count() - 1, Color(0.15, 0.15, 0.15, 0))
	p.color_ramp = g
	p.emitting = true
	fx_layer.add_child(p)
	get_tree().create_timer(p.lifetime + 0.5).timeout.connect(p.queue_free)


func shake(amount: float) -> void:
	_shake = maxf(_shake, amount)


func _process(delta: float) -> void:
	if not paused and not level_won:
		_elapsed += delta
	if _shake > 0.05:
		camera.offset = Vector2(randf_range(-1, 1), randf_range(-1, 1)) * _shake
		_shake = maxf(0.0, _shake - delta * 18.0)
	else:
		camera.offset = Vector2.ZERO


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause") and not level_won:
		_set_paused(not paused)
	elif event.is_action_pressed("mute_music"):
		_toggle_bus("Music")
	elif event.is_action_pressed("mute_sfx"):
		_toggle_bus("SFX")
	elif event.is_action_pressed("restart") and level_won:
		get_tree().paused = false
		get_tree().reload_current_scene()


func _set_paused(p: bool) -> void:
	paused = p
	get_tree().paused = p
	audio.music_set_paused(p)
	pause_label.visible = p


func _toggle_bus(bus_name: String) -> void:
	audio.set_bus_muted(bus_name, not audio.is_bus_muted(bus_name))
	_update_hud()


func _on_player_damaged(_tank, _amount) -> void:
	_update_hud()


func _on_player_destroyed(_tank) -> void:
	audio.music_stop()  # failure: the music cuts, only the explosion tail remains
	message.text = "YunqiZ destroyed - respawning"
	message.visible = true
	_update_hud()
	await get_tree().create_timer(2.0).timeout
	if level_won or not player.is_dead:
		return
	player.reset_full(SPAWN)
	message.visible = false
	audio.music_start()  # respawn: the music restarts from the beginning
	_update_hud()


## level_won is checked and set before the victory sound, so the sound can only play once.
func _on_enemy_destroyed(_tank) -> void:
	remaining = maxi(0, remaining - 1)
	_update_hud()
	if remaining == 0 and not level_won:
		level_won = true
		player.controls_enabled = false
		audio.music_stop()
		audio.play("victory")
		_show_victory()


func _build_ui() -> void:
	var ui := CanvasLayer.new()
	ui.layer = 10
	ui.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(ui)
	var top := HBoxContainer.new()
	top.position = Vector2(16, 12)
	top.add_theme_constant_override("separation", 10)
	ui.add_child(top)
	var name_label := Label.new()
	name_label.text = "YunqiZ"
	top.add_child(name_label)
	health_bar = ProgressBar.new()
	health_bar.custom_minimum_size = Vector2(200, 20)
	health_bar.max_value = player.max_health
	health_bar.show_percentage = false
	# Playtest revision: the default grey fill was hard to read on the dark ground.
	_hp_fill = StyleBoxFlat.new()
	health_bar.add_theme_stylebox_override("fill", _hp_fill)
	var hp_bg := StyleBoxFlat.new()
	hp_bg.bg_color = Color(0, 0, 0, 0.6)
	health_bar.add_theme_stylebox_override("background", hp_bg)
	top.add_child(health_bar)
	enemies_label = Label.new()
	top.add_child(enemies_label)
	var right := HBoxContainer.new()
	right.position = Vector2(960, 10)
	right.add_theme_constant_override("separation", 8)
	ui.add_child(right)
	music_btn = Button.new()
	music_btn.focus_mode = Control.FOCUS_NONE
	music_btn.pressed.connect(_toggle_bus.bind("Music"))
	right.add_child(music_btn)
	sfx_btn = Button.new()
	sfx_btn.focus_mode = Control.FOCUS_NONE
	sfx_btn.pressed.connect(_toggle_bus.bind("SFX"))
	right.add_child(sfx_btn)
	var hint := Label.new()
	hint.text = "WASD move   mouse aim   LMB / Space fire   Esc pause   M music   N sound"
	hint.position = Vector2(16, 690)
	hint.modulate = Color(1, 1, 1, 0.7)
	ui.add_child(hint)
	message = _center_label(ui, 28)
	message.visible = false
	pause_label = _center_label(ui, 36)
	pause_label.text = "PAUSED  (Esc / P to resume)"
	pause_label.visible = false
	victory_panel = PanelContainer.new()
	victory_panel.position = Vector2(440, 190)
	victory_panel.custom_minimum_size = Vector2(400, 320)
	victory_panel.visible = false
	ui.add_child(victory_panel)
	var vb := VBoxContainer.new()
	vb.alignment = BoxContainer.ALIGNMENT_CENTER
	vb.add_theme_constant_override("separation", 12)
	victory_panel.add_child(vb)
	var title := Label.new()
	title.text = "VICTORY"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 44)
	vb.add_child(title)
	var pic := Control.new()
	pic.custom_minimum_size = Vector2(177, 150)
	pic.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(pic)
	var h := TextureRect.new()
	h.texture = load("res://assets/game/yunqiz/hull_right.png")
	h.position = Vector2(0, -6)
	pic.add_child(h)
	var t := TextureRect.new()
	t.texture = load("res://assets/game/yunqiz/turret_right.png")
	t.position = Vector2(0, -6 - 21.7)
	pic.add_child(t)
	victory_stats = Label.new()
	victory_stats.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(victory_stats)


func _center_label(parent: Node, font_size: int) -> Label:
	var l := Label.new()
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.position = Vector2(0, 320)
	l.size = Vector2(1280, 60)
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0))
	l.add_theme_constant_override("outline_size", 6)
	parent.add_child(l)
	return l


func _update_hud() -> void:
	if health_bar == null:
		return
	health_bar.value = player.health
	var r := float(player.health) / float(player.max_health)
	_hp_fill.bg_color = Color(0.3, 0.8, 0.3) if r > 0.6 else (Color(0.95, 0.75, 0.2) if r > 0.3 else Color(0.9, 0.25, 0.2))
	enemies_label.text = "Enemy tanks left: %d" % remaining
	music_btn.text = "Music: %s (M)" % ("OFF" if audio.is_bus_muted("Music") else "ON")
	sfx_btn.text = "Sound: %s (N)" % ("OFF" if audio.is_bus_muted("SFX") else "ON")


func _show_victory() -> void:
	var secs := int(_elapsed)
	victory_stats.text = "Enemy tanks destroyed: %d / %d\nTime: %d:%02d\n\nPress R to play again" % [enemies.size(), enemies.size(), secs / 60, secs % 60]
	victory_panel.visible = true
