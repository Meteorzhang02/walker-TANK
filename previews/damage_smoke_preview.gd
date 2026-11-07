extends Node2D
## Frame-strip fixture for Effect B (CHANGE-BRIEF.md, Effect B "The frame strip"). Preview only:
## changes no game script. A standing YunqiZ drawn as tank.gd draws it (hull and turret sprites at
## scale 0.5, turret at TURRET_OFFSET, facing up_right as at the game's spawn, aim_angle -0.6) on
## the real ground tile, beside one real cover block (scripts/cover.gd, world = null, never hit).
## Camera at (640, 360), zoom 1. The smoke sits at TURRET_OFFSET, as tank.gd will place it, and is
## driven only through its follow(), the same mapping the tank will call.
## Frame numbers are Engine.get_frames_drawn(), which equals the Movie Maker frame number.

## [frame, health_ratio]: condition starts, heavier damage, condition ends (as on respawn).
const STEPS := [[10, 0.5], [60, 0.1], [110, 1.0]]

## Fixed seed for this preview's instance only; the effect scene never sets one.
@export var fixed_seed := 7

@onready var smoke: GPUParticles2D = $YunqiZ/Smoke

var _done := {}


func _ready() -> void:
	smoke.use_fixed_seed = true
	smoke.seed = fixed_seed


func _process(_delta: float) -> void:
	var f := Engine.get_frames_drawn()
	for step in STEPS:
		if f >= step[0] and not _done.has(step[0]):
			_done[step[0]] = true
			smoke.follow(step[1], false)
			print("preview: frame %d, h %.2f -> emitting %s, amount_ratio %.4f, amount %d" % [f, step[1], smoke.emitting, smoke.amount_ratio, smoke.amount])
