from program_data import ProgramData

class Programs():
    ActivePrograms = []
		
    def reset():
        Programs.ActivePrograms = []

    def AddProgram(vertexShader, fragmentShader):
        program_number = -1
        new_program = True
        for i in range(len(Programs.ActivePrograms)):
            pd = Programs.ActivePrograms[i]
        
            if (pd.CompareShaders(vertexShader, fragmentShader)):
                new_program = False
                program_number = i
                break
        
        if (new_program == True):
            pd = ProgramData(vertexShader, fragmentShader)
            Programs.ActivePrograms.append(pd)
            program_number = len(Programs.ActivePrograms) - 1
        return program_number
		
    def Draw(program, vertexBufferObject, indexBufferObject,
                        mm, indexDataLength, color):
        Programs.ActivePrograms[program].Draw(vertexBufferObject, indexBufferObject, 
                                              mm, indexDataLength, color)

    def DrawWireFrame(program, vertexBufferObject, indexBufferObject,
                        mm, indexDataLength, color):
        Programs.ActivePrograms[program].DrawWireFrame(vertexBufferObject, indexBufferObject, 
                                              mm, indexDataLength, color)

		
    def SetUniformColor(program, color):
        Programs.ActivePrograms[program].SetUniformColor(color)
		
    def SetUniformTexture(program, colorTexUnit):
        Programs.ActivePrograms[program].SetUniformTexture(colorTexUnit)

    def SetUniformScale(program, scale):
        Programs.ActivePrograms[program].SetUniformScale(scale)

    def SetTexture(program, texture, oneTwenty):
        return Programs.ActivePrograms[program].SetTexture(texture, oneTwenty)

    def SetTexture(program, texture):
        Programs.ActivePrograms[program].SetTexture(texture)
		
    def SetLightPosition(program, lightPos):
        Programs.ActivePrograms[program].SetLightPosition(lightPos)

    def SetModelSpaceLightPosition(program, modelSpaceLightPos):
        Programs.ActivePrograms[program].SetModelSpaceLightPosition(modelSpaceLightPos)
		
    def SetDirectionToLight(program, dirToLight):
        Programs.ActivePrograms[program].SetDirectionToLight(dirToLight)

    def SetLightIntensity(program, lightIntensity):
        Programs.ActivePrograms[program].SetLightIntensity(lightIntensity)

    def SetAmbientIntensity(program, ambientIntensity):
        Programs.ActivePrograms[program].SetAmbientIntensity(ambientIntensity)

    def SetNormalModelToCameraMatrix(program, normalModelToCameraMatrix):
        Programs.ActivePrograms[program].SetNormalModelToCameraMatrix(normalModelToCameraMatrix)

    def SetModelToCameraMatrix(program, modelToCameraMatrix):
        Programs.ActivePrograms[program].SetModelToCameraMatrix(modelToCameraMatrix)

    def SetUpLightBlock(program, numberOfLights):
        Programs.ActivePrograms[program].SetUpLightBlock(numberOfLights)

    def SetUpMaterialBlock(program):
        Programs.ActivePrograms[program].SetUpMaterialBlock()

    def UpdateLightBlock(program, lb):
        Programs.ActivePrograms[program].UpdateLightBlock(lb)

    def UpdateMaterialBlock(program, mb):
        Programs.ActivePrograms[program].UpdateMaterialBlock(mb)

    # for testing only.  This should be calculated
    def SetVertexStride(program, vertexStride):
        Programs.ActivePrograms[program].SetVertexStride(vertexStride)

    def SetShadowMap(program, shadowMap):
        Programs.ActivePrograms[program].SetShadowMap(shadowMap)

    def GetProgramInfoLog(program):
        return Programs.ActivePrograms[program].getProgramInfoLog()

    def GetVertexShaderInfoLog(program):
        return Programs.ActivePrograms[program].getVertexShaderInfoLog()

    def GetVertexShader(program):
        return Programs.ActivePrograms[program].getVertexShader()

    def GetFragmentShader(program):
        return Programs.ActivePrograms[program].getFragmentShader()

    def GetVertexAttributes(program):
        return Programs.ActivePrograms[program].getVertexAttributes()

    def GetVertexShaderSource(program):
        return Programs.ActivePrograms[program].getVertexShaderSource()

    def GetUniforms(program):
        return Programs.ActivePrograms[program].getUniforms()

    def GetVertexShaderInfo(program):
        result = ""
        result += "\n"
        result += Programs.GetProgramInfoLog(program)
        result += "\n"
        result += Programs.GetVertexShaderInfoLog(program)
        result += "\n"
        result += "Vertex Shader = " + str(Programs.GetVertexShader(program))
        result += "\n"
        result += str(Programs.GetVertexShaderSource(program))
        result += "\n"
        result += Programs.GetVertexAttributes(program)
        result += Programs.GetUniforms(program)
        return result

    def GetFragmentShaderSource(program):
        return Programs.ActivePrograms[program].getFragmentShaderSource()

    def GetFragmentShaderInfo(program):
        result = ""
        result += "Fragment Shader = " + str(Programs.GetFragmentShader(program))
        result += "\n"
        result += str(Programs.GetFragmentShaderSource(program))
        result += "\n"
        return result
			
    def DumpShaders():
        result = ""
        for program in range(len(Programs.ActivePrograms)):
            result += "\n"
            result += "Program " + program.ToString()
            result += "\n"
            result += Programs.GetVertexShaderInfo(program)
            result += "\n"
            result += Programs.GetFragmentShaderInfo(program)
            result += "\n"
        return result

    def GetProgram(program):
        return Programs.ActivePrograms[program].GetProgram()

    def GetModelToCameraMatrixUnif(program):
        return Programs.ActivePrograms[program].GetModelToCameraMatrixUnif()

    def GetCameraToClipMatrixUniform(program):
        return Programs.ActivePrograms[program].GetCameraToClipMatrixUniform()

    def GetShadowMapUniform(program):
        return Programs.ActivePrograms[program].GetShadowMapUniform()
