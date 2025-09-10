import numpy as np
import OpenGL.GL as GL
import random
from ogle import Ogle

import sys
import time
from pathlib import Path
from debug import Debug

sys.path.append(str(Path(__file__).parent.parent / 'common/'))

from shader import Shader
from texture2d import Texture2D

class OceanFFT():

    PI=np.pi
    def __init__(self):
        self.GRID_DIM=1024
        self.RESOLUTION=512
        self.WORK_GROUP_DIM=32
        self.width = 1280
        self.height = 720
        self.window_title = "OceanFFT | Ogle"
        self.enable_debug_callback = True
        self.enable_cursor = False
        self.changed = True

        self.ocean_size = 1024
        self.wind_magnitude = 24.142135
        self.wind_angle = 45
        self.choppiness = 5.5
        self.sun_elevation = 0
        self.sun_azimuth = 90
        self.wireframe_mode = False
        self.is_ping_phase = True

        self.delta_time = 0
        self.cam_pos = [0, 60, 0]
        self.cam_pos = [295.627, 252, 77.7584]
        

    def Initialize(self):
        # Generate grid
        vertex_count = self.GRID_DIM + 1
        
        vertices = np.zeros((vertex_count * vertex_count, 5), dtype=np.float32)
        indices = np.zeros((self.GRID_DIM * self.GRID_DIM * 2 * 3), dtype=np.uint32)
        
        tex_coord_scale = 2.0
        
        idx = 0
        scale = 1
        for z in range(int(-self.GRID_DIM / 2), int(self.GRID_DIM / 2+1), 1):
            for x in range(int(-self.GRID_DIM / 2), int(self.GRID_DIM / 2+1), 1):
                vertices[idx][0] = x * scale
                vertices[idx][1] = 0
                vertices[idx][2] = z * scale
                u = x / self.GRID_DIM + 0.5
                v = z / self.GRID_DIM + 0.5
                vertices[idx][3] = u * tex_coord_scale
                vertices[idx][4] = v * tex_coord_scale
                idx += 1

        #print("vertices", len(vertices), vertices)
        
        # Clockwise winding
        idx = 0
        for y in range(self.GRID_DIM):
            for x in range(self.GRID_DIM):
                indices[idx + 0] = (vertex_count * y) + x
                indices[idx + 1] = (vertex_count * (y + 1)) + x
                indices[idx + 2] = (vertex_count * y) + x + 1
        
                indices[idx + 3] = (vertex_count * y) + x + 1
                indices[idx + 4] = (vertex_count * (y + 1)) + x
                indices[idx + 5] = (vertex_count * (y + 1)) + x + 1
                idx += 6
        
        #print("indices", len(indices), indices)

        self.grid_vbo = Ogle.VertexBuffer(vertices)
        self.grid_ibo = Ogle.IndexBuffer(indices)
        
        attribs = np.array([ [ 3, 0 ], [ 2, 3*4 ] ], dtype=np.int32)
        self.grid_vao = Ogle.VertexArray(self.grid_vbo, self.grid_ibo, attribs, 4*len(vertices[0]))
        
        # TODO camera = std::make_unique<Ogle::Camera>(glm::vec3(0.f, 60.f, 0.f), 0.1f, 1000.f, 1000.f);
        
        # Initial spectrum
        self.initial_spectrum_program = Shader.createAndLinkComputeProgram("../shaders/CS_InitialSpectrum.comp")
        self.initial_spectrum_texture = Texture2D(self.RESOLUTION, self.RESOLUTION, GL.GL_R32F, GL.GL_RED, GL.GL_FLOAT)
        
        # Phase
        ping_phase_array = np.zeros((self.RESOLUTION * self.RESOLUTION), dtype=np.float32)
        
        for i in range(self.RESOLUTION * self.RESOLUTION):
            ping_phase_array[i] = random.uniform(0, 1) * 2.0 * np.pi
        #print("ping_phase_array", ping_phase_array)

        self.phase_program = Shader.createAndLinkComputeProgram("../shaders/CS_Phase.comp")
        self.ping_phase_texture = Texture2D(self.RESOLUTION, self.RESOLUTION, GL.GL_R32F, GL.GL_RED, GL.GL_FLOAT, 
                                       GL.GL_NEAREST, GL.GL_NEAREST, GL.GL_CLAMP_TO_BORDER, 
                                       GL.GL_CLAMP_TO_BORDER, ping_phase_array)
        self.pong_phase_texture = Texture2D(self.RESOLUTION, self.RESOLUTION, GL.GL_R32F, GL.GL_RED, GL.GL_FLOAT)
        
        # Time-varying spectrum
        
        self.spectrum_program = Shader.createAndLinkComputeProgram("../shaders/CS_Spectrum.comp")
        self.spectrum_texture = Texture2D(self.RESOLUTION, self.RESOLUTION, GL.GL_RGBA32F, GL.GL_RGBA, GL.GL_FLOAT, 
                                     GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_REPEAT, GL.GL_REPEAT)
        
        self.temp_texture = Texture2D(self.RESOLUTION, self.RESOLUTION, GL.GL_RGBA32F, GL.GL_RGBA, GL.GL_FLOAT)
        
        self.fft_horizontal_program = Shader.createAndLinkComputeProgram("../shaders/CS_FFTHorizontal.comp")
        self.fft_vertical_program = Shader.createAndLinkComputeProgram("../shaders/CS_FFTVertical.comp")

        # Normal map

        self.normal_map_program = Shader.createAndLinkComputeProgram("../shaders/CS_NormalMap.comp")
        self.normal_map = Texture2D(self.RESOLUTION, self.RESOLUTION, GL.GL_RGBA32F, GL.GL_RGBA, GL.GL_FLOAT, 
                               GL.GL_LINEAR, GL.GL_LINEAR, GL.GL_REPEAT, GL.GL_REPEAT)
        
        # Ocean shading
        self.ocean_program = Shader.createAndLinkProgramFiles("../shaders/VS_Ocean.vert", "../shaders/FS_Ocean.frag")

        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_BLEND)
        GL.glClearColor(0.674, 0.966, 0.988, 1.0)

    def SetInt(self, program, name, value):
        location = GL.glGetUniformLocation(program, name)
        GL.glUniform1i(location, value)

    def SetFloat(self, program, name, value):
        location = GL.glGetUniformLocation(program, name)
        GL.glUniform1f(location, value)        

    def SetVec2(self, program, name, value):
        location = GL.glGetUniformLocation(program, name)
        GL.glUniform2fv(location, 1, value)

    def SetVec3(self, program, name, value):
        location = GL.glGetUniformLocation(program, name)
        GL.glUniform3fv(location, 1, value) 

    def SetMat4(self, program, name, value):
        location = GL.glGetUniformLocation(program, name)
        GL.glUniformMatrix4fv(location, 1, False, value)               
 
    def Update(self):
        start_time = time.time()
        if (self.changed):

            GL.glUseProgram(self.initial_spectrum_program)
            self.SetInt(self.initial_spectrum_program, "u_ocean_size", self.ocean_size)
            self.SetInt(self.initial_spectrum_program, "u_resolution", self.RESOLUTION)
        
            wind_angle_rad = self.wind_angle * np.pi / 180
            self.SetVec2(self.initial_spectrum_program, "u_wind", [self.wind_magnitude * np.cos(wind_angle_rad), 
                                                                   self.wind_magnitude * np.sin(wind_angle_rad)])
            self.initial_spectrum_texture.BindImage(0, GL.GL_WRITE_ONLY)
        
            GL.glDispatchCompute(int(self.RESOLUTION / self.WORK_GROUP_DIM), 
                                 int(self.RESOLUTION / self.WORK_GROUP_DIM), 1)
            GL.glFinish()
        
            self.changed = False
        
        GL.glUseProgram(self.phase_program)
        self.SetInt(self.phase_program, "u_ocean_size", self.ocean_size)
        self.SetFloat(self.phase_program, "u_delta_time", self.delta_time)
        self.SetInt(self.phase_program, "u_resolution", self.RESOLUTION)
        
        if (self.is_ping_phase):
            #print("ping")type
            self.ping_phase_texture.BindImage(0, GL.GL_READ_ONLY)
            self.pong_phase_texture.BindImage(1, GL.GL_WRITE_ONLY)
        else:
            #print("pong")
            self.ping_phase_texture.BindImage(1, GL.GL_WRITE_ONLY)
            self.pong_phase_texture.BindImage(0, GL.GL_READ_ONLY)
        
        GL.glDispatchCompute(int(self.RESOLUTION / self.WORK_GROUP_DIM), 
                             int(self.RESOLUTION / self.WORK_GROUP_DIM), 1)
        GL.glFinish()

        #self.ping_phase_texture.Bind(0)
        #self.ping_phase_texture.print_values(0, 10, self.RESOLUTION, self.RESOLUTION)
        #self.pong_phase_texture.Bind(0)
        #self.pong_phase_texture.print_values(0, 10, self.RESOLUTION, self.RESOLUTION)        
        
        GL.glUseProgram(self.spectrum_program)
        
        self.SetInt(self.spectrum_program, "u_ocean_size", self.ocean_size)
        self.SetFloat(self.spectrum_program, "u_choppiness", self.choppiness)
        
        if self.is_ping_phase:
            self.pong_phase_texture.BindImage(0, GL.GL_READ_ONLY)
        else:
            self.ping_phase_texture.BindImage(0, GL.GL_READ_ONLY)

        self.initial_spectrum_texture.BindImage(1, GL.GL_READ_ONLY)
        
        self.spectrum_texture.BindImage(2, GL.GL_WRITE_ONLY)
        
        GL.glDispatchCompute(int(self.RESOLUTION / self.WORK_GROUP_DIM), 
                             int(self.RESOLUTION / self.WORK_GROUP_DIM), 1)
        GL.glFinish()
        
        # Rows
        GL.glUseProgram(self.fft_horizontal_program)
        self.SetInt(self.fft_horizontal_program, "u_total_count", self.RESOLUTION)
        
        temp_as_input = False   # Should you use temp_texture as input to the FFT shader?
        
        p = 1
        while (p < self.RESOLUTION):
            if (temp_as_input):
                self.temp_texture.BindImage(0, GL.GL_READ_ONLY)
                self.spectrum_texture.BindImage(1, GL.GL_WRITE_ONLY)
            else:
                self.spectrum_texture.BindImage(0, GL.GL_READ_ONLY)
                self.temp_texture.BindImage(1, GL.GL_WRITE_ONLY)
        
            self.SetInt(self.fft_horizontal_program, "u_subseq_count", p)
        
            # One work group per row
            GL.glDispatchCompute(self.RESOLUTION, 1, 1)
            GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        
            if (temp_as_input):
                temp_as_input = False
            else:
                temp_as_input = True
            p *= 2
        
        # Cols
        GL.glUseProgram(self.fft_vertical_program)
        self.SetInt(self.fft_vertical_program, "u_total_count", self.RESOLUTION)
        
        p = 1
        while (p < self.RESOLUTION):
            if (temp_as_input):
                self.temp_texture.BindImage(0, GL.GL_READ_ONLY)
                self.spectrum_texture.BindImage(1, GL.GL_WRITE_ONLY)
            else:
                self.spectrum_texture.BindImage(0, GL.GL_READ_ONLY)
                self.temp_texture.BindImage(1, GL.GL_WRITE_ONLY)
        
            self.SetInt(self.fft_vertical_program, "u_subseq_count", p)
        
            # One work group per col
            GL.glDispatchCompute(self.RESOLUTION, 1, 1)
            GL.glMemoryBarrier(GL.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        
            if (temp_as_input):
                temp_as_input = False
            else:
                temp_as_input = True
            p *= 2

        GL.glFinish()

        #self.temp_texture.Bind(0)
        #self.temp_texture.print_values(0, 10, self.RESOLUTION, self.RESOLUTION)
        #self.spectrum_texture.Bind(0)
        #self.spectrum_texture.print_values(0, 10, self.RESOLUTION, self.RESOLUTION)  


        # Generate Normal Map

        GL.glUseProgram(self.normal_map_program)
        self.spectrum_texture.BindImage(0, GL.GL_READ_ONLY)
        self.normal_map.BindImage(1, GL.GL_WRITE_ONLY)

        self.SetInt(self.normal_map_program, "u_resolution", self.RESOLUTION)
        self.SetInt(self.normal_map_program, "u_ocean_size", self.ocean_size)

        GL.glDispatchCompute(int(self.RESOLUTION / self.WORK_GROUP_DIM), 
                             int(self.RESOLUTION / self.WORK_GROUP_DIM), 1)
        GL.glFinish()

        #self.normal_map.Bind(0)
        #self.normal_map.print_values(0, 10, self.RESOLUTION, self.RESOLUTION)
        
        # Ocean Shading

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        GL.glUseProgram(self.ocean_program)
        cam_mat = [[0.974279, 0, -4.37201e-08, -4.37114e-08], [0, 1.73205, 0, 0], [-4.25871e-08, 0,
                   -1.0002, -1], [0, -103.923, -0.20002, 0]]
        cam_mat = [0.923584, 0.439366, 0.192421, 0.192382,
                   1.07723e-05, 1.04659, -0.796955, -0.796796,
                    0.31018, -1.30828, -0.57292, -0.572805,
                     -297.159, -291.899, 188.297, 188.459] 


        #cam_mat = np.linalg.inv(cam_mat)
        self.SetMat4(self.ocean_program, "u_pv", cam_mat) # glm::value_ptr(camera->GetProjViewMatrix((float)settings.width / settings.height)));
        self.SetVec3(self.ocean_program, "u_world_camera_pos", self.cam_pos) # camera->position.x, camera->position.y, camera->position.z);
        self.SetInt(self.ocean_program, "u_ocean_size", self.ocean_size)
        if self.wireframe_mode:
            self.SetInt(self.ocean_program, "u_wireframe", 1)
        else:
            self.SetInt(self.ocean_program, "u_wireframe", 0)

        sun_elevation_rad = self.sun_elevation * np.pi / 180
        sun_azimuth_rad = self.sun_azimuth * np.pi / 180
        self.SetVec3(self.ocean_program, "u_sun_direction", [-np.cos(sun_elevation_rad) * np.cos(sun_azimuth_rad), 
                     -np.sin(sun_elevation_rad), -np.cos(sun_elevation_rad) * np.sin(sun_azimuth_rad)])
        
        self.SetInt(self.ocean_program, "u_displacement_map", 0)
        if temp_as_input:
            self.temp_texture.Bind(0)
        else: 
            self.spectrum_texture.Bind(0)   # Todo: Make it clear that here we are binding disp map

        self.SetInt(self.ocean_program, "u_normal_map", 1)
        self.normal_map.Bind(1)
        
        #print(Debug.getUniforms(self.ocean_program))
        #Debug.readVertexBuffer(self.ocean_program, self.grid_vbo)
        #Debug.readIndexBuffer(self.ocean_program, self.grid_ibo)

        if self.is_ping_phase:
            self.is_ping_phase = False
        else:
            self.is_ping_phase = True
        
        Ogle.Bind(self.grid_vao)
        Ogle.BindIbo(self.grid_ibo)
        #Ogle.BindVbo(self.grid_vbo) # is this needed?

        if (self.wireframe_mode):
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        #GL.glEnableVertexAttribArray(0)
        #GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 5, 0)
        #GL.glEnableVertexAttribArray(1)
        #GL.glVertexAttribPointer(1, 2, GL.GL_FLOAT, GL.GL_FALSE, 5, 3)

        GL.glDrawElements(GL.GL_TRIANGLES, self.GRID_DIM * self.GRID_DIM * 2 * 3, GL.GL_UNSIGNED_INT, None)
        self.delta_time = (time.time() - start_time)*5

        GL.glFinish()

        #self.temp_texture.Bind(0)
        #self.temp_texture.print_values(0, 10, self.RESOLUTION, self.RESOLUTION)
        #self.spectrum_texture.Bind(0)
        #self.spectrum_texture.print_values(0, 10, self.RESOLUTION, self.RESOLUTION) 
        #self.normal_map.Bind(1)
        #self.normal_map.print_values(0, 10, self.RESOLUTION, self.RESOLUTION) 

        


