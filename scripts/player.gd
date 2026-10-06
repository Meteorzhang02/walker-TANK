extends "res://scripts/tank.gd"
## YunqiZ: WASD / arrows to move, mouse to aim, left mouse button or Space to fire.

var controls_enabled := true


func _think(_delta: float) -> void:
	if not controls_enabled:
		move_dir = Vector2.ZERO
		return
	move_dir = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	aim_angle = (get_global_mouse_position() - (global_position + TURRET_OFFSET)).angle()
	if Input.is_action_pressed("fire"):
		try_fire()
