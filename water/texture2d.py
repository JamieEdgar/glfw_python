import OpenGL.GL as GL
import numpy as np

class Texture2D:
    def __init__(self, width, height, internal_format, format, type, min_filter = GL.GL_NEAREST, 
                 max_filter = GL.GL_NEAREST, wrap_r = GL.GL_CLAMP_TO_BORDER, 
                 wrap_s = GL.GL_CLAMP_TO_BORDER, data=None):
        self.width = width
        self.height = height
        self.internal_format = internal_format
        self.format = format
        self.type = type
        self.id = GL.glGenTextures(1)
        #print("Texture ID", self.id)

        self.Bind(0)

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, min_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, max_filter)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_R, wrap_r)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, wrap_s)

        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, internal_format, width, height, 0, format, type, data)

        #self.Unbind()

    def Bind(self, sel):
        if sel == 0:
            GL.glActiveTexture(GL.GL_TEXTURE0)
        if sel == 1:
            GL.glActiveTexture(GL.GL_TEXTURE1)
        if sel == 2:
            GL.glActiveTexture(GL.GL_TEXTURE2)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.id)

    def Unbind(self):
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    def BindImage(self, unit, access):
        GL.glBindImageTexture(unit, self.id, 0, GL.GL_FALSE, 0, access, self.internal_format)    

    def get_values(self, set, x, y):
        collection_size = x * y * 4
        compute_data = np.zeros( collection_size, np.float32 )
        compute_data = GL.glGetTexImage(GL.GL_TEXTURE_2D, set, self.format, GL.GL_FLOAT, compute_data)
        return compute_data

    def print_values(self, set, count, x, y):
        values = self.get_values(set, x, y)
        for i in range(count):
            print(values[i], end=" ")
        print("")

