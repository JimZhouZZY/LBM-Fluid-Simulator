# LBM Fluid Simulator <br> 格子-玻尔兹曼法流体力学数值模拟计算器
[ English | 中文 ]

**WARNING: The code style is really bad due to my lazy and lack of experience. I'm sorry about this**


This project was a project for a competition.<br>
It is **a fluid simulator using Lattice-Boltzmann Method with nice GUI** (two GUI versions, Tkinter and PyQt5). I started the project in September, 2021. And the result came that I won the first prize in March, 2023. There isn't any secret now, so I'm uploading to share my work. Though this project is mainly in Chinese, I hope this can help someone. <br>

## Tips:
1. **Please be sure to run the code in the code's root floder**. There is still some logic issues in the program (that I'm too lazy and busy to solve now), especially when doing file operations like screenshotting and saving project. It will possibly accidentally create some .PNG or .LBM files if you are not running the code in the code's root directory. So make sure you "cd" to the projects floder first then "py main.py".
2. **Make sure you haven't missed a file**. There may be issues while running without "Screenshots" floder, icon files, or .ttf file(in PyQt5 version)
3. **Tkinter Version is recommended**. It's more fully annotated.
4. Actually sympy is unnecessary in PyQt5 version. I remember I once replaced it with numpy, but I the code is in my school. Maybe I'll update when I'm back to school.

（under construction）

## Environments:
**Tkinter Version**: Python3 with matplotlib. <br>
**PyQt5 Version**: Python3 with matplotlib, sympy and PyQt5. <br>

## Theme of the Project:
Since the development of fluid mechanics, it has penetrated into all aspects of life.<br>
In the classroom, the knowledge of fluid mechanics is often involved. In many cases, schools and teachers do not have suitable tools to demonstrate, so they can only use formulas and simple lines on the blackboard to tell relevant knowledge, which makes it difficult for many students to understand and appreciate the hidden meaning of fluid mechanics. The beauty of abstraction.<br>
In learning, many beginners of numerical methods or fluid mechanics suffer from the fact that books are too abstract and too jumpy, and often they can only find boring core codes, and cannot find simple algorithm programs that are convenient for practice.<br>
This program is able to solve these problems.<br>
For classroom teaching, this program not only has a scientific and rigorous LBM algorithm, but also has an easy-to-use GUI and rich interactivity, which almost meets all the adjustment needs of Tan Shu, and can demonstrate the flow phenomenon scientifically, conveniently and quickly.<br>
For professional learning, the algorithm of this program adopts simple BGK simulation, which is rigorous and easy to understand. Rich interactive functions realize single calculation and multiple parameter adjustments, get rid of the boring parameter adjustment process, and speed up the understanding of the meaning of various parameters.<br>

## Rendings:
### Overview of the program interface
![窗口总览](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/962a31b1-3761-4836-8da5-809ad7d90045)
### Classic Example: Roof-driven Flow
![（经典算例）顶盖驱动流](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/663fa756-7c4f-4d79-b84c-fd88475e61e9)
### Classic Example: Jet Flow
![（经典算例）喷射流](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/a238dbd7-e710-4528-a883-48098bac4980)
### Classic Example: Simple Porous Media
![（经典算例）多孔介质2](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/dc0d6a07-e873-495f-9873-eb0c9d1c4fb9)
### Curl Animation
![旋度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/62a233f3-6c6d-4454-bde3-e6816390fe23)
### Density Animation
![密度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/2d846618-541e-4282-b9d0-bf1e2a2830a3)
### Vertical Speed Animation
![垂直速度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/6bfb4eee-9aa8-46a2-9f9c-66eba76b31c9)
### Horizontal Speed Animation
![水平速度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/bd790595-728c-41d0-b4c8-07927e70879c)
### Velocity Vector Animation
![速度矢量动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/6a5d5e56-ab97-45f2-96a7-199668a41b10)

## References:
https://physics.weber.edu/schroeder/fluids/

<p align="right"> Jim Zhou (ZZY) <br> 2023.7.28 </p>

