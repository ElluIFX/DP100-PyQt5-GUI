import os
import sys
from platform import architecture
from typing import Any

if architecture()[0] != "32bit":
    # Call venv to run this script

    path = os.path.dirname(__file__)
    venv_py_path = os.path.join(path, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_py_path):
        os.system(f"{venv_py_path} {sys.argv[0]}")
        sys.exit(0)
    else:
        raise RuntimeError("venv not found")

import warnings

warnings.filterwarnings("ignore")
"""ignore matplotlib warning"""
import cmd
import difflib
import math
import time
from threading import Lock, Thread

import matplotlib.animation as animation
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, TextBox
from simple_pid import PID

from DP100API import DP100

api = DP100()


class TColor:
    # color for terminal
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    PURPLE = "\033[1;35m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"

    RST = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERL = "\033[4m"
    BACKG = "\033[7m"

    HIDECURSOR = "\033[?25l"
    SHOWCURSOR = "\033[?25h"
    CLEARLINE = "\033[K"
    CLEARALL = "\033[2J"


def parse(arg):
    "Convert a series of zero or more numbers to an argument tuple"
    if not arg:
        return tuple()
    args = []
    for arg_ in arg.split():
        try:
            args.append(eval(arg_))
        except:
            args.append(arg_)
    return tuple(args)


def print_dict_as_table(title: str, content: dict, key_lenght: int = 10, value_lenght: int = 30) -> None:
    print("-" * (key_lenght + value_lenght + 5))
    print(f"|{TColor.YELLOW}{title:^{key_lenght + value_lenght + 3}}{TColor.RST}|")
    print("-" * (key_lenght + value_lenght + 5))
    for key, value in content.items():
        if isinstance(value, bool):
            value = str(value)
        print(
            f"|{TColor.BLUE}{key.capitalize():^{key_lenght}}{TColor.RST} | {TColor.CYAN}{value:^{value_lenght}}{TColor.RST}|"
        )
    print("-" * (key_lenght + value_lenght + 5))


class Data_Share:
    start_time = time.perf_counter()
    last_time = 0.0
    update_flag = False
    sweep_flag = False
    wave_flag = False
    save_datas_flag = False
    init_data_flag = False
    pid_flag = False
    pid_setpoint = 0
    voltage = 0
    current = 0
    power = 0
    energy = 0
    sync_lock = Lock()
    voltages = np.ones(400, np.float64)
    currents = np.ones(400, np.float64)
    times = np.ones(400, np.float64)


