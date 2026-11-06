extends Node2D
## Effect A root (CHANGE-BRIEF.md, Effect A): frees the burst when Dust, the longest emitter, finishes.
## Sets no particle settings; those live in effects/cover_hit_burst.tscn.


func _ready() -> void:
	$Dust.finished.connect(queue_free)
