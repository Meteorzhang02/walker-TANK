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

enum Motion { IDLE, MOVING }
enum Weapon { READY, FIRING }
# Phase table of the `shoot` clip (brief): 30 fps, shell on frame 1, weapon READY again at frame 5.
const SHOOT_FPS := 30.0
const SHOOT_ACTIVE_FRAME := 1
const SHOOT_END_FRAME := 5
const DUST_BEHIND := 34.0        # display px behind the tank; a guess, human check

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
var smoke: GPUParticles2D
var flames: CPUParticles2D
var _t := 0.0
# A7 state machine. Only tank.gd writes these three.
var _motion := Motion.IDLE
var _weapon := Weapon.READY
var _fire_ticks := 0             # physics ticks since the press tick (press tick = 0)
var _shot_pos := Vector2.ZERO    # muzzle position captured on the press tick
var _shot_dir := Vector2.ZERO    # aim captured on the press tick
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
	# A7 clip nodes. DustMount is added before Suspension, so it draws under the hull by tree
	# order (same z_index, earlier sibling first). z_index -1 is avoided: it could sink the dust
	# below the arena ground, which draws at z 0.
	var dust_mount := Node2D.new()
	dust_mount.name = "DustMount"
	dust_mount.visible = false
	add_child(dust_mount)
	var dust := Sprite2D.new()
	dust.name = "Dust"
	dust.texture = load("res://assets/game/fx/track_dust_sheet.png")
	dust.hframes = 4
	dust.vframes = 1
	dust.frame = 0
	dust.scale = Vector2(2, 2)   # TUNING revision 1: set once, not animated
	dust_mount.add_child(dust)
	var suspension := Node2D.new()
	suspension.name = "Suspension"
	add_child(suspension)
	hull = Sprite2D.new()
	hull.scale = Vector2(0.5, 0.5)
	suspension.add_child(hull)
	turret = Sprite2D.new()
	turret.scale = Vector2(0.5, 0.5)
	turret.position = TURRET_OFFSET
	suspension.add_child(turret)
	var motion_anim := AnimationPlayer.new()
	motion_anim.name = "MotionAnim"
	motion_anim.root_node = NodePath("..")
	motion_anim.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS
	motion_anim.add_animation_library("", load("res://animations/motion_clips.tres"))
	add_child(motion_anim)
	var fire_anim := AnimationPlayer.new()
	fire_anim.name = "FireAnim"
	fire_anim.root_node = NodePath("..")
	fire_anim.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_PHYSICS
	fire_anim.add_animation_library("", load("res://animations/fire_clips.tres"))
	add_child(fire_anim)
	smoke = preload("res://effects/damage_smoke.tscn").instantiate()
	smoke.position = TURRET_OFFSET
	add_child(smoke)
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
	# Runs before the death return: a shot already committed finishes after death.
	_weapon_tick()
	if is_dead:
		_update_motion()
		return
	_think(delta)
	_update_motion()
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


func _ticks_for_frame(frame: int) -> int:
	return int(round(frame * Engine.physics_ticks_per_second / SHOOT_FPS))


## Motion machine: IDLE <-> MOVING. Starts and stops MotionAnim; owns DustMount position/visible.
func _update_motion() -> void:
	var moving := not is_dead and move_dir != Vector2.ZERO
	var mount: Node2D = get_node("DustMount")
	if moving:
		var behind := -move_dir.normalized() * DUST_BEHIND
		mount.position = Vector2(behind.x, behind.y * SIN_E)
	if moving and _motion == Motion.IDLE:
		_motion = Motion.MOVING
		mount.visible = true
		get_node("MotionAnim").play("track_dust")
	elif not moving and _motion == Motion.MOVING:
		_motion = Motion.IDLE
		mount.visible = false
		get_node("MotionAnim").stop()


## Weapon machine: FIRING -> READY. The shell, muzzle FX and fire sound come out on the active
## tick (frame 1), read from a tick counter and not from the clip.
func _weapon_tick() -> void:
	if _weapon != Weapon.FIRING:
		return
	_fire_ticks += 1
	if _fire_ticks == _ticks_for_frame(SHOOT_ACTIVE_FRAME) and world != null:
		var pos := _shot_pos
		world.spawn_shell(self, pos, _shot_dir)
		world.spawn_fx("muzzle", pos + TURRET_OFFSET)
		_play_fire_sound()
		fired.emit(self)
	if _fire_ticks >= _ticks_for_frame(SHOOT_END_FRAME):
		_weapon = Weapon.READY


## Overridden by the player (input) and the enemies (AI).
func _think(_delta: float) -> void:
	pass


## Fires if the reload timer allows it. The reload check is what stops double triggers:
## no shell and no sound while reloading.
func try_fire() -> bool:
	if is_dead or _weapon == Weapon.FIRING or reload_left > 0.0 or world == null:
		return false
	reload_left = reload_time
	recoil = 3.0
	_weapon = Weapon.FIRING
	_fire_ticks = 0
	_shot_pos = muzzle_position()
	_shot_dir = aim_vec()
	get_node("FireAnim").play("shoot")
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
	smoke.follow(0.0, true)
	if world:
		world.spawn_fx("explosion", global_position + TURRET_OFFSET)
		world.shake(6.0)
		world.audio.play("explode")
	destroyed.emit(self)


func _update_damage_look() -> void:
	var r := float(health) / float(max_health)
	smoke.follow(r, is_dead)
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