class Plotter:
    def __init__(self, data: Data_Share) -> None:
        self.data = data
        self.dataname = {
            "v": "Voltage (V)",
            "i": "Current (A)",
            "p": "Power (W)",
            "r": "Resistance (Ω)",
        }
        self.keep = False
        self.ax1_data = "v"
        self.ax2_data = "i"
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, num="DP100输出监控", figsize=(10, 6))
        self.ax2.grid()
        self.ax1.grid()
        self.non_block_inited = False
        (self.line1,) = self.ax1.plot([], [], "b-", animated=True)
        (self.line2,) = self.ax2.plot([], [], "r-", animated=True)
        self.ax2.set_xlabel("Time (s)")
        self.ax1.set_ylabel(self.dataname[self.ax1_data])
        self.ax2.set_ylabel(self.dataname[self.ax2_data])
        self._init_widget()

    def _init_widget(self):
        self.button_on = Button(
            plt.axes([0.05, 0.92, 0.08, 0.04]),
            "ON",
            color="lightgreen",
            hovercolor="white",
        )
        self.button_on.on_clicked(self._on)
        self.button_off = Button(
            plt.axes([0.15, 0.92, 0.08, 0.04]),
            "OFF",
            color="lightcoral",
            hovercolor="white",
        )
        self.button_off.on_clicked(self._off)
        self.button_rst = Button(
            plt.axes([0.25, 0.92, 0.08, 0.04]),
            "RESET",
            color="bisque",
            hovercolor="white",
        )
        self.button_rst.on_clicked(self._reset_data)
        self.button_hs = Button(
            plt.axes([0.35, 0.92, 0.08, 0.04]),
            "KEEP",
            color="skyblue",
            hovercolor="white",
        )
        self.button_hs.on_clicked(self._keep)
        self.button_v1 = Button(plt.axes([0.92, 0.8, 0.04, 0.04]), "V", color="white", hovercolor="grey")
        self.button_v1.on_clicked(lambda event: self._set_data(1, "v"))
        self.button_i1 = Button(plt.axes([0.92, 0.75, 0.04, 0.04]), "I", color="white", hovercolor="grey")
        self.button_i1.on_clicked(lambda event: self._set_data(1, "i"))
        self.button_p1 = Button(plt.axes([0.92, 0.7, 0.04, 0.04]), "P", color="white", hovercolor="grey")
        self.button_p1.on_clicked(lambda event: self._set_data(1, "p"))
        self.button_r1 = Button(plt.axes([0.92, 0.65, 0.04, 0.04]), "R", color="white", hovercolor="grey")
        self.button_r1.on_clicked(lambda event: self._set_data(1, "r"))
        self.button_v2 = Button(plt.axes([0.92, 0.38, 0.04, 0.04]), "V", color="white", hovercolor="grey")
        self.button_v2.on_clicked(lambda event: self._set_data(2, "v"))
        self.button_i2 = Button(plt.axes([0.92, 0.33, 0.04, 0.04]), "I", color="white", hovercolor="grey")
        self.button_i2.on_clicked(lambda event: self._set_data(2, "i"))
        self.button_p2 = Button(plt.axes([0.92, 0.28, 0.04, 0.04]), "P", color="white", hovercolor="grey")
        self.button_p2.on_clicked(lambda event: self._set_data(2, "p"))
        self.button_r2 = Button(plt.axes([0.92, 0.23, 0.04, 0.04]), "R", color="white", hovercolor="grey")
        self.button_r2.on_clicked(lambda event: self._set_data(2, "r"))
        self.text_vs = TextBox(
            plt.axes([0.51, 0.92, 0.1, 0.04]),
            "V-set ",
            initial=str(api.get_state()["v_set"]) if not self.data.pid_flag else "P-CTRL",
        )
        self.text_vs.on_submit(self._vset)
        self.text_is = TextBox(
            plt.axes([0.69, 0.92, 0.1, 0.04]),
            "I-set ",
            initial=str(api.get_state()["i_set"]),
        )
        self.text_is.on_submit(self._iset)
        self.text_ps = TextBox(
            plt.axes([0.87, 0.92, 0.1, 0.04]),
            "P-set ",
            initial=str(self.data.pid_setpoint) if self.data.pid_flag else "OFF",
        )
        self.text_ps.on_submit(self._pidset)
        if self.data.pid_flag:
            self.text_vs.set_active(False)
        else:
            self.text_ps.set_active(False)
        if self.data.wave_flag:
            self.text_vs.set_active(False)
            self.text_vs.set_val("G_WAVE")

    def _set_data(self, axnum, dataname):
        if axnum == 1:
            self.ax1_data = dataname
            self.ax1.set_ylabel(self.dataname[dataname])
        elif axnum == 2:
            self.ax2_data = dataname
            self.ax2.set_ylabel(self.dataname[dataname])

    def _reset_data(self, event):
        with self.data.sync_lock:
            self.data.voltages = np.ones_like(self.data.voltages)
            self.data.currents = np.ones_like(self.data.currents)
            self.data.times = np.ones_like(self.data.times)
            self.data.init_data_flag = True
            self.data.start_time = time.perf_counter()
            self.data.energy = 0
            self.data.last_time = 0

    def _keep(self, event):
        self.keep = not self.keep

    def _vset(self, expression):
        try:
            get = float(expression)
            api.set_output(v_set=get)
        except:
            pass

    def _iset(self, expression):
        try:
            get = float(expression)
            api.set_output(i_set=get)
        except:
            pass

    def _pidset(self, expression):
        try:
            get = float(expression)
            self.data.pid_setpoint = get
        except:
            pass

    def _on(self, event):
        api.set_output(True)

    def _off(self, event):
        api.set_output(False)

    def plot_init(self):
        return self.line1, self.line2

    def plot_update(self, i):
        if not self.keep:
            t = self.data.times
            c = self.data.currents
            v = self.data.voltages
            datas = {"v": v, "i": c}
            if "r" in (self.ax1_data, self.ax2_data):
                r = np.divide(v, c, out=np.ones_like(v) * -1, where=c != 0)
                datas["r"] = r
            if "p" in (self.ax1_data, self.ax2_data):
                p = np.multiply(v, c)
                datas["p"] = p
            self.line1.set_xdata(t)
            self.line2.set_xdata(t)
            self.line1.set_ydata(datas[self.ax1_data])
            self.line2.set_ydata(datas[self.ax2_data])
            self.ax2.autoscale_view()
            self.ax1.autoscale_view()
            ax1_max = np.max(datas[self.ax1_data])
            ax1_min = np.min(datas[self.ax1_data])
            ax1_add = max(0.05, (ax1_max - ax1_min) * 0.1)
            ax2_max = np.max(datas[self.ax2_data])
            ax2_min = np.min(datas[self.ax2_data])
            ax2_add = max(0.05, (ax2_max - ax2_min) * 0.1)
            self.ax1.set_ylim(
                ax1_min - ax1_add,
                ax1_max + ax1_add,
            )
            self.ax2.set_ylim(
                ax2_min - ax2_add,
                ax2_max + ax2_add,
            )
            self.ax2.set_xlim(t[0], t[-1])
            self.ax1.set_xlim(t[0], t[-1])
        self.fig.canvas.draw()
        return (self.line1, self.line2)

    def show(self, fps: float = 30.0):
        ani = animation.FuncAnimation(
            self.fig,
            self.plot_update,
            init_func=self.plot_init,
            interval=int(1000 / fps),
            blit=True,
        )
        plt.show(block=True)

    def show_non_block(self, fps: float = 30.0):
        if not self.non_block_inited:
            ani = animation.FuncAnimation(
                self.fig,
                self.plot_update,
                init_func=self.plot_init,
                interval=int(1000 / fps),
                blit=True,
            )
            self.non_block_inited = True
        plt.pause(1 / fps)


