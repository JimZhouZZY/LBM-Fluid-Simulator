#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################
#Made by ZZY                                   #
#2021.11 - 2022.3                              #
#秦皇岛市海港区                                 #
################################################

# 开发日志：
# 日志：2021/12/25 开始记载日志
# 日志：2021/12/25 实现流线动画绘制，但是十分卡顿，运算跟不上。
# 日志：           尝试多线程，Debug下正常运行，但Run下无法正常运行
# 日志：2021/12/26 尝试改进算法，优化Barrier分辨率（浸入式边界条件），失败。
# 日志：           改进输出输出机制，现在可以在运行过程中编辑Barrier、v0等参数了
# 日志：           尝试通过曲线方程绘制Barrier
# 日志：2021/12/31 探索造成数据溢出的原因
# 日志：           造成数据溢出的原因是：雷诺数增大，层流变为湍流，计算时步长值太小。
# 日志：2022/1/1   尝试用tkinter写GUI
# 日志：2022/1/13  PYINSTALLER
# 日志：2022/1/14  打包成功，制作完安装程序
# 日志：2022/1/16  打包出现bug。开发方程模块。完成方程解析。
# 日志：2022/1/17  方程旋转。
# 日志：2022/1/18  绘制barrier，但存在许多bug。
# 日志：2022/1/24  完成C++上对核心算法部分的重写。尝试使用Boost混合编程。
# 日志：2022/1/26  完善方程输入机制，现在方程可以用分号隔开输入啦。
# daily:2022/1/29 convert it to python[3], linux version, but there's a problem 'zsh: segmentation fault', which probably means that the memory isnt enough
# 日志：2022/1/30  完成动画的文件输入和输出，但是失真严重;
# 日志：..later..  解决失真问题。numpy的输出是带有科学计数法的，直接裁剪字符串会改变数值，使用numpy.round()即可。
# 日志：2022/2/3   初步实现对河流的数值模拟
# 日志：2022/3/11  好久没记了。懒。Pyqt5
# 日志：懒懒懒
# 日志：2022/3     做完啦！

#import numexpr
#from inspect import Traceback
#import winsound
from fileinput import filename
#from tkinter import Widget, ttk
import traceback
#from PyQt5 import QtCore
# import matplotlib
# matplotlib.use("Agg")
#import linecache
#from matplotlib.backends.backend_qt import Main[5]indow
#from IPython.external.qt_loaders import import_pyqt5
import matplotlib.pyplot
#from matplotlib.style import available
import numpy
import os
#from numpy.lib.npyio import save
import sympy
import sys
import threading
import time
#import multiprocessing
#from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer 
from PyQt5.QtCore import QThread 
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QCheckBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sympy import *
#import webbrowser

#from sympy.solvers.diophantine.diophantine import prime_as_sum_of_two_squares
#import qtawesome


# 这里用from tkinter import ttk或者import tkinter.ttk都会报错
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from numba import cuda
# from numba import vectorize
# from numpy import seterr
# Define constants:

# from numba import jit 使用需要修改numpy对数组的运算部分，改成numba能支持的for循环格式

# from tkinter import *

