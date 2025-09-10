#version 460 core

layout (location = 0) in vec3 VS_in_world_pos;

out vec3 FS_in_world_pos;

uniform mat4 u_pv;

void main()
{
	vec3 position = VS_in_world_pos;
	gl_Position = u_pv * vec4(position, 1.f);
	FS_in_world_pos = position;
}