def state_callback(data: Data_Share, voltage, current):
    v = voltage / 1000
    i = current / 1000
    p = v * i
    t1 = time.perf_counter()
    with data.sync_lock:
        t = t1 - data.start_time
        data.power = p
        data.energy += p * (t - data.last_time)
        data.last_time = t
        data.voltage = v
        data.current = i
        if data.save_datas_flag:
            if not data.init_data_flag:
                data.voltages = np.hstack((data.voltages[1:], v))
                data.currents = np.hstack((data.currents[1:], i))
                data.times = np.hstack((data.times[1:], t))
            else:
                data.voltages *= v
                data.currents *= i
                data.times *= t
                data.init_data_flag = False
    if current != 0:
        r = f"{voltage / current:.3f}"
    else:
        r = "Inf "
    print(
        f" > {TColor.ITALIC}{TColor.YELLOW}电压:{TColor.CYAN} {v:.3f}V {TColor.YELLOW}电流:{TColor.CYAN} {i:.3f}A {TColor.YELLOW}功率(平均):{TColor.CYAN} {data.power:.3f}W ({data.energy/t:.3f}W) {TColor.YELLOW}能量:{TColor.CYAN} {data.energy:.3f}J {TColor.YELLOW}负载阻抗:{TColor.CYAN} {r}Ω {TColor.YELLOW}记录时间:{TColor.CYAN} {t:.2f}s{TColor.RST}"
        + " " * 6,
        end="\r",
    )


def update_worker(api_: DP100, data: Data_Share, freq: int = 60):
    t0 = time.perf_counter()
    while data.update_flag:
        t1 = time.perf_counter()
        if t1 - t0 > 1 / freq:
            t0 = t1
            api_.get_output_info()
        else:
            time.sleep(0.001)


