extends Node
## A5 hit flash driver: gives YunqiZ's hull and turret one shared ShaderMaterial
## (res://shaders/hit_flash.gdshader) and drives hit_amount from the tank's signals.
## Presentation only: it listens to damaged / destroyed and never writes game state.
##   damaged   -> hit_amount = 1.0, then a linear fade to 0.0 over DURATION of scaled time
##   damaged during the fade -> restarts at 1.0
##   destroyed -> 0.0 at once (and it stays 0.0 through reset_full(): a dead tank takes no hits)
## It is a child of the tank, so it inherits the World's PROCESS_MODE_PAUSABLE and holds
## its value while the tree is paused.

const SHADER_PATH := "res://shaders/hit_flash.gdshader"
const PARAM := "hit_amount"
const SET_PARAMS := [PARAM]  # every uniform this driver writes (checked against the shader)
const DURATION := 0.5

var tank = null
var material: ShaderMaterial
var _age := 0.0
var _active := false


## Creates the driver under `t` and wires it up. Call after `t` is in the tree (hull exists).
func attach(t) -> Node:
	tank = t
	name = "HitFlashDriver"
	var shader := load(SHADER_PATH) as Shader
	if shader == null:
		push_error("hit_flash_driver: cannot load %s" % SHADER_PATH)
	else:
		var declared := shader.get_shader_uniform_list().map(func(u): return u.name)
		for p in SET_PARAMS:
			if not declared.has(p):
				push_error("hit_flash_driver: %s does not declare uniform '%s'" % [SHADER_PATH, p])
		material = ShaderMaterial.new()
		material.shader = shader
		material.set_shader_parameter(PARAM, 0.0)
		t.hull.material = material
		t.turret.material = material
	t.damaged.connect(_on_damaged)
	t.destroyed.connect(_on_destroyed)
	t.add_child(self)
	return self


func _on_damaged(_tank, _amount) -> void:
	_age = 0.0
	_active = true
	_set_amount(1.0)


func _on_destroyed(_tank) -> void:
	_active = false
	_set_amount(0.0)


## Show the value for the current age, then advance: the frame of the hit draws 1.0.
func _process(delta: float) -> void:
	if not _active:
		return
	var v := 1.0 - _age / DURATION
	if v <= 1e-6:
		v = 0.0
		_active = false
	_set_amount(v)
	_age += delta


func _set_amount(v: float) -> void:
	if material:
		material.set_shader_parameter(PARAM, v)
