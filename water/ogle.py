import OpenGL.GL as GL
import ctypes

class Ogle():
    def VertexBuffer(vertices):
        id = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, id)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        return id
    
    def IndexBuffer(indices):
        id = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, id)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        return id

    def VertexArray(vbo, ibo, attribs, stride):
        id = GL.glGenVertexArrays(1)

        Ogle.Bind(id)
        if (ibo != 0): 
            Ogle.BindIbo(ibo)
        Ogle.BindVbo(vbo)


        for i in range(len(attribs)):
            GL.glEnableVertexAttribArray(i)
            if i == 0:
                GL.glVertexAttribPointer(i, attribs[i][0], GL.GL_FLOAT, GL.GL_FALSE, stride, None)
            else:
                offset = attribs[i][1].item()
                GL.glVertexAttribPointer(i, attribs[i][0], GL.GL_FLOAT, GL.GL_FALSE, stride, ctypes.c_void_p(offset))
            #GL.glEnableVertexAttribArray(i)

        Ogle.Unbind()      # Three of these seems strange?
        Ogle.Unbind()
        Ogle.Unbind()
        return id


    def Bind(id):
        GL.glBindVertexArray(id)

    def BindIbo(id):
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, id)

    def BindVbo(id):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, id)

    def Unbind():
        GL.glBindVertexArray(0)     