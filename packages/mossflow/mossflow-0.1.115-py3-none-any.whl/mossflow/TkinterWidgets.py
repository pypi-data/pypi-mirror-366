import tkinter as tk
from tkhtmlview import HTMLLabel
from tkinter import ttk,colorchooser,messagebox
from tkinter import font as tkfont
from pyopengltk import OpenGLFrame
from OpenGL.GL import *
from OpenGL.WGL import *
import numpy as np
from math import pi, cos, sin
from PIL import Image, ImageDraw, ImageFont
import cv2
import time
import json
from tkinter import filedialog, messagebox
import os,sys
import importlib.util
from importlib.resources import files, as_file
import re
from OpenGL.GL.shaders import compileShader, compileProgram
import glm
from enum import Enum
class TextureFormat(Enum):
    Color = 0
    Luminance = 1
    DepthColor = 2
def load_icon(iconpath='main.ico'):
    try:
        # 使用files() API (Python 3.9+)
        ref = files("mossflow.resources") / f"{iconpath}"
        with as_file(ref) as icon_path:
            return str(icon_path)  # 返回绝对路径
    except Exception as e:
        print(f"加载图标失败: {e}")
        return None
iconp=load_icon()
class ImgViewer(tk.Toplevel):
    def __init__(self, parent, module):
        """
        图像查看器窗口
        :param parent: 父窗口
        :param image: 要显示的图像（numpy数组）
        """
        super().__init__(parent)    
        self.maxscalevalue = tk.DoubleVar()
        self.minscalevalue = tk.DoubleVar()
        self.title("Image Viewer")
        self.iconbitmap(load_icon())  # 设置窗口图标
        self.geometry(f"600x600+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        toolmenu_frame = tk.Frame(self)
        toolmenu_frame.grid(row=0, column=0, sticky='ew')
        
        self.image = None
        self.format = format
        self.pixelformat = None
        self.insideformat = None
        
        image_frame = tk.Frame(self)        
        image_frame.grid(row=1, column=0, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, minsize=30)
        
        
        self.iv = ImgGLFrame(image_frame)
        self.iv.pack(fill=tk.BOTH, expand=True)
    
        imgscommbox = ttk.Combobox(toolmenu_frame, state="readonly", values=[key for key, value in module.parameters.items() if isinstance(value, np.ndarray)], width=6)
        imgscommbox.grid(row=0, column=0, padx=2, pady=1,sticky='w')
        imgscommbox.bind("<<ComboboxSelected>>", lambda event: self.changecurrentimage(module.parameters[imgscommbox.get()]))
        tk.Button(toolmenu_frame, text="Save",command=lambda: self.save_image()).grid(row=0, column=1, padx=0, pady=1,sticky='w')
        
        self.label = tk.Label(toolmenu_frame, text="Min-Max:")
        
        self.minscale = tk.Scale(toolmenu_frame,state='disabled',from_=-10,to=10,variable=self.minscalevalue,orient=tk.HORIZONTAL,resolution=0.01,troughcolor="gray", sliderrelief=tk.RAISED, activebackground="blue", font=("Arial", 10))
        
        self.maxscale = tk.Scale(toolmenu_frame,state='disabled',from_=-10,to=10,variable=self.maxscalevalue,orient=tk.HORIZONTAL,resolution=0.01,troughcolor="gray", sliderrelief=tk.RAISED, activebackground="red", font=("Arial", 10))
        
        
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
    def changecurrentimage(self,img:np.ndarray):
        if img is not None:
            if img.ndim == 2 or (img.ndim == 3 and img.shape[2] == 1) :
                if img.dtype == np.float32:
                    self.format = GL_R32F
                    self.insideformat = GL_RED
                    self.pixelformat = GL_FLOAT
                else:
                    self.format = GL_LUMINANCE
                    self.insideformat = GL_LUMINANCE
                    self.pixelformat =GL_UNSIGNED_BYTE
            elif img.ndim == 3 and img.shape[2] == 3 and img.dtype == np.uint8:
                self.format = GL_BGRA
                self.insideformat = GL_BGRA
                self.pixelformat =GL_UNSIGNED_BYTE
            elif img.ndim == 3 and img.shape[2] == 4 and img.dtype == np.uint8:
                self.format = GL_BGRA
                self.insideformat = GL_BGRA
                self.pixelformat =GL_UNSIGNED_BYTE
            else:
                self.lastrunstatus = False
                self.breifimage = None
                self.statuscolor = [1.0, 0.0, 0.0]
            self.image = img
            self.on_load()
    def on_load(self):
        self.iv.load_texture(self.image.shape[1], self.image.shape[0], self.image, self.format ,self.insideformat,self.pixelformat)
        if self.format == GL_R32F:
            self.label.grid(row=1, column=0, padx=5, pady=1)
            self.minscale.grid(row=1, column=1, padx=0, pady=1)
            self.maxscale.grid(row=1, column=2, padx=0, pady=1)
            self.minscale.configure(state='normal',from_=self.iv.minvalue, to=self.iv.maxvalue)
            self.maxscale.configure(state='normal',from_=self.iv.minvalue, to=self.iv.maxvalue)
            self.minscalevalue.set(self.iv.minvalue)
            self.maxscalevalue.set(self.iv.maxvalue)
            self.minscalevalue.trace_add("write", lambda *args: self.iv.set_minv(self.minscalevalue.get()))  # 绑定变量变化事件
            self.maxscalevalue.trace_add("write", lambda *args: self.iv.set_maxv(self.maxscalevalue.get()))  # 绑定变量变化事件
        else:
            self.label.grid_forget()
            self.minscale.grid_forget()
            self.maxscale.grid_forget()

    def on_window_close(self):
        self.destroy()
        del self
    def save_image(self):
        """保存图像到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.iv.tkMakeCurrent()  # 确保OpenGL上下文正确
                screenshotpixels= glReadPixels(0, 0, self.iv.width, self.iv.height, GL_BGR, GL_UNSIGNED_BYTE)
                cv2.imwrite(file_path, np.flipud(np.frombuffer(screenshotpixels, dtype=np.uint8).reshape(self.iv.height, self.iv.width, 3)))
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {e}")
class NumericInputPad:
    def __init__(self, parent, message=None):
        
        window = tk.Toplevel(parent)
        windowx = parent.winfo_rootx()+parent.winfo_width() - 370
        windowy = parent.winfo_rooty()+parent.winfo_height() - 500
        window.geometry(f"360x480+{windowx}+{windowy}")      

        self.root = window
        self.root.title("NumericInputPad")
        self.root.resizable(False, False)
        self.root.configure(bg="#f5f5f5")
        
        self.message = message
        
        # 自定义字体
        self.display_font = tkfont.Font(family="Arial", size=28, weight="bold")
        self.button_font = tkfont.Font(family="Arial", size=18)
        self.special_button_font = tkfont.Font(family="Arial", size=14)
        
        # 显示区域
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        self.display = tk.Entry(
            self.root,
            textvariable=self.display_var,
            font=self.display_font,
            bd=2,
            relief=tk.FLAT,
            bg="#ffffff",
            fg="#333333",
            justify="right",
            insertwidth=0,
            readonlybackground="#ffffff",
        )
        self.display.grid(row=0, column=0, columnspan=4, padx=15, pady=(20, 15), ipady=12, sticky="ew")
        
        # 按钮样式配置
        self.button_config = {
            "font": self.button_font,
            "bd": 0,
            "relief": tk.RAISED,
            "height": 1,
            "width": 4,
            "activebackground": "#e0e0e0",
            "highlightthickness": 0,
            "highlightbackground": "#cccccc"
        }
        
        # 数字按钮布局
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
            ('0', 4, 1), ('.', 4, 2), ('-', 4, 0),
            ('⌫', 1, 3), ('C', 2, 3), ('确定', 3, 3, 2)
        ]
        
        # 创建按钮
        for button_info in buttons:
            text = button_info[0]
            row = button_info[1]
            col = button_info[2]
            rowspan = button_info[3] if len(button_info) > 3 else 1
            
            btn_style = self.button_config.copy()
            
            if text.isdigit():
                btn_style.update({"bg": "#ffffff", "fg": "#333333"})
            elif text in ['.', '-']:
                btn_style.update({"bg": "#f0f0f0", "fg": "#666666"})
            else:
                if text == '确定':
                    btn_style.update({
                        "bg": "#4CAF50", 
                        "fg": "white", 
                        "font": self.special_button_font,
                        "height": 3
                    })
                else:
                    btn_style.update({
                        "bg": "#e0e0e0", 
                        "fg": "#333333",
                        "font": self.special_button_font
                    })
            
            button = tk.Button(self.root, text=text, **btn_style)
            
            if rowspan > 1:
                button.grid(row=row, column=col, rowspan=rowspan, padx=5, pady=5, sticky="nswe")
            else:
                button.grid(row=row, column=col, padx=5, pady=5)
            
            button.bind("<Button-1>", lambda e, t=text: self.on_button_click(t))
        
        # 配置网格布局权重
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        
        # 初始化输入状态
        self.current_input = "0"
        self.has_decimal = False
    
    def on_button_click(self, button_text):
        if button_text.isdigit():
            self.process_digit(button_text)
        elif button_text == '.':
            self.process_decimal()
        elif button_text == '-':
            self.process_sign()
        elif button_text == '⌫':
            self.process_backspace()
        elif button_text == 'C':
            self.process_clear()
        elif button_text == '确定':
            self.process_confirm()
    
    def process_digit(self, digit):
        if self.current_input == "0":
            self.current_input = digit
        elif self.current_input == "-0":
            self.current_input = "-" + digit
        else:
            self.current_input += digit
        self.update_display()
    
    def process_decimal(self):
        if not self.has_decimal:
            # 如果当前是"0"或"-0"，在添加小数点前不需要保留0
            if self.current_input == "0":
                self.current_input = "0."
            elif self.current_input == "-0":
                self.current_input = "-0."
            else:
                self.current_input += '.'
            self.has_decimal = True
            self.update_display()
    
    def process_sign(self):
        if self.current_input.startswith('-'):
            self.current_input = self.current_input[1:]
        else:
            if self.current_input != "0":
                self.current_input = '-' + self.current_input
        self.update_display()
    
    def process_backspace(self):
        if len(self.current_input) > 1:
            # 检查是否删除了小数点
            if self.current_input[-1] == '.':
                self.has_decimal = False
            self.current_input = self.current_input[:-1]
            
            # 处理删除负号后的情况
            if self.current_input == "-":
                self.current_input = "0"
        else:
            self.current_input = "0"
            self.has_decimal = False
        
        self.update_display()
    
    def process_clear(self):
        self.current_input = "0"
        self.has_decimal = False
        self.update_display()
    
    def process_confirm(self):
        if self.message is None:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_input)
            messagebox.showinfo("Copy!", "Copied to clipboard!")
            self.root.destroy()  # 关闭数字键盘窗口   
            return
        else:
            self.message(self.current_input)
        self.root.destroy()  # 关闭数字键盘窗口
    def update_display(self):
        # 确保显示格式正确
        display_text = self.current_input
        
        # 处理".x"显示为"0.x"的情况
        if display_text.startswith('.') or (display_text.startswith('-') and display_text[1] == '.'):
            if display_text.startswith('-'):
                display_text = "-0" + display_text[1:]
            else:
                display_text = "0" + display_text
        
        # 处理只有负号的情况
        if display_text == "-":
            display_text = "-0"
        
        # 处理"-0"后面跟着数字的情况
        if display_text.startswith("-0") and len(display_text) > 2 and display_text[2] != '.':
            display_text = "-" + display_text[2:]
        
        # 更新显示和内部状态
        self.display_var.set(display_text)
        self.current_input = display_text
class LangCombo:
    def __init__(self,parent,defultlange,callback = None):
        self.langselector = ttk.Combobox(parent, state="readonly",values=['zh','en'], width=6)
        self.langselector.set(defultlange)
        self.langselector.pack(side='right', anchor='ne', padx=0, pady=0)
        self.langselector.bind("<<ComboboxSelected>>", callback)
    @classmethod
    def show(cls, parent, defultlange, callback=None):
        """显示语言选择窗口"""
        cls.instance = cls(parent, defultlange, callback)
        return cls.instance.langselector
class PlaceholderEntry(ttk.Frame):
    """
    一个带提示文字的输入框组件（基于Frame封装）
    - 支持 placeholder 提示
    - 支持 ttk 样式
    - 提供 get()/set() 方法操作文本
    """
    def __init__(self, master, placeholder="", **kwargs):
        super().__init__(master)
        
        # 默认配置
        self.placeholder = placeholder
        self.entry_var = tk.StringVar()
        
        # 创建 ttk 样式
        self.style = ttk.Style()
        self.style.configure("Placeholder.TEntry", foreground="grey")
        self.style.configure("Normal.TEntry", foreground="black")
        
        # 创建输入框
        self.entry = ttk.Entry(
            self,
            textvariable=self.entry_var,
            style="Placeholder.TEntry",
            **kwargs
        )
        self.entry.pack(fill="both", expand=True)
        
        # 初始化提示文字
        self._show_placeholder()
        
        # 绑定事件
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)
    
    def _show_placeholder(self):
        """显示提示文字"""
        self.entry_var.set(self.placeholder)
        self.entry.config(style="Placeholder.TEntry")
    
    def _hide_placeholder(self):
        """隐藏提示文字"""
        if self.entry_var.get() == self.placeholder:
            self.entry_var.set("")
        self.entry.config(style="Normal.TEntry")
    
    def _on_focus_in(self, event):
        """获得焦点时隐藏提示"""
        if self.entry_var.get() == self.placeholder:
            self._hide_placeholder()
    
    def _on_focus_out(self, event):
        """失去焦点时显示提示（如果内容为空）"""
        if not self.entry_var.get():
            self._show_placeholder()
    
    def get(self):
        """获取输入内容（自动过滤提示文字）"""
        text = self.entry_var.get()
        return text
    
    def set(self, text):
        """设置输入内容"""
        self.entry_var.set(text)
        self.entry.config(style="Normal.TEntry")
class FlowPlane(OpenGLFrame):
    def __init__(self, *args, **kwargs):
        print("FlowPlane init")
        super().__init__(*args, **kwargs)
        # 语言设置
        self.language = 'zh'
        # 外观设置
        self.background_color = [0.11, 0.13, 0.22, 1.0]
        self.drawobjects = {}
        self.selectobjects = []
        # 部件初始化
        self.infolabel = tk.Label(self, text="Information", bg="black", fg="white")
        self.infolabel.pack(side='left',anchor='nw', padx=0, pady=0)
        self.infolabel.bind("<Double-Button-1>", self.copy_to_clipboard)
        # 动画使能
        self.animate = True
        # 窗口大小
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        # 缩放和位置变量
        self.scale = 1.0
        self.min_scale = 0.01
        self.max_scale = 100.0
        self.offset_x = 0#self.width / 2
        self.offset_y = 0#self.height / 2
        self.rotation_angle = 0  # 旋转角度（弧度）       
        # 鼠标跟踪
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_mouse_x = 0
        self.current_mouse_y = 0
        self.curent_img_x = 0
        self.curent_img_y = 0
        self.dragging = False     
        # 绑定事件
        self.bind("<Motion>", self.on_mouse_move)  # 鼠标移动事件
        self.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.bind("<Button-4>", self.on_mouse_wheel)    # Linux上滚
        self.bind("<Button-5>", self.on_mouse_wheel)    # Linux下滚
        self.bind("<ButtonPress-3>", self.on_button3_press) # 右键按下事件
        self.bind("<ButtonPress-2>", self.on_button2_press) # 中键按下事件
        self.bind("<B3-Motion>", self.on_mouseright_drag) # 右键拖动事件
        self.bind("<ButtonRelease-3>", self.on_button3_release) # 右键释放事件
        self.bind("<Button-1>", self.on_mouseleft_click)  # 左键单击事件
        self.bind("<Double-Button-1>", self.on_mouseleftdouble_click) # 左键双击事件
        self.bind("<Double-Button-3>", self.on_mouselrightdouble_click) # 右键双击事件

        self.bind("<Configure>", self.on_resize) # 窗口大小变化事件
        self.bind("<F5>", self.on_f5)  # F5键事件
        self.bind("<F11>", self.on_f11)
        self.bind("<Delete>", self.on_delete)  # Delete键事件
        # 上下文菜单字典
        self.texts = {
            'zh':{
                'update_drawobjects_msg_title': "更新模块",
                'update_drawobjects_msg_content': "模块已存在，是否覆盖？",
                'update_drawobjects_msg_error': "模块名称不能为空。",
                'on_confirmbuttonclick_errormsg_title': "错误",
                'on_confirmbuttonclick_errormsg_content': "设置输入失败，请检查参数。",
                'module': "模块",
                'langeuage': "语言",
                'setting': "设置",
                'link': "链接",
                'basicline': "链接",
                'ifline': "条件分支",
                'script': "脚本",
                'tool': '工具',
                'calculator': "计算器",
                'numberkeyboard': "数字键盘",
                'imageviewer': "图像查看器",
                'defaulttask': "默认任务",
                'save': "保存任务",
            },
            'en':{
                'update_drawobjects_msg_title': "Update Module",
                'update_drawobjects_msg_content': "Module already exists. Overwrite?",
                'update_drawobjects_msg_error': "Module name cannot be empty.",
                'on_confirmbuttonclick_errormsg_title': "Error",
                'on_confirmbuttonclick_errormsg_content': "Failed to set input, please check parameters.",
                'module': "Module",
                'langeuage': "Language",
                'setting': "Settings",
                'link': "Link",
                'basicline': "Basic Line",
                'ifline': "If Line",
                'script': "Script",
                'tool': 'Tool',
                'calculator': "Calculator",
                'numberkeyboard': "Numeric Pad",
                'imageviewer': "Image Viewer",
                'defaulttask': "Default Task",
                'save': "Save Task",
            }
        }
        # 上下文菜单
        self.context_menu = tk.Menu(self,tearoff=0)
        
        self.setting_menu = tk.Menu(self.context_menu, tearoff=0)
        self.module_menu = tk.Menu(self.context_menu, tearoff=0)
        #self.link_menu = tk.Menu(self.context_menu, tearoff=0)
        self.tool_menu = tk.Menu(self.context_menu, tearoff=0)
                
        self.setting_menu.add_cascade(label=self.texts[self.language]['langeuage'],command=lambda: LangCombo.show(self,defultlange=self.language,callback=self.on_language_change))  
        self.setting_menu.add_cascade(label=self.texts[self.language]['defaulttask'],command=lambda :self.load_task())  # 添加默认任务加载
        self.setting_menu.add_cascade(label=self.texts[self.language]['save'], command=lambda :self.save_task())  # 添加保存任务
        
        self.tool_menu.add_cascade(label=self.texts[self.language]['numberkeyboard'], command=lambda : NumericInputPad(self))  # 添加计算器工具
        self.tool_menu.add_cascade(label=self.texts[self.language]['imageviewer'],accelerator="F11", command=lambda : self.on_f11(None))  # 添加图像查看器工具
        
        #self.link_menu.add_cascade(label=self.texts[self.language]['basicline'], command=lambda : self.update_drawobjects(Grpahics_WrapLineModule.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language]['basicline'],message=self.on_message)))
        #self.link_menu.add_cascade(label=self.texts[self.language]['ifline'], command=lambda : self.update_drawobjects(Grpahics_WrapIfLineModule.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language]['ifline'],message=self.on_message)))  
            
        self.module_menu.add_cascade(label=self.texts[self.language]['script'], command=lambda :self.on_addscript())
        
        
        self.context_menu.add_cascade(label=self.texts[self.language]['setting'], menu=self.setting_menu)
        self.context_menu.add_cascade(label=self.texts[self.language]['module'], menu=self.module_menu)        
        #self.context_menu.add_cascade(label=self.texts[self.language]['link'], menu=self.link_menu)
        self.context_menu.add_cascade(label=self.texts[self.language]['tool'], menu=self.tool_menu)
        self.menulist = []
        self.ini_module()  # 初始化模块
    def save_task(self):
        """保存当前任务到文件"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".flp",
            filetypes=[("FlowTask files", "*.flp"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    data={
                        'language': self.language,
                        'background_color': self.background_color,
                        'scale': self.scale,
                        'offset_x': self.offset_x,
                        'offset_y': self.offset_y,
                        'rotation_angle': self.rotation_angle,
                        'modlues': {key: obj.get_json_data() for key, obj in self.drawobjects.items() if not obj.linemodule},
                        'linemodules': {key: obj.get_json_data() for key, obj in self.drawobjects.items() if obj.linemodule},
                        'texts': self.texts                 
                    }
                    json.dump(data, f, ensure_ascii=False, indent=4)                    
            except Exception as e:
                self.drawobjects.clear()  # 清空现有模块
                messagebox.showerror("Error", f"Failed to save task: {e}")
    def load_task(self,defult_path=None):
        """从文件加载任务"""
        if defult_path is None:
            file_path = filedialog.askopenfilename(
                title="Open Task File",
                filetypes=[("FlowTask files", "*.flp"), ("All files", "*.*")]
            )
        file_path = defult_path
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.language = data.get('language', 'zh')
                self.background_color = data.get('background_color', [0.11, 0.13, 0.22, 1.0])
                self.scale = data.get('scale', 1.0)
                self.offset_x = data.get('offset_x', 0)
                self.offset_y = data.get('offset_y', 0)
                self.rotation_angle = data.get('rotation_angle', 0)
                #self.texts = data.get('texts', self.texts)
                
                # 清空现有模块
                self.drawobjects.clear()
                
                # 加载模块
                for key, module_data in data.get('modlues', {}).items():
                    module_class = getattr(sys.modules[module_data['class']], module_data['class'])
                    module_instance = module_class.from_json(module_data)
                    module_instance.message = self.on_message   
                    module_instance.get_image()
                    self.update_drawobjects(module_instance)
                
                # 加载连线模块
                for key, module_data in data.get('linemodules', {}).items():
                    module_class = getattr(sys.modules[module_data['class']], module_data['class'])
                    module_instance = module_class.from_json(module_data,self.drawobjects)
                    module_instance.message = self.on_message   
                    self.update_drawobjects(module_instance)             
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load task: {e}")
    def on_addscript(self):
        file_path = filedialog.askopenfilename(
            title="Open Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(f'{module_name}', file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            my_class = getattr(module, module_name)()
            rawname = getattr(my_class, 'rawname')
            zhname = getattr(my_class,'zhname')
            enname = getattr(my_class,'enname')
            self.texts['zh'][rawname] = zhname
            self.texts['en'][rawname] = enname
            self.update_drawobjects(my_class.from_userdefined(self,self.curent_img_x,self.curent_img_y,name=self.texts[self.language][rawname],message=self.on_message))
            # 这里可以添加后续处理代码，比如显示内容或进一步操作
    def load_module(self,directory):
        def get_directory_tree_with_depth(directory, target_depth=None):
            """
            获取目录树，并记录每个节点的深度
            :param directory: 目标目录路径
            :param target_depth: 可选，指定要返回的层级深度（从0开始）
            :return: 
                - 如果未指定 target_depth: 返回完整树形结构 + 各节点深度字典
                - 如果指定 target_depth: 返回该层级的所有目录和文件
            """
            tree = {}
            depth_info = {}  # 记录各层级的深度信息

            for root, dirs, files in os.walk(directory):
                # 计算当前深度（根目录为0）
                rel_path = os.path.relpath(root, directory)
                current_depth = 0 if rel_path == "." else len(rel_path.split(os.sep))

                # 如果指定了 target_depth，只收集目标层级的数据
                if target_depth is not None and current_depth != target_depth:
                    continue
                
                # 构建当前层级的树结构
                current_level = tree
                if rel_path != ".":
                    for part in rel_path.split(os.sep):
                        current_level = current_level.setdefault(part, {})

                # 添加文件和子目录
                current_level["_files"] = files
                current_level["_depth"] = current_depth  # 记录深度
                for dir_name in dirs:
                    current_level[dir_name] = {}

                # 记录深度信息（用于按深度索引）
                if current_depth not in depth_info:
                    depth_info[current_depth] = []
                depth_info[current_depth].append({
                    "path": root,
                    "dirs": dirs,
                    "files": files
                })

            # 返回结果
            if target_depth is not None:
                return depth_info.get(target_depth, [])
            else:
                return {
                    "tree": tree,          # 完整树形结构
                    "depth_info": depth_info  # 按深度分组的节点信息
                }
        trees = get_directory_tree_with_depth(directory)   
        menus=[]
        for key,items in trees['depth_info'].items():
            for index,item in enumerate(items):
                files = item['files']
                depth=int(key)
                if '__init__.py' in files:
                    with open(os.path.join(item['path'], '__init__.py'), 'r', encoding='utf-8') as f:
                        content = f.read()
                        name = None
                        try:
                            match = re.search(r'name\s*=\s*({.*?})', content, re.DOTALL)
                            if match:
                                name_dict = eval(match.group(1))
                                name = name_dict
                        except Exception as e:
                                name = None
                        if name :
                            self.texts['zh'][name['rawname']] = name['zh']
                            self.texts['en'][name['rawname']] = name['en']

                            if depth==0:
                                rootmenu = tk.Menu(self.module_menu, tearoff=0)
                                menus.append([name['rawname'],rootmenu,[],self.module_menu,1+len(self.menulist)])
                                self.module_menu.add_cascade(label=self.texts[self.language][name['rawname']], menu=rootmenu)
                            else:
                                cacademenu = tk.Menu(menus[depth-1][1], tearoff=0)
                                menus.append([name['rawname'],cacademenu,[],menus[depth-1][1],index])
                                menus[depth-1][1].add_cascade(label=self.texts[self.language][name['rawname']], menu=cacademenu)
                    pys=[]
                    for file in files:
                        if file.endswith('.py') and file != '__init__.py':
                            file_path = os.path.join(item['path'], file)
                            module_name = os.path.splitext(os.path.basename(file_path))[0]
                            spec = importlib.util.spec_from_file_location(f'{module_name}', file_path)
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module  # 将模块添加到系统模块中
                            spec.loader.exec_module(module)
                            my_class = getattr(module, module_name)
                            rawname = getattr(my_class, 'rawname')
                            zhname = getattr(my_class,'zhname')
                            enname = getattr(my_class,'enname')
                            self.texts['zh'][rawname] = zhname
                            self.texts['en'][rawname] = enname
                            
                            menus[-1][1].add_cascade(label=self.texts[self.language][rawname],command=lambda cls=my_class: self.update_drawobjects(cls.from_userdefined(self, self.curent_img_x, self.curent_img_y,name=cls.rawname,message=self.on_message)))
                            
                            pys.append(rawname)
                    menus[-1][2] = pys 
        self.menulist.append(menus)
    def ini_module(self):
        directory = os.path.join(os.getcwd(), 'mossflow','mossmodlues')  # 拼接模块目录路径
       
        #print("Current file path:", current_file_path)
        #directory = filedialog.askdirectory(title="Select Module Directory")    
        if directory:
            for path in os.listdir(directory):
                self.load_module(os.path.join(directory, path))
            self.load_task(os.path.join(directory, 'defult.flp'))  # 加载默认任务文件
    def on_language_change(self,event):
        """语言切换"""
        after_lang=event.widget.get()
        self.language = after_lang  # 获取当前选择的语言

        for obj in self.drawobjects.values():
            if hasattr(obj, "language"):
                obj.language=after_lang
        event.widget.destroy()  # 销毁语言选择组件
        
        self.context_menu.entryconfig(0, label=self.texts[self.language]['setting'])
        self.context_menu.entryconfig(1, label=self.texts[self.language]['module'])
        #self.context_menu.entryconfig(2, label=self.texts[self.language]['link'])   
        self.context_menu.entryconfig(2, label=self.texts[self.language]['tool'])
        
        self.tool_menu.entryconfig(0, label=self.texts[self.language]['numberkeyboard'])
        self.tool_menu.entryconfig(1, label=self.texts[self.language]['imageviewer'])
        
        self.setting_menu.entryconfig(0, label=self.texts[self.language]['langeuage'])
        self.setting_menu.entryconfig(1, label=self.texts[self.language]['defaulttask'])
        self.setting_menu.entryconfig(2, label=self.texts[self.language]['save'])
        
        self.module_menu.entryconfig(0, label=self.texts[self.language]['script'])

        
        #self.link_menu.entryconfig(0, label=self.texts[self.language]['basicline'])
        #self.link_menu.entryconfig(1, label=self.texts[self.language]['ifline'])

        for menus in self.menulist:
            for menu in menus:
                for i in range(len(menu[2])):
                    if menu[2][i] in self.texts[self.language]:
                        menu[1].entryconfig(i, label=self.texts[self.language][menu[2][i]])
                menu[3].entryconfig(menu[4], label=self.texts[self.language][menu[0]])    
                print(menu[3].entrycget(menu[4], "label"))                     
    def update_drawobjects(self,module):
        """更新绘图对象"""
        keys = list(self.drawobjects.keys())
        if module.text in keys:
            if not messagebox.askyesno(self.texts[self.language]['update_drawobjects_msg_title'], self.texts[self.language]['update_drawobjects_msg_content']):
                return
            # If user selects Yes, allow overwrite (do nothing here, will overwrite below)
        else:
            if module.text == "":
                messagebox.showerror(self.texts[self.language]['update_drawobjects_msg_title'], self.texts[self.language]['update_drawobjects_msg_error'])
                return
        self.drawobjects[module.text] = module   
        #module.show_parameter_page(module.x,module.y,self)  
    # region Gobal Functions
    def on_message(self,module,operationcode:int,**kwargs):
        def on_objectselection(event):
            selected_index = modulecombo.current()
            if selected_index != -1:
                paramcombo['values'] = list(self.drawobjects[modulecombo.get()].parameters.keys())  # 更新输出选项
        def on_outputselection(event):
            pass
        def on_confirmbuttonclick(event):
            try:           
                selected_index = modulecombo.current()
                if selected_index != -1 and operationcode == 1:
                    paramname= kwargs['paramname']
                    keyname = kwargs['keyname']
                    setattr(module, paramname,self.drawobjects[modulecombo.get()]) # 赋值模块
                    setattr(module, keyname,paramcombo.get()) # 赋值模块
                    
                    kwargs['button'].config(text=f"{paramname}:   {getattr(module,paramname).text}\n    {gstr(getattr(module,keyname))}")  # 更新按钮文本
                    
                    window.destroy()
            except Exception as e:
                messagebox.showerror(self.texts['on_confirmbuttonclick_errormsg_title'], self.texts['on_confirmbuttonclick_errormsg_content'] + f"\n{e}")
        # 删除模块
        if operationcode == -1:
            del self.drawobjects[module.text]
            del module
            return
        # 修改模块名称
        if operationcode == -2:
            first_key = next((k for k, v in self.drawobjects.items() if v == module), None)
            self.drawobjects[module.text] = self.drawobjects.pop(first_key)  # 取出旧键值并赋给新键
            return
        if operationcode == 3:
            module.load(self.drawobjects)
            return
        elif operationcode == 1:
            pass
        window= tk.Toplevel(self)
        window.iconbitmap(iconp)  # 设置窗口图标
        l1=getattr(sys.modules['Grpahics_WrapIfLineModule'],'Grpahics_WrapIfLineModule')
        l2=getattr(sys.modules['Grpahics_WrapLineModule'],'Grpahics_WrapLineModule')
        modulecombo = ttk.Combobox(window, values=[key for key in self.drawobjects.keys() if not isinstance(self.drawobjects[key], (l1,l2))], state="readonly")
        modulecombo.bind("<<ComboboxSelected>>", on_objectselection)  # 绑定选择事件
        modulecombo.grid(column=0,row=0,pady=1)
        paramcombo = ttk.Combobox(window)
        paramcombo.bind("<<ComboboxSelected>>", on_outputselection)  # 绑定选择事件
        paramcombo.grid(column=0,row=1,pady=1)        
        confirmbutton = tk.Button(window, text="Confirm")
        confirmbutton.bind("<Button-1>", on_confirmbuttonclick)  # 绑定单击事件
        confirmbutton.grid(column=0,row=2,pady=1)
    def copy_to_clipboard(self,evetn):
        # 清空剪切板并复制标签内容
        self.clipboard_clear()
        self.clipboard_append(self.infolabel.cget("text"))
        messagebox.showinfo("Copy!", "Copied to clipboard!")
    # endregion
    # region GL functions
    def on_resize(self, event):
        try:
            self.tkMakeCurrent()
            self.width = event.width
            self.height = event.height

            # 防止初始化为0大小
            if self.width < 1 or self.height < 1:
                self.width, self.height = 800, 800
            glViewport(0, 0, self.width, self.height)
        except Exception as e:
            pass
        # version = glGetString(GL_VERSION)
        # if version:
        #     try:
        #         glViewport(0, 0, self.width, self.height)
        #     except Exception as e:
        #         messagebox.askquestion('Error',f"Error updating viewport: {e}", icon='error')
    def initgl(self):
        """初始化OpenGL和加载纹理"""
        self.tkMakeCurrent()
        glClearColor(self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3])
    def redraw(self):
        """渲染纹理四边形"""
        self.tkMakeCurrent()
        glUseProgram(0)  # 禁用着色器程序
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(self.background_color[0], self.background_color[1], self.background_color[2], self.background_color[3])

        if True:            
            # 设置投影矩阵
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(-self.width/2, self.width/2, self.height/2, -self.height/2,-1,1)
            
            # 设置模型视图矩阵
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # 应用缩放和平移
            glTranslatef(self.offset_x,self.offset_y, 0)
            glScalef(self.scale, self.scale, 1)
            glRotatef(self.rotation_angle*(180/pi), 0, 0, 1)
            keys = list(self.drawobjects.keys())
            for i,key in enumerate(keys):
                self.drawobjects[key].GLDraw()
            glColor3f(1.0, 1.0, 1.0)

    # endregion
    # region Mouse Event
    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y
        imgpos= self.WindowPos2GLPos(self.current_mouse_x, self.current_mouse_y)
        self.curent_img_x = imgpos[0]
        self.curent_img_y = imgpos[1]
        #self.infolabel.config(text= f"GLPosition {self.curent_img_x:.2f}, {self.curent_img_y:.2f},\nScale: {self.scale:.2f}, \nOffset: ({self.offset_x:.2f}, {self.offset_y:.2f})")
    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 确定缩放方向
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # 上滚/放大
            zoom_factor = 1.1
        else:  # 下滚/缩小
            zoom_factor = 0.9
        
        # 应用缩放限制
        new_scale = self.scale * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        
        self.scale = new_scale
        self.redraw() 
    def on_button3_press(self, event):
        """开始拖动"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.dragging = True
    def on_button2_press(self, event):
        self.tkMakeCurrent()
        glViewport(0, 0, self.width, self.height)
        self.reset_view()
        self.redraw()
    def on_mouseright_drag(self, event):
        """处理拖动"""
        if self.dragging and len(self.selectobjects)== 0:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            
            self.offset_x += dx
            self.offset_y += dy

            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.redraw()
        if self.dragging and len(self.selectobjects) > 0:
            lastglx,lastgly= self.WindowPos2GLPos(self.last_mouse_x, self.last_mouse_y)
            curglx,curgly= self.WindowPos2GLPos(event.x, event.y)
            for i in range(len(self.selectobjects)):
                self.selectobjects[i].x += curglx - lastglx
                self.selectobjects[i].y += curgly - lastgly
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.redraw()
    def on_mouseleft_click(self,event):
        """处理左键单击事件"""
        self.focus_force()
        # 获取鼠标在窗口中的位置
        mouse_x = event.x
        mouse_y = event.y
        keys = list(self.drawobjects.keys())
        for i,key in enumerate(keys):
            self.drawobjects[key].status = 'Normal'
        self.selectobjects.clear()
        # 计算鼠标在图片坐标系中的位置
        mouse_x_imgsystem,mouse_y_imgsystem= self.WindowPos2GLPos(mouse_x, mouse_y)
        for i,key in enumerate(keys):
            tryselectobjs= self.drawobjects[key].contains(mouse_x_imgsystem, mouse_y_imgsystem)
            if tryselectobjs is not None: 
                if isinstance(tryselectobjs, list):
                    self.selectobjects.extend(tryselectobjs)
                else:
                    self.selectobjects.append(tryselectobjs)
                self.infolabel.config(text= tryselectobjs.moudlestatus)
                break
            else:
                self.drawobjects[key].status = 'Normal'
        self.redraw()       
    def on_button3_release(self, event):
        """结束拖动"""
        self.dragging = False
    def on_mouseleftdouble_click(self,event):
        """处理左键双击事件"""
        # 打开上下文菜单
        # 获取鼠标在窗口中的位置
        mouse_x = event.x
        mouse_y = event.y
        keys = list(self.drawobjects.keys())
        for i,key in enumerate(keys):
            self.drawobjects[key].status = 'Normal'
        self.selectobjects.clear()
        # 计算鼠标在图片坐标系中的位置
        mouse_x_imgsystem,mouse_y_imgsystem= self.WindowPos2GLPos(mouse_x, mouse_y)
        for i,key in enumerate(keys):
            self.drawobjects[key].show_parameter_page(mouse_x_imgsystem, mouse_y_imgsystem,self)    
    def on_mouselrightdouble_click(self,event):
        """处理右键双击事件"""
        # 打开上下文菜单
        
        self.context_menu.post(event.x_root, event.y_root)    
    # endregion
    # region Keyboard Event
    def on_f5(self,event):
        """处理F5键事件"""
        if len(self.selectobjects)>0:
            for i in range(len(self.selectobjects)):
                self.selectobjects[i].run()
                self.infolabel.config(text= self.selectobjects[i].moudlestatus)
    def on_f11(self,event):
        iv=ImgViewer(self,self.selectobjects[0])
        #iv.after(200, iv.on_load)  # 确保在窗口显示后重绘
    def on_delete(self,event):
        """处理Delete键事件"""
        if len(self.selectobjects)>0:
            if tk.messagebox.askokcancel("Delete", "Are you sure you want to delete these modules?"):
                for i in range(len(self.selectobjects)):
                    del self.drawobjects[self.selectobjects[i].text]
                    del self.selectobjects[i]
                self.redraw()
    # endregion
    # region View Functions
    def reset_view(self):
        self.scale = 1.0
        self.offset_x = 0#self.width / 2
        self.offset_y = 0#self.height / 2
        self.curent_img_x =0
        self.curent_img_y =0
        self.current_mouse_x =0
        self.current_mouse_y =0
        self.redraw()
    def GLPos2WindowPos(self, x, y):
        """将图片坐标转换为窗口坐标，考虑旋转"""
        affine_matrix = np.array([
        [self.scale * cos(self.rotation_angle), -self.scale * sin(self.rotation_angle), self.offset_x],
        [self.scale * sin(self.rotation_angle), self.scale * cos(self.rotation_angle), self.offset_y],
        [0, 0, 1]])
        point = np.array([x, y, 1])
        transformed_point = np.dot(affine_matrix, point)
        return transformed_point[0]+self.width/2, transformed_point[1]+self.height/2
    def WindowPos2GLPos(self, x, y):
        """将窗口坐标转换为图片坐标，考虑旋转"""
        # 减去偏移
        x = x - self.width/2
        y = y - self.height/2
        affine_matrix = np.array([
        [self.scale * cos(self.rotation_angle), -self.scale * sin(self.rotation_angle), self.offset_x],
        [self.scale * sin(self.rotation_angle), self.scale * cos(self.rotation_angle), self.offset_y],
        [0, 0, 1]])
        point = np.array([x, y, 1])
        affine_matrix_inv=np.linalg.inv(affine_matrix)
        # 反向旋转
        transformed_point = np.dot(affine_matrix_inv, point)
        return transformed_point[0], transformed_point[1]
    # endregion
class ImgGLFrame(OpenGLFrame):
    #顶点着色器
    vertex_shader = """
        #version 330 core
        layout(location = 0) in vec3 position;
        layout(location = 1) in vec2 texCoord;
        uniform mat4 projection;
        uniform mat4 model;
        uniform mat4 view;
        out vec2 vTexCoord;

        void main()
        {
            gl_Position = projection*view*model*vec4(position, 1.0);
            vTexCoord = texCoord;
        }
        """
    #片段着色器
    fragment_shader = """
        #version 330 core
        in vec2 vTexCoord;
        out vec4 fragColor;

        uniform sampler2D textureSampler;
        uniform int texturetype;  // 0: RGB, 1: Luminance
        uniform float minv;  // 最小亮度
        uniform float maxv;  // 最大亮度
        vec3 hsv2rgb(vec3 c) {
            vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
            vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
            return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
        }

        vec3 luminanceToColor(float luminance, float minLuminance, float maxLuminance) 
        {
            float normalizedLuminance = (luminance - minLuminance) / (maxLuminance - minLuminance);
            normalizedLuminance = clamp(1-normalizedLuminance, 0.0, 1.0);

            // 调整Hue范围：0.0（红）→ ~0.8（紫）
            float hue = normalizedLuminance * 0.8; // 限制在红→紫之间
            vec3 hsvColor = vec3(hue, 1.0, 1.0); // 饱和度和亮度设为1
            return hsv2rgb(hsvColor);
        }
        
        void main()
        {
            if (texturetype == 0) 
            {
                fragColor = texture(textureSampler, vTexCoord);  // 直接使用纹理
            } 
            else if (texturetype == 1) 
            {
                float luminance = texture(textureSampler, vTexCoord).r;  // 获取纹理的红色通道作为亮度
                float normalizeluminance = clamp((luminance - minv) / (maxv-minv), 0.0, 1.0);
                if(luminance < minv || luminance > maxv) 
                {
                    fragColor = vec4(0.0, 0.0, 0.0, 1.0);  // 如果亮度不在范围内，设置为黑色
                }
                else 
                {
                    fragColor = vec4(normalizeluminance, normalizeluminance, normalizeluminance, 1.0);  // 将亮度值应用到RGB通道
                }
            }
            else if (texturetype == 2) 
            {
                float luminance = texture(textureSampler, vTexCoord).r;  // 获取纹理的红色通道作为亮度
                vec3 color = luminanceToColor(luminance,minv,maxv);  // 将亮度值转换为颜色
                if(luminance < minv || luminance > maxv) 
                {
                    fragColor = vec4(0.0, 0.0, 0.0, 1.0);  // 如果亮度不在范围内，设置为黑色
                } 
                else 
                {
                    fragColor = vec4(color, 1.0);  // 将颜色应用到输出
                }
            }
        }
        """
    #shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img_texture_data=None
        self.infolabel = tk.Label(self, text="Information", bg="black", fg="white")
        self.infolabel.pack(anchor='nw', padx=10, pady=10)
        self.infolabel.bind("<Double-Button-1>", self.copy_to_clipboard)

        self.texture_id = None

        self.animate = False

        self.width = self.winfo_width()
        self.height = self.winfo_height()
        # 缩放和位置变量
        self.scale = 1.0
        self.min_scale = 0.01
        self.max_scale = 100.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        
        # 鼠标跟踪
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.current_mouse_x = 0
        self.current_mouse_y = 0
        self.curent_img_x = 0
        self.curent_img_y = 0
        self.dragging = False
        
        # 绑定事件
        self.bind("<Motion>", self.on_mouse_move)  # 鼠标移动事件
        self.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.bind("<Button-4>", self.on_mouse_wheel)    # Linux上滚
        self.bind("<Button-5>", self.on_mouse_wheel)    # Linux下滚
        self.bind("<ButtonPress-1>", self.on_button1_press)
        self.bind("<ButtonPress-2>", self.on_button2_press)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<Configure>", self.on_resize)
        self.bind("<Destroy>", self.close)  # 窗口销毁时清除OpenGL资源    
    def initgl(self):
        self.tkMakeCurrent()
        glClearColor(0.2, 0.2, 0.2, 1.0)  
        self.shader =self.create_shader_program()
    #     vertices = np.array([
    #             # 位置    纹理坐标
    #              -100, -100,   0.0,  0.0,   0.0,  # 左下
    #              100,  -100,   0.0,  1.0,   0.0,  # 右下
    #              100,  100,    0.0,  1.0,   1.0,  # 右上
    #              -100,  100,   0.0,  0.0,   1.0   # 左上
    #         ], dtype=np.float32)
        self.indices = np.array([
                0, 1, 2,
                2, 3, 0
            ], dtype=np.uint32)
            # 创建VAO, VBO和EBO
        self.vao = glGenVertexArrays(1)  # 创建顶点数组对象
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)
    #     glBindVertexArray(self.vao)
        
    # # 绑定并设置顶点缓冲
    #     glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    #     glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    # 绑定并设置元素缓冲
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
    
    # # 位置属性
    #     glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
    #     glEnableVertexAttribArray(0)
    
    # # 纹理坐标属性
    #     glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
    #     glEnableVertexAttribArray(1)
    
    # # 解绑VAO
    #     glBindVertexArray(0)
    # 创建纹理
        self.texture_id = glGenTextures(1)
        self.img_height = 8
        self.img_width = 8
        # checkerboard = np.array([
        #     [255, 255, 255, 255, 0, 0, 0, 0],
        #     [255, 255, 255, 255, 0, 0, 0, 0],
        #     [255, 255, 255, 255, 0, 0, 0, 0],
        #     [255, 255, 255, 255, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 255, 255, 255, 255],
        #     [0, 0, 0, 0, 255, 255, 255, 255],
        #     [0, 0, 0, 0, 255, 255, 255, 255],
        #     [0, 0, 0, 0, 255, 255, 255, 255],
        #     ], dtype=np.uint8)
        # glBindTexture(GL_TEXTURE_2D, self.texture_id)   
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE,8,8,0,GL_LUMINANCE, GL_UNSIGNED_BYTE, checkerboard)
        # #glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 8, 8, 0, GL_RED, GL_UNSIGNED_BYTE, checkerboard)
        # glBindTexture(GL_TEXTURE_2D, 0)  # 禁用纹理
            
    def close(self,event):
        """清除OpenGL选项"""
        self.tkMakeCurrent()
        if self.texture_id is not None:
            glDeleteTextures([self.texture_id])
            self.texture_id = None
        if self.vao is not None:
            glDeleteVertexArrays(1, [self.vao])
            self.vao = None
        if self.vbo is not None:
            glDeleteBuffers(1, [self.vbo])
            self.vbo = None
        if self.ebo is not None:
            glDeleteBuffers(1, [self.ebo])
            self.ebo = None
        if self.shader is not None:
            glDeleteProgram(self.shader)
            self.shader = None
    def copy_to_clipboard(self,evetn):
        # 清空剪切板并复制标签内容
        self.clipboard_clear()
        self.clipboard_append(self.infolabel.cget("text"))
        messagebox.showinfo("Copy!", "Copied to clipboard!")
    def on_resize(self, event):
        """处理窗口大小变化"""
        self.tkMakeCurrent()
        self.width = self.winfo_width()
        self.height = self.winfo_height()
        
        # 防止初始化为0大小
        if self.width < 1 or self.height < 1:
            self.width, self.height = 800, 800
        version = glGetString(GL_VERSION)
        if version and hasattr(self, 'shader'):
            try:
                glViewport(0, 0, self.width, self.height)
            except Exception as e:
                messagebox.askquestion('Error',f"Error updating viewport: {e}", icon='error')
    def ortho_matrix(self,left, right, bottom, top, near, far):
        return glm.ortho(left, right, bottom, top, near, far)
    def view_matrix(self):       
        return glm.lookAt(glm.vec3(0, 0, 1),  # 相机位置
                          glm.vec3(0, 0, 0),  # 目标位置
                          glm.vec3(0, 1, 0))
    # 计算模型视图矩阵（平移+缩放）
    def model_matrix(self,offset_x, offset_y, scale):
        modelm= glm.mat4(1.0)  # 单位矩阵
        translation = glm.translate(modelm, glm.vec3( self.offset_x, self.offset_y, 0))  # 平移
        scaling = glm.scale(modelm, glm.vec3(scale, scale, 1))
        return translation*scaling  # 返回平移+缩放后的模型矩阵
    def load_texture(self,width:int,height:int,texture_data:np.ndarray,format,insideformat,pixel_format):
        """加载图片并创建OpenGL纹理"""
        try:
            self.minvalue = 0
            self.maxvalue = 1
            self.tkMakeCurrent()
            if self.shader is None:
                messagebox.askquestion('Error',f"Error creating shader program: {glGetError()}", icon='error')
                return            
            if self.texture_id is not None:
                glDeleteTextures([self.texture_id])
                self.texture_id = None        
            glBindVertexArray(self.vao)  # 绑定VAO
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)  # 绑定VBO
            vertices = np.array([
                # 位置    纹理坐标
                 -width/2, -height/2,   0.0,  0.0,   0.0,  # 左下
                 width/2,  -height/2,   0.0,  1.0,   0.0,  # 右下
                 width/2,  height/2,    0.0,  1.0,   1.0,  # 右上
                 -width/2,  height/2,   0.0,  0.0,   1.0   # 左上
            ], dtype=np.float32)          
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
    
    # 绑定并设置元素缓冲
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_DYNAMIC_DRAW)
    
    # 位置属性
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)
    
    # 纹理坐标属性
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), ctypes.c_void_p(3 * sizeof(GLfloat)))
            glEnableVertexAttribArray(1)
    
    # 解绑VAO
            glBindVertexArray(0)
            if format == GL_R32F:
                textureType = TextureFormat.DepthColor
                vaild_values = texture_data[texture_data > -10000]
                self.maxvalue =  np.max(vaild_values)
                self.minvalue =  np.min(vaild_values)
                glUniform1f(glGetUniformLocation(self.shader, "maxv"), self.maxvalue)  # 设置纹理类型
                glUniform1f(glGetUniformLocation(self.shader, "minv"), self.minvalue)  # 设置纹理类型
            else:
                textureType = TextureFormat.Color
                
            glUniform1i(glGetUniformLocation(self.shader, "texturetype"), textureType.value)  # 设置纹理类型
                  
            self.texture_id = glGenTextures(1)  # 创建纹理ID   
            self.img_width = width
            self.img_height = height

            self.img_texture_data = texture_data
            self.format=format
            self.insideformat = insideformat
            self.pixel_format=pixel_format
            glBindTexture(GL_TEXTURE_2D, self.texture_id)   
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)  # 边缘处理
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexImage2D(GL_TEXTURE_2D, 0, self.format, self.img_width, self.img_height,0, self.insideformat, self.pixel_format, self.img_texture_data)
            glBindTexture(GL_TEXTURE_2D, 0)  # 禁用纹理

            self.on_button2_press(None)  # 重置视图
            
            self.animate = True

        except Exception as e:
            messagebox.askquestion('Error',f"Error updating viewport: {e},\n,{glGetError()}", icon='error')

            self.texture_id = None      
    def set_maxv(self, maxv:float):
        """设置最大亮度值"""
        self.tkMakeCurrent()
        glUseProgram(self.shader)  # 使用着色器程序
        if self.shader is not None:
            glUniform1f(glGetUniformLocation(self.shader, "maxv"), maxv)
            self.redraw()
        glUseProgram(0)  # 禁用着色器程序
    def set_minv(self, minv:float):
        """设置最小亮度值"""
        self.tkMakeCurrent()
        glUseProgram(self.shader)  # 使用着色器程序
        if self.shader is not None:
            glUniform1f(glGetUniformLocation(self.shader, "minv"), minv)
            self.redraw()
        glUseProgram(0)  # 禁用着色器程序
    def create_shader_program(self):
        """创建并编译着色器程序"""
        # 编译着色器
        vertex = compileShader(self.vertex_shader, GL_VERTEX_SHADER)
        fragment = compileShader(self.fragment_shader, GL_FRAGMENT_SHADER)

        # 链接着色器程序
        program = compileProgram(vertex, fragment)

        # 检查链接状态
        if not glGetProgramiv(program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(program).decode()
            print(f"程序链接错误: {error}")
            glDeleteProgram(program)
            return None

        return program        
    def redraw(self):
        """渲染纹理四边形"""
        # wglMakeCurrent(self.winfo_id(), wglCreateContext(self.winfo_id))  # 设置当前上下文
        self.tkMakeCurrent()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.11, 0.13, 0.09, 1.0)
        glUseProgram(self.shader)  # 使用着色器程序

        # 检查程序链接状态
        if self.texture_id:
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"),
                               1, GL_TRUE, np.array((self.ortho_matrix(-self.width/2, self.width/2,self.height/2, -self.height/2, -1, 1))))
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "model"),
                               1, GL_TRUE, np.array(self.model_matrix(self.offset_x,self.offset_y,self.scale)))  # 单位矩阵
            glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"),
                               1, GL_TRUE, np.array(self.view_matrix()))
            # 设置投影矩阵
            # glMatrixMode(GL_PROJECTION)
            # glLoadIdentity()
            # glOrtho(0, self.width, self.height, 0,-1,1)
            
            # # 设置模型视图矩阵
            # glMatrixMode(GL_MODELVIEW)
            # glLoadIdentity()
            
            # # 应用缩放和平移
            # glTranslatef(self.offset_x,self.offset_y, 0)
            # glScalef(self.scale, self.scale, 1)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glUniform1i(glGetUniformLocation(self.shader, "textureSampler"), 0)
            
            glBindVertexArray(self.vao)
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
            
            
            # 绘制纹理四边形
            # glBindTexture(GL_TEXTURE_2D, self.texture_id)
            # glTexImage2D(GL_TEXTURE_2D, 0, self.format, self.img_width, self.img_height,0, self.format, self.pixel_format, self.img_texture_data)
            # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            # glBegin(GL_QUADS)
            # glTexCoord2f(0, 0); glVertex2f(0, 0)
            # glTexCoord2f(1, 0); glVertex2f(self.img_width, 0)
            # glTexCoord2f(1, 1); glVertex2f(self.img_width, self.img_height)
            # glTexCoord2f(0, 1); glVertex2f(0, self.img_height)
            # glEnd()
            
            # # glDisable(GL_TEXTURE_2D)
            # glUseProgram(0)  # 禁用着色器程序
            # glBegin(GL_LINES)
            # glColor3f(1.0, 0.0, 0.0)  # 设置线条颜色为红色 (R,G,B)
            # # 定义线条的两个端点
            # glVertex2f(0, 0)  # 起点 (x1, y1)
            # glVertex2f(0, 100)    # 终点 (x2, y2)
            # glColor3f(0.0, 0.0, 1.0)  # 设置线条颜色为红色 (R,G,B)
            # glVertex2f(0, 0)  # 起点 (x1, y1)
            # glVertex2f(100, 0) 
            # glEnd()
            # glColor3f(1.0, 1.0, 1.0)
    def on_mouse_move(self, event):
        """处理鼠标移动事件"""
        self.current_mouse_x = event.x
        self.current_mouse_y = event.y


        imgpos= self.WindowPos2ImagePos(self.current_mouse_x, self.current_mouse_y)
        self.curent_img_x = imgpos[0]
        self.curent_img_y = imgpos[1]
        if self.img_texture_data is not None:
            self.curent_img_x = 0  if self.curent_img_x> self.img_width-1 or self.curent_img_x<0 else self.curent_img_x
            self.curent_img_y = 0  if self.curent_img_y> self.img_height-1 or self.curent_img_y<0 else self.curent_img_y
            currentvalue= self.img_texture_data[int(self.curent_img_y), int(self.curent_img_x)]
            self.infolabel.config(text= f"CurrentPosition {self.curent_img_x:.2f}, {self.curent_img_y:.2f},\nImageValue {currentvalue}\nScale: {self.scale:.2f}, \nOffset: ({self.offset_x:.2f}, {self.offset_y:.2f})\nSize: ({self.img_width}, {self.img_height})")
    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件"""
        # 获取鼠标在窗口中的位置
        mouse_x = event.x
        mouse_y = event.y
        
        # 计算鼠标在图片坐标系中的位置
        mouse_x_imgsystem,mouse_y_imgsystem= self.WindowPos2ImagePos(mouse_x, mouse_y)
                
        
        # 确定缩放方向
        if event.num == 4 or (hasattr(event, 'delta') and event.delta > 0):  # 上滚/放大
            zoom_factor = 1.1
        else:  # 下滚/缩小
            zoom_factor = 0.9
        
        # 应用缩放限制
        new_scale = self.scale * zoom_factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        self.scale = new_scale
        x,y= self.ImagePos2WindowPos(mouse_x_imgsystem, mouse_y_imgsystem)
        self.offset_x = mouse_x-x + self.offset_x
        self.offset_y = mouse_y-y + self.offset_y
        self.redraw() 
    def on_button1_press(self, event):
        """开始拖动"""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.dragging = True
    def on_button2_press(self, event):
        self.reset_view()
        self.redraw()
    def on_mouse_drag(self, event):
        """处理拖动"""
        if self.dragging:
            dx = event.x - self.last_mouse_x
            dy = event.y - self.last_mouse_y
            self.offset_x += dx
            self.offset_y += dy
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.redraw()
    def reset_view(self):
        if self.width / self.height > 1:
            self.scale = self.height / self.img_height
            self.offset_x = 0
            self.offset_y = 0
            self.curent_img_x =0
            self.curent_img_y =0
            self.current_mouse_x =0
            self.current_mouse_y =0
        else:
            self.scale = self.width / self.img_width
            self.offset_x = 0
            self.offset_y = 0
            self.curent_img_x =0
            self.curent_img_y =0
            self.current_mouse_x =0
            self.current_mouse_y =0
        self.redraw()
    def on_button_release(self, event):
        """结束拖动"""
        self.dragging = False
    def ImagePos2WindowPos(self, x, y):
        """将图片坐标转换为窗口坐标"""
        window_x = (x - self.img_width/2)*self.scale + self.offset_x + self.width/2
        window_y = (y - self.img_height/2)*self.scale + self.offset_y + self.height/2
        return window_x, window_y
    def WindowPos2ImagePos(self, x, y):
        """将窗口坐标转换为图片坐标"""
        image_x = (x-self.width/2 - self.offset_x) / self.scale+self.img_width/2
        image_y = (y-self.height/2 - self.offset_y) / self.scale+self.img_height/2
        return image_x, image_y
class Graphics_ValueModule():
    def __init__(self,x:int=0,y:int=0,name:str='ValueModule',message=None):
        self.linemodule = False
        self.x = x
        self.y = y
        self.radius = 10
        self.text = name
        self.selectdistance = 10
        self.status = 'Normal'
        self.normalcolor = [0.0,0.5,0.5,1.0]
        self.selectedcolor = [1.0, 0.0, 0.0,1.0]
        self.statuscolor = [1.0, 0.0, 0.0,1.0]
        self.drawtext = True
        self.font_path = "C:\\Windows\\Fonts\\msyh.ttc"  # 微软雅黑字体
        self.font_size = 16
        self.font = ImageFont.truetype(self.font_path, self.font_size)
        self.textcolor = [1.0, 1.0, 1.0,1.0]
        self.enable = True
        self.lastrunstatus = False
        self.textimage = None
        self.breifimage = None
        self.breifimage_visible = tk.IntVar()
        self.language = 'zh'
        self.spantime=0
        self.padding = 12
        self.get_image()
        self.message=message
        self.parameters={'lastrunstatus':self.lastrunstatus,}
        self.breifimagewidth = self.textimage.shape[1]
        self.breifimageheight = self.textimage.shape[0]*(self.textimage.shape[1]//self.breifimagewidth+1)
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.texts = {}
        self.set_language(self.language)
        self.description_html = {
            'zh': 
                """
                <div style="
                    font-family: Arial, sans-serif;
                    background-color: #f0f8ff;
                    text-align: left;
                    padding: 10px;
                ">
                    <div style="
                        display: inline-block;
                        text-align: left;
                        padding: 10px;
                        border: 2px solid #4a90e2;
                        border-radius: 10px;
                        background-color: #ffffff;
                    ">
                        <h3 style="color: #4a90e2;">欢迎来到CVFLOW应用</h3>
                        <p style="font-size: 15px; color: #333;">我们很高兴见到您！</p>
                        <img src="{path}" alt="Title Icon" style="width: 100%; height: auto; margin-top: 5px;">

                    </div>
                </div>
                """.format(path=iconp),
            'en': 
                """
                <div style="
                    font-family: Arial, sans-serif;
                    background-color: #f0f8ff;
                    text-align: left;
                    padding: 10px;
                ">
                    <div style="
                        display: inline-block;
                        text-align: left;
                        padding: 10px;
                        border: 2px solid #4a90e2;
                        border-radius: 10px;
                        background-color: #ffffff;
                    ">
                        <h3 style="color: #4a90e2;">Welcome to Cvflow App</h3>
                        <p style="font-size: 15px; color: #333;">It's nice to see you here!</p>
                        <img src="{path}" alt="Title Icon" style="width: 100%; height: auto; margin-top: 5px;">
                
                    </div>
                </div>
                """.format(path=iconp)
        }
    @classmethod
    def from_userdefined(cls,master,x:int=0,y:int=0,name:str='ValueModule',message=None):
        toplevel= tk.Toplevel(master)
        toplevel.iconbitmap(iconp)
        toplevel.title("User Defined Module")
        
        inputbox = PlaceholderEntry(toplevel,placeholder=name,width=60)
             
        result=[]
        def on_submit():
            result.append(inputbox.get())  # 保存输入内容
            toplevel.destroy()  # 关闭窗口

        submit_btn = ttk.Button(toplevel, text="确定", command=on_submit)
        inputbox.pack(pady=10)
        submit_btn.pack(pady=10)
        toplevel.bind("<Return>", lambda event: on_submit())  # 按回车键提交
        rootx = master.winfo_rootx()
        rooty = master.winfo_rooty()
        toplevel.geometry(f"+{rootx}+{rooty}")  # 设置新窗口位置
        
        # 阻塞等待窗口关闭
        submit_btn.focus_set()  # 设置按钮为默认焦点
        toplevel.wait_window()

        # 窗口关闭后，检查用户是否输入了内容
        name = result[0] if result else ""
        return cls(x=x, y=y,name=name, message=message)
    @classmethod
    def from_json(cls, json_data,message=None):
        """从JSON数据创建Graphics_ValueModule实例"""
        x = json_data.get('x', 0)
        y = json_data.get('y', 0)
        name = json_data.get('name', 'ValueModule')
        module = cls(x=x, y=y, name=name,message=message)
        
        # 设置其他属性
        module.linemodule = json_data.get('linemodule', False)
        module.text = json_data.get('text', name)
        module.normalcolor = json_data.get('normalcolor', [0.0, 0.5, 0.5, 1.0])
        module.selectedcolor = json_data.get('selectedcolor', [1.0, 0.0, 0.0, 1.0])
        module.statuscolor = json_data.get('statuscolor', [1.0, 0.0, 0.0, 1.0])
        module.drawtext = json_data.get('drawtext', True)
        module.font_path = json_data.get('font_path', "C:\\Windows\\Fonts\\msyh.ttc")
        module.font_size = json_data.get('font_size', 16)
        module.textcolor = json_data.get('textcolor', [1.0, 1.0, 1.0, 1.0])
        module.enable = json_data.get('enable', True)
        module.lastrunstatus = json_data.get('lastrunstatus', False)
        module.breifimage_visible.set(json_data.get('breifimage_visible', True))
        module.breifimagewidth = json_data.get('breifimagewidth', 200)
        module.breifimageheight = json_data.get('breifimageheight', 100)
        
        # 设置语言和描述
        language = json_data.get('language', 'zh')
        module.set_language(language)
        
        return module
    def set_language(self,language:str):
        if language == 'zh':
            self.texts['color_choose']='颜色选择'
            self.texts['del_button']= '删除'
            self.texts['del_button_tip_title']='删除模块'
            self.texts['del_button_tip_content']='确定删除该模块吗？'
            self.texts['run_button']= '运行'
            self.texts['save_button']= '保存'
            self.texts['load_button']= '加载'
            self.texts['info_label']= '信息'
            self.texts['tab1']='视图'
            self.texts['tab2']='参数'
            self.texts['tab3']='说明'
            self.texts['name_label']='名称'
            self.texts['labelcolor']='标签颜色'
            self.texts['fontsize']='字体大小'
            self.texts['fontpath']='字体路径'
            self.texts['brifeimage']='显示简略图'
            self.texts['brifeimagewidth']='简略图宽度'
            self.texts['brifeimageheight']='简略图高度'
            self.texts['language']='语言'
            self.texts['load_button_tip_title']='错误'
            self.texts['load_button_tip_content']='加载模块失败，请检查模块文件是否存在或格式是否正确。'
            pass
        else:
            self.texts['color_choose']='Choose Color'
            self.texts['del_button']= 'Delete'
            self.texts['del_button_tip_title']='Delete Module'
            self.texts['del_button_tip_content']='Are you sure you want to delete this module?'
            self.texts['run_button']= 'Run'
            self.texts['save_button']= 'Save'
            self.texts['load_button']= 'Load'
            self.texts['info_label']= 'Info'
            self.texts['tab1']='View'
            self.texts['tab2']='Parameter'
            self.texts['tab3']='Description'
            self.texts['name_label']='Name'
            self.texts['labelcolor']='Label Color'
            self.texts['fontsize']='Font Size'
            self.texts['fontpath']='Font Path'
            self.texts['brifeimage']='Show Brife Image'
            self.texts['brifeimagewidth']='Brife Image Width'
            self.texts['brifeimageheight']='Brife Image Height'
            self.texts['language']='Language'
            self.texts['load_button_tip_title']='Error'
            self.texts['load_button_tip_content']='Failed to load module, please check if the module file exists or if the format is correct.'
            pass
    def get_image(self):
        
        self.font= ImageFont.truetype(self.font_path, self.font_size)
        # 设置字体路径，使用 Windows 系统的字体

        #self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.text=self.text.replace('\\n','\n')
        self.lines = self.text.split('\n')
        # 计算每行文本的大小并找到最大宽度
        
        text_widths = [self.font.getbbox(line)[2]-self.font.getbbox(line)[0] for line in self.lines]
        text_width = max(text_widths) if text_widths else 0        
                
        self.bbox= self.font.getbbox(self.text)
        self.width = text_width + 2 * self.padding
        self.height = (self.bbox[3]-self.bbox[1])*len(self.lines) + 2 * self.padding
        self.textimage = np.full((self.height, self.width, 4),(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255),int(self.normalcolor[3]*255)), dtype=np.uint8)
        
        self.pil_image = Image.new("RGBA", (self.width, self.height), (int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255),int(self.normalcolor[3]*255)))
        self.textdraw = ImageDraw.Draw(self.pil_image)
    def get_inside_rect(self):
        x1 = self.x + self.padding
        y1 = self.y + self.padding
        x2 = self.x + self.width - self.padding
        y2 = self.y + self.height - self.padding
        return x1, y1, x2, y2
    def get_output_triangle(self):
        x1 = self.x + self.width/2
        y1 = self.y + self.height
        p1x = x1 + self.radius/2
        p1y = y1
        p2x = x1 - self.radius/2
        p2y = y1 
        p3x = x1
        p3y = y1 + self.radius/2
        return p1x, p1y, p2x, p2y, p3x, p3y
    def get_input_triangle(self):
        x1 = self.x + self.width/2
        y1 = self.y
        p1x = x1 + self.radius/2
        p1y = y1
        p2x = x1 - self.radius/2
        p2y = y1 
        p3x = x1
        p3y = y1 - self.radius/2
        return p1x, p1y, p2x, p2y, p3x, p3y
    def check_inside(self,x:int,y:int):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        x1, y1, x2, y2 = self.get_inside_rect()
        if x1 <= x <= x2 and y1 <= y <= y2:
            self.status = 'Selected'
            return self
        else:
            self.status = 'Normal'
            return None
    def run(self):
        starttime = time.perf_counter()
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.parameters['lastrunstatus']=self.lastrunstatus
    def show_parameter_page(self,x,y,parent):
        x1, y1, x2, y2 = self.get_inside_rect()
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return
        def update_io():
            tab2.children.clear()
            keys = list(self.parameters.keys())
            for i,key in enumerate(keys):
                tk.Label(tab2, text=f"{key}\n    {gstr(self.parameters[key])}",anchor='w',justify='left').grid(row=i, column=0,sticky='ew' ,pady=5)
            pass
        def change_language():
            self.language = languages_commbox.get()
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            html_label.set_html(self.description_html[self.language])
        def check_language():
            self.set_language(self.language)
            run_button.config(text=self.texts['run_button'])
            del_button.config(text=self.texts['del_button'])
            save_button.config(text=self.texts['save_button'])
            load_button.config(text=self.texts['load_button'])
            info_label.config(text=self.texts['info_label'])
            notebook.tab(tab1, text=self.texts['tab1'])
            notebook.tab(tab2, text=self.texts['tab2'])
            notebook.tab(tab3, text=self.texts['tab3'])
            namelabel.config(text=self.texts['name_label'])
            button.config(text=self.texts['color_choose'])
            labelcolor.config(text=self.texts['labelcolor'])
            fontsize_label.config(text=self.texts['fontsize'])
            fontpath_label.config(text=self.texts['fontpath'])
            brieifimage_width.config(text=self.texts['brifeimagewidth'])
            brieifimage_height.config(text=self.texts['brifeimageheight'])
            breifimage_enbale.config(text=self.texts['brifeimage'])
            languages_lable.config(text=self.texts['language'])
            html_label.set_html(self.description_html[self.language])
        def choose_color():
            color = colorchooser.askcolor(color=(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255)), title=self.texts['color_choose'])
            if color[0] is not None:
                self.normalcolor = [color[0][0]/255,color[0][1]/255,color[0][2]/255,1.0]
                button.config(bg=color[1])
        def run_button_click():
            self.run()
            info_label.config(text=f'Info: CT:{self.spantime:.4f}s')
            update_io()
        def del_button_click():
            if tk.messagebox.askokcancel(self.texts['del_button_tip_title'], self.texts['del_button_tip_content']):
                self.message(self,-1)
                window.destroy()
        window= tk.Toplevel(parent)
        window.title(self.text)
        window.iconbitmap(iconp)
        window.geometry(f'300x432+{parent.winfo_rootx()}+{parent.winfo_rooty()}')
        button_frame = tk.Frame(window)
        button_frame.pack(side='top', anchor='nw', pady=5)

        run_button = tk.Button(button_frame, text=self.texts['run_button'], command=run_button_click)
        run_button.pack(side='left', padx=1)

        del_button = tk.Button(button_frame, text=self.texts['del_button'], command=del_button_click)
        del_button.pack(side='left', padx=1)
        
        save_button = tk.Button(button_frame, text=self.texts['save_button'], command=self.save)
        save_button.pack(side='left', padx=1)
        
        load_button = tk.Button(button_frame, text=self.texts['load_button'], command=self.load)
        load_button.bind('<Button-1>',lambda event: self.load(),add=True)
        load_button.bind('<Button-1>',lambda event: update_io(),add=True)
        load_button.pack(side='left', padx=1)

        info_label = tk.Label(window,text=self.texts['info_label'])
        info_label.pack(side='bottom',anchor='sw')

        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True)
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        notebook.add(tab1,text='View')
        notebook.add(tab2,text='Parameter')
        notebook.add(tab3,text='Description')
        
        frame = tk.Frame(tab1)
        frame.pack(padx=10, pady=10)
        tk.Label(frame, text="X:").grid(row=0, column=0, pady=5)
        x_entry = tk.Entry(frame)
        x_entry.insert(0, self.x)
        x_entry.grid(row=0, column=1, pady=5)
        x_entry.bind('<Return>', lambda event: setattr(self, 'x', int(x_entry.get())))
        tk.Label(frame, text="Y:").grid(row=1, column=0, pady=5)
        y_entry = tk.Entry(frame)
        y_entry.insert(0, self.y)
        y_entry.grid(row=1, column=1, pady=5)
        y_entry.bind('<Return>', lambda event: setattr(self, 'y', int(y_entry.get())))
        namelabel= tk.Label(frame, text=self.texts['name_label'])
        namelabel.grid(row=2, column=0, pady=5)
        text_entry = tk.Entry(frame)
        text_entry.delete(0, 'end')
        text_entry.insert(0, self.text)
        text_entry.grid(row=2, column=1, pady=5)
        text_entry.bind('<Return>',lambda event: setattr(self,'text',text_entry.get()),add=True)
        text_entry.bind('<Return>',lambda event: self.get_image(),add=True)
        text_entry.bind('<Return>',lambda event: self.message(self,-2),add=True)

        labelcolor=tk.Label(frame, text=self.texts['labelcolor'])
        labelcolor.grid(row=4, column=0, pady=5)
        button = tk.Button(frame, text=self.texts['color_choose'], command=choose_color)
        button.grid(row=4,column=1,pady=5)
        
        fontsize_label=tk.Label(frame, text=self.texts['fontsize'])
        fontsize_label.grid(row=5, column=0, pady=5)
        spinbox= tk.Spinbox(frame,from_=1,to=48)
        spinbox.delete(0, 'end')
        spinbox.insert(0, self.font_size)
        spinbox.bind('<Button-1>',lambda evemt: setattr(self,'font_size',int(spinbox.get())),add=True)
        spinbox.bind('<Button-1>',lambda evemt: self.get_image(),add=True)
        

        spinbox.grid(row=5,column=1,pady=5)
        
        
        fontpath_label=tk.Label(frame, text=self.texts['fontpath'])
        fontpath_label.grid(row=6, column=0, pady=5)
        fontscale_spinbox= tk.Entry(frame)
        fontscale_spinbox.delete(0, 'end')
        fontscale_spinbox.insert(0, self.font_path)
        fontscale_spinbox.bind('<Return>',lambda event: setattr(self,'font_path',fontscale_spinbox.get()),add=True)
        fontscale_spinbox.bind('<Return>',lambda event: self.get_image(),add=True)
        fontscale_spinbox.grid(row=6,column=1,pady=5)
        
        brieifimage_width = tk.Label(frame, text=self.texts['brifeimagewidth'])
        brieifimage_width.grid(row=7, column=0, pady=5)
        brieifimage_width_entry = tk.Entry(frame)
        brieifimage_width_entry.delete(0, 'end')
        brieifimage_width_entry.insert(0, self.breifimagewidth)
        brieifimage_width_entry.grid(row=7, column=1, pady=5)
        brieifimage_width_entry.bind('<Return>',lambda event: setattr(self,'breifimagewidth',int(brieifimage_width_entry.get())))
        
        brieifimage_height = tk.Label(frame, text=self.texts['brifeimageheight'])
        brieifimage_height.grid(row=8, column=0, pady=5)
        brieifimage_height_entry = tk.Entry(frame)
        brieifimage_height_entry.delete(0, 'end')
        brieifimage_height_entry.insert(0, self.breifimageheight)
        brieifimage_height_entry.grid(row=8, column=1, pady=5)
        brieifimage_height_entry.bind('<Return>',lambda event: setattr(self,'breifimageheight',int(brieifimage_height_entry.get())))
        
        breifimage_enbale = tk.Label(frame, text=self.texts['brifeimage'])
        breifimage_enbale.grid(row=9, column=0, pady=5)
        breifimage_enbale_checkbox = tk.Checkbutton(frame, variable= self.breifimage_visible, onvalue=1, offvalue=0)
        breifimage_enbale_checkbox.grid(row=9, column=1, pady=5)
        
        languages_lable = tk.Label(frame, text=self.texts['language'])
        languages_lable.grid(row=10, column=0, pady=5)
        languages_commbox = ttk.Combobox(frame,values= ['en', 'zh'], state='readonly', width=5)
        languages_commbox.set(self.language)
        languages_commbox.grid(row=10, column=1, pady=5)
        languages_commbox.bind('<<ComboboxSelected>>', lambda event: change_language(), add=True)
                  
        html_label = HTMLLabel(tab3, html=self.description_html[self.language])
        html_label.pack(fill=tk.BOTH, expand=True)
        
        check_language()        
        update_io()
    def render_text(self, x, y):
        if self.drawtext is not True:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glColor3f(1.0, 1.0, 1.0)        
                
        self.pil_image = Image.new("RGBA", (self.width, self.height), (int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255),int(self.normalcolor[3]*255)))
        self.textdraw = ImageDraw.Draw(self.pil_image)

        self.textdraw.text((self.padding, self.padding - self.bbox[1]), self.text, font=self.font, fill=(int(self.textcolor[0]*255),int(self.textcolor[1]*255),int(self.textcolor[2]*255),int(self.textcolor[3]*255)))

        self.textimage = np.array(self.pil_image)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.textimage.shape[1], self.textimage.shape[0], 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, self.textimage)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # 绘制四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + self.textimage.shape[1], y)
        glTexCoord2f(1, 1); glVertex2f(x + self.textimage.shape[1], y + self.textimage.shape[0])
        glTexCoord2f(0, 1); glVertex2f(x, y + self.textimage.shape[0])
        glEnd()

        glDeleteTextures(1,[texture])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)   
    def render_breifimage(self, x, y):
        if self.breifimage is None or self.breifimage_visible.get() == 0:
            return
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        breifimage_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, breifimage_texture)
        glColor3f(1.0, 1.0, 1.0)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, self.breifimage.shape[1], self.breifimage.shape[0], 
                     0, GL_LUMINANCE, GL_FLOAT, self.breifimage)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # 绘制四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x + self.textimage.shape[1], y)
        glTexCoord2f(1, 0); glVertex2f(x + self.textimage.shape[1]+self.breifimagewidth, y)
        glTexCoord2f(1, 1); glVertex2f(x + self.textimage.shape[1]+self.breifimagewidth, y + self.breifimageheight)
        glTexCoord2f(0, 1); glVertex2f(x + self.textimage.shape[1], y + self.breifimageheight)
        glEnd()

        glDeleteTextures(1,[breifimage_texture])

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)  
    def GLDraw(self):
        if True:
            self.render_text(self.x, self.y)
            self.render_breifimage(self.x, self.y)
            if self.status == 'Normal':
                glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
            else:
                glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
            glBegin(GL_LINE_LOOP)
            glVertex2f(self.x, self.y)
            glVertex2f(self.x + self.textimage.shape[1], self.y)
            glVertex2f(self.x + self.textimage.shape[1], self.y + self.textimage.shape[0])
            glVertex2f(self.x, self.y + self.textimage.shape[0])
            glEnd()
            
            glColor3f(self.statuscolor[0], self.statuscolor[1], self.statuscolor[2])
            
            glBegin(GL_QUADS)
            glVertex2f(self.x-self.radius/2, self.y+2*self.radius-self.radius/2)
            glVertex2f(self.x+self.radius/2, self.y+2*self.radius-self.radius/2)
            glVertex2f(self.x+self.radius/2, self.y+2*self.radius+self.radius/2)
            glVertex2f(self.x-self.radius/2, self.y+2*self.radius+self.radius/2)
            glEnd()      
            
            glColor3f(1.0, 1.0, 1.0)     
    def contains(self,x:int,y:int):
        """判断点是否在坐标系内"""
        if self.enable is not True:
            return None
        return self.check_inside(x,y)
    def get_distance(self,x:int,y:int):
        """获取坐标系到点的距离"""
        distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
        return distance
    def save(self):
        """保存模块为JSON"""
        file_path = filedialog.asksaveasfilename(defaultextension=f"{self.text}.cvvm",
                                                 filetypes=[("JSON files", "*.cvvm"), ("All files", "*.*")])
        if file_path:
            try:
                # 只保存可序列化的属性
                data = self.get_json_data()
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Module saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save module: {e}")
    def get_json_data(self):
        """获取模块的JSON数据"""
        return {
            "class": self.__class__.__name__,
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "text": self.text,
            "normalcolor": self.normalcolor,
            "selectedcolor": self.selectedcolor,
            "font_path": self.font_path,
            "font_size": self.font_size,
            "textcolor": self.textcolor,
            "parameters": {k: None if isinstance(v, np.ndarray) else v for k, v in self.parameters.items()},
            "breifimagewidth": self.breifimagewidth,
            "breifimageheight": self.breifimageheight,
            "status": self.status,
            "language": self.language,
            'breifimage_visible': self.breifimage_visible.get(),
            "lastrunstatus": self.lastrunstatus,
        }
    def load(self):
        """加载模块的JSON文件"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.cvvm"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("class") != self.__class__.__name__:
                    messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_tip_content'])
                    return
                # 只加载可序列化的属性
                self.x = data.get("x", self.x)
                self.y = data.get("y", self.y)
                self.radius = data.get("radius", self.radius)
                self.text = data.get("text", self.text)
                self.normalcolor = data.get("normalcolor", self.normalcolor)
                self.selectedcolor = data.get("selectedcolor", self.selectedcolor)
                self.font_path = data.get("font_path", self.font_path)
                self.font_size = data.get("font_size", self.font_size)
                self.textcolor = data.get("textcolor", self.textcolor)
                self.parameters = data.get("parameters", {})
                self.breifimagewidth = data.get("breifimagewidth",self.breifimagewidth)
                self.breifimageheight = data.get("breifimageheight",self.breifimageheight)
                self.status = data.get("status",self.status)
                self.language = data.get("language",self.language)
                
        except Exception as e:
            messagebox.showerror(self.texts['load_button_tip_title'], self.texts['load_button_content'] + str(e))
def gstr(object):
    if isinstance(object,np.ndarray):
        return str(object.shape)
    else:
        return str(object)
        
