import datetime
import logging
import math
import os
import random
import sys
import time
from typing import List

os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import warnings

# ignore opengl runtime warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

from threading import Lock

import numpy as np
import pyqtgraph as pg
import qdarktheme
from PyQt5 import QtCore, QtGui, QtWidgets
from lib.qframelesswindow import AcrylicWindow, FramelessWindow, TitleBar
from simple_pid import PID

OPENGL_AVAILABLE = False
try:
    import OpenGL

    OPENGL_AVAILABLE = True
    pg.setConfigOption("enableExperimental", True)
    pg.setConfigOption("antialias", True)
    logger.info("OpenGL successfully enabled")
except Exception as e:
    logger.warning(f"Enabling OpenGL failed with {e}.")

try:
    import numba as nb

    pg.setConfigOption("useNumba", True)
    logger.info("Numba successfully enabled")
except Exception as e:
    logger.warning(f"Enabling Numba failed with {e}.")
from DP100API import DP100
from DP100GUI import Ui_DialogGraphics, Ui_DialogSettings, Ui_MainWindow

api = DP100()

_PATH = os.path.dirname(__file__)
ICON_PATH = os.path.join(_PATH, "icon.ico")
qdarktheme.enable_hi_dpi()
app = QtWidgets.QApplication(sys.argv)


class FmtAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        if len(values) == 0 or max(values) < 1e6:
            return super().tickStrings(values, scale, spacing)
        else:
            return [f"{v:.2e}" for v in values]


class Data_Share:
    def __init__(self, data_length=1000) -> None:
        self.start_time = time.perf_counter()
        self.graph_start_time = time.perf_counter()
        self.last_time = 0
        self.save_datas_flag = False
        self.filter_k = 1
        self.voltage = 0
        self.current = 0
        self.power = 0
        self.energy = 0
        self.resistance = 0
        self.sync_lock = Lock()
        self.voltages = np.zeros(data_length, np.float64)
        self.currents = np.zeros(data_length, np.float64)
        self.powers = np.zeros(data_length, np.float64)
        self.resistances = np.zeros(data_length, np.float64)
        self.times = np.zeros(data_length, np.float64)
        self.update_count = data_length
        self.data_length = data_length


class Data_Record:
    def __init__(self) -> None:
        self.voltages: List[float] = []
        self.currents: List[float] = []
        self.times: List[float] = []
        self.start_time = None

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


def set_color(widget: QtWidgets.QWidget, rgb):
    color = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})" if isinstance(rgb, tuple) else rgb
    widget.setStyleSheet(f"color: {color}")


class FPSCounter(object):
    def __init__(self, max_sample=40) -> None:
        self.t = time.perf_counter()
        self.max_sample = max_sample
        self.t_list: List[float] = []
        self._fps = 0.0

    def clear(self) -> None:
        self.t = time.perf_counter()
        self.t_list = []
        self._fps = 0.0

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
        if length == 0:
            self._fps = 0.0
        else:
            fps = length / sum_t
            if self._fps < 1:
                self._fps = fps
            self._fps += (fps - self._fps) * 2 / self._fps
        return self._fps


