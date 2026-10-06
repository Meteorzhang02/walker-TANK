extends StaticBody2D
## Destructible brick cover: intact -> cracked after 2 hits -> broken after 4 hits.
## Broken cover is low rubble: it no longer blocks tanks or shells.

const HITS_TO_CRACK := 2
const HITS_TO_BREAK := 4

var world = null
var hits := 0
var stage := 0
var sprite: Sprite2D
var shape: CollisionShape2D
var _tex := []


func _ready() -> void:
	collision_layer = 1
	collision_mask = 0
	for n in ["intact", "cracked", "broken"]:
		_tex.append(load("res://assets/game/env/cover_%s.png" % n))
	sprite = Sprite2D.new()
	sprite.scale = Vector2(0.5, 0.5)
	sprite.position = Vector2(0, -6.2)  # the wall's ground centre sits 72 px below the source image centre
	sprite.texture = _tex[0]
	add_child(sprite)
	shape = CollisionShape2D.new()
	var r := RectangleShape2D.new()
	r.size = Vector2(72.6, 22.0)
	shape.shape = r
	add_child(shape)


func take_hit(_shell: Node = null) -> void:
	if stage >= 2:
		return
	hits += 1
	var new_stage := 2 if hits >= HITS_TO_BREAK else (1 if hits >= HITS_TO_CRACK else 0)
	if world:
		world.audio.play("cover_hit")
		world.spawn_fx("debris", global_position + Vector2(0, -8))
	if new_stage != stage:
		stage = new_stage
		sprite.texture = _tex[stage]
		if stage == 2:
			shape.set_deferred("disabled", true)
