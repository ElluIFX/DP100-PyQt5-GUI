# 基于PyQt5的正点原子DP100数控电源上位机

A PyQt5-based PC GUI for Aliantek DP100 digital power supply

Check [ketukil's fork](https://github.com/ketukil/Alientek-DP100-PyQT5-english-gui) if you need an English GUI.

> [!IMPORTANT]
> 本项目停止更新，新功能将使用Pyside6重新开发，以匹配我其他上位机的最新代码，同时支持多语言
>
> This project has been achieved, and new features will be redeveloped using PySide6 to match the latest code of my other upper-level machines, with support for multiple languages.
>
> 😊👉 https://github.com/ElluIFX/DP100-PySide6-GUI

## 功能

- 基本参数设定、预设组管理、设置修改
- 高达100Hz（可调）的数据采集、绘图、分析、保存
- PID恒功率控制
- 参数扫描（电压/电流）
- 函数发生器（正弦/方波/三角波/锯齿波/随机波）
- 操作序列（顺序执行操作）
- Material Design 风格

## Features

- Basic parameter setting, preset group management, setting modification
- Data acquisition, plotting, analysis and saving up to 100Hz (adjustable)
- PID constant power control
- Parameter scanning (voltage/current)
- Function generator (sine/square/triangle/sawtooth/random)
- Operation sequence (execute operations in sequence)
- Material Design style

## 依赖

使用了修改后的`QFramelessWindow`包，在`lib`文件夹中

release提供了打包好的exe文件，无需安装python环境

> 界面字体用了更纱黑体且没做fallback，记得去[微软商店](https://www.microsoft.com/store/productId/9MW0M424NCZ7?ocid=pdpshare)装一个

## Dependencies

A modified `QFramelessWindow` package is used in the `lib` folder

The release provides a packaged exe file, no need to install the python environment

> The interface font uses Sarasa UI and no fallback. Remember to install one in the [Microsoft Store](https://www.microsoft.com/store/productId/9MW0M424NCZ7?ocid=pdpshare)

## 关于二进制文件大小

Pyinstaller打包Qt程序时会自动添加不必要的Qt Plugins，导致二进制文件过大，认真修改spec文件排除不需要的dll和库可以减小到差不多30MB，但是我懒得改了，就这样

## About the size of the binary file

When Pyinstaller packages Qt programs, it will automatically add unnecessary Qt Plugins, which will cause the binary file to be too large. Carefully modify the spec file to exclude unnecessary dll and libraries, which can be reduced to about 30MB, but I am too lazy to change it, so it is

## Other

写着方便自己用的，没时间接受pr，有需要请自行fork

Written for my own use, no time to accept pr, please fork it yourself if you need it

## Something interesting about OPP

DP100的过功率限制实际上只做了硬件UI的限制,通过API可以设置得比限制的105W更高,具体用法可以查看[DP100API.py](./DP100API.py)最下方的example,经过测试150W可以正常工作

The upper limit of over-power protection actually is performed only in the hardware UI, and can be bypassed by API, which can be set to higher than the limit of 105W. For details, see the example at the bottom of [DP100API.py](./DP100API.py).
After testing, DP100 can work well at 150W.

## Screenshots

![1701177770319](image/readme/1701177770319.png)
