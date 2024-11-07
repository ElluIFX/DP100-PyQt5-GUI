import datetime
import json
import math
import os
import random
import sys
import time
import warnings
from threading import Lock
from typing import List, Optional, Tuple

from loguru import logger

import mdp_controller
import richuru
from mdp_controller import MDP_P906

ARG_PATH = os.path.dirname(sys.argv[0])
ABS_PATH = os.path.dirname(__file__)

if os.environ.get("MDP_ENABLE_LOG") is not None:
    richuru.install()
    logger.add(
        os.path.join(ARG_PATH, "mdp.log"), level="TRACE", backtrace=True, diagnose=True
    )
else:
    richuru.install(tracebacks_suppress=[mdp_controller])

os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"

# ignore opengl runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

from qframelesswindow import FramelessWindow, TitleBar

OPENGL_AVAILABLE = False
try:
    import OpenGL  # noqa: F401

    OPENGL_AVAILABLE = True
    pg.setConfigOption("enableExperimental", True)
    pg.setConfigOption("antialias", True)
    logger.info("OpenGL successfully enabled")
except Exception as e:
    logger.warning(f"Enabling OpenGL failed with {e}.")

try:
    import numba as nb  # noqa: F401

    pg.setConfigOption("useNumba", True)
    logger.info("Numba successfully enabled")
except Exception as e:
    logger.warning(f"Enabling Numba failed with {e}.")


import numpy as np
import qdarktheme
from serial.tools.list_ports import comports
from simple_pid import PID

from mdp_gui_template import Ui_DialogGraphics, Ui_DialogSettings, Ui_MainWindow

SETTING_FILE = os.path.join(ARG_PATH, "settings.json")
ICON_PATH = os.path.join(ABS_PATH, "icon.ico")
FONT_PATH = os.path.join(ABS_PATH, "SarasaFixedSC-SemiBold.ttf")
qdarktheme.enable_hi_dpi()
app = QtWidgets.QApplication(sys.argv)

# get system language
system_lang = QtCore.QLocale.system().name()
logger.info(f"System language: {system_lang}")
ENGLISH = False
if not system_lang.startswith("zh") or os.environ.get("MDP_FORCE_ENGLISH") == "1":
    trans = QtCore.QTranslator()
    trans.load(os.path.join(ABS_PATH, "en_US.qm"))
    app.installTranslator(trans)
    ENGLISH = True

# load custom font
_ = QtGui.QFontDatabase.addApplicationFont(FONT_PATH)
fonts = QtGui.QFontDatabase.applicationFontFamilies(_)
logger.info(f"Loaded custom {len(fonts)} fonts from {FONT_PATH}")
logger.debug(f"Fonts: {fonts}")


class FmtAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        if len(values) == 0 or max(values) < 1e6:
            return super().tickStrings(values, scale, spacing)
        else:
            return [f"{v:.2e}" for v in values]


class RealtimeData:
    def __init__(self, data_length) -> None:
        self.start_time = time.perf_counter()
        self.eng_start_time = time.perf_counter()
        self.last_time = 0
        self.save_datas_flag = False
        self.voltage_tmp = []
        self.current_tmp = []
        self.energy = 0
        self.sync_lock = Lock()
        self.voltages = np.zeros(data_length, np.float64)
        self.currents = np.zeros(data_length, np.float64)
        self.powers = np.zeros(data_length, np.float64)
        self.resistances = np.zeros(data_length, np.float64)
        self.times = np.zeros(data_length, np.float64)
        self.update_count = data_length
        self.data_length = data_length


class RecordData:
    def __init__(self) -> None:
        self.voltages: List[float] = []
        self.currents: List[float] = []
        self.times: List[float] = []
        self.start_time = 0
        self.last_time = 0

    def add_values(self, voltage, current, time):
        self.voltages.append(voltage)
        self.currents.append(current)
        self.times.append(time)

    def to_csv(self, filename):
        data = np.array([self.times, self.voltages, self.currents]).T
        np.savetxt(
            filename,
            data,
            delimiter=",",
            fmt="%f",
            header="time,voltage,current",
            comments="",
        )


class FPSCounter(object):
    def __init__(self, max_sample=40) -> None:
        self.t = time.perf_counter()
        self.max_sample = max_sample
        self.t_list: List[float] = []
        self._fps = 0

    def clear(self) -> None:
        self.t = time.perf_counter()
        self.t_list = []
        self._fps = 0

    def tick(self) -> None:
        t = time.perf_counter()
        self.t_list.append(t - self.t)
        self.t = t
        if len(self.t_list) > self.max_sample:
            self.t_list.pop(0)

    @property
    def fps(self) -> float:
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


class CustomTitleBar(TitleBar):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.label = QtWidgets.QLabel(name, self)
        self.label.setStyleSheet(
            "QLabel{font: 13px 'Microsoft YaHei UI'; margin: 10px}"
        )
        self.label.adjustSize()
        self.darkStyle = {
            "normal": {
                "color": (255, 255, 255),
            }
        }
        self.lightStyle = {
            "normal": {
                "color": (20, 20, 20),
            }
        }
        self.autoStyle = {
            "normal": {
                "color": (140, 140, 140),
            }
        }

    def set_theme(self, theme):
        style = getattr(self, f"{theme}Style")
        self.minBtn.updateStyle(style)
        self.maxBtn.updateStyle(style)
        self.closeBtn.updateStyle(style)
        self.fullBtn.updateStyle(style)