class CustomTitleBar(TitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.label = QtWidgets.QLabel("AlienTek DP100 Controller", self)
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


class DP100GUI(QtWidgets.QMainWindow, FramelessWindow):  # QtWidgets.QMainWindow
    data = Data_Share()
    data_fps = 100
    graph_fps = 100
    graph_max_fps = 100
    graph_keep_flag = False
    graph_record_flag = False
    output_state = False
    _v_set = 0
    _i_set = 0
    open_r = 1e6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.fps_counter = FPSCounter()
        # self.windowEffect.setAcrylicEffect(self.winId(), "10101090")
        self.CustomTitleBar = CustomTitleBar(self)
        self.CustomTitleBar.set_theme("dark")
        self.ui.comboDataFps.setCurrentText(f"{self.data_fps}Hz")
        self.setTitleBar(self.CustomTitleBar)
        self.initSignals()
        self.resize(900, 780)
        self.initGraph()
        self.initTimer()
        self.update_connection_state()
        api.register_output_info_callback(self._state_callback)
        self.ui.progressBarVoltage.setMaximum(1000)
        self.ui.progressBarCurrent.setMaximum(1000)
        self._last_state_change_t = time.perf_counter()
        self.titleBar.raise_()
        self.ui.comboPreset.setItemData(0, 0, QtCore.Qt.UserRole - 1)
        self.ui.btnSeqStop.hide()
        self.ui.listSeq.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def initTimer(self):
        self.check_connection_timer = QtCore.QTimer(self)
        self.check_connection_timer.timeout.connect(self.update_connection_state)
        self.state_request_sender_timer = QtCore.QTimer(self)
        self.state_request_sender_timer.setTimerType(QtCore.Qt.PreciseTimer)
        self.state_request_sender_timer.timeout.connect(api.get_output_info)
        self.draw_graph_timer = QtCore.QTimer(self)
        self.draw_graph_timer.timeout.connect(self.draw_graph)
        self.func_sweep_timer = QtCore.QTimer(self)
        self.func_sweep_timer.timeout.connect(self._func_sweep)
        self.func_wave_gen_timer = QtCore.QTimer(self)
        self.func_wave_gen_timer.timeout.connect(self._func_wave_gen)
        self.func_keep_power_timer = QtCore.QTimer(self)
        self.func_keep_power_timer.timeout.connect(self._func_keep_power)
        self.func_seq_timer = QtCore.QTimer(self)
        self.func_seq_timer.timeout.connect(self._func_seq)
        self.graph_record_save_timer = QtCore.QTimer(self)
        self.graph_record_save_timer.timeout.connect(self._graph_record_save)

    def initSignals(self):
        self.ui.comboDataFps.currentTextChanged.connect(self._set_data_fps)
        self.ui.comboPreset.currentTextChanged.connect(self._set_preset)
        self._ignore_preset_changed_signal = False
        self.ui.comboPresetEdit.currentTextChanged.connect(self._get_preset)
        self.ui.comboGraph1Data.currentTextChanged.connect(self._set_graph1_data)
        self.ui.comboGraph2Data.currentTextChanged.connect(self._set_graph2_data)
        self.ui.spinBoxVoltage.valueChanged.connect(self._voltage_changed)
        self.ui.spinBoxCurrent.valueChanged.connect(self._current_changed)
        self.ui.comboWaveGenType.currentTextChanged.connect(self._set_wavegen_type)

    def startMyTimer(self):
        self.data.start_time = time.perf_counter()
        self.data.graph_start_time = time.perf_counter()
        self.data.last_time = 0
        self.data.energy = 0
        self.check_connection_timer.start(1000)
        self.state_request_sender_timer.start(1000 // self.data_fps)
        self.draw_graph_timer.start(1000 // self.graph_fps)

    def stopMyTimer(self):
        self.check_connection_timer.stop()
        self.state_request_sender_timer.stop()
        self.draw_graph_timer.stop()
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

    ##########  Basic Functions  ##########

    @property
    def preset(self):
        return int(self.ui.comboPreset.currentText())

    @property
    def v_set(self):
        return self._v_set

    @v_set.setter
    def v_set(self, value):
        api.set_output(
            output=self.output_state,
            v_set=value,
            i_set=self._i_set,
            preset=self.preset,
        )
        self._v_set = value
        self.ui.spinBoxVoltage.setValue(value)
        self._last_state_change_t = time.perf_counter()

    @property
    def i_set(self):
        return self._i_set

    @i_set.setter
    def i_set(self, value):
        api.set_output(
            output=self.output_state,
            v_set=self._v_set,
            i_set=value,
            preset=self.preset,
        )
        self._i_set = value
        self.ui.spinBoxCurrent.setValue(value)
        self._last_state_change_t = time.perf_counter()

    def update_output_state_text(self):
        state = api.get_state()
        to_state = state["output"]
        preset = state["preset"]
        v_set = state["v_set"]
        i_set = state["i_set"]
        if to_state:
            self.ui.btnOutput.setText("Running")
            set_color(self.ui.btnOutput, "lightgreen")
        else:
            self.ui.btnOutput.setText("Stopped")
            set_color(self.ui.btnOutput, "khaki")
        self.output_state = to_state
        self.ui.comboPreset.setCurrentText(str(preset))
        self._v_set = v_set
        self.ui.spinBoxVoltage.setValue(v_set)
        self._i_set = i_set
        self.ui.spinBoxCurrent.setValue(i_set)

    @QtCore.pyqtSlot()
    def on_btnOutput_clicked(self):
        self.output_state = not self.output_state
        self._last_state_change_t = time.perf_counter()
        api.set_output(self.output_state)
        self.update_output_state_text()
        api.set_output(self.output_state)

    def update_connection_state(self):
        state = api.connected
        if state:
            self.ui.labelConnectState.setText("Connected")
            set_color(self.ui.labelConnectState, "lightgreen")
            self.ui.frameOutputSetting.setEnabled(True)
            self.ui.frameGraph.setEnabled(True)
            if (
                self.output_state
                and self.v_set > 0
                and self.i_set > 0
                and self.data.voltage < 0.9 * self.v_set
                and self.data.current < 0.9 * self.i_set
                and time.perf_counter() - self._last_state_change_t > 0.5
            ):
                self.ui.btnOutput.setText("Error")
                set_color(self.ui.btnOutput, "red")
            elif self.ui.btnOutput.text() == "Error":
                self.update_output_state_text()
        else:
            self.ui.labelConnectState.setText("Not Connected")
            set_color(self.ui.labelConnectState, "red")
            set_color(self.ui.btnOutput, "grey")
            self.ui.frameOutputSetting.setEnabled(False)
            self.ui.frameGraph.setEnabled(False)
            self.ui.progressBarCurrent.setValue(0)
            self.ui.progressBarVoltage.setValue(0)
            self._state_callback(0, 0)
            self.stopMyTimer()

    @QtCore.pyqtSlot()
    def on_btnConnect_clicked(self):
        try:
            if api.connected:
                api.disconnect()
            else:
                api.connect()
                self._last_state_change_t = time.perf_counter()
                self.startMyTimer()
                state = api.get_state()
                self.ui.spinBoxVoltage.setValue(state["v_set"])
                self.ui.spinBoxCurrent.setValue(state["i_set"])
                self._v_set = state["v_set"]
                self._i_set = state["i_set"]
                preset = str(state["preset"])
                if preset != self.ui.comboPreset.currentText():
                    self._ignore_preset_changed_signal = True
                    self.ui.comboPreset.setCurrentText(preset)
                    self._get_preset(self.ui.comboPresetEdit.currentText())
                self.update_output_state_text()
                self.ui.btnGraphClear.clicked.emit()
        except Exception as e:
            self.ui.labelConnectState.setText("Connection Failed")
            set_color(self.ui.labelConnectState, "red")
            QtCore.QTimer.singleShot(1000, self.update_connection_state)
            return
        self.update_connection_state()

    def _state_callback(self, voltage, current):
        v = voltage / 1000
        i = current / 1000
        p = voltage * current / 1000000
        if current != 0:
            r = voltage / current
        else:
            r = self.open_r
        t1 = time.perf_counter()
        data = self.data
        with data.sync_lock:
            t = t1 - data.start_time
            data.energy += voltage * current * (t - data.last_time) / 1000000
            data.last_time = t
            data.power += (p - data.power) * data.filter_k
            data.voltage += (v - data.voltage) * data.filter_k
            data.current += (i - data.current) * data.filter_k
            data.resistance += (r - data.resistance) * data.filter_k
            if data.save_datas_flag:
                # data.voltages = np.hstack((data.voltages[1:], v))
                # data.currents = np.hstack((data.currents[1:], i))
                # data.powers = np.hstack((data.powers[1:], p))
                # data.resistances = np.hstack((data.resistances[1:], r))
                # data.times = np.hstack((data.times[1:], t1 - data.graph_start_time))
                data.voltages = np.roll(data.voltages, -1)
                data.currents = np.roll(data.currents, -1)
                data.powers = np.roll(data.powers, -1)
                data.resistances = np.roll(data.resistances, -1)
                data.times = np.roll(data.times, -1)
                data.voltages[-1] = v
                data.currents[-1] = i
                data.powers[-1] = p
                data.resistances[-1] = r
                data.times[-1] = t1 - data.graph_start_time
                if data.update_count > 0:
                    data.update_count -= 1
        if self.graph_record_flag:
            self.graph_record_data.voltages.append(v)
            self.graph_record_data.currents.append(i)
            if self.graph_record_data.start_time is None:
                self.graph_record_data.start_time = t1
            self.graph_record_data.times.append(t1 - self.graph_record_data.start_time)
        r_text = f"{data.resistance:.3f}" if data.resistance < self.open_r - 1 else "--"
        self.ui.lcdVoltage.display(f"{data.voltage:.3f}")
        self.ui.lcdCurrent.display(f"{data.current:.3f}")
        self.ui.lcdResistence.display(r_text)
        self.ui.lcdPower.display(f"{data.power:.3f}")
        self.ui.lcdAvgPower.display(f"{data.energy / t:.3f}")
        self.ui.lcdEnerge.display(f"{data.energy:.3f}")
        self.fps_counter.tick()

    def _set_filter_k(self, k):
        self.data.filter_k = k

    def _set_data_fps(self, text):
        if text != "":
            self.data_fps = int(text.replace("Hz", ""))
        self.graph_fps = min(self.data_fps, self.graph_max_fps)
        if self.state_request_sender_timer.isActive():
            self.state_request_sender_timer.stop()
            self.state_request_sender_timer.start(int(1000 / self.data_fps))
        if self.draw_graph_timer.isActive():
            self.draw_graph_timer.stop()
            self.draw_graph_timer.start(int(1000 / self.graph_fps))
        self.fps_counter.clear()

    def _set_graph_max_fps(self, fps):
        self.graph_max_fps = fps
        self._set_data_fps(self.ui.comboDataFps.currentText())

    def _set_data_length(self, length):
        save = self.data.save_datas_flag
        filter_k = self.data.filter_k
        self.data = Data_Share(length)
        self.curve1.setData(x=[], y=[])
        self.curve2.setData(x=[], y=[])
        self.data.save_datas_flag = save
        self.data.filter_k = filter_k

    @QtCore.pyqtSlot()
    def on_btnRecordClear_clicked(self):
        with self.data.sync_lock:
            self.data.start_time = time.perf_counter()
            self.data.last_time = 0
            self.data.energy = 0

    def update_progressbar(self):
        v_value = round(self.data.voltage / self.v_set * 1000) if self.v_set != 0 else 0
        i_value = round(self.data.current / self.i_set * 1000) if self.i_set != 0 else 0
        self.ui.progressBarVoltage.setValue(v_value)
        self.ui.progressBarCurrent.setValue(i_value)
        self.ui.progressBarVoltage.update()
        self.ui.progressBarCurrent.update()

    @QtCore.pyqtSlot()
    def on_spinBoxVoltage_editingFinished(self):
        v_set = self.ui.spinBoxVoltage.value()
        self.v_set = v_set

    @QtCore.pyqtSlot()
    def on_spinBoxCurrent_editingFinished(self):
        i_set = self.ui.spinBoxCurrent.value()
        self.i_set = i_set

    def _voltage_changed(self, value):
        if not self.ui.checkBoxQuickset.isChecked():
            return
        self.v_set = value

    def _current_changed(self, value):
        if not self.ui.checkBoxQuickset.isChecked():
            return
        self.i_set = value

    ##########  Image Plotting  ##########

    def initGraph(self):
        self.ui.widgetGraph1.setBackground(None)
        self.ui.widgetGraph2.setBackground(None)
        self.ui.widgetGraph1.setLabel("left", "Voltage", units="V")
        self.ui.widgetGraph2.setLabel("left", "Current", units="A")
        self._graph_units_dict = {
            "Voltage": "V",
            "Current": "A",
            "Power": "W",
            "Impedance": "Ω",
        }
        self.ui.widgetGraph1.showGrid(x=True, y=True)
        self.ui.widgetGraph2.showGrid(x=True, y=True)
        self.ui.widgetGraph1.setMouseEnabled(x=False, y=False)
        self.ui.widgetGraph2.setMouseEnabled(x=False, y=False)
        self.pen1 = pg.mkPen(color="salmon", width=1)
        self.pen2 = pg.mkPen(color="turquoise", width=1)
        self.curve1 = self.ui.widgetGraph1.plot(pen=self.pen1, clear=True)
        self.curve2 = self.ui.widgetGraph2.plot(pen=self.pen2, clear=True)
        self.data.graph_start_time = time.perf_counter()
        self.data.save_datas_flag = True
        self._graph_auto_scale_flag = True
        self.ui.widgetGraph1.setAxisItems(
            axisItems={"left": FmtAxisItem(orientation="left")}
        )
        self.ui.widgetGraph2.setAxisItems(
            axisItems={"left": FmtAxisItem(orientation="left")}
        )
        self._set_graph1_data("Voltage")
        self._set_graph2_data("Current")

    def _get_data(self, text):
        if text == "Voltage":
            return self.data.voltages[self.data.update_count :]
        elif text == "Current":
            return self.data.currents[self.data.update_count :]
        elif text == "Power":
            return self.data.powers[self.data.update_count :]
        elif text == "Impedance":
            return self.data.resistances[self.data.update_count :]
        elif text == "None":
            return None

    _typename_dict = {
        "Voltage": "V",
        "Current": "I",
        "Power": "P",
        "Impedance": "R",
    }

    def float_str(self, value, limit=1e5):
        if value > limit:
            return f"{value:.1e}"
        else:
            return f"{value:.3f}"

    def draw_graph(self):
        self.update_progressbar()
        self.ui.labelFps.setText(f"{self.fps_counter.fps:.1f}Hz")
        if self.graph_keep_flag:
            return
        type1 = self.ui.comboGraph1Data.currentText()
        type2 = self.ui.comboGraph2Data.currentText()
        data1 = self._get_data(type1)
        data2 = self._get_data(type2)
        time = self.data.times[self.data.update_count :]
        text1 = None
        text2 = None
        if data1 is not None and data1.size > 0:
            self.curve1.setData(x=time, y=data1)
            avg1 = np.mean(data1)
            max1 = np.max(data1)
            min1 = np.min(data1)
            pp1 = max1 - min1
            _ = self._typename_dict[type1]
            text1 = f"{_}avg: {self.float_str(avg1)}  {_}max: {self.float_str(max1)}  {_}min: {self.float_str(min1)}  {_}pp: {self.float_str(pp1)}"
        if data2 is not None and data2.size > 0:
            self.curve2.setData(x=time, y=data2)
            avg2 = np.mean(data2)
            max2 = np.max(data2)
            min2 = np.min(data2)
            pp2 = max2 - min2
            _ = self._typename_dict[type2]
            text2 = f"{_}avg: {self.float_str(avg2)}  {_}max: {self.float_str(max2)}  {_}min: {self.float_str(min2)}  {_}pp: {self.float_str(pp2)}"
        if text1 and text2:
            text = text1 + "  |  " + text2
        elif text1:
            text = text1
        elif text2:
            text = text2
        else:
            text = "No Info"
        self.ui.labelGraphInfo.setText(text)
        if time.size != 0 and self._graph_auto_scale_flag:
            if data1 is not None:
                max1 = np.max(data1)
                min1 = np.min(data1)
                if max1 != np.inf and min1 != -np.inf:
                    add1 = max(0.02, (max1 - min1) * 0.05)
                    self.ui.widgetGraph1.setYRange(min1 - add1, max1 + add1)
                    self.ui.widgetGraph1.setXRange(time[0], time[-1])
            if data2 is not None:
                max2 = np.max(data2)
                min2 = np.min(data2)
                if max2 != np.inf and min2 != -np.inf:
                    add2 = max(0.02, (max2 - min2) * 0.05)
                    self.ui.widgetGraph2.setYRange(min2 - add2, max2 + add2)
                    self.ui.widgetGraph2.setXRange(time[0], time[-1])

    def _set_graph1_data(self, text):
        if text == "None":
            self.ui.widgetGraph1.hide()
            return
        self.ui.widgetGraph1.show()
        self.ui.widgetGraph1.setLabel("left", text, units=self._graph_units_dict[text])

    def _set_graph2_data(self, text):
        if text == "None":
            self.ui.widgetGraph2.hide()
            return
        self.ui.widgetGraph2.show()
        self.ui.widgetGraph2.setLabel("left", text, units=self._graph_units_dict[text])

    @QtCore.pyqtSlot()
    def on_btnGraphClear_clicked(self):
        with self.data.sync_lock:
            self.data.save_datas_flag = False
            self.data.voltages = np.zeros_like(self.data.voltages)
            self.data.currents = np.zeros_like(self.data.currents)
            self.data.powers = np.zeros_like(self.data.powers)
            self.data.resistances = np.zeros_like(self.data.resistances)
            self.data.times = np.zeros_like(self.data.times)
            self.data.update_count = self.data.data_length
            self.data.graph_start_time = time.perf_counter()
            self.data.save_datas_flag = True
        self.curve1.setData(x=[], y=[])
        self.curve2.setData(x=[], y=[])

    @QtCore.pyqtSlot()
    def on_btnGraphKeep_clicked(self):
        self.graph_keep_flag = not self.graph_keep_flag
        if self.graph_keep_flag:
            self.ui.btnGraphKeep.setText("Release")
        else:
            self.ui.btnGraphKeep.setText("Hold")
        mouse_enabled = self.graph_keep_flag or (not self._graph_auto_scale_flag)
        self.ui.widgetGraph1.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)
        self.ui.widgetGraph2.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)

    @QtCore.pyqtSlot()
    def on_btnGraphAutoScale_clicked(self):
        self._graph_auto_scale_flag = not self._graph_auto_scale_flag
        if self._graph_auto_scale_flag:
            self.ui.btnGraphAutoScale.setText("Auto")
        else:
            self.ui.btnGraphAutoScale.setText("Manual")
        mouse_enabled = self.graph_keep_flag or (not self._graph_auto_scale_flag)
        self.ui.widgetGraph1.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)
        self.ui.widgetGraph2.setMouseEnabled(x=mouse_enabled, y=mouse_enabled)

    @QtCore.pyqtSlot()
    def on_btnGraphRecord_clicked(self):
        self.graph_record_flag = not self.graph_record_flag
        if self.graph_record_flag:
            self.graph_record_data = Data_Record()
            time_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
            self.graph_record_filename = f"./record_{time_str}.csv"
            self.ui.btnGraphRecord.setText("Stop")
            self.graph_record_save_timer.start(5000)
        else:
            self.graph_record_save_timer.stop()
            self.graph_record_data.to_csv(self.graph_record_filename)
            self.graph_record_data = Data_Record()
            msg_box = QtWidgets.QMessageBox()
            msg_box.setWindowTitle("Recording Complete")
            msg_box.setText(f"Data saved to: {self.graph_record_filename[2:]}")
            msg_box.exec_()
            self.ui.btnGraphRecord.setText("Record")

    def _graph_record_save(self):
        if self.graph_record_flag:
            self.graph_record_data.to_csv(self.graph_record_filename)
        else:
            self.graph_record_save_timer.stop()

    ######### Auxiliary Functions - Preset Group #########

    def _check_edit_presets(self):
        if (
            self.ui.comboPresetEdit.currentText() == self.ui.comboPreset.currentText()
            or self.ui.comboPresetEdit.currentText() == "0"
        ):
            self.ui.btnPresetSave.setText("Cannot Modify")
            self.ui.btnPresetSave.setEnabled(False)
        else:
            self.ui.btnPresetSave.setText("Save")
            self.ui.btnPresetSave.setEnabled(True)

    def _set_preset(self, text):
        if self._ignore_preset_changed_signal:
            self._ignore_preset_changed_signal = False
            return
        preset = int(text)
        if preset == 0:
            return
        get = api.get_preset(preset)
        now_state = self.output_state
        api.set_output(False)
        api.use_preset(preset)
        self._v_set = get["v_set"]
        self._i_set = get["i_set"]
        api.set_output(
            preset=preset, output=now_state, v_set=self.v_set, i_set=self.i_set
        )
        self.ui.spinBoxVoltage.setValue(self.v_set)
        self.ui.spinBoxCurrent.setValue(self.i_set)
        self._check_edit_presets()

    @QtCore.pyqtSlot()
    def on_btnPresetSave_clicked(self):
        preset = int(self.ui.comboPresetEdit.currentText())
        v_set = self.ui.spinBoxPresetVoltage.value()
        i_set = self.ui.spinBoxPresetCurrent.value()
        ovp = self.ui.spinBoxPresetOvp.value()
        ocp = self.ui.spinBoxPresetOcp.value()
        try:
            api.set_preset(preset, v_set, i_set, ovp, ocp)
            self.ui.btnPresetSave.setText("Save Successful")
        except:
            self.ui.btnPresetSave.setText("Save Failed")
        QtCore.QTimer.singleShot(1000, lambda: self.ui.btnPresetSave.setText("Save"))

    def _get_preset(self, text):
        preset = int(text)
        get = api.get_preset(preset)
        self.ui.spinBoxPresetVoltage.setValue(get["v_set"])
        self.ui.spinBoxPresetCurrent.setValue(get["i_set"])
        self.ui.spinBoxPresetOvp.setValue(get["ovp"])
        self.ui.spinBoxPresetOcp.setValue(get["ocp"])
        self._check_edit_presets()

    ######### Auxiliary Functions - Parameter Scan #########

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
            except:
                self.ui.btnSweep.setText("Invalid Parameter")
                QtCore.QTimer.singleShot(
                    1000, lambda: self.ui.btnSweep.setText("Disabled")
                )
                return
            self._sweep_temp = None
            self.func_sweep_timer.start(int(self._sweep_delay * 1000))
            self.ui.btnSweep.setText("Enabled")
            if self._sweep_target == "Voltage":
                self.ui.spinBoxVoltage.setEnabled(False)
            elif self._sweep_target == "Current":
                self.ui.spinBoxCurrent.setEnabled(False)
            self.ui.scrollAreaSweep.setEnabled(False)
            if not self.output_state:
                self.v_set = self._sweep_start
                self.on_btnOutput_clicked()

    def stop_func_sweep(self):
        self.func_sweep_timer.stop()
        self.ui.btnSweep.setText("Disabled")
        if self._sweep_target == "Voltage":
            self.ui.spinBoxVoltage.setEnabled(True)
        elif self._sweep_target == "Current":
            self.ui.spinBoxCurrent.setEnabled(True)
        self.ui.scrollAreaSweep.setEnabled(True)

    def _func_sweep(self):
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
        if self._sweep_target == "Voltage":
            self.v_set = self._sweep_temp
        elif self._sweep_target == "Current":
            self.i_set = self._sweep_temp

    ######### Auxiliary Functions - Generator #########

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
            except:
                self.ui.btnWaveGen.setText("Invalid Parameter")
                QtCore.QTimer.singleShot(
                    1000, lambda: self.ui.btnWaveGen.setText("Disabled")
                )
                return
            self._wavegen_start_time = time.perf_counter()
            self.func_wave_gen_timer.start(int(1000 / self._wavegen_loopfreq))
            self.ui.btnWaveGen.setText("Enabled")
            self.ui.spinBoxWaveGenLoopFreq.setEnabled(False)
            self.ui.spinBoxVoltage.setEnabled(False)
            if not self.output_state:
                self.v_set = self._wavegen_lowlevel
                self.on_btnOutput_clicked()

    def stop_func_wave_gen(self):
        self.func_wave_gen_timer.stop()
        self.ui.btnWaveGen.setText("Disabled")
        self.ui.spinBoxWaveGenLoopFreq.setEnabled(True)
        self.ui.spinBoxVoltage.setEnabled(True)

    def _set_wavegen_type(self, _):
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

    def _func_wave_gen(self):
        t = time.perf_counter() - self._wavegen_start_time
        if self._wavegen_type == "Sine Wave":
            voltage = (
                self._wavegen_lowlevel
                + (self._wavegen_highlevel - self._wavegen_lowlevel)
                * (math.sin(2 * math.pi / self._wavegen_period * t) + 1.0)
                / 2
            )
        elif self._wavegen_type == "Square Wave":
            voltage = (
                self._wavegen_highlevel
                if math.sin(2 * math.pi / self._wavegen_period * t) > 0
                else self._wavegen_lowlevel
            )
        elif self._wavegen_type == "Triangle Wave":
            mul = (t / self._wavegen_period) % 2
            mul = mul if mul < 1 else 2 - mul
            voltage = (
                self._wavegen_lowlevel
                + (self._wavegen_highlevel - self._wavegen_lowlevel) * mul
            )
        elif self._wavegen_type == "Sawtooth Wave":
            voltage = (self._wavegen_highlevel - self._wavegen_lowlevel) * (
                (t / self._wavegen_period) % 1
            ) + self._wavegen_lowlevel
        elif self._wavegen_type == "Noise":
            voltage = random.uniform(self._wavegen_lowlevel, self._wavegen_highlevel)
        else:
            voltage = 0
        voltage = max(
            min(voltage, self._wavegen_highlevel), self._wavegen_lowlevel
        )  # Limiting
        self.v_set = voltage

    ######### Auxiliary Functions - Power Hold #########

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
            except:
                self.ui.btnKeepPower.setText("Invalid Parameter")
                QtCore.QTimer.singleShot(
                    1000, lambda: self.ui.btnKeepPower.setText("Disabled")
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
            self.func_keep_power_timer.start(int(1000 / self._keep_power_loopfreq))
            self.ui.btnKeepPower.setText("Enabled")
            self.ui.spinBoxVoltage.setEnabled(False)
            self.ui.spinBoxKeepPowerLoopFreq.setEnabled(False)

    def stop_func_keep_power(self):
        self.func_keep_power_timer.stop()
        self.ui.btnKeepPower.setText("Disabled")
        self.ui.spinBoxVoltage.setEnabled(True)
        self.ui.spinBoxKeepPowerLoopFreq.setEnabled(True)

    def _func_keep_power(self):
        if not self.output_state:
            if self._keep_power_pid.auto_mode:
                self._keep_power_pid.set_auto_mode(False)
            voltage = 0
        else:
            if not self._keep_power_pid.auto_mode:
                self._keep_power_pid.set_auto_mode(True, last_output=self.v_set)
            voltage = self._keep_power_pid(self.data.power)
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

    ######### Auxiliary Functions - Sequence #########

    def _seq_btn_disable(self):
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

    def _seq_btn_enable(self):
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
        self._seq_btn_disable()
        self._start_seq(loop=False)
        if not self.output_state:
            self.ui.btnOutput.click()

    @QtCore.pyqtSlot()
    def on_btnSeqLoop_clicked(self):
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        self._seq_btn_disable()
        self._start_seq(loop=True)
        if not self.output_state:
            self.ui.btnOutput.click()

    @QtCore.pyqtSlot()
    def on_btnSeqStop_clicked(self):
        self.func_seq_timer.stop()
        self._seq_btn_enable()

    # listSeq Delete
    def _seq_del_item(self):
        row = self.ui.listSeq.currentRow()
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        if row == -1:
            row = cnt - 1
        self.ui.listSeq.takeItem(row)
        self.ui.listSeq.setCurrentRow(max(row - 1, 0))

    def _seq_edit_item(self):
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
            "Edit Action",
            "Please ensure that the action text format is correct after modification, otherwise the action cannot be recognized",
            text=text,
        )
        if not ok:
            return
        item.setText(text)

    def _seq_clear_all(self):
        ok = QtWidgets.QMessageBox.question(
            self,
            "Clear Sequence",
            "Are you sure you want to clear the sequence?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )
        if ok == QtWidgets.QMessageBox.Yes:
            self.ui.listSeq.clear()

    # listSeq Context Menu (listSeq)
    @QtCore.pyqtSlot(QtCore.QPoint)
    def on_listSeq_customContextMenuRequested(self, pos):
        row = self.ui.listSeq.currentRow()
        cnt = self.ui.listSeq.count()
        if cnt == 0:
            return
        if row == -1:
            return
        menu = QtWidgets.QMenu()
        menu.addAction("Edit", lambda: self._seq_edit_item())
        menu.addAction("Delete", lambda: self._seq_del_item())
        menu.addAction("Clear", lambda: self._seq_clear_all())
        menu.exec_(QtGui.QCursor.pos())

    # Double-click to Edit
    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_listSeq_itemDoubleClicked(self, item):
        self._seq_edit_item()

    @QtCore.pyqtSlot()
    def on_btnSeqDelay_clicked(self):
        row = self.ui.listSeq.currentRow()
        delay, ok = QtWidgets.QInputDialog.getInt(
            self, "Enter Delay", "Enter Delay Time (ms)", 1000, 0, 100000, 1
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"Delay {delay} ms")
        self.ui.listSeq.setCurrentRow(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqWaitTime_clicked(self):
        row = self.ui.listSeq.currentRow()
        time_now_str = datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S")
        wait_time, ok = QtWidgets.QInputDialog.getText(
            self,
            "Enter Wait Time",
            "Enter Wait Time (format: YYYY-MM-DD HH:MM:SS)",
            text=time_now_str,
        )
        if not ok:
            return
        try:
            datetime.datetime.strptime(wait_time, "%y-%m-%d %H:%M:%S")
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Incorrect Time Format")
            return
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"Wait {wait_time}")
        self.ui.listSeq.setCurrentRow(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqVoltage_clicked(self):
        row = self.ui.listSeq.currentRow()
        voltage, ok = QtWidgets.QInputDialog.getDouble(
            self, "Enter Voltage", "Enter Voltage Value [V]", 1, 0, 30, 2
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"Voltage {voltage:.2f} V")
        self.ui.listSeq.setCurrentRow(row + 1)

    @QtCore.pyqtSlot()
    def on_btnSeqCurrent_clicked(self):
        row = self.ui.listSeq.currentRow()
        current, ok = QtWidgets.QInputDialog.getDouble(
            self, "Enter Current", "Enter Current Value [A]", 1, 0, 5, 3
        )
        if not ok:
            return
        self.ui.listSeq.insertItem(row + 1, f"Current {current:.3f} A")
        self.ui.listSeq.setCurrentRow(row + 1)

    def _switch_to_seq(self, index) -> bool:
        if index > self._seq_cnt:
            return False
        item = self.ui.listSeq.item(index)
        if item is None:
            return False
        self._seq_index = index
        self.ui.listSeq.setCurrentRow(index)
        text = item.text()
        self._seq_type = text.split(" ")[0]
        if self._seq_type == "Wait":
            self._seq_value = datetime.datetime.strptime(
                text[len(self._seq_type) + 1 :], "%y-%m-%d %H:%M:%S"
            )
        else:
            self._seq_value = float(text[len(self._seq_type) + 1 : -2])  # type: ignore
        if self._seq_type in ("Delay", "Wait") or self._seq_index == 0:
            self._seq_time = time.perf_counter()
        return True

    def _start_seq(self, loop=False):
        self._seq_loop = loop
        self._seq_index = 0
        self._seq_cnt = self.ui.listSeq.count()
        self._switch_to_seq(0)
        self.func_seq_timer.start(1)

    def _func_seq(self):
        now = time.perf_counter()
        if self._seq_type == "Delay":
            if now - self._seq_time < self._seq_value / 1000:
                return
        elif self._seq_type == "Wait":
            now = datetime.datetime.now()
            if now < self._seq_value:
                return
        elif self._seq_type == "Voltage":
            self.v_set = self._seq_value
        elif self._seq_type == "Current":
            self.i_set = self._seq_value
        else:
            raise ValueError("Unknown seq type")
        if not self._switch_to_seq(self._seq_index + 1):
            if self._seq_loop:
                self._switch_to_seq(0)
            else:
                self.func_seq_timer.stop()
                self._seq_btn_enable()

    @QtCore.pyqtSlot()
    def on_btnSeqSave_clicked(self):
        if self.ui.listSeq.count() == 0:
            return
        # Save to File
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save", "", "Text File (*.txt)"
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
        # Load from File
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open", "", "Text File (*.txt)"
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
                assert _[0] in ["Delay", "Voltage", "Current", "Wait"]
                if _[0] != "Wait":
                    assert _[2] in ["ms", "V", "A"]
                    float(_[1])
                self.ui.listSeq.addItem(line)
            except:
                QtWidgets.QMessageBox.warning(
                    self, "Error", f"Data Validation Error: {line}"
                )
                return


MainWindow = DP100GUI()


class DP100Settings(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogSettings()
        self.ui.setupUi(self)
        self.api_lock = QtCore.QMutex()
        api._api_lock = QtCore.QMutexLocker(self.api_lock)

    def initValues(self):
        settings = api.get_settings()
        self.ui.spinBoxBacklight.setValue(settings["backlight"])
        self.ui.spinBoxVolume.setValue(settings["volume"])
        self.ui.spinBoxOtp.setValue(settings["otp"])
        self.ui.spinBoxOpp.setValue(settings["opp"])
        self.ui.checkBoxRevProtect.setChecked(settings["reverse_protect"])
        self.ui.checkBoxAuto.setChecked(settings["auto_output"])

    def show(self) -> None:
        if not api.connected:
            QtWidgets.QMessageBox.warning(self, "Error", "Device Not Connected")
            return
        self.initValues()
        return super().show()

    @QtCore.pyqtSlot()
    def on_btnSave_clicked(self):
        settings = (
            int(self.ui.spinBoxBacklight.value()),
            int(self.ui.spinBoxVolume.value()),
            self.ui.spinBoxOpp.value(),
            int(self.ui.spinBoxOtp.value()),
            bool(self.ui.checkBoxRevProtect.isChecked()),
            bool(self.ui.checkBoxAuto.isChecked()),
        )
        api.set_settings(*settings)
        self.ui.btnSave.setText("Save Successful")
        QtCore.QTimer.singleShot(1000, self._reset_btn_text)

    def _reset_btn_text(self):
        self.ui.btnSave.setText("Save")


class DP100Graphics(QtWidgets.QDialog):
    set_max_fps_sig = QtCore.pyqtSignal(float)
    set_data_len_sig = QtCore.pyqtSignal(int)
    set_filter_k_sig = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogGraphics()
        self.ui.setupUi(self)
        if not OPENGL_AVAILABLE:
            self.ui.checkBoxOpenGL.setEnabled(False)
        # connect signals
        self.ui.radioDark.clicked.connect(lambda: self.set_theme("dark"))
        self.ui.radioLight.clicked.connect(lambda: self.set_theme("light"))
        self.ui.radioAuto.clicked.connect(lambda: self.set_theme("auto"))
        self.ui.checkBoxOpenGL.clicked.connect(self.set_opengl)
        self.ui.comboFilterK.currentTextChanged.connect(self.set_filter)

    def set_theme(self, theme):
        # app.setStyleSheet(qdarktheme.load_stylesheet(theme))
        qdarktheme.setup_theme(theme)
        MainWindow.ui.widgetGraph1.setBackground(None)
        MainWindow.ui.widgetGraph2.setBackground(None)
        MainWindow.CustomTitleBar.set_theme(theme)

    def set_opengl(self, enable):
        pg.setConfigOption("useOpenGL", enable)
        logger.info(f"OpenGL {'enabled' if enable else 'disabled'}")

    def on_spinMaxFps_editingFinished(self):
        self.set_max_fps_sig.emit(self.ui.spinMaxFps.value())

    def on_spinDataLength_editingFinished(self):
        self.set_data_len_sig.emit(self.ui.spinDataLength.value())

    # def on_spinFilterK_editingFinished(self):
    #     self.set_filter_k_sig.emit(self.ui.spinFilterK.value())

    def set_filter(self, _=None) -> None:
        text = self.ui.comboFilterK.currentText()
        if text == "None":
            self.set_filter_k_sig.emit(1)
        elif text == "Low":
            self.set_filter_k_sig.emit(0.25)
        elif text == "Medium":
            self.set_filter_k_sig.emit(0.1)
        elif text == "High":
            self.set_filter_k_sig.emit(0.01)
        elif text == "Very High":
            self.set_filter_k_sig.emit(0.001)

    def _init_spin(self, length, fps):
        self.ui.spinDataLength.setValue(length)
        self.ui.spinMaxFps.setValue(fps)


DialogSettings = DP100Settings()
DialogGraphics = DP100Graphics()
DialogGraphics._init_spin(MainWindow.data.data_length, MainWindow.graph_max_fps)
MainWindow.ui.btnSettings.clicked.connect(DialogSettings.show)
MainWindow.ui.btnGraphics.clicked.connect(DialogGraphics.show)
DialogGraphics.set_max_fps_sig.connect(MainWindow._set_graph_max_fps)
DialogGraphics.set_data_len_sig.connect(MainWindow._set_data_length)
DialogGraphics.set_filter_k_sig.connect(MainWindow._set_filter_k)
# app.setStyleSheet(qdarktheme.load_stylesheet())
app.setWindowIcon(QtGui.QIcon(ICON_PATH))

qdarktheme.setup_theme()


def show_app():
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    show_app()
