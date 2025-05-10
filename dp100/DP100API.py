# ruff: noqa: E402

import os
import sys
from platform import architecture

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

if architecture()[0] == "32bit":
    dll_name = "ATK-DP100DLL(x86)_2.0"
elif architecture()[0] == "64bit":
    dll_name = "ATK-DP100DLL(x64)_2.0"
else:
    raise Exception("Unknown architecture")
logger.info(f"Loading {dll_name}.dll")


sys.path.append(os.path.dirname(__file__))
from pythonnet import load as load_pythonnet

load_pythonnet("netfx")
import clr

dll = clr.AddReference(dll_name)
logger.success(f"Loaded dll info: {dll}, {dll.Location}, {dll.FullName}")

from threading import Lock
from typing import Callable, Optional

from ATK_DP100DLL import ATKDP100API  # type: ignore
from System import Byte, String, UInt16  # type: ignore

UShort = UInt16


class Fake_Lock:
    def __enter__(self) -> bool:
        return True

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        return True

    def release(self) -> None:
        pass


class DP100:
    def __init__(self, use_lock: bool = False) -> None:
        self._api = ATKDP100API()
        self._api_lock = Lock() if use_lock else Fake_Lock()
        self._callback: Optional[Callable] = None
        self._api.DevStateChanageEvent = self._api.DevStateChanage(self._callback_proxy)

    def __enter__(self) -> "DP100":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.disconnect()
        except Exception:
            pass

    def __del__(self):
        try:
            self.disconnect()
        except Exception:
            pass

    @staticmethod
    def _print_api_methods() -> list:
        api = ATKDP100API()
        method_list = api.__class__.__dict__.keys()
        for method in method_list:
            if not method.startswith("_") and callable(getattr(api, method)):
                print(f"Method: {method}\nHelp: {getattr(api, method).__doc__}\n")
        return method_list

    @property
    def connected(self) -> bool:
        """
        设备是否连接
        """
        return self._api.get_ConnState()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def connect(self) -> None:
        """
        连接设备
        """
        if not self.connected:
            with self._api_lock:
                ret = self._api.DevOpenOrClose()
            logger.debug(f"连接设备: {ret}")
            assert ret, ConnectionError("连接设备失败")
            logger.info("连接设备成功")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def disconnect(self) -> None:
        """
        断开设备
        """
        if self.connected:
            with self._api_lock:
                ret = self._api.DevOpenOrClose()
            logger.debug(f"断开设备: {ret}")
            assert not ret, "断开设备失败"
            logger.info("断开设备成功")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_device_info(self) -> dict:
        """
        获取设备信息
        return: dict(
            device_name: str, 设备型号
            hardware_version: str, 硬件版本
            application_version: str, 软件版本
            device_SN: str, 设备序列号
            device_status: str, 设备状态(APP/BOOT)
        )
        """
        string_vars = [String(" " * 32) for _ in range(5)]
        with self._api_lock:
            ret = self._api.GetDevInfo(*string_vars)
        logger.debug(f"获取设备信息: {ret}")
        assert ret[0], "获取设备信息失败, 设备可能未连接"
        return {
            "device_name": str(ret[1]).replace("\uf8f5", "").replace("\x00", ""),
            "hardware_version": str(ret[2]),
            "application_version": str(ret[3]),
            "device_SN": str(ret[4]),
            "device_status": str(ret[5]),
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_state(self) -> dict:
        """
        获取设备状态
        return: dict(
            preset: int, 当前预设组
            output: bool, 输出状态
            v_set: float, 设定电压 V
            i_set: float, 设定电流 A
            ovp: float, 设定过压保护 V
            ocp: float, 设定过流保护 A
        )
        """
        args = [Byte(0), Byte(0), UInt16(0), UInt16(0), UInt16(0), UInt16(0)]
        with self._api_lock:
            ret = self._api.GetCurrentBasic(*args)
        logger.debug(f"获取设备状态: {ret}")
        assert ret[0], "获取设备状态失败, 设备可能未连接"
        return {
            "preset": int(ret[1]),
            "output": bool(ret[2]),
            "v_set": float(ret[3]) / 1000,
            "i_set": float(ret[4]) / 1000,
            "ovp": float(ret[5]) / 1000,
            "ocp": float(ret[6]) / 1000,
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_preset(self, index: int) -> dict:
        """
        获取预设组信息
        index: 预设组索引
        return: dict(
            v_set: float, 设定电压 V
            i_set: float, 设定电流 A
            ovp: float, 设定过压保护 V
            ocp: float, 设定过流保护 A
        )
        """
        assert 0 <= index <= 9, "预设组索引必须在0-9之间"
        args = [Byte(index), UInt16(0), UInt16(0), UInt16(0), UInt16(0)]
        with self._api_lock:
            ret = self._api.GetGroupInfo(*args)
        logger.debug(f"获取预设组: {index} -> {ret}")
        assert ret[0], "获取预设组信息失败"
        return {
            "v_set": float(ret[2]) / 1000,
            "i_set": float(ret[1]) / 1000,
            "ovp": float(ret[4]) / 1000,
            "ocp": float(ret[3]) / 1000,
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def set_preset(
        self, index: int, v_set: float, i_set: float, ovp: float, ocp: float
    ) -> None:
        """
        设置预设组（必须是当前未使用的预设组）
        index: 预设组索引
        v_set: 设定电压 V
        i_set: 设定电流 A
        ovp: 设定过压保护 V
        ocp: 设定过流保护 A
        """
        assert 0 <= index <= 9, "预设组索引必须在0-9之间"
        args = [
            Byte(index),
            UInt16(round(i_set * 1000)),
            UInt16(round(v_set * 1000)),
            UInt16(round(ocp * 1000)),
            UInt16(round(ovp * 1000)),
        ]
        with self._api_lock:
            ret = self._api.SetGroupInfo(*args)
        logger.debug(f"设置预设组: {index}, {v_set}, {i_set}, {ovp}, {ocp} -> {ret}")
        assert ret, "设置预设组信息失败"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def use_preset(self, index: int) -> None:
        """
        使用预设组
        """
        args = [
            Byte(index),
            UInt16(0),
            UInt16(0),
            UInt16(0),
            UInt16(0),
        ]
        with self._api_lock:
            ret = self._api.UseGroup(*args)
        logger.debug(f"使用预设组: {index} -> {ret}")
        assert ret, "使用预设组失败"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def set_output(
        self,
        output: Optional[bool] = None,
        v_set: Optional[float] = None,
        i_set: Optional[float] = None,
        preset: Optional[int] = None,
    ) -> None:
        """
        设置输出状态
        output: 输出使能
        v_set: 设定电压 V
        i_set: 设定电流 A
        preset: 使用的预设组
        (上述参数均为可选参数，若不传入则不修改)
        """
        if output is None or v_set is None or i_set is None or preset is None:
            state = self.get_state()
            output = state["output"] if output is None else output
            v_set = state["v_set"] if v_set is None else v_set
            i_set = state["i_set"] if i_set is None else i_set
            preset = state["preset"] if preset is None else preset
        args = [
            Byte(preset),
            UShort(round(i_set * 1000)),
            UShort(round(v_set * 100) * 10),
        ]
        if output:
            with self._api_lock:
                ret = self._api.OpenOut(*args)
        else:
            with self._api_lock:
                ret = self._api.CloseOut(*args)
        logger.debug(f"设置输出: {output}, {v_set}, {i_set}, {preset} -> {ret}")
        assert ret, "设置输出状态失败"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_settings(self) -> dict:
        """
        获取系统设置
        return: dict(
            backlight: int, 背光等级(0-4)
            volume: int, 音量等级(0-4)
            opp: float, 过功率保护值 <=105W
            otp: int, 过热保护值 50-80C
            reverse_protect: bool, 反接保护
            auto_output: bool, 上电自动输出
        )
        """
        args = [Byte(0), Byte(0), UInt16(0), UInt16(0), Byte(0), Byte(0)]
        with self._api_lock:
            ret = self._api.GetSysPar(*args)
        logger.debug(f"获取系统设置: {ret}")
        assert ret[0], "获取系统设置失败"
        return {
            "backlight": int(ret[1]),
            "volume": int(ret[2]),
            "opp": float(ret[3]) / 10,
            "otp": int(ret[4]),
            "reverse_protect": bool(ret[5]),
            "auto_output": bool(ret[6]),
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def set_settings(
        self,
        backlight: Optional[int] = None,
        volume: Optional[int] = None,
        opp: Optional[float] = None,
        otp: Optional[int] = None,
        reverse_protect: Optional[bool] = None,
        auto_output: Optional[bool] = None,
    ) -> None:
        """
        设置系统设置
        backlight: 背光等级(0-4)
        volume: 音量等级(0-4)
        opp: 过功率保护值 <=105W
        otp: 过热保护值 50-80C
        reverse_protect: bool, 反接保护
        auto_output: bool, 上电自动输出
        (上述参数均为可选参数，若不传入则不修改)
        """
        settings = self.get_settings()
        appver = self.get_device_info()["application_version"]
        backlight = settings["backlight"] if backlight is None else backlight
        volume = settings["volume"] if volume is None else volume
        opp = settings["opp"] if opp is None else opp
        otp = settings["otp"] if otp is None else otp
        reverse_protect = (
            settings["reverse_protect"] if reverse_protect is None else reverse_protect
        )
        auto_output = settings["auto_output"] if auto_output is None else auto_output
        args = [
            str(appver),
            Byte(backlight),
            Byte(volume),
            UShort(round(opp * 10)),
            UShort(otp),
            Byte(reverse_protect),
            Byte(auto_output),
        ]
        with self._api_lock:
            ret = self._api.SetSysPar(*args)
        logger.debug(
            f"设置系统设置: {{backlight: {backlight}, volume: {volume}, opp: {opp}, otp: {otp}, reverse_protect: {reverse_protect}, auto_output: {auto_output}}} -> {ret}"
        )
        assert ret, "设置系统设置失败"

    def register_output_info_callback(self, callback) -> None:
        """
        注册输出信息回调函数
        callback: 回调函数, 传入参数为 Uint16: 电压 mV, Uint16: 电流 mA
        """
        assert callable(callback), "回调函数必须是可调用的"
        self._api.ReceBasicInfoEvent += self._api.ReceBasicInfo(callback)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_output_info(self) -> None:
        """
        发送请求获取输出电压电流信息 (需先注册回调函数)
        """
        with self._api_lock:
            self._api.GetBasicInfo()

    def _callback_proxy(self, a: int, b: int):
        if self._callback:
            self._callback(a, b)

    def register_state_change_callback(self, callback) -> None:
        """
        注册连接状态变化回调函数
        callback: 回调函数
        """
        assert callable(callback), "回调函数必须是可调用的"
        self._callback = callback

    def unregister_callback(self) -> None:
        """
        注销回调函数
        """
        self._callback = None


if __name__ == "__main__":
    # 用于测试
    api = DP100()
    api.connect()
    print(api.get_device_info())
    api.set_settings(opp=150)  # overrided
    print(api.get_settings())