# 格子-玻尔兹曼法流体力学数值模拟计算器

**屎山警告**

这个项目是为了参加比赛而编写的 <br>
它是**一个拥有漂亮易用的GUI（包括Tkinter和PyQt5两个版本）的，使用格子玻尔兹曼法的流体力学数值计算程序**。我从2021年11月开始这个项目，经过两年的努力，成功拿到了参与的比赛的一等奖第一名。现在这个项目已经不需要保密，因此我将它上传于此，希望能够为需要帮助的人尽一点绵薄之力。由于能力和水平有限，粗陋之处请多多包涵。

## 提示：
1. **请确保在代码所在的根目录下运行代码**。由于时间仓促和后来我的慵懒于忙碌，无暇再改一些程序中的低级逻辑错误。具体多是在文件操作上，有时因为目录不对、缺乏文件等，会报错/错误操作文件。因此请先"cd"到项目所在的目录，然后再"py main.py"打开
2. **请确保没有遗漏文件**。如果缺失“Screenshots”文件夹、图标文件或.ttf字体文件，程序可能报错。
3. **更加推荐Tkinter版本**。Tkinter版本的注释更加完善。
4. 事实上PyQt5版本中的sympy库是非必要的。我记得做过一个删去sympy用numpy代替的版本，但是源码在学校忘记拷回来了。等我有空回学校再上传吧。

（施工中）

## 运行环境:
**Tkinter版本**: 带有 matplotlib 库的 Python3。 <br>
**PyQt5版本**: 带有 matplotlib、sympy 和 PyQt5 库的 Python3。 <br>

## 作品主题：
流体力学发展至今，已经深入到了生活的方方面面。 <br>
在课堂中，也时常涉及到流体力学的知识。而很多时候，学校、老师没有合适的工具去演示，只能生硬地在黑板上用公式和简单的线条来讲述相关知识，这让许多同学很难理解，也很难体会到蕴藏在流体力学的抽象中的美妙。 <br>
在学习中，不少数值方法或是流体力学的初学者苦于书本太抽象太跳跃，并且往往只能找到枯燥的核心代码，找不到方便实践的简单算法程序。 <br>
本程序正能解决这些问题。 <br>
对于课堂教学，本程序既有科学严谨的LBM算法，又有简单易用的GUI以及丰富的交互性，几乎满足所有谭舒调整的需要，能够科学而方便快捷地演示流动现象。 <br>
对于专业学习，本程序的算法采用简单的BGK模拟，严谨中不失简单易懂。丰富的交互功能实现单次计算，多次调参，摆脱枯燥的调参过程，加快对各种参数意义的理解。 <br>

## 效果图

### 窗口总览
![窗口总览](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/962a31b1-3761-4836-8da5-809ad7d90045)
### 经典算例：顶盖驱动流
![（经典算例）顶盖驱动流](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/663fa756-7c4f-4d79-b84c-fd88475e61e9)
### 经典算例：喷射流
![（经典算例）喷射流](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/a238dbd7-e710-4528-a883-48098bac4980)
### 经典算例：简单的多孔介质
![（经典算例）多孔介质2](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/dc0d6a07-e873-495f-9873-eb0c9d1c4fb9)
### 旋度动画
![旋度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/62a233f3-6c6d-4454-bde3-e6816390fe23)
### 密度动画
![密度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/2d846618-541e-4282-b9d0-bf1e2a2830a3)
### 垂直速度动画
![垂直速度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/6bfb4eee-9aa8-46a2-9f9c-66eba76b31c9)
### 水平速度动画
![水平速度动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/bd790595-728c-41d0-b4c8-07927e70879c)
### 速度矢量动画
![速度矢量动画](https://github.com/JimZhouZZY/LBM-Fluid-Simulator/assets/140597003/6a5d5e56-ab97-45f2-96a7-199668a41b10)

## 参考资源
https://physics.weber.edu/schroeder/fluids/

<p align="right"> 周支宇 (ZZY) <br> 2023.7.28 </p>