def center_window(instance: QtWidgets.QWidget) -> None:
    geo = instance.geometry()
    scr_geo = QtWidgets.QApplication.desktop().screenGeometry()
    center_x = (scr_geo.width() - geo.width()) // 2
    center_y = (scr_geo.height() - geo.height()) // 2
    instance.move(center_x, center_y)


def float_str(value, limit=1e5):
    if value > limit:
        return f"{value:.1e}"
    else:
        return f"{value:.3f}"


def set_color(widget: QtWidgets.QWidget, rgb):
    if rgb is None:
        widget.setStyleSheet("")
        return
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


class Setting:
    def __init__(self) -> None:
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
        self.baudrate = 921600
        self.comport = ""
        self.address = "AA:BB:CC:DD:EE"
        self.freq = 2521
        self.txpower = "4dBm"
        self.idcode = ""
        self.color = "#66CCFF"
        self.m01ch = "CH-0"
        self.blink = False

        self.data_pts = 1000
        self.graph_max_fps = 50
        self.state_fps = 15
        self.interp = 1
        self.avgmode = 1
        self.opengl = False

        self.v_threshold = 0.002
        self.i_threshold = 0.002
        self.use_cali = False
        self.v_cali_k = 1.0
        self.v_cali_b = 0.0
        self.i_cali_k = 1.0
        self.i_cali_b = 0.0

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.__dict__, f, indent=4, ensure_ascii=False)

    def load(self, filename):
        if not os.path.exists(filename):
            self.save(filename)
            return
        self.__dict__.update(json.load(open(filename, "r")))

    def __repr__(self) -> str:
        return f"Setting({self.__dict__})"


setting = Setting()
setting.load(SETTING_FILE)
pg.setConfigOption("useOpenGL", setting.opengl)