#matplotlib.pyplot.switch_backend('agg')
oncanvas = False
update = True
nheight = 100
nwidth = 150
edge = 0
force_vector_switch = False
list_lift = []
list_drag = []
list_gen = []
show_lift_drag = False
lock_draw_2 = False
lock_draw = False
alert = False
killThreadAnimation = False
kill = False
skip = True
nx4 = []
ny4 = []
nx1 = []
nx2 = []
ny1 = []
ny2 = []
nx3 = []
ny3 = []
# y = symbols('y', real=True)
changing = False
change_v = False
change_viscosity = False
gen = 0
drag = 0
lift = 0
dforce = True
tank = 0
ncurl = 1  # 临时的
# ----------------------
height = 100 # 100
width =  150 # 150
# ----------------------
viscosity = 0.020
omega = 1 / (3 * viscosity + 0.5)  # 松驰系数
u0 = 0.1
four9th = 4.0 / 9.0
one9th = 1.0 / 9.0
one36th = 1.0 / 36.0
performanceData = False
u1 = u0
nviscosity = viscosity
bindable = False
start_start = False
first_st_var = True
change_barrier_switch = False
change_animation_switch = False
write_switch = False
animation_type = 0 # 0=旋度动画，1=密度动画, 2=流线
contrast = 1
animating = False
y, x = numpy.mgrid[0:height:1, 0:width:1]
y1, x1 = numpy.mgrid[0:int(height/4):1, 0:int(width/4):1]
x1 = 4*x1
y1 = 4*y1
ux1 = numpy.zeros((int(height/4), int(width/4)))
uy1 = numpy.zeros((int(height/4), int(width/4)))
u2 = numpy.zeros((int(height), int(width)))
#u21 = numpy.zeros((int(height/4), int(width/4)))
# 初始化
n0 = four9th * (numpy.ones((height, width)) - 1.5 * u0 ** 2)
n3 = one9th * (numpy.ones((height, width)) - 1.5 * u0 ** 2)
n7 = one9th * (numpy.ones((height, width)) - 1.5 * u0 ** 2)
n1 = one9th * (numpy.ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n5 = one9th * (numpy.ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n2 = one36th * (numpy.ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n8 = one36th * (numpy.ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n4 = one36th * (numpy.ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n6 = one36th * (numpy.ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n = [n0, n1, n2, n3, n4, n5, n6, n7, n8]
rho = n[0] + n[3] + n[7] + n[1] + n[5] + n[2] + n[8] + n[4] + n[6]
ux = (n[1] + n[2] + n[8] - n[5] - n[4] - n[6]) / rho
uy = (n[3] + n[2] + n[4] - n[7] - n[8] - n[6]) / rho

for i in range(int(height/4)):
    for j in range(int(width/4)):
        ux1[i, j] = ux[i*4, j*4]
        uy1[i, j] = uy[i*4, j*4]
barrier = numpy.zeros((height, width), bool)
for i in range(16):
    barrier[int((height / 2) + 8 - i), int(width / 2)] = True
nbarrier = numpy.zeros((height, width), bool) 
nnbarrier = numpy.zeros((height, width), bool) 
nbarrier = barrier
nnbarrier = nbarrier 
xp = []
yp = []
for i in range(height):
    for j in range(width):
        if nnbarrier[i, j]:
            xp.append(j - width / 2)
            yp.append(i - height / 2)


barrier3 = numpy.roll(barrier, 1, axis=0) 
barrier7 = numpy.roll(barrier, -1, axis=0) 
barrier1 = numpy.roll(barrier, 1, axis=1)  
barrier5 = numpy.roll(barrier, -1, axis=1)
barrier2 = numpy.roll(barrier3, 1, axis=1)
barrier4 = numpy.roll(barrier3, -1, axis=1)
barrier8 = numpy.roll(barrier7, 1, axis=1)
barrier6 = numpy.roll(barrier7, -1, axis=1)

barrier_zone = numpy.zeros((height, width))
barrier_area = barrier3 + barrier7 + barrier1 + barrier5 + barrier2 + barrier4 + barrier8 + barrier6
for i in range(height):
    for j in range(width):
        if barrier_area[i, j] > 0:
            barrier_zone[i, j] = True


# @vectorize(['float32(float32, float32)'], target='gpu')

# @cuda.jit
change_barrier_switch = False
first_write = True
barrier_zone = numpy.zeros((height, width))
for i in range(height):
    for j in range(width):
        if barrier[i , j]:
            barrier_zone[i, j] = True
            barrier_zone[i-1, j-1] = True
            barrier_zone[i, j-1] = True
            barrier_zone[i-1, j] = True
            barrier_zone[i+1, j+1] = True
            barrier_zone[i+1, j] = True
            barrier_zone[i, j+1] = True
            barrier_zone[i-1, j+1] = True
            barrier_zone[i+1, j-1] = True
changeable_barrier_switch = False

def stream():
    global change_barrier_switch, nbarrier, barrier_zone, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood
    global n
    try:
        if kill:
            sys.exit()
        elif killThreadAnimation:
            print('KILLED')
            sys.exit()
        if changeable_barrier_switch:
            changeable_barrier()
        if change_barrier_switch:
            print("CHANGE")
            barrier = nbarrier
            barrier3 = numpy.roll(barrier, 1, axis=0)
            barrier7 = numpy.roll(barrier, -1, axis=0)
            barrier1 = numpy.roll(barrier, 1, axis=1)
            barrier5 = numpy.roll(barrier, -1, axis=1)
            barrier2 = numpy.roll(barrier3, 1, axis=1)
            barrier4 = numpy.roll(barrier3, -1, axis=1)
            barrier8 = numpy.roll(barrier7, 1, axis=1)
            barrier6 = numpy.roll(barrier7, -1, axis=1)
            bImageArray[:, :, 3] = 0  # 刷新Barrier图像
            bImageArray[barrier, 3] = 255
            change_barrier_switch = False
            blood[:, :] = 0
            blood[barrier] = 100
            if show_lift_drag:
                for i in range(height):
                    for j in range(width):
                        if barrier[i , j]:
                            barrier_zone[i, j] = True
                            barrier_zone[i-1, j-1] = True
                            barrier_zone[i, j-1] = True
                            barrier_zone[i-1, j] = True
                            barrier_zone[i+1, j+1] = True
                            barrier_zone[i+1, j] = True
                            barrier_zone[i, j+1] = True
                            barrier_zone[i-1, j+1] = True
                            barrier_zone[i+1, j-1] = True
        n[3] = numpy.roll(n[3], 1, axis=0)  
        n[2] = numpy.roll(n[2], 1, axis=0)
        n[4] = numpy.roll(n[4], 1, axis=0)
        n[7] = numpy.roll(n[7], -1, axis=0)
        n[8] = numpy.roll(n[8], -1, axis=0)
        n[6] = numpy.roll(n[6], -1, axis=0)
        n[1] = numpy.roll(n[1], 1, axis=1) 
        n[2] = numpy.roll(n[2], 1, axis=1)
        n[8] = numpy.roll(n[8], 1, axis=1)
        n[5] = numpy.roll(n[5], -1, axis=1)
        n[4] = numpy.roll(n[4], -1, axis=1)
        n[6] = numpy.roll(n[6], -1, axis=1)
        if edge == 0:
            n[3][barrier3] = n[7][barrier]
            n[3][1, :] = n[7][0, :]
            n[7][barrier7] = n[3][barrier]
            n[7][height - 2, :] = n[3][height - 1, :]
            n[1][barrier1] = n[5][barrier]
            n[5][barrier5] = n[1][barrier]
            n[2][barrier2] = n[6][barrier]
            n[2][1, :] = n[6][0, :]
            n[4][barrier4] = n[8][barrier]
            n[4][1, :] = n[8][0, :]
            n[8][barrier8] = n[4][barrier]
            n[8][height - 2, :] = n[4][height - 1, :]
            n[6][barrier6] = n[2][barrier]
            n[6][height - 2, :] = n[2][height - 1, :]
        elif edge == 1:
            n[3][barrier3] = n[7][barrier]
            #n[3][1, :] = n[7][0, :]
            n[7][barrier7] = n[3][barrier]
            n[1][barrier1] = n[5][barrier]
            n[5][barrier5] = n[1][barrier]
            n[2][barrier2] = n[6][barrier]
            #n[2][1, :] = n[6][0, :]
            n[4][barrier4] = n[8][barrier]
            #n[4][1, :] = n[8][0, :]
            n[8][barrier8] = n[4][barrier]
            n[6][barrier6] = n[2][barrier]
        if edge == 2:
            n[3][barrier3] = n[7][barrier]
            n[3][1, :] = n[7][0, :]
            n[7][barrier7] = n[3][barrier]
            n[7][height - 2, :] = n[3][height - 1, :]
            n[1][barrier1] = n[5][barrier]
            #n[1][: width - 2] = n[5][:, width - 1]
            n[5][barrier5] = n[1][barrier]
            n[5][:, width - 2] = n[1][:, width - 1]
            n[2][barrier2] = n[6][barrier]
            n[2][1, :] = n[6][0, :]
            n[4][barrier4] = n[8][barrier]
            n[4][1, :] = n[8][0, :]
            n[4][:, width - 2] = n[8][:, width - 1]
            n[8][barrier8] = n[4][barrier]
            n[8][height - 2, :] = n[4][height - 1, :]
            n[6][barrier6] = n[2][barrier]
            n[6][height - 2, :] = n[2][height - 1, :]
            n[6][:, width - 2] = n[2][:, width - 1]
        if edge == 3:
            n[3][barrier3] = n[7][barrier]
            n[3][1, :] = n[7][0, :]
            n[7][barrier7] = n[3][barrier]
            n[7][height - 2, :] = n[3][height - 1, :]
            n[1][barrier1] = n[5][barrier]
            n[1][:, 1] = n[5][:, 0]
            n[5][barrier5] = n[1][barrier]
            n[5][:, width - 2] = n[1][:, width - 1]
            n[2][barrier2] = n[6][barrier]
            n[2][1, :] = n[6][0, :]
            n[2][:, 1] = n[6][:, 0]
            n[4][barrier4] = n[8][barrier]
            n[4][1, :] = n[8][0, :]
            n[4][:, width - 2] = n[8][:, width - 1]
            n[8][barrier8] = n[4][barrier]
            n[8][height - 2, :] = n[4][height - 1, :]
            n[8][:, 1] = n[4][:, 0]
            n[6][barrier6] = n[2][barrier]
            n[6][height - 2, :] = n[2][height - 1, :]
    except:
        print('WARNING: BARRIER CHANGED ILLEGALLY')
        traceback.print_exc()

#numexpr.set_num_threads(4)
def feq(num):
    #global c
    return (c[num, 0] * rho * (u2115 + 3 * (c[num, 1] * ux + c[num, 2] * uy)  + c[num, 5] * 4.5 * ux2 + c[num, 6] * 4.5 * uy2 + 4.5 * (c[num, 3] * u2 + c[num, 4] * 2 * uxuy)))
    #return (numexpr.evaluate('c[num, 0] * rho * (u2115 + 3 * (c[num, 1] * ux + c[num, 2] * uy)  + c[num, 5] * 4.5 * ux2 + c[num, 6] * 4.5 * uy2 + 4.5 * (c[num, 3] * u2 + c[num, 4] * 2 * uxuy))'))
    #return (numexpr.evaluate('c['+ str(num) + ', 0] * rho * (u2115 + 3 * (c['+ str(num) + ', 1] * ux + c['+ str(num) + ', 2] * uy)  + c['+ str(num) + ', 5] * 4.5 * ux2 + c['+ str(num) + ', 6] * 4.5 * uy2 + 4.5 * (c['+ str(num) + ', 3] * u2 + c['+ str(num) + ', 4] * 2 * uxuy))'))

# 权重，ux， uy， u2， uxuy， ux2， uy2
c = numpy.array([[four9th, 0, 0, 0, 0, 0, 0],
                 [one9th, 1, 0, 0, 0, 1, 0],
                 [one36th, 1, 1, 1, 1, 0, 0],
                 [one9th, 0, 1, 0, 0, 0, 1],
                 [one36th, -1, 1, 1, -1, 0, 0],
                 [one9th, -1, 0, 0, 0, 1, 0],
                 [one36th, -1, -1, 1, 1, 0, 0],
                 [one9th, 0, -1, 0, 0, 0, 1],
                 [one36th, 1, -1, 1, -1, 0, 0]])
# Collide particles within each cell to redistribute velocities (could be optimized a little more):
# @jit 的使用需要修改numpy对数组的运算部分，改成numba能支持的for循环格式
def collide():
    global rho, ux, uy, n, k, u0, u1, u2, change_v, change_viscosity, viscosity, \
        omega, gen, dforce, barrier, uxuy, u2115, ux2, uy2
    if kill:
        sys.exit()
    elif killThreadAnimation:
        print('KILLED')
        sys.exit()
    try:
        omega = 1 / (3 * viscosity + 0.5)
        rho = n[0] + n[3] + n[7] + n[1] + n[5] + n[2] + n[8] + n[4] + n[6]
        ux = (n[1] + n[2] + n[8] - n[5] - n[4] - n[6]) / rho
        uy = (n[3] + n[2] + n[4] - n[7] - n[8] - n[6]) / rho
        ux2 = ux * ux
        uy2 = uy * uy
        u2 = ux2 + uy2
        u2115 = 1 - 1.5 * u2
        uxuy = ux * uy
        for i in range(9):
            n[i] = (1 - omega) * n[i] + omega * feq(i)
        for i in range(height):
            try:
                if edge != 3:
                    if not barrier[i, 0]:
                            n[1][i, 0] = one9th * (1 + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                            n[5][i, 0] = one9th * (1 - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                            n[2][i, 0] = one36th * (1 + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                            n[8][i, 0] = one36th * (1 + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                            n[4][i, 0] = one36th * (1 - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                            n[6][i, 0] = one36th * (1 - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                else:
                    n[1][height-3:height-2, :] = one9th * (1 + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                    n[5][height-3:height-2, :] = one9th * (1 - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                    n[2][height-3:height-2, :] = one36th * (1 + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                    n[8][height-3:height-2, :] = one36th * (1 + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                    n[4][height-3:height-2, :] = one36th * (1 - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
                    n[6][height-3:height-2, :] = one36th * (1 - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
            except IndexError:
                traceback.print_exc()
        gen += 1
    except:
        traceback.print_exc()
        #main_window.Alert()
    

# @jit
def Lift_Drag(ld):
    global ux, uy, drag, lift, barrier_zone
    '''
    drag = 0
    lift = 0
    for i_drag in range(height):
        drag = drag + ux[i_drag, 0] - ux[i_drag, width - 1]
    for i_lift in range(height):
        lift = lift + uy[i_lift, 0] - uy[i_lift, 48]
    '''
    if ld:
        '''
        lift = 0
        for i in range(height):
            for j in range(width):
                if barrier_zone[i, j]:
                    lift += -uy[i, j]
        return lift
        '''
        lift = 0
        for i in range(height):
            lift += - uy[i, 1] + uy[i, width-2]
        lift = lift/height
        return lift
    elif not ld:
        '''
        drag = 0
        for i in range(height):
            for j in range(width):
                if barrier_zone[i, j]:
                    drag += u0 - ux[i, j]
        return drag
        '''
        drag = 0
        for i in range(height):
            drag += - ux[i, 1] + ux[i, width-2]
        drag = drag/height
        #drag = drag - 0.10  # 边界阻力 0.18
        #print(drag)
        return drag


# Compute curl of the macroscopic velocity field:
def curl(ux, uy):
    global ncurl
    ncurl = numpy.roll(uy, -1, axis=1) - numpy.roll(uy, 1, axis=1) - numpy.roll(ux, -1, axis=0) + numpy.roll(ux, 1,
                                                                                                             axis=0)
    return ncurl


'''
def flood():
    global rho, ux, uy, n[0], n[3], n[7], n[1], n[5], n[2], n[4], n[8], n[6], tank, nx4, ny4, nx1, nx2, ny1, ny2, nx3, ny3
    nx1 = n[1] - n[5]
    ny1 = n[3] - n[7]
    nx2 = n[2] - n[6]
    ny2 = n[4] - n[8]
    cosa = (1 / 2) * (2 ** (1 / 2))
    nx3 = nx2 * cosa + ny2 * cosa
    ny3 = nx2 * cosa + ny2 * cosa
    nx4 = nx3 + nx1
    ny4 = ny3 + ny1
    tank = ny4 / nx4
    return tank
'''


def fresh_status():
    while True:
        if kill:
            sys.exit()
        if oncanvas and xdata != None:
            main_window.FreshDetail()
            time.sleep(0.1)
        else:
            main_window.fresh_status()
            time.sleep(0.1)

def fresh_details(event):
    global oncanvas
    oncanvas = True

def close_details(event):
    global oncanvas
    oncanvas = False

xdata = 0
ydata = 0
moving = False
def mouse_move(event):
    global xdata, ydata, moving
    if (not moving and oncanvas) or drawing:
        moving = True
        xdata, ydata = event.xdata, event.ydata
        if not drawing:
            time.sleep(0.01)
        moving = False
        #print(xdata, xdata)


def drawing_mouse_move(event):
    global xdata, ydata
    xdata, ydata = event.xdata, event.ydata
    #print(xdata, xdata)

pen = True
eraser = False
drawing = False
def draw_pressed(event):
    global drawing, nnbarrier, xp, yp, nbarrier, barrier
    try:
        drawing = True
        gen=0
        last_xdata = int(xdata)
        last_ydata = int(ydata)
        if drawing:
            nnbarrier = numpy.zeros((height,width), bool)
            #nnbarrier[barrier] = True
            for i in range(len(xp)):
                nnbarrier[int(yp[i] + height/2), int(xp[i] + width/2)] = True
        while drawing:
            try:
                main_window.Drawing()
                if pen and (xdata != None):
                    print('Pen')
                    xline = numpy.linspace(round(last_xdata), round(xdata), num=50)
                    yline = numpy.linspace(round(last_ydata), round(ydata), num=50)
                    #drawing_mouse_move(event)
                    #nbarrier[int(ydata), int(xdata)] = True
                    #print(nbarrier[int(ydata), int(xdata)])
                    for i in range(50):
                        nnbarrier[int(round(yline[i])), int(round(xline[i]))] = True
                        xp.append(int(round(xline[i]) - width/2))
                        yp.append(int(round(yline[i]) - height/2))
                    last_xdata = int(xdata)
                    last_ydata = int(ydata)
                    fresheq()
                    if update:
                        freshbarrier()
                elif eraser and (xdata != None):
                    print('Eraser')
                    xline = numpy.linspace(round(last_xdata), round(xdata), num=50)
                    yline = numpy.linspace(round(last_ydata), round(ydata), num=50)
                    #drawing_mouse_move(event)
                    #nbarrier[int(ydata), int(xdata)] = True
                    #print(nbarrier[int(ydata), int(xdata)])
                    for i in range(50):
                        if nnbarrier[int(round(yline[i])), int(round(xline[i]))]:
                            nnbarrier[int(round(yline[i])), int(round(xline[i]))] = False
                    xp = []
                    yp = []
                    for i in range(height):
                        for j in range(width):
                            if nnbarrier[i, j]:
                                xp.append(int(j - width/2))
                                yp.append(int(i - height/2))
                    last_xdata = int(xdata)
                    last_ydata = int(ydata)
                    fresheq()
                    if update:
                        freshbarrier()
                else:
                    time.sleep(0.01)
            except:
                print('ERROR')
    except:
        traceback.print_exc()

def thread_draw_pressed(event):
    if not drawing:
        print('1')
        thread_it(draw_pressed, event)

def draw_released(event):
    global drawing
    print('0')
    time.sleep(0.05)
    drawing = False

matplotlib.pyplot.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
matplotlib.pyplot.rcParams['axes.unicode_minus']=False #用来正常显示负号

eqFig = matplotlib.pyplot.figure(num=2, figsize=(5, 3))
eqax = eqFig.add_subplot(111)
eqax.xaxis.grid(True, which='major')
eqax.yaxis.grid(True, which='major')
eqbImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
eqbImageArray[nnbarrier, 3] = 255  # set alpha=255 only at barrier sites
eqbarrierImage = matplotlib.pyplot.imshow(eqbImageArray, origin='lower', interpolation='none')
matplotlib.pyplot.connect('motion_notify_event', mouse_move)
matplotlib.pyplot.connect('figure_enter_event', fresh_details)
matplotlib.pyplot.connect('figure_leave_event', close_details)
matplotlib.pyplot.connect('button_press_event', thread_draw_pressed)
matplotlib.pyplot.connect('button_release_event', draw_released)

ldFig = matplotlib.pyplot.figure(num=3, figsize=(10, 3))
ax = ldFig.add_subplot(111)
ax.set_xlabel(u'代数')
ax.set_ylabel(u'力')
ax.set_title(u'力-代数 曲线')
ax.xaxis.grid(True, which='major')
ax.yaxis.grid(True, which='major')
l1, = ax.plot(list_gen, list_lift, 'b', label=u'升力')
l2, = ax.plot(list_gen, list_drag, 'r', label=u'阻力')
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1])
#ax2 = ldFig.add_subplot(122)
#ax2.set_xlabel(u'代数')
#ax2.set_ylabel(u'阻力(Fx)')
#ax2.set_title(u'阻力-代数 曲线')


theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
fluidImage = matplotlib.pyplot.imshow(curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                      cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')


#matplotlib.pyplot.show()

code_switch_2 = True
def exec_codes():
    global code_switch_2
    code_switch_2 = False
    print(code_switch_2)
    print('EXEC_CODE')
    exec(text_code.get('1.0', 'end'))


def nextGen(gens):
    global start_start, animating#first_st_var, bindable, change_barrier_switch
    '''
    if first_st_var:
        bindable = True
        change_barrier(1)
        first_st_var = False
    if coding_switch:
        if coding.get():
            if code_switch_2:
                threadCode = threading.Thread(target=exec_codes, name='T_Coding')
                threadCode.start()
    count_gen = 0
    for i_ng in range(gens):
        count_gen += 1
        stream()
        collide()
        if count_gen == 20:
            count_gen = 0
            if changeable.get():
                changeable_barrier()
    if write_start.get():
        print('PREWRITING')
        write()
    '''
    print("NEXT GEN")
    for step in range(gens):
        if not changing:
            animating = True
            stream()
            collide()
            animating = False
        else:
            traceback.print_exc()
    fluidImage.set_array(curl(ux, uy))
    barrierImage.set_array(bImageArray)
    print('NEXT GEN CAL DONE')
    main_window.Draw()


save_lock = False
def nextFrame(arg):
    global save_lock, animating,theFig,fluidImage,barrierImage,bImageArray,kill, skip, gen,ux1,uy1,killThreadAnimation, spd,alert, write_switch, changeable, start_start, lcoding, codes, text_code, code_switch_2, contrast, first_write, list_lift, list_drag, list_gen
    if kill:
        sys.exit()
    elif killThreadAnimation:
        print('KILLED')
        sys.exit()
    if arg == 0:
        rang = int(20 * spd)
    else:
        rang = arg
    for step in range(rang):
        if n[3][int(height/2), int(width/2)] >= 10:
            start_start = False
            #killThreadAnimation = True
            main_window.ShowStart()
            #thread_it(main_window.Alert)
            alert = True
            thread_it(play)
            break
        while True:
            if not changing:
                break
            time.sleep(0.001)
        animating=True
        stream()
        collide()
        animating=False
    if not lock_draw:
        try:
            if not (force_vector_switch) or (animation_type == 2 or animation_type == 3):
                if animation_type == 0:
                    fluidImage.set_array(contrast*curl(ux, uy))
                elif animation_type == 1:
                    fluidImage.set_array(contrast*(rho-1))
                elif animation_type == 2:
                    #fluidImage.cla()
                    #fluidImage.streamplot(x, y, ux, uy, density=2.5, color='black', linewidth=0.5, arrowsize=0.5)
                    
                    #fluidImage = theFig.add_subplot(111)
                    save_lock = True
                    theFig.clf()
                    theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                    fluidImage = matplotlib.pyplot.streamplot(x, y, ux, uy, density=1, color='black', linewidth=0.5, arrowsize=0.5)
                    bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                    bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                    barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                    save_lock = False
                elif animation_type == 3:
                    for i in range(int(height/4)):
                        for j in range(int(width/4)):
                            ux1[i, j] = ux[i*4, j*4]
                            uy1[i, j] = uy[i*4, j*4]
                            #u21[i, j] = u2[i*4, j*4]
                    #theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                    #fluidImage = theFig.add_subplot(111)
                    #fluidImage.quiver(x1, y1, ux1, uy1, angles="xy", minlength=0.01)
                    save_lock = True
                    theFig.clf()
                    theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                    fluidImage = matplotlib.pyplot.quiver(x1, y1, ux1, uy1, minlength=0.01)
                    bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                    bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                    barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                    save_lock = False
                    #fluidImage.quiver(x1, y1, ux1, uy1, u21, scale=7, minlength=0, norm=matplotlib.pyplot.Normalize(-0.1, 0.1),cmap=matplotlib.pyplot.get_cmap('bwr'))
                elif animation_type == 4:
                    fluidImage.set_array(contrast*ux)
                elif animation_type == 5:
                    fluidImage.set_array(contrast*uy)
            else:
                for i in range(height):
                        for j in range(width):
                            if barrier[i, j]:
                                xf = j
                                yf = i
                change_animation(main_window.combo_animation_type.currentText())
                force_vector = matplotlib.pyplot.arrow(xf,yf,20*Lift_Drag(False), -20*Lift_Drag(True), width=1)
        except:
            traceback.print_exc()
    if show_lift_drag:
        if len(list_gen) > 1:
            del list_lift[0]
            del list_drag[0]
            del list_gen[0]
        list_lift.append(Lift_Drag(True))
        list_drag.append(Lift_Drag(False))
        list_gen.append(int(gen))
        thread_it(main_window.Draw_ld())
    barrierImage.set_array(bImageArray)
    frames_per_second()
    if write_switch:
        write()
        if first_write:
            first_write = False
    main_window.Draw()

playing = False
def play():
    global playing
    if not playing:
    #process_it(winsound.PlaySound,"SystemExit", winsound.SND_ALIAS)
    #thread_it(winsound.PlaySound,"SystemExit", winsound.SND_ALIAS)
        playing = True
        winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
        playing = False
    

gps = 0
fps = 0
t0 = 0
last_gen = 0
def frames_per_second():
    global t0, fps, gps, last_gen
    t1 = time.perf_counter()
    dt = t1 - t0
    t0 = t1
    fps = '%.1f' % (1.0/dt)
    gps = '%.1f' % ((gen - last_gen) / dt)
    last_gen = int(gen)



def thread_it(func, *args):
    '''将函数打包进线程'''
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()

def process_it(func, *args):
    '''将函数打包进程'''
    p = multiprocessing.Process(target=func, args=args)
    p.start()

def starter():
    global start_start, first_st_var, bindable, change_barrier_switch
    while 1:
        if kill:
            sys.exit()
        elif killThreadAnimation:
            print('KILLED')
            sys.exit()
        if start_start:
            #if not lock_draw:
                #thread_it(main_window.Draw)
            #thread_it(thread_it, main_window.Draw)
            #t = threading.Thread(target=main_window.Draw)
            #t.start()
            nextFrame(0)
            #t0=time.perf_counter()
            #print(time.perf_counter()-t0)
            #t.join()
        else:
            time.sleep(0.1)


def HelpPause():
    global start_start
    if start_start:
        start_start = False
        main_window.ShowStart()


def HelpStart():
    global start_start, gen
    if not start_start:
        start_start = True
        main_window.HideStart()


spd = 1


def HelpAniSpd(h_spd):
    global spd
    spd = float(h_spd)
    # print('Animation Speed: ', spd)


draw_start_switch = True


def draw_continue(event=None):
    global canvaseq, draw_start_switch, nnbarrier
    if not draw_start_switch:
        canvaseq.get_tk_widget().unbind('<Motion>')
    else:
        # print (event.x, event.y)
        canvaseq.get_tk_widget().bind('<Motion>', draw_continue)
        dbx = ((float(event.x) - 83) / 347) * width
        dby = (1 - (float(event.y) - 37) / 230) * height
        print(dbx, dby)
        if not nnbarrier[int(round(dby)), int(round(dbx))]:
            nnbarrier[int(round(dby)), int(round(dbx))] = True
            fresheq()


def draw_start(event=None):
    global canvaseq, drawing_start, draw_start_switch, nnbarrier, equation_window
    draw_start_switch = True
    if drawing_start.get():
        print('DRAWING ON')
        # print event.x, event.y
        canvaseq.get_tk_widget().bind('<Motion>', draw_continue)
        dbx = ((float(event.x) - 83) / 347) * width
        dby = (1 - (float(event.y) - 37) / 230) * height
        print(dbx, dby)
        if not nnbarrier[int(round(dby)), int(round(dbx))]:
            nnbarrier[int(round(dby)), int(round(dbx))] = True
            fresheq()


def Help_draw_start(*argnone):
    global drawing_start
    drawing_start = True


def HelpBindDraw():
    global canvaseq, draw_start_switch


def draw_stop(argnone):
    global draw_start_switch
    print('DRAWING OFF')
    draw_start_switch = False




agln = 0
def roteq(agl):
    global nnbarrier, agln  # , nxp, nyp
    # print(xp, '\n', yp)
    nxp = []
    nyp = []
    nnbarrier = numpy.zeros((height, width), bool)
    agln = agl
    cosa = float(sympy.cos(agln))  # 预运算
    sina = float(sympy.sin(agln))
    try:
        for j in range(len(xp)):
            nxp.append(round(xp[j] * cosa - yp[j] * sina))
            nyp.append(round(yp[j] * cosa + xp[j] * sina))
            nnbarrier[int(nyp[j] + height / 2), int(nxp[j] + width / 2)] = True
    except:
        traceback.print_exc()
        print('ERROR: \n ROTEQ: Index does not match')
    # Equation(1, 1, 1, 1, 1, True)
    #fresheq()


def HelpRot(aglh):
    aglrot = 0
    brk = False
    while not brk:
        aglrot += pi / 90
        roteq(aglrot)
        freshbarrier()
        time.sleep(0.01)
        if aglrot >= 2 * pi:
            brk = True


def fresheq():
    global nnbarrier, canvaseq, nbarrier, change_barrier_switch, eqbarrierImage, eqbImageArray
    eqbImageArray[:, :, 3] = 0  # 刷新eqBarrier图像
    eqbImageArray[nnbarrier, 3] = 255
    eqbarrierImage.set_array(eqbImageArray)
    time.sleep(0.01)
    main_window.Draw_eq()

def initeq():
    global nnbarrier, canvaseq, nbarrier, change_barrier_switch, eqbarrierImage, eqbImageArray, xp, yp
    eqbImageArray[:, :, 3] = 0  # 刷新eqBarrier图像
    eqbImageArray[barrier, 3] = 255
    eqbarrierImage.set_array(eqbImageArray)
    xp = []
    yp = []
    for i in range(height):
        for j in range(width):
            if barrier[i, j]:
                xp.append(j - width / 2)
                yp.append(i - height / 2)
    time.sleep(0.01)
    main_window.Draw_eq()

def freshbarrier():
    global nnbarrier, nbarrier, change_barrier_switch, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood, changing
    while True:
        if not animating:
            break
        time.sleep(0.001)
    changing = True
    barrier = nnbarrier
    barrier3 = numpy.roll(barrier, 1, axis=0) 
    barrier7 = numpy.roll(barrier, -1, axis=0)
    barrier1 = numpy.roll(barrier, 1, axis=1)
    barrier5 = numpy.roll(barrier, -1, axis=1)
    barrier2 = numpy.roll(barrier3, 1, axis=1)
    barrier4 = numpy.roll(barrier3, -1, axis=1)
    barrier8 = numpy.roll(barrier7, 1, axis=1)
    barrier6 = numpy.roll(barrier7, -1, axis=1)
    bImageArray[:, :, 3] = 0  # 刷新Barrier图像
    bImageArray[barrier, 3] = 255
    barrierImage.set_array(bImageArray)
    change_barrier_switch = False
    blood[:, :] = 0
    blood[barrier] = 100
    main_window.Draw()
    changing = False

def freshnbarrier():
    global nnbarrier, nbarrier, change_barrier_switch, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood, changing
    changing = True
    while True:
        if not animating:
            barrier = nbarrier
            barrier3 = numpy.roll(barrier, 1, axis=0)
            barrier7 = numpy.roll(barrier, -1, axis=0)
            barrier1 = numpy.roll(barrier, 1, axis=1)
            barrier5 = numpy.roll(barrier, -1, axis=1)
            barrier2 = numpy.roll(barrier3, 1, axis=1)
            barrier4 = numpy.roll(barrier3, -1, axis=1)
            barrier8 = numpy.roll(barrier7, 1, axis=1)
            barrier6 = numpy.roll(barrier7, -1, axis=1)
            bImageArray[:, :, 3] = 0  # 刷新Barrier图像
            bImageArray[barrier, 3] = 255
            barrierImage.set_array(bImageArray)
            change_barrier_switch = False
            blood[:, :] = 0
            blood[barrier] = 100
            main_window.Draw()
            break
        else:
            time.sleep(0.03)
    changing = False

def Equation(inputx, inputy, tstart, tend, ex):
    global change_barrier_switch, nbarrier, nnbarrier, start_start, canvaseq, ninputx, ninputy, ix, iy, xp, yp
    try:
        #xp = []
        #yp = []
        x, y, t = sympy.symbols("x y t", real=True)
        equation_xs = inputx.split(';')
        for i in range(len(equation_xs)):
            if equation_xs[i] == '':
                del equation_xs[i]
        equation_ys = inputy.split(';')
        for i in range(len(equation_ys)):
            if equation_ys[i] == '':
                del equation_ys[i]
        print(equation_xs)
        # print equation_xs, equation_ys
        i1 = 0
        w1 = len(equation_xs)
        if len(equation_xs) == len(equation_ys):
            st = int(tstart)
            ed = int(tend)
            exa = int(ex)
            all = exa * ed - exa * st
            steps = w1 * all
            step = 0
            i1 += 1
            i_eq = 0
            if id(nnbarrier) == id(barrier):
                nnbarrier = numpy.zeros((height, width), bool)
                for i in range(len(xp)):
                    nnbarrier[int(yp[i] + height/2), int(xp[i] + width/2)] = True
            eqbImageArray[:, :, 3] = 0  # 刷新eqBarrier图像
            eqbImageArray[nnbarrier, 3] = 255
            eqbarrierImage.set_array(eqbImageArray)
            for value in equation_xs:
                if value == '':
                    equation_xs.remove(value)
            for value in equation_ys:
                if value == '':
                    equation_ys.remove(value)
            # delta_progressbar_value = 85/len(equation_xs)
            for value in equation_xs:
                print(i_eq)
                ix = ''
                iy = ''
                ninputx = 'ix=' + value
                ninputy = 'iy=' + equation_ys[i_eq]
                #ix = 10 * sin(t)
                #print('old:', ix)
                print(ninputx)
                print(ninputy)
                strx = 'global ix \n' + ninputx
                stry = 'global iy \n' + ninputy
                exec(strx)
                exec(stry)
                # eval(ninputy)
                i_eq += 1
                
                print('ix=', ix)
                print('iy=', iy)
                # Ex = 10 * sympy.sin(t)
                Ex = sympy.sympify(ix)
                Ey = sympy.sympify(iy)
                # Ex = 16 * ((sympy.sin(t)) ** 3)
                # Ey = 13 * sympy.cos(t) - 5 * sympy.cos(2 * t) - 2 * sympy.cos(3 * t) - sympy.cos(4 * t)
                # Ex = input()
                # Ey = input()
                
                for tent in range(exa * st, exa * ed, 1):
                    step += 1
                    main_window.SetEqProgressBar(100*step/steps)
                    print(step/steps)
                    nt = tent / exa
                    x = int(round(Ex.subs(t, nt)) + width / 2)
                    y = int(round(Ey.subs(t, nt)) + height / 2)
                    xp.append(x - width / 2)
                    yp.append(y - height / 2)
                    nnbarrier[y, x] = True
                # progressbar_value = n * 85/len(equation_xs) + 15
                # ProgressbarEq['value'] = progressbar_value
                print("-> FRESHEQ")
                fresheq()
            if update:
                freshbarrier()
    except:
        traceback.print_exc()
        main_window.Alert()



switch_eq = True




coding_switch = False
def codings():
    global coding, text_code, coding_switch, scale_u0
    coding_switch = True
    coding_window = tkinter.Toplevel(control_window)
    coding_window.geometry('800x600')

    coding = tkinter.BooleanVar()
    CheckCoding = tkinter.Checkbutton(coding_window, text='编程', variable=coding, onvalue=True, offvalue=False)
    CheckCoding.place(x=600, y=400)

    text_code = tkinter.Text(coding_window, width=40, height=15)
    text_code.insert(tkinter.END, "global u0    # Example\n"
                                  "while True:\n"
                                  "    u1 = u0\n"
                                  "    while True:\n"
                                  "        u1 += 0.001\n"
                                  "        scale_u0.set(u1)\n"
                                  "        if u1 >= 0.11:\n"
                                  "            break\n"
                                  "        time.sleep(0.01)\n"
                                  "    while True:\n"
                                  "        u1 += -0.001\n"
                                  "        scale_u0.set(u1)\n"
                                  "        if u1 <= 0.001:\n"
                                  "            break\n"
                                  "        time.sleep(0.01)\n")
    text_code.place(x=2, y=2)

    coding_window.mainloop()

def performance():  # 开发中
    global gen
    perf = True
    time_performance = 0
    while perf:
        time_performance = time_performance + 0.11  # 辅助开发功能
        time_left = 15 - time_performance
        time.sleep(0.1)
        os.system('cls')
        print('Generation:', gen)
        print('Time left:', time_left)
        print('Lift=', lift)
        print('drag=', drag)
        print('v0=', u0)
        if time_performance >= 15:  # 辅助开发功能
            perf = False


def help_u1(h_u):
    global u1
    u1 = float(h_u)
    # print('v0: ', u1)


def help_viscosity(h_viscosity):
    global nviscosity
    nviscosity = float(h_viscosity)
    # print('viscosity: ', nviscosity)


def change_barrier(barrier_set):
    global change_barrier_switch, nbarrier
    if barrier_set == u'(默认)':
        pass
    else:
        nbarrier = numpy.zeros((height, width), bool)
        if barrier_set == u'平板 短   垂直':
            for i_change_barrier_switch in range(16):
                nbarrier[int((height / 2) + 8 - i_change_barrier_switch), int(width / 2)] = True
        elif barrier_set == u'平板 短   水平':
            for i_change_barrier_switch in range(16):
                nbarrier[int(height / 2), int((width / 2) + 8 - i_change_barrier_switch)] = True
        elif barrier_set == u'平板 短   α=45°':
            for i_change_barrier_switch in range(16):
                nbarrier[int((height / 2) - 8 + i_change_barrier_switch), int((
                        (width / 2) - i_change_barrier_switch - 8))] = True
        elif barrier_set == u'倒三角型（平角头）':
            for i_change_barrier_switch in range(8):
                nbarrier[
                int((height / 2) - (8 - i_change_barrier_switch)):int(
                    (height / 2) + (8 - i_change_barrier_switch)),
                int((width / 2) - 4 + (i_change_barrier_switch))] = True
        elif barrier_set == u'正三角型（钝角头）':
            for i_change_barrier_switch in range(8):
                nbarrier[
                int((height / 2) - (8 - i_change_barrier_switch)):int(
                    (height / 2) + (8 - i_change_barrier_switch)),
                int((width / 2) + 4 - (i_change_barrier_switch))] = True
        elif barrier_set == u'机翼 简单 α=0°':
            nbarrier[int(height / 2), 34:50] = True
            nbarrier[int(height / 2) - 1, 8:34] = True
            nbarrier[int(height / 2), 7] = True
            nbarrier[int(height / 2) + 1, 8] = True
            nbarrier[int(height / 2) + 2, 9] = True
            nbarrier[int(height / 2) + 2, 10] = True
            nbarrier[int(height / 2) + 3, 11:15] = True
            nbarrier[int(height / 2) + 4, 15:24] = True
            nbarrier[int(height / 2) + 3, 24:32] = True
            nbarrier[int(height / 2) + 2, 32:39] = True
            nbarrier[int(height / 2) + 1, 39:46] = True
        elif barrier_set == u'机翼 简单 α=0° 襟翼展开':
            nbarrier[int(height / 2), 34:50] = True
            nbarrier[int(height / 2) - 1, 8:34] = True
            nbarrier[int(height / 2), 7] = True
            nbarrier[int(height / 2) + 1, 8] = True
            nbarrier[int(height / 2) + 2, 9] = True
            nbarrier[int(height / 2) + 2, 10] = True
            nbarrier[int(height / 2) + 3, 11:15] = True
            nbarrier[int(height / 2) + 4, 15:24] = True
            nbarrier[int(height / 2) + 3, 24:32] = True
            nbarrier[int(height / 2) + 2, 32:39] = True
            nbarrier[int(height / 2) + 1, 39:46] = True
            for i_change_barrier_switch in range(1, 6):  # 襟翼开
                nbarrier[int((height / 2) - 3 - i_change_barrier_switch), int(
                    36 + 2 * i_change_barrier_switch)] = True
                nbarrier[int((height / 2) - 3 - i_change_barrier_switch), int(
                    36 + 2 * i_change_barrier_switch + 1)] = True
        elif barrier_set == u'正方形（16x16）':
            for i_change_barrier_switch in range(-8, 9, 1):
                for j_change_barrier_switch in range(-8, 9, 1):
                    nbarrier[int(height / 2 + i_change_barrier_switch), int(
                        width / 2 + j_change_barrier_switch)] = True
        elif barrier_set == u'小河0':
            for i_change_barrier_switch in range(height):
                for j_change_barrier_switch in range(width):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
            for i_change_barrier_switch in range(0, 2, 1):
                nbarrier[int(height / 2 + i_change_barrier_switch), :] = False
        elif barrier_set == u'小河1':
            for i_change_barrier_switch in range(height):
                for j_change_barrier_switch in range(width):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
            for i_change_barrier_switch in range(-2, 3, 1):
                nbarrier[int(height / 2 + i_change_barrier_switch), :] = False
        elif barrier_set == u'小河2':
            for i_change_barrier_switch in range(height):
                for j_change_barrier_switch in range(width):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
            for i_change_barrier_switch in range(-4, 5, 1):
                nbarrier[int(height / 2 + i_change_barrier_switch), :] = False
        elif barrier_set == u'小河3':
            for i_change_barrier_switch in range(height):
                for j_change_barrier_switch in range(width):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
            for i_change_barrier_switch in range(-4, 5, 1):
                for j_change_barrier_switch in range(0, int(width / 4), 1):
                    nbarrier[int(height / 2 + i_change_barrier_switch), j_change_barrier_switch] = False
                for j_change_barrier_switch in range(int(width / 4), int(width / 2), 1):
                    nbarrier[int(height / 2 + i_change_barrier_switch - 1), j_change_barrier_switch] = False
                for j_change_barrier_switch in range(int(width / 2), int(3 * width / 4), 1):
                    nbarrier[int(height / 2 + i_change_barrier_switch - 2), j_change_barrier_switch] = False
                for j_change_barrier_switch in range(int(3 * width / 4), width, 1):
                    nbarrier[int(height / 2 + i_change_barrier_switch - 3), j_change_barrier_switch] = False
        elif barrier_set == u'小河(bug)':
            move1 = 0
            for i_change_barrier_switch in range(0, height):
                for j_change_barrier_switch in range(0, width, 2):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch - move1] = True
                    if move1 == 0:
                        move1 = 1
                    else:
                        move1 = 0
            nbarrier[:, 0] = True
            for i_change_barrier_switch in range(-4, 5):
                nbarrier[int(height / 2 + i_change_barrier_switch), :] = False
            for i_change_barrier_switch in range(-12, -4):
                for j_change_barrier_switch in range(30, 50):
                    nbarrier[int(height / 2 + i_change_barrier_switch), j_change_barrier_switch] = False
        elif barrier_set == u'多孔介质1':
            move1 = 0
            for i_change_barrier_switch in range(0, height, 4):
                for j_change_barrier_switch in range(int(width/8), int(width/2), 4):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
        elif barrier_set == u'多孔介质2':
            move1 = 0
            for i_change_barrier_switch in range(0, height, 8):
                for j_change_barrier_switch in range(int(width/8), int(width/2), 8):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
        elif barrier_set == u'射流':
            move1 = 0
            for i_change_barrier_switch in range(0, height):
                for j_change_barrier_switch in range(int(width/8), int(width/2)):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = True
            for i_change_barrier_switch in range(int(height/2-3), int(height/2+3)):
                for j_change_barrier_switch in range(0, width-1):
                    nbarrier[i_change_barrier_switch, j_change_barrier_switch] = False
        freshnbarrier()



def Debug():
    while 1:
        print('u0 =', u0, '\n',
              'viscosity =', viscosity, '\n',
              'Animation Speed =', spd, '\n',
              'Barrier Selected:', barrier_set, '\n')
        Lift_Drag()
        time.sleep(0.25)
        os.system('cls')


def HelpDebug():
    threadDebug = threading.Thread(target=Debug, name='T_Debug')  # GUI线程
    threadDebug.start()


def write():
    global gen, ncurl, first_write
    print('WRITE GEN=', gen)
    # os.remove('data.txt')
    if first_write:
        output = open('data.LBM', 'w')  # 重新写入
        first_write = False
    else:
        output = open('data.LBM', 'a')  # 继续写入
    # output.write('Gen=')
    # output.write(str(gen))
    # output.write(';')
    for i_write in range(height):
        for j_write in range(width):
            ostring = str(round(ncurl[i_write, j_write], 6))
            output.write(ostring)
            '''
            ostring = str(ncurl[i_write, j_write])
            ostr = ostring[:6]
            for i_str in range(len(ostring)):
                if ostring[i_str] == 'e':
                    es = float(ostring[i_str+1:])
                    ostr = str(float(ostr) * numpy.power(10, es))
            output.write(ostr)
            '''
            if j_write != width - 1:
                output.write(',')
        output.write('\n')
    # output.write(';')
    output.close()


list_text = numpy.zeros((height, width), float)


def file_in(heightin, widthin, frame_number, filename):
    global ncurl, list_text
    file = open(filename, "r")
    row = []
    for i_line_height in range((frame_number - 1) * height, frame_number * height):
        row.append(linecache.getline(filename, i_line_height))
    i_cl = 0
    for i_line in range(len(row)):
        line = row[i_line].strip().split(',')
        # print(line)
        j_cl = 0
        for words in line:
            # print (words)
            if words != '':
                list_text[i_cl, j_cl] = float(words)
            j_cl += 1
        i_cl += 1
    file.close()
    ncurl = list_text




def animate_file_in(filename):
    global height, width, barrier, start_start, PauseButton, StartButton, t0
    if start_start:
        HelpPause()
    frame_number = 0
    file = open(filename, "r")
    lines_count = 0
    for line in file:
        lines_count += 1
    all_frames = lines_count / height
    file.close()
    print(all_frames)
    t0 = 0
    bImageArray[:, :, 3] = 0  # 刷新Barrier图像
    barrierImage.set_array(bImageArray)
    for i_frames in range(int(all_frames)):
        frame_number += 1
        file_in(height, width, frame_number, filename)

        fluidImage.set_array(ncurl)  # 刷新图像

        main_window.Draw()
        time.sleep(0.03)
        frames_per_second()

deep = 225
nbImageArray = numpy.zeros((height, width))
blood = numpy.ones((height, width))


def changeable_barrier():
    global rho, bImageArray, deep, height, width, nbImageArray, n, barrier, nbarrier, change_barrier_switch, blood, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6
    blood[barrier] += - 1000 * (numpy.abs(n[5][barrier5]- n[1][barrier5]) + numpy.abs(n[1][barrier1] - n[5][barrier1]) +
                                  numpy.abs(n[7][barrier7] - n[3][barrier7]) + numpy.abs(n[3][barrier3] - n[7][barrier3]) +
                                  numpy.abs(n[2][barrier2] - n[6][barrier2]) + numpy.abs(n[6][barrier6] - n[2][barrier2]) +
                                  numpy.abs(n[8][barrier8] - n[4][barrier8]) + numpy.abs(n[4][barrier4] - n[8][barrier4]))
    #print(blood[45, 0])
    for i in range(height):
        for j in range(width):
            if blood[i, j] < 0:
                #print('DELETE')
                nbarrier[i, j] = 0
                change_barrier_switch = True
    if (True in nbarrier) == False:
        main_window.checkbox_changeable.setChecked(False)
    #freshnbarrier()
     


def change_animation(type):
    global fliudImage, animation_type, lock_draw, ux, uy, x, y, ux1, uy1
    global theFig
    global fluidImage
    global bImageArray
    global barrierImage
    #matplotlib.pyplot.close(1)
    if not lock_draw:
        try:
            lock_draw = True
            while True:
                if not save_lock:
                    break
                time.sleep(0.01)
            theFig.clf() # 请勿删去否则plt.draw速度减慢
            if type == u'旋度动画':
                animation_type = 0
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                fluidImage = matplotlib.pyplot.imshow(contrast*curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                            cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
                bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                
                #fluidImage = matplotlib.pyplot.imshow(curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                                    #cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
            elif type == u'密度动画':
                animation_type = 1
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                fluidImage = matplotlib.pyplot.imshow(contrast*(rho-1), origin='lower', norm=matplotlib.pyplot.Normalize(-0.075, 0.075),
                                                    cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
                bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                '''
                fluidImage = matplotlib.pyplot.imshow(rho, origin='lower', norm=matplotlib.pyplot.Normalize(0.9, 1.1),
                                                    cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
                                            '''
            elif type == u'流线':
                animation_type = 2
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                #fluidImage = theFig.add_subplot(111)
                fluidImage = matplotlib.pyplot.streamplot(x, y, ux, uy, density=1, color='black', linewidth=1)
                bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                #theFig.show()
                #main_window.Draw()
                #bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                #bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                #barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                #ax.clear()
            elif type == u'速度矢量':
                animation_type = 3
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                #print('11:',height)
                for i in range(int(height/4)):
                    for j in range(int(width/4)):
                        ux1[i, j] = ux[i*4, j*4]
                        uy1[i, j] = uy[i*4, j*4]
                        #u21[i, j] = u2[i*4, j*4]
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                #fluidImage = theFig.add_subplot(111)
                #fluidImage.quiver(x1, y1, ux1, uy1, angles="xy", minlength=0.01)
                fluidImage = matplotlib.pyplot.quiver(x1, y1, ux1, uy1, minlength=0.01)
                bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
            elif type == u'水平速度':
                animation_type = 4
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                fluidImage = matplotlib.pyplot.imshow(contrast*ux, origin='lower', norm=matplotlib.pyplot.Normalize(-0.3, 0.3),
                                                    cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
                bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
            elif type == u'垂直速度':
                animation_type = 5
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                fluidImage = matplotlib.pyplot.imshow(contrast*uy, origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                                    cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
                bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
            main_window.Draw()
            lock_draw = False
        except:
            traceback.print_exc()

def file_import(filename):
    global ux, uy, rho, edge, nwidth, nheight, gen, n, nbarrier, change_barrier_switch, nnbarrier, xp, yp, list_gen, list_lift, list_drag, last_gen
    try:
        file = numpy.load(filename)
        #last_gen = 0
        nheight = int(file['height'])
        nwidth = int(file['width'])
        main_window.Reset()
        list_lift = []
        list_drag = []
        list_gen = []
        gen = int(file['gen'])
        edge = int(file['edge'])
        n = file['n']
        nbarrier = file['barrier']
        ux = file['ux']
        uy = file['uy']
        rho = file['rho']
        nnbarrier=nbarrier
        xp = []
        yp = []
        for i in range(height):
            for j in range(width):
                if nnbarrier[i, j]:
                    xp.append(j - width / 2)
                    yp.append(i - height / 2)
        if not start_start:
            freshbarrier()
        else:
            change_barrier_switch = True
        fresheq()
        change_animation(main_window.combo_animation_type.currentText())
        main_window.ld_window.Draw()
        main_window.Draw()
        #n[0]=n[0],n[3]=n[3],n[7]=n[7],n[1]=n[1],n[5]=n[5],n[2]=n[2],n[8]=n[8],n[6]=n[6],n[4]=n[4],barrier=barrier
    except:
        traceback.print_exc()


class Main_window(QWidget):
    def __init__(self):
        super(Main_window, self).__init__()
        global theFig, fluidImage, barrierImage
        # 图标
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle('LBM流体力学数值模拟计算器')

        # 字体
        fontId = QFontDatabase.addApplicationFont("fontawesome-webfont.ttf")
        fontName = QFontDatabase.applicationFontFamilies(fontId)[0]
        self.font = QFont(fontName, 20)
        self.font_status = QFont(fontName, 15)
        self.font_menu = QFont(fontName)

        
        # 图像
        #self.figure = matplotlib.pyplot.figure(facecolor='#FFD7C4') #可选参数,facecolor为背景颜色
        self.canvas = FigureCanvas(theFig)
        self.canvas.setCursor(QCursor(Qt.CrossCursor))

        #子窗口
        self.equation_window = Equation_window()
        self.lattice_window = Lattice_window()
        self.lattice_window.signal.connect(lambda:self.ChangeLattice(nheight, nwidth))
        self.author_window = Author_window()
        self.instructor_window = Instructor_window()
        self.thanks_window = Thanks_window()
        self.ld_window = Ld_window()
        self.alert_window = Alert_window()

        #复选框
        self.checkbox_changeable = QCheckBox('可变障碍（侵蚀作用）',self)
        self.checkbox_changeable.stateChanged.connect(self.changeable_barrier)

        self.checkbox_force = QCheckBox('受力矢量',self)
        self.checkbox_force.stateChanged.connect(self.ForceVector)

        # 按钮
        self.button_start = QPushButton()
        self.button_start.setFont(self.font)
        self.button_start.setText("")
        self.button_start.setFixedHeight(50)
        self.button_pause = QPushButton()
        self.button_pause.setFont(self.font)
        self.button_pause.setText("")
        self.button_pause.setFixedHeight(50)
        self.button_next20gen = QPushButton("下20代")
        self.button_next20gen.setFixedHeight(50)

        self.button_import = QPushButton()
        self.button_import.setText("导入")
        self.button_import.setFixedHeight(50)
        
        self.button_export = QPushButton()
        self.button_export.setText("导出")
        self.button_export.setFixedHeight(50)

        self.button_equation = QPushButton("障碍方程")

        self.button_record = QToolButton()
        self.button_record.setText("录制")
        self.button_record.setCheckable(True)
        self.button_record.setChecked(False)
        self.button_record.setAutoRaise(True)
        self.button_record.clicked.connect(self.Record)
        self.button_record.setFixedHeight(50)
        #self.button_record.setStyleSheet()

        self.button_reset = QPushButton()
        self.button_reset.setText("重置") 
        self.button_reset.setFixedHeight(50)

        # 按钮连接事件
        self.button_start.clicked.connect(HelpStart)
        self.button_pause.clicked.connect(HelpPause)
        self.button_import.clicked.connect(self.ChooseFile)
        self.button_next20gen.clicked.connect(lambda: thread_it(nextFrame, 20))
        self.button_equation.clicked.connect(self.EquationWindow)
        self.button_export.clicked.connect(self.Export)
        self.button_record.clicked.connect(self.Record)
        self.button_reset.clicked.connect(self.Reset)

        # 滑动条
        self.slider_u0=QSlider(Qt.Horizontal)
        self.slider_u0.setMinimum(0)#最小值,100倍，下同
        self.slider_u0.setMaximum(120)#最大值
        self.slider_u0.setSingleStep(1)#步长
        self.slider_u0.setTickPosition(QSlider.TicksBelow)#设置刻度位置，在下方
        self.slider_u0.setTickInterval(30)#设置刻度间隔
        self.slider_u0.setValue(100)

        self.slider_viscosity=QSlider(Qt.Horizontal)
        self.slider_viscosity.setMinimum(5)#最小值
        self.slider_viscosity.setMaximum(200)#最大值
        self.slider_viscosity.setSingleStep(1)#步长
        self.slider_viscosity.setTickPosition(QSlider.TicksBelow)#设置刻度位置，在下方
        self.slider_viscosity.setTickInterval(48)#设置刻度间隔
        self.slider_viscosity.setValue(20)

        self.slider_animation_speed = QSlider(Qt.Horizontal)
        self.slider_animation_speed.setMinimum(0)  # 最小值
        self.slider_animation_speed.setMaximum(400)  # 最大值
        self.slider_animation_speed.setSingleStep(1)  # 步长
        self.slider_animation_speed.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置，在下方
        self.slider_animation_speed.setTickInterval(50)  # 设置刻度间隔
        self.slider_animation_speed.setValue(100)

        self.slider_animation_contrast = QSlider(Qt.Horizontal)
        self.slider_animation_contrast.setMinimum(0)  # 最小值
        self.slider_animation_contrast.setMaximum(200)  # 最大值
        self.slider_animation_contrast.setSingleStep(1)  # 步长
        self.slider_animation_contrast.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置，在下方
        self.slider_animation_contrast.setTickInterval(50)  # 设置刻度间隔
        self.slider_animation_contrast.setValue(100)

        # 标签
        self.label_status_gen = QLabel()
        self.label_status_gen.setText("代数："+"0 代")
        self.label_status_gen.setFixedHeight(25)

        self.label_status_frame = QLabel()
        self.label_status_frame.setText("帧率："+"0 帧/秒")
        self.label_status_frame.setFixedHeight(25)

        self.label_status_gps = QLabel()
        self.label_status_gps.setText("代率："+"0 代/秒")
        self.label_status_gps.setFixedHeight(25)

        self.label_status_record = QLabel()
        self.label_status_record.setText("障碍：不可变")
        #self.label_status_record.setHidden(True)
        self.label_status_record.setFixedHeight(25)

        self.label_status_light1 = QLabel()
        self.label_status_light1.setFont(self.font_status)
        self.label_status_light1.setText("")
        self.label_status_light1.setStyleSheet("color: green")
        self.label_status_light1.setFixedHeight(25)

        self.label_status_light2 = QLabel()
        self.label_status_light2.setFont(self.font_status)
        self.label_status_light2.setText("")
        self.label_status_light2.setStyleSheet("color: green")
        self.label_status_light2.setFixedHeight(25)

        self.label_status_light3 = QLabel()
        self.label_status_light3.setFont(self.font_status)
        self.label_status_light3.setText("")
        self.label_status_light3.setStyleSheet("color: green")
        self.label_status_light3.setFixedHeight(25)

        self.label_frame = QLabel()
        self.label_frame.setText("打开")
        self.label_frame.setFixedHeight(25)

        self.label_fluid = QLabel()
        self.label_fluid.setText("流动参数：")
        self.label_fluid.setFixedHeight(25)

        self.label_u0 = QLabel()
        self.label_u0.setText("来流速度")

        self.label_show_u0 = QLabel()
        self.slider_u0.valueChanged.connect(self.Change_u0)
        self.label_show_u0.setText(str('%.3f' % (self.slider_u0.value() / 1000)))

        self.label_viscosity = QLabel()
        self.label_viscosity.setText("粘性系数")

        self.label_show_viscosity = QLabel()
        self.slider_viscosity.valueChanged.connect(self.Change_viscosity)
        self.label_show_viscosity.setText(str('%.3f' % (self.slider_viscosity.value() / 1000)))

        self.label_barrier = QLabel()
        self.label_barrier.setText("障碍参数：")
        self.label_barrier.setFixedHeight(25)

        self.label_barrierset = QLabel()
        self.label_barrierset.setText("障碍预设")

        self.label_animation = QLabel()
        self.label_animation.setText("动画参数：")
        self.label_animation.setFixedHeight(25)

        self.label_animation_type = QLabel()
        self.label_animation_type.setText("动画类型")

        self.label_animation_speed = QLabel()
        self.label_animation_speed.setText("动画速度")

        self.label_show_animation_speed = QLabel()
        self.slider_animation_speed.valueChanged.connect(self.Change_animation_speed)
        self.label_show_animation_speed.setText(str('%.2f' % (self.slider_animation_speed.value() / 100)))

        self.label_animation_contrast = QLabel()
        self.label_animation_contrast.setText("对比度")

        self.label_show_animation_contrast = QLabel()
        self.slider_animation_contrast.valueChanged.connect(self.Change_animation_contrast)
        self.label_show_animation_contrast.setText(str('%.2f' % (self.slider_animation_contrast.value() / 100)))

        # 框线
        '''
        self.frame_menu = QFrame()  # 菜单栏下划线
        self.frame_menu.resize(100, 100)
        self.frame_menu.setFrameShape(QFrame.Box)
        self.frame_menu.setMidLineWidth(1)
        self.frame_menu.setLineWidth(1)
        self.frame_menu.setFrameShadow(QFrame.Sunken)
        self.frame_menu.move(250, 250)
        '''

        self.frame_fluid = QFrame()
        self.frame_fluid.resize(100, 100)
        self.frame_fluid.setFrameShape(QFrame.Panel)
        self.frame_fluid.setMidLineWidth(1)
        self.frame_fluid.setLineWidth(1)
        self.frame_fluid.setFrameShadow(QFrame.Sunken)

        self.frame_barrier = QFrame()
        self.frame_barrier.resize(100, 100)
        self.frame_barrier.setFrameShape(QFrame.Panel)
        self.frame_barrier.setMidLineWidth(1)
        self.frame_barrier.setLineWidth(1)
        self.frame_barrier.setFrameShadow(QFrame.Sunken)

        self.frame_animation = QFrame()
        self.frame_animation.resize(100, 100)
        self.frame_animation.setFrameShape(QFrame.Panel)
        self.frame_animation.setMidLineWidth(1)
        self.frame_animation.setLineWidth(1)
        self.frame_animation.setFrameShadow(QFrame.Sunken)

        # 下拉菜单
        self.combo_barrier = QComboBox()
        self.combo_barrier.addItems(['(默认)', '平板 短   垂直', '平板 短   水平', '平板 短   α=45°', '倒三角型（平角头）',
                                     '正三角型（钝角头）', '机翼 简单 α=0°', '机翼 简单 α=0° 襟翼展开', '正方形（16x16）',
                                     '小河1', '小河2', '多孔介质1', '多孔介质2', '射流'])
        self.combo_barrier.activated.connect(self.ChangeBrrierComboBox)

        self.combo_animation_type = QComboBox()
        self.combo_animation_type.addItems(['旋度动画', '密度动画','流线', '速度矢量', '水平速度', '垂直速度'])
        #print(self.combo_barrier.currentIndex())
        self.combo_animation_type.activated.connect(lambda:self.ChangeAnimationComboBox(False, self.combo_barrier.currentIndex()))
        
        # 设置布局
        #layout_upndown = QGridLayout() # 适应布局
        layout_window = QHBoxLayout() # 全局布局
        layout_cnb = QVBoxLayout() # canvas and button
        layout_status = QHBoxLayout()
        layout_button = QHBoxLayout()
        layout_snf = QGridLayout() # sliders and functions

        layout_status.addWidget(self.label_status_gen)
        layout_status.addWidget(self.label_status_frame)
        layout_status.addWidget(self.label_status_gps)
        layout_status.addWidget(self.label_status_record)
        layout_lights = QHBoxLayout()
        layout_lights.addWidget(self.label_status_light1)
        layout_lights.addWidget(self.label_status_light2)
        layout_lights.addWidget(self.label_status_light3)
        widget_lights = QWidget()
        widget_lights.setLayout(layout_lights)
        widget_lights.setFixedWidth(90)
        #layout_status.addWidget(widget_lights)
        #layout_status.addWidget(self.label_status_light1)
        widget_status = QWidget()
        widget_status.setLayout(layout_status)
        widget_status.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout_button.addWidget(self.button_next20gen)
        layout_button.addWidget(self.button_start)
        layout_button.addWidget(self.button_pause)
        layout_button.addWidget(self.button_reset)
        layout_button.addWidget(self.button_import)
        #layout_button.addWidget(self.button_record)
        layout_button.addWidget(self.button_export)
        self.button_pause.setHidden(True)
        widget_button = QWidget()
        widget_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        widget_button.setLayout(layout_button)

        layout_cnb.addWidget(widget_status)
        layout_cnb.addWidget(self.canvas)
        layout_cnb.addWidget(widget_button)
        widget_cnb = QWidget()
        widget_cnb.setLayout(layout_cnb)

        layout_snf.addWidget(self.frame_fluid, 0, 0, 3, 5)
        layout_snf.addWidget(self.label_fluid, 0, 1)
        layout_snf.addWidget(self.label_u0, 1, 1)
        layout_snf.addWidget(self.slider_u0, 1, 2)
        layout_snf.addWidget(self.label_show_u0, 1, 3)
        layout_snf.addWidget(self.label_viscosity, 2, 1)
        layout_snf.addWidget(self.slider_viscosity, 2, 2)
        layout_snf.addWidget(self.label_show_viscosity, 2, 3)
        layout_snf.addWidget(self.frame_barrier, 3, 0, 4, 5)
        layout_snf.addWidget(self.label_barrier, 3, 1)
        layout_snf.addWidget(self.label_barrierset, 4, 1)
        layout_snf.addWidget(self.combo_barrier, 4, 2)
        layout_snf.addWidget(self.button_equation, 5, 2)
        layout_snf.addWidget(self.checkbox_changeable, 6, 2)
        layout_snf.addWidget(self.frame_animation, 7, 0, 4, 5)
        layout_snf.addWidget(self.label_animation, 7, 1)
        layout_snf.addWidget(self.label_animation_type, 8, 1)
        layout_snf.addWidget(self.combo_animation_type, 8, 2)
        layout_snf.addWidget(self.label_animation_speed, 9, 1)
        layout_snf.addWidget(self.slider_animation_speed, 9, 2)
        layout_snf.addWidget(self.label_show_animation_speed, 9, 3)
        layout_snf.addWidget(self.label_animation_contrast, 10, 1)
        layout_snf.addWidget(self.slider_animation_contrast, 10, 2)
        layout_snf.addWidget(self.label_show_animation_contrast, 10, 3)
        #layout_snf.addWidget(self.checkbox_force, 11, 2)
        #layout_snf.addWidget(self.button_reset, 11, 1)
        widget_snf = QWidget()
        widget_snf.setLayout(layout_snf)
        widget_snf.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout_window.addWidget(widget_cnb)
        layout_window.addWidget(widget_snf)

        #widget_window = QWidget()
        #widget_window.setLayout(layout_window)

        #layout_upndown.addWidget(self.frame_menu, 0, 0, 1, 1)
        #layout_upndown.addWidget(widget_window, 1, 0, 1, 1)
        #layout.addWidget(self.button_draw)

        self.setLayout(layout_window)

        # 菜单栏
        self.menuBar = QMenuBar(self)
        self.menuBar.resize(3000, 25)

        self.menu_file = self.menuBar.addMenu('文件')
        self.action_file_import = QAction('导入', self)
        self.action_file_import.setShortcut('Ctrl+o')
        self.action_file_import.triggered.connect(self.ChooseFile)
        self.action_file_export = QAction('导出', self)
        self.action_file_export.setShortcut('Ctrl+s')
        self.action_file_export.triggered.connect(self.Export)
        self.action_file_save = QAction('截图为', self)
        self.action_file_save.setShortcut('Ctrl+alt+s')
        self.action_file_save.triggered.connect(self.SavePhoto)
        self.action_file_cut = QAction('截图', self)
        self.action_file_cut.setShortcut('F1')
        self.action_file_cut.triggered.connect(lambda:self.SavePhotoStep2(''))
        self.menu_file.addAction(self.action_file_import)
        self.menu_file.addAction(self.action_file_export)
        self.menu_file.addAction(self.action_file_save)
        self.menu_file.addAction(self.action_file_cut)
        self.menu_file.addSeparator()
        self.action_file_exit = QAction('退出', self)
        self.action_file_exit.triggered.connect(self.Exit)
        self.menu_file.addAction(self.action_file_exit)

        self.menu_operation = self.menuBar.addMenu('操作')
        self.action_start = QAction('开始', self)
        self.action_start.setShortcut('Ctrl+p')
        self.action_start.triggered.connect(HelpStart)
        self.action_pause = QAction('暂停', self)
        self.action_pause.setShortcut('Ctrl+p')
        #self.action_pause.setVisible(False)
        self.action_pause.setEnabled(False)
        self.action_pause.triggered.connect(HelpPause)
        self.action_next1gen = QAction('下一代', self)
        self.action_next1gen.triggered.connect(lambda: thread_it(nextFrame, 1))
        self.action_next10gen = QAction('下10代', self)
        self.action_next10gen.triggered.connect(lambda: thread_it(nextFrame, 10))
        self.action_next100gen = QAction('下100代', self)
        self.action_next100gen.triggered.connect(lambda: thread_it(nextFrame, 100))
        self.action_next1000gen = QAction('下1000代（慎用）', self)
        self.action_next1000gen.triggered.connect(lambda: thread_it(nextFrame, 1000))
        self.action_spdup = QAction('动画加速', self)
        self.action_spdup.triggered.connect(self.spdup)
        self.action_spdup.setShortcut('Ctrl+=')
        self.action_spddn = QAction('动画减速', self)
        self.action_spddn.triggered.connect(self.spddn)
        self.action_spddn.setShortcut('Ctrl+-')
        self.action_ctrup = QAction('增加对比度', self)
        self.action_ctrup.triggered.connect(self.contrast_up)
        self.action_ctrdn = QAction('减小对比度', self)
        self.action_ctrdn.triggered.connect(self.contrast_dn)
        self.action_reset = QAction('重置参数', self)
        self.action_reset.triggered.connect(self.Reset)
        self.action_reset.setShortcut('Ctrl+n')
        self.menu_operation.addAction(self.action_start)
        self.menu_operation.addAction(self.action_pause)
        self.menu_operation.addSeparator()
        self.menu_operation.addAction(self.action_spdup)
        self.menu_operation.addAction(self.action_spddn)
        self.menu_operation.addSeparator()
        self.menu_operation.addAction(self.action_ctrup)
        self.menu_operation.addAction(self.action_ctrdn)
        self.menu_operation.addSeparator()
        self.menu_operation.addAction(self.action_next1gen)
        self.menu_operation.addAction(self.action_next10gen)
        self.menu_operation.addAction(self.action_next100gen)
        self.menu_operation.addAction(self.action_next1000gen)
        self.menu_operation.addSeparator()
        self.menu_operation.addAction(self.action_reset)
        
        self.menu_view = self.menuBar.addMenu('查看')
        self.action_view_curl = QAction('旋度动画', self)
        self.action_view_curl.triggered.connect(lambda: self.ChangeAnimationComboBox(True, 0))
        self.action_view_curl.setCheckable(True)
        self.action_view_curl.setChecked(True)
        self.action_view_rho = QAction('密度动画', self)
        self.action_view_rho.triggered.connect(lambda: self.ChangeAnimationComboBox(True, 1))
        self.action_view_rho.setCheckable(True)
        self.action_view_rho.setChecked(False)
        self.action_view_stream = QAction('流线', self)
        self.action_view_stream.triggered.connect(lambda: self.ChangeAnimationComboBox(True, 2))
        self.action_view_stream.setCheckable(True)
        self.action_view_stream.setChecked(False)
        self.action_view_v = QAction('速度矢量', self)
        self.action_view_v.triggered.connect(lambda: self.ChangeAnimationComboBox(True, 3))
        self.action_view_v.setCheckable(True)
        self.action_view_v.setChecked(False)
        self.action_view_vx = QAction('水平速度', self)
        self.action_view_vx.triggered.connect(lambda: self.ChangeAnimationComboBox(True, 4))
        self.action_view_vx.setCheckable(True)
        self.action_view_vx.setChecked(False)
        self.action_view_vy = QAction('垂直速度', self)
        self.action_view_vy.triggered.connect(lambda: self.ChangeAnimationComboBox(True, 5))
        self.action_view_vy.setCheckable(True)
        self.action_view_vy.setChecked(False)
        self.action_view_ld = QAction('升阻力-代数图', self)
        self.action_view_ld.triggered.connect(self.LiftDragWindow)
        self.menu_view.addAction(self.action_view_curl)
        self.menu_view.addAction(self.action_view_rho)
        self.menu_view.addAction(self.action_view_stream)
        self.menu_view.addAction(self.action_view_v)
        self.menu_view.addAction(self.action_view_vx)
        self.menu_view.addAction(self.action_view_vy)
        self.menu_view.addSeparator()
        self.menu_view.addAction(self.action_view_ld)

        self.menu_advanced = self.menuBar.addMenu('高级')
        self.menu_lattice = self.menu_advanced.addMenu("格子规格")
        self.menu_lattice_5075 = QAction('50x75', self)
        self.menu_lattice_5075.triggered.connect(lambda: self.ChangeLattice(50,75))
        self.menu_lattice_5075.setCheckable(True)
        self.menu_lattice_5075.setChecked(False)
        self.menu_lattice_6090 = QAction('60x90', self)
        self.menu_lattice_6090.triggered.connect(lambda: self.ChangeLattice(60,90))
        self.menu_lattice_6090.setCheckable(True)
        self.menu_lattice_6090.setChecked(False)
        self.menu_lattice_80120 = QAction('80x120', self)
        self.menu_lattice_80120.triggered.connect(lambda: self.ChangeLattice(80,120))
        self.menu_lattice_80120.setCheckable(True)
        self.menu_lattice_80120.setChecked(False)
        self.menu_lattice_100150 = QAction('100x150', self)
        self.menu_lattice_100150.triggered.connect(lambda: self.ChangeLattice(100,150))
        self.menu_lattice_100150.setCheckable(True)
        self.menu_lattice_100150.setChecked(True)
        self.menu_lattice_160240 = QAction('160x240', self)
        self.menu_lattice_160240.triggered.connect(lambda: self.ChangeLattice(160,240))
        self.menu_lattice_160240.setCheckable(True)
        self.menu_lattice_160240.setChecked(False)
        self.menu_lattice_200300 = QAction('200x300', self)
        self.menu_lattice_200300.triggered.connect(lambda: self.ChangeLattice(200,300))
        self.menu_lattice_200300.setCheckable(True)
        self.menu_lattice_200300.setChecked(False)
        self.menu_lattice_8080 = QAction('80x80', self)
        self.menu_lattice_8080.triggered.connect(lambda: self.ChangeLattice(80,80))
        self.menu_lattice_8080.setCheckable(True)
        self.menu_lattice_8080.setChecked(False)
        self.menu_lattice_120120 = QAction('120x120', self)
        self.menu_lattice_120120.triggered.connect(lambda: self.ChangeLattice(120,120))
        self.menu_lattice_120120.setCheckable(True)
        self.menu_lattice_120120.setChecked(False)
        self.menu_lattice_160160 = QAction('160x160', self)
        self.menu_lattice_160160.triggered.connect(lambda: self.ChangeLattice(160,160))
        self.menu_lattice_160160.setCheckable(True)
        self.menu_lattice_160160.setChecked(False)
        self.menu_lattice_200200 = QAction('200x200', self)
        self.menu_lattice_200200.triggered.connect(lambda: self.ChangeLattice(200,200))
        self.menu_lattice_200200.setCheckable(True)
        self.menu_lattice_200200.setChecked(False)
        self.menu_lattice_set = QAction('自定义', self)
        self.menu_lattice_set.triggered.connect(self.lattice_window.show)
        self.menu_lattice.addAction(self.menu_lattice_5075)
        self.menu_lattice.addAction(self.menu_lattice_6090)
        self.menu_lattice.addAction(self.menu_lattice_80120)
        self.menu_lattice.addAction(self.menu_lattice_100150)
        self.menu_lattice.addAction(self.menu_lattice_160240)
        self.menu_lattice.addAction(self.menu_lattice_200300)
        self.menu_lattice.addSeparator()
        self.menu_lattice.addAction(self.menu_lattice_8080)
        self.menu_lattice.addAction(self.menu_lattice_120120)
        self.menu_lattice.addAction(self.menu_lattice_160160)
        self.menu_lattice.addAction(self.menu_lattice_200200)
        self.menu_lattice.addSeparator()
        self.menu_lattice.addAction(self.menu_lattice_set)
        self.menu_edge = self.menu_advanced.addMenu("边界条件")
        self.menu_edge_0 = QAction('风洞流：上下反弹', self)
        self.menu_edge_0.triggered.connect(lambda: self.ChangeEdge(0))
        self.menu_edge_0.setCheckable(True)
        self.menu_edge_0.setChecked(True)
        self.menu_edge_1 = QAction('风洞流：无反弹', self)
        self.menu_edge_1.triggered.connect(lambda: self.ChangeEdge(1))
        self.menu_edge_1.setCheckable(True)
        self.menu_edge_1.setChecked(False)
        self.menu_edge_2 = QAction('风洞流：三侧反弹', self)
        self.menu_edge_2.triggered.connect(lambda: self.ChangeEdge(2))
        self.menu_edge_2.setCheckable(True)
        self.menu_edge_2.setChecked(False)
        self.menu_edge_3 = QAction('方腔流：全侧反弹', self)
        self.menu_edge_3.triggered.connect(lambda: self.ChangeEdge(3))
        self.menu_edge_3.setCheckable(True)
        self.menu_edge_3.setChecked(False)
        self.menu_edge.addAction(self.menu_edge_0)
        self.menu_edge.addAction(self.menu_edge_1)
        self.menu_edge.addAction(self.menu_edge_2)
        self.menu_edge.addAction(self.menu_edge_3)

        
        

        self.menu_about = self.menuBar.addMenu('关于')
        self.action_about_algorithm = QAction('算法', self)
        self.action_about_algorithm.triggered.connect(lambda:self.web("http://82.157.170.107/2022/03/29/%e6%a0%bc%e5%ad%90%e7%8e%bb%e5%b0%94%e5%85%b9%e6%9b%bc%e7%ae%97%e6%b3%95/"))
        self.action_about_author = QAction('作者', self)
        self.action_about_author.triggered.connect(self.AuthorWindow)
        self.action_about_instructor = QAction('指导', self)
        self.action_about_instructor.triggered.connect(self.InstructorWindow)
        self.action_about_thanks = QAction('特别感谢', self)
        self.action_about_thanks.triggered.connect(self.ThanksWindow)
        self.menu_about.addAction(self.action_about_algorithm)
        self.menu_about.addSeparator()
        #self.menu_about.addAction(self.action_about_author)
        #self.menu_about.addAction(self.action_about_instructor)
        self.menu_about.addAction(self.action_about_thanks)

        self.menu_help = self.menuBar.addMenu('帮助')
        self.action_help_doc = QAction('帮助文档', self)
        self.action_help_doc.triggered.connect(lambda:self.web("http://82.157.170.107/2022/01/22/fluidsimulator/"))
        self.menu_help.addAction(self.action_help_doc)

        #状态栏
        
    #def Show(self):
        #self.widget_window.show()

    def Change_u0(self):
        global u0
        u0 = self.slider_u0.value()/1000
        self.label_show_u0.setText(str('%.3f' % (self.slider_u0.value() / 1000)))

    def Change_viscosity(self):
        global viscosity
        viscosity = self.slider_viscosity.value()/1000
        self.label_show_viscosity.setText(str('%.3f' % (self.slider_viscosity.value() / 1000)))

    def HideStart(self):
        self.button_start.setHidden(True)
        self.button_pause.setHidden(False)
        self.action_start.setEnabled(False)
        self.action_pause.setEnabled(True)
        self.action_next1gen.setEnabled(False)
        self.action_next10gen.setEnabled(False)
        self.action_next100gen.setEnabled(False)
        self.action_next1000gen.setEnabled(False)
        QApplication.processEvents()

    def ShowStart(self):
        global fps, gps
        self.button_start.setHidden(False)
        self.button_pause.setHidden(True)
        self.action_start.setEnabled(True)
        self.action_pause.setEnabled(False)
        self.action_next1gen.setEnabled(True)
        self.action_next10gen.setEnabled(True)
        self.action_next100gen.setEnabled(True)
        self.action_next1000gen.setEnabled(True)
        time.sleep(0.1)
        fps=0
        gps=0
        QApplication.processEvents()

    def Draw(self):
        self.canvas.draw()
        #QApplication.processEvents()

    def ChangeBrrierComboBox(self):
        change_barrier(self.combo_barrier.currentText())

    def EquationWindow(self):
        initeq()
        self.equation_window.show()
        #self.equation_window.exec_()

    def Draw_eq(self):
        self.equation_window.Draw()
    
    def Draw_ld(self):
        self.ld_window.Draw()

    def Change_animation_speed(self):
        global spd
        spd = self.slider_animation_speed.value() / 100
        self.label_show_animation_speed.setText(str('%.2f' % (self.slider_animation_speed.value() / 100)))

    def Change_animation_contrast(self):
        global contrast
        contrast = self.slider_animation_contrast.value() / 100
        self.label_show_animation_contrast.setText(str('%.2f' % (self.slider_animation_contrast.value() / 100)))

    able = True
    def ChangeAnimationComboBox(self, mode_menu, type):
        if self.able:
            self.able = False
            if mode_menu:
                self.combo_animation_type.setCurrentIndex(type)
            if self.combo_animation_type.currentIndex() == 0:
                self.action_view_curl.setChecked(True)
                self.action_view_rho.setChecked(False)
                self.action_view_stream.setChecked(False)
                self.action_view_v.setChecked(False)
                self.action_view_vx.setChecked(False)
                self.action_view_vy.setChecked(False)
            elif self.combo_animation_type.currentIndex() == 1:
                self.action_view_curl.setChecked(False)
                self.action_view_rho.setChecked(True)
                self.action_view_stream.setChecked(False)
                self.action_view_v.setChecked(False)
                self.action_view_vx.setChecked(False)
                self.action_view_vy.setChecked(False)
            elif self.combo_animation_type.currentIndex() == 2:
                self.action_view_curl.setChecked(False)
                self.action_view_rho.setChecked(False)
                self.action_view_stream.setChecked(True)
                self.action_view_v.setChecked(False)
                self.action_view_vx.setChecked(False)
                self.action_view_vy.setChecked(False)
            elif self.combo_animation_type.currentIndex() == 3:
                self.action_view_curl.setChecked(False)
                self.action_view_rho.setChecked(False)
                self.action_view_stream.setChecked(False)
                self.action_view_v.setChecked(True)
                self.action_view_vx.setChecked(False)
                self.action_view_vy.setChecked(False)
            elif self.combo_animation_type.currentIndex() == 4:
                self.action_view_curl.setChecked(False)
                self.action_view_rho.setChecked(False)
                self.action_view_stream.setChecked(False)
                self.action_view_v.setChecked(False)
                self.action_view_vx.setChecked(True)
                self.action_view_vy.setChecked(False)
            elif self.combo_animation_type.currentIndex() == 5:
                self.action_view_curl.setChecked(False)
                self.action_view_rho.setChecked(False)
                self.action_view_stream.setChecked(False)
                self.action_view_v.setChecked(False)
                self.action_view_vx.setChecked(False)
                self.action_view_vy.setChecked(True)
            change_animation(self.combo_animation_type.currentText())
            self.able = True

    def Record(self):
        global write_switch, first_write
        if self.button_record.isChecked():
            self.label_status_record.setText("录制"+"开启")
            write_switch = True
            first_write = True
        else:
            self.label_status_record.setText("录制" + "关闭")
            write_switch = False

    def fresh_status(self):
        self.label_status_gen.setText("代数："+ str(gen) + " 代")
        self.label_status_frame.setText("帧率：" + str(fps) + " 帧/秒")
        self.label_status_gps.setText("代率：" + str(gps) + " 代/秒")
        #self.label_status_record.setHidden(True)
        if self.checkbox_changeable.isChecked():
            self.label_status_record.setText("障碍：可变")
        else:
            self.label_status_record.setText("障碍：不可变")
        if alert:
            self.label_status_gps.setHidden(True)
            self.label_status_gen.setHidden(True)
            self.label_status_frame.setStyleSheet("color:red")
            self.label_status_frame.setText('计算出现发散，请重置流动')

       
    def FreshDetail(self):
        try:
            if xdata != None:
                self.label_status_gen.setText('x:'+str('%.1f' % xdata)+'  y:'+str('%.1f' % ydata))
                self.label_status_frame.setText('ux:'+str('%.4f' % ux[int(ydata), int(xdata)])+'  uy:'+str('%.4f' % uy[int(ydata), int(xdata)]))
                self.label_status_gps.setText('  密度:'+str('%.4f' % rho[int(ydata), int(xdata)]))
                self.label_status_record.setText('障碍:'+str(barrier[int(ydata), int(xdata)]))
                #self.label_status_record.setHidden(False)
        except:
            traceback.print_exc()
            #self.fresh_status()
            

    def ChooseFile(self):
        try:
            fileName_choose, filetype = QFileDialog.getOpenFileName(self, "选取文件", './Projects', "LBM工程文件 (*.lbm);;All Files (*)")
            '''
            if fileName_choose == "":
                print("\n取消选择")
                return
            print("\n你选择的文件为:")
            print(fileName_choose)
            print("文件筛选器类型: ", filetype)
            '''
            thread_it(file_import,fileName_choose)
        except:
            traceback.print_exc()

    def web(self, website):
        webbrowser.open(website)

    def Exit(self):
        global kill
        kill = True
        sys.exit()

    def SavePhoto(self):
        #datetime.datetime.now()
        self.filename, filetype = QFileDialog.getSaveFileName(self, '保存到图片', './Screenshots', "PNG图片 (*.png)")
        try:
            while True:
                if not save_lock:
                    break
                time.sleep(0.01)
            if self.filename == "":
                theFig.savefig(str(os.getcwd())+'/'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.png')
            else:
                theFig.savefig(self.filename)
        except:
            traceback.print_exc()

    
    def SavePhotoStep2(self, fn):
        try:
            while True:
                if not save_lock:
                    break
                time.sleep(0.01)
            if fn == "":
                print(str(os.getcwd())+'/'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.png')
                theFig.savefig(str(os.getcwd())+'\Screenshots'+'\\'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.png')
            else:
                traceback.print_exc()
        except:
            traceback.print_exc()


    def AuthorWindow(self):
        self.author_window.show()

    def InstructorWindow(self):
        self.instructor_window.show()

    def ThanksWindow(self):
        self.thanks_window.show()

    def spdup(self):
        self.slider_animation_speed.setValue(self.slider_animation_speed.value()+50)

    def spddn(self):
        self.slider_animation_speed.setValue(self.slider_animation_speed.value()-50)
    
    def contrast_up(self):
        self.slider_animation_contrast.setValue(self.slider_animation_contrast.value()+50)

    def contrast_dn(self):
        self.slider_animation_contrast.setValue(self.slider_animation_contrast.value()-50)
    
    def Reset(self):
        global start_start, animating
        start_start = False
        while True:
            if not animating:
                break
            time.sleep(0.01)
        global change_barrier_switch, nbarrier, barrier_zone, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood
        global n, changing, x, y, x1, y1, ux1, uy1, n
        global change_v, change_viscosity, gen, drag, lift, dforce, tank, ncurl, omega, performanceData, u1, nviscosity, nnbarrier, first_write
        global bindable, alert, first_st_var, change_animation_switch, write_switch, animation_type, contrast, ux, uy, killThreadAnimation
        global theFig, eqFig, ldFig, bImageArray, eqbImageArray, barrierImage, eqbarrierImage, l1, l2, fluidImage, blood, height, width, ax
        eqFig.clf()
        ldFig.clf()
        self.label_status_gen.setHidden(False)
        self.label_status_frame.setStyleSheet("color:black")
        blood = numpy.ones((nheight, nwidth))
        alert = False
        #killThreadAnimation = True
        change_v = False
        change_viscosity = False
        changing = False
        gen = 0
        drag = 0
        lift = 0
        dforce = True
        tank = 0
        ncurl = 1  # 临时的
        # ----------------------
        height = int(nheight)  # lattice dimensions 建议 100x150
        width = int(nwidth)
        # ----------------------
        # height = 600  # lattice dimensions
        # width = 800
        # viscosity = 0.005  # fluid viscosity
        viscosity = 0.020
        omega = 1 / (3 * viscosity + 0.5)  # "relaxation" parameter
        u0 = 0.1  # initial and in-flow speed
        four9th = 4.0 / 9.0  # abbreviations for lattice-Boltzmann weight factors
        one9th = 1.0 / 9.0
        one36th = 1.0 / 36.0
        performanceData = False  # set to True if performance data is desired
        u1 = u0
        nviscosity = viscosity
        bindable = False
        first_st_var = True
        change_barrier_switch = False
        change_animation_switch = False
        write_switch = False
        animation_type = 0 # 0=旋度动画，1=密度动画, 2=流线
        contrast = 1
        y, x = numpy.mgrid[0:height:1, 0:width:1]
        y1, x1 = numpy.mgrid[0:height:4, 0:width:4]
        ux1 = numpy.zeros((int(height/4), int(width/4)))
        uy1 = numpy.zeros((int(height/4), int(width/4)))
        if x1.shape[0] != ux1.shape[0]:
            if x1.shape[0] > ux1.shape[0]:
                x1 = numpy.delete(x1, int(x1.shape[0]-1), axis=0)
            elif x1.shape[0] < ux1.shape[0]:
                ux1 = numpy.delete(ux1, int(ux1.shape[0]-1), axis=0)
        if y1.shape[0] != uy1.shape[0]:
                if y1.shape[0] > uy1.shape[0]:
                    y1 = numpy.delete(y1, int(y1.shape[0]-1), axis=0)
                elif y1.shape[0] < uy1.shape[0]:
                    uy1 = numpy.delete(uy1, int(uy1.shape[0]-1), axis=0)
        if x1.shape[1] != ux1.shape[1]:
            if x1.shape[1] > ux1.shape[1]:
                x1 = numpy.delete(x1, int(x1.shape[1]-1), axis=1)
            elif x1.shape[1] < ux1.shape[1]:
                ux1 = numpy.delete(ux1, int(ux1.shape[1]-1), axis=1)
        if y1.shape[1] != uy1.shape[1]:
                if y1.shape[1] > uy1.shape[1]:
                    y1 = numpy.delete(y1, int(y1.shape[1]-1), axis=1)
                elif y1.shape[1] < uy1.shape[1]:
                    uy1 = numpy.delete(uy1, int(uy1.shape[0]-1), axis=1)
        

        # 初始化
        #del n[0],n[3],n[7],n[1],n[5],n[2],n[6],n[4],n[6]
        n0 = four9th * (numpy.ones((height, width)) - 1.5 * u0 ** 2)
        n3 = one9th * (numpy.ones((height, width)) - 1.5 * u0 ** 2)
        n7 = one9th * (numpy.ones((height, width)) - 1.5 * u0 ** 2)
        n1 = one9th * (numpy.ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n5 = one9th * (numpy.ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n2 = one36th * (numpy.ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n8 = one36th * (numpy.ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n4 = one36th * (numpy.ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n6 = one36th * (numpy.ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n = [n0, n1, n2, n3, n4, n5, n6, n7, n8]
        rho = n[0] + n[3] + n[7] + n[1] + n[5] + n[2] + n[8] + n[4] + n[6]  # macroscopic density
        ux = (n[1] + n[2] + n[8] - n[5] - n[4] - n[6]) / rho  # macroscopic x velocity
        uy = (n[3] + n[2] + n[4] - n[7] - n[8] - n[6]) / rho  # macroscopic y velocity
        barrier = numpy.zeros((height, width), bool)  # True wherever there's a barrier
        animating = False
        for i in range(16):
            barrier[int((height / 2) + 8 - i), int(width / 2)] = True
        nbarrier = barrier
        nnbarrier = nbarrier

        barrier3 = numpy.roll(barrier, 1, axis=0) 
        barrier7 = numpy.roll(barrier, -1, axis=0)  
        barrier1 = numpy.roll(barrier, 1, axis=1)  
        barrier5 = numpy.roll(barrier, -1, axis=1)
        barrier2 = numpy.roll(barrier3, 1, axis=1)
        barrier4 = numpy.roll(barrier3, -1, axis=1)
        barrier8 = numpy.roll(barrier7, 1, axis=1)
        barrier6 = numpy.roll(barrier7, -1, axis=1)

        barrier_zone = numpy.zeros((height, width))
        barrier_area = barrier3 + barrier7 + barrier1 + barrier5 + barrier2 + barrier4 + barrier8 + barrier6
        for i in range(height):
            for j in range(width):
                if barrier_area[i, j] > 0:
                    barrier_zone[i, j] = True

        eqFig = matplotlib.pyplot.figure(num=2, figsize=(5, 3))
        eqax = eqFig.add_subplot(111)
        eqax.xaxis.grid(True, which='major')
        eqax.yaxis.grid(True, which='major')
        eqbImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
        eqbImageArray[nnbarrier, 3] = 255  # set alpha=255 only at barrier sites
        eqbarrierImage = matplotlib.pyplot.imshow(eqbImageArray, origin='lower', interpolation='none')


        ldFig = matplotlib.pyplot.figure(num=3, figsize=(10, 3))
        ax = ldFig.add_subplot(111)
        ax.set_xlabel(u'代数')
        ax.set_ylabel(u'力')
        ax.set_title(u'力-代数 曲线')
        ax.xaxis.grid(True, which='major')
        ax.yaxis.grid(True, which='major')
        l1, = ax.plot(list_gen, list_lift, 'b', label=u'升力')
        l2, = ax.plot(list_gen, list_drag, 'r', label=u'阻力')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1])
        #ax2 = ldFig.add_subplot(122)
        #ax2.set_xlabel(u'代数')
        #ax2.set_ylabel(u'阻力(Fx)')
        #ax2.set_title(u'阻力-代数 曲线')


        theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
        fluidImage = matplotlib.pyplot.imshow(curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                            cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
        bImageArray = numpy.zeros((height, width, 4), numpy.uint8)  # an RGBA image
        bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
        barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')



        # @vectorize(['float32(float32, float32)'], target='gpu')

        # @cuda.jit
        change_barrier_switch = False
        first_write = True
        barrier_zone = numpy.zeros((height, width))
        
        self.slider_viscosity.setValue(20)
        self.slider_u0.setValue(100)
        self.slider_animation_speed.setValue(100)
        self.slider_animation_contrast.setValue(100)
        freshbarrier()
        #change_animation('旋度动画')
        change_animation(self.combo_animation_type.currentText())
        nextFrame(0)
        killThreadAnimation = False
        self.ld_window.Clear()
        start_start = False
        self.ShowStart()
        self.canvas.draw()
        fresheq()
        #threadAnimation = threading.Thread(target=starter, name='T_Animation')  # 动画开始线程
        #threadAnimation.start()
        print('RESETED')

    def changeable_barrier(self):
        global changeable_barrier_switch
        if changeable_barrier_switch:
            changeable_barrier_switch = False
        elif not changeable_barrier_switch:
            changeable_barrier_switch = True
        
    def LiftDragWindow(self):
        self.ld_window.show()

        
    def Alert(self):
        #global alert
        alert_window = QMessageBox(QMessageBox.Warning, '警告', '请输入正确的表达式')
        #alert = False
        alert_window.exec_()
        #QApplication.processEvents()
        #self.alert_window.show()
    
    def SetEqProgressBar(self, value):
        self.equation_window.progressbar.setValue(value)
    
    def closeEvent(self,event): #函数名固定不可变
        global kill
        kill = True
        self.equation_window.close()
        self.ld_window.close()
        self.lattice_window.close()
        self.alert_window.close()
        self.author_window.close()
        self.thanks_window.close()
        self.instructor_window.close()
        event.accept()
    
    def Export(self):
        self.filename, filetype = QFileDialog.getSaveFileName(self, '保存工程', './Projects', "LBM工程文件 (*.lbm)")
        try:
            if filename == '':
                numpy.savez(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())), height=height, width=width, n=n ,barrier=barrier, gen=gen,edge=edge, ux=ux,uy=uy,rho=rho)
            else:
                numpy.savez(self.filename, height=height, width=width, n=n ,barrier=barrier, gen=gen,edge=edge, ux=ux,uy=uy,rho=rho)
            os.rename(self.filename+'.npz', self.filename)
        except:
            traceback.print_exc()
    
    def ForceVector(self, state):
        global force_vector_switch
        if state == Qt.Checked:
            force_vector_switch = True
        else:
            force_vector_switch = False

    able_lattice = True
    def ChangeLattice(self, height, width, *arg):
        global nheight, nwidth
        if self.able_lattice:
            self.able_lattice = False
            self.menu_lattice_5075.setChecked(False)
            self.menu_lattice_6090.setChecked(False)
            self.menu_lattice_80120.setChecked(False)
            self.menu_lattice_100150.setChecked(False)
            self.menu_lattice_160240.setChecked(False)
            self.menu_lattice_200300.setChecked(False)
            self.menu_lattice_8080.setChecked(False)
            self.menu_lattice_120120.setChecked(False)
            self.menu_lattice_160160.setChecked(False)
            self.menu_lattice_200200.setChecked(False)
            if arg == None:
                exec('main_window.menu_lattice_'+str(height)+str(width)+'.setChecked(True)')
            nheight = height
            nwidth = width
            self.Reset()
            self.able_lattice = True
    
    able_edge = True
    def ChangeEdge(self, nedge):
        global edge
        if self.able_edge:
            self.able_edge = False
            edge = int(nedge)
            if nedge == 3 or nedge == 2:
                global n
                n[3][:,:] = one9th
                n[7][:,:] = one9th
                n[1][:,:] = one9th
                n[5][:,:] = one9th
                n[2][:,:] = one9th
                n[8][:,:] = one9th
                n[4][:,:] = one9th
                n[6][:,:] = one9th
            self.menu_edge_0.setChecked(False)
            self.menu_edge_1.setChecked(False)
            self.menu_edge_2.setChecked(False)
            self.menu_edge_3.setChecked(False)
            exec('main_window.menu_edge_'+str(nedge)+'.setChecked(True)')
            self.able_edge = True

    def Drawing(self):                     
        self.equation_window.slider_x.setValue(0)
        self.equation_window.slider_y.setValue(0)
        self.equation_window.slider_rot.setValue(0)

 



        

class Equation_window(QWidget):
    #signal = pyqtSignal()
    def __init__(self):
        super(Equation_window, self).__init__()
        global update

        #QShortcut(q)
        #self.signal.connect(self.Draw)
        self.last_x = 0
        self.last_y = 0

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('障碍方程')
        self.setWindowIcon(QIcon('icon.ico'))
        self.resize(500, 600)

        #self.figure = matplotlib.pyplot.figure(facecolor='#FFD7C4')  # 可选参数,facecolor为背景颜色
        self.eqcanvas = FigureCanvas(eqFig)
        self.eqcanvas.setCursor(QCursor(Qt.CrossCursor))

        #标签
        self.label_xt = QLabel("x(t)=")
        self.label_yt = QLabel("y(t)=")
        self.label_x = QLabel("x+"+"0")
        self.label_y = QLabel("y+"+"0")
        self.label_rot = QLabel(""+"0"+"°")
        self.label_tmin = QLabel("最小值：")
        self.label_tmin.setFixedHeight(25)
        self.label_tmax = QLabel("最大值：")
        self.label_tmax.setFixedHeight(25)
        self.label_exp = QLabel("精确度：")
        self.label_exp.setFixedHeight(25)

        #编辑栏
        self.line_xt = QLineEdit("10*sin(t);16*((sin(t))**3);")
        self.line_xt.returnPressed.connect(lambda: Equation(self.line_xt.text(), self.line_yt.text(), int(self.line_tmin.text()), int(self.line_tmax.text()), int(self.line_exp.text())))
        self.line_yt = QLineEdit("10*cos(t);13*cos(t)-5*cos(2 * t)-2*cos(3*t)-cos(4*t);")
        self.line_yt.returnPressed.connect(lambda: Equation(self.line_xt.text(), self.line_yt.text(), int(self.line_tmin.text()), int(self.line_tmax.text()), int(self.line_exp.text())))
        self.line_tmin = QLineEdit("-100")
        self.line_tmin.setFixedHeight(25)
        #self.line_tmin.setFixedWidth(80)
        self.line_tmax = QLineEdit("100")
        self.line_tmin.setFixedHeight(25)
        #self.line_tmin.setFixedWidth(80)
        self.line_exp = QLineEdit("1")
        self.line_exp.setFixedHeight(25)
        #self.line_exp.setFixedWidth(80)


        #按钮
        self.button_confirm_equation = QPushButton("绘制方程")
        self.button_pen_eraser = QPushButton("鼠标：绘制")
        self.button_clear_barrier = QPushButton("清除障碍")
        self.button_confirm_barrier = QPushButton("更新障碍")
        self.button_reset = QPushButton("默认参数")
        

        self.button_unfold = QToolButton()
        self.button_unfold.setText(">>")
        self.button_unfold.setCheckable(True)
        self.button_unfold.setChecked(False)
        #self.button_unfold.setAutoRaise(True)
        self.button_unfold.clicked.connect(self.Unfold)

        #self.button_unfold.setFixedHeight(20)

        self.button_confirm_equation.clicked.connect(self.Change_Eq)
        self.button_clear_barrier.clicked.connect(self.ClearBarrier)
        self.button_confirm_barrier.clicked.connect(freshbarrier)
        self.button_pen_eraser.clicked.connect(self.PenEraser)
        self.button_reset.clicked.connect(self.Reset)

        # 勾选
        self.check_auto_confirm = QCheckBox("自动更新", self)
        self.check_auto_confirm.setChecked(True)
        self.check_auto_confirm.stateChanged.connect(self.AutoConfirm)

        # 滑动条
        self.slider_x=QSlider(Qt.Horizontal)
        self.slider_x.setMinimum(-width/2)
        self.slider_x.setMaximum(width/2)
        self.slider_x.setSingleStep(1)
        self.slider_x.setTickPosition(QSlider.TicksBelow)
        self.slider_x.setTickInterval(10)
        self.slider_x.setValue(0)
        self.slider_x.valueChanged.connect(self.Change_x)

        self.slider_y=QSlider(Qt.Vertical)
        self.slider_y.setMinimum(-height/2)
        self.slider_y.setMaximum(height/2)
        self.slider_y.setSingleStep(1)
        self.slider_y.setTickPosition(QSlider.TicksBelow)
        self.slider_y.setTickInterval(10)
        self.slider_y.setValue(0)
        self.slider_y.valueChanged.connect(self.Change_y)

        self.slider_rot=QSlider(Qt.Horizontal)
        self.slider_rot.setMinimum(-180)
        self.slider_rot.setMaximum(180)
        self.slider_rot.setSingleStep(3)
        self.slider_rot.setTickPosition(QSlider.TicksBelow)
        self.slider_rot.setTickInterval(15)
        self.slider_rot.setValue(0)
        self.slider_rot.valueChanged.connect(self.Change_rot)

        # 进度条
        self.progressbar = QProgressBar()
        self.progressbar.setFixedWidth(80)
        self.progressbar.setValue(0)

        # 布局
        self.layout_linext = QHBoxLayout()
        self.layout_linext.addWidget(self.label_xt)
        self.layout_linext.addWidget(self.line_xt)
        self.layout_linext.addWidget(self.button_confirm_equation)
        self.widget_xt = QWidget()
        self.widget_xt.setLayout(self.layout_linext)

        self.layout_lineyt = QHBoxLayout()
        self.layout_lineyt.addWidget(self.label_yt)
        self.layout_lineyt.addWidget(self.line_yt)
        self.layout_lineyt.addWidget(self.progressbar)
        self.widget_yt = QWidget()
        self.widget_yt.setLayout(self.layout_lineyt)

        self.layout_x = QHBoxLayout()
        self.layout_x.addWidget(self.label_x)
        self.layout_x.addWidget(self.slider_x)
        self.widget_x = QWidget()
        self.widget_x.setLayout(self.layout_x)

        self.layout_rot = QHBoxLayout()
        self.layout_rot.addWidget(self.label_rot)
        self.layout_rot.addWidget(self.slider_rot)
        self.widget_rot = QWidget()
        self.widget_rot.setLayout(self.layout_rot)

        self.layout_eqwindow = QGridLayout()
        self.layout_eqwindow.addWidget(self.widget_xt, 1, 1, 1, 4)
        self.layout_eqwindow.addWidget(self.widget_yt, 2, 1, 1, 4)
        self.layout_eqwindow.addWidget(self.widget_x, 5, 1, 1, 4)
        self.layout_eqwindow.addWidget(self.widget_rot, 6, 1, 1, 4)
        self.layout_eqwindow.addWidget(self.eqcanvas, 4, 1, 1, 4)
        self.layout_eqwindow.addWidget(self.slider_y, 4, 5, 1, 1)
        self.layout_eqwindow.addWidget(self.label_y, 3, 5, 1, 1)
        self.layout_eqwindow.addWidget(self.check_auto_confirm, 7, 1)
        self.layout_eqwindow.addWidget(self.button_pen_eraser, 7, 2)
        self.layout_eqwindow.addWidget(self.button_clear_barrier, 7, 3)
        self.layout_eqwindow.addWidget(self.button_confirm_barrier, 7, 4)
        
        
        

        self.widget_eqwindow = QWidget()
        self.widget_eqwindow.setLayout(self.layout_eqwindow)

        layout_unfold = QHBoxLayout()
        layout_unfold.addWidget(self.label_tmin)
        layout_unfold.addWidget(self.line_tmin)
        layout_unfold.addWidget(self.label_tmax)
        layout_unfold.addWidget(self.line_tmax)
        layout_unfold.addWidget(self.label_exp)
        layout_unfold.addWidget(self.line_exp)
        layout_unfold.addWidget(self.button_reset)
        self.widget_unfold = QWidget()
        self.widget_unfold.setLayout(layout_unfold)
        self.layout_eqwindow.addWidget(self.widget_unfold, 3, 1, 1, 4)
        #self.widget_unfold.setFixedWidth(150)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.widget_eqwindow)
        #self.layout.addWidget(self.widget_unfold)
        #self.widget_unfold.setHidden(True)

        self.setLayout(self.layout)

    def Draw(self):
        self.eqcanvas.draw()
    
    
    def Change_x(self):
        global nnbarrier
        self.label_x.setText("x"+str("%+d" % int(self.slider_x.value())))
        #nnbarrier[int(yp[i]+ height / 2), int(xp[i]+self.slider_x.value() + width / 2)] = True
        nnbarrier = numpy.roll(nnbarrier, int(self.slider_x.value() - self.last_x), axis=1)
        self.last_x = self.slider_x.value()
        fresheq()
        if update:
            freshbarrier()

    def Change_y(self):
        global nnbarrier
        self.label_y.setText("y+"+str(int(self.slider_y.value())))
        nnbarrier = numpy.roll(nnbarrier, int(self.slider_y.value() - self.last_y), axis=0)
        self.last_y = self.slider_y.value()
        fresheq()
        if update:
            freshbarrier()
    
    def Change_rot(self):
        global nnbarrier
        '''
        global xp, yp
        xp = []
        yp = []
        for i in range(height):
            for j in range(width):
                if nnbarrier[i, j]:
                    xp.append(int(j - width / 2))
                    yp.append(int(i - height / 2))
        '''
        #lock.acquire()
        self.label_rot.setText(""+str(int(self.slider_rot.value()))+"°")
        roteq(self.slider_rot.value()/180 * sympy.pi)
        nnbarrier = numpy.roll(nnbarrier, int(self.slider_x.value()), axis=1)
        nnbarrier = numpy.roll(nnbarrier, int(self.slider_y.value()), axis=0)
        fresheq()
        
        if update:
            freshbarrier()
        #lock.release()

    def Change_Eq(self):
        self.slider_x.setValue(0)
        self.slider_y.setValue(0)
        self.slider_rot.setValue(0)
        Equation(self.line_xt.text(), self.line_yt.text(), int(self.line_tmin.text()), int(self.line_tmax.text()), int(self.line_exp.text()))

    def AutoConfirm(self, state):
        global update
        if state != Qt.Checked:
            update = False
        else:
            update = True
    
    def Unfold(self):
        self.button_unfold.setText("<<")
        self.button_unfold.clicked.connect(self.Fold)
        #self.layout_eqwindow.setSizeConstraint(QLayout.SetFixedSize)
        self.widget_unfold.setHidden(False)

    def Fold(self):
        self.button_unfold.setText(">>")
        self.button_unfold.clicked.connect(self.Unfold)
        #self.layout_eqwindow.setSizeConstraint(QLayout.SetFixedSize)
        self.widget_unfold.setHidden(True)

    def ClearBarrier(self):
        global xp, yp, nnbarrier, nbarrier
        xp=[]
        yp=[]
        nnbarrier = numpy.zeros((height,width),bool)
        #nbarrier = numpy.zeros((height,width),bool)
        fresheq()
        if update:
            freshbarrier()
    
    def PenEraser(self):
        global pen, eraser
        if pen:
            self.button_pen_eraser.setText('鼠标：擦除')
            pen = False
            eraser = True
        else:
            self.button_pen_eraser.setText('鼠标：绘制')
            eraser = False
            pen = True

    '''
    def closeEvent(self,event): #函数名固定不可变
        print(barrier == nnbarrier.all())
        a = barrier == nnbarrier.all()
        if a:
            traceback.print_exc()
        else:
            reply=QtWidgets.QMessageBox.question(self,u'未更新障碍',u'确认退出?',QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
            #QtWidgets.QMessageBox.question(self,u'弹窗名',u'弹窗内容',选项1,选项2)
            if reply==QtWidgets.QMessageBox.Yes:
                event.accept()#关闭窗口
            else:
                event.ignore()#忽视点击X事件
    '''

    def Reset(self):
        #编辑栏
        self.line_xt.setText("10*sin(t);16*((sin(t))**3);")
        self.line_yt.setText("10*cos(t);13*cos(t)-5*cos(2 * t)-2*cos(3*t)-cos(4*t);")
        self.line_tmin.setText('100')
        self.line_tmax.setText('100')
        self.line_exp.setText('1')

        # 滑动条
        self.slider_x.setValue(0)
        self.slider_y.setValue(0)
        self.slider_rot.setValue(0)

        # 进度条
        self.progressbar.setValue(0)
    



class Alert_window(QWidget):
    def __init__(self):
        super(Alert_window, self).__init__()

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('警告')
        self.setWindowIcon(QIcon('icon.ico'))
        self.resize(200, 200)

        self.label_alert = QLabel('计算发散，请重置数值')

        self.button_yes = QPushButton('重置')
        self.button_yes.clicked.connect(self.job)

        layout_altwindow = QGridLayout()
        layout_altwindow.addWidget(self.label_alert, 1, 1)
        layout_altwindow.addWidget(self.button_yes, 2, 1)

        self.setLayout(layout_altwindow)
    
    def job(self):
        main_window.Reset()
        sys.exit()



    

        



class Ld_window(QWidget):
    def __init__(self):
        super(Ld_window, self).__init__()
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setWindowTitle('升力阻力-代数 曲线')
        self.resize(600,425)

        self.ldcanvas = FigureCanvas(ldFig)
        self.ldcanvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.checkbox_ld = QCheckBox('刷新显示 升力阻力-代数 曲线', self)
        self.checkbox_ld.stateChanged.connect(self.Switch)
        #self.checkbox_ld.setChecked(True)
        self.checkbox_ld.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.button_clear = QPushButton('清除曲线')
        self.button_clear.clicked.connect(self.Clear)
        self.button_clear.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout_ldwindow = QGridLayout()
        layout_ldwindow.addWidget(self.ldcanvas, 1, 1, 1, 3)
        layout_ldwindow.addWidget(self.checkbox_ld, 2, 1)
        layout_ldwindow.addWidget(self.button_clear, 2, 3)
        

        self.setLayout(layout_ldwindow)

    def Draw(self):
        ax.set_xlabel(u'代数')
        ax.set_ylabel(u'力')
        ax.set_title(u'力-代数 曲线')
        #ax2.set_xlabel(u'代数')
        #ax2.set_ylabel(u'阻力(Fx)')
        #ax2.set_title(u'阻力-代数 曲线')
        l1, = ax.plot(list_gen, list_lift, 'b', label=u'升力')
        l2, = ax.plot(list_gen, list_drag, 'r', label=u'阻力')
        #ax2.plot(list_gen, list_drag, linewidth=1, color='blue')
        #ax.legend(l1,l2,(u'升力','阻力',))
        self.ldcanvas.draw()
    
    def Switch(self, state):
        global show_lift_drag
        if state == Qt.Checked:
            show_lift_drag = True
        else:
            show_lift_drag = False
    
    def Clear(self):
        ax.cla()
        ax.set_xlabel(u'代数')
        ax.set_ylabel(u'力')
        ax.set_title(u'力-代数 曲线')
        ax.xaxis.grid(True, which='major')
        ax.yaxis.grid(True, which='major')
        l1, = ax.plot(list_gen, list_lift, 'b', label=u'升力')
        l2, = ax.plot(list_gen, list_drag, 'r', label=u'阻力')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles[::-1], labels[::-1])
        #ax2.cla()

    def closeEvent(self,event): #函数名固定不可变
        self.checkbox_ld.setChecked(False)
        self.Clear()
        event.accept()
        '''
        reply=QtWidgets.QMessageBox.question(self,u'警告',u'确认退出?',QtWidgets.QMessageBox.Yes,QtWidgets.QMessageBox.No)
        #QtWidgets.QMessageBox.question(self,u'弹窗名',u'弹窗内容',选项1,选项2)
        if reply==QtWidgets.QMessageBox.Yes:
            event.accept()#关闭窗口
        else:
            event.ignore()#忽视点击X事件
        '''
    
    def showEvent(self, event):
        self.checkbox_ld.setChecked(True)
        event.accept()
        #traceback.print_exc()


class Lattice_window(QWidget):
    signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('自定义')
        self.setWindowIcon(QIcon('icon.ico'))

        


        layout = QGridLayout()

        self.label_height = QLabel('格子高:')
        self.label_width = QLabel('格子宽:')
        self.line_height = QLineEdit('100')
        self.line_width = QLineEdit('150')
        self.button_confirm = QPushButton('确定')
        self.button_confirm.clicked.connect(lambda:self.ChangeLattice(self.line_height.text(),self.line_width.text()))
        self.button_cancel = QPushButton('取消')
        self.button_cancel.clicked.connect(self.Exit)

        layout.addWidget(self.label_height, 1,1)
        layout.addWidget(self.line_height, 1,2)
        layout.addWidget(self.label_width, 2,1)
        layout.addWidget(self.line_width, 2,2)
        layout.addWidget(self.button_confirm, 3,1)
        layout.addWidget(self.button_cancel, 3,2)

        self.setLayout(layout)


    def ChangeLattice(self, height, width):
        global nheight, nwidth
        try:
            if (50<= int(height) <= 999) and (50 <= int(width) <= 999):
                nheight = int(height)
                nwidth = int(width)
                self.signal.emit('1')
                self.close()
            else:
                alert_window2 = QMessageBox(QMessageBox.Warning, '警告', '输入范围限制在[50,999]')
                alert_window2.exec_()
        except:
            traceback.print_exc()
            alert_window1 = QMessageBox(QMessageBox.Warning, '警告', '请输入数字')
            alert_window1.exec_()
    
    def Exit(self):
        self.close()





class Author_window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.label_introduction = QLabel("秦皇岛市第一中学高一年级十六班学生周支宇")

        layout.addWidget(self.label_introduction)

        self.setLayout(layout)

class Instructor_window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.label_introduction = QLabel("秦皇岛市第一中学")

        layout.addWidget(self.label_introduction)

        self.setLayout(layout)


class Thanks_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.ico'))
        layout = QVBoxLayout()
        self.label = QLabel("    特别感谢秦皇岛市第一中学，感谢它为我提供了一个良好的平台\n"
                            "    特别感谢我的父母，感谢他们支持我的爱好。\n"
                            #"    特别感谢武汉航达公司刘启峰同志，感谢他对我的耐心指导，感谢他对程序科学性问题上提出的宝贵建议\n"
                            "    特别感谢秦皇岛市第一中学信息处的指导教师们，感谢他们各方面的指导\n"
                            "    感谢我的姐姐，感谢她同我一起分享编写程序的成就感\n" \
                            "\n" \
                            "    在此献上最诚挚的谢意！谢谢你们！")

        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignTop)
        self.label.setFont(QFont("宋体", 12))
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setFixedSize(300,300)


class TStatus(QThread):
    def __init_(self):

        super(TStatus, self).__init__()

    def run(self):
        self.timer = QTimer()  # 使用Qtimer代替time防止bug卡死
        while True:
            # time.sleep(0.1)
            main_window.fresh_status()
            self.timer.start(100)  # 单位为毫秒

lock = threading.Lock()



#euqation_window = Equation_window()
if __name__ == '__main__':
    # global satrt_start, first_sr_var, bindabel, change_barrier_switch

    threadAnimation = threading.Thread(target=starter, name='T_Animation')  # 动画开始线程
    threadAnimation.start()

    app = QApplication(sys.argv)
    #main_window = Main_window()
    main_window = Main_window()
    thread_it(fresh_status)
    matplotlib.pyplot.connect('motion_notify_event', mouse_move)
    matplotlib.pyplot.connect('figure_enter_event', fresh_details)
    matplotlib.pyplot.connect('figure_leave_event', close_details)
    #thread = TStatus()
    #thread.start()
    main_window.show()
    #main_window.Show()
    sys.exit(app.exec_())

    #GUI()

# threadChangeBarrier = threading.Thread(target=change_barrier_switch, name='T_ChangeBarrier')
# threadChangeBarrier.start()
# thread3 = threading.Thread(target=performance, name='T_Performance')
# thread3.start()

# nextFrame(arg)


# matplotlib.pyplot.show()
