extends "res://scripts/tank.gd"
## Enemy tank: wanders between random waypoints, turns its turret toward YunqiZ and fires when it
## has a clear line of sight. Uses the YunqiZ sprites tinted grey (code, not a separate asset).

var target = null
var arena := Rect2(90, 90, 1100, 540)
var _wp := Vector2.ZERO
var _wp_left := 0.0
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	super._ready()
	_rng.randomize()
	reload_left = _rng.randf_range(1.5, 3.0)


func _think(delta: float) -> void:
	if target == null or target.is_dead or world == null or world.level_won:
		move_dir = Vector2.ZERO
		return
	_wp_left -= delta
	if _wp_left <= 0.0 or global_position.distance_to(_wp) < 12.0:
		_wp = Vector2(_rng.randf_range(arena.position.x, arena.end.x), _rng.randf_range(arena.position.y, arena.end.y))
		_wp_left = _rng.randf_range(2.0, 4.0)
	var to_wp := _wp - global_position
	move_dir = to_wp.normalized() if to_wp.length() > 12.0 else Vector2.ZERO
	var to_target: Vector2 = target.global_position - global_position
	aim_angle = lerp_angle(aim_angle, to_target.angle(), clampf(delta * 3.0, 0.0, 1.0))
	var off := absf(wrapf(aim_angle - to_target.angle(), -PI, PI))
	if reload_left <= 0.0 and to_target.length() < 700.0 and off < 0.15 and _has_line_of_sight():
		if try_fire():
			reload_left = reload_time + _rng.randf_range(0.0, 1.0)


func _has_line_of_sight() -> bool:
	var q := PhysicsRayQueryParameters2D.create(global_position, target.global_position, 1 | 2, [get_rid()])
	var hit := get_world_2d().direct_space_state.intersect_ray(q)
	return not hit.is_empty() and hit.collider == target


func _play_fire_sound() -> void:
	world.audio.play("fire", -6.0, 0.85, "enemy_fire")


func _play_hit_sound() -> void:
	world.audio.play("player_hit", -8.0, 0.8, "enemy_hit")
