# ruff: noqa: E402

import datetime
import json
import math
import os
import random
import sys
import time
import warnings
from functools import partial
from threading import Lock
from typing import List, Optional

os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"
warnings.filterwarnings("ignore", category=RuntimeWarning)

ARG_PATH = os.path.dirname(sys.argv[0])
ABS_PATH = os.path.dirname(__file__)
import richuru
from loguru import logger

if os.environ.get("MDP_ENABLE_LOG") is not None or "--debug" in sys.argv:
    richuru.install(level="DEBUG")
    logger.add(
        os.path.join(ARG_PATH, "dp100.log"),
        level="TRACE",
        backtrace=True,
        diagnose=True,
    )
    DEBUG = True
else:
    richuru.install(level="INFO")
    DEBUG = False
logger.info("---- NEW SESSION ----")
logger.info(f"ARG_PATH: {ARG_PATH}")
logger.info(f"ABS_PATH: {ABS_PATH}")

try:
    sys.path.append(os.path.dirname(ABS_PATH))
    from dp100 import DP100
except ImportError:
    logger.info("Redirecting to repo")
    sys.path.append(os.path.dirname(os.path.dirname(ABS_PATH)))
    from dp100 import DP100

    logger.success("Imported from repo")

import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
from qframelesswindow import FramelessWindow

OPENGL_AVALIABLE = False
if sys.platform == "win32":  # OpenGL is not available on Linux
    try:
        import OpenGL  # noqa: F401

        OPENGL_AVALIABLE = True
        logger.success("OpenGL successfully enabled")
    except Exception as e:
        logger.warning(f"Enabling OpenGL failed with {e}.")
else:
    logger.info("OpenGL disabled on Linux")

NUMBA_ENABLED = False
try:
    import llvmlite  # noqa: F401
    import numba as nb  # noqa: F401

    pg.setConfigOption("useNumba", True)
    logger.success("Numba successfully enabled")
    NUMBA_ENABLED = True
except Exception as e:
    logger.warning(f"Enabling Numba failed with {e}.")


import numpy as np
import qdarktheme
from gui_template import Ui_DialogGraphics, Ui_DialogSettings, Ui_MainWindow
from simple_pid import PID
from superqt.utils import signals_blocked

DEVICE_NAME = "DP100"
SETTING_FILE = os.path.join(ARG_PATH, "settings.json")
ICON_PATH = os.path.join(ABS_PATH, "icon.ico")
FONT_PATH = os.path.join(ABS_PATH, "SarasaFixedSC-SemiBold.ttf")
BAT_EXAMPLE_PATH = os.path.join(ABS_PATH, "Li-ion.csv")
VERSION = "Ver2.0.0"
qdarktheme.enable_hi_dpi()
app = QtWidgets.QApplication(sys.argv)

# get system language
system_lang = QtCore.QLocale.system().name()
logger.info(f"System language: {system_lang}")
ENGLISH = False
if (
    not system_lang.startswith("zh")
    or os.environ.get("MDP_FORCE_ENGLISH") == "1"
    or "--english" in sys.argv
):
    trans = QtCore.QTranslator()
    trans.load(os.path.join(ABS_PATH, "en_US.qm"))
    app.installTranslator(trans)
    ENGLISH = True

# load custom font
_ = QtGui.QFontDatabase.addApplicationFont(FONT_PATH)
fonts = QtGui.QFontDatabase.applicationFontFamilies(_)
logger.info(f"Loaded custom fonts: {fonts}")
global_font = QtGui.QFont()
global_font.setFamily(fonts[0])
app.setFont(global_font)

from gui_source.custom import (
    CustomInputDialog,
    CustomMessageBox,
    CustomTitleBar,
    FmtAxisItem,
)


class RealtimeData:
    """实时数据存储和管理类，用于存储电压、电流等实时数据"""

    def __init__(self, data_length) -> None:
        # 初始化数据存储区，包括时间戳、临时数据和各种测量值的数组
        self.start_time = time.perf_counter()  # 记录开始时间
        self.eng_start_time = time.perf_counter()  # 记录能量计算开始时间
        self.last_time = 0  # 上次更新时间
        self.voltage_tmp = []  # 临时电压数据
        self.current_tmp = []  # 临时电流数据
        self.energy = 0  # 累计能量
        self.sync_lock = Lock()  # 线程同步锁，防止数据读写冲突
        self.voltages = np.zeros(data_length, np.float64)  # 电压数组
        self.currents = np.zeros(data_length, np.float64)  # 电流数组
        self.powers = np.zeros(data_length, np.float64)  # 功率数组
        self.resistances = np.zeros(data_length, np.float64)  # 电阻数组
        self.times = np.zeros(data_length, np.float64)  # 时间数组
        self.update_count = 0  # 更新计数器
        self.data_length = data_length  # 数据长度


class RecordData:
    """数据记录类，用于存储和导出数据到CSV文件"""

    def __init__(self) -> None:
        self.voltages: List[float] = []  # 电压列表
        self.currents: List[float] = []  # 电流列表
        self.times: List[float] = []  # 时间列表
        self.start_time = 0  # 记录开始时间
        self.last_time = 0  # 上次记录时间

    def add_values(self, voltage, current, time):
        """添加一组测量值到记录中"""
        self.voltages.append(voltage)
        self.currents.append(current)
        self.times.append(time)

    def to_csv(self, filename):
        """将记录的数据保存为CSV文件"""
        data = np.array([self.times, self.voltages, self.currents]).T
        np.savetxt(
            filename,
            data,
            delimiter=",",
            fmt="%f",
            header="time/s,voltage/V,current/A",
            comments="",
        )


class FPSCounter(object):
    """帧率计数器，用于计算和平滑显示FPS（每秒帧数）"""

    def __init__(self, max_sample=40) -> None:
        self.t = time.perf_counter()  # 初始时间戳
        self.max_sample = max_sample  # 最大样本数量
        self.t_list: List[float] = []  # 时间间隔列表
        self._fps = 0  # 当前FPS值

    def clear(self) -> None:
        """清空计数器"""
        self.t = time.perf_counter()
        self.t_list = []
        self._fps = 0

    def tick(self) -> None:
        """记录一帧，更新计数器"""
        t = time.perf_counter()
        self.t_list.append(t - self.t)
        self.t = t
        if len(self.t_list) > self.max_sample:
            self.t_list.pop(0)

    @property
    def fps(self) -> float:
        """计算并返回当前FPS值，带有平滑处理"""
        length = len(self.t_list)
        sum_t = sum(self.t_list)
        if length == 0 or sum_t == 0:
            self._fps = 0
        else:
            fps = length / sum_t
            if abs(fps - self._fps) > 2 or self._fps == 0:
                self._fps = fps
            else:
                self._fps += (fps - self._fps) * 2 / self._fps
        return self._fps


def center_window(instance: QtWidgets.QWidget, width=None, height=None) -> None:
    """将窗口居中显示在屏幕上，可选指定宽度和高度"""
    if instance.isMaximized():  # restore window size
        instance.showNormal()
    if instance.isVisible():  # bring window to front
        instance.activateWindow()
    scr_geo = QtWidgets.QApplication.primaryScreen().geometry()
    logger.debug(f"Screen geometry: {scr_geo}")
    if not width or not height:  # center window
        geo = instance.geometry()
        center_x = (scr_geo.width() - geo.width()) // 2
        center_y = (scr_geo.height() - geo.height()) // 2
        instance.move(center_x, center_y)
    else:  # set window size and center window
        center_x = (scr_geo.width() - width) // 2
        center_y = (scr_geo.height() - height) // 2
        instance.setGeometry(center_x, center_y, width, height)


def float_str(value, limit=1e5):
    """格式化浮点数字符串，大于limit的值使用科学计数法"""
    if value > limit:
        return f"{value:.1e}"
    else:
        return f"{value:.3f}"


def set_color(widget: QtWidgets.QWidget, rgb):
    """设置控件的文本颜色"""
    if not rgb or rgb == "default":
        widget.setStyleSheet("")
        return
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


