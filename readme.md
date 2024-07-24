# Miniware MDP-P906 数控电源上位机

不需要MDP-M01显控模块即可对电源进行远程控制，理论上同时支持P905(未测试)

> 感谢Miniware在百忙之中花费一年时间开发了一个必须使用显控模块才能控制的上位机，且功能如此简陋，他明明可以一直拖着，但还是整了一个玩具来糊弄大家

**[English Version](./readme_EN.md)**

## 鸣谢

本项目中使用到的协议部分来源于[leommxj/mdp_commander](https://github.com/leommxj/mdp_commander)，如果没有这个项目我没有任何办法测试出M01和P906的通信协议.

在该项目的基础上花费大量时间优化通信质量，最终实现高达100fps的稳定且长时间数据获取.

## 功能

- 支持输出/电压/电流设置
- 读取设备状态
- 实时读取输出的ADC测量值

## 使用方法

### 前提

本项目需要一个[淘宝](https://item.taobao.com/item.htm?spm=a1z09.2.0.0.521d2e8dccjOe1)上售价为30元的USB转NRF24L01模块，如下图

![1721840271138](image/readme/1721840271138.png)

这个模块具有独立的PA功放，因此，相比于leommxj使用的Arduino RF，它能实现高达两米的通信距离，但是，该模块使用了自己的协议来实现无线串口，这与控制设备所需要的原始NRF24L01数据流并不兼容

有意思的是，模块使用了一块正版的STM32F030F4P6作为主控，我们可以编写自己的程序覆写进去，实现对它硬件的废物利用

### 改造方法1

将模块的外壳撬开，翻到背面，可以看到如图的五个测试点

![1721840680045](image/readme/1721840680045.png)

下载[STM32 CubeProgrammer](https://www.st.com/en/development-tools/stm32cubeprog.html)并打开，如图设置

![1721840819305](image/readme/1721840819305.png)

现在，用一根镊子短接上图中的`BOOT0`和`3V3`两个测试点，**且在整个烧录过程中必须保持短接**

将模块插入电脑，选择正确的端口号后点击`Connect`进行连接，一切正常的话，应该如图所示，成功解除芯片上的读写保护

![1721841074236](image/readme/1721841074236.png)

接下来切换到下载页，选择我发布在release中的固件包（当然，你也可以自行编译），完成固件烧录

![1721841174409](image/readme/1721841174409.png)

### 改造方法2

和方法1没有本质区别，只是当通过BOOT0进入串口bootloader后不一定能解除读写保护，在这种情况下，如果你有ST-LINK，可以按如图所示的SWD接线进行连接，然后按下图勾选即可解除保护

![1721841339876](image/readme/1721841339876.png)

### 控制

自行查看代码，注释写好了

[test_main.py](./test_main.py) 测试读取示例

[mdp_p906.py](.mdp_controller/mdp_p906.py) 完整API实现

## TODO

移植我的[DP100-PyQt5-GUI](https://github.com/ElluIFX/DP100-PyQt5-GUI)项目到这里，实现一个完整的上位机

## 参考

[leommxj/mdp_commander](https://github.com/leommxj/mdp_commander) 中的协议实现

[mokhwasomssi/stm32_hal_nrf24l01p](https://github.com/mokhwasomssi/stm32_hal_nrf24l01p) 中的NRF24L01P驱动实现
