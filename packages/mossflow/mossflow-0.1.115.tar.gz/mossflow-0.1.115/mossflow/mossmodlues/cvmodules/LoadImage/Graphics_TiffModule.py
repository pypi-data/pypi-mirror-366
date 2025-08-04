from OpenGL.GL import *
from OpenGL.WGL import *
import cv2 as cv
import tkinter as tk
import time
from tkinter import messagebox
import numpy as np
from mossflow.TkinterWidgets import Graphics_ValueModule,gstr
from tkhtmlview import HTMLLabel
from tkinter import ttk,colorchooser
import tifffile as tiff

class Graphics_TiffModule(Graphics_ValueModule):
    rawname = 'tiff'
    zhname = '加载TIFF'
    enname = 'LoadTIFF'
    def __init__(self,x:int=0,y:int=0,name:str='LoadTiff',message=None):
        super().__init__(x,y,name,message)
        self.linemodule = False
        self.breifimage_visible = tk.IntVar(value=1)
        self.parameters={'filename':None,'lastrunstatus':self.lastrunstatus}

    def run(self):
        starttime = time.perf_counter()
        self.statuscolor = [1.0, 1.0, 0.0]
        """打开文件对话框，选择图片文件"""
        try:
            self.rawimg = tiff.imread(self.parameters['filename'])
            if self.rawimg.ndim == 3:
                self.rawimg = self.rawimg[:, :, 0]  # 取第一个通道
                self.format = GL_LUMINANCE
                self.pixel_format =GL_FLOAT
                self.parameters['image']=np.expand_dims(self.rawimg, axis=-1)  # 添加一个维度以匹配GL_LUMINANCE的要求
                self.breifimage = self.parameters['image'][::16, ::16]  # 下采样
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            elif self.rawimg.ndim == 2:
                self.format = GL_LUMINANCE
                self.pixel_format =GL_FLOAT
                self.parameters['image']=np.expand_dims(self.rawimg, axis=-1)
                self.breifimage = self.parameters['image'][::16, ::16]  # 下采样
                self.lastrunstatus = True
                self.statuscolor = [0.0, 1.0, 0.0]
            else:
                self.lastrunstatus = False
                self.breifimage = None
                self.statuscolor = [1.0, 0.0, 0.0]
        except Exception as e:
            self.breifimage = None
            self.lastrunstatus = False
            self.statuscolor = [1.0, 0.0, 0.0]
            messagebox.showerror("Error", f"Failed to load image: {e}")
        self.spantime= time.perf_counter() - starttime
        self.moudlestatus = f'Name: {self.text} \n Status: {self.status} \n Time: {self.spantime:.4f}s \n LastRunStatus: {self.lastrunstatus}'
        self.parameters['lastrunstatus']=self.lastrunstatus
