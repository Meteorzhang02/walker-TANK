extends Node
## Plays every sound and the music loop. Sounds only report game events: game state is always
## changed first by the caller, so a muted or missing sound never changes what happens.
## `counts` records how many times each event asked for a sound (used by the automated test).

const SFX := {
	"fire": "res://assets/audio/sfx/SFX-fire.wav",
	"cover_hit": "res://assets/audio/sfx/SFX-cover-hit.wav",
	"player_hit": "res://assets/audio/sfx/SFX-player-hit.wav",
	"explode": "res://assets/audio/sfx/SFX-explode.wav",
	"victory": "res://assets/audio/sfx/SFX-victory.wav",
}
const MUSIC := "res://assets/audio/music/MUS-battle-loop.ogg"

var counts := {}
var music: AudioStreamPlayer
var _players := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_bus("Music")
	_ensure_bus("SFX")
	for key in SFX:
		var p := AudioStreamPlayer.new()
		p.stream = load(SFX[key])
		p.bus = "SFX"
		p.max_polyphony = 4
		add_child(p)
		_players[key] = p
	music = AudioStreamPlayer.new()
	var s = load(MUSIC)
	if s is AudioStreamOggVorbis:
		s.loop = true
	music.stream = s
	music.bus = "Music"
	music.volume_db = -4.0
	add_child(music)


func _ensure_bus(bus_name: String) -> void:
	if AudioServer.get_bus_index(bus_name) == -1:
		AudioServer.add_bus()
		var i := AudioServer.bus_count - 1
		AudioServer.set_bus_name(i, bus_name)
		AudioServer.set_bus_send(i, "Master")


func play(key: String, volume_db: float = 0.0, pitch: float = 1.0, count_key: String = "") -> void:
	var ck := count_key if count_key != "" else key
	counts[ck] = int(counts.get(ck, 0)) + 1
	var p: AudioStreamPlayer = _players[key]
	p.volume_db = volume_db
	p.pitch_scale = pitch
	p.play()


func count(key: String) -> int:
	return int(counts.get(key, 0))


func music_start() -> void:
	music.stream_paused = false
	music.play(0.0)


func music_stop() -> void:
	music.stop()


func music_set_paused(p: bool) -> void:
	music.stream_paused = p


func set_bus_muted(bus_name: String, muted: bool) -> void:
	AudioServer.set_bus_mute(AudioServer.get_bus_index(bus_name), muted)


func is_bus_muted(bus_name: String) -> bool:
	return AudioServer.is_bus_mute(AudioServer.get_bus_index(bus_name))