class MDPMainwindow(QtWidgets.QMainWindow, FramelessWindow):  # QtWidgets.QMainWindow
    data = RealtimeData(setting.data_pts)
    data_fps = 50
    graph_keep_flag = False
    graph_record_flag = False
    output_state = False
    locked = False
    _v_set = 0
    _i_set = 0
    open_r = 1e7

    def __init__(self, parent=None):
        self.api: Optional[MDP_P906] = None

        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.fps_counter = FPSCounter()
        self.CustomTitleBar = CustomTitleBar(self, self.tr("MDP-P906 数控电源上位机"))
        self.CustomTitleBar.set_theme("dark")
        self.ui.comboDataFps.setCurrentText(f"{self.data_fps}Hz")
        self.setTitleBar(self.CustomTitleBar)
        self.initSignals()
        self.resize(920, 800)
        self.initGraph()
        self.initTimer()
        self.set_interp(setting.interp)
        self.refresh_preset()
        self.get_preset("1")
        self.close_state_ui()
        self.ui.progressBarVoltage.setMaximum(1000)
        self.ui.progressBarCurrent.setMaximum(1000)
        self._last_state_change_t = time.perf_counter()
        self.titleBar.raise_()
        self.ui.btnSeqStop.hide()
        self.ui.listSeq.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.spinBoxVoltage.setSingleStep(0.001)
        self.ui.spinBoxCurrent.setSingleStep(0.001)

        if ENGLISH:
            font = QtGui.QFont()
            font.setFamily("Sarasa Fixed SC SemiBold")
            font.setPointSize(7)
            self.ui.btnSeqCurrent.setFont(font)
            self.ui.btnSeqCurrent.setText("I-SET")
            self.ui.btnSeqVoltage.setFont(font)
            self.ui.btnSeqVoltage.setText("V-SET")
            self.ui.btnSeqDelay.setFont(font)
            self.ui.btnSeqWaitTime.setFont(font)
            self.ui.btnSeqSingle.setFont(font)
            self.ui.btnSeqSingle.setText("Once")
            self.ui.btnSeqLoop.setFont(font)
            self.ui.btnSeqSave.setFont(font)
            self.ui.btnSeqLoad.setFont(font)

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        center_window(self)
        return super().showEvent(a0)

    def initTimer(self):
        self.state_request_sender_timer = QtCore.QTimer(self)
        self.state_request_sender_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.state_request_sender_timer.timeout.connect(self.request_state)
        self.update_state_timer = QtCore.QTimer(self)
        self.update_state_timer.timeout.connect(self.update_state)
        self.draw_graph_timer = QtCore.QTimer(self)
        self.draw_graph_timer.timeout.connect(self.draw_graph)
        self.state_lcd_timer = QtCore.QTimer(self)
        self.state_lcd_timer.timeout.connect(self.update_state_lcd)
        self.func_sweep_timer = QtCore.QTimer(self)
        self.func_sweep_timer.timeout.connect(self.func_sweep)
        self.func_wave_gen_timer = QtCore.QTimer(self)
        self.func_wave_gen_timer.timeout.connect(self.func_wave_gen)
        self.func_keep_power_timer = QtCore.QTimer(self)
        self.func_keep_power_timer.timeout.connect(self.func_keep_power)
        self.func_seq_timer = QtCore.QTimer(self)
        self.func_seq_timer.timeout.connect(self.func_seq)
        self.graph_record_save_timer = QtCore.QTimer(self)
        self.graph_record_save_timer.timeout.connect(self.graph_record_save)

    def initSignals(self):
        self.ui.comboDataFps.currentTextChanged.connect(self.set_data_fps)
        self.ui.comboPreset.currentTextChanged.connect(self.set_preset)
        self.ui.comboPresetEdit.currentTextChanged.connect(self.get_preset)
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

    def startMyTimer(self):
        t = time.perf_counter()
        self.data.start_time = t
        self.data.eng_start_time = t
        self.data.last_time = t
        self.data.energy = 0
        self.update_state_timer.start(100)
        self.state_request_sender_timer.start(round(1000 / self.data_fps))
        self.draw_graph_timer.start(
            round(1000 / min(self.data_fps, setting.graph_max_fps))
        )
        self.state_lcd_timer.start(round(1000 / min(self.data_fps, setting.state_fps)))

    def stopMyTimer(self):
        self.state_request_sender_timer.stop()
        self.draw_graph_timer.stop()
        self.state_lcd_timer.stop()
        if self.func_sweep_timer.isActive():
            self.stop_func_sweep()
        if self.func_wave_gen_timer.isActive():
            self.stop_func_wave_gen()
        if self.func_keep_power_timer.isActive():
            self.stop_func_keep_power()

    def switch_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def set_step(self, spin: QtWidgets.QDoubleSpinBox, f, t):
        STEPS = {
            0: 0.001,
            -1: 0.001,
            -2: 0.01,
            -3: 0.1,
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

    @property
    def v_set(self):
        return self._v_set

    @v_set.setter
    def v_set(self, value):
        if self.api is None or self.locked:
            return
        self.api.set_voltage(value)
        self._v_set = value
        self.ui.spinBoxVoltage.setValue(value)
        self._last_state_change_t = time.perf_counter()

    @property
    def i_set(self):
        return self._i_set

    @i_set.setter
    def i_set(self, value):
        if self.api is None or self.locked:
            return
        self.api.set_current(value)
        self._i_set = value
        self.ui.spinBoxCurrent.setValue(value)
        self._last_state_change_t = time.perf_counter()

    def update_state(self):
        if self.api is None:
            return
        self.ui.labelComSpeed.setText(f"{self.api._adp.speed_counter.KBps:.1f}kBps")
        errrate = self.api._adp.speed_counter.error_rate * 100
        self.ui.labelErrRate.setText(f"CON-ERR {errrate:.0f}%")
        clr = "red" if errrate > 50 else ("yellow" if errrate > 10 else None)
        set_color(self.ui.labelErrRate, clr)
        set_color(self.ui.labelComSpeed, clr)
        (
            State,
            Locked,
            SetVoltage,
            SetCurrent,
            InputVoltage,
            InputCurrent,
            Temperature,
            ErrFlag,
            _,
        ) = self.api.get_status()
        self.ui.btnOutput.setText(f"-  {State.upper()}  -")
        set_color(
            self.ui.btnOutput,
            {"off": "khaki", "on": "lightgreen", "cv": "skyblue", "cc": "tomato"}[
                State
            ],
        )
        self.output_state = State != "off"
        self.locked = Locked
        self.ui.frameOutputSetting.setEnabled(not Locked)
        if SetVoltage >= 0:
            self._v_set = SetVoltage
            if not self.ui.spinBoxVoltage.hasFocus():
                self.ui.spinBoxVoltage.setValue(SetVoltage)
        if SetCurrent >= 0:
            self._i_set = SetCurrent
            if not self.ui.spinBoxCurrent.hasFocus():
                self.ui.spinBoxCurrent.setValue(SetCurrent)
        self.ui.labelLockState.setText("[LOCKED]" if Locked else "UNLOCKED")
        set_color(self.ui.labelLockState, "orangered" if Locked else None)
        self.ui.labelInputVals.setText(f"{InputVoltage:.2f}V {InputCurrent:.2f}A")
        self.ui.labelTemperature.setText(f"TEMP {Temperature:.1f}℃")
        self.ui.labelError.setText(
            f"ERROR-{ErrFlag:02X}" if ErrFlag != 0 else "NO ERROR"
        )
        set_color(self.ui.labelError, "red" if ErrFlag != 0 else None)

    @QtCore.pyqtSlot()
    def on_btnOutput_clicked(self):
        if self.api is None:
            return
        self.output_state = not self.output_state
        self._last_state_change_t = time.perf_counter()
        self.api.set_output(self.output_state)
        self.update_state()

    def close_state_ui(self):
        self.ui.labelConnectState.setText(self.tr("未连接"))
        set_color(self.ui.labelConnectState, None)
        self.ui.frameOutputSetting.setEnabled(False)
        self.ui.frameSystemState.setEnabled(False)
        self.ui.frameGraph.setEnabled(False)
        self.ui.progressBarCurrent.setValue(0)
        self.ui.progressBarVoltage.setValue(0)
        self.state_callback([(0, 0)])
        self.ui.btnOutput.setText("[N/A]")
        set_color(self.ui.btnOutput, None)
        for widget in [
            self.ui.labelLockState,
            self.ui.labelInputVals,
            self.ui.labelTemperature,
            self.ui.labelError,
            self.ui.labelComSpeed,
            self.ui.labelErrRate,
        ]:
            set_color(widget, None)
            widget.setText("[N/A]")
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

    def open_state_ui(self):
        self.ui.labelConnectState.setText(self.tr("已连接"))
        set_color(self.ui.labelConnectState, "lightgreen")
        self.ui.frameOutputSetting.setEnabled(True)
        self.ui.frameGraph.setEnabled(True)
        self.ui.frameSystemState.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_btnConnect_clicked(self):
        try:
            if self.api is not None:
                self.stopMyTimer()
                self.close_state_ui()
                api = self.api
                self.api = None
                api.close()
            else:
                if not setting.idcode:
                    QtWidgets.QMessageBox.warning(
                        self,
                        self.tr("警告"),
                        self.tr("IDCODE为空, 请先完成连接设置"),
                    )
                    return
                color_rgb = bytes.fromhex(setting.color.lstrip("#"))
                api = None
                try:
                    api = MDP_P906(
                        port=setting.comport,
                        baudrate=setting.baudrate,
                        address=setting.address,
                        freq=int(setting.freq),
                        blink=setting.blink,
                        idcode=setting.idcode,
                        led_color=(color_rgb[0], color_rgb[1], color_rgb[2]),
                        m01_channel=int(setting.m01ch[3]),
                        tx_output_power=setting.txpower,
                    )
                    api.connect(retry_times=2)
                except Exception as e:
                    if api is not None:
                        api.close()
                    logger.exception("Failed to connect")
                    raise e
                self.api = api
                self.api.register_realtime_value_callback(self.state_callback)
                self._last_state_change_t = time.perf_counter()
                self.startMyTimer()
                self.update_state()
                self.open_state_ui()
                self.ui.btnGraphClear.clicked.emit()
        except Exception as e:
            #     self.ui.labelConnectState.setText(self.tr("连接失败"))
            #     set_color(self.ui.labelConnectState, "red")
            #     QtCore.QTimer.singleShot(
            #         2000,
            #         lambda: (
            #             self.ui.labelConnectState.setText(self.tr("未连接")),
            #             set_color(self.ui.labelConnectState, None),
            #         ),
            #     )
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("连接失败"),
                str(e),
            )
            return

    def request_state(self):
        if self.api is not None:
            self.api.request_realtime_value()

    def state_callback(self, rtvalues: List[Tuple[float, float]]):
        vt, it = setting.v_threshold, setting.i_threshold
        if setting.use_cali:
            rtvalues = [
                (
                    v * setting.v_cali_k + setting.v_cali_b,
                    i * setting.i_cali_k + setting.i_cali_b,
                )
                for v, i in rtvalues
            ]
        len_ = len(rtvalues)
        rtvalues = [(v if v > vt else 0.0, i if i > it else 0.0) for v, i in rtvalues]
        t1 = time.perf_counter()
        data = self.data
        if self.graph_record_flag:
            if self.graph_record_data.start_time == 0:
                self.graph_record_data.start_time = t1
                self.graph_record_data.last_time = t1
            else:
                t = t1 - self.graph_record_data.start_time
                dt = t1 - self.graph_record_data.last_time
                self.graph_record_data.last_time = t1
                for idx, (v, i) in enumerate(rtvalues):
                    self.graph_record_data.add_values(
                        v, i, t - dt + (dt / len_) * (idx + 1)
                    )
        with data.sync_lock:
            for v, i in rtvalues:
                data.voltage_tmp.append(v)
                data.current_tmp.append(i)
            if len(rtvalues) == 9:
                if setting.avgmode == 1:
                    rtvalues = np.array(rtvalues)
                    rtvalues = np.reshape(rtvalues, [3, 3, 2])
                    rtvalues = np.mean(rtvalues, axis=(1))
                    len_ = 3
                elif setting.avgmode == 2:
                    rtvalues = np.array(rtvalues)
                    rtvalues = np.reshape(rtvalues, [1, 9, 2])
                    rtvalues = np.mean(rtvalues, axis=(1))
                    len_ = 1
            t = t1 - data.start_time
            dt = t1 - data.last_time
            data.last_time = t1
            if data.save_datas_flag:
                data.voltages = np.roll(data.voltages, -len_)
                data.currents = np.roll(data.currents, -len_)
                data.powers = np.roll(data.powers, -len_)
                data.resistances = np.roll(data.resistances, -len_)
                data.times = np.roll(data.times, -len_)
                if data.update_count >= len_:
                    data.update_count -= len_
            for idx, (v, i) in enumerate(rtvalues):
                data.energy += v * i * (dt / len_)
                if data.save_datas_flag:
                    data.voltages[-len_ + idx] = v
                    data.currents[-len_ + idx] = i
                    data.powers[-len_ + idx] = v * i
                    data.resistances[-len_ + idx] = v / i if i != 0 else self.open_r
                    data.times[-len_ + idx] = t - dt + (dt / len_) * (idx + 1)
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
                f"{data.energy / (data.last_time - data.eng_start_time):.{3+setting.interp}f}"
            )
            self.ui.lcdEnerge.display(f"{data.energy:.{3+setting.interp}f}")
        power = vavg * iavg
        if iavg >= 0.002:  # 致敬P906的愚蠢adc
            resistance = vavg / iavg
        else:
            resistance = self.open_r
        r_text = (
            f"{resistance:.{3+setting.interp}f}"
            if resistance < self.open_r / 100
            else "--"
        )
        self.ui.lcdVoltage.display(f"{vavg:.{3+setting.interp}f}")
        self.ui.lcdCurrent.display(f"{iavg:.{3+setting.interp}f}")
        self.ui.lcdResistence.display(r_text)
        self.ui.lcdPower.display(f"{power:.{3+setting.interp}f}")

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

    def set_data_fps(self, text):
        if text != "":
            self.data_fps = int(text.replace("Hz", ""))
        if self.state_request_sender_timer.isActive():
            self.state_request_sender_timer.stop()
            self.state_request_sender_timer.start(round(1000 / self.data_fps))
        if self.draw_graph_timer.isActive():
            self.draw_graph_timer.stop()
            self.draw_graph_timer.start(
                round(1000 / min(self.data_fps, setting.graph_max_fps))
            )
        if self.state_lcd_timer.isActive():
            self.state_lcd_timer.stop()
            self.state_lcd_timer.start(
                round(1000 / min(self.data_fps, setting.state_fps))
            )
        self.fps_counter.clear()

    def set_graph_max_fps(self, _):
        self.set_data_fps(self.ui.comboDataFps.currentText())

    def set_state_fps(self, fps):
        self.set_data_fps(self.ui.comboDataFps.currentText())

    def set_data_length(self, length) -> None:
        self.data.data_length = length
        self.on_btnGraphClear_clicked()

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
        self.ui.widgetGraph1.setBackground(None)
        self.ui.widgetGraph2.setBackground(None)
        self.ui.widgetGraph1.setLabel("left", self.tr("电压"), units="V")
        self.ui.widgetGraph2.setLabel("left", self.tr("电流"), units="A")
        self._graph_units_dict = {
            self.tr("电压"): "V",
            self.tr("电流"): "A",
            self.tr("功率"): "W",
            self.tr("阻值"): "Ω",
        }
        self.ui.widgetGraph1.showGrid(x=True, y=True)
        self.ui.widgetGraph2.showGrid(x=True, y=True)
        self.ui.widgetGraph1.setMouseEnabled(x=False, y=False)
        self.ui.widgetGraph2.setMouseEnabled(x=False, y=False)
        self.pen1 = pg.mkPen(color="salmon", width=1)
        self.pen2 = pg.mkPen(color="turquoise", width=1)
        self.curve1 = self.ui.widgetGraph1.plot(pen=self.pen1, clear=True)
        self.curve2 = self.ui.widgetGraph2.plot(pen=self.pen2, clear=True)
        self.data.save_datas_flag = True
        self._graph_auto_scale_flag = True
        self.ui.widgetGraph1.setAxisItems(
            axisItems={"left": FmtAxisItem(orientation="left")}
        )
        self.ui.widgetGraph2.setAxisItems(
            axisItems={"left": FmtAxisItem(orientation="left")}
        )
        self.set_graph1_data(self.tr("电压"))
        self.set_graph2_data(self.tr("电流"))

    def get_data(self, text):
        if text == self.tr("电压"):
            data = self.data.voltages[self.data.update_count :]
        elif text == self.tr("电流"):
            data = self.data.currents[self.data.update_count :]
        elif text == self.tr("功率"):
            data = self.data.powers[self.data.update_count :]
        elif text == self.tr("阻值"):
            data = self.data.resistances[self.data.update_count :]
            time = self.data.times[self.data.update_count :]
            # find indexs that != self.open_r
            indexs = np.where(data != self.open_r)[0]
            data = data[indexs]
            if data.size == 0:
                return None, None, None, None, None
            time = time[indexs]
            return data, np.max(data), np.min(data), np.mean(data), time
        elif text == self.tr("无"):
            return None, None, None, None, None
        if data.size == 0:
            return None, None, None, None, None
        return (
            data,
            np.max(data),
            np.min(data),
            np.mean(data),
            self.data.times[self.data.update_count :],
        )

    _typename_dict = None

    def draw_graph(self):
        if self._typename_dict is None:
            self._typename_dict = {
                self.tr("电压"): "V",
                self.tr("电流"): "I",
                self.tr("功率"): "P",
                self.tr("阻值"): "R",
            }
        self.ui.labelFps.setText(f"{self.fps_counter.fps:.1f}Hz")
        if self.graph_keep_flag:
            return
        type1 = self.ui.comboGraph1Data.currentText()
        type2 = self.ui.comboGraph2Data.currentText()
        with self.data.sync_lock:
            data1, max1, min1, avg1, time1 = self.get_data(type1)
            data2, max2, min2, avg2, time2 = self.get_data(type2)
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
                    self.ui.widgetGraph1.setXRange(time1[0], time1[-1])
            if data2 is not None and time2.size != 0:
                if max2 != np.inf and min2 != -np.inf:
                    add2 = max(0.01, (max2 - min2) * 0.05)
                    self.ui.widgetGraph2.setYRange(min2 - add2, max2 + add2)
                    self.ui.widgetGraph2.setXRange(time2[0], time2[-1])

    def set_graph1_data(self, text):
        if text == self.tr("无"):
            self.ui.widgetGraph1.hide()
            return
        self.ui.widgetGraph1.show()
        self.ui.widgetGraph1.setLabel("left", text, units=self._graph_units_dict[text])

    def set_graph2_data(self, text):
        if text == self.tr("无"):
            self.ui.widgetGraph2.hide()
            return
        self.ui.widgetGraph2.show()
        self.ui.widgetGraph2.setLabel("left", text, units=self._graph_units_dict[text])

    @QtCore.pyqtSlot()
    def on_btnGraphClear_clicked(self):
        with self.data.sync_lock:
            self.data.save_datas_flag = False
            self.data.voltages = np.zeros(self.data.data_length, np.float64)
            self.data.currents = np.zeros(self.data.data_length, np.float64)
            self.data.powers = np.zeros(self.data.data_length, np.float64)
            self.data.resistances = np.zeros(self.data.data_length, np.float64)
            self.data.times = np.zeros(self.data.data_length, np.float64)
            self.data.update_count = self.data.data_length
            t = time.perf_counter()
            self.data.start_time = t
            self.data.last_time = t
            self.data.save_datas_flag = True

        self.curve1.setData(x=[], y=[])
        self.curve2.setData(x=[], y=[])

    @QtCore.pyqtSlot()
    def on_btnGraphKeep_clicked(self):
        self.graph_keep_flag = not self.graph_keep_flag
        if self.graph_keep_flag:
            self.ui.btnGraphKeep.setText(self.tr("解除"))
        else:
            self.ui.btnGraphKeep.setText(self.tr("保持"))
        mouse_enabled = self.graph_keep_flag or (not self._graph_auto_scale_flag)
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
        self.ui.widgetGraph1.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)
        self.ui.widgetGraph2.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)

    @QtCore.pyqtSlot()
    def on_btnGraphRecord_clicked(self):
        self.graph_record_flag = not self.graph_record_flag
        if self.graph_record_flag:
            self.graph_record_data = RecordData()
            time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            self.graph_record_filename = f"./record_{time_str}.csv"
            self.ui.btnGraphRecord.setText(self.tr("停止"))
            self.graph_record_save_timer.start(30000)
        else:
            self.graph_record_save_timer.stop()
            self.graph_record_data.to_csv(self.graph_record_filename)
            self.graph_record_data = RecordData()
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle(self.tr("录制完成"))
            msg_box.setText(
                self.tr("数据已保存至：") + f"{self.graph_record_filename[2:]}"
            )
            msg_box.exec_()
            self.ui.btnGraphRecord.setText(self.tr("录制"))

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

    ######### 辅助功能-参数扫描 #########

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
            self.func_sweep_timer.start(round(self._sweep_delay * 1000))
            self.ui.btnSweep.setText(self.tr("功能已开启"))
            if self._sweep_target == self.tr("电压"):
                self.ui.spinBoxVoltage.setEnabled(False)
            elif self._sweep_target == self.tr("电流"):
                self.ui.spinBoxCurrent.setEnabled(False)
            self.ui.scrollAreaSweep.setEnabled(False)
            if not self.output_state:
                self.v_set = self._sweep_start
                self.on_btnOutput_clicked()

    def stop_func_sweep(self):
        self.func_sweep_timer.stop()
        self.ui.btnSweep.setText(self.tr("功能已关闭"))
        if self._sweep_target == self.tr("电压"):
            self.ui.spinBoxVoltage.setEnabled(True)
        elif self._sweep_target == self.tr("电流"):
            self.ui.spinBoxCurrent.setEnabled(True)
        self.ui.scrollAreaSweep.setEnabled(True)

    def func_sweep(self):
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
            self._swep_temp = self._sweep_stop
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
            self._wavegen_start_time = time.perf_counter()
            self.func_wave_gen_timer.start(round(1000 / self._wavegen_loopfreq))
            self.ui.btnWaveGen.setText(self.tr("功能已开启"))
            self.ui.spinBoxWaveGenLoopFreq.setEnabled(False)
            self.ui.spinBoxVoltage.setEnabled(False)
            if not self.output_state:
                self.v_set = self._wavegen_lowlevel
                self.on_btnOutput_clicked()

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
            voltage = self._keep_power_pid(self.data.powers[-1])
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
        text, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr("编辑动作"),
            self.tr("请确保修改后动作文本格式正确,否则无法识别动作"),
            text=text,
        )
        if not ok:
            return
        item.setText(text)

    def seq_clear_all(self):
        ok = QtWidgets.QMessageBox.question(
            self,
            self.tr("清空序列"),
            self.tr("确定要清空序列吗？"),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if ok == QtWidgets.QMessageBox.Yes:
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

    @QtCore.pyqtSlot()
    def on_btnSeqDelay_clicked(self):
        row = self.ui.listSeq.currentRow()
        delay, ok = QtWidgets.QInputDialog.getInt(
            self,
            self.tr("输入延时"),
            self.tr("请输入延时时间 (ms)"),
            1000,
            0,
            100000,
            1,
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"DELAY {delay} ms")
        self.ui.listSeq.setCurrentRow(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqWaitTime_clicked(self):
        row = self.ui.listSeq.currentRow()
        time_now_str = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        wait_time, ok = QtWidgets.QInputDialog.getText(
            self,
            self.tr("输入等待时间"),
            self.tr("请输入等待时间 (格式: 年-月-日 时:分:秒)"),
            text=time_now_str,
        )
        if not ok:
            return
        try:
            datetime.datetime.strptime(wait_time, "%y-%m-%d %H:%M:%S")
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, self.tr("错误"), self.tr("时间格式错误")
            )
            return
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"WAIT {wait_time}")
        self.ui.listSeq.setCurrentRow(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqVoltage_clicked(self):
        row = self.ui.listSeq.currentRow()
        voltage, ok = QtWidgets.QInputDialog.getDouble(
            self, self.tr("输入电压"), self.tr("请输入电压值 (V)"), 1, 0, 30, 3
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"SET-V {voltage:.3f} V")
        self.ui.listSeq.setCurrentRow(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqCurrent_clicked(self):
        row = self.ui.listSeq.currentRow()
        current, ok = QtWidgets.QInputDialog.getDouble(
            self, self.tr("输入电流"), self.tr("请输入电流值 (A)"), 1, 0, 10, 3
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"SET-I {current:.3f} A")
        self.ui.listSeq.setCurrentRow(row + 1)

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
                " ".join(text.split()[1:]), "%y-%m-%d %H:%M:%S"
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
            self.v_set = self._seq_value
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
            except Exception:
                QtWidgets.QMessageBox.warning(
                    self, self.tr("错误"), self.tr("数据验证错误: ") + f"{line}"
                )
                return


MainWindow = MDPMainwindow()


class MDPSettings(QtWidgets.QDialog, FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.ui = Ui_DialogSettings()
        self.ui.setupUi(self)
        self.CustomTitleBar = CustomTitleBar(self, self.tr("连接设置"))
        self.CustomTitleBar.set_theme("dark")
        self.CustomTitleBar.set_allow_double_toggle_max(False)
        self.CustomTitleBar.set_min_btn_enabled(False)
        self.CustomTitleBar.set_max_btn_enabled(False)
        self.CustomTitleBar.set_full_btn_enabled(False)
        self.CustomTitleBar.set_close_btn_enabled(False)
        self.setTitleBar(self.CustomTitleBar)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def initValues(self):
        self.ui.spinBoxBaud.setValue(setting.baudrate)
        self.ui.lineEditAddr1.setText(setting.address.split(":")[0])
        self.ui.lineEditAddr2.setText(setting.address.split(":")[1])
        self.ui.lineEditAddr3.setText(setting.address.split(":")[2])
        self.ui.lineEditAddr4.setText(setting.address.split(":")[3])
        self.ui.lineEditAddr5.setText(setting.address.split(":")[4])
        self.ui.spinBoxFreq.setValue(setting.freq)
        self.ui.comboBoxPower.setCurrentText(setting.txpower)
        self.ui.lineEditIdcode.setText(setting.idcode)
        self.ui.lineEditColor.setText(setting.color)
        self.ui.spinBoxM01.setValue(int(setting.m01ch[3]))
        self.ui.comboBoxPort.setCurrentText(
            setting.comport if setting.comport else self.tr("自动")
        )
        self.ui.comboBoxBlink.setCurrentText(
            self.tr("闪烁") if setting.blink else self.tr("常亮")
        )

    def refreshPorts(self):
        self.ui.comboBoxPort.clear()
        self.ui.comboBoxPort.addItem(self.tr("自动"))
        ports = []
        for port in comports():
            self.ui.comboBoxPort.addItem(port.name)
            ports.append(port.name)
        if setting.comport not in ports:
            self.ui.comboBoxPort.setCurrentText(self.tr("自动"))
        else:
            self.ui.comboBoxPort.setCurrentText(setting.comport)

    @QtCore.pyqtSlot()
    def on_btnMatch_clicked(self):
        if MainWindow.api is not None:
            QtWidgets.QMessageBox.warning(
                self, self.tr("错误"), self.tr("请先断开连接")
            )
            return
        self.on_btnSave_clicked()
        try:
            color_rgb = bytes.fromhex(setting.color.lstrip("#"))
            api = MDP_P906(
                port=setting.comport,
                baudrate=setting.baudrate,
                address=setting.address,
                freq=int(setting.freq),
                blink=setting.blink,
                idcode=setting.idcode,
                led_color=(color_rgb[0], color_rgb[1], color_rgb[2]),
                m01_channel=int(setting.m01ch[3]),
                tx_output_power=setting.txpower,
                debug=os.environ.get("MDP_DEBUG_LOG") is not None,
            )
            idcode = api.auto_match()
        except Exception as e:
            logger.exception(self.tr("自动配对失败"))
            QtWidgets.QMessageBox.warning(self, self.tr("自动配对失败"), str(e))
            return
        finally:
            api.close()
        QtWidgets.QMessageBox.information(
            self, self.tr("自动配对成功"), f"IDCODE: {idcode}"
        )
        self.ui.lineEditIdcode.setText(idcode)
        self.on_btnSave_clicked()

    def show(self) -> None:
        self.initValues()
        self.refreshPorts()
        self.ui.lineEditColorIndicator.setStyleSheet(
            f"background-color: {setting.color}"
        )
        if self.isVisible():
            self.close()
        super().show()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        center_window(self)
        return super().showEvent(a0)

    @QtCore.pyqtSlot()
    def on_lineEditColor_editingFinished(self):
        color = self.ui.lineEditColor.text()
        try:
            _ = bytes.fromhex(color.lstrip("#"))
            self.ui.lineEditColorIndicator.setStyleSheet(f"background-color: {color}")
        except Exception:
            QtWidgets.QMessageBox.warning(
                self,
                self.tr("错误"),
                self.tr("颜色格式错误, 请输入形如#FFFFFF的16进制颜色代码"),
            )
            self.ui.lineEditColor.setText(setting.color)

    def save_settings(self):
        setting.baudrate = int(self.ui.spinBoxBaud.value())
        setting.address = ":".join(
            [
                self.ui.lineEditAddr1.text(),
                self.ui.lineEditAddr2.text(),
                self.ui.lineEditAddr3.text(),
                self.ui.lineEditAddr4.text(),
                self.ui.lineEditAddr5.text(),
            ]
        )
        setting.freq = int(self.ui.spinBoxFreq.value())
        setting.txpower = self.ui.comboBoxPower.currentText()
        setting.idcode = self.ui.lineEditIdcode.text()
        setting.color = self.ui.lineEditColor.text()
        setting.m01ch = f"CH-{int(self.ui.spinBoxM01.value())}"
        setting.comport = (
            self.ui.comboBoxPort.currentText()
            if self.ui.comboBoxPort.currentText() != self.tr("自动")
            else ""
        )
        setting.blink = self.ui.comboBoxBlink.currentText() == self.tr("闪烁")
        setting.save(SETTING_FILE)

    @QtCore.pyqtSlot()
    def on_btnSave_clicked(self):
        self.ui.btnSave.setText(self.tr("重新连接生效"))
        QtCore.QTimer.singleShot(1000, self._reset_btn_text)

    def _reset_btn_text(self):
        self.ui.btnSave.setText(self.tr("应用 / Apply"))

    @QtCore.pyqtSlot()
    def on_btnOk_clicked(self):
        self.save_settings()
        self.close()


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
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        if not OPENGL_AVAILABLE:
            self.ui.checkBoxOpenGL.setEnabled(False)
            self.ui.checkBoxOpenGL.setCheckState(False)
        self.ui.checkBoxOpenGL.clicked.connect(self.set_opengl)

    def initValues(self):
        self.ui.spinMaxFps.setValue(setting.graph_max_fps)
        self.ui.spinStateFps.setValue(setting.state_fps)
        self.ui.spinDataLength.setValue(setting.data_pts)
        self.ui.comboInterp.setCurrentIndex(setting.interp)
        self.ui.comboAvgMode.setCurrentIndex(setting.avgmode)
        if OPENGL_AVAILABLE:
            self.ui.checkBoxOpenGL.setChecked(setting.opengl)
        self.ui.spinStateVThres.setValue(setting.v_threshold)
        self.ui.spinStateIThres.setValue(setting.i_threshold)
        self.ui.checkBoxUseCali.setChecked(setting.use_cali)
        self.ui.spinCaliVk.setValue(setting.v_cali_k)
        self.ui.spinCaliVb.setValue(setting.v_cali_b)
        self.ui.spinCaliIk.setValue(setting.i_cali_k)
        self.ui.spinCaliIb.setValue(setting.i_cali_b)

    def show(self) -> None:
        self.initValues()
        if self.isVisible():
            self.close()
        super().show()

    def showEvent(self, a0: QtGui.QShowEvent) -> None:
        center_window(self)
        return super().showEvent(a0)

    @QtCore.pyqtSlot(int)
    def on_comboTheme_currentIndexChanged(self, index):
        self.set_theme(self.ui.comboTheme.currentText().lower())

    def set_theme(self, theme):
        qdarktheme.setup_theme(theme)
        MainWindow.ui.widgetGraph1.setBackground(None)
        MainWindow.ui.widgetGraph2.setBackground(None)
        MainWindow.CustomTitleBar.set_theme(theme)
        DialogSettings.CustomTitleBar.set_theme(theme)
        DialogGraphics.CustomTitleBar.set_theme(theme)

    def set_opengl(self, enable):
        setting.opengl = enable
        pg.setConfigOption("useOpenGL", enable)
        logger.info(f"OpenGL {'enabled' if enable else 'disabled'}")

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
        setting.data_pts = self.ui.spinDataLength.value()
        self.set_data_len_sig.emit(self.ui.spinDataLength.value())

    @QtCore.pyqtSlot(int)
    def on_comboInterp_currentIndexChanged(self, index):
        setting.interp = self.ui.comboInterp.currentIndex()
        self.set_interp_sig.emit(index)

    @QtCore.pyqtSlot(int)
    def on_comboAvgMode_currentIndexChanged(self, index):
        setting.avgmode = self.ui.comboAvgMode.currentIndex()

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

    @QtCore.pyqtSlot(int)
    def on_checkBoxUseCali_stateChanged(self, state: int):
        setting.use_cali = state == QtCore.Qt.CheckState.Checked

    @QtCore.pyqtSlot()
    def on_btnClose_clicked(self):
        try:
            setting.graph_max_fps = self.ui.spinMaxFps.value()
            setting.state_fps = self.ui.spinStateFps.value()
            setting.data_pts = self.ui.spinDataLength.value()
            setting.interp = self.ui.comboInterp.currentIndex()
            setting.avgmode = self.ui.comboAvgMode.currentIndex()
            setting.opengl = self.ui.checkBoxOpenGL.isChecked()
            setting.v_threshold = self.ui.spinStateVThres.value()
            setting.i_threshold = self.ui.spinStateIThres.value()
            setting.use_cali = self.ui.checkBoxUseCali.isChecked()
            setting.v_cali_k = self.ui.spinCaliVk.value()
            setting.v_cali_b = self.ui.spinCaliVb.value()
            setting.i_cali_k = self.ui.spinCaliIk.value()
            setting.i_cali_b = self.ui.spinCaliIb.value()
            setting.save(SETTING_FILE)
        except Exception as e:
            logger.error(e)
        self.close()


DialogSettings = MDPSettings()
DialogGraphics = MDPGraphics()
MainWindow.ui.btnSettings.clicked.connect(DialogSettings.show)
MainWindow.ui.btnGraphics.clicked.connect(DialogGraphics.show)
DialogGraphics.set_max_fps_sig.connect(MainWindow.set_graph_max_fps)
DialogGraphics.state_fps_sig.connect(MainWindow.set_state_fps)
DialogGraphics.set_data_len_sig.connect(MainWindow.set_data_length)
DialogGraphics.set_interp_sig.connect(MainWindow.set_interp)
app.setWindowIcon(QtGui.QIcon(ICON_PATH))

qdarktheme.setup_theme()


def show_app():
    MainWindow.show()
    MainWindow.activateWindow()  # bring window to front
    sys.exit(app.exec_())


if __name__ == "__main__":
    show_app()
