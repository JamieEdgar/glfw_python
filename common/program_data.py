import OpenGL.GL as GL
import numpy as np
from light_block import LightBlock
from material_block import MaterialBlock
from shader import Shader
from world_matrixes import cameraToClip, worldToCamera
from textures import Textures
from message_box import MessageBox

class ProgramData():


    POSITION_DATA_SIZE_IN_ELEMENTS = 3
    NORMAL_DATA_SIZE_IN_ELEMENTS = 3
    NORMAL_START = 3 * 4 # POSITION_DATA_SIZE_IN_ELEMENTS * BYTES_PER_FLOAT;
    TEXTURE_DATA_SIZE_IN_ELEMENTS = 2
    TEXTURE_START = 3 * 4 + 3 * 4   

    def __init__(self, vertexShaderIn, fragmentShaderIn):
        self.vertexShader = vertexShaderIn
        self.fragmentShader = fragmentShaderIn
        self.vertex_shader = Shader.compileShader(GL.GL_VERTEX_SHADER, self.vertexShader)
        self.fragment_shader = Shader.compileShader(GL.GL_FRAGMENT_SHADER, self.fragmentShader)
        self.theProgram  = Shader.createAndLinkProgram(self.vertex_shader, self.fragment_shader)

        self.positionAttribute = GL.glGetAttribLocation(self.theProgram, "position")
        self.colorAttribute = GL.glGetAttribLocation(self.theProgram, "color")
        if (self.positionAttribute != -1):
            if (self.positionAttribute != 0):
                MessageBox.Show("These meshes only work with position at location 0 " + self.vertexShader)
        if (self.colorAttribute != -1):
            if (self.colorAttribute != 1):
                MessageBox.Show("These meshes only work with color at location 1" + self.vertexShader)

        self.modelToWorldMatrixUnif = GL.glGetUniformLocation(self.theProgram, "modelToWorldMatrix")
        self.worldToCameraMatrixUnif = GL.glGetUniformLocation(self.theProgram, "worldToCameraMatrix")
        self.cameraToClipMatrixUnif = GL.glGetUniformLocation(self.theProgram, "cameraToClipMatrix")
        if (self.cameraToClipMatrixUnif == -1):
            self.cameraToClipMatrixUnif = GL.glGetUniformLocation(self.theProgram, "Projection.cameraToClipMatrix")
        self.baseColorUnif = GL.glGetUniformLocation(self.theProgram, "baseColor")
        self.modelToCameraMatrixUnif = GL.glGetUniformLocation(self.theProgram, "modelToCameraMatrix")
        self.normalModelToCameraMatrixUnif = GL.glGetUniformLocation(self.theProgram, "normalModelToCameraMatrix")
        self.dirToLightUnif =  GL.glGetUniformLocation(self.theProgram, "dirToLight")
        self.lightPosUnif = GL.glGetUniformLocation(self.theProgram, "lightPos")
        self.modelSpaceLightPosUnif = GL.glGetUniformLocation(self.theProgram, "modelSpaceLightPos")
        self.lightIntensityUnif = GL.glGetUniformLocation(self.theProgram, "lightIntensity")
        self.ambientIntensityUnif = GL.glGetUniformLocation(self.theProgram, "ambientIntensity")
        self.normalAttribute = GL.glGetAttribLocation(self.theProgram, "normal")
        self.texCoordAttribute = GL.glGetAttribLocation(self.theProgram, "texCoord")
        self.sampler = 0
        self.colorTextureUnif = GL.glGetUniformLocation(self.theProgram, "diffuseColorTex")
        self.scaleUniform = GL.glGetUniformLocation(self.theProgram, "scaleFactor")
        self.shadowMapUniform = GL.glGetUniformLocation(self.theProgram,"ShadowMap")

        self.vertexStride = 3 * 4
        if (self.normalAttribute != -1):
            self.vertexStride = 3 * 4 * 2
            
        if (self.texCoordAttribute != -1):
            self.CreateSampler()
            self.vertexStride = 3 * 4 * 2 + 2 * 4            
        self.texUnit = 0
        print("Normal Attribute", self.normalAttribute)
        print("Vertex stride", self.vertexStride)
		
    def CreateSampler(self):
        GL.glGenSamplers(1, self.sampler)
        GL.glSamplerParameteri(self.sampler, GL.GL_TEXTURE_MAG_FILTER,  GL.GL_NEAREST)
        GL.glSamplerParameteri(self.sampler, GL.GL_TEXTURE_MIN_FILTER,  GL.GL_NEAREST)
        GL.glSamplerParameteri(self.sampler, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
		
    def CompareShaders(self, vertexShaderIn, fragmentShaderIn):
        return ((vertexShaderIn == self.vertexShader) & (self.fragmentShader == fragmentShaderIn))
		
    def Draw(self, vertexBufferObject, indexBufferObject, mm, indexDataLength, color):
        GL.glUseProgram(self.theProgram);	
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertexBufferObject)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, indexBufferObject)
        
        GL.glUniformMatrix4fv(self.cameraToClipMatrixUnif, 1, False, cameraToClip)
        GL.glUniformMatrix4fv(self.worldToCameraMatrixUnif, 1, False, worldToCamera)
        
        if (self.modelToWorldMatrixUnif != -1):
            GL.glUniformMatrix4fv(self.modelToWorldMatrixUnif, 1, False, mm)
        if (self.modelToCameraMatrixUnif != -1):
            GL.glUniformMatrix4fv(self.modelToCameraMatrixUnif, 1, False, mm)
        if (self.baseColorUnif != -1):
            GL.glUniform4fv(self.baseColorUnif, 1, color)
        

        GL.glEnableVertexAttribArray(self.positionAttribute)
        # Prepare the triangle coordinate data
        GL.glVertexAttribPointer(self.positionAttribute, ProgramData.POSITION_DATA_SIZE_IN_ELEMENTS, 
        GL.GL_FLOAT, False, self.vertexStride, 0)
			
        if (self.normalAttribute != -1):
            GL.glEnableVertexAttribArray(self.normalAttribute)
            GL.glVertexAttribPointer(self.normalAttribute, ProgramData.NORMAL_DATA_SIZE_IN_ELEMENTS, 
                GL.GL_FLOAT, False, self.vertexStride, ProgramData.NORMAL_START)

        if (self.texCoordAttribute != -1):
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glEnableVertexAttribArray(self.texCoordAttribute)
            GL.glVertexAttribPointer(self.texCoordAttribute, ProgramData.TEXTURE_DATA_SIZE_IN_ELEMENTS, 
                GL.GL_FLOAT, False, self.vertexStride, ProgramData.TEXTURE_START)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.current_texture)
            GL.glBindSampler(self.texUnit, self.sampler)	

        # Draw the triangle
        GL.glDrawElements(GL.GL_TRIANGLES, indexDataLength, GL.GL_UNSIGNED_SHORT, None)

        # Disable vertex array
        GL.glDisableVertexAttribArray(self.positionAttribute)
        if (self.normalAttribute != -1):
            GL.glDisableVertexAttribArray(self.normalAttribute)
        
        if (self.texCoordAttribute != -1):
            GL.glDisableVertexAttribArray(self.texCoordAttribute)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def DrawWireFrame(self, vertexBufferObject, indexBufferObject, mm, indexDataLength, color):
        GL.UseProgram(self.theProgram)
        GL.BindBuffer(GL.GL_ARRAY_BUFFER, vertexBufferObject[0])
        GL.BindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, indexBufferObject[0])

        GL.UniformMatrix4(self.cameraToClipMatrixUnif, False, cameraToClip)
        GL.UniformMatrix4(self.worldToCameraMatrixUnif, False, worldToCamera)

        if (self.modelToWorldMatrixUnif != -1):
            GL.UniformMatrix4(self.modelToWorldMatrixUnif, False, mm)
        if (self.modelToCameraMatrixUnif != -1):
            GL.UniformMatrix4(self.modelToCameraMatrixUnif, False, mm)
        if (self.baseColorUnif != -1):
            GL.Uniform4(self.baseColorUnif, 1, color)


        GL.EnableVertexAttribArray(self.positionAttribute)
        # Prepare the triangle coordinate data
        GL.VertexAttribPointer(self.positionAttribute, ProgramData.POSITION_DATA_SIZE_IN_ELEMENTS, 
            GL.GL_FLOAT, False, self.vertexStride, 0)

        if (self.normalAttribute != -1):
            GL.EnableVertexAttribArray(self.normalAttribute)
            GL.VertexAttribPointer(self.normalAttribute, ProgramData.NORMAL_DATA_SIZE_IN_ELEMENTS, 
                GL.GL_FLOAT, False, self.vertexStride, ProgramData.NORMAL_START)

        if (self.texCoordAttribute != -1):
            GL.Enable(GL.GL_TEXTURE_2D)
            GL.EnableVertexAttribArray(self.texCoordAttribute)
            GL.VertexAttribPointer(self.texCoordAttribute, ProgramData.TEXTURE_DATA_SIZE_IN_ELEMENTS, 
                GL.GL_FLOAT, False, self.vertexStride, ProgramData.TEXTURE_START)
            GL.BindTexture(GL.GL_TEXTURE_2D, self.current_texture)
            GL.BindSampler(self.texUnit, self.sampler)

        # Draw the wireframes
        for i in range(0, indexDataLength, 3):
            GL.DrawElements(GL.GL_LINE_LOOP, 3, GL.GL_UNSIGNED_SHORT, i * 2) # 2 is size of short

        # Disable vertex array
        GL.DisableVertexAttribArray(self.positionAttribute)
        if (self.normalAttribute != -1):
            GL.DisableVertexAttribArray(self.normalAttribute)
        if (self.texCoordAttribute != -1):
            GL.DisableVertexAttribArray(self.texCoordAttribute)

        GL.BindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.BindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.UseProgram(0)
			
    def ToString(self):
        result = ""
        result += "theProgram = " + self.theProgram.ToString()
        result += "positionAttribute = " + self.positionAttribute.ToString()
        result += "colorAttribute = " + self.colorAttribute.ToString()
        result += "modelToCameraMatrixUnif = " + self.modelToCameraMatrixUnif.ToString()
        result += "modelToWorldMatrixUnif = " + self.modelToWorldMatrixUnif.ToString()
        result += "worldToCameraMatrixUnif = " + self.worldToCameraMatrixUnif.ToString()
        result += "cameraToClipMatrixUnif = " + self.cameraToClipMatrixUnif.ToString()
        result += "baseColorUnif = " + self.baseColorUnif.ToString()
        result += "normalModelToCameraMatrixUnif = " + self.normalModelToCameraMatrixUnif.ToString()
        result += "dirToLightUnif = " + self.dirToLightUnif.ToString()
        result += "lightIntensityUnif = " + self.lightIntensityUnif.ToString()
        result += "ambientIntensityUnif = " + self.ambientIntensityUnif.ToString()
        result += "normalAttribute = " + self.normalAttribute.ToString()
        return result
		
    def SetUniformColor(self, color):
        GL.UseProgram(self.theProgram)
        GL.Uniform4(self.baseColorUnif, color)
        GL.UseProgram(0)
		
    def SetUniformTexture(self, colorTexUnit):
        GL.UseProgram(self.theProgram)
        GL.Uniform1(self.colorTextureUnif, colorTexUnit)
        GL.UseProgram(0)

    def SetUniformScale(self, scale):
        GL.UseProgram(self.theProgram)
        GL.Uniform1(self.scaleUniform, scale)
        GL.UseProgram(0)
			
    def SetTexture(self, texture, oneTwenty):
        self.current_texture = Textures.Load(texture, 1, False, False, oneTwenty)
        return self.current_texture

    def SetTexture(self, texture):
        current_texture = texture
		
    def SetLightPosition(self, lightPosition):
        GL.glUseProgram(self.theProgram)
        GL.glUniform3fv(self.lightPosUnif, 1, lightPosition)
        GL.glUseProgram(0)

    def SetModelSpaceLightPosition(self, modelSpaceLightPos):
        GL.UseProgram(self.theProgram)
        GL.Uniform3(self.modelSpaceLightPosUnif, modelSpaceLightPos)
        GL.UseProgram(0)

    def SetDirectionToLight(self, dirToLight):
        GL.UseProgram(self.theProgram)
        GL.Uniform3(self.dirToLightUnif, dirToLight)
        GL.UseProgram(0)
		
    def SetLightIntensity(self, lightIntensity):
        GL.UseProgram(self.theProgram)
        GL.Uniform4(self.lightIntensityUnif, lightIntensity)
        GL.UseProgram(0)

    def SetAmbientIntensity(self, ambientIntensity):
        GL.UseProgram(self.theProgram)
        GL.Uniform4(self.ambientIntensityUnif, ambientIntensity)
        GL.UseProgram(0)

    def SetNormalModelToCameraMatrix(self, normalModelToCameraMatrix):
        GL.UseProgram(self.theProgram)
        GL.UniformMatrix3(self.normalModelToCameraMatrixUnif, False, normalModelToCameraMatrix)
        GL.UseProgram(0)

    def SetModelToCameraMatrix(self, modelToCameraMatrix):
        GL.UseProgram(self.theProgram)
        GL.UniformMatrix4(self.modelToCameraMatrixUnif, False, modelToCameraMatrix)
        GL.UseProgram(0)

    def SetUpLightBlock(self, numberOfLights):
        self.lightBlock = LightBlock(numberOfLights)
        self.lightBlock.SetUniforms(self.theProgram)

    def SetUpMaterialBlock(self):
        self.materialBlock = MaterialBlock()
        self.materialBlock.SetUniforms(self.theProgram)

    def UpdateLightBlock(self, lb):
        self.lightBlock.Update(lb)

    def UpdateMaterialBlock(self, mb):
        self.materialBlock.Update(mb)
		
    def SetVertexStride(self, vertexStrideIn):
        self.vertexStride = vertexStrideIn

    def SetShadowMap(self, shadowMap):
        GL.UseProgram(self.theProgram)
        GL.Uniform1(shadowMap, shadowMap)
        GL.UseProgram(0)

    def getVertexShader(self):
        return self.vertex_shader

    def getVertexShaderSource(self):
        return self.getShaderSource(self.vertex_shader)

    def getFragmentShaderSource(self):
        return self.getShaderSource(self.fragment_shader)

    def getProgramInfoLog(self):
        GL.glValidateProgram(self.theProgram)
        return GL.glGetProgramInfoLog(self.theProgram)

    def getVertexShaderInfoLog(self):
        return self.getShaderInfoLog(self.vertex_shader)

    def getFragmentShaderInfoLog(self):
        return self.getShaderInfoLog(self.fragment_shader)

    def getShaderInfoLog(self, shader):
        return GL.glGetShaderInfoLog(shader)

    def getShaderSource(self, shader):
        source = ""
        length = 0
        bufSize = 4096
        source = GL.glGetShaderSource(shader)
        return source

    def getVertexAttributes(self):
        result = ""
        buf_size = 255
        type_out = None
        attribCount = GL.glGetProgramiv(self.theProgram, GL.GL_ACTIVE_ATTRIBUTES)
        result += "\nattributes " + str(attribCount)
        for i in range(attribCount):
            name, size, type = GL.glGetActiveAttrib(self.theProgram, i, buf_size)
            result += "\n" + str(name) + " " + str(size) + " " + str(type)
        return result

    def getUniformFloats(self, name, Length):
        location = GL.glGetUniformLocation(self.theProgram, name)
        result = ""
        values = np.zeros(Length, np.float32)
        GL.glGetUniformfv(self.theProgram, location, values)
        for i in range(len(values)):
            result += str(values[i]) + " "
        return result

    def getUniforms(self):
        result = ""
        buffer_size = 256
        uniformCount = GL.glGetProgramiv(self.theProgram, GL.GL_ACTIVE_UNIFORMS)
        result += "\nuniforms " + str(uniformCount)
        for i in range(uniformCount):
            name, size, type = GL.glGetActiveUniform(self.theProgram, i, buffer_size)
            result += "\n" + str(name)
            typeString = ""
            match type:
                case GL.GL_FLOAT_VEC2: 
                    typeString += self.getUniformFloats(name, 2)
                case GL.GL_FLOAT_VEC3: 
                    typeString += self.getUniformFloats(name, 3)
                case GL.GL_FLOAT_VEC4:
                    typeString += self.getUniformFloats(name, 4)
                case GL.GL_INT_VEC2:
                    pass
                case GL.GL_INT_VEC3:
                    pass
                case GL.GL_INT_VEC4:
                    pass
                case GL.GL_BOOL:
                    pass
                case GL.GL_BOOL_VEC2:
                    pass
                case GL.GL_BOOL_VEC3:
                    pass
                case GL.GL_BOOL_VEC4:
                    pass
                case GL.GL_FLOAT_MAT2: 
                    typeString += self.getUniformFloats(name, 4)
                case GL.GL_FLOAT_MAT3: 
                    typeString += self.getUniformFloats(name, 9)
                case GL.GL_FLOAT_MAT4: 
                    typeString += self.getUniformFloats(name, 16)
                case GL.GL_SAMPLER_2D:
                    pass
                case GL.GL_SAMPLER_CUBE:
                    pass
            result += " type = " + typeString
        return result

    def getFragmentShader(self):
        return self.fragment_shader

    def GetProgram(self):
        return self.theProgram

    def GetModelToCameraMatrixUnif(self):
        return self.modelToCameraMatrixUnif

    def GetCameraToClipMatrixUniform(self):
        return self.cameraToClipMatrixUnif

    def GetShadowMapUniform(self):
        return self.shadowMapUniform