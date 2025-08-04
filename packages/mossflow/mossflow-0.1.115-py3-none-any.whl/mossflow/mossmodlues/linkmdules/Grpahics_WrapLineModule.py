from OpenGL.GL import *
from OpenGL.WGL import *
import cv2 as cv
import tkinter as tk
import time
from tkinter import messagebox
import numpy as np
from mossflow.TkinterWidgets import Graphics_ValueModule,gstr,PlaceholderEntry,iconp
from tkhtmlview import HTMLLabel
from tkinter import ttk,colorchooser,filedialog
import json

class Grpahics_WrapLineModule(Graphics_ValueModule):
    rawname = 'BaseLine'
    zhname = '链接'
    enname = 'Link'
    def __init__(self,A:Graphics_ValueModule=None,B:Graphics_ValueModule=None,KeyA:str=None,KeyB:str=None,name:str='WrapLine',message=None):
        super().__init__(0,0,name,message)
        self.linemodule = True
        # self.rawname = 'BaseLine'
        # self.zhname = '链接'
        # self.enname = 'Link'
        self.A = A
        self.B = B
        self.KyeA = KeyA
        self.KyeB = KeyB
        self.width = self.radius
        self.height = self.radius
        self.selectedcolor = [1.0, 0.0, 0.0,1.0]
        self.normalcolor = [1.0, 1.0, 1.0,1.0]
        self.status = 'Normal'
        self.selectdistance = 10
        self.parameters = {f'{self.A.text}': self.A.parameters[KeyA],f'{self.B.text}': self.B.parameters[KeyB]}
    @classmethod
    def from_userdefined(cls,master,x:int=0,y:int=0,name:str='ValueModule',message=None):
        toplevel= tk.Toplevel(master)
        toplevel.iconbitmap(iconp)
        toplevel.title("User Defined Module")
        rootx = master.winfo_rootx()
        rooty = master.winfo_rooty()
        toplevel.geometry(f'300x100+{rootx}+{rooty}')
        inputbox = PlaceholderEntry(toplevel,placeholder=name,width=60)
        result=[]
        def on_submit():
            result.append(inputbox.get())  # 保存输入内容
            toplevel.destroy()  # 关闭窗口
        toplevel.bind('<Return>', lambda event: on_submit())  # 按回车键提交
        submit_btn = ttk.Button(toplevel, text="确定", command=on_submit)
        inputbox.pack(pady=10)
        submit_btn.pack(pady=10)

        # 阻塞等待窗口关闭
        submit_btn.focus_set()  # 设置按钮为默认焦点
        toplevel.wait_window()

        # 窗口关闭后，检查用户是否输入了内容
        name = result[0] if result else ""
        line=cls(A=Graphics_ValueModule(),B=Graphics_ValueModule(),KeyA='lastrunstatus',KeyB='lastrunstatus',name=name,message=message)
        return line
    @classmethod
    def from_json(cls, json_data ,modlues,message=None):
        x= json_data.get('x', 0)
        y = json_data.get('y', 0)
        # 从JSON数据中获取x和y坐标
        name = json_data.get('name', 'WrapLine')
        # 从JSON数据中获取name
        A = json_data.get('A', None)
        B = json_data.get('B', None)
        KeyA = json_data.get('KeyA', 'lastrunstatus')
        KeyB = json_data.get('KeyB', 'lastrunstatus')
        # 从JSON数据中获取A和B的值
        linemodule= cls(A=modlues[A],B=modlues[B],KeyA=KeyA,KeyB=KeyB,name=name,message=message)
        linemodule.x = x
        linemodule.y = y
        linemodule.radius = json_data.get('radius', 20)
        linemodule.normalcolor = json_data.get('normalcolor', [1.0, 1.0, 1.0, 1.0])
        linemodule.selectedcolor = json_data.get('selectedcolor', [1.0, 0.0, 0.0, 1.0])
        linemodule.status = json_data.get('status', 'Normal')
        linemodule.font_path = json_data.get('font_path', 'arial.ttf')
        linemodule.font_size = json_data.get('font_size', 12)
        linemodule.textcolor = json_data.get('textcolor', [0.0, 0.0, 0.0, 1.0])
        linemodule.breifimagewidth = json_data.get('breifimagewidth', 100)
        linemodule.breifimageheight = json_data.get('breifimageheight', 100)
        linemodule.language = json_data.get('language', 'en')
        linemodule.text = json_data.get('text', 'WrapLine')
        linemodule.parameters = json_data.get('parameters', {})
        linemodule.set_language(linemodule.language)
        return linemodule
    def get_inside_rect(self):
        return self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius
    def bezier_curve_points(self, num_segments=50):
        """
        使用生成器生成贝塞尔曲线上的点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            num_segments: 用于近似曲线的线段数量。

        Yields:
            (x, y) 元组，表示贝塞尔曲线上的点。
        """
        ox1,oy1,ox2,oy2,ox3,oy3= self.A.get_output_triangle()
        ix1,iy1,ix2,iy2,ix3,iy3= self.B.get_input_triangle()
        dy= (oy3-iy3)/2
        dx= (ox3-ix3)/2
        control_points = [(ox3,oy3),(ox3-dx/20,oy3-dy/2),(ix3+dx/20,iy3+dy/2),(ix3,iy3)]
        for i in range(num_segments + 1):
            t = float(i) / num_segments
            yield self.bezier_point(control_points, t)
    def bezier_point(self,control_points, t):
        """
        计算贝塞尔曲线上的一个点。

        Args:
            control_points: 控制点列表，每个点是一个 (x, y) 元组。
            t: 参数值，范围从 0.0 到 1.0，表示曲线上的位置。

        Returns:
            (x, y) 元组，表示曲线上的点。
        """

        n = len(control_points) - 1
        x = 0.0
        y = 0.0

        for i, point in enumerate(control_points):
            x += self.binomial_coefficient(n, i) * pow(1 - t, n - i) * pow(t, i) * point[0]
            y += self.binomial_coefficient(n, i) * pow(1 - t, n - i) * pow(t, i) * point[1]

        return x, y
    def binomial_coefficient(self,n, k):
        """
        计算二项式系数 (n choose k)。
        """
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        if k > n // 2:
            k = n - k
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        return result
    def GLDraw(self):
        if self.status == 'Normal':
            glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
        else:
            glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])
        
        if self.A is None or self.B is None:
            glBegin(GL_LINE_STRIP)
            glVertex2f(self.x-self.radius*2, self.y-self.radius*2)
            glVertex2f(self.x+self.radius*2, self.y-self.radius*2)
            glVertex2f(self.x+self.radius*2, self.y+self.radius*2)
            glVertex2f(self.x-self.radius*2, self.y+self.radius*2)
            glEnd()        
            return    
            
        glColor3f(0.5, 0.5, 0.5)     
        glBegin(GL_LINE_STRIP)
        for index,point in enumerate(self.bezier_curve_points()):
            glVertex2f(point[0], point[1])
            if index == 25:
                self.x = point[0]
                self.y = point[1]
        glEnd()
        if self.status == 'Normal':
            glColor3f(self.normalcolor[0], self.normalcolor[1], self.normalcolor[2])
        else:
            glColor3f(self.selectedcolor[0], self.selectedcolor[1], self.selectedcolor[2])        
        glBegin(GL_QUADS)
        glVertex2f(self.x-self.radius/2, self.y-self.radius/2)
        glVertex2f(self.x+self.radius/2, self.y-self.radius/2)
        glVertex2f(self.x+self.radius/2, self.y+self.radius/2)
        glVertex2f(self.x-self.radius/2, self.y+self.radius/2)        
        glEnd()
        
        glColor3f(1.0, 1.0, 1.0)     
        if self.A.parameters[self.KyeA] is not None:
            # Draw output triangle
            p1x, p1y, p2x, p2y, p3x, p3y = self.A.get_output_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()
        if self.B.parameters[self.KyeB] is not None:
            # Draw input triangle
            p1x, p1y, p2x, p2y, p3x, p3y = self.B.get_input_triangle()
            glBegin(GL_LINE_LOOP)
            glVertex2f(p1x, p1y)
            glVertex2f(p2x, p2y)
            glVertex2f(p3x, p3y)
            glEnd()
        
        glColor3f(1.0, 1.0, 1.0)
    def run(self):
        starttime = time.perf_counter()
        try:
            self.B.parameters[self.KyeB]=self.A.parameters[self.KyeA]
            self.lastrunstatus = True
        except Exception as e:
            self.lastrunstatus = False
            messagebox.showerror("Error", f"Failed to set line parameters: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
    def save(self):
        """保存模块为JSON"""
        file_path = filedialog.asksaveasfilename(defaultextension=f"{self.text}.cvlm",
                                                 filetypes=[("JSON files", "*.cvlm"), ("All files", "*.*")])
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
            "parameters": self.parameters,
            "breifimagewidth": self.breifimagewidth,
            "breifimageheight": self.breifimageheight,
            "language": self.language,
            "status": self.status,
            "KeyA": self.KyeA,
            "KeyB": self.KyeB,
            "A": self.A.text,
            "B": self.B.text
        }
    def load(self,modules):
        """加载模块的JSON文件"""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.cvlm"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data.get("class") != self.__class__.__name__:
                    messagebox.showerror('Load Error', 'The selected file is not a valid WrapLineModule file.')
                    return
                # 只加载可序列化的属性
                try:
                    x = data.get("x", self.x)
                    y = data.get("y", self.y)
                    radius = data.get("radius", self.radius)
                    text = data.get("text", self.text)
                    normalcolor = data.get("normalcolor", self.normalcolor)
                    selectedcolor = data.get("selectedcolor", self.selectedcolor)
                    font_path = data.get("font_path", self.font_path)
                    font_size = data.get("font_size", self.font_size)
                    textcolor = data.get("textcolor", self.textcolor)
                    parameters = data.get("parameters", {})
                    breifimagewidth = data.get("breifimagewidth",self.breifimagewidth)
                    breifimageheight = data.get("breifimageheight",self.breifimageheight)
                    language = data.get("language", self.language)
                    status = data.get("status",self.status)
                    KyeA = data.get("KeyA",self.KyeA)
                    KyeB = data.get("KeyB",self.KyeB)
                    A = modules[data.get("A",self.A.text)]
                    B = modules[data.get("B",self.B.text)]
                except KeyError as e:
                    messagebox.showerror('Load Error', f'Missing required key: {e}')
                    return
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
                self.language = data.get("language", self.language)
                self.status = data.get("status",self.status)
                self.KyeA = data.get("KeyA",self.KyeA)
                self.KyeB = data.get("KeyB",self.KyeB)
                self.A = modules[data.get("A",self.A.text)]
                self.B = modules[data.get("B",self.B.text)]
        except Exception as e:
            messagebox.showerror('Load Error',str(e))              
    def show_parameter_page(self,x,y,parent):
        x1, y1, x2, y2 = self.get_inside_rect()
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            return
        def update_io():
            buttona.config(text=f"A:   {self.A.text}\n    {self.KyeA}:{gstr(self.A.parameters[self.KyeA])}")
            buttonb.config(text=f"B:   {self.B.text}\n    {self.KyeB}:{gstr(self.B.parameters[self.KyeB])}")       
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
            htmllabel.set_html(self.description_html[self.language])
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
            htmllabel.set_html(self.description_html[self.language])

        def choose_color():
            color = colorchooser.askcolor(color=(int(self.normalcolor[0]*255),int(self.normalcolor[1]*255),int(self.normalcolor[2]*255)), title="Choose Color")
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
        rootx = parent.winfo_rootx()
        rooty = parent.winfo_rooty()
        window.geometry(f'300x432+{rootx}+{rooty}')

        button_frame = tk.Frame(window)
        button_frame.pack(side='top', anchor='nw', pady=5)

        run_button = tk.Button(button_frame, text=self.texts['run_button'], command=run_button_click)
        run_button.pack(side='left', padx=1)

        del_button = tk.Button(button_frame, text=self.texts['del_button'], command=del_button_click)
        del_button.pack(side='left', padx=1)
        
        save_button = tk.Button(button_frame, text=self.texts['save_button'], command=self.save)
        save_button.pack(side='left', padx=1)
        
        load_button = tk.Button(button_frame, text=self.texts['load_button'], command=self.load)
        load_button.bind('<Button-1>',lambda event: update_io(),add=True)
        load_button.bind('<Button-1>',lambda event: self.message(self,3),add=True)
        load_button.pack(side='left', padx=1)

        info_label = tk.Label(window,text=self.texts['info_label'])
        info_label.pack(side='bottom',anchor='sw')

        notebook = ttk.Notebook(window)
        notebook.pack(fill='both', expand=True)
        tab1 = ttk.Frame(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)

        notebook.add(tab1,text=self.texts['tab1'])
        notebook.add(tab2,text=self.texts['tab2'])
        notebook.add(tab3,text=self.texts['tab3'])

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
        namelabel=tk.Label(frame, text=self.texts['name_label'])
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
                
        buttona=tk.Button(tab2, text=f"A:   {self.A.text}\n    {gstr(self.A.parameters[self.KyeA])}",justify='left',anchor='w')
        buttona.grid(row=0, column=0,sticky='ew' ,pady=5)
        buttona.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','A'),('keyname','KyeA'),('button',buttona)])),add=True)

        buttonb=tk.Button(tab2, text=f"B:   {self.B.text}\n    {gstr(self.B.parameters[self.KyeB])}",justify='left',anchor='w')
        buttonb.grid(row=1, column=0,sticky='ew' ,pady=5)
        buttonb.bind('<Button-1>',lambda event: self.message(self,1,**dict([('paramname','B'),('keyname','KyeB'),('button',buttonb)])),add=True) 
        
        htmllabel= HTMLLabel(tab3, html=self.description_html[self.language])
        htmllabel.pack(fill=tk.BOTH, expand=True)              
        
        notebook.select(tab2)
        
        check_language()
        update_io()