class DP100_Cmd_Settings(cmd.Cmd):
    intro: str = "\n[ 系统设置: 输入help查看帮助, quit返回用户界面 输入不带参数时输出当前设置 ]"
    prompt: str = f"\n{TColor.YELLOW}⚙ {TColor.RST}SETTINGS > "

    def do_quit(self, arg):
        """返回用户界面"""
        return True

    def do_EOF(self, arg):
        """返回用户界面"""
        print()
        return True

    def do_backlight(self, arg):
        """设置背光亮度 参数: 亮度(0-4)"""
        if not arg:
            self.do_help("backlight")
            print(f"{TColor.YELLOW}当前背光亮度: {api.get_settings()['backlight']}{TColor.RST}")
        else:
            api.set_settings(backlight=int(arg))
            time.sleep(0.2)
            self.do_backlight(None)

    def do_volume(self, arg):
        """设置音量 参数: 音量(0-4)"""
        if not arg:
            self.do_help("volume")
            print(f"{TColor.YELLOW}当前音量: {api.get_settings()['volume']}{TColor.RST}")
        else:
            api.set_settings(volume=int(arg))
            time.sleep(0.2)
            self.do_volume(None)

    def do_opp(self, arg):
        """设置过功率保护值 参数: 过功率保护值(<=105W)"""
        if not arg:
            self.do_help("opp")
            print(f"{TColor.YELLOW}当前过功率保护值: {api.get_settings()['opp']}{TColor.RST}")
        else:
            api.set_settings(opp=float(arg))
            time.sleep(0.2)
            self.do_opp(None)

    def do_otp(self, arg):
        """设置过温保护值 参数: 过温保护值(50-80C)"""
        if not arg:
            self.do_help("otp")
            print(f"{TColor.YELLOW}当前过温保护值: {api.get_settings()['otp']}{TColor.RST}")
        else:
            api.set_settings(otp=int(arg))
            time.sleep(0.2)
            self.do_otp(None)


