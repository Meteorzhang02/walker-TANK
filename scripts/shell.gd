extends Area2D
## A shell travels on the ground plane and is drawn raised to turret height.
## has_hit is set on the first contact and the shell is freed, so one shell = one hit = one sound.

const DRAW_OFFSET := Vector2(0.0, -10.85)

var shooter = null
var world = null
var dir := Vector2.RIGHT
var speed := 460.0
var damage := 25
var has_hit := false
var _life := 2.0


func _ready() -> void:
	collision_layer = 0
	collision_mask = 1 | 2
	var s := CollisionShape2D.new()
	var c := CircleShape2D.new()
	c.radius = 3.0
	s.shape = c
	add_child(s)
	body_entered.connect(_on_body_entered)


func _physics_process(delta: float) -> void:
	position += dir * speed * delta
	_life -= delta
	if _life <= 0.0:
		queue_free()


func _draw() -> void:
	draw_line(DRAW_OFFSET - dir * 9.0, DRAW_OFFSET, Color(1, 0.8, 0.4, 0.6), 2.0)
	draw_circle(DRAW_OFFSET, 2.5, Color(1, 0.92, 0.6))


func _on_body_entered(body) -> void:
	if has_hit or body == shooter:
		return
	if shooter != null and "team" in body and "team" in shooter and body.team == shooter.team:
		return  # no friendly fire; the shell keeps flying
	has_hit = true
	if body.has_method("take_hit"):
		body.take_hit(self)
	elif body.has_method("take_damage"):
		body.take_damage(damage, shooter)
	if world:
		world.spawn_fx("impact", global_position + DRAW_OFFSET)
	queue_free()