class Setting:
    """应用程序设置类，管理和持久化所有用户配置"""

    def __init__(self) -> None:
        # 预设组配置
        self.presets = {
            "1": (3.3, 2),
            "2": (3.3, 5),
            "3": (5, 2),
            "4": (5, 5),
            "5": (9, 5),
            "6": (12, 5),
            "7": (20, 5),
            "8": (24, 10),
            "9": (30, 10),
        }
        # 通信设置
        self.baudrate = 921600
        self.comport = ""

        # 图表设置
        self.data_pts = 100000  # 数据点数
        self.display_pts = 400  # 显示点数
        self.graph_max_fps = 50  # 图表最大刷新率
        self.state_fps = 10  # 状态刷新率
        self.interp = 0  # 插值设置
        self.opengl = False  # 是否使用OpenGL
        self.antialias = True  # 是否使用抗锯齿
        self.bitadjust = False  # 位调整设置

        # 输出设置
        self.last_vset = 5  # 上次电压设置
        self.last_iset = 2  # 上次电流设置

        # 校准和阈值设置
        self.v_threshold = 0.002  # 电压阈值
        self.i_threshold = 0.002  # 电流阈值
        self.use_cali = False  # 是否使用校准
        self.v_cali_k = 1.0  # 电压校准系数k
        self.v_cali_b = 0.0  # 电压校准偏移b
        self.i_cali_k = 1.0  # 电流校准系数k
        self.i_cali_b = 0.0  # 电流校准偏移b
        self.vset_cali_k = 1.0  # 电压设置校准系数k
        self.vset_cali_b = 0.0  # 电压设置校准偏移b
        self.iset_cali_k = 1.0  # 电流设置校准系数k
        self.iset_cali_b = 0.0  # 电流设置校准偏移b
        self.output_warning = False  # 输出警告设置
        self.lock_when_output = False  # 输出时锁定设置
        self.unlock_opp = False  # 解锁过功率保护上限

        # 主题设置
        self.theme = "dark"
        # 颜色配置
        self.color_palette = {
            "dark": {
                "off": "khaki",
                "on": "lightgreen",
                "cv": "skyblue",
                "cc": "tomato",
                "lcd_voltage": "default",
                "lcd_current": "default",
                "lcd_power": "default",
                "lcd_energy": "default",
                "lcd_avg_power": "default",
                "lcd_resistance": "default",
                "general_green": "mediumaquamarine",
                "general_red": "orangered",
                "general_yellow": "yellow",
                "general_blue": "lightblue",
                "line1": "salmon",
                "line2": "turquoise",
            },
            "light": {
                "lcd_voltage": "default",
                "lcd_current": "default",
                "lcd_power": "default",
                "lcd_energy": "default",
                "lcd_avg_power": "default",
                "lcd_resistance": "default",
                "off": "darkgoldenrod",
                "on": "darkgreen",
                "cv": "darkblue",
                "cc": "darkred",
                "general_green": "forestgreen",
                "general_red": "firebrick",
                "general_yellow": "goldenrod",
                "general_blue": "darkblue",
                "line1": "orangered",
                "line2": "darkcyan",
            },
            "modify_this_to_add_your_custom_theme": {
                "based_on_dark_or_light": "dark",
                "any_other_item": "any_other_color",
            },
        }

    def save(self, filename):
        """保存设置到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=4, ensure_ascii=False)

    def load(self, filename):
        """从文件加载设置"""
        if not os.path.exists(filename):
            self.save(filename)
            return
        def_colorplate = self.color_palette
        self.__dict__.update(json.load(open(filename, "r", encoding="utf-8")))
        for k, v in def_colorplate.items():
            if k not in self.color_palette:
                self.color_palette[k] = v
            elif len(self.color_palette[k]) < len(v):
                v.update(self.color_palette[k])
                self.color_palette[k] = v

    def get_color(self, key, override_theme=None):
        """获取指定主题下的颜色"""
        t = override_theme or self.theme
        if t in ("dark", "light"):
            return self.color_palette[t].get(key)
        else:
            if "based_on_dark_or_light" not in self.color_palette[t]:
                self.color_palette[t]["based_on_dark_or_light"] = "dark"
            return self.color_palette[t].get(
                key,
                self.color_palette[self.color_palette[t]["based_on_dark_or_light"]].get(
                    key
                ),
            )

    def __repr__(self) -> str:
        return f"Setting({self.__dict__})"


setting = Setting()
setting.load(SETTING_FILE)
setting.save(SETTING_FILE)


def update_pyqtgraph_setting():
    """更新PyQtGraph设置，包括抗锯齿和OpenGL支持"""
    pg.setConfigOption("antialias", setting.antialias)
    if OPENGL_AVALIABLE:
        pg.setConfigOption("enableExperimental", setting.opengl)
        pg.setConfigOption("useOpenGL", setting.opengl)
    logger.debug(f"Antialias: {setting.antialias}, OpenGL: {setting.opengl}")


update_pyqtgraph_setting()


class MDPThread(QtCore.QThread):
    """用于与设备通信的线程类，实现异步数据采集"""

    error_signal = QtCore.pyqtSignal(str)  # 错误信号
    data_signal = QtCore.pyqtSignal(float, float, float)  # 电压、电流、时间戳
    state_signal = QtCore.pyqtSignal(dict)  # 状态信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.api: Optional[DP100] = None  # PDAPI接口
        self.data_timer = QtCore.QTimer(self)  # 定时器，用于定期读取数据
        self.data_timer.setTimerType(QtCore.Qt.PreciseTimer)  # 使用精确定时器
        self.data_timer.timeout.connect(self.request_callback)  # 连接回调函数

    def run(self):
        """线程主循环，保持线程运行"""
        while True:
            time.sleep(1)

    def set_api(self, api: Optional[DP100]):
        """设置API接口"""
        logger.info(f"Setting API to {api}")
        if not api and self.data_timer.isActive():
            self.data_timer.stop()
        self.api = api
        if self.api is not None:
            self.api.register_output_info_callback(self.data_callback)

    def set_data_freq(self, freq: float):
        """设置数据采集频率"""
        if freq > 0:
            if self.data_timer.isActive():
                self.data_timer.stop()
            self.data_timer.setInterval(round(1000 / freq))  # 计算定时器间隔
            self.data_timer.start()
        else:
            self.data_timer.stop()

    def request_callback(self):
        if self.api is not None:
            try:
                self.api.get_output_info()
            except Exception as e:
                self.error_signal.emit(str(e))

    def data_callback(self, v_mv: int, i_ma: int):
        self.data_signal.emit(v_mv / 1000, i_ma / 1000, time.perf_counter())

    def state_callback(self):
        if self.api is not None:
            try:
                self.state_signal.emit(self.api.get_state())
            except Exception as e:
                self.error_signal.emit(str(e))

    def action_proxy(self, func: str, args: dict):
        if self.api is not None:
            try:
                getattr(self.api, func)(**args)
            except Exception as e:
                self.error_signal.emit(str(e))


class MDPMainwindow(QtWidgets.QMainWindow, FramelessWindow):  # QtWidgets.QMainWindow
    """上位机主窗口类，管理UI界面和所有功能"""

    set_data_freq_signal = QtCore.pyqtSignal(float)  # 设置数据频率信号
    state_signal = QtCore.pyqtSignal()  # 状态信号
    action_signal = QtCore.pyqtSignal(str, dict)  # 动作信号

    uip_values_signal = QtCore.pyqtSignal(float, float, float)  # 电压、电流、功率信号
    display_data_signal = QtCore.pyqtSignal(
        list, list, str, str, str, str, str, bool
    )  # 显示数据信号
    highlight_point_signal = QtCore.pyqtSignal(float, float)  # 高亮点信号

    close_signal = QtCore.pyqtSignal()  # 关闭信号
    data = RealtimeData(setting.data_pts)  # 实时数据对象
    data_sr = 50.0  # 数据刷新率
    graph_keep_flag = False  # 图表保持标志
    graph_record_flag = False  # 图表记录标志
    locked = False  # 锁定标志
    uip_values_signal = QtCore.pyqtSignal(float, float, float)
    display_data_signal = QtCore.pyqtSignal(list, list, str, str, str, str, str, bool)
    highlight_point_signal = QtCore.pyqtSignal(float, float)

    close_signal = QtCore.pyqtSignal()
    data = RealtimeData(setting.data_pts)
    graph_keep_flag = False
    graph_record_flag = False
    locked = False
    _v_set = 0.0
    _i_set = 0.0
    _output_state = False
    _preset = 0
    open_r = 1e7
    continuous_energy_counter = 0
    model = "Unknown"

    def __init__(self, parent=None):
        self.api: Optional[DP100] = None

        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.initSignals()
        self.initGraph()
        self.initTimer()
        self.fps_counter = FPSCounter()
        self.CustomTitleBar = CustomTitleBar(
            self,
            self.tr("DP100 数控电源上位机") + f" {VERSION} By Ellu",
        )
        self.CustomTitleBar.set_theme("dark")
        self.setTitleBar(self.CustomTitleBar)
        self.set_interp(setting.interp)
        self.refresh_preset()
        self.get_preset("1")
        self.refresh_preset_hw()
        self.get_preset_hw("")
        self.close_state_ui()
        self.load_battery_model(BAT_EXAMPLE_PATH)
        center_window(self, 920, 800)
        self.ui.progressBarVoltage.setMaximum(1000)
        self.ui.progressBarCurrent.setMaximum(1000)
        self._last_state_change_t = time.perf_counter()
        self.titleBar.raise_()
        self.ui.btnSeqStop.hide()
        self.ui.listSeq.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.spinBoxVoltage.setSingleStep(0.001)
        self.ui.spinBoxCurrent.setSingleStep(0.001)
        self.ui.doubleSpinBoxSampleRate.setValue(self.data_sr)

        self.ui.tabWidget.tabBar().setVisible(False)
        self.ui.labelTab.setText(
            self.ui.tabWidget.tabText(self.ui.tabWidget.currentIndex())
        )

        self.mdp_thread = MDPThread()
        self.set_data_freq_signal.connect(self.mdp_thread.set_data_freq)
        self.state_signal.connect(self.mdp_thread.state_callback)
        self.action_signal.connect(self.mdp_thread.action_proxy)
        self.mdp_thread.data_signal.connect(self.data_callback)
        self.mdp_thread.state_signal.connect(self.update_state_cbk)
        self.mdp_thread.error_signal.connect(self.error_handler)
        self.mdp_thread.start()

        if ENGLISH:
            c_font = QtGui.QFont()
            c_font.setFamily("Sarasa Fixed SC SemiBold")
            c_font.setPointSize(7)
            self.ui.btnSeqCurrent.setFont(c_font)
            self.ui.btnSeqCurrent.setText("I-SET")
            self.ui.btnSeqVoltage.setFont(c_font)
            self.ui.btnSeqVoltage.setText("V-SET")
            self.ui.btnSeqDelay.setFont(c_font)
            self.ui.btnSeqWaitTime.setFont(c_font)
            self.ui.btnSeqSingle.setFont(c_font)
            self.ui.btnSeqSingle.setText("Once")
            self.ui.btnSeqLoop.setFont(c_font)
            self.ui.btnSeqSave.setFont(c_font)
            self.ui.btnSeqLoad.setFont(c_font)

    @QtCore.pyqtSlot(int)
    def on_tabWidget_currentChanged(self, index):
        self.ui.labelTab.setText(self.ui.tabWidget.tabText(index))
        if index == 0:
            self.ui.pushButtonLastTab.setEnabled(False)
        elif index == self.ui.tabWidget.count() - 1:
            self.ui.pushButtonNextTab.setEnabled(False)
        else:
            self.ui.pushButtonLastTab.setEnabled(True)
            self.ui.pushButtonNextTab.setEnabled(True)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        pos = event.pos()
        label_geom = self.ui.labelTab.geometry()
        label_pos = self.ui.labelTab.mapTo(self, QtCore.QPoint(0, 0))
        label_rect = QtCore.QRect(label_pos, label_geom.size())
        if self.api is not None and label_rect.contains(pos):
            delta = event.angleDelta().y()
            current_idx = self.ui.tabWidget.currentIndex()
            if delta > 0:
                if current_idx > 0:
                    self.ui.tabWidget.setCurrentIndex(current_idx - 1)
            else:
                if current_idx < self.ui.tabWidget.count() - 1:
                    self.ui.tabWidget.setCurrentIndex(current_idx + 1)
            event.accept()
        else:
            event.ignore()

    @QtCore.pyqtSlot()
    def on_pushButtonLastTab_clicked(self):
        idx = self.ui.tabWidget.currentIndex()
        if idx > 0:
            self.ui.tabWidget.setCurrentIndex(idx - 1)

    @QtCore.pyqtSlot()
    def on_pushButtonNextTab_clicked(self):
        idx = self.ui.tabWidget.currentIndex()
        if idx < self.ui.tabWidget.count() - 1:
            self.ui.tabWidget.setCurrentIndex(idx + 1)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close_signal.emit()
        setting.save(SETTING_FILE)
        return super().closeEvent(a0)

    def initTimer(self):
        """初始化所有定时器"""
        # 状态更新定时器
        self.update_state_timer = QtCore.QTimer(self)
        self.update_state_timer.timeout.connect(self.update_state)

        # 图表绘制定时器
        self.draw_graph_timer = QtCore.QTimer(self)
        self.draw_graph_timer.timeout.connect(self.draw_graph)

        # LCD状态更新定时器
        self.state_lcd_timer = QtCore.QTimer(self)
        self.state_lcd_timer.timeout.connect(self.update_state_lcd)

        # 扫描功能定时器
        self.func_sweep_timer = QtCore.QTimer(self)
        self.func_sweep_timer.timeout.connect(self.func_sweep)

        # 波形生成定时器
        self.func_wave_gen_timer = QtCore.QTimer(self)
        self.func_wave_gen_timer.timeout.connect(self.func_wave_gen)

        # 功率保持定时器
        self.func_keep_power_timer = QtCore.QTimer(self)
        self.func_keep_power_timer.timeout.connect(self.func_keep_power)

        # 序列执行定时器
        self.func_seq_timer = QtCore.QTimer(self)
        self.func_seq_timer.timeout.connect(self.func_seq)

        # 电池模拟定时器
        self.func_bat_sim_timer = QtCore.QTimer(self)
        self.func_bat_sim_timer.timeout.connect(self.func_bat_sim)

        # 记录保存定时器
        self.graph_record_save_timer = QtCore.QTimer(self)
        self.graph_record_save_timer = QtCore.QTimer(self)
        self.graph_record_save_timer.timeout.connect(self.graph_record_save)

    def initSignals(self):
        self.ui.doubleSpinBoxSampleRate.valueChanged.connect(self.set_data_fps)
        self.ui.comboPreset.currentTextChanged.connect(self.set_preset)
        self.ui.comboPreset2.currentTextChanged.connect(self.set_preset_hw)
        self.ui.comboPresetEdit.currentTextChanged.connect(self.get_preset)
        self.ui.comboPresetEdit2.currentTextChanged.connect(self.get_preset_hw)
        self.ui.comboGraph1Data.currentTextChanged.connect(self.set_graph1_data)
        self.ui.comboGraph2Data.currentTextChanged.connect(self.set_graph2_data)
        self.ui.spinBoxVoltage.valueChanged.connect(self.voltage_changed)
        self.ui.spinBoxCurrent.valueChanged.connect(self.current_changed)
        self.ui.comboWaveGenType.currentTextChanged.connect(self.set_wavegen_type)
        self.ui.spinBoxVoltage.lineEdit().cursorPositionChanged.connect(
            lambda *args: self.set_step(self.ui.spinBoxVoltage, *args)
        )
        self.ui.spinBoxCurrent.lineEdit().cursorPositionChanged.connect(
            lambda *args: self.set_step(self.ui.spinBoxCurrent, *args)
        )
        self.ui.horizontalSlider.sliderMoved.connect(
            self.on_horizontalSlider_sliderMoved
        )

    def startMyTimer(self):
        t = time.perf_counter()
        self.data.start_time = t
        self.data.eng_start_time = t
        self.data.last_time = t
        self.data.energy = 0
        self.set_data_freq_signal.emit(self.data_sr)
        self.draw_graph_timer.start(
            min(round(1000 / self.data_sr), round(1000 / setting.graph_max_fps))
        )
        self.state_lcd_timer.start(
            min(round(1000 / self.data_sr), round(1000 / setting.state_fps))
        )
        self.update_state_timer.start(250)

    def stopMyTimer(self):
        self.draw_graph_timer.stop()
        self.state_lcd_timer.stop()
        self.set_data_freq_signal.emit(0)
        if self.func_sweep_timer.isActive():
            self.stop_func_sweep()
        if self.func_wave_gen_timer.isActive():
            self.stop_func_wave_gen()
        if self.func_keep_power_timer.isActive():
            self.stop_func_keep_power()
        if self.func_seq_timer.isActive():
            self.stop_func_seq()
        if self.func_bat_sim_timer.isActive():
            self.stop_func_bat_sim()
        if self.graph_record_save_timer.isActive():
            self.on_btnGraphRecord_clicked()
        if self.update_state_timer.isActive():
            self.update_state_timer.stop()

    def switch_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def set_step(self, spin: QtWidgets.QDoubleSpinBox, f, t):
        if not setting.bitadjust:
            # enable adaptive step size
            spin.setStepType(
                QtWidgets.QAbstractSpinBox.StepType.AdaptiveDecimalStepType
            )
            return
        spin.setStepType(QtWidgets.QAbstractSpinBox.StepType.DefaultStepType)
        STEPS = {
            0: 0.01,
            -1: 0.01,
            -2: 0.1,
        }
        if spin.lineEdit().hasSelectedText():
            return
        text = spin.lineEdit().text()
        tt = t - len(spin.lineEdit().text())
        t -= 1
        if tt == 0:
            t -= 1
        if text[t] == ".":
            if f < t:
                t += 1
            else:
                t -= 1
        if t <= 0:
            t = 0
        if spin.value() >= 10 and t == 0:
            t = 1
        spin.lineEdit().setSelection(t, 1)
        spin.setSingleStep(STEPS.get(tt, 1))

    ##########  基本功能  ##########

    def sync_state(self, output=None, v_set=None, i_set=None, preset=None):
        if self.api is None or self.locked:
            return
        self.action_signal.emit(
            "set_output",
            {
                "output": output if output is not None else self._output_state,
                "v_set": v_set if v_set is not None else self._v_set,
                "i_set": i_set if i_set is not None else self._i_set,
                "preset": preset if preset is not None else self._preset,
            },
        )

    @property
    def v_set(self):
        return self._v_set

    @v_set.setter
    def v_set(self, value):
        if self.api is None or self.locked:
            return
        value = max(0, min(value, self.ui.spinBoxVoltage.maximum()))
        self._v_set = value
        setting.last_vset = value
        self.ui.spinBoxVoltage.setValue(value)
        if setting.use_cali:
            value = value * setting.vset_cali_k + setting.vset_cali_b
        self.sync_state(v_set=value)
        self._last_state_change_t = time.perf_counter()

    @property
    def i_set(self):
        return self._i_set

    @i_set.setter
    def i_set(self, value):
        if self.api is None or self.locked:
            return
        value = max(0, min(value, self.ui.spinBoxCurrent.maximum()))
        self._i_set = value
        setting.last_iset = value
        self.ui.spinBoxCurrent.setValue(value)
        if setting.use_cali:
            value = value * setting.iset_cali_k + setting.iset_cali_b
        self.sync_state(i_set=value)
        self._last_state_change_t = time.perf_counter()

    @property
    def output_state(self):
        return self._output_state

    @output_state.setter
    def output_state(self, value):
        if self.api is None or value == self._output_state:
            return
        if setting.output_warning and not self._output_state:
            ok = CustomMessageBox.question(
                self,
                self.tr("警告"),
                self.tr("确定要打开输出?")
                + f"\n{self.tr('电压')}: {self.v_set:.3f}V"
                + f"\n{self.tr('电流')}: {self.i_set:.3f}A",
            )
            if not ok:
                return
        self._output_state = value
        self._last_state_change_t = time.perf_counter()
        self.sync_state(output=value)
        self.update_state()

    @QtCore.pyqtSlot()
    def on_btnSettings_clicked(self):
        if self.api is None:
            CustomMessageBox(
                self,
                self.tr("错误"),
                self.tr("请先连接设备"),
            )
            return
        DialogSettings.show()

    @property
    def preset(self):
        return self._preset

    @preset.setter
    def preset(self, value):
        self._preset = value
        self.sync_state(preset=value)
        self.update_state()

    def update_state(self):
        if self.api is None:
            return
        self.state_signal.emit()

    def update_state_cbk(self, state: dict):
        if self.api is None:
            return
        self._v_set = state["v_set"]
        self._i_set = state["i_set"]
        self._output_state = state["output"]
        self._preset = state["preset"]
        # update ui
        if not self.ui.spinBoxVoltage.hasFocus():
            self.ui.spinBoxVoltage.setValue(self._v_set)
        if not self.ui.spinBoxCurrent.hasFocus():
            self.ui.spinBoxCurrent.setValue(self._i_set)
        state_str = "on" if self._output_state else "off"
        self.ui.btnOutput.setText(f"-  {state_str.upper()}  -")
        set_color(
            self.ui.btnOutput,
            setting.get_color(state_str),
        )
        # check lock
        self.locked = False
        self.ui.frameOutputSetting.setEnabled(not self.locked)
        if setting.lock_when_output and self._output_state:
            self.locked = True
        self.ui.spinBoxVoltage.setEnabled(not self.locked)
        self.ui.spinBoxCurrent.setEnabled(not self.locked)

    @QtCore.pyqtSlot()
    def on_btnOutput_clicked(self):
        self.output_state = not self.output_state

    def close_state_ui(self):
        self.ui.labelConnectState.setText(self.tr("未连接"))
        set_color(self.ui.labelConnectState, None)
        self.ui.frameOutputSetting.setEnabled(False)
        self.ui.frameGraph.setEnabled(False)
        self.ui.progressBarCurrent.setValue(0)
        self.ui.progressBarVoltage.setValue(0)
        self.data_callback(0, 0, time.perf_counter())
        self.ui.btnOutput.setText("[N/A]")
        set_color(self.ui.btnOutput, None)
        self.curve1.setData(x=[], y=[])
        self.curve2.setData(x=[], y=[])
        self.ui.labelGraphInfo.setText("No Info")
        for widget in [
            self.ui.lcdVoltage,
            self.ui.lcdCurrent,
            self.ui.lcdResistence,
            self.ui.lcdPower,
            self.ui.lcdAvgPower,
            self.ui.lcdEnerge,
        ]:
            widget.display("")
        self.ui.horizontalSlider.setRange(0, 10)
        self.ui.horizontalSlider.setValue((2, 8))
        self.ui.labelBufferSize.setText("N/A")
        self.ui.labelDisplayRange.setText("N/A")
        set_color(self.ui.labelBufferSize, None)
        self.ui.frameGraphControl.setEnabled(False)

    def open_state_ui(self):
        self.ui.labelConnectState.setText(self.tr("已连接"))
        set_color(
            self.ui.labelConnectState,
            setting.get_color("general_green"),
        )
        self.ui.frameOutputSetting.setEnabled(True)
        self.ui.frameGraph.setEnabled(True)
        self.ui.frameGraphControl.setEnabled(True)
        self.ui.spinBoxVoltage.setValue(setting.last_vset)
        self.ui.spinBoxCurrent.setValue(setting.last_iset)
        self._v_set = setting.last_vset
        self._i_set = setting.last_iset

    def error_handler(self, error_type: str):
        self.disconnect_device()
        CustomMessageBox(self, self.tr("错误"), error_type)

    def disconnect_device(self):
        self.stopMyTimer()
        self.close_state_ui()
        api = self.api
        self.api = None
        self.mdp_thread.set_api(None)
        try:
            api.disconnect()
        except Exception:
            pass
        self.api = None
        self.v_set = 0.0
        self.i_set = 0.0
        self.model = "Unknown"
        self.ui.spinBoxCurrent.setRange(0, 10)
        self.CustomTitleBar.set_name(
            self.tr("DP100 数控电源上位机") + f" {VERSION} By Ellu"
        )
        if DialogSettings.visible:
            DialogSettings.close()

    @QtCore.pyqtSlot()
    def on_btnConnect_clicked(self):
        try:
            if self.api is not None:
                self.disconnect_device()
            else:
                api = None
                try:
                    api = DP100()
                    api.connect()
                    time.sleep(0.05)
                    api.get_device_info()
                except Exception as e:
                    if api is not None:
                        try:
                            api.disconnect()
                        except Exception:
                            pass
                    logger.exception("Failed to connect")
                    raise e
                self.api = api
                self.mdp_thread.set_api(api)
                self._last_state_change_t = time.perf_counter()
                self.open_state_ui()
                self.get_preset_hw("")
                self.startMyTimer()
                self.update_state()
                self.on_btnGraphClear_clicked(skip_confirm=True)
        except Exception as e:
            error = self.tr("无法与设备建立通信, 请检查USB连接是否正常")
            CustomMessageBox(self, self.tr("连接失败"), error)
            logger.exception("Failed to operation")
            raise e

    def data_callback(self, volt: float, curr: float, timestamp: float):
        if setting.use_cali:
            volt = volt * setting.v_cali_k + setting.v_cali_b
            curr = curr * setting.i_cali_k + setting.i_cali_b
        if volt < setting.v_threshold:
            volt = 0
        if curr < setting.i_threshold:
            curr = 0
        data = self.data
        if self.graph_record_flag:
            if self.graph_record_data.start_time == 0:
                self.graph_record_data.start_time = timestamp
                self.graph_record_data.last_time = timestamp
            else:
                t = timestamp - self.graph_record_data.start_time
                dt = timestamp - self.graph_record_data.last_time
                self.graph_record_data.last_time = timestamp
                self.graph_record_data.add_values(volt, curr, t)
        eng = 0
        with data.sync_lock:
            data.voltage_tmp.append(volt)
            data.current_tmp.append(curr)
            t = timestamp - data.start_time
            dt = timestamp - data.last_time
            data.last_time = timestamp
            eng += volt * curr * dt
            self.continuous_energy_counter += eng
            data.energy += eng
            if data.update_count + 1 > data.data_length:
                offset = data.update_count + 1 - data.data_length
                data.voltages = np.roll(data.voltages, -offset)
                data.currents = np.roll(data.currents, -offset)
                data.powers = np.roll(data.powers, -offset)
                data.resistances = np.roll(data.resistances, -offset)
                data.times = np.roll(data.times, -offset)
                data.update_count -= offset
            data.voltages[data.update_count] = volt
            data.currents[data.update_count] = curr
            data.powers[data.update_count] = volt * curr
            data.resistances[data.update_count] = (
                volt / curr if curr != 0 else self.open_r
            )
            data.times[data.update_count] = t - dt
            data.update_count += 1
        self.fps_counter.tick()

    def update_state_lcd(self):
        data = self.data
        if len(data.voltage_tmp) == 0 or len(data.current_tmp) == 0:
            return
        with data.sync_lock:
            vavg = sum(data.voltage_tmp) / len(data.voltage_tmp)
            iavg = sum(data.current_tmp) / len(data.current_tmp)
            data.voltage_tmp.clear()
            data.current_tmp.clear()
            self.ui.lcdAvgPower.display(
                f"{data.energy / (data.last_time - data.eng_start_time):.{3 + setting.interp}f}"
            )
            self.ui.lcdEnerge.display(f"{data.energy:.{3 + setting.interp}f}")
        power = vavg * iavg
        if iavg >= 0.002:  # 致敬P906的愚蠢adc
            resistance = vavg / iavg
        else:
            resistance = self.open_r
        r_text = (
            f"{resistance:.{3 + setting.interp}f}"
            if resistance < self.open_r / 100
            else "--"
        )
        self.ui.lcdVoltage.display(f"{vavg:.{3 + setting.interp}f}")
        self.ui.lcdCurrent.display(f"{iavg:.{3 + setting.interp}f}")
        self.ui.lcdResistence.display(r_text)
        self.ui.lcdPower.display(f"{power:.{3 + setting.interp}f}")
        self.uip_values_signal.emit(vavg, iavg, power)
        v_value = round(vavg / self.v_set * 1000) if self.v_set != 0 else 0
        i_value = round(iavg / self.i_set * 1000) if self.i_set != 0 else 0
        self.ui.progressBarVoltage.setValue(min(v_value, 1000))
        self.ui.progressBarCurrent.setValue(min(i_value, 1000))
        self.ui.progressBarVoltage.update()
        self.ui.progressBarCurrent.update()

    def set_interp(self, interp):
        self.ui.lcdVoltage.setDigitCount(6 + interp)
        self.ui.lcdCurrent.setDigitCount(6 + interp)
        self.ui.lcdResistence.setDigitCount(6 + interp)
        self.ui.lcdPower.setDigitCount(6 + interp)
        self.ui.lcdAvgPower.setDigitCount(6 + interp)
        self.ui.lcdEnerge.setDigitCount(6 + interp)

    def set_data_fps(self, val: float):
        if val < 1:
            return
        self.data_sr = val
        self.set_data_freq_signal.emit(self.data_sr)
        if self.draw_graph_timer.isActive():
            self.draw_graph_timer.stop()
            self.draw_graph_timer.start(
                min(round(1000 / self.data_sr), round(1000 / setting.graph_max_fps))
            )
        if self.state_lcd_timer.isActive():
            self.state_lcd_timer.stop()
            self.state_lcd_timer.start(
                min(round(1000 / self.data_sr), round(1000 / setting.state_fps))
            )
        self.fps_counter.clear()

    def set_graph_max_fps(self, _):
        self.set_data_fps(self.ui.doubleSpinBoxSampleRate.value())

    def set_state_fps(self, fps):
        self.set_data_fps(self.ui.doubleSpinBoxSampleRate.value())

    def set_data_length(self, length) -> None:
        self.data.data_length = length
        self.on_btnGraphClear_clicked(skip_confirm=True)

    @QtCore.pyqtSlot()
    def on_btnRecordClear_clicked(self):
        with self.data.sync_lock:
            self.data.energy = 0
            self.data.eng_start_time = time.perf_counter()

    @QtCore.pyqtSlot()
    def on_spinBoxVoltage_editingFinished(self):
        v_set = self.ui.spinBoxVoltage.value()
        self.ui.spinBoxVoltage.setSingleStep(0.001)
        self.v_set = v_set

    @QtCore.pyqtSlot()
    def on_spinBoxCurrent_editingFinished(self):
        i_set = self.ui.spinBoxCurrent.value()
        self.ui.spinBoxCurrent.setSingleStep(0.001)
        self.i_set = i_set

    def voltage_changed(self, value):
        if not self.ui.checkBoxQuickset.isChecked():
            return
        self.v_set = value

    def current_changed(self, value):
        if not self.ui.checkBoxQuickset.isChecked():
            return
        self.i_set = value

    ##########  图像绘制  ##########

    def initGraph(self):
        """初始化图表组件和设置"""
        # 设置图表背景和标签
        self.ui.widgetGraph1.setBackground(None)
        self.ui.widgetGraph2.setBackground(None)
        self.ui.widgetGraph1.setLabel("left", self.tr("电压"), units="V")
        self.ui.widgetGraph2.setLabel("left", self.tr("电流"), units="A")

        # 设置单位字典
        self._graph_units_dict = {
            self.tr("电压"): "V",
            self.tr("电流"): "A",
            self.tr("功率"): "W",
            self.tr("阻值"): "Ω",
        }

        # 设置网格和鼠标交互
        self.ui.widgetGraph1.showGrid(x=True, y=True)
        self.ui.widgetGraph2.showGrid(x=True, y=True)
        self.ui.widgetGraph1.setMouseEnabled(x=False, y=False)
        self.ui.widgetGraph2.setMouseEnabled(x=False, y=False)

        # 创建画笔和曲线
        self.pen1 = pg.mkPen(color=setting.get_color("line1"), width=1)
        self.pen2 = pg.mkPen(color=setting.get_color("line2"), width=1)
        self.curve1 = self.ui.widgetGraph1.plot(pen=self.pen1, clear=True)
        self.curve2 = self.ui.widgetGraph2.plot(pen=self.pen2, clear=True)

        # 设置自动缩放标志
        self._graph_auto_scale_flag = True

        # 创建左侧轴并同步
        axis1 = FmtAxisItem(orientation="left")
        axis2 = FmtAxisItem(orientation="left")
        axis1.syncWith(axis2, left_spacing=True)
        axis2.syncWith(axis1, left_spacing=True)
        self.ui.widgetGraph1.setAxisItems(axisItems={"left": axis1})
        self.ui.widgetGraph2.setAxisItems(axisItems={"left": axis2})

        # 设置初始数据类型
        self.set_graph1_data(self.tr("电压"), skip_update=True)
        self.set_graph2_data(self.tr("电流"), skip_update=True)

    def update_pen(self):
        """更新画笔颜色"""
        self.pen1.setColor(QtGui.QColor(setting.get_color("line1")))
        self.pen2.setColor(QtGui.QColor(setting.get_color("line2")))

    def get_data(self, text: str, display_pts: int, r_offset: int = 0):
        """获取指定类型的数据，用于绘图

        参数:
            text: 数据类型（电压/电流/功率/阻值）
            display_pts: 显示点数
            r_offset: 右侧偏移

        返回:
            data: 数据数组
            time: 时间数组
            start_index: 开始索引
            to_index: 结束索引
            max_val: 最大值
            min_val: 最小值
            avg_val: 平均值
        """
        if text == self.tr("电压"):
            data = self.data.voltages[: self.data.update_count]
        elif text == self.tr("电流"):
            data = self.data.currents[: self.data.update_count]
        elif text == self.tr("功率"):
            data = self.data.powers[: self.data.update_count]
        elif text == self.tr("阻值"):
            data = self.data.resistances[: self.data.update_count]
            time = self.data.times[: self.data.update_count]
            # 找出非开路的索引
            indexs = np.where(data != self.open_r)[0]
            data = data[indexs]
            if data.size == 0:
                return None, None, None, None, None, None, None
            time = time[indexs]
            start_index = max(0, len(data) - display_pts - r_offset)
            to_index = len(data) - r_offset
            eval_data = data[start_index:to_index]
            return (
                data,
                time,
                start_index,
                to_index,
                np.max(eval_data),
                np.min(eval_data),
                np.mean(eval_data),
            )
        else:
            return None, None, None, None, None, None, None
        if data.size == 0:
            return None, None, None, None, None, None, None
        start_index = max(0, len(data) - display_pts - r_offset)
        to_index = len(data) - r_offset
        eval_data = data[start_index:to_index]
        return (
            data,
            self.data.times[: self.data.update_count],
            start_index,
            to_index,
            np.max(eval_data),
            np.min(eval_data),
            np.mean(eval_data),
        )

    _typename_dict = None

    _left_last = -1

    def on_horizontalSlider_sliderMoved(self, values):
        left = int(values[0])
        right = int(values[1])
        left_moved = left != self._left_last
        if right - left < setting.display_pts:
            if left_moved:
                right = min(
                    left + setting.display_pts, self.ui.horizontalSlider._maximum
                )
                if right - left < setting.display_pts:
                    left = max(right - setting.display_pts, 0)
            else:
                left = max(right - setting.display_pts, 0)
                if right - left < setting.display_pts:
                    right = min(
                        left + setting.display_pts, self.ui.horizontalSlider._maximum
                    )
            with signals_blocked(self.ui.horizontalSlider):
                self.ui.horizontalSlider.setValue((left, right))
        self._left_last = left

    def draw_graph(self):
        """绘制图表，更新数据显示

        主要功能：
        1. 更新FPS显示
        2. 处理滑块和显示范围
        3. 获取并显示数据
        4. 更新信息标签
        5. 自动缩放图表
        """
        # 初始化类型字典（如果未初始化）
        if self._typename_dict is None:
            self._typename_dict = {
                self.tr("电压"): "V",
                self.tr("电流"): "I",
                self.tr("功率"): "P",
                self.tr("阻值"): "R",
            }

        # 更新FPS显示
        self.ui.labelFps.setText(f"{self.fps_counter.fps:.1f}Hz")

        # 如果图表保持标志为真，不更新图表
        if self.graph_keep_flag:
            return

        # 获取图表数据类型
        type1 = self.ui.comboGraph1Data.currentText()
        type2 = self.ui.comboGraph2Data.currentText()

        # 使用同步锁获取数据
        with self.data.sync_lock:
            update_count = self.data.update_count

            if update_count > setting.display_pts + 5:
                left, right = self.ui.horizontalSlider.sliderPosition()
                max_ = self.ui.horizontalSlider._maximum
                syncing = right == max_
                allfit = syncing and (left == 0)
                if not self.ui.horizontalSlider.isEnabled():
                    self.ui.horizontalSlider.setEnabled(True)
                    allfit = False
                    left = max(1, right - setting.display_pts)
                if allfit:
                    display_pts = update_count
                else:
                    display_pts = max(int(right) - int(left), setting.display_pts)
                if not syncing:
                    r_offset = update_count - int(right)
                else:
                    r_offset = 0
                right = update_count - r_offset
                if not allfit:
                    left = max(0, right - display_pts)
                else:
                    left = 0
                self.ui.horizontalSlider.setRange(0, update_count)
            else:
                display_pts = update_count
                r_offset = 0
                syncing = True
                allfit = False
                left = 0
                right = update_count
                self.ui.horizontalSlider.setEnabled(False)
                self.ui.horizontalSlider.setRange(0, 10)
            if syncing:
                self.ui.horizontalSlider.setValue((left, update_count))
            data1, time1, start_index1, to_index1, max1, min1, avg1 = self.get_data(
                type1, display_pts, r_offset
            )
            data2, time2, start_index2, to_index2, max2, min2, avg2 = self.get_data(
                type2, display_pts, r_offset
            )
        self.ui.labelBufferSize.setText(
            f"{update_count / self.data.data_length * 100:.1f}%"
        )
        self.ui.labelBufferSize.setToolTip(
            self.tr("数据缓冲区占用率") + f"\n{update_count} / {self.data.data_length}"
        )
        self.ui.labelDisplayRange.setText(str(display_pts))
        if update_count > self.data.data_length * 0.95:
            set_color(
                self.ui.labelBufferSize,
                setting.get_color("general_yellow"),
            )

        _ = self._typename_dict.get(type1)
        if data1 is not None and data1.size > 0:
            self.curve1.setData(x=time1, y=data1)
            text1 = f"{_}avg: {float_str(avg1)}  {_}max: {float_str(max1)}  {_}min: {float_str(min1)}  {_}pp: {float_str(max1 - min1)}"
        else:
            self.curve1.setData(x=[], y=[])
            text1 = f"{_}avg: N/A  {_}max: N/A  {_}min: N/A  {_}pp: N/A"
        _ = self._typename_dict.get(type2)
        if data2 is not None and data2.size > 0:
            self.curve2.setData(x=time2, y=data2)
            text2 = f"{_}avg: {float_str(avg2)}  {_}max: {float_str(max2)}  {_}min: {float_str(min2)}  {_}pp: {float_str(max2 - min2)}"
        else:
            self.curve2.setData(x=[], y=[])
            text2 = f"{_}avg: N/A  {_}max: N/A  {_}min: N/A  {_}pp: N/A"
        if data1 is not None and data2 is not None:
            text = text1 + "  |  " + text2
        elif data1 is not None:
            text = text1
        elif data2 is not None:
            text = text2
        else:
            text = "No Info"
        self.ui.labelGraphInfo.setText(text)
        if self._graph_auto_scale_flag:
            if data1 is not None and time1.size != 0:
                if max1 != np.inf and min1 != -np.inf:
                    add1 = max(0.01, (max1 - min1) * 0.05)
                    self.ui.widgetGraph1.setYRange(min1 - add1, max1 + add1)
                    self.ui.widgetGraph1.setXRange(
                        time1[start_index1], time1[to_index1 - 1]
                    )
            if data2 is not None and time2.size != 0:
                if max2 != np.inf and min2 != -np.inf:
                    add2 = max(0.01, (max2 - min2) * 0.05)
                    self.ui.widgetGraph2.setYRange(min2 - add2, max2 + add2)
                    self.ui.widgetGraph2.setXRange(
                        time2[start_index2], time2[to_index2 - 1]
                    )

    def set_graph1_data(self, text, skip_update=False):
        if text == self.tr("无"):
            self.ui.widgetGraph1.hide()
            return
        self.ui.widgetGraph1.show()
        self.ui.widgetGraph1.setLabel("left", text, units=self._graph_units_dict[text])
        if not skip_update and self.draw_graph_timer.isActive():  # force update axis
            self.ui.widgetGraph1.setYRange(0, 0)
            self.ui.widgetGraph2.setYRange(0, 0)
            self.draw_graph()

    def set_graph2_data(self, text, skip_update=False):
        if text == self.tr("无"):
            self.ui.widgetGraph2.hide()
            return
        self.ui.widgetGraph2.show()
        self.ui.widgetGraph2.setLabel("left", text, units=self._graph_units_dict[text])
        if not skip_update and self.draw_graph_timer.isActive():
            self.ui.widgetGraph1.setYRange(0, 0)
            self.ui.widgetGraph2.setYRange(0, 0)
            self.draw_graph()

    @QtCore.pyqtSlot()
    def on_btnGraphClear_clicked(self, _=None, skip_confirm=False):
        if not skip_confirm and not CustomMessageBox.question(
            self,
            self.tr("警告"),
            self.tr("确定要清空数据缓冲区吗？"),
        ):
            return
        with self.data.sync_lock:
            self.data.voltages = np.zeros(self.data.data_length, np.float64)
            self.data.currents = np.zeros(self.data.data_length, np.float64)
            self.data.powers = np.zeros(self.data.data_length, np.float64)
            self.data.resistances = np.zeros(self.data.data_length, np.float64)
            self.data.times = np.zeros(self.data.data_length, np.float64)
            self.data.update_count = 0
            t = time.perf_counter()
            self.data.start_time = t
            self.data.last_time = t

        self.curve1.setData(x=[], y=[])
        self.curve2.setData(x=[], y=[])
        set_color(self.ui.labelBufferSize, None)

    @QtCore.pyqtSlot()
    def on_btnGraphKeep_clicked(self):
        self.graph_keep_flag = not self.graph_keep_flag
        if self.graph_keep_flag:
            self.ui.btnGraphKeep.setText(self.tr("解除"))
            self.ui.comboGraph1Data.setEnabled(False)
            self.ui.comboGraph2Data.setEnabled(False)
        else:
            self.ui.btnGraphKeep.setText(self.tr("保持"))
            self.ui.comboGraph1Data.setEnabled(True)
            self.ui.comboGraph2Data.setEnabled(True)
        mouse_enabled = self.graph_keep_flag or (not self._graph_auto_scale_flag)
        self.ui.frameGraphControl.setEnabled(not mouse_enabled)
        self.ui.widgetGraph1.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)
        self.ui.widgetGraph2.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)

    @QtCore.pyqtSlot()
    def on_btnGraphAutoScale_clicked(self):
        self._graph_auto_scale_flag = not self._graph_auto_scale_flag
        if self._graph_auto_scale_flag:
            self.ui.btnGraphAutoScale.setText(self.tr("适应"))
        else:
            self.ui.btnGraphAutoScale.setText(self.tr("手动"))
        mouse_enabled = self.graph_keep_flag or (not self._graph_auto_scale_flag)
        self.ui.frameGraphControl.setEnabled(not mouse_enabled)
        self.ui.widgetGraph1.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)
        self.ui.widgetGraph2.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)

    @QtCore.pyqtSlot()
    def on_btnGraphRecord_clicked(self):
        self.graph_record_flag = not self.graph_record_flag
        if self.graph_record_flag:
            self.graph_record_data = RecordData()
            time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            self.graph_record_filename = os.path.join(
                ARG_PATH, f"record_{time_str}.csv"
            )
            self.ui.btnGraphRecord.setText(self.tr("停止"))
            self.graph_record_save_timer.start(30000)
        else:
            self.graph_record_save_timer.stop()
            self.graph_record_data.to_csv(self.graph_record_filename)
            self.graph_record_data = RecordData()

            CustomMessageBox(
                self,
                self.tr("录制完成"),
                self.tr("数据已保存至：")
                + f"\n{os.path.basename(self.graph_record_filename)}",
                additional_actions=[
                    (
                        self.tr("打开文件路径"),
                        partial(self._handle_open_filebase, self.graph_record_filename),
                    ),
                ],
            )
            self.ui.btnGraphRecord.setText(self.tr("录制"))

    @QtCore.pyqtSlot()
    def on_btnGraphDump_clicked(self):
        path, ok = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.tr("保存数据"),
            os.path.join(ARG_PATH, "data_buffer_dump.csv"),
            "CSV Files (*.csv)",
        )
        if not ok:
            return
        with self.data.sync_lock:
            voltages = self.data.voltages[: self.data.update_count]
            currents = self.data.currents[: self.data.update_count]
            powers = self.data.powers[: self.data.update_count]
            resistances = self.data.resistances[: self.data.update_count]
            times = self.data.times[: self.data.update_count]
            np.savetxt(
                path,
                np.c_[times, voltages, currents, powers, resistances],
                delimiter=",",
                header="time/s,voltage/V,current/A,power/W,resistance/ohm",
                comments="",
                fmt="%f",
            )
        CustomMessageBox(
            self,
            self.tr("保存完成"),
            self.tr("数据已保存至：") + f"\n{os.path.basename(path)}",
            additional_actions=[
                (
                    self.tr("打开文件路径"),
                    partial(self._handle_open_filebase, path),
                ),
            ],
        )

    def _handle_open_filebase(self, file):
        folder = os.path.dirname(file)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder))
        return True

    def graph_record_save(self):
        if self.graph_record_flag:
            self.graph_record_data.to_csv(self.graph_record_filename)
        else:
            self.graph_record_save_timer.stop()

    ######### 辅助功能-预设组 #########

    def set_preset(self, _):
        text = self.ui.comboPreset.currentText()
        if not text or not text[1].isdigit():
            return
        voltage, current = setting.presets[text[1]]
        self.v_set = voltage
        self.i_set = current
        self.ui.comboPreset.setCurrentIndex(0)

    def refresh_preset(self):
        idx = self.ui.comboPreset.currentIndex()
        self.ui.comboPreset.clear()
        self.ui.comboPreset.addItem("[>] " + self.tr("选择预设"))
        self.ui.comboPreset.addItems(
            [f"[{k}] {v[0]:06.3f}V {v[1]:06.3f}A" for k, v in setting.presets.items()]
        )
        self.ui.comboPreset.setCurrentIndex(idx)
        self.ui.comboPreset.setItemData(0, 0, QtCore.Qt.UserRole - 1)
        idx = self.ui.comboPresetEdit.currentIndex()
        self.ui.comboPresetEdit.clear()
        self.ui.comboPresetEdit.addItems(
            [f"Preset-{k}" for k, v in setting.presets.items()]
        )
        self.ui.comboPresetEdit.setCurrentIndex(idx)

    @QtCore.pyqtSlot()
    def on_btnPresetSave_clicked(self):
        preset = self.ui.comboPresetEdit.currentText()
        if not preset:
            return
        preset = preset.split("-")[1]
        v_set = self.ui.spinBoxPresetVoltage.value()
        i_set = self.ui.spinBoxPresetCurrent.value()
        try:
            setting.presets[preset] = [v_set, i_set]
            setting.save(SETTING_FILE)
            self.ui.btnPresetSave.setText(self.tr("保存成功"))
            self.refresh_preset()
        except Exception:
            logger.exception(self.tr("保存预设失败"))
            self.ui.btnPresetSave.setText(self.tr("保存失败"))
        QtCore.QTimer.singleShot(
            1000, lambda: self.ui.btnPresetSave.setText(self.tr("保存"))
        )

    def get_preset(self, text):
        if "-" not in text:
            return
        voltage, current = setting.presets[text.split("-")[1]]
        self.ui.spinBoxPresetVoltage.setValue(voltage)
        self.ui.spinBoxPresetCurrent.setValue(current)

    ######### 辅助功能-预设组(硬件) #########

    def set_preset_hw(self, _):
        if self.api is not None:
            preset = self.ui.comboPreset2.currentIndex()
            if preset == 0:
                preset = self.preset
                self.ui.comboPreset2.setCurrentIndex(preset)
                return
            self.action_signal.emit("use_preset", {"index": preset})

    def refresh_preset_hw(self):
        self.ui.comboPreset2.clear()
        for i in range(0, 10):
            self.ui.comboPreset2.addItem(f"Group-{i}")
        self.ui.comboPresetEdit2.clear()
        self.ui.comboPresetEdit2.addItems([f"Group-{i}" for i in range(0, 10)])

    @QtCore.pyqtSlot()
    def on_btnPreset2Save_clicked(self):
        if self.api is None:
            return
        idx = self.ui.comboPresetEdit2.currentIndex()
        v_set = self.ui.spinBoxPreset2Voltage.value()
        i_set = self.ui.spinBoxPreset2Current.value()
        ovp = self.ui.spinBoxPreset2OVP.value()
        ocp = self.ui.spinBoxPreset2OCP.value()
        try:
            self.api.set_preset(idx, v_set, i_set, ovp, ocp)
            self.ui.btnPreset2Save.setText(self.tr("保存成功"))
        except Exception:
            logger.exception(self.tr("保存预设失败"))
            self.ui.btnPreset2Save.setText(self.tr("保存失败"))
        QtCore.QTimer.singleShot(
            1000, lambda: self.ui.btnPreset2Save.setText(self.tr("保存"))
        )

    def get_preset_hw(self, _):
        if self.api is not None:
            text = self.ui.comboPresetEdit2.currentText()
            if "-" not in text:
                return
            idx = int(text.split("-")[1])
            preset = self.api.get_preset(idx)
            self.ui.spinBoxPreset2Voltage.setValue(preset["v_set"])
            self.ui.spinBoxPreset2Current.setValue(preset["i_set"])
            self.ui.spinBoxPreset2OVP.setValue(preset["ovp"])
            self.ui.spinBoxPreset2OCP.setValue(preset["ocp"])

    ######### 辅助功能-参数扫描 #########

    _sweep_response_type = ""
    _sweep_response_data_y = []
    _sweep_response_data_x = []
    _sweep_response_x_label = ""
    _sweep_response_y_label = ""
    _sweep_response_x_unit = ""
    _sweep_response_y_unit = ""
    _sweep_flag = False

    @QtCore.pyqtSlot()
    def on_btnSweep_clicked(self):
        if self.func_sweep_timer.isActive():
            self.stop_func_sweep()
        else:
            self._sweep_target = self.ui.comboSweepTarget.currentText()
            self._sweep_start = self.ui.spinBoxSweepStart.value()
            self._sweep_stop = self.ui.spinBoxSweepStop.value()
            self._sweep_step = self.ui.spinBoxSweepStep.value()
            self._sweep_delay = self.ui.spinBoxSweepDelay.value()
            try:
                assert self._sweep_step > 0
                assert self._sweep_start != self._sweep_stop
                assert self._sweep_delay > 0
            except Exception:
                self.ui.btnSweep.setText(self.tr("非法参数"))
                QtCore.QTimer.singleShot(
                    1000, lambda: self.ui.btnSweep.setText(self.tr("功能已关闭"))
                )
                return

            self._sweep_temp = None
            if self.ui.comboSweepRecord.currentIndex() == 0:
                self._sweep_response_type = ""
            else:
                self._sweep_response_type = self.ui.comboSweepRecord.currentText()
                units_dict = {
                    self.tr("电压"): "V",
                    self.tr("电流"): "A",
                    self.tr("功率"): "W",
                    self.tr("阻值"): "Ω",
                }
                self._sweep_response_x_label = self._sweep_target
                self._sweep_response_y_label = self._sweep_response_type
                self._sweep_response_x_unit = units_dict[self._sweep_target]
                self._sweep_response_y_unit = units_dict[self._sweep_response_type]
                self._sweep_response_data_x = []
                self._sweep_response_data_y = []

            self._sweep_flag = True
            self.ui.btnSweep.setText(self.tr("功能已开启"))
            if self._sweep_target == self.tr("电压"):
                self.ui.spinBoxVoltage.setEnabled(False)
            elif self._sweep_target == self.tr("电流"):
                self.ui.spinBoxCurrent.setEnabled(False)
            self.ui.scrollAreaSweep.setEnabled(False)

            self.v_set = self._sweep_start
            self.func_sweep_timer.start(round(self._sweep_delay * 1000))

    @QtCore.pyqtSlot()
    def on_btnSweepShowRecord_clicked(self):
        if not self._sweep_response_type:
            CustomMessageBox(self, self.tr("错误"), self.tr("扫描响应记录为空"))
            return
        len_y = len(self._sweep_response_data_y)
        len_x = len(self._sweep_response_data_x)
        min_len = min(len_x, len_y)
        MainWindow.display_data_signal.emit(
            self._sweep_response_data_x[:min_len],
            self._sweep_response_data_y[:min_len],
            self._sweep_response_x_label,
            self._sweep_response_y_label,
            self._sweep_response_x_unit,
            self._sweep_response_y_unit,
            self.tr("扫描响应结果曲线"),
            False,
        )

    @QtCore.pyqtSlot(str)
    def on_comboSweepTarget_currentTextChanged(self, text):
        if text == self.tr("电压"):
            self.ui.spinBoxSweepStart.setSuffix("V")
            self.ui.spinBoxSweepStop.setSuffix("V")
            self.ui.spinBoxSweepStep.setSuffix("V")
            self.ui.spinBoxSweepStart.setRange(0, 30)
            self.ui.spinBoxSweepStop.setRange(0, 30)
            self.ui.spinBoxSweepStep.setRange(0.001, 30)
        elif text == self.tr("电流"):
            self.ui.spinBoxSweepStart.setSuffix("A")
            self.ui.spinBoxSweepStop.setSuffix("A")
            self.ui.spinBoxSweepStep.setSuffix("A")
            self.ui.spinBoxSweepStart.setRange(0, 10)
            self.ui.spinBoxSweepStop.setRange(0, 10)
            self.ui.spinBoxSweepStep.setRange(0.001, 10)

    def stop_func_sweep(self):
        self.func_sweep_timer.stop()
        self.ui.btnSweep.setText(self.tr("功能已关闭"))
        if self._sweep_target == self.tr("电压"):
            self.ui.spinBoxVoltage.setEnabled(True)
        elif self._sweep_target == self.tr("电流"):
            self.ui.spinBoxCurrent.setEnabled(True)
        self.ui.scrollAreaSweep.setEnabled(True)

    def func_sweep(self):
        if self._sweep_response_type:
            _data_sources = {
                self.tr("电压"): self.data.voltages,
                self.tr("电流"): self.data.currents,
                self.tr("功率"): self.data.powers,
                self.tr("阻值"): self.data.resistances,
            }
            self._sweep_response_data_x.append(
                _data_sources[self._sweep_response_x_label][self.data.update_count - 1]
            )
            self._sweep_response_data_y.append(
                _data_sources[self._sweep_response_y_label][self.data.update_count - 1]
            )

        if not self._sweep_flag:
            self.stop_func_sweep()
            return

        if self._sweep_temp is None:
            self._sweep_temp = self._sweep_start
        else:
            if self._sweep_start <= self._sweep_stop:
                self._sweep_temp += self._sweep_step
            else:
                self._sweep_temp -= self._sweep_step

        if (
            self._sweep_start > self._sweep_stop
            and self._sweep_temp <= self._sweep_stop
        ) or (
            self._sweep_start <= self._sweep_stop
            and self._sweep_temp >= self._sweep_stop
        ):
            self._sweep_temp = self._sweep_stop
            self._sweep_flag = False
            self.stop_func_sweep()

        if self._sweep_target == self.tr("电压"):
            self.v_set = self._sweep_temp
        elif self._sweep_target == self.tr("电流"):
            self.i_set = self._sweep_temp

    ######### 辅助功能-发生器 #########

    @QtCore.pyqtSlot()
    def on_btnWaveGen_clicked(self):
        if self.func_wave_gen_timer.isActive():
            self.stop_func_wave_gen()
        else:
            self._wavegen_type = self.ui.comboWaveGenType.currentText()
            self._wavegen_period = self.ui.spinBoxWaveGenPeriod.value()
            self._wavegen_highlevel = self.ui.spinBoxWaveGenHigh.value()
            self._wavegen_lowlevel = self.ui.spinBoxWaveGenLow.value()
            self._wavegen_loopfreq = self.ui.spinBoxWaveGenLoopFreq.value()
            try:
                assert self._wavegen_highlevel > self._wavegen_lowlevel
                assert self._wavegen_period > 0
                assert self._wavegen_loopfreq > 0
            except Exception:
                self.ui.btnWaveGen.setText(self.tr("非法参数"))
                QtCore.QTimer.singleShot(
                    1000, lambda: self.ui.btnWaveGen.setText(self.tr("功能已关闭"))
                )
                return
            self.ui.btnWaveGen.setText(self.tr("功能已开启"))
            self.ui.spinBoxWaveGenLoopFreq.setEnabled(False)
            self.ui.spinBoxVoltage.setEnabled(False)
            self._wavegen_start_time = 0

            self.v_set = self._wavegen_lowlevel
            self._wavegen_start_time = time.perf_counter()
            self.func_wave_gen_timer.start(round(1000 / self._wavegen_loopfreq))
            self.v_set = self._wavegen_lowlevel

    def stop_func_wave_gen(self):
        self.func_wave_gen_timer.stop()
        self.ui.btnWaveGen.setText(self.tr("功能已关闭"))
        self.ui.spinBoxWaveGenLoopFreq.setEnabled(True)
        self.ui.spinBoxVoltage.setEnabled(True)

    def set_wavegen_type(self, _):
        self._wavegen_type = self.ui.comboWaveGenType.currentText()

    @QtCore.pyqtSlot()
    def on_spinBoxWaveGenPeriod_editingFinished(self):
        self._wavegen_period = self.ui.spinBoxWaveGenPeriod.value()

    @QtCore.pyqtSlot()
    def on_spinBoxWaveGenHigh_editingFinished(self):
        self._wavegen_highlevel = self.ui.spinBoxWaveGenHigh.value()

    @QtCore.pyqtSlot()
    def on_spinBoxWaveGenLow_editingFinished(self):
        self._wavegen_lowlevel = self.ui.spinBoxWaveGenLow.value()

    def func_wave_gen(self):
        t = time.perf_counter() - self._wavegen_start_time
        if self._wavegen_type == self.tr("正弦波"):
            voltage = (
                self._wavegen_lowlevel
                + (self._wavegen_highlevel - self._wavegen_lowlevel)
                * (math.sin(2 * math.pi / self._wavegen_period * t) + 1.0)
                / 2
            )
        elif self._wavegen_type == self.tr("方波"):
            voltage = (
                self._wavegen_highlevel
                if math.sin(2 * math.pi / self._wavegen_period * t) > 0
                else self._wavegen_lowlevel
            )
        elif self._wavegen_type == self.tr("三角波"):
            mul = (t / self._wavegen_period) % 2
            mul = mul if mul < 1 else 2 - mul
            voltage = (
                self._wavegen_lowlevel
                + (self._wavegen_highlevel - self._wavegen_lowlevel) * mul
            )
        elif self._wavegen_type == self.tr("锯齿波"):
            voltage = (self._wavegen_highlevel - self._wavegen_lowlevel) * (
                (t / self._wavegen_period) % 1
            ) + self._wavegen_lowlevel
        elif self._wavegen_type == self.tr("噪音"):
            voltage = random.uniform(self._wavegen_lowlevel, self._wavegen_highlevel)
        else:
            voltage = 0
        voltage = max(
            min(voltage, self._wavegen_highlevel), self._wavegen_lowlevel
        )  # 限幅
        self.v_set = voltage

    ######### 辅助功能-功率保持 #########

    @QtCore.pyqtSlot()
    def on_btnKeepPower_clicked(self):
        if self.func_keep_power_timer.isActive():
            self.stop_func_keep_power()
        else:
            self._keep_power_target = self.ui.spinBoxKeepPowerSet.value()
            self._keep_power_loopfreq = self.ui.spinBoxKeepPowerLoopFreq.value()
            self._keep_power_pid_i = self.ui.spinBoxKeepPowerPi.value()
            self._keep_power_pid_max_v = self.ui.spinBoxKeepPowerMaxV.value()
            try:
                assert self._keep_power_loopfreq > 0
                assert self._keep_power_pid_i > 0
            except Exception:
                self.ui.btnKeepPower.setText(self.tr("非法参数"))
                QtCore.QTimer.singleShot(
                    1000, lambda: self.ui.btnKeepPower.setText(self.tr("功能已关闭"))
                )
                return
            self._keep_power_pid = PID(
                0,
                self._keep_power_pid_i,
                0,
                setpoint=self._keep_power_target,
                auto_mode=False,
            )
            self._keep_power_pid.output_limits = (0, self._keep_power_pid_max_v)
            self._keep_power_pid.set_auto_mode(True, last_output=self.v_set)
            self.func_keep_power_timer.start(round(1000 / self._keep_power_loopfreq))
            self.ui.btnKeepPower.setText(self.tr("功能已开启"))
            self.ui.spinBoxVoltage.setEnabled(False)
            self.ui.spinBoxKeepPowerLoopFreq.setEnabled(False)

    def stop_func_keep_power(self):
        self.func_keep_power_timer.stop()
        self.ui.btnKeepPower.setText(self.tr("功能已关闭"))
        self.ui.spinBoxVoltage.setEnabled(True)
        self.ui.spinBoxKeepPowerLoopFreq.setEnabled(True)

    def func_keep_power(self):
        if not self.output_state:
            if self._keep_power_pid.auto_mode:
                self._keep_power_pid.set_auto_mode(False)
            voltage = 0
        else:
            if not self._keep_power_pid.auto_mode:
                self._keep_power_pid.set_auto_mode(True, last_output=self.v_set)
            voltage = self._keep_power_pid(self.data.powers[self.data.update_count - 1])
        self.v_set = voltage

    @QtCore.pyqtSlot()
    def on_spinBoxKeepPowerSet_editingFinished(self):
        self._keep_power_target = self.ui.spinBoxKeepPowerSet.value()
        if self.func_keep_power_timer.isActive():
            self._keep_power_pid.setpoint = self._keep_power_target

    @QtCore.pyqtSlot()
    def on_spinBoxKeepPowerPi_editingFinished(self):
        self._keep_power_pid_i = self.ui.spinBoxKeepPowerPi.value()
        if self.func_keep_power_timer.isActive():
            self._keep_power_pid.tunings = (0, self._keep_power_pid_i, 0)

    @QtCore.pyqtSlot()
    def on_spinBoxKeepPowerMaxV_editingFinished(self):
        self._keep_power_pid_max_v = self.ui.spinBoxKeepPowerMaxV.value()
        if self.func_keep_power_timer.isActive():
            self._keep_power_pid.output_limits = (0, self._keep_power_pid_max_v)

    ######### 辅助功能-电池模拟 #########

    _battery_models = {}
    _bat_sim_soc = []
    _bat_sim_voltage = []
    _bat_sim_total_energy = 0
    _bat_sim_used_energy = 0
    _bat_sim_stop_energy = 0
    _bat_sim_cells = 1
    _bat_sim_internal_r = 0.0
    _bat_sim_last_e_temp = 0
    _bat_sim_start_time = 0

    def load_battery_model(self, path):
        csv = np.loadtxt(path, delimiter=",", skiprows=1)
        csv_name = os.path.basename(os.path.splitext(path)[0])
        soc = csv[:, 0]
        voltage = csv[:, 1]
        self._battery_models[csv_name] = (soc, voltage)
        if csv_name not in [
            self.ui.comboBatSimCurve.itemText(i)
            for i in range(self.ui.comboBatSimCurve.count())
        ]:
            self.ui.comboBatSimCurve.addItem(csv_name)
        self.ui.comboBatSimCurve.setCurrentText(csv_name)

    @QtCore.pyqtSlot()
    def on_btnBatSimLoad_clicked(self):
        path, ok = QtWidgets.QFileDialog.getOpenFileName(
            self, self.tr("打开"), "", self.tr("CSV文件 (*.csv)")
        )
        if path == "" or not ok:
            return
        self.load_battery_model(path)

    @QtCore.pyqtSlot()
    def on_btnBatSimPreview_clicked(self):
        curve_name = self.ui.comboBatSimCurve.currentText()
        if curve_name not in self._battery_models:
            return
        soc, voltage = self._battery_models[curve_name]
        new_soc = np.arange(0, 100 + 1e-9, 0.1)
        new_voltage = np.interp(new_soc, soc, voltage)
        self.display_data_signal.emit(
            new_soc.tolist(),
            new_voltage.tolist(),
            self.tr("SOC"),
            self.tr("电压"),
            "%",
            "V",
            f"{curve_name} Voltage-SOC (State of Charge) Curve",
            True,
        )

    def set_batsim_widget_enabled(self, enabled):
        for item in self.ui.scrollAreaBatSim.findChildren(QtWidgets.QPushButton):
            if item is not self.ui.btnBatSimPreview:
                item.setEnabled(enabled)
        for item in self.ui.scrollAreaBatSim.findChildren(QtWidgets.QDoubleSpinBox):
            item.setEnabled(enabled)
        for item in self.ui.scrollAreaBatSim.findChildren(QtWidgets.QComboBox):
            item.setEnabled(enabled)

    @QtCore.pyqtSlot()
    def on_btnBatSim_clicked(self):
        if self.func_bat_sim_timer.isActive():
            self.func_bat_sim_timer.stop()
            self.set_batsim_widget_enabled(True)
            self.ui.btnBatSim.setText(self.tr("功能已关闭"))
        else:
            curve_name = self.ui.comboBatSimCurve.currentText()
            if curve_name not in self._battery_models:
                return
            self._bat_sim_soc = self._battery_models[curve_name][0]
            self._bat_sim_voltage = self._battery_models[curve_name][1]
            self._bat_sim_cells = self.ui.spinBoxBatSimCells.value()
            self._bat_sim_total_energy = (
                self.ui.spinBoxBatSimCap.value() * 3600 * self._bat_sim_cells
            )  # Wh->J
            self._bat_sim_used_energy = (
                1 - self.ui.spinBoxBatSimCurrent.value() / 100
            ) * self._bat_sim_total_energy
            self._bat_sim_stop_energy = self._bat_sim_total_energy - (
                self.ui.spinBoxBatSimStop.value() / 100 * self._bat_sim_total_energy
            )
            self._bat_sim_internal_r = (
                self.ui.spinBoxBatSimRes.value() / 1000
            )  # mOhm->Ohm
            self._bat_sim_last_e_temp = self.continuous_energy_counter
            self.ui.labelBatSimTime.setText("Discharge Time: 00:00:00")
            self.ui.btnBatSim.setText(self.tr("功能已开启"))
            self.set_batsim_widget_enabled(False)
            self.display_data_signal.emit(
                self._bat_sim_soc.tolist(),
                self._bat_sim_voltage.tolist(),
                self.tr("SOC"),
                self.tr("电压"),
                "%",
                "V",
                f"{curve_name} Battery Simulation Real-Time Curve",
                True,
            )

            self.v_set = 0
            self.func_bat_sim_timer.start(
                round(1000 / self.ui.spinBoxBatSimLoopFreq.value())
            )
            self._bat_sim_start_time = time.perf_counter()

    def func_bat_sim(self):
        add_e = self.continuous_energy_counter - self._bat_sim_last_e_temp
        self._bat_sim_last_e_temp += add_e
        self._bat_sim_used_energy += add_e
        if self._bat_sim_used_energy >= self._bat_sim_stop_energy:
            self.output_state = False
            self.on_btnBatSim_clicked()
        new_percent = (
            (self._bat_sim_total_energy - self._bat_sim_used_energy)
            / self._bat_sim_total_energy
            * 100
        )
        self.ui.spinBoxBatSimCurrent.setValue(new_percent)
        new_volt = np.interp(new_percent, self._bat_sim_soc, self._bat_sim_voltage)
        self.v_set = (
            new_volt
            - self._bat_sim_internal_r * self.data.currents[self.data.update_count - 1]
        ) * self._bat_sim_cells
        self.highlight_point_signal.emit(new_percent, new_volt)
        self.ui.labelBatSimTime.setText(
            "Discharge Time: "
            + time.strftime(
                "%H:%M:%S", time.gmtime(time.perf_counter() - self._bat_sim_start_time)
            )
        )

    ######### 辅助功能-序列 #########

    def seq_btn_disable(self):
        self.ui.btnSeqSave.hide()
        self.ui.btnSeqLoad.hide()
        self.ui.btnSeqSingle.hide()
        self.ui.btnSeqLoop.hide()
        self.ui.btnSeqDelay.hide()
        self.ui.btnSeqWaitTime.hide()
        self.ui.btnSeqVoltage.hide()
        self.ui.btnSeqCurrent.hide()
        self.ui.listSeq.setEnabled(False)
        self.ui.btnSeqStop.show()

    def seq_btn_enable(self):
        self.ui.btnSeqSave.show()
        self.ui.btnSeqLoad.show()
        self.ui.btnSeqSingle.show()
        self.ui.btnSeqLoop.show()
        self.ui.btnSeqDelay.show()
        self.ui.btnSeqWaitTime.show()
        self.ui.btnSeqVoltage.show()
        self.ui.btnSeqCurrent.show()
        self.ui.listSeq.setEnabled(True)
        self.ui.btnSeqStop.hide()

    @QtCore.pyqtSlot()
    def on_btnSeqSingle_clicked(self):
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        self.seq_btn_disable()
        self.start_seq(loop=False)
        if not self.output_state:
            self.ui.btnOutput.click()

    @QtCore.pyqtSlot()
    def on_btnSeqLoop_clicked(self):
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        self.seq_btn_disable()
        self.start_seq(loop=True)
        if not self.output_state:
            self.ui.btnOutput.click()

    @QtCore.pyqtSlot()
    def on_btnSeqStop_clicked(self):
        self.func_seq_timer.stop()
        self.seq_btn_enable()

    # listSeq 删除
    def seq_del_item(self):
        row = self.ui.listSeq.currentRow()
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        if row == -1:
            row = cnt - 1
        self.ui.listSeq.takeItem(row)
        self.ui.listSeq.setCurrentRow(max(row - 1, 0))

    def seq_edit_item(self):
        row = self.ui.listSeq.currentRow()
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        if row == -1:
            return
        item = self.ui.listSeq.item(row)
        text = item.text()
        if text.split()[0] == "DELAY":
            delay, ok = CustomInputDialog.getInt(
                self,
                self.tr("编辑动作"),
                self.tr("请输入延时时间:"),
                default_value=int(text.split()[1]),
                min_value=0,
                max_value=100000,
                step=1,
                suffix="ms",
            )
            if not ok:
                return
            item.setText(f"DELAY {delay} ms")
        elif text.split()[0] == "WAIT":
            default_value = QtCore.QDateTime.fromString(
                " ".join(text.split()[1:]), "%Y-%m-%d %H:%M:%S"
            )
            wait_time, ok = CustomInputDialog.getDateTime(
                self,
                self.tr("编辑动作"),
                self.tr("请输入等待时间:"),
                default_value=default_value,
            )
            if not ok:
                return
            item.setText(f"WAIT  {wait_time.toString('yyyy-MM-dd HH:mm:ss')}")
        elif text.split()[0] == "SET-V":
            voltage, ok = CustomInputDialog.getDouble(
                self,
                self.tr("编辑动作"),
                self.tr("请输入电压值(0=关断):"),
                default_value=float(text.split()[1]),
                min_value=0,
                max_value=30,
                step=0.001,
                decimals=3,
                suffix="V",
            )
            if not ok:
                return
            item.setText(f"SET-V {voltage:.3f} V")
        elif text.split()[0] == "SET-I":
            current, ok = CustomInputDialog.getDouble(
                self,
                self.tr("编辑动作"),
                self.tr("请输入电流值:"),
                default_value=float(text.split()[1]),
                min_value=0,
                max_value=10,
                step=0.001,
                decimals=3,
                suffix="A",
            )
            if not ok:
                return
            item.setText(f"SET-I {current:.3f} A")
        else:
            CustomMessageBox(
                self,
                self.tr("错误"),
                self.tr("无法识别动作"),
            )

    def seq_clear_all(self):
        if CustomMessageBox.question(
            self,
            self.tr("警告"),
            self.tr("确定要清空序列吗？"),
        ):
            self.ui.listSeq.clear()

    # listSeq 右键菜单 (listSeq)
    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_listSeq_customContextMenuRequested(self, pos):
        row = self.ui.listSeq.currentRow()
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        if row == -1:
            return
        menu = QtWidgets.QMenu()
        menu.addAction(self.tr("编辑"), lambda: self.seq_edit_item())
        menu.addAction(self.tr("删除"), lambda: self.seq_del_item())
        menu.addAction(self.tr("清空"), lambda: self.seq_clear_all())
        menu.exec_(QtGui.QCursor.pos())

    # 双击修改
    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_listSeq_itemDoubleClicked(self, item):
        self.seq_edit_item()

    def seq_set_item_font(self, index):
        item = self.ui.listSeq.item(index)
        sfont = QtGui.QFont()
        sfont.setFamily("Sarasa Fixed SC SemiBold")
        sfont.setPointSize(10)
        item.setFont(sfont)

    @QtCore.pyqtSlot()
    def on_btnSeqDelay_clicked(self):
        row = self.ui.listSeq.currentRow()
        delay, ok = CustomInputDialog.getInt(
            self,
            self.tr("添加动作"),
            self.tr("请输入延时时间:"),
            default_value=1000,
            min_value=0,
            max_value=100000,
            step=1,
            suffix="ms",
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"DELAY {delay} ms")
        self.ui.listSeq.setCurrentRow(row + 1)
        self.seq_set_item_font(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqWaitTime_clicked(self):
        row = self.ui.listSeq.currentRow()
        wait_time, ok = CustomInputDialog.getDateTime(
            self,
            self.tr("添加动作"),
            self.tr("请输入等待时间:") + "\n" + self.tr("格式: 年-月-日 时:分:秒"),
        )
        if not ok:
            return
        wait_time_str = wait_time.toString("yyyy-MM-dd HH:mm:ss")
        self.ui.listSeq.insertItem(row + 1, f"WAIT  {wait_time_str}")
        self.ui.listSeq.setCurrentRow(row + 1)
        self.seq_set_item_font(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqVoltage_clicked(self):
        row = self.ui.listSeq.currentRow()
        voltage, ok = CustomInputDialog.getDouble(
            self,
            self.tr("添加动作"),
            self.tr("请输入电压值(0=关断):"),
            default_value=5,
            min_value=0,
            max_value=30,
            step=0.001,
            decimals=3,
            suffix="V",
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"SET-V {voltage:.3f} V")
        self.ui.listSeq.setCurrentRow(row + 1)
        self.seq_set_item_font(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqCurrent_clicked(self):
        row = self.ui.listSeq.currentRow()
        current, ok = CustomInputDialog.getDouble(
            self,
            self.tr("添加动作"),
            self.tr("请输入电流值:"),
            default_value=1,
            min_value=0,
            max_value=10,
            step=0.001,
            decimals=3,
            suffix="A",
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"SET-I {current:.3f} A")
        self.ui.listSeq.setCurrentRow(row + 1)
        self.seq_set_item_font(row + 1)

    def switch_to_seq(self, index) -> bool:
        if index > self._seq_cnt:
            return False
        item = self.ui.listSeq.item(index)
        if item is None:
            return False
        self._seq_index = index
        self.ui.listSeq.setCurrentRow(index)
        text = item.text()
        self._seq_type = text.split()[0]
        if self._seq_type == "WAIT":
            self._seq_value = datetime.datetime.strptime(
                " ".join(text.split()[1:]), "%Y-%m-%d %H:%M:%S"
            )
        else:
            self._seq_value = float(text.split()[1])
        if self._seq_type in ("DELAY", "WAIT") or self._seq_index == 0:
            self._seq_time = time.perf_counter()
        return True

    def start_seq(self, loop=False):
        self._seq_loop = loop
        self._seq_index = 0
        self._seq_cnt = self.ui.listSeq.count()
        self.switch_to_seq(0)
        self.func_seq_timer.start(1)

    def func_seq(self):
        now = time.perf_counter()
        if self._seq_type == "DELAY":
            if now - self._seq_time < self._seq_value / 1000:
                return
        elif self._seq_type == "WAIT":
            now = datetime.datetime.now()
            if now < self._seq_value:
                return
        elif self._seq_type == "SET-V":
            if self._seq_value == 0:
                self.v_set = 0
                self.output_state = False
            else:
                self.v_set = self._seq_value
                if not self.output_state:
                    self.output_state = True
        elif self._seq_type == "SET-I":
            self.i_set = self._seq_value
        else:
            raise ValueError("Unknown seq type")
        if not self.switch_to_seq(self._seq_index + 1):
            if self._seq_loop:
                self.switch_to_seq(0)
            else:
                self.func_seq_timer.stop()
                self.seq_btn_enable()

    @QtCore.pyqtSlot()
    def on_btnSeqSave_clicked(self):
        if self.ui.listSeq.count() == 0:
            return
        # 保存到文件
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, self.tr("保存"), "", self.tr("文本文件 (*.txt)")
        )
        if filename == "" or filename is None:
            return
        lines = []
        for i in range(self.ui.listSeq.count()):
            lines.append(self.ui.listSeq.item(i).text())
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    @QtCore.pyqtSlot()
    def on_btnSeqLoad_clicked(self):
        # 从文件加载

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, self.tr("打开"), "", self.tr("文本文件 (*.txt)")
        )

        if filename == "" or filename is None:
            return
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.read().strip().split("\n")
        self.ui.listSeq.clear()
        for line in lines:
            try:
                _ = line.split(" ")
                assert len(_) == 3
                assert _[0] in ["WAIT", "DELAY", "SET-V", "SET-I"]
                if _[0] != "WAIT":
                    assert _[2] in ["ms", "V", "A"]
                    float(_[1])
                self.ui.listSeq.addItem(line)
                self.seq_set_item_font(self.ui.listSeq.count() - 1)
            except Exception:
                CustomMessageBox(
                    self, self.tr("错误"), self.tr("数据验证错误: ") + f"{line}"
                )
                return


MainWindow = MDPMainwindow()


class MDPSettings(QtWidgets.QDialog, FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_DialogSettings()
        self.ui.setupUi(self)
        self.CustomTitleBar = CustomTitleBar(self, self.tr("电源设置"))
        self.CustomTitleBar.set_theme("dark")
        self.CustomTitleBar.set_allow_double_toggle_max(False)
        self.CustomTitleBar.set_min_btn_enabled(False)
        self.CustomTitleBar.set_max_btn_enabled(False)
        self.CustomTitleBar.set_full_btn_enabled(False)
        self.CustomTitleBar.set_close_btn_enabled(False)
        self.setTitleBar(self.CustomTitleBar)

        set_color(self.ui.checkBoxUnlockOPP, setting.get_color("general_red"))

        self.visible = False

    def initValues(self):
        self.ui.checkBoxOutputWarn.setChecked(setting.output_warning)
        self.ui.checkBoxSetLock.setChecked(setting.lock_when_output)
        self.ui.checkBoxUnlockOPP.setChecked(setting.unlock_opp)
        if setting.unlock_opp:
            self.ui.spinBoxOPP.setMaximum(180)
            set_color(self.ui.spinBoxOPP, setting.get_color("general_red"))
        else:
            self.ui.spinBoxOPP.setMaximum(105)
            set_color(self.ui.spinBoxOPP, None)

        info = MainWindow.api.get_device_info()
        self.ui.labelDeviceName.setText(info["device_name"])
        self.ui.labelHWVer.setText(info["hardware_version"])
        self.ui.labelFWVer.setText(info["application_version"])
        self.ui.labelSN.setText(info["device_SN"])

        set = MainWindow.api.get_settings()
        self.ui.spinBoxBacklight.setValue(set["backlight"])
        self.ui.spinBoxVolume.setValue(set["volume"])
        self.ui.spinBoxOPP.setValue(set["opp"])
        self.ui.spinBoxOTP.setValue(set["otp"])
        self.ui.checkBoxRevProtect.setChecked(set["reverse_protect"])
        self.ui.checkBoxAutoOutput.setChecked(set["auto_output"])

    @QtCore.pyqtSlot()
    def on_btnSubmit_clicked(self):
        set = {
            "backlight": int(self.ui.spinBoxBacklight.value()),
            "volume": int(self.ui.spinBoxVolume.value()),
            "opp": float(self.ui.spinBoxOPP.value()),
            "otp": int(self.ui.spinBoxOTP.value()),
            "reverse_protect": bool(self.ui.checkBoxRevProtect.isChecked()),
            "auto_output": bool(self.ui.checkBoxAutoOutput.isChecked()),
        }
        MainWindow.api.set_settings(**set)
        CustomMessageBox(
            self,
            self.tr("成功"),
            self.tr("设置已保存"),
        )

    def show(self) -> None:
        self.initValues()
        center_window(self)
        super().show()
        self.visible = True

    def hide(self) -> None:
        super().hide()
        self.visible = False

    def save_settings(self):
        setting.output_warning = self.ui.checkBoxOutputWarn.isChecked()
        setting.lock_when_output = self.ui.checkBoxSetLock.isChecked()
        setting.unlock_opp = self.ui.checkBoxUnlockOPP.isChecked()
        setting.save(SETTING_FILE)

    def check_connection(self):
        if MainWindow.api is None:
            CustomMessageBox(
                self,
                self.tr("错误"),
                self.tr("请先连接设备"),
            )
            return False
        return True

    @QtCore.pyqtSlot()
    def on_btnOk_clicked(self):
        self.save_settings()
        self.close()

    @QtCore.pyqtSlot(int)
    def on_checkBoxSetLock_stateChanged(self, state: int):
        setting.lock_when_output = state == QtCore.Qt.CheckState.Checked

    @QtCore.pyqtSlot(int)
    def on_checkBoxOutputWarn_stateChanged(self, state: int):
        setting.output_warning = state == QtCore.Qt.CheckState.Checked

    @QtCore.pyqtSlot(int)
    def on_checkBoxUnlockOPP_stateChanged(self, state: int):
        if state == QtCore.Qt.CheckState.Checked and self.visible:
            if not CustomMessageBox.question(
                self,
                self.tr("警告"),
                self.tr(
                    "在超出官方允许的功率范围外使用设备极有可能会对设备造成不可逆的损坏!\n本软件不承担解锁造成的任何损失, 是否继续?"
                ),
            ):

                def _():
                    self.ui.checkBoxUnlockOPP.setChecked(False)
                    setting.unlock_opp = False

                QtCore.QTimer.singleShot(1, _)
                return
        setting.unlock_opp = state == QtCore.Qt.CheckState.Checked
        if setting.unlock_opp:
            self.ui.spinBoxOPP.setMaximum(180)
            set_color(self.ui.spinBoxOPP, setting.get_color("general_red"))
        else:
            self.ui.spinBoxOPP.setMaximum(105)
            set_color(self.ui.spinBoxOPP, None)


class MDPGraphics(QtWidgets.QDialog, FramelessWindow):
    set_max_fps_sig = QtCore.pyqtSignal(float)
    state_fps_sig = QtCore.pyqtSignal(float)
    set_data_len_sig = QtCore.pyqtSignal(int)
    set_interp_sig = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogGraphics()
        self.ui.setupUi(self)
        self.CustomTitleBar = CustomTitleBar(self, self.tr("图形设置"))
        self.CustomTitleBar.set_theme("dark")
        self.CustomTitleBar.set_allow_double_toggle_max(False)
        self.CustomTitleBar.set_min_btn_enabled(False)
        self.CustomTitleBar.set_max_btn_enabled(False)
        self.CustomTitleBar.set_full_btn_enabled(False)
        self.CustomTitleBar.set_close_btn_enabled(False)
        self.setTitleBar(self.CustomTitleBar)
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        if NUMBA_ENABLED:
            self.ui.labelNumba.setVisible(True)
        else:
            self.ui.labelNumba.setVisible(False)

        if not OPENGL_AVALIABLE:
            self.ui.checkBoxOpenGL.setEnabled(False)
            self.ui.checkBoxOpenGL.setChecked(False)

        for k in setting.color_palette:
            if k not in ("dark", "light", "modify_this_to_add_your_custom_theme"):
                self.ui.comboTheme.addItem(k)

    def initValues(self):
        self.ui.spinMaxFps.setValue(setting.graph_max_fps)
        self.ui.spinStateFps.setValue(setting.state_fps)
        self.ui.spinDataLength.setValue(setting.data_pts)
        self.ui.spinDisplayLength.setMaximum(setting.data_pts)
        self.ui.spinDisplayLength.setValue(setting.display_pts)
        self.ui.comboInterp.setCurrentIndex(setting.interp)
        self.ui.spinStateVThres.setValue(setting.v_threshold)
        self.ui.spinStateIThres.setValue(setting.i_threshold)
        self.ui.checkBoxUseCali.setChecked(setting.use_cali)
        self.ui.spinCaliVk.setValue(setting.v_cali_k)
        self.ui.spinCaliVb.setValue(setting.v_cali_b)
        self.ui.spinCaliIk.setValue(setting.i_cali_k)
        self.ui.spinCaliIb.setValue(setting.i_cali_b)
        self.ui.spinCaliVk_2.setValue(setting.vset_cali_k)
        self.ui.spinCaliVb_2.setValue(setting.vset_cali_b)
        self.ui.spinCaliIk_2.setValue(setting.iset_cali_k)
        self.ui.spinCaliIb_2.setValue(setting.iset_cali_b)
        self.ui.checkBoxAntialias.setChecked(setting.antialias)
        self.ui.checkBoxOpenGL.setChecked(setting.opengl)
        self.ui.comboTheme.setCurrentIndex(
            {"light": 1, "dark": 0}.get(setting.theme, setting.theme)
        )
        self.ui.comboInput.setCurrentIndex(int(not setting.bitadjust))

    def show(self) -> None:
        self.initValues()
        center_window(self)
        super().show()

    @QtCore.pyqtSlot(int)
    def on_comboInput_currentIndexChanged(self, index):
        setting.bitadjust = index == 0

    @QtCore.pyqtSlot(int)
    def on_comboTheme_currentIndexChanged(self, index):
        set_theme({0: "dark", 1: "light"}.get(index, self.ui.comboTheme.currentText()))

    @QtCore.pyqtSlot(int)
    def on_checkBoxAntialias_stateChanged(self, state: int):
        setting.antialias = state == QtCore.Qt.CheckState.Checked
        update_pyqtgraph_setting()

    @QtCore.pyqtSlot(int)
    def on_checkBoxOpenGL_stateChanged(self, state: int):
        setting.opengl = state == QtCore.Qt.CheckState.Checked
        update_pyqtgraph_setting()

    @QtCore.pyqtSlot(float)
    def on_spinMaxFps_valueChanged(self, _=None):
        setting.graph_max_fps = self.ui.spinMaxFps.value()
        self.set_max_fps_sig.emit(self.ui.spinMaxFps.value())

    @QtCore.pyqtSlot(float)
    def on_spinStateFps_valueChanged(self, _=None):
        setting.state_fps = self.ui.spinStateFps.value()
        self.state_fps_sig.emit(self.ui.spinStateFps.value())

    @QtCore.pyqtSlot()
    def on_spinDataLength_editingFinished(self):
        value = self.ui.spinDataLength.value()
        if value == setting.data_pts:
            return
        setting.data_pts = value
        self.set_data_len_sig.emit(value)
        self.ui.spinDisplayLength.setMaximum(value)

    @QtCore.pyqtSlot()
    def on_spinDisplayLength_editingFinished(self):
        setting.display_pts = self.ui.spinDisplayLength.value()

    @QtCore.pyqtSlot(int)
    def on_comboInterp_currentIndexChanged(self, index):
        setting.interp = self.ui.comboInterp.currentIndex()
        self.set_interp_sig.emit(index)

    @QtCore.pyqtSlot(float)
    def on_spinStateVThres_valueChanged(self, _=None):
        setting.v_threshold = self.ui.spinStateVThres.value()

    @QtCore.pyqtSlot(float)
    def on_spinStateIThres_valueChanged(self, _=None):
        setting.i_threshold = self.ui.spinStateIThres.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliVk_valueChanged(self, _=None):
        setting.v_cali_k = self.ui.spinCaliVk.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliVb_valueChanged(self, _=None):
        setting.v_cali_b = self.ui.spinCaliVb.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliIk_valueChanged(self, _=None):
        setting.i_cali_k = self.ui.spinCaliIk.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliIb_valueChanged(self, _=None):
        setting.i_cali_b = self.ui.spinCaliIb.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliVk_2_valueChanged(self, _=None):
        setting.vset_cali_k = self.ui.spinCaliVk_2.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliVb_2_valueChanged(self, _=None):
        setting.vset_cali_b = self.ui.spinCaliVb_2.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliIk_2_valueChanged(self, _=None):
        setting.iset_cali_k = self.ui.spinCaliIk_2.value()

    @QtCore.pyqtSlot(float)
    def on_spinCaliIb_2_valueChanged(self, _=None):
        setting.iset_cali_b = self.ui.spinCaliIb_2.value()

    @QtCore.pyqtSlot(int)
    def on_checkBoxUseCali_stateChanged(self, state: int):
        setting.use_cali = state == QtCore.Qt.CheckState.Checked

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        try:
            setting.graph_max_fps = self.ui.spinMaxFps.value()
            setting.state_fps = self.ui.spinStateFps.value()
            setting.data_pts = self.ui.spinDataLength.value()
            setting.display_pts = self.ui.spinDisplayLength.value()
            setting.interp = self.ui.comboInterp.currentIndex()
            setting.v_threshold = self.ui.spinStateVThres.value()
            setting.i_threshold = self.ui.spinStateIThres.value()
            setting.use_cali = self.ui.checkBoxUseCali.isChecked()
            setting.v_cali_k = self.ui.spinCaliVk.value()
            setting.v_cali_b = self.ui.spinCaliVb.value()
            setting.i_cali_k = self.ui.spinCaliIk.value()
            setting.i_cali_b = self.ui.spinCaliIb.value()
            setting.vset_cali_k = self.ui.spinCaliVk_2.value()
            setting.vset_cali_b = self.ui.spinCaliVb_2.value()
            setting.iset_cali_k = self.ui.spinCaliIk_2.value()
            setting.iset_cali_b = self.ui.spinCaliIb_2.value()
            setting.antialias = self.ui.checkBoxAntialias.isChecked()
            setting.opengl = self.ui.checkBoxOpenGL.isChecked()
            setting.bitadjust = self.ui.comboInput.currentIndex() == 0
            setting.save(SETTING_FILE)
        except Exception as e:
            logger.error(e)
        self.close()


class TransparentFloatingWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # 设置窗口为无边框和置顶
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setWindowTitle("DP100 Floating Monitor")

        # 设置窗口大小和透明度
        self.setFixedSize(75, 140)
        self.setWindowOpacity(0.95)

        font_title = QtGui.QFont()
        font_title.setFamily("Sarasa Fixed SC SemiBold")
        font_title.setPointSize(10)

        font_value = QtGui.QFont()
        font_value.setFamily("Sarasa Fixed SC SemiBold")
        font_value.setPointSize(12)

        # 创建主窗口布局
        window_layout = QtWidgets.QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)

        # 创建Frame
        frame = QtWidgets.QFrame(self)
        frame.setStyleSheet("QFrame { background-color: rgba(17, 17, 21, 100); }")
        window_layout.addWidget(frame)

        # 创建Frame内部布局
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QtWidgets.QLabel(" DP100 ", self)
        self.title_label.setFont(font_title)
        set_color(self.title_label, "rgb(200, 200, 200)")
        layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        self.label_visable = True

        self.v_label = QtWidgets.QLabel(self.tr("电压 U"), self)
        self.v_label.setFont(font_title)
        set_color(self.v_label, setting.get_color("general_red", "dark"))
        layout.addWidget(self.v_label)
        self.voltage_label = QtWidgets.QLabel("", self)
        self.voltage_label.setFont(font_value)
        set_color(self.voltage_label, setting.get_color("general_red", "dark"))
        layout.addWidget(self.voltage_label)

        self.i_label = QtWidgets.QLabel(self.tr("电流 I"), self)
        self.i_label.setFont(font_title)
        set_color(self.i_label, setting.get_color("general_green", "dark"))
        layout.addWidget(self.i_label)
        self.current_label = QtWidgets.QLabel("", self)
        self.current_label.setFont(font_value)
        set_color(self.current_label, setting.get_color("general_green", "dark"))
        layout.addWidget(self.current_label)

        self.p_label = QtWidgets.QLabel(self.tr("功率 P"), self)
        self.p_label.setFont(font_title)
        set_color(self.p_label, setting.get_color("general_blue", "dark"))
        layout.addWidget(self.p_label)
        self.power_label = QtWidgets.QLabel("", self)
        self.power_label.setFont(font_value)
        set_color(self.power_label, setting.get_color("general_blue", "dark"))
        layout.addWidget(self.power_label)

        self.setLayout(window_layout)

        self.dragging = False
        self.offset = None

        self.update_values(0, 0, 0)

    def center_window(self):
        self.screen = QtWidgets.QApplication.primaryScreen().geometry()
        x = self.screen.width() - self.width() - 10
        y = self.screen.height() // 2 - self.height() // 2
        self.move(x, y)
        self.setWindowOpacity(0.95)

    def update_values(self, u, i, p):
        self.voltage_label.setText(f"{u:06.3f} V")
        self.current_label.setText(f"{i:06.3f} A")
        if p < 100:
            self.power_label.setText(f"{p:06.3f} W")
        else:
            self.power_label.setText(f"{p:06.2f} W")

    def switch_visibility(self):
        if self.isVisible():
            self.close()
        else:
            self.center_window()
            self.show()

    def wheelEvent(self, event):
        current_opacity = self.windowOpacity()
        if event.angleDelta().y() > 0:
            new_opacity = min(1.0, current_opacity + 0.1)
        else:
            new_opacity = max(0.1, current_opacity - 0.1)
        self.setWindowOpacity(new_opacity)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            move = event.globalPos() - self.offset
            x = max(0, min(move.x(), self.screen.width() - self.width()))
            y = max(0, min(move.y(), self.screen.height() - self.height()))
            self.move(x, y)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False

    def mouseDoubleClickEvent(self, event):
        self.switch_label_visibility()

    def switch_label_visibility(self):
        self.label_visable = not self.label_visable
        if self.label_visable:
            self.v_label.setVisible(True)
            self.i_label.setVisible(True)
            self.p_label.setVisible(True)
            self.setFixedHeight(140)
        else:
            self.v_label.setVisible(False)
            self.i_label.setVisible(False)
            self.p_label.setVisible(False)
            self.setFixedHeight(80)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        toggle_action = menu.addAction(
            self.tr("折叠") if self.label_visable else self.tr("展开")
        )
        close_action = menu.addAction(self.tr("关闭"))

        action = menu.exec_(event.globalPos())

        if action == toggle_action:
            self.switch_label_visibility()
        elif action == close_action:
            self.close()


class ResultGraphWindow(QtWidgets.QDialog, FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建主布局
        self.main_layout = QtWidgets.QVBoxLayout()

        # padding
        label = QtWidgets.QLabel("")
        label.setFixedHeight(25)
        self.main_layout.addWidget(label)
        self.setLayout(self.main_layout)

        # 设置自定义标题栏
        self.setWindowTitle("DP100 Result Graph Window")
        self.CustomTitleBar = CustomTitleBar(self, "DP100 Result Graph Window")
        self.CustomTitleBar.set_theme("dark")
        self.CustomTitleBar.set_allow_double_toggle_max(False)
        self.CustomTitleBar.set_full_btn_enabled(False)
        self.setTitleBar(self.CustomTitleBar)

        # 创建图表组件
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel("left", "Y-Axis")
        self.plot_widget.setLabel("bottom", "X-Axis")

        # 创建曲线
        self.pen = pg.mkPen(color=setting.get_color("line1"), width=2)
        self.fit_pen = pg.mkPen(color=setting.get_color("line2"), width=2)
        self.curve = self.plot_widget.plot(pen=self.pen)
        self.curve.setData([], [])
        self.curve_fit = self.plot_widget.plot(pen=self.fit_pen)
        self.curve_fit.setData([], [])
        self.plot_widget.autoRange()
        self.main_layout.addWidget(self.plot_widget)

        self.hlayout = QtWidgets.QHBoxLayout()

        self.btnXYSwap = QtWidgets.QPushButton("X/Y")
        self.hlayout.addWidget(self.btnXYSwap)
        self.btnXYSwap.clicked.connect(self.swapXY)

        label = QtWidgets.QLabel(self.tr("多项式拟合次数:"))
        label.setFont(global_font)
        self.hlayout.addWidget(label)

        self.spinBoxFit = QtWidgets.QSpinBox()
        self.spinBoxFit.setRange(0, 8)
        self.spinBoxFit.setValue(0)
        self.hlayout.addWidget(self.spinBoxFit)
        self.spinBoxFit.valueChanged.connect(self.update_fit_result)

        self.labelFitResult = QtWidgets.QLabel("N/A")
        self.labelFitResult.setFont(global_font)
        self.hlayout.addWidget(self.labelFitResult)

        self.hlayout.setStretch(0, 0)
        self.hlayout.setStretch(1, 0)
        self.hlayout.setStretch(2, 0)
        self.hlayout.setStretch(3, 1)

        self.main_layout.addLayout(self.hlayout)

        self.x_data = []
        self.y_data = []

    def format_fit_result(self, result):
        result = list(result)
        for i in range(len(result)):
            if abs(result[i]) < 1e-9:
                result[i] = 0
        text = "y = ("
        for i, coef in enumerate(result):
            if i != 0:
                text += " + ("
            text += f"{coef:0.4g}"
            ml = len(result) - i - 1
            if ml > 1:
                text += f"x^{ml}"
            elif ml == 1:
                text += "x"
            text += ")"
        return text

    def update_fit_result(self, _=None):
        if len(self.x_data) + len(self.y_data) < 4 or self.spinBoxFit.value() < 1:
            self.labelFitResult.setText("N/A")
            self.curve_fit.setData([], [])
            return
        logger.info(
            f"fit {len(self.x_data)} points with {self.spinBoxFit.value()} order"
        )
        z = np.polyfit(self.x_data, self.y_data, self.spinBoxFit.value())

        y_pred = np.polyval(z, self.x_data)
        rmse = np.sqrt(np.mean((np.array(self.y_data) - y_pred) ** 2))
        logger.info(f"fit result: {z} with rmse={rmse:0.4g}")
        self.labelFitResult.setText(f"rmse={rmse:0.4f} {self.format_fit_result(z)}")
        SAMPLE_N = 1000
        x_fit = np.linspace(min(self.x_data), max(self.x_data), SAMPLE_N)
        y_fit = np.polyval(z, x_fit)
        self.curve_fit.setData(x_fit, y_fit)

    def showData(self, x, y, x_label, y_label, x_unit, y_unit, title, disable_swap):
        self.x_data = x
        self.y_data = y
        self.x_label = x_label
        self.y_label = y_label
        self.x_unit = x_unit
        self.y_unit = y_unit
        self.title = title
        self.curve.setData(x, y)
        self.plot_widget.setLabel("bottom", x_label, units=x_unit)
        self.plot_widget.setLabel("left", y_label, units=y_unit)
        self.plot_widget.autoRange()
        self.CustomTitleBar.set_name(title)
        if disable_swap:
            self.btnXYSwap.setVisible(False)
        else:
            self.btnXYSwap.setVisible(True)
        if hasattr(self, "vLine"):
            self.plot_widget.removeItem(self.vLine)
        if hasattr(self, "hLine"):
            self.plot_widget.removeItem(self.hLine)
        if not self.isVisible():
            self.spinBoxFit.setValue(0)
        self.update_fit_result()
        if not self.isVisible():
            self.show()
            center_window(self, 800, 600)

    def swapXY(self):
        self.x_data, self.y_data = self.y_data, self.x_data
        self.x_label, self.y_label = self.y_label, self.x_label
        self.x_unit, self.y_unit = self.y_unit, self.x_unit
        self.showData(
            self.x_data,
            self.y_data,
            self.x_label,
            self.y_label,
            self.x_unit,
            self.y_unit,
            self.title,
            False,
        )

    def highlightPoint(self, x, y):
        if hasattr(self, "vLine"):
            self.plot_widget.removeItem(self.vLine)
        if hasattr(self, "hLine"):
            self.plot_widget.removeItem(self.hLine)

        self.vLine = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen(setting.get_color("line2")),
        )
        self.hLine = pg.InfiniteLine(
            angle=0,
            movable=False,
            pen=pg.mkPen(setting.get_color("line2")),
        )
        self.vLine.setPos(x)
        self.hLine.setPos(y)
        self.plot_widget.addItem(self.vLine)
        self.plot_widget.addItem(self.hLine)


DialogSettings = MDPSettings()
DialogGraphics = MDPGraphics()
DialogResult = ResultGraphWindow()
FloatingWindow = TransparentFloatingWindow()
# MainWindow.ui.btnSettings.clicked.connect(DialogSettings.show)
MainWindow.ui.btnGraphics.clicked.connect(DialogGraphics.show)
DialogGraphics.set_max_fps_sig.connect(MainWindow.set_graph_max_fps)
DialogGraphics.state_fps_sig.connect(MainWindow.set_state_fps)
DialogGraphics.set_data_len_sig.connect(MainWindow.set_data_length)
DialogGraphics.set_interp_sig.connect(MainWindow.set_interp)
MainWindow.ui.btnRecordFloatWindow.clicked.connect(FloatingWindow.switch_visibility)
MainWindow.uip_values_signal.connect(FloatingWindow.update_values)
MainWindow.display_data_signal.connect(DialogResult.showData)
MainWindow.highlight_point_signal.connect(DialogResult.highlightPoint)
MainWindow.close_signal.connect(FloatingWindow.close)
MainWindow.close_signal.connect(DialogResult.close)
MainWindow.close_signal.connect(DialogGraphics.close)
MainWindow.close_signal.connect(DialogSettings.close)
app.setWindowIcon(QtGui.QIcon(ICON_PATH))


def set_theme(theme):
    setting.theme = theme
    if theme not in ("dark", "light"):
        sys_theme = setting.color_palette[theme]["based_on_dark_or_light"]
    else:
        sys_theme = theme
    additional_qss = (
        "QToolTip {"
        "   color: rgb(228, 231, 235);"
        "   background-color: rgb(32, 33, 36);"
        "   border: 1px solid rgb(63, 64, 66);"
        "   border-radius: 4px;"
        "}"
        "QSlider::add-page:horizontal {"
        "   background: #36ff8888;"
        "}"
        "QSlider::sub-page:horizontal {"
        "   background: #368888ff;"
        "}"
        if sys_theme == "dark"
        else "QToolTip {"
        "   color: rgb(32, 33, 36);"
        "   background-color: white;"
        "   border: 1px solid rgb(218, 220, 224);"
        "   border-radius: 4px;"
        "}"
        "QSlider::add-page:horizontal {"
        "   background: #36880000;"
        "}"
        "QSlider::sub-page:horizontal {"
        "   background: #36000088;"
        "}"
    )
    qdarktheme.setup_theme(
        sys_theme,
        additional_qss=additional_qss,
    )
    MainWindow.ui.widgetGraph1.setBackground(None)
    MainWindow.ui.widgetGraph2.setBackground(None)
    MainWindow.CustomTitleBar.set_theme(sys_theme)
    DialogSettings.CustomTitleBar.set_theme(sys_theme)
    DialogGraphics.CustomTitleBar.set_theme(sys_theme)
    set_color(
        DialogGraphics.ui.labelNumba,
        setting.get_color("general_green"),
    )
    if MainWindow.api is not None:
        set_color(
            MainWindow.ui.labelConnectState,
            setting.get_color("general_green"),
        )
    MainWindow.update_pen()
    DialogResult.pen.setColor(QtGui.QColor(setting.get_color("line1")))
    MainWindow.ui.horizontalSlider.setStyleSheet("background: none;")
    MainWindow.ui.horizontalSlider.setBarVisible(False)

    set_color(MainWindow.ui.lcdVoltage, setting.get_color("lcd_voltage"))
    set_color(MainWindow.ui.lcdCurrent, setting.get_color("lcd_current"))
    set_color(MainWindow.ui.lcdPower, setting.get_color("lcd_power"))
    set_color(MainWindow.ui.lcdEnerge, setting.get_color("lcd_energy"))
    set_color(
        MainWindow.ui.lcdAvgPower,
        setting.get_color("lcd_avg_power"),
    )
    set_color(
        MainWindow.ui.lcdResistence,
        setting.get_color("lcd_resistance"),
    )


set_theme(setting.theme)


def show_app():
    MainWindow.show()
    MainWindow.activateWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    show_app()
