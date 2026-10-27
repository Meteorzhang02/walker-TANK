shader_type spatial;
render_mode unshaded;

uniform sampler2D tex_srgb : source_color, filter_nearest;
uniform sampler2D tex_raw : filter_nearest;
uniform bool use_srgb = true;

void fragment() {
	if (use_srgb) {
		ALBEDO = texture(tex_srgb, UV).rgb;
	} else {
		ALBEDO = texture(tex_raw, UV).rgb;
	}
}