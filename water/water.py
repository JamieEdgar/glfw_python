import OpenGL.GL as GL
import numpy as np
from texture2d import Texture2D
import glfw

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'common/'))

print(sys.path)

from shader import Shader
from ocean_fft import OceanFFT

print("water")
print("Based on C++ code at https://github.com/achalpandeyy/OceanFFT")

if not glfw.init():
    raise RuntimeError("GLFW initialization failed")

window = glfw.create_window(1280, 720, "OceanFFT Python Version", None, None)
if not window:
    glfw.terminate()
    raise RuntimeError("GLFW window creation failed")
glfw.make_context_current(window)

offt = OceanFFT()
offt.Initialize()
    

count = 0

while not glfw.window_should_close(window):
        #ShowScreen()
        glfw.swap_buffers(window)
        #GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        #GL.glLoadIdentity()
        offt.Update()
        if count % 47 == 0:
             #offt.choppiness = 25
             pass
        if count < 10 == 0:
             #offt.wind_magnitude += 1
             offt.changed = True
             count += 1
             #offt.cam_pos = [0, 1000, 0]
        glfw.poll_events()

glfw.destroy_window(window)
glfw.terminate()


