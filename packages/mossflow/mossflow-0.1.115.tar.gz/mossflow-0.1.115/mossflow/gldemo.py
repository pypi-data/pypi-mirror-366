import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np

# 创建顶点着色器
vertex_shader = """
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 texCoord;
out vec2 vTexCoord;
void main() {
    gl_Position = vec4(position, 1.0);
    vTexCoord = texCoord;
}
"""

# 创建片段着色器
fragment_shader = """
#version 330 core
in vec2 vTexCoord;
uniform sampler2D textureSampler;
out vec4 fragColor;
void main() {
    fragColor = texture(textureSampler, vTexCoord);
}
"""

def create_shader_program():
    """创建并编译着色器程序"""
    # 编译着色器
    vertex = compileShader(vertex_shader, GL_VERTEX_SHADER)
    fragment = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    
    # 链接着色器程序
    program = compileProgram(vertex, fragment)
    
    # 检查链接状态
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        print(f"程序链接错误: {error}")
        glDeleteProgram(program)
        return None
    
    return program

def create_texture(image_path):
    """从文件创建纹理"""
    # 加载图像
    image = pygame.image.load(image_path)
    image = pygame.transform.flip(image, False, True)  # 翻转图像以适应OpenGL坐标
    image_data = pygame.image.tostring(image, "RGBA", 1)
    
    # 创建纹理
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # 设置纹理参数
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    # 加载纹理数据
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.get_width(), image.get_height(), 
                 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    
    # 生成Mipmap
    glGenerateMipmap(GL_TEXTURE_2D)
    
    # 解绑纹理
    glBindTexture(GL_TEXTURE_2D, 0)
    
    return texture_id

def main():
    # 初始化Pygame和OpenGL
    pygame.init()
    pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("PyOpenGL 纹理渲染示例")
    
    # 设置OpenGL
    glClearColor(0.2, 0.3, 0.3, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    # 创建着色器程序
    shader_program = create_shader_program()
    if shader_program is None:
        pygame.quit()
        return
    
    # 创建纹理 (使用示例图片，也可以替换为其他图片路径)
    try:
        texture_id = create_texture("example.png")  # 替换为你的图片路径
    except:
        print("无法加载纹理图片，创建默认纹理")
        # 创建棋盘格纹理作为回退
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        # 创建简单的棋盘格图案
        checkerboard = np.array([
            [255, 255, 255, 255, 0, 0, 0, 0],
            [255, 255, 255, 255, 0, 0, 0, 0],
            [255, 255, 255, 255, 0, 0, 0, 0],
            [255, 255, 255, 255, 0, 0, 0, 0],
            [0, 0, 0, 0, 255, 255, 255, 255],
            [0, 0, 0, 0, 255, 255, 255, 255],
            [0, 0, 0, 0, 255, 255, 255, 255],
            [0, 0, 0, 0, 255, 255, 255, 255],
        ], dtype=np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 8, 8, 0, GL_RED, GL_UNSIGNED_BYTE, checkerboard)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
    
    # 定义顶点数据 (位置和纹理坐标)
    vertices = np.array([
        # 位置          # 纹理坐标
        -0.5, -0.5, 0.0, 0.0, 0.0,  # 左下
         0.5, -0.5, 0.0, 1.0, 0.0,  # 右下
         0.5,  0.5, 0.0, 1.0, 1.0,  # 右上
        -0.5,  0.5, 0.0, 0.0, 1.0   # 左上
    ], dtype=np.float32)
    
    # 定义索引数据
    indices = np.array([
        0, 1, 2,  # 第一个三角形
        0, 2, 3   # 第二个三角形
    ], dtype=np.uint32)
    
    # 创建顶点数组对象(VAO)和顶点缓冲对象(VBO)
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)
    
    glBindVertexArray(vao)
    
    # 绑定并设置顶点缓冲
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # 绑定并设置元素缓冲
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    
    # 位置属性
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    
    # 纹理坐标属性
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    glEnableVertexAttribArray(1)
    
    # 解绑VAO
    glBindVertexArray(0)
    
    # 主循环
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # 清除缓冲
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 使用着色器程序
        glUseProgram(shader_program)
        
        # 绑定纹理
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glUniform1i(glGetUniformLocation(shader_program, "textureSampler"), 0)
        
        # 绘制矩形
        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        # 交换缓冲
        pygame.display.flip()
        clock.tick(60)
    
    # 清理资源
    glDeleteVertexArrays(1, [vao])
    glDeleteBuffers(1, [vbo])
    glDeleteBuffers(1, [ebo])
    glDeleteProgram(shader_program)
    glDeleteTextures(1, [texture_id])
    
    pygame.quit()

if __name__ == "__main__":
    main()