class DP100_Cmd(cmd.Cmd):
    intro: str = f"\n{TColor.CYAN}[ 本程序为DP100数控电源的命令行界面, 输入 help 或 ? 查看帮助 ]{TColor.RST}"
    data = Data_Share()
    doc_header: str = f"可用命令 (输入 help <命令> 查看详细帮助):"
    cmd_history: list = []

    def _try_warpper(func: Any):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"{TColor.RED}错误: {e}{TColor.RST}")
                return False

        setattr(wrapper, "__doc__", func.__doc__)
        return wrapper

    @_try_warpper
    def preloop(self) -> None:
        try:
            api.connect()
        except:
            pass
        self.postcmd(False, "")
        names = self.get_names()
        self._commands = []
        for name in names:
            if name.startswith("do_"):
                self._commands.append(name[3:])
        api.register_output_info_callback(lambda x, y: state_callback(self.data, x, y))
        return super().preloop()

    def do_help(self, arg: str):
        """查看可用命令, 使用 help <命令> 查看命令的详细帮助"""
        print(TColor.YELLOW, end="")
        super().do_help(arg)
        print(TColor.RST, end="")
        return False

    def postloop(self) -> None:
        try:
            api.disconnect()
        except:
            pass
        self.data.update_flag = False
        self.data.sweep_flag = False
        self.data.pid_flag = False
        self.data.wave_flag = False
        print("Bye~")
        return super().postloop()

    def emptyline(self) -> bool:
        found_command = getattr(self, "_found_command", None)
        if found_command:
            self._found_command = None
            return self.onecmd(found_command)
        return False

    @_try_warpper
    def postcmd(self, stop: bool, line: str) -> bool:
        if not stop:
            if api.connected:
                self.prompt = f"\n{TColor.GREEN}●{TColor.RST} DP100 > "
            else:
                self.prompt = f"\n{TColor.RED}○{TColor.RST} DP100 > "
        return super().postcmd(stop, line)

    def do_exit(self, arg):
        """退出程序并关闭连接"""
        return True

    def do_EOF(self, arg):
        """退出程序并关闭连接"""
        print()
        return True

    def get_closest_command(self, line: str):
        diffs = {}
        for command in self._commands:
            diffs[command] = difflib.SequenceMatcher(None, line, command).quick_ratio()
        command_sorted = sorted(diffs.items(), key=lambda x: x[1], reverse=True)
        return command_sorted

    def default(self, line: str) -> None:
        if line.startswith("!"):
            index = int(line[1:])
            return self.onecmd(self.cmd_history[index])
        command_sorted = self.get_closest_command(line)
        command = command_sorted[0][0]
        diff = command_sorted[0][1]
        if diff > 0.6:
            print(f"{TColor.YELLOW}未知命令, 您是不是在找 '{command}'{TColor.RST}")
            self._found_command = command
        else:
            print(f"{TColor.YELLOW}未知命令, 输入 help 或 ? 查看帮助{TColor.RST}")

    @_try_warpper
    def onecmd(self, line: str) -> bool:
        ret = super().onecmd(line)
        if ret is not False and line != "h" and line != "help" and line[0] != "!":
            self.cmd_history.append(line)
        return ret

    def do_connect(self, arg):
        """连接DP100"""
        api.connect()

    def do_disconnect(self, arg):
        """断开DP100"""
        api.disconnect()

    def do_about(self, arg):
        """打印设备信息"""
        print_dict_as_table("Device Info", api.get_device_info(), 30, 30)

    def do_state(self, arg):
        """打印设备状态"""
        print_dict_as_table("Device State", api.get_state(), 30, 30)

    def do_get_preset(self, arg):
        """获取预设组信息 参数: <预设组ID>"""
        if not arg:
            return self.do_help("get_preset")
        index = int(arg)
        print_dict_as_table(f"Preset-{index}", api.get_preset(index), 30, 30)

    def do_set_preset(self, arg):
        """设置预设组信息 参数: <预设组ID>"""
        if not arg:
            return self.do_help("set_preset")
        index = int(arg)
        print(f"[设置预设组-{index}]")
        voltage = float(input("设定电压(V): "))
        current = float(input("设定电流(A): "))
        ovp = float(input("过压保护(V): "))
        ocp = float(input("过流保护(A): "))
        api.set_preset(index, voltage, current, ovp, ocp)
        print(f"[预设组-{index}设置完成]")
        time.sleep(0.2)
        print_dict_as_table(f"Preset-{index}", api.get_preset(index), 30, 30)

    def do_use_preset(self, arg):
        """使用预设组 参数: <预设组ID>"""
        if not arg:
            return self.do_help("use_preset")
        api.use_preset(int(arg))
        time.sleep(0.2)
        self.do_state(None)

    def do_on(self, arg):
        """打开输出"""
        api.set_output(True)

    def do_off(self, arg):
        """关闭输出"""
        api.set_output(False)

    def do_vset(self, arg):
        """设置电压 参数: <电压(V)>"""
        if not arg:
            return self.do_help("vset")
        api.set_output(v_set=float(arg))

    def do_iset(self, arg):
        """设置电流 参数: <电流(A)>"""
        if not arg:
            return self.do_help("iset")
        api.set_output(i_set=float(arg))

    def do_watch(self, arg):
        """监视输出 参数: [刷新频率=60]"""
        print(f"\n{TColor.CYAN}[ 开始监视输出, 按Enter键执行命令或停止 ]{TColor.YELLOW}")
        print(f"额外命令: reset 清空统计\n{TColor.RST}")
        freq = int(arg) if arg else 60
        self.data.update_flag = True
        self.data.start_time = time.perf_counter()
        self.data.last_time = 0
        self.data.energy = 0
        t = Thread(
            target=update_worker,
            args=(api, self.data, freq),
            daemon=True,
        )
        t.start()
        while True:
            try:
                command = input()
            except:
                break
            if command == "":
                break
            elif command.startswith("power"):
                if self.data.pid_flag:
                    try:
                        power = float(command.split(" ")[1])
                        self.data.pid_setpoint = power
                    except:
                        pass
            elif command.startswith("reset"):
                with self.data.sync_lock:
                    self.data.start_time = time.perf_counter()
                    self.data.last_time = 0
                    self.data.energy = 0
            elif "watch" in command:
                print(f"{TColor.RED}错误: 无法在监视期间执行监视命令{TColor.RST}")
            else:
                try:
                    self.onecmd(command)
                except Exception as e:
                    print(f"{TColor.RED}错误: {e}{TColor.RST}")
        self.data.update_flag = False
        t.join()
        print(f"{TColor.CYAN}[ 监视结束 ]{TColor.RST}")

    def do_graph(self, arg):
        """显示实时数据曲线 参数: [刷新频率]"""
        args = parse(arg)
        fps = float(args[0]) if len(args) > 0 else 45
        t = None
        if not self.data.update_flag:
            self.data.update_flag = True
            self.data.start_time = time.perf_counter()
            self.data.last_time = 0
            self.data.energy = 0
            t = Thread(
                target=update_worker,
                args=(api, self.data, max(fps, 60)),
                daemon=True,
            )
            t.start()
        self.data.currents = np.ones_like(self.data.currents)
        self.data.voltages = np.ones_like(self.data.voltages)
        self.data.times = np.ones_like(self.data.times)
        self.data.init_data_flag = True
        self.data.save_datas_flag = True
        plot = Plotter(self.data)
        print(f"{TColor.CYAN}[ 开始绘图, UI将阻塞主线程, 关闭窗口停止 ]{TColor.RST}" + " " * 70)
        plot.show(fps)
        self.data.save_datas_flag = False
        if t:
            self.data.update_flag = False
            t.join()
        print(f"{TColor.CYAN}[ 绘图结束 ]{TColor.RST}" + " " * 100)

    def do_settings(self, arg):
        """进入系统设置"""
        DP100_Cmd_Settings().cmdloop()

    def do_sweep(self, arg):
        """电压扫描功能 参数: <起始电压(V)> <终止电压(V)> <步进电压(V)> <每步延时(s)>"""
        if not arg:
            return self.do_help("sweep")
        assert self.data.sweep_flag is False, "扫描功能已经在运行"
        args = parse(arg)
        start = float(args[0])
        stop = float(args[1])
        step = float(args[2])
        delay = float(args[3])
        self.data.sweep_flag = True
        Thread(target=self._sweep_worker, args=(start, stop, step, delay), daemon=True).start()
        print(f"{TColor.CYAN}[ 电压扫描开始, 扫描范围: {start}V - {stop}V, 步进: {step}V, 延时: {delay}s ]{TColor.RST}")

    def _sweep_worker(self, start, stop, step, delay):
        v = start
        t0 = time.perf_counter() - delay
        while self.data.sweep_flag:
            t1 = time.perf_counter()
            if t1 - t0 > delay:
                t0 = t1
                if (start < stop and v > stop) or (start > stop and v < stop):
                    break
                api.set_output(output=True, v_set=v)
                v += step
            else:
                time.sleep(0.001)
        if self.data.sweep_flag:
            api.set_output(output=True, v_set=stop)
            self.data.sweep_flag = False
        else:
            api.set_output(output=False)

    def do_sweep_stop(self, arg):
        """停止电压扫描"""
        self.data.sweep_flag = False
        print(f"{TColor.CYAN}[ 扫描已停止 ]{TColor.RST}")

    def do_power_constant(self, arg):
        """恒功率功能 参数: <目标功率(W)> <闭环I参数>"""
        if not arg:
            return self.do_help("power_constant")
        assert self.data.pid_flag is False, "恒功率功能已开启"
        args = parse(arg)
        power = float(args[0])
        i_arg = float(args[1])
        self.data.pid_flag = True
        t = Thread(target=self._power_pid_worker, args=(i_arg, power), daemon=True)
        t.start()
        print(f"{TColor.CYAN}[ 恒功率已开启, 目标功率: {power}W, 闭环I参数: {i_arg}, 命令 'power <功率>' 可修改目标功率 ]{TColor.RST}")
        self.do_watch(None)
        self.data.pid_flag = False
        t.join()
        api.set_output(False)
        print(f"{TColor.CYAN}[ 恒功率已关闭 ]{TColor.RST}")

    def _power_pid_worker(self, i, setpoint):
        FREQ = 30
        self.data.pid_setpoint = setpoint
        pid = PID(0, i, 0, setpoint=self.data.pid_setpoint, sample_time=1 / 60)
        pid.output_limits = (0, 20)
        api.set_output(output=True, v_set=0)
        t0 = time.perf_counter()
        circuit_open = False
        while self.data.pid_flag:
            t1 = time.perf_counter()
            if t1 - t0 > 1 / FREQ:
                t0 = t1
                if self.data.current != 0:
                    if circuit_open:
                        circuit_open = False
                        pid.set_auto_mode(True, 0)
                    pid.setpoint = self.data.pid_setpoint
                    out = pid(self.data.power)
                    api.set_output(output=True, v_set=out)
                else:
                    circuit_open = True
                    pid.set_auto_mode(False)
                    api.set_output(output=True, v_set=0.1)
            else:
                time.sleep(0.001)

    def do_clear(self, arg):
        """清空屏幕"""
        os.system("cls")

    def do_history(self, arg):
        """显示历史命令"""
        for i, cmd in enumerate(self.cmd_history):
            print(f"{TColor.CYAN}{i:d}: {TColor.YELLOW}{cmd}{TColor.RST}")

    do_h = do_history

    def do_sleep(self, arg):
        """等待功能 参数: <时间(s)>"""
        if not arg:
            return self.do_help("sleep")
        time.sleep(float(arg))

    def do_sequence_cmd(self, arg):
        """执行命令序列"""
        command = ""
        command_list = []
        index = 0
        print(f"{TColor.CYAN}[ 逐个输入指令, 以end结束 ]{TColor.RST}")
        while True:
            index += 1
            command = input(f"{TColor.YELLOW}{index:d}: {TColor.RST}")
            if command == "end":
                break
            command_list.append(command)
        print(f"{TColor.CYAN}[ 命令序列开始执行 ]{TColor.RST}")
        for index, command in enumerate(command_list):
            print(f"{TColor.CYAN}[ 执行 {TColor.YELLOW}CMD - {index:d}{TColor.CYAN} ]{TColor.RST}")
            self.onecmd(command)
        print(f"{TColor.CYAN}[ 命令序列执行完毕 ]{TColor.RST}")

    def do_wave(self, arg):
        """波形发生器 参数: <波形类型> <周期(s)> <高电平(V)> <低电平(V)> [更新频率(Hz)=30]\n波形类型: sin, square, triangle, sawtooth"""
        if not arg:
            return self.do_help("wave")
        assert self.data.wave_flag is False, "波形发生器已开启"
        args = parse(arg)
        wave_type = args[0]
        assert wave_type[:3] in ["sin", "squ", "tri", "saw"], "波形类型错误"
        period = args[1]
        high_level = args[2]
        low_level = args[3]
        update_frequency = float(args[4]) if len(args) > 4 else 30
        self.data.wave_flag = True
        Thread(
            target=self._wave_worker,
            args=(wave_type, period, high_level, low_level, update_frequency),
            daemon=True,
        ).start()
        print(
            f"{TColor.CYAN}[ 波形发生器已开启, 波形类型: {wave_type}, 周期: {period}s, 高电平: {high_level}V, 低电平: {low_level}V ]{TColor.RST}"
        )

    def _wave_worker(self, wave_type, period, high_level, low_level, update_frequency):
        t1 = time.perf_counter()
        state = api.get_state()
        iset = state["i_set"]
        preset = state["preset"]
        high_level = float(high_level)
        low_level = float(low_level)
        period = float(period)
        while self.data.wave_flag:
            t2 = time.perf_counter()
            if t2 - t1 >= 1 / update_frequency:
                t1 = t2
                if wave_type[:3] == "sin":
                    voltage = low_level + (high_level - low_level) * (math.sin(2 * math.pi / period * t2) + 1.0) / 2
                elif wave_type[:3] == "squ":
                    voltage = high_level if math.sin(2 * math.pi / period * t2) > 0 else low_level
                elif wave_type[:3] == "tri":
                    mul = (t2 / period) % 2
                    mul = mul if mul < 1 else 2 - mul
                    voltage = low_level + (high_level - low_level) * mul
                elif wave_type[:3] == "saw":
                    voltage = (high_level - low_level) * ((t2 / period) % 1) + low_level
                voltage = max(min(voltage, high_level), low_level)  # 限幅
                api.set_output(output=True, v_set=voltage, i_set=iset, preset=preset)
            else:
                time.sleep(0.001)
        api.set_output(False)

    def do_wave_stop(self, arg):
        """停止波形发生器"""
        self.data.wave_flag = False
        print(f"{TColor.CYAN}[ 波形发生器已停止 ]{TColor.RST}")


if __name__ == "__main__":
    DP100_Cmd().cmdloop()
