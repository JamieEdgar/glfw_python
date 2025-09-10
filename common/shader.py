import OpenGL.GL as GL
from message_box import MessageBox

class Shader():

    def readShaderSource(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                file_content_as_string = file.read()
            #print(file_content_as_string)
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return file_content_as_string
    
    def compileFromFile(shaderType, filename):
        shaderSource = Shader.readShaderSource(filename)
        return Shader.compileShader(shaderType, shaderSource)

    def compileShader(shaderType, shaderSource):
        shaderHandle = GL.glCreateShader(shaderType)

        if (shaderHandle != 0):
            # Pass in the shader source.
            GL.glShaderSource(shaderHandle, shaderSource)

            # Compile the shader.
            GL.glCompileShader(shaderHandle)

            # Get the compilation status.
            compileStatus = GL.glGetShaderiv(shaderHandle, GL.GL_COMPILE_STATUS)

            # If the compilation failed, delete the shader.
            if (compileStatus == 0):
                shaderInfoLog = GL.glGetShaderInfoLog(shaderHandle)
                MessageBox.Show("Error creating shader: " + str(shaderInfoLog))
                GL.DeleteShader(shaderHandle)
                shaderHandle = 0

        if (shaderHandle == 0):
            MessageBox.Show("Error creating shader.")

        return shaderHandle
    
    def createAndLinkProgramFiles(vertex, frag):
        vertexShaderHandle = Shader.compileFromFile(GL.GL_VERTEX_SHADER, vertex)
        fragmentShaderHandle = Shader.compileFromFile(GL.GL_FRAGMENT_SHADER, frag)
        return Shader.createAndLinkProgram(vertexShaderHandle, fragmentShaderHandle)

		
    def createAndLinkProgram(vertexShaderHandle, fragmentShaderHandle):
        programHandle = GL.glCreateProgram()

        if (programHandle != 0):
            # Bind the vertex shader to the program.
            GL.glAttachShader(programHandle, vertexShaderHandle)

            # Bind the fragment shader to the program.
            GL.glAttachShader(programHandle, fragmentShaderHandle)

            # Link the two shaders together into a program.
            GL.glLinkProgram(programHandle)
	
            # Get the link status.
            linkStatus = GL.glGetProgramiv(programHandle, GL.GL_LINK_STATUS)

            # If the link failed, delete the program.
            if (linkStatus == 0):
                errorInfo = GL.glGetProgramInfoLog(programHandle)
                MessageBox.Show("Error compiling program: " + errorInfo)
                GL.glDeleteProgram(programHandle)
                programHandle = 0
        return programHandle
    
    def createAndLinkComputeProgram(filename):
        programHandle = GL.glCreateProgram()

        if (programHandle != 0):
            # Bind the compute shader to the program.
            computeShaderHandle = Shader.compileFromFile(GL.GL_COMPUTE_SHADER, filename)
            GL.glAttachShader(programHandle, computeShaderHandle)

            # Link the two shaders together into a program.
            GL.glLinkProgram(programHandle)
	
            # Get the link status.
            linkStatus = GL.glGetProgramiv(programHandle, GL.GL_LINK_STATUS)

            # If the link failed, delete the program.
            if (linkStatus == 0):
                errorInfo = GL.glGetProgramInfoLog(programHandle)
                MessageBox.Show("Error compiling program: " + errorInfo)
                GL.glDeleteProgram(programHandle)
                programHandle = 0
        return programHandle        

		
    def createAndLinkProgramAttr(vertexShaderHandle, fragmentShaderHandle, attributes):
        programHandle = GL.CreateProgram()

        if (programHandle != 0):
            # Bind the vertex shader to the program.
            GL.AttachShader(programHandle, vertexShaderHandle)

            # Bind the fragment shader to the program.
            GL.AttachShader(programHandle, fragmentShaderHandle)

            # Bind attributes
            if (attributes != None):
                size = len(attributes)
                for i in range(size):
                    GL.BindAttribLocation(programHandle, i, attributes[i])

            # Link the two shaders together into a program.
            GL.LinkProgram(programHandle)

            # Get the link status.
            linkStatus = [0]
            GL.GetProgram(programHandle, GL.GL_LINK_STATUS, linkStatus)

            # If the link failed, delete the program.
            if (linkStatus[0] == 0):
                MessageBox.Show("Error compiling program: " + GL.GetProgramInfoLog(programHandle))
                GL.DeleteProgram(programHandle)
                programHandle = 0

        if (programHandle == 0):
            MessageBox.Show("Error creating program.")

        return programHandle

    def LinkProgram(shaderHandles):
        programHandle = GL.CreateProgram()

        if (programHandle != 0):
            # Bind the shaders to the program.
            for handle in shaderHandles:
                GL.AttachShader(programHandle, handle)
                
            # Link the two shaders together into a program.
            GL.LinkProgram(programHandle)

            # Get the link status.
            linkStatus = [0]
            GL.GetProgram(programHandle, GL.GL_LINK_STATUS, linkStatus)

            # If the link failed, delete the program.
            if (linkStatus[0] == 0):
                errorInfo = GL.GetProgramInfoLog(programHandle)
                MessageBox.Show("Error compiling program: " + errorInfo)
                GL.DeleteProgram(programHandle)
                programHandle = 0
        return programHandle
