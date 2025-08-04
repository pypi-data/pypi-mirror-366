from OpenGL.GL import *
from OpenGL.WGL import *
import cv2 as cv
import tkinter as tk
import time
from tkinter import messagebox
import numpy as np
from mossflow.TkinterWidgets import Graphics_ValueModule,gstr
from tkhtmlview import HTMLLabel
from tkinter import ttk,colorchooser,filedialog

class Graphics_OpenFileModule(Graphics_ValueModule):
    rawname = 'openfile'
    zhname = '打开文件'
    enname = 'OpenFile'
    def __init__(self,x:int=0,y:int=0,name:str='OpenFile',message=None):
        super().__init__(x,y,name,message)
        self.linemodule = False
        self.parameters={'filename':None,'lastrunstatus':self.lastrunstatus}

    def run(self):
        starttime = time.perf_counter()
        self.statuscolor = [1.0, 1.0, 0.0]
        """打开文件对话框，选择图片文件"""
        try:
            reslut = filedialog.askopenfilename(title="Open File", filetypes=[("All Files", "*.*")])
            if reslut:
                self.parameters['filename']=reslut
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            else:
                self.lastrunstatus = False
                self.statuscolor = [1.0, 0.0, 0.0]
        except Exception as e:
            self.lastrunstatus = False
            self.statuscolor = [1.0, 0.0, 0.0]
            messagebox.showerror("Error", f"Failed to load image: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.parameters['lastrunstatus']=self.lastrunstatus
