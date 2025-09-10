import OpenGL.GL as GL
import numpy as np
import ctypes

class Debug():
    def get_uniform(program, name):
        GL.glUseProgram(program)
        location = GL.glGetUniformLocation(program, name)
        print(name, location)

    def getUniformFloats(program, name, Length):
        location = GL.glGetUniformLocation(program, name)
        result = ""
        values = np.zeros(Length, np.float32)
        GL.glGetUniformfv(program, location, values)
        for i in range(len(values)):
            result += str(values[i]) + " "
        return result   
    
    def getUniformInts(program, name, Length):
        location = GL.glGetUniformLocation(program, name)
        result = ""
        values = np.zeros(Length, np.int32)
        GL.glGetUniformiv(program, location, values)
        for i in range(len(values)):
            result += str(values[i]) + " "
        return result         

    def getUniforms(program):
        GL.glUseProgram(program)
        result = ""
        buffer_size = 256
        uniformCount = GL.glGetProgramiv(program, GL.GL_ACTIVE_UNIFORMS)
        result += "\nuniforms " + str(uniformCount)
        for i in range(uniformCount):
            name, size, type = GL.glGetActiveUniform(program, i, buffer_size)
            result += "\n" + str(name)
            typeString = ""
            match type:
                case GL.GL_FLOAT_VEC2: 
                    typeString += Debug.getUniformFloats(program, name, 2)
                case GL.GL_FLOAT_VEC3: 
                    typeString += Debug.getUniformFloats(program, name, 3)
                case GL.GL_FLOAT_VEC4:
                    typeString += Debug.getUniformFloats(program, name, 4)
                case GL.GL_INT:
                    typeString += Debug.getUniformInts(program, name, 1)
                case GL.GL_INT_VEC2:
                    typeString += Debug.getUniformInts(program, name, 2)
                case GL.GL_INT_VEC3:
                    typeString += Debug.getUniformInts(program, name, 3)
                case GL.GL_INT_VEC4:
                    typeString += Debug.getUniformInts(program, name, 4)
                case GL.GL_BOOL:
                    pass
                case GL.GL_BOOL_VEC2:
                    pass
                case GL.GL_BOOL_VEC3:
                    pass
                case GL.GL_BOOL_VEC4:
                    pass
                case GL.GL_FLOAT_MAT2: 
                    typeString += Debug.getUniformFloats(program, name, 4)
                case GL.GL_FLOAT_MAT3: 
                    typeString += Debug.getUniformFloats(program, name, 9)
                case GL.GL_FLOAT_MAT4: 
                    typeString += Debug.getUniformFloats(program, name, 16)
                case GL.GL_SAMPLER_2D:
                    typeString = "GL_SAMPLER_2D"
                case GL.GL_SAMPLER_CUBE:
                    pass
            result += " type = " + typeString
        return result        
    
    def readVertexBuffer(program, vbo, length=100):
        GL.glUseProgram(program)
        # Bind the VBO
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)

        # Map the buffer for reading
        # Using glMapBufferRange for a specific range or glMapBuffer for the whole buffer
        mapped_data = GL.glMapBufferRange(GL.GL_ARRAY_BUFFER, 0, length, GL.GL_MAP_READ_BIT)

        if mapped_data is not None:
            # Convert the mapped data to a NumPy array for easier manipulation
            # Adjust dtype based on your vertex data format (e.g., GL_FLOAT for positions)
            vertex_data = (ctypes.c_float * length).from_address(mapped_data)

            # Process or print the vertex_data
            print("Vertex data read from VBO:")
            for i in range(length):
                print(vertex_data[i], end = " ")
            print("")

            # Unmap the buffer
            GL.glUnmapBuffer(GL.GL_ARRAY_BUFFER)
        else:
            print("Failed to map buffer.")

        # Unbind the VBO (optional, but good practice)
        #glBindBuffer(GL_ARRAY_BUFFER, 0)

    def readIndexBuffer(program, ibo, length=100):
        GL.glUseProgram(program)
        # Bind the VBO
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ibo)

        # Map the buffer for reading
        # Using glMapBufferRange for a specific range or glMapBuffer for the whole buffer
        mapped_data = GL.glMapBufferRange(GL.GL_ELEMENT_ARRAY_BUFFER, 0, length, GL.GL_MAP_READ_BIT)

        if mapped_data is not None:
            # Convert the mapped data to a NumPy array for easier manipulation
            # Adjust dtype based on your vertex data format (e.g., GL_FLOAT for positions)
            index_data = (ctypes.c_int * length).from_address(mapped_data)

            # Process or print the vertex_data
            print("Index data read from IBO:")
            for i in range(length):
                print(index_data[i], end = " ")
            print("")

            # Unmap the buffer
            GL.glUnmapBuffer(GL.GL_ELEMENT_ARRAY_BUFFER)
        else:
            print("Failed to map buffer.")

        # Unbind the VBO (optional, but good practice)
        #glBindBuffer(GL_ARRAY_BUFFER, 0)        