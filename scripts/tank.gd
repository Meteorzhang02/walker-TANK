extends CharacterBody2D
## Base tank (YunqiZ and the enemy tanks): hull that faces the movement direction, turret that
## faces the aim, 8 facings from 5 generated directions (3 mirrored), health with visible damage
## states, reload, recoil and destruction.

signal fired(tank)
signal damaged(tank, amount)
signal destroyed(tank)

const SIN_E := 0.8192            # sin(55 deg): vertical squash of the oblique view
const TURRET_OFFSET := Vector2(0.0, -10.85)  # turret pivot above the hull origin, display px
const BARREL_LEN := 40.4         # barrel tip distance from the pivot (0.78 units), display px
const RADIUS := 16.6             # collision circle: half the hull width
# Facing slots clockwise from screen-right (y points down): texture name and mirror flag.
const SLOT_TEX := ["right", "down_right", "down", "down_right", "right", "up_right", "up", "up_right"]
const SLOT_FLIP := [false, false, false, true, true, true, false, false]

@export var team := "player"
@export var max_health := 100
@export var speed := 110.0
@export var reload_time := 0.8
@export var shell_damage := 25
@export var tint := Color(1, 1, 1)

var world = null
var health := 100
var is_dead := false
var reload_left := 0.0
var invuln_left := 0.0
var aim_angle := 0.0
var move_dir := Vector2.ZERO
var recoil := 0.0
var hull: Sprite2D
var turret: Sprite2D
var smoke: CPUParticles2D
var flames: CPUParticles2D
var _t := 0.0
var _hull_tex := {}
var _turret_tex := {}


func _ready() -> void:
	health = max_health
	collision_layer = 2
	collision_mask = 1 | 2
	var shape := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = RADIUS
	shape.shape = circle
	add_child(shape)
	for d in ["right", "down_right", "down", "up", "up_right"]:
		_hull_tex[d] = load("res://assets/game/yunqiz/hull_%s.png" % d)
		_turret_tex[d] = load("res://assets/game/yunqiz/turret_%s.png" % d)
	hull = Sprite2D.new()
	hull.scale = Vector2(0.5, 0.5)
	add_child(hull)
	turret = Sprite2D.new()
	turret.scale = Vector2(0.5, 0.5)
	turret.position = TURRET_OFFSET
	add_child(turret)
	smoke = _make_trail(Color(0.42, 0.42, 0.42, 0.75), Color(0.2, 0.2, 0.2, 0.0), 16, 1.6, -40.0)
	flames = _make_trail(Color(1.0, 0.6, 0.15, 0.95), Color(0.7, 0.1, 0.0, 0.0), 20, 0.5, -70.0)
	modulate = tint
	_set_sprite(hull, _hull_tex, _slot_for(Vector2.RIGHT.rotated(aim_angle)))
	_set_sprite(turret, _turret_tex, _slot_for(Vector2.RIGHT.rotated(aim_angle)))


func _make_trail(c0: Color, c1: Color, amount: int, life: float, rise: float) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.amount = amount
	p.lifetime = life
	p.emitting = false
	p.local_coords = false
	p.position = TURRET_OFFSET
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_SPHERE
	p.emission_sphere_radius = 6.0
	p.direction = Vector2(0, -1)
	p.spread = 25.0
	p.gravity = Vector2(0, rise)
	p.initial_velocity_min = 5.0
	p.initial_velocity_max = 15.0
	p.scale_amount_min = 3.0
	p.scale_amount_max = 6.0
	var g := Gradient.new()
	g.set_color(0, c0)
	g.set_color(1, c1)
	p.color_ramp = g
	add_child(p)
	return p


func _slot_for(screen_vec: Vector2) -> int:
	var ground := Vector2(screen_vec.x, screen_vec.y / SIN_E)
	var a := fposmod(ground.angle(), TAU)
	return int(round(a / (PI / 4.0))) % 8


func _set_sprite(s: Sprite2D, tex: Dictionary, slot: int) -> void:
	s.texture = tex[SLOT_TEX[slot]]
	s.flip_h = SLOT_FLIP[slot]


func aim_vec() -> Vector2:
	return Vector2.RIGHT.rotated(aim_angle)


## Muzzle point on the ground plane (shells travel on the ground plane; they are drawn raised).
func muzzle_position() -> Vector2:
	var v := aim_vec()
	var ground := Vector2(v.x, v.y / SIN_E).normalized()
	return global_position + Vector2(ground.x, ground.y * SIN_E) * BARREL_LEN


func _physics_process(delta: float) -> void:
	_t += delta
	reload_left = maxf(0.0, reload_left - delta)
	invuln_left = maxf(0.0, invuln_left - delta)
	if is_dead:
		return
	_think(delta)
	velocity = move_dir * speed
	move_and_slide()
	if move_dir != Vector2.ZERO:
		_set_sprite(hull, _hull_tex, _slot_for(move_dir))
	_set_sprite(turret, _turret_tex, _slot_for(aim_vec()))
	recoil = maxf(0.0, recoil - delta * 20.0)
	# Moving state: track rumble. Idle state: slight engine shake.
	var wobble := Vector2(0, sin(_t * 30.0) * 0.6) if move_dir != Vector2.ZERO else Vector2(0, sin(_t * 12.0) * 0.2)
	var kick := -aim_vec() * recoil
	hull.position = wobble + kick
	turret.position = TURRET_OFFSET + wobble + kick


## Overridden by the player (input) and the enemies (AI).
func _think(_delta: float) -> void:
	pass


## Fires if the reload timer allows it. The reload check is what stops double triggers:
## no shell and no sound while reloading.
func try_fire() -> bool:
	if is_dead or reload_left > 0.0 or world == null:
		return false
	reload_left = reload_time
	recoil = 3.0
	var pos := muzzle_position()
	world.spawn_shell(self, pos, aim_vec())
	world.spawn_fx("muzzle", pos + TURRET_OFFSET)
	_play_fire_sound()
	fired.emit(self)
	return true


func _play_fire_sound() -> void:
	world.audio.play("fire")


func _play_hit_sound() -> void:
	world.audio.play("player_hit")


## A short invulnerability window ignores repeat hits; the fatal hit plays the explosion only.
func take_damage(amount: int, _from: Node = null) -> void:
	if is_dead or invuln_left > 0.0:
		return
	invuln_left = 0.3
	health = maxi(0, health - amount)
	if health <= 0:
		die()
		return
	_flash()
	if world:
		_play_hit_sound()
	_update_damage_look()
	damaged.emit(self, amount)


## is_dead is set before anything else, so die() can only run once.
func die() -> void:
	if is_dead:
		return
	is_dead = true
	health = 0
	velocity = Vector2.ZERO
	modulate = Color(0.32, 0.3, 0.28)
	flames.emitting = false
	smoke.emitting = true
	if world:
		world.spawn_fx("explosion", global_position + TURRET_OFFSET)
		world.shake(6.0)
		world.audio.play("explode")
	destroyed.emit(self)


func _update_damage_look() -> void:
	var r := float(health) / float(max_health)
	smoke.emitting = r <= 0.6
	flames.emitting = r <= 0.3


func _flash() -> void:
	modulate = Color(2.2, 2.2, 2.2)
	create_tween().tween_property(self, "modulate", tint, 0.15)


func reset_full(pos: Vector2) -> void:
	global_position = pos
	health = max_health
	is_dead = false
	reload_left = 0.0
	invuln_left = 1.0
	modulate = tint
	smoke.emitting = false
	flames.emitting = false
