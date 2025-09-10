#version 460 core

layout (location = 0) out vec4 FS_out_color;

in vec3 FS_in_world_pos;

void main()
{
    FS_out_color = vec4(1.f, 0.f, 0.f, 1.f); //
}
