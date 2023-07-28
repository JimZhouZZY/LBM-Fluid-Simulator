#!/usr/bin/python
# -*- coding: utf-8 -*-

################################################
#LBMFluidSimulatorTkinterVersionV0.1.1         #
#Made by ZZY                                   #
#2021.11 - 2022.3                              #
#秦皇岛市海港区                                 #
################################################
###############################################################################################################
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
# 日志：..later..  解决失真问题。numpy的输出是带有科学计数法的，直接裁剪字符串会改变数值，使用round()即可。
# 日志：2022/2/3   初步实现对河流的数值模拟
# 日志：2022/3/11  好久没记了。懒。Pyqt5
# 日志：懒懒懒
# 日志：2022/3     做完啦！
# 日志：2022/4     删去sympy，方程模块变快了。
# 日志：2022/4/13  Tkinter...为了五月份的比赛
# 日志: 2022/11/5  尝试多模块重构，工作量太大了，周日之前做不完，加点注释吧。
# 日志：..Later..  美化代码
###############################################################################################################


############################
#Generic imports
############################
import os                 # os, sys 用于进行系统操作
import sys
import time               # 时间，用于计时计算
import tkinter            # GUI库
import traceback          # 错误溯源
import threading          # 多线程
import multiprocessing    # 多进程，但是暂未使用
import matplotlib.pyplot  # matplotlib的画图库
import tkinter.messagebox # 消息窗口
import tkinter.filedialog # 文件选择器
import tkinter.ttk as ttk # ttk美化
from   numpy     import * # 计算库
from   fileinput import filename # 方便文件读写
from   matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # matplotlib的Tkinter接口


############################
#初始化常规数据
############################
# -----------布尔类型----------- 
changeable_barrier_switch = False # 可变障碍开关，用于开关侵蚀模拟
change_animation_switch = False   # 改变动画类型开关
change_barrier_switch = False     # 改变障碍开关
killThreadAnimation = False       # 关闭动画开关
force_vector_switch = False       # 受力箭头开关，注意这一功能还没有开发出来
draw_start_switch = True          # 绘图开关
change_viscosity = False          # 改变粘度
show_lift_drag = False            # 展示力-代数曲线开关
drawing_start = False             # 开始绘图开关，指鼠标摁下
write_switch = False              # 写入开关
lock_draw_2 = False               # ***锁定画图，后面的2是沿用下来的,可能是远古时代Debug产生的,现应该无用
start_start = False               # 开始动画开关，名称是远古时代Debug沿用下来的
first_st_var = True               # 障碍方程相关
first_write = True                # ***首次写入,可能是远古时代Debug产生的,现应该无用
lock_draw = False                 # ***锁定画图,可能是远古时代Debug产生的,现应该无用
animating = False                 # 正在动画中, 用于线程之间同步, 提高效率
save_lock = False                 # 保存时锁定
oncanvas = False                  # 鼠标在Plot图上， 用于绘画以及参数显示切换到探测
changing = False                  # 正在改变障碍
switch_eq = True                  # 方程开关，可能是远古时代Debug产生的
change_v = False                  # 改变初速度
bindable = False                  # ***允许绑定, 远古时代解决tkinter listbox bug的产物, 现应该无用
drawing = False                   # 正在绘画
moving = False                    # 鼠标在移动
eraser = False                    # 橡皮擦模式
update = True                     # 自动更新曲线
dforce = True                     # 微扰, 在算法的最开始使用以增加不稳定性, 使得结果更快失稳, 提高科学性(计算机计算的太理想论)
alert = False                     # 警报
kill = False                      # 结束程序
skip = True                       # 跳过一代运算, 用于Bug出现时继续运算
pen = True                        # 铅笔模式
# -----------空列表-----------
list_lift = []                    # 用于储存升力历史数据
list_drag = []                    # 用于储存阻力历史数据
list_gen = []                     # 用于储存代数历史数据
nx4 = []                          # 用于储存新速度的列表
ny4 = []
nx1 = []
nx2 = []
ny1 = []
ny2 = []
nx3 = []
ny3 = []
xp = []                           # 用于记录障碍数据的横坐标
yp = []                           # 用于记录障碍数据的纵坐标
# -----------整型浮点-----------
pi = 3.1415926535
nheight = 100
nwidth = 150
last_gen = 0
deep = 225
ncurl = 1
xdata = 0
ydata = 0
edge = 0
drag = 0
lift = 0
agln = 0
tank = 0
gps = 0
fps = 0
spd = 1
gen = 0
t0 = 0
t = 0
# -----------格子规格----------- 
height = 100
width =  150
# -----------流动参数-----------
viscosity = 0.020                  # 粘性系数
omega = 1 / (3 * viscosity + 0.5)  # 松驰系数
one36th = 1.0 / 36.0               # 预计算一些常用的数值，加速运算
four9th = 4.0 / 9.0
one9th = 1.0 / 9.0
u0 = 0.1                           # 初速度
u1 = u0
nviscosity = viscosity             # 新粘度
# -----------动画参数----------- 
animation_type = 0                 # 动画类型（0=旋度动画，1=密度动画, 2=流线）
contrast = 1                       # 对比度


############################
#初始化numpy数据
############################

# 这些变量用于计算矢量空间， x1，y1 乘4， 来减小箭头的密度
y, x = mgrid[0:height:1, 0:width:1]
y1, x1 = mgrid[0:int(height/4):1, 0:int(width/4):1]
x1 = 4*x1
y1 = 4*y1

# 宏观速度
ux1 = zeros((int(height/4), int(width/4)))
uy1 = zeros((int(height/4), int(width/4)))
u2 = zeros((int(height), int(width))) # u2 = u * u

