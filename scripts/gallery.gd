extends Node2D
## Test gallery for TEST-REPORT.md: YunqiZ in all 8 facings, its states, the enemy tint and the
## collision circle, drawn in-engine at 2x game size. Open scenes/gallery.tscn and press F6.

const TankScript := preload("res://scripts/tank.gd")  # base tank: no mouse aim, so each turret keeps its own facing
const EnemyScript := preload("res://scripts/enemy.gd")
const NAMES := ["right", "down-right", "down", "down-left\n(mirrored)", "left\n(mirrored)", "up-left\n(mirrored)", "up", "up-right"]
const SIN_E := 0.8192

func _ready() -> void:
	scale = Vector2(2, 2)
	var bg := ColorRect.new()
	bg.color = Color(0.29, 0.24, 0.2)
	bg.position = Vector2(-20, -20)
	bg.size = Vector2(700, 400)
	bg.z_index = -10
	add_child(bg)
	for i in 8:
		var g := i * PI / 4.0
		var t = _tank(TankScript, Vector2(40 + i * 75, 55), Vector2(cos(g), sin(g) * SIN_E).angle())
		t._set_sprite(t.hull, t._hull_tex, i)
		_label(NAMES[i], Vector2(10 + i * 75, 85))
	var states := ["idle", "smoke\n(<=60% health)", "fire\n(<=30% health)", "destroyed", "enemy tint"]
	for i in states.size():
		var pos := Vector2(40 + i * 110, 175)
		var t
		if i == 4:
			t = _tank(EnemyScript, pos, 0.0)
		else:
			t = _tank(TankScript, pos, -0.5)
		if i == 1:
			t.health = 55
			t._update_damage_look()
		elif i == 2:
			t.health = 20
			t._update_damage_look()
		elif i == 3:
			t.die()
		_label(states[i], Vector2(5 + i * 110, 205))
	_label("Green circles = collision shape (radius 16.6 px at game size). Shown at 2x.", Vector2(10, 260))


func _tank(script, pos: Vector2, aim: float):
	var t = script.new()
	t.position = pos
	t.aim_angle = aim
	if script == EnemyScript:
		t.tint = Color(0.58, 0.6, 0.66)
	add_child(t)
	var ring := Line2D.new()
	ring.width = 1.0
	ring.default_color = Color(0.2, 1.0, 0.4, 0.9)
	ring.z_index = 5
	for k in 33:
		ring.add_point(pos + Vector2.RIGHT.rotated(k * TAU / 32.0) * 16.6)
	add_child(ring)
	return t


func _label(text: String, pos: Vector2) -> void:
	var l := Label.new()
	l.text = text
	l.position = pos
	l.scale = Vector2(0.5, 0.5)
	l.add_theme_font_size_override("font_size", 18)
	add_child(l)

