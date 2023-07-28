# LBM Fluid Simulator
This project was a project for a competition.<br>
It is **a fluid simulator using Lattice-Boltzmann Method with nice GUI** (two GUI versions, Tkinter and PyQt5). I started the project in September, 2021. And the result came that I won the first prize in March, 2023. There isn't any secret now, so I'm uploading to share my work. Though this project is mainly in Chinese, I hope this can help someone. <br>

## Tips:
1. **Please be sure to run the program in the program's root floder**. There is still some logic issues in the program (that I'm too lazy and busy to solve now), especially when doing file operations like screenshotting and saving project. It will possibly accidentally create some .PNG or .LBM files if you are not running the code in the code's root directory, and there may be issues while running without "Screenshots" floder, icon files, and .ttf file(if PyQt5 version). So make sure you "cd" to the projects floder first then "py main.py".

（under construction）

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