# 微观速度，在D2Q9模型下一共有九个方向
'''
           n4                n3
           +-----------------^----------------xxn2
           |xx               |             xxx |
           |  x              |           xxx   |
           |    xx           |         xx      |
           |     xxx         |       xxx       |
           |       xxxx      |     xxx         |
           |          xxx    |   xxx           |
           |            xxx  |xxx              |
           |               xxxx                |
        n5 <---------------xn0x---------------->n1
           |             xxx |xx               |
           |           xxx   | xx              |
           |         xxx     |  xxx            |
           |       xxx       |    xxx          |
           |     xxx         |      xx         |
           |    xx           |       xxx       |
           |  xx             |         xx      |
           |xxx              |           xx    |
           xx                |             xx  |
           ------------------v---------------xx|
         n6                 n7                 n8
'''
n0 = four9th * (ones((height, width)) - 1.5 * u0 ** 2)
n3 = one9th * (ones((height, width)) - 1.5 * u0 ** 2)
n7 = one9th * (ones((height, width)) - 1.5 * u0 ** 2)
n1 = one9th * (ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n5 = one9th * (ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n2 = one36th * (ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n8 = one36th * (ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n4 = one36th * (ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n6 = one36th * (ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
n = [n0, n1, n2, n3, n4, n5, n6, n7, n8]

# 密度，无量纲
rho = n[0] + n[3] + n[7] + n[1] + n[5] + n[2] + n[8] + n[4] + n[6]

# x，y方向的宏观速度
ux = (n[1] + n[2] + n[8] - n[5] - n[4] - n[6]) / rho
uy = (n[3] + n[2] + n[4] - n[7] - n[8] - n[6]) / rho

# 方程系数矩阵，分别对应：权重，ux， uy， u2， uxuy， ux2， uy2
c = array([[four9th, 0, 0, 0, 0, 0, 0],
         [one9th, 1, 0, 0, 0, 1, 0],
         [one36th, 1, 1, 1, 1, 0, 0],
         [one9th, 0, 1, 0, 0, 0, 1],
         [one36th, -1, 1, 1, -1, 0, 0],
         [one9th, -1, 0, 0, 0, 1, 0],
         [one36th, -1, -1, 1, 1, 0, 0],
         [one9th, 0, -1, 0, 0, 0, 1],
         [one36th, 1, -1, 1, -1, 0, 0]])

list_text = zeros((height, width), float)

# 新的障碍图像数据Array
nbImageArray = zeros((height, width))

# 障碍的"血量", 用于侵蚀模拟
blood = ones((height, width))


############################
#初始化障碍
############################

# 初始化矢量空间
for i in range(int(height/4)):
    for j in range(int(width/4)):
        ux1[i, j] = ux[i*4, j*4]
        uy1[i, j] = uy[i*4, j*4]
 
# 初始化barrier,全赋值为0(空)
barrier = zeros((height, width), bool)

# 绘制一个高16px的竖直板
for i in range(16):
    barrier[int((height / 2) + 8 - i), int(width / 2)] = True

# nbarrier用于更新计算中的障碍
# nnbarrier用于更新障碍方程窗口中的障碍
nbarrier = zeros((height, width), bool) 
nnbarrier = zeros((height, width), bool) 
nbarrier = barrier
nnbarrier = nbarrier 

# 把刚才绘制的数据赋到数据点坐标列表里
for i in range(height):
    for j in range(width):
        if nnbarrier[i, j]:
            xp.append(j - width / 2)
            yp.append(i - height / 2)

# barrier向各个方向平移一个单位的位置, 也就是边界层
# 这里的roll也是numpy的函数
barrier3 = roll(barrier, 1, axis=0) 
barrier7 = roll(barrier, -1, axis=0) 
barrier1 = roll(barrier, 1, axis=1)  
barrier5 = roll(barrier, -1, axis=1)
barrier2 = roll(barrier3, 1, axis=1)
barrier4 = roll(barrier3, -1, axis=1)
barrier8 = roll(barrier7, 1, axis=1)
barrier6 = roll(barrier7, -1, axis=1)

# 边阶层
barrier_zone = zeros((height, width))
barrier_zone = zeros((height, width))
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


############################
#LBM算法核心
############################

# 流动运算，简单地把微观速度传递到相应方向的下一个格子
def stream():
    global change_barrier_switch, nbarrier, barrier_zone, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood
    global n
    try:
        # 先看看是否结束程序了
        if kill:
            sys.exit()
        elif killThreadAnimation:
            print('KILLED')
            sys.exit()
        
        # 调用Checkbox的状态，看看要不要改变障碍模式
        if main_window.bool_changeable_barrier.get():
            changeable_barrier()
        
        # 先计算障碍的变化，事实上顺序无关紧要
        if change_barrier_switch:
            print("CHANGE")
            
            # 把barrier更新成nbarrier
            barrier = nbarrier
            
            # 更新边界
            barrier3 = roll(barrier, 1, axis=0)
            barrier7 = roll(barrier, -1, axis=0)
            barrier1 = roll(barrier, 1, axis=1)
            barrier5 = roll(barrier, -1, axis=1)
            barrier2 = roll(barrier3, 1, axis=1)
            barrier4 = roll(barrier3, -1, axis=1)
            barrier8 = roll(barrier7, 1, axis=1)
            barrier6 = roll(barrier7, -1, axis=1)
            
            # 刷新Barrier图像
            bImageArray[:, :, 3] = 0  
            bImageArray[barrier, 3] = 255
            
            # 关开关
            change_barrier_switch = False
            
            # 更新‘血量’
            blood[:, :] = 0
            blood[barrier] = 100
            
            # 更新边界区域
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
        
        # 流动运算，简单地把微观速度传递到相应方向的下一个格子
        n[3] = roll(n[3], 1, axis=0)  
        n[2] = roll(n[2], 1, axis=0)
        n[4] = roll(n[4], 1, axis=0)
        n[7] = roll(n[7], -1, axis=0)
        n[8] = roll(n[8], -1, axis=0)
        n[6] = roll(n[6], -1, axis=0)
        n[1] = roll(n[1], 1, axis=1) 
        n[2] = roll(n[2], 1, axis=1)
        n[8] = roll(n[8], 1, axis=1)
        n[5] = roll(n[5], -1, axis=1)
        n[4] = roll(n[4], -1, axis=1)
        n[6] = roll(n[6], -1, axis=1)
        
        # 边阶层处理，反弹格式对应着：                       #此处可能出错
        # 0-反弹格式：三侧反弹
        # 1-反弹格式：方腔流（全侧反弹）
        # 2-反弹格式：无反弹
        # 3-反弹格式：风洞（上下反弹）
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

# 平衡状态公式，c是之前定义的系数矩阵。
# 这是BGK近似
def feq(num):
    return (c[num, 0] * rho * (u2115 + 3 * (c[num, 1] * ux + c[num, 2] * uy)  + c[num, 5] * 4.5 * ux2 + c[num, 6] * 4.5 * uy2 + 4.5 * (c[num, 3] * u2 + c[num, 4] * 2 * uxuy)))

# 计算碰撞，这是LBM的精髓所在
# 这里运用 BGK 近似
def collide():
    global rho, ux, uy, n, k, u0, u1, u2, change_v, change_viscosity, viscosity, \
        omega, gen, dforce, barrier, uxuy, u2115, ux2, uy2
    
    # 先看看是否结束程序了
    if kill:
        sys.exit()
    elif killThreadAnimation:
        print('KILLED')
        sys.exit()
    
    try:
        # 预计算一些常用的数值，加速运算
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
        
            # 著名的LBM状态转移方程
            # n = (1-omega)n + feq * omega
            n[i] = (1 - omega) * n[i] + omega * feq(i)
            
        for i in range(height):
            try:
                # 对反弹格式3（无反弹）特殊处理，加速运算
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
                # 防一手
                traceback.print_exc()
        gen += 1
    except:
        traceback.print_exc()


############################
#其他计算函数
############################

# 计算升力和阻力
# ld = Lift&Drag,前者为0
def Lift_Drag(ld): 
    global ux, uy, drag, lift, barrier_zone
    if ld:
        lift = 0
        for i in range(height):
            for j in range(width):
                if barrier_zone[i, j]:
                    lift += -uy[i, j]
        return lift
    elif not ld:
        drag = 0
        for i in range(height):
            for j in range(width):
                if barrier_zone[i, j]:
                    drag += u0 - ux[i, j]
        return drag


# 计算宏观流动的旋度:
def curl(ux, uy):
    global ncurl
    ncurl = roll(uy, -1, axis=1) - roll(uy, 1, axis=1) - roll(ux, -1, axis=0) + roll(ux, 1,axis=0)
    return ncurl

#计算动画数据
def frames_per_second():
    global t0, fps, gps, last_gen
    t1 = time.perf_counter()
    dt = t1 - t0
    t0 = t1
    fps = '%.1f' % (1.0/dt)
    gps = '%.1f' % ((gen - last_gen) / dt)
    last_gen = int(gen)


############################
#刷新数据
############################

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


############################
#鼠标获取和绘制
############################
def mouse_move(event):
    global xdata, ydata, moving
    if (not moving and oncanvas) or drawing:
        moving = True
        xdata, ydata = event.xdata, event.ydata
        if not drawing:
            time.sleep(0.01)
        moving = False

def drawing_mouse_move(event):
    global xdata, ydata
    xdata, ydata = event.xdata, event.ydata

def draw_pressed(event):
    global drawing, nnbarrier, xp, yp, nbarrier, barrier
    try:
        drawing = True
        gen=0
        last_xdata = int(xdata)
        last_ydata = int(ydata)
        if drawing:
            nnbarrier = zeros((height,width), bool)
            for i in range(len(xp)):
                nnbarrier[int(yp[i] + height/2), int(xp[i] + width/2)] = True
        while drawing:
            try:
                main_window.Drawing()
                if pen and (xdata != None):
                    print('Pen')
                    xline = linspace(round(last_xdata), round(xdata), num=50)
                    yline = linspace(round(last_ydata), round(ydata), num=50)
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
                    xline = linspace(round(last_xdata), round(xdata), num=50)
                    yline = linspace(round(last_ydata), round(ydata), num=50)
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
                traceback.print_exc()
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
    global canvaseq, drawing_start, draw_start_switch, nnbarrier
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


############################
#初始化matplotlib
############################
matplotlib.pyplot.switch_backend('agg') # matplotlib 嵌入模式
matplotlib.pyplot.rcParams['font.sans-serif']=['SimHei'] # 用来正常显示中文标签
matplotlib.pyplot.rcParams['axes.unicode_minus']=False # 用来正常显示负号

eqFig = matplotlib.pyplot.figure(num=2, figsize=(5, 3))
eqax = eqFig.add_subplot(111)
eqax.xaxis.grid(True, which='major')
eqax.yaxis.grid(True, which='major')
eqbImageArray = zeros((height, width, 4), uint8)  # an RGBA image
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

theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
fluidImage = matplotlib.pyplot.imshow(curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                      cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
matplotlib.pyplot.connect('motion_notify_event', mouse_move)
matplotlib.pyplot.connect('figure_enter_event', fresh_details)
matplotlib.pyplot.connect('figure_leave_event', close_details)


############################
#动画控制
############################
def nextGen(gens):
    global start_start, animating
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
            animating = False
            main_window.ShowStart()
            alert = True
            thread_it(play)
            break
        wt = 0
        while True:
            if not changing:
                break
            wt += 1
            if wt == 10:
                print("Warning: Too long for waiting.")
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
                    save_lock = True
                    theFig.clf()
                    theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                    fluidImage = matplotlib.pyplot.streamplot(x, y, ux, uy, density=contrast, color='black', linewidth=0.5, arrowsize=0.5)
                    bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                    bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                    barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                    save_lock = False
                elif animation_type == 3:
                    for i in range(int(height/4)):
                        for j in range(int(width/4)):
                            ux1[i, j] = ux[i*4, j*4]
                            uy1[i, j] = uy[i*4, j*4]
                    save_lock = True
                    theFig.clf()
                    theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                    fluidImage = matplotlib.pyplot.quiver(x1, y1, ux1, uy1, minlength=0.01, scale=5*(2 - contrast))
                    bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                    bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                    barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                    save_lock = False
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
                change_animation(main_window.combo_animation_type.get())
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
        thread_it(main_window.ld_Window.Draw)
    barrierImage.set_array(bImageArray)
    frames_per_second()
    if write_switch:
        write()
        if first_write:
            first_write = False
    main_window.Draw()

def starter():
    global start_start, first_st_var, bindable, change_barrier_switch, animating
    while True:
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
            animating = False
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

def HelpAniSpd(h_spd):
    global spd
    spd = float(h_spd)

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
            wt = 0
            while True:
                if not save_lock:
                    break
                time.sleep(0.01)
                wt += 1
                if wt == 25:
                    print("RuntimeError: Too long for waiting.")
                    break
            theFig.clf() # 请勿删去否则plt.draw速度减慢
            if type == u'旋度动画' or type==0:
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
                bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                
                #fluidImage = matplotlib.pyplot.imshow(curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                                    #cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
            elif type == u'密度动画' or type==1:
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
                bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                '''
                fluidImage = matplotlib.pyplot.imshow(rho, origin='lower', norm=matplotlib.pyplot.Normalize(0.9, 1.1),
                                                    cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
                                            '''
            elif type == u'流线' or type==2:
                animation_type = 2
                '''
                del theFig
                del fluidImage
                del bImageArray
                del barrierImage
                '''
                theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
                #fluidImage = theFig.add_subplot(111)
                fluidImage = matplotlib.pyplot.streamplot(x, y, ux, uy, density=contrast, color='black', linewidth=0.5)
                bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                #theFig.show()
                #main_window.Draw()
                #bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                #bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                #barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
                #ax.clear()
            elif type == u'速度矢量' or type==3:
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
                fluidImage = matplotlib.pyplot.quiver(x1, y1, ux1, uy1, minlength=0.01, scale=5 * (2 - contrast))
                bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
            elif type == u'水平速度' or type==4:
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
                bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
            elif type == u'垂直速度' or type==5:
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
                bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
                bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
                barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')
            main_window.Draw()
            lock_draw = False
        except:
            traceback.print_exc()


############################
#声音控制
############################
playing = False
def play():
    global playing
    if not playing:
        playing = True
        winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
        playing = False


############################
#常规函数
############################
def thread_it(func, *args):
    '''将函数打包进线程'''
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()

def process_it(func, *args):
    '''将函数打包进程'''
    p = multiprocessing.Process(target=func, args=args)
    p.start()


############################
#障碍方程
############################
def roteq(agl):
    global nnbarrier, agln  # , nxp, nyp
    # print(xp, '\n', yp)
    nxp = []
    nyp = []
    nnbarrier = zeros((height, width), bool)
    agln = agl
    cosa = float(cos(agln))  # 预运算
    sina = float(sin(agln))
    try:
        for j in range(len(xp)):
            nxp.append(round(xp[j] * cosa - yp[j] * sina))
            nyp.append(round(yp[j] * cosa + xp[j] * sina))
            nnbarrier[int(nyp[j] + height / 2), int(nxp[j] + width / 2)] = True
    except:
        traceback.print_exc()
        print('ERROR: \n ROTEQ: Index does not match')

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


############################
#障碍刷新
############################
def freshbarrier():
    global nnbarrier, nbarrier, change_barrier_switch, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood, changing
    """
    wt = 0
    while True:
        if not animating:
            break
        print("WAITING")
        time.sleep(0.03)
        wt += 1
        if wt == 25:
            print("RuntimeError: Too long for waiting.")
            break
    """
    changing = True
    barrier = nnbarrier
    barrier3 = roll(barrier, 1, axis=0) 
    barrier7 = roll(barrier, -1, axis=0)
    barrier1 = roll(barrier, 1, axis=1)
    barrier5 = roll(barrier, -1, axis=1)
    barrier2 = roll(barrier3, 1, axis=1)
    barrier4 = roll(barrier3, -1, axis=1)
    barrier8 = roll(barrier7, 1, axis=1)
    barrier6 = roll(barrier7, -1, axis=1)
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
    wt = 0
    while True:
        if not animating or animating:
            barrier = nbarrier
            barrier3 = roll(barrier, 1, axis=0)
            barrier7 = roll(barrier, -1, axis=0)
            barrier1 = roll(barrier, 1, axis=1)
            barrier5 = roll(barrier, -1, axis=1)
            barrier2 = roll(barrier3, 1, axis=1)
            barrier4 = roll(barrier3, -1, axis=1)
            barrier8 = roll(barrier7, 1, axis=1)
            barrier6 = roll(barrier7, -1, axis=1)
            bImageArray[:, :, 3] = 0  # 刷新Barrier图像
            bImageArray[barrier, 3] = 255
            barrierImage.set_array(bImageArray)
            change_barrier_switch = False
            blood[:, :] = 0
            blood[barrier] = 100
            main_window.Draw()
            break
        else:
            wt += 1
            time.sleep(0.03)
            if wt == 25:
                print("RuntimeError: Too long for waiting.")
                break
    changing = False

def change_barrier(barrier_set):
    global change_barrier_switch, nbarrier
    if barrier_set == u'(默认)':
        pass
    else:
        nbarrier = zeros((height, width), bool)
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

def Equation(inputx, inputy, tstart, tend, ex,):
    global change_barrier_switch, nbarrier, nnbarrier, start_start, canvaseq, ninputx, ninputy, ix, iy, xp, yp
    try:
        #xp = []
        #yp = []
        #x, y, t = sympy.symbols("x y t", real=True)
        equation_xs = inputx.split(';')
        for i in range(len(equation_xs)):
            if equation_xs[i] == '':
                del equation_xs[i]
        equation_ys = inputy.split(';')
        for i in range(len(equation_ys)):
            if equation_ys[i] == '':
                del equation_ys[i]
        print(equation_xs)
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
                nnbarrier = zeros((height, width), bool)
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
            for iv in range(len(equation_xs)):
                Exs = equation_xs[iv].split('u')
                Eys = equation_ys[iv].split('u')
                for t in range(exa * st, exa * ed, 1):
                    step += 1
                    #main_window.SetEqProgressBar(100*step/steps)
                    ProgressbarEq['value'] = 100*step/steps
                    #nt = tent / exa
                    Ex2 = ''
                    Ey2 = ''
                    for i in range(len(Exs)):
                        if i != len(Exs) - 1:
                            Ex2 = Ex2 + Exs[i] + str(tent)
                        else:
                            Ex2 = Ex2 + Exs[i]
                    for i in range(len(Eys)):
                        if i != len(Eys) - 1:
                            Ey2 = Ey2 + Eys[i] + str(tent)
                        else:
                            Ey2 = Ey2 + Eys[i]
                    #print(Ex2)
                    x = int(round(eval(Ex2) + width / 2 ))
                    #print(x)
                    y = int(round(eval(Ey2) + height / 2 ))
                    xp.append(x - width / 2)
                    yp.append(y - height / 2)
                    if 0 <= x < width and 0 <= y < height -1:
                        print(x, y)
                        nnbarrier[y, x] = True
                print("-> FRESHEQ")
                fresheq()
            if update:
                freshbarrier()
    except:
        traceback.print_exc()
        main_window.Alert()

def changeable_barrier():
    global rho, bImageArray, deep, height, width, nbImageArray, n, barrier, nbarrier, change_barrier_switch, blood, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6
    blood[barrier] += - 1000 * (abs(n[5][barrier5]- n[1][barrier5]) + abs(n[1][barrier1] - n[5][barrier1]) +
                                  abs(n[7][barrier7] - n[3][barrier7]) + abs(n[3][barrier3] - n[7][barrier3]) +
                                  abs(n[2][barrier2] - n[6][barrier2]) + abs(n[6][barrier6] - n[2][barrier2]) +
                                  abs(n[8][barrier8] - n[4][barrier8]) + abs(n[4][barrier4] - n[8][barrier4]))
    #print(blood[45, 0])
    for i in range(height):
        for j in range(width):
            if blood[i, j] < 0:
                #print('DELETE')
                nbarrier[i, j] = 0
                change_barrier_switch = True
    if (True in nbarrier) == False:
        main_window.check_changeable_barrier.invoke()


############################
#辅助函数 
############################
def help_u0(var):
    global u0
    u0 = float(var)
    main_window.text_u0.set(str("%.3f" %u0))

def help_viscosity(var):
    global viscosity
    viscosity = float(var)
    main_window.text_viscosity.set(str("%.3f" %viscosity))

def help_change_barrier(arg):
    change_barrier(main_window.text_barrier.get())

def help_change_animation(arg):
    change_animation(main_window.text_animation_type.get())


############################
#文件读写
############################
def write():
    global gen, ncurl, first_write
    print('WRITE GEN=', gen)
    # os.remove('data.txt')
    if first_write:
        output = open('data.LBM', 'w')  # 重新写入
        first_write = False
    else:
        output = open('data.LBM', 'a')  # 继续写入
    for i_write in range(height):
        for j_write in range(width):
            ostring = str(round(ncurl[i_write, j_write], 6))
            output.write(ostring)
            if j_write != width - 1:
                output.write(',')
        output.write('\n')
    output.close()

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

def file_import(filename):
    global ux, uy, rho, edge, nwidth, nheight, gen, n, nbarrier, change_barrier_switch, nnbarrier, xp, yp, list_gen, list_lift, list_drag, last_gen
    try:
        file = load(filename)
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
        change_animation(main_window.combo_animation_type.get())
        main_window.ld_Window.Draw()
        main_window.Draw()
    except:
        traceback.print_exc()


############################
#窗口布局
############################
# 主窗口布局如图：
        '''
        +-------------------------------------------------------------+
        |+--------------------------------------++-------------------+|
        ||                                      ||  Lable with pic   ||
        ||           frame with lable           ||                   ||
        |+--------------------------------------++-------------------+|
        ||                                      |+++++-------+++++++++|
        ||                                      |++++|Sliders|++++++++|
        ||                                      |+++++-------+++++++++|
        ||                                      +-+++++++++++++++++++-+
        ||                                      | +-----------------+ |
        ||                                      | | Lables          | |
        ||           Canvas                     | |       +--------++ |
        ||                                      | |       |Button  || |
        ||                                      | +-------+--------+| |
        ||                                      | +-------+Checkbox++ |
        ||                                      | |                 | |
        ||                                      | | Lables n Sliders| |
        ||                                      | |                 | |
        |+--------------------------------------+ +-----------------+ |
        +---------------------------------------+-+-----------------+-+
        '''
# 障碍方程窗口布局如图：
        '''
        +-----+----+-----+---+------------------------------+-++---+---+
        |x()= |++++|Input|box|++++++++++++++++++++++++++++++| ||BTN|+++|
        |y()= |+++++-----+---+++++++++++++++++++++++++++++++| ++--++--+|
        |     +----+++-----++++------+----------+-----+-----+ |PRG|BAR||
        |  t start:|+|INPUT|++| t end| INPUT BOX|ocnc |     | +---+---++
        |          |++-----+++|      +----------+     +-----+          |
        | +--------+----------+------+----------+-----+-----++  +----+ |
        | |                                                  |  |  S | |
        | |                                                  |  |  L | |
        | |                                                  |  |  I | |
        | |                                                  |  |  D | |
        | |                                                  |  |  E | |
        | |          CANVAS                                  |  |  R | |
        | |                                                  |  |    | |
        | |                                                  |  |    | |
        | |                                                  |  |    | |
        | |                                                  |  |    | |
        | |                                                  |  |    | |
        | |                                                  |  |    | |
        | |                                                  |  |    | |
        | +--------------------------------------------------+  +----+ |
        | |        SLIDER                                    |         |
        | +----------------++------+-+----+--+--++-----+-+--++------+  |
        |                  ||Ck bx |+|DRAW|++|  ||CLEAR|+|  ||UPDATE|  |
        +------------------++------+-+----+--+--++-----+-+--++------+--+
        '''
# 升力阻力-代数曲线窗口布局如图：
        '''
        +---------------------------------------------------------------------------------------+
        |                                                                                       |
        |                                                                                       |
        |                             Lift-Drag Curve                                           |
        |     +-------------------------------------------------------------+-----+------+      |
        |     |                                                             |+++++|LIFT  |      |
        | 0.04-                                                             +-----+DRAG  |      |
        |     |                                                                          |      |
        |     |                                                                          |      |
        | 0.02-                                                                          |      |
        |     +                                                                          |      |
        | 0.00-                                                                          |      |
        |     +                                                                          |      |
        | -0.02                                                                          |      |
        | -0.04                                                                          |      |
        |     ---------1-------------1------------1-----------1-------------+------------+------+
        |            -0.04         -0.02         0.0         0.02           |CHECK BOX   |CLEAR |
        |                                                                   |            |      |
        +-------------------------------------------------------------------+------------+------+
        '''
class Main_window(tkinter.Frame):
    def __init__(self, master):
        super().__init__(master)
        global canvas, canvaseq, canvasld
        
        self.equation_window = Equation_window()
        self.ld_Window = Ld_window()

        root.title("LBM流体力学数值模拟计算器")
        root.resizable(width=False, height=False)

        self.eqwinlock = False

        self.text_u0 = tkinter.StringVar()
        self.text_viscosity = tkinter.StringVar()
        self.text_u0.set(str("%.3f" % u0))
        self.text_viscosity.set(str("%.3f" % viscosity))
        self.text_barrier = tkinter.StringVar()
        self.text_animation_type = tkinter.StringVar()
        self.text_animation_speed = tkinter.StringVar()
        self.text_animation_speed.set('1.000')
        self.text_animation_contrast = tkinter.StringVar()
        self.text_animation_contrast.set('1.000')
        self.text_label_status_gen = tkinter.StringVar()
        self.text_label_status_fps = tkinter.StringVar()
        self.text_label_status_gps = tkinter.StringVar()
        self.text_label_status_barrier = tkinter.StringVar()
        self.text_label_status_gen.set("代数："+ str(gen) + " 代        ")
        self.text_label_status_fps.set("帧率：" + str(fps) + " 帧/秒        ")
        self.text_label_status_gps.set("代率：" + str(gps) + " 代/秒        ")
        self.text_label_status_barrier.set("障碍：不可用")
        self.bool_changeable_barrier = tkinter.BooleanVar()
        self.bool_changeable_barrier.set(False)
        self.bool_auto_update = tkinter.BooleanVar()
        self.bool_auto_update.set(True)
        self.bool_ld_auto_update = tkinter.BooleanVar()
        self.bool_ld_auto_update.set(True)

        #菜单栏
        self.menuBar = tkinter.Menu(root)
        root.config(menu=self.menuBar)

        self.menu_file = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='文件',menu=self.menu_file)
        self.menu_file.add_command(label='新建',command=self.Reset)
        self.menu_file.add_command(label='打开',command=self.ChooseFile)
        self.menu_file.add_command(label='保存',command=self.Export)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='截图',command=lambda:self.SavePhotoStep2(''))
        self.menu_file.add_command(label='截图为',command=self.SavePhoto)
        self.menu_file.add_separator()
        self.menu_file.add_command(label='退出',command=self.Exit)

        self.menu_operation = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='操作',menu=self.menu_operation)
        self.menu_operation.add_command(label='开始',command=HelpStart)
        self.menu_operation.add_command(label='暂停',command=HelpPause)
        self.menu_operation.add_separator()
        self.menu_operation.add_command(label='下一代',command=lambda:nextFrame(1))
        self.menu_operation.add_command(label='下十代',command=lambda:nextFrame(10))
        self.menu_operation.add_command(label='下百代',command=lambda:nextFrame(100))
        self.menu_operation.add_command(label='下千代',command=lambda:nextFrame(1000))
        self.menu_operation.add_separator()
        self.menu_operation.add_command(label='重置参数',command=self.Reset)

        self.menu_view = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='查看',menu=self.menu_view)
        self.menu_view.add_command(label='旋度动画',command=lambda:change_animation(0))
        self.menu_view.add_command(label='密度动画',command=lambda:change_animation(1))
        self.menu_view.add_command(label='流线',command=lambda:change_animation(2))
        self.menu_view.add_command(label='速度矢量',command=lambda:change_animation(3))
        self.menu_view.add_command(label='水平速度',command=lambda:change_animation(4))
        self.menu_view.add_command(label='垂直速度',command=lambda:change_animation(5))
        self.menu_view.add_separator()
        self.menu_view.add_command(label='升力阻力-代数 图',command=self.LiftDragWindow)

        self.menu_advanced = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='高级',menu=self.menu_advanced)
        self.menu_advanced.add_command(label='格子规格：50x70',command=lambda: self.ChangeLattice(50,75))
        self.menu_advanced.add_command(label='格子规格：60x90',command=lambda: self.ChangeLattice(60,90))
        self.menu_advanced.add_command(label='格子规格：80x120',command=lambda: self.ChangeLattice(80,120))
        self.menu_advanced.add_command(label='格子规格：100x150',command=lambda: self.ChangeLattice(100,150))
        self.menu_advanced.add_command(label='格子规格：160x240',command=lambda: self.ChangeLattice(160,240))
        self.menu_advanced.add_command(label='格子规格：200x300',command=lambda: self.ChangeLattice(200,300))
        self.menu_advanced.add_command(label='自定义格子规格',command=self.LatticeWindow)
        self.menu_advanced.add_separator()
        self.menu_advanced.add_command(label='反弹格式：风洞（上下反弹）', command=lambda: self.ChangeEdge(0))
        self.menu_advanced.add_command(label='反弹格式：无反弹', command=lambda: self.ChangeEdge(1))
        self.menu_advanced.add_command(label='反弹格式：三侧反弹', command=lambda: self.ChangeEdge(2))
        self.menu_advanced.add_command(label='反弹格式：方腔流（全侧反弹）', command=lambda: self.ChangeEdge(3))

        self.menu_about = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='关于',menu=self.menu_about)
        

        self.menu_help = tkinter.Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='帮助',menu=self.menu_help)


        #框线
        self.layout_window = tkinter.Frame(root)
        self.layout_window.grid()
        # 主窗口结构
        # cnb-{status} | snf-{fluid}
        #    -{canvas} |    -{barrier}
        #    -{button} |    -{animation}
        
        #左侧 canvas and button
        self.layout_cnb = tkinter.Frame(self.layout_window)
        self.layout_cnb.grid(column=0, row=0)

        self.layout_status = tkinter.LabelFrame(self.layout_cnb, text="基本信息",bd=1)
        self.layout_canvas = tkinter.Frame(self.layout_cnb)
        canvas = FigureCanvasTkAgg(theFig, self.layout_canvas)
        canvas.get_tk_widget().grid()
        
        canvaseq = FigureCanvasTkAgg(eqFig, root)
        canvasld = FigureCanvasTkAgg(eqFig, root)
        self.layout_button = tkinter.Frame(self.layout_cnb)
        self.layout_status.grid(column=0, row=0)
        self.layout_canvas.grid(column=0, row=1)
        self.layout_button.grid(column=0, row=2)

        self.label_status_gen = tkinter.Label(self.layout_status, textvariable=self.text_label_status_gen)
        self.label_status_fps = tkinter.Label(self.layout_status, textvariable=self.text_label_status_fps)
        self.label_status_gps = tkinter.Label(self.layout_status, textvariable=self.text_label_status_gps)
        self.label_status_barrier = tkinter.Label(self.layout_status, textvariable=self.text_label_status_barrier)
        self.label_status_gen.grid(column=0, row=0)
        self.label_status_fps.grid(column=1, row=0)
        self.label_status_gps.grid(column=2, row=0)
        self.label_status_barrier.grid(column=3, row=0)

        #右侧 sliders and functions
        self.layout_snf = tkinter.Frame(self.layout_window)
        self.layout_snf.grid(column=1, row=0)
        
        try:
            self.photo = tkinter.PhotoImage(file=sys.path[0]+'\Title.png')
            self.frame_label_photo = tkinter.Label(self.layout_snf, image=self.photo)
            self.frame_label_photo.grid(column=0, row=0)
        except:
            traceback.print_exc()

        self.frame_fluid = tkinter.LabelFrame(self.layout_snf, text="流动参数", width=300, height=100, bd=1)
        self.frame_fluid.grid(column=0, row = 1)

        self.frame_barrier = tkinter.LabelFrame(self.layout_snf, width=300, height=100, text="障碍参数", bd=1)
        self.frame_barrier.grid(column=0, row = 2)

        self.frame_animation = tkinter.LabelFrame(self.layout_snf, width=300, height=100, text="动画参数", bd=1)
        self.frame_animation.grid(column=0, row = 3)

        #按钮
        self.button_pause = ttk.Button(self.layout_button, text='暂停', command=HelpPause)
        self.button_start = ttk.Button(self.layout_button, text='开始', command=HelpStart)
        self.button_next20gen = ttk.Button(self.layout_button, text='下一帧', command=lambda: thread_it(nextFrame, 20))
        self.button_reset = ttk.Button(self.layout_button, text='重置', command=self.Reset)
        self.button_import = ttk.Button(self.layout_button, text='打开', command=self.ChooseFile)
        self.button_export = ttk.Button(self.layout_button, text='保存', command=self.Export)
        self.button_next20gen.grid(column=0, row=0)
        self.button_start.grid(column=1, row=0)
        self.button_reset.grid(column=2, row=0)
        self.button_import.grid(column=3, row=0)
        self.button_export.grid(column=4, row=0)
        self.layout_button.grid(column=0, row=3)

        self.button_equation = ttk.Button(self.frame_barrier, text='高级障碍', command=lambda:thread_it(self.HelpEquationWindow))
        self.button_equation.grid(column=1, row=1)

        #标签
        self.label_u0 = tkinter.Label(self.frame_fluid, text="来流速度：")
        self.label_u0.grid(column=0, row=0)
        self.label_var_u0 = tkinter.Label(self.frame_fluid, textvariable=self.text_u0)
        self.label_var_u0.grid(column=2, row=0)
        self.label_viscosity = tkinter.Label(self.frame_fluid, text="粘性系数：")
        self.label_viscosity.grid(column=0, row=1)
        self.label_var_viscosity = tkinter.Label(self.frame_fluid, textvariable=self.text_viscosity)
        self.label_var_viscosity.grid(column=2, row=1)
        self.label_barrier = tkinter.Label(self.frame_barrier, text="障碍预设：")
        self.label_barrier.grid(column=0, row=0)

        self.label_animation_type = tkinter.Label(self.frame_animation, text="动画类型：")
        self.label_animation_speed = tkinter.Label(self.frame_animation, text="动画速度：")
        self.label_animation_contrast = tkinter.Label(self.frame_animation, text="对比程度：")
        self.label_animation_type.grid(column=0, row=0)
        self.label_animation_speed.grid(column=0, row=1)
        self.label_animation_contrast.grid(column=0, row=2)

        self.label_show_animation_speed = tkinter.Label(self.frame_animation, textvariable=self.text_animation_speed)
        self.label_show_animation_speed.grid(column=2, row=1)

        self.label_show_animation_contrast = tkinter.Label(self.frame_animation, textvariable=self.text_animation_contrast)
        self.label_show_animation_contrast.grid(column=2, row=2)

        #滑动条
        self.slider_u0 = ttk.Scale(self.frame_fluid, from_=0, to=0.12, orient=tkinter.HORIZONTAL, command=help_u0, length=125)
        self.slider_u0.set(u0)
        self.slider_u0.grid(column=1, row=0)

        self.slider_viscosity = ttk.Scale(self.frame_fluid, from_=0.005, to=0.20, orient=tkinter.HORIZONTAL,
                                          command=help_viscosity, length=125)
        self.slider_viscosity.set(viscosity)
        self.slider_viscosity.grid(column=1, row=1)

        self.slider_animation_speed = ttk.Scale(self.frame_animation, from_=0, to=8, orient=tkinter.HORIZONTAL,
                                          command=self.Change_animation_speed)
        self.slider_animation_speed.set(1)
        self.slider_animation_speed.grid(column=1, row=1)

        self.slider_animation_contrast = ttk.Scale(self.frame_animation, from_=0, to=2, orient=tkinter.HORIZONTAL,
                                                command=self.Change_animation_contrast)
        self.slider_animation_contrast.set(1)
        self.slider_animation_contrast.grid(column=1, row=2)

        #下拉菜单
        self.combo_barrier = ttk.Combobox(self.frame_barrier, textvariable=self.text_barrier)
        self.combo_barrier['value'] = ('(默认)', '平板 短   垂直', '平板 短   水平', '平板 短   α=45°', '倒三角型（平角头）',
                                     '正三角型（钝角头）', '机翼 简单 α=0°', '机翼 简单 α=0° 襟翼展开', '正方形（16x16）',
                                     '小河1', '小河2', '多孔介质1', '多孔介质2', '射流')
        self.combo_barrier.current(0)
        self.combo_barrier.bind('<<ComboboxSelected>>', help_change_barrier)
        self.combo_barrier.grid(column=1,row=0)

        self.combo_animation_type = ttk.Combobox(self.frame_animation, textvariable=self.text_animation_type)
        self.combo_animation_type['value'] = ('旋度动画', '密度动画','流线', '速度矢量', '水平速度', '垂直速度')
        self.combo_animation_type.current(0)
        self.combo_animation_type.bind('<<ComboboxSelected>>', help_change_animation)
        self.combo_animation_type.grid(column=1, row=0, columnspan=2)

        #勾选框
        self.check_changeable_barrier = ttk.Checkbutton(self.frame_barrier, text="可变障碍", variable=self.bool_changeable_barrier, onvalue=True, offvalue=False)
        self.check_changeable_barrier.grid(column=1, row=2)
    
    able_lattice = True
    def ChangeLattice(self, height, width, *arg):
        global nheight, nwidth, animating
        if self.able_lattice:
            if (50<= int(height) <= 999) and (50 <= int(width) <= 999):
                self.able_lattice = False
                nheight = height
                nwidth = width
                self.Reset()
                self.able_lattice = True
            else:
                tkinter.messagebox.askretrycancel("请输入符合要求的数值", "输入范围限制在[50,999]，仅数字")
                self.lattice_window.attributes("-topmost",1)

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
            self.able_edge = True

    def Draw(self):
        canvas.draw()

    def HideStart(self):
        self.button_start.grid_forget()
        self.button_pause.grid(column=1, row=0)

    def ShowStart(self):
        self.button_pause.grid_forget()
        self.button_start.grid(column=1, row=0)

    def Record(self):
        pass

    def Export(self):
        a = False
        if start_start:
            HelpPause()
            a = True
        try:
            self.filename = tkinter.filedialog.asksaveasfile(title="保存", defaultextension=".LBM", filetypes=[("格子-玻尔兹曼 工程文件",".LBM")]).name
        except:
            traceback.print_exc()
        try:
            if filename == '':
                savez(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())), height=height, width=width, n=n ,barrier=barrier, gen=gen,edge=edge, ux=ux,uy=uy,rho=rho)
            else:
                savez(self.filename, height=height, width=width, n=n ,barrier=barrier, gen=gen,edge=edge, ux=ux,uy=uy,rho=rho)
            os.remove(self.filename)
            os.rename(self.filename+'.npz', self.filename)
            if a:
                HelpStart()
        except:
            if a:
                HelpStart()
            traceback.print_exc()

    def ChooseFile(self):
        try:
            fileName_choose = tkinter.filedialog.askopenfilename(title="导入",filetypes=[("格子-玻尔兹曼 工程文件",".LBM")])
            thread_it(file_import,fileName_choose)
        except:
            traceback.print_exc()

    def SavePhoto(self):
        self.filename = tkinter.filedialog.asksaveasfile(title="保存到图片", defaultextension=".png", filetypes=[("图片文件",".PNG")]).name
        try:
            wt = 0
            while True:
                if not save_lock:
                    break
                time.sleep(0.01)
                wt += 25
                if wt == 25:
                    print("RuntimeError: Too long for waiting.")
                    break
            os.remove(self.filename)
            if self.filename == "":
                theFig.savefig(sys.path[0]+'/'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.png')
            else:
                theFig.savefig(self.filename)
        except:
            traceback.print_exc()

    
    def SavePhotoStep2(self, fn):
        try:
            wt = 0
            while True:
                if not save_lock:
                    break
                time.sleep(0.01)
                wt += 25
                if wt == 25:
                    print("RuntimeError: Too long for waiting.")
                    break
            if fn == "":
                print(str(os.getcwd())+'/'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.png')
                theFig.savefig(sys.path[0]+'\Screenshots'+'\\'+time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+'.png')
            else:
                traceback.print_exc()
        except:
            traceback.print_exc()


    def Change_animation_speed(self, var):
        global spd
        spd = float('%.2f' % float(var))
        self.text_animation_speed.set(str('%.2f' % (float(var))))

    def Change_animation_contrast(self, var):
        global contrast
        contrast = float('%.2f' % float(var))
        self.text_animation_contrast.set(str('%.2f' % float(var)))

    def HelpEquationWindow(self):
        a = False
        if start_start:
            a = True
        HelpPause()
        wt = 0
        while True:
            if not animating:
                self.EquationWindow()
                if a:
                    HelpStart()
                break
            time.sleep(0.03)
            wt += 1
            if wt == 25:
                print("RuntimeError: Too long for waiting.")
                break

    def EquationWindow(self):
        global canvaseq, ProgressbarEq, nnbarrier, xp, yp
        if not self.eqwinlock:
            self.eqwinlock = True
            nnbarrier = barrier
            
            xp = []
            yp = []
            for i in range(height):
                for j in range(width):
                    if nnbarrier[i, j]:
                        xp.append(j - width / 2)
                        yp.append(i - height / 2)

            self.Equation_window = tkinter.Toplevel(root)
            self.Equation_window.resizable(width=False, height=False)
            self.Equation_window.protocol("WM_DELETE_WINDOW", self.eqcloseEvent)
            
            self.equation_window.last_x = 0
            self.equation_window.last_y = 0

            self.text_dx = tkinter.StringVar()
            self.text_dy = tkinter.StringVar()
            self.text_dx.set(str(0))
            self.text_dy.set(str(0))

            self.frame_eq_t = tkinter.Frame(self.Equation_window)
            self.frame_eq_t.grid(column=0, row = 2, columnspan=2)

            Labal_x = tkinter.Label(self.Equation_window, text="x(t) =")
            Labal_x.grid(row=0, column=0)

            Labal_y = tkinter.Label(self.Equation_window, text="y(t) =")
            Labal_y.grid(row=1, column=0)

            Labal_t = tkinter.Label(self.frame_eq_t ,text="t的起始值:")
            Labal_t.grid(row=0, column=0)
            Labal_te = tkinter.Label(self.frame_eq_t, text="t的终止值:")
            Labal_te.grid(row=0, column=2)

            Labal_ex = tkinter.Label(self.frame_eq_t, text="计算精度：")
            Labal_ex.grid(row=0, column=4)

            in_xt = tkinter.StringVar()
            in_xt.set('10*sin(t);')  # 预输入的值
            Entry_x = tkinter.Entry(self.Equation_window, width=65, textvariable=in_xt)
            Entry_x.grid(row=0, column=1)

            in_yt = tkinter.StringVar()
            in_yt.set('10*cos(t);')
            Entry_y = tkinter.Entry(self.Equation_window, width=65, textvariable=in_yt)
            Entry_y.grid(row=1, column=1)

            in_t = tkinter.StringVar()
            in_t.set('-200')
            Entry_t = tkinter.Entry(self.frame_eq_t, width=10, textvariable=in_t)
            Entry_t.grid(row=0, column=1)
            in_te = tkinter.StringVar()
            in_te.set('200')
            Entry_te = tkinter.Entry(self.frame_eq_t, width=10, textvariable=in_te)
            Entry_te.grid(row=0, column=3)

            in_ex = tkinter.StringVar()  # 计算精度
            in_ex.set('2')
            Entry_ex = tkinter.Entry(self.frame_eq_t, width=10, textvariable=in_ex)
            Entry_ex.grid(row=0, column=5)

            
            canvaseq = FigureCanvasTkAgg(eqFig, self.Equation_window)
            canvaseq.get_tk_widget().grid(row=3, column=0, columnspan=2)

            EqButton_Confirm = ttk.Button(self.Equation_window, text='确定',
                                            command=lambda: thread_it(Equation, Entry_x.get(), Entry_y.get(),
                                                                        Entry_t.get(),
                                                                        Entry_te.get(), Entry_ex.get()))
            EqButton_Confirm.grid(row=0, column=3)

            Default_Confirm = ttk.Button(self.frame_eq_t, text='默认参数',
                                            command=lambda: thread_it(Equation, Entry_x.get(), Entry_y.get(),
                                                                        Entry_t.get(),
                                                                        Entry_te.get(), Entry_ex.get()))
            Default_Confirm.grid(row=0, column=7)

            ProgressbarEq = ttk.Progressbar(self.Equation_window, length=80, maximum=100)
            ProgressbarEq.grid(row=1, column=3)

            self.slider_eq_x = ttk.Scale(self.Equation_window, from_=-int(width/2), to=int(width/2), orient=tkinter.HORIZONTAL,
                                            command=self.equation_window.Change_x, length=500)
            self.slider_eq_x.set(0)
            self.slider_eq_x.grid(column=1, row=5, columnspan=2)

            self.slider_eq_y = ttk.Scale(self.Equation_window, from_=-int(height/2), to=int(height/2), orient=tkinter.VERTICAL,
                                            command=self.equation_window.Change_y, length=300)
            self.slider_eq_y.set(0)
            self.slider_eq_y.grid(column=3, row=3)

            self.label_dx = tkinter.Label(self.Equation_window, textvariable=self.text_dx)
            self.label_dx.grid(column=0, row=5)

            self.label_dy = tkinter.Label(self.Equation_window, textvariable=self.text_dy)
            self.label_dy.grid(column=3, row=2)

            self.eq_frame_tool = tkinter.Frame(self.Equation_window)
            self.eq_frame_tool.grid(column=0, row=6, columnspan=3)

            self.eq_check_autoupdate = ttk.Checkbutton(self.eq_frame_tool, text="自动更新", variable=self.bool_auto_update, onvalue=True, offvalue=False, command=self.equation_window.AutoConfirm)
            self.eq_check_autoupdate.grid(row=0, column=0)

            self.eq_button_pen = ttk.Button(self.eq_frame_tool, text='鼠标：绘制',
                                            command=self.equation_window.PenEraser)
            self.eq_button_pen.grid(row=0, column=1)

            self.eq_button_eraser = ttk.Button(self.eq_frame_tool, text='鼠标：擦除',
                                            command=self.equation_window.PenEraser)

            self.eq_button_clear = ttk.Button(self.eq_frame_tool, text='清除障碍',
                                            command=lambda:thread_it(main_window.equation_window.ClearBarrier))
            self.eq_button_clear.grid(row=0, column=2)

            self.eq_button_update = ttk.Button(self.eq_frame_tool, text='更新障碍',
                                            command=freshbarrier)
            self.eq_button_update.grid(row=0, column=3)

    def LiftDragWindow(self):
        global canvasld, show_lift_drag
        show_lift_drag = True
        self.ld_window = tkinter.Toplevel(root)
        self.ld_window.resizable(width=False, height=False)
        self.ld_window.protocol("WM_DELETE_WINDOW", self.ld_Window.closeEvent)

        self.ld_button_fresh = ttk.Button(self.ld_window, text="清除曲线", command=self.ld_Window.Clear)
        self.ld_button_fresh.grid(column=4, row=1)

        self.ld_check_auto = ttk.Checkbutton(self.ld_window, text="自动刷新曲线", variable=self.bool_ld_auto_update\
                                            , onvalue=True, offvalue=False, command=self.ld_Window.Switch)
        self.ld_check_auto.grid(column=3, row=1)

        canvasld = FigureCanvasTkAgg(ldFig, self.ld_window)
        canvasld.get_tk_widget().grid(column=0, row=0, columnspan=4)

    def LatticeWindow(self):
        self.lattice_window = tkinter.Toplevel(root)
        self.lattice_window.resizable(width=False, height=False)

        self.lattice_label_height = tkinter.Label(self.lattice_window, text="格子高度：")
        self.lattice_label_height.grid(column=0, row=0)
        self.lattice_label_width = tkinter.Label(self.lattice_window, text="格子宽度：")
        self.lattice_label_width.grid(column=0, row=1)

        self.str_lattice_height = tkinter.StringVar()
        self.lattice_line_height = tkinter.Entry(self.lattice_window, textvariable=self.str_lattice_height)
        self.lattice_line_height.grid(column=1, row=0)
        
        self.str_lattice_width = tkinter.StringVar()
        self.lattice_line_width = tkinter.Entry(self.lattice_window, textvariable=self.str_lattice_width)
        self.lattice_line_width.grid(column=1, row=1)

        self.lattice_button_cancel = ttk.Button(self.lattice_window, text="取消", command=self.Destroy_lattice)
        self.lattice_button_cancel.grid(column=0, row=2)

        self.lattice_button_confirm = ttk.Button(self.lattice_window, text="确定", command=self.LatticeConfirm)
        self.lattice_button_confirm.grid(column=1, row=2)

    def Destroy_lattice(self):
        self.lattice_window.destroy()

    def LatticeConfirm(self):
        try:
            self.ChangeLattice(int(self.str_lattice_height.get()), int(self.str_lattice_width.get()))
        except ValueError:
            tkinter.messagebox.askretrycancel("请输入符合要求的数值", "输入范围限制在[50,999]，仅数字")
            self.lattice_window.attributes("-topmost",1)

    def Destroy_ld(self):
        self.ld_window.destroy()
    
    def eqcloseEvent(self):
        self.eqwinlock = False
        self.Equation_window.destroy()

    def Draw_eq(self):
        canvaseq.draw()

    def Reset(self):
        global start_start, animating
        HelpPause()
        wt = 0
        while True:
            if not animating:
                break
            print("WAITING")
            time.sleep(0.03)
            wt += 1
            if wt == 25:
                print("RuntimeError: Too long for waiting.")
                break
        global change_barrier_switch, nbarrier, barrier_zone, barrier3, barrier7, barrier1, barrier5, barrier2, barrier4, barrier8, barrier6, barrier, blood
        global n, changing, x, y, x1, y1, ux1, uy1, n
        global change_v, change_viscosity, gen, drag, lift, dforce, tank, ncurl, omega, performanceData, u1, nviscosity, nnbarrier, first_write
        global bindable, alert, first_st_var, change_animation_switch, write_switch, animation_type, contrast, ux, uy, killThreadAnimation
        global theFig, eqFig, ldFig, bImageArray, eqbImageArray, barrierImage, eqbarrierImage, l1, l2, fluidImage, blood, height, width, ax
        eqFig.clf()
        ldFig.clf()
        blood = ones((nheight, nwidth))
        alert = False
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
        y, x = mgrid[0:height:1, 0:width:1]
        y1, x1 = mgrid[0:height:4, 0:width:4]
        ux1 = zeros((int(height/4), int(width/4)))
        uy1 = zeros((int(height/4), int(width/4)))
        if x1.shape[0] != ux1.shape[0]:
            if x1.shape[0] > ux1.shape[0]:
                x1 = delete(x1, int(x1.shape[0]-1), axis=0)
            elif x1.shape[0] < ux1.shape[0]:
                ux1 = delete(ux1, int(ux1.shape[0]-1), axis=0)
        if y1.shape[0] != uy1.shape[0]:
                if y1.shape[0] > uy1.shape[0]:
                    y1 = delete(y1, int(y1.shape[0]-1), axis=0)
                elif y1.shape[0] < uy1.shape[0]:
                    uy1 = delete(uy1, int(uy1.shape[0]-1), axis=0)
        if x1.shape[1] != ux1.shape[1]:
            if x1.shape[1] > ux1.shape[1]:
                x1 = delete(x1, int(x1.shape[1]-1), axis=1)
            elif x1.shape[1] < ux1.shape[1]:
                ux1 = delete(ux1, int(ux1.shape[1]-1), axis=1)
        if y1.shape[1] != uy1.shape[1]:
                if y1.shape[1] > uy1.shape[1]:
                    y1 = delete(y1, int(y1.shape[1]-1), axis=1)
                elif y1.shape[1] < uy1.shape[1]:
                    uy1 = delete(uy1, int(uy1.shape[0]-1), axis=1)
        

        # 初始化
        #del n[0],n[3],n[7],n[1],n[5],n[2],n[6],n[4],n[6]
        n0 = four9th * (ones((height, width)) - 1.5 * u0 ** 2)
        n3 = one9th * (ones((height, width)) - 1.5 * u0 ** 2)
        n7 = one9th * (ones((height, width)) - 1.5 * u0 ** 2)
        n1 = one9th * (ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n5 = one9th * (ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n2 = one36th * (ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n8 = one36th * (ones((height, width)) + 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n4 = one36th * (ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n6 = one36th * (ones((height, width)) - 3 * u0 + 4.5 * u0 ** 2 - 1.5 * u0 ** 2)
        n = [n0, n1, n2, n3, n4, n5, n6, n7, n8]
        rho = n[0] + n[3] + n[7] + n[1] + n[5] + n[2] + n[8] + n[4] + n[6]  # macroscopic density
        ux = (n[1] + n[2] + n[8] - n[5] - n[4] - n[6]) / rho  # macroscopic x velocity
        uy = (n[3] + n[2] + n[4] - n[7] - n[8] - n[6]) / rho  # macroscopic y velocity
        barrier = zeros((height, width), bool)  # True wherever there's a barrier
        animating = False
        for i in range(16):
            barrier[int((height / 2) + 8 - i), int(width / 2)] = True
        nbarrier = barrier
        nnbarrier = nbarrier

        barrier3 = roll(barrier, 1, axis=0) 
        barrier7 = roll(barrier, -1, axis=0)  
        barrier1 = roll(barrier, 1, axis=1)  
        barrier5 = roll(barrier, -1, axis=1)
        barrier2 = roll(barrier3, 1, axis=1)
        barrier4 = roll(barrier3, -1, axis=1)
        barrier8 = roll(barrier7, 1, axis=1)
        barrier6 = roll(barrier7, -1, axis=1)

        barrier_zone = zeros((height, width))
        eqFig = matplotlib.pyplot.figure(num=2, figsize=(5, 3))
        eqax = eqFig.add_subplot(111)
        eqax.xaxis.grid(True, which='major')
        eqax.yaxis.grid(True, which='major')
        eqbImageArray = zeros((height, width, 4), uint8)  # an RGBA image
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


        theFig = matplotlib.pyplot.figure(num=1, figsize=(5, 3))
        fluidImage = matplotlib.pyplot.imshow(curl(ux, uy), origin='lower', norm=matplotlib.pyplot.Normalize(-0.1, 0.1),
                                            cmap=matplotlib.pyplot.get_cmap('bwr'), interpolation='none')
        bImageArray = zeros((height, width, 4), uint8)  # an RGBA image
        bImageArray[barrier, 3] = 255  # set alpha=255 only at barrier sites
        barrierImage = matplotlib.pyplot.imshow(bImageArray, origin='lower', interpolation='none')

        change_barrier_switch = False
        first_write = True
        barrier_zone = zeros((height, width))
        
        self.slider_viscosity.set(0.02)
        self.slider_u0.set(0.1)
        self.slider_animation_speed.set(1)
        self.slider_animation_contrast.set(1)
        freshbarrier()
        change_animation(self.combo_animation_type.get())
        nextFrame(0)
        killThreadAnimation = False
        self.ld_Window.Clear()
        start_start = False
        self.ShowStart()
        canvas.draw()
        fresheq()
        print('RESETED')

    def fresh_status(self):
        try:
            self.text_label_status_gen.set("代数："+ str(gen) + " 代        ")
            self.text_label_status_fps.set("帧率：" + str(fps) + " 帧/秒        ")
            self.text_label_status_gps.set("代率：" + str(gps) + " 代/秒        ")
            if alert:
                try:
                    self.label_status_gps.setHidden(True)
                    self.label_status_gen.setHidden(True)
                    self.label_status_fps.setStyleSheet("color:red")
                    self.label_status_fps.setText('计算出现发散，请重置流动')
                except:
                    pass
        except:
            traceback.print_exc()
            pass
      
    def FreshDetail(self):
        try:
            if xdata != None:
                self.text_label_status_gen.set('x:'+str('%.1f' % xdata)+'  y:'+str('%.1f' % ydata))
                self.text_label_status_fps.set('ux:'+str('%.4f' % ux[int(ydata), int(xdata)])+'  uy:'+str('%.4f' % uy[int(ydata), int(xdata)]))
                self.text_label_status_gps.set('  密度:'+str('%.4f' % rho[int(ydata), int(xdata)]))
                self.text_label_status_barrier.set('障碍:'+str(barrier[int(ydata), int(xdata)]))
        except:
            traceback.print_exc()

    def Exit(self):
        global kill
        kill = True
        sys.exit()
    
    def Drawing(self):                     
        self.text_dx.set(0)
        self.text_dy.set(0)
    

class Equation_window():
    def __init__(self):
        super().__init__()
        self.last_x = 0
        self.last_y = 0
    
    def Draw(self):
        self.eqcanvas.draw()
    
    def Change_x(self, *arg):
        global nnbarrier
        lx = int(main_window.slider_eq_x.get())
        main_window.text_dx.set(str(lx))
        nnbarrier = roll(nnbarrier, int(lx- self.last_x), axis=1)
        self.last_x = lx
        fresheq()
        if update:
            freshbarrier()

    def Change_y(self, *arg):
        global nnbarrier
        ly = int(main_window.slider_eq_y.get())
        main_window.text_dy.set(str(ly))
        nnbarrier = roll(nnbarrier, int(self.last_y - ly), axis=0)
        self.last_y = ly
        fresheq()
        if update:
            freshbarrier()
    
    def Change_rot(self):
        global nnbarrier
        self.label_rot.setText(""+str(int(self.slider_rot.value()))+"°")
        roteq(self.slider_rot.value()/180 * sympy.pi)
        nnbarrier = roll(nnbarrier, int(self.slider_x.value()), axis=1)
        nnbarrier = roll(nnbarrier, int(self.slider_y.value()), axis=0)
        fresheq()
        
        if update:
            freshbarrier()

    def Change_Eq(self):
        self.slider_x.setValue(0)
        self.slider_y.setValue(0)
        self.slider_rot.setValue(0)
        Equation(self.line_xt.text(), self.line_yt.text(), int(self.line_tmin.text()), int(self.line_tmax.text()), int(self.line_exp.text()))

    def AutoConfirm(self):
        global update
        if main_window.bool_auto_update.get():
            update = True
        else:
            update = False
    
    def Unfold(self):
        self.button_unfold.setText("<<")
        self.button_unfold.clicked.connect(self.Fold)
        self.widget_unfold.setHidden(False)

    def Fold(self):
        self.button_unfold.setText(">>")
        self.button_unfold.clicked.connect(self.Unfold)
        self.widget_unfold.setHidden(True)

    def ClearBarrier(self):
        global xp, yp, nnbarrier, nbarrier
        xp=[]
        yp=[]
        nnbarrier = zeros((height,width),bool)
        fresheq()
        if update:
            freshbarrier()
    
    def PenEraser(self):
        global pen, eraser
        if pen:
            main_window.eq_button_pen.grid_forget()
            main_window.eq_button_eraser.grid(column=1, row=0)
            pen = False
            eraser = True
        else:
            main_window.eq_button_eraser.grid_forget()
            main_window.eq_button_pen.grid(column=1, row=0)
            eraser = False
            pen = True

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
        ProgressbarEq['value'] = 0


class Ld_window():
    def __init__(self):
        super().__init__()
        pass

    def Draw(self):
        ax.set_xlabel(u'代数')
        ax.set_ylabel(u'力')
        ax.set_title(u'力-代数 曲线')
        l1, = ax.plot(list_gen, list_lift, 'b', label=u'升力')
        l2, = ax.plot(list_gen, list_drag, 'r', label=u'阻力')
        canvasld.draw()
    
    def Switch(self):
        global show_lift_drag
        if main_window.bool_ld_auto_update.get():
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
    
    def closeEvent(event):
        global show_lift_drag
        show_lift_drag = False
        main_window.Destroy_ld()


threadAnimation = threading.Thread(target=starter, name='T_Animation')  # 动画开始线程
threadAnimation.start()
root = tkinter.Tk()
main_window = Main_window(root)
main_window.Draw()
thread_it(fresh_status)
main_window.mainloop()
