shader_type spatial;

group_uniforms colour;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 albedo_tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float brightness : hint_range(0.0, 2.0) = 1.0;

group_uniforms surface;
uniform sampler2D roughness_tex : filter_linear_mipmap, repeat_enable;
uniform float roughness_scale : hint_range(0.0, 1.0) = 1.0;
uniform float uv_scale : hint_range(0.1, 4.0) = 0.5;
group_uniforms;

varying vec3 obj_pos;
varying vec3 obj_normal;

void vertex() {
	obj_pos = VERTEX;
	obj_normal = NORMAL;
}

void fragment() {
	vec3 n = abs(obj_normal);
	vec2 uv;
	if (n.x > n.y && n.x > n.z) {
		uv = vec2(obj_pos.z, -obj_pos.y);
	} else if (n.y > n.z) {
		uv = obj_pos.xz;
	} else {
		uv = vec2(obj_pos.x, -obj_pos.y);
	}
	uv *= uv_scale;
	ALBEDO = texture(albedo_tex, uv).rgb * albedo_tint.rgb * brightness;
	ROUGHNESS = texture(roughness_tex, uv).r * roughness_scale;
}