# ruff: noqa: E402

import os
import sys
import time
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


class FakeLock:
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
        self._api_lock = Lock() if use_lock else FakeLock()
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
        Whether the device is connected
        """
        return self._api.get_ConnState()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def connect(self) -> None:
        """
        Connect device
        """
        if not self.connected:
            with self._api_lock:
                ret = self._api.DevOpenOrClose()
            logger.debug(f"Connect device: {ret}")
            assert ret, ConnectionError("Failed to connect to device")
            logger.info("Device connected successfully")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def disconnect(self) -> None:
        """
        Disconnect device
        """
        if self.connected:
            with self._api_lock:
                ret = self._api.DevOpenOrClose()
            logger.debug(f"Disconnect device: {ret}")
            assert not ret, "Failed to disconnect device"
            logger.info("Device disconnected successfully")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_device_info(self) -> dict:
        """
        Get device information
        return: dict(
            device_name: str, Device model
            hardware_version: str, Hardware version
            application_version: str, Software version
            device_SN: str, Device serial number
            device_status: str, Device status (APP/BOOT)
        )
        """
        string_vars = [String(" " * 32) for _ in range(5)]
        with self._api_lock:
            ret = self._api.GetDevInfo(*string_vars)
        logger.debug(f"Get device info: {ret}")
        assert ret[0], "Failed to get device information, device may not be connected"
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
        Get device status
        return: dict(
            preset: int, Current preset group
            output: bool, Output status
            v_set: float, Set voltage V
            i_set: float, Set current A
            ovp: float, Set overvoltage protection V
            ocp: float, Set overcurrent protection A
        )
        """
        args = [Byte(0), Byte(0), UInt16(0), UInt16(0), UInt16(0), UInt16(0)]
        with self._api_lock:
            ret = self._api.GetCurrentBasic(*args)
        logger.debug(f"Get device status: {ret}")
        assert ret[0], "Failed to get device status, device may not be connected"
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
        Get preset group information
        index: Preset group index
        return: dict(
            v_set: float, Set voltage V
            i_set: float, Set current A
            ovp: float, Set overvoltage protection V
            ocp: float, Set overcurrent protection A
        )
        """
        assert 0 <= index <= 9, "Preset group index must be between 0-9"
        args = [Byte(index), UInt16(0), UInt16(0), UInt16(0), UInt16(0)]
        with self._api_lock:
            ret = self._api.GetGroupInfo(*args)
        logger.debug(f"Get preset group: {index} -> {ret}")
        assert ret[0], "Failed to get preset group information"
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
        Set preset group (must be a currently unused preset group)
        index: Preset group index
        v_set: Set voltage V
        i_set: Set current A
        ovp: Set overvoltage protection V
        ocp: Set overcurrent protection A
        """
        assert 0 <= index <= 9, "Preset group index must be between 0-9"
        args = [
            Byte(index),
            UInt16(round(i_set * 1000)),
            UInt16(round(v_set * 1000)),
            UInt16(round(ocp * 1000)),
            UInt16(round(ovp * 1000)),
        ]
        with self._api_lock:
            ret = self._api.SetGroupInfo(*args)
        logger.debug(
            f"Set preset group: {index}, {v_set}, {i_set}, {ovp}, {ocp} -> {ret}"
        )
        assert ret, "Failed to set preset group information"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def use_preset(self, index: int) -> None:
        """
        Use preset group
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
        logger.debug(f"Use preset group: {index} -> {ret}")
        assert ret, "Failed to use preset group"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def set_output(
        self,
        output: Optional[bool] = None,
        v_set: Optional[float] = None,
        i_set: Optional[float] = None,
        preset: Optional[int] = None,
    ) -> None:
        """
        Set output status
        output: Output enable
        v_set: Set voltage V
        i_set: Set current A
        preset: Used preset group
        (The above parameters are optional, if not passed, they will not be modified)
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
            close_args = [
                Byte(preset),
                UShort(0),
                UShort(0),
            ]
            with self._api_lock:
                ret = self._api.CloseOut(*close_args)
                time.sleep(0.04)
                ret &= self._api.CloseOut(*args)
        logger.debug(f"Set output: {output}, {v_set}, {i_set}, {preset} -> {ret}")
        assert ret, "Failed to set output status"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_settings(self) -> dict:
        """
        Get system settings
        return: dict(
            backlight: int, Backlight level (0-4)
            volume: int, Volume level (0-4)
            opp: float, Over power protection value <=105W
            otp: int, Over temperature protection value 50-80C
            reverse_protect: bool, Reverse connection protection
            auto_output: bool, Auto output on power-on
        )
        """
        args = [Byte(0), Byte(0), UInt16(0), UInt16(0), Byte(0), Byte(0)]
        with self._api_lock:
            ret = self._api.GetSysPar(*args)
        logger.debug(f"Get system settings: {ret}")
        assert ret[0], "Failed to get system settings"
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
        Set system settings
        backlight: Backlight level (0-4)
        volume: Volume level (0-4)
        opp: Over power protection value <=105W
        otp: Over temperature protection value 50-80C
        reverse_protect: bool, Reverse connection protection
        auto_output: bool, Auto output on power-on
        (The above parameters are optional, if not passed, they will not be modified)
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
            f"Set system settings: {{backlight: {backlight}, volume: {volume}, opp: {opp}, otp: {otp}, reverse_protect: {reverse_protect}, auto_output: {auto_output}}} -> {ret}"
        )
        assert ret, "Failed to set system settings"

    def register_output_info_callback(self, callback) -> None:
        """
        Register output information callback function
        callback: Callback function, input parameters are Uint16: voltage mV, Uint16: current mA
        """
        assert callable(callback), "Callback function must be callable"
        self._api.ReceBasicInfoEvent += self._api.ReceBasicInfo(callback)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0))
    def get_output_info(self) -> None:
        """
        Send request to get output voltage and current information (callback function needs to be registered first)
        """
        with self._api_lock:
            self._api.GetBasicInfo()

    def _callback_proxy(self, a: int, b: int):
        if self._callback:
            self._callback(a, b)

    def register_state_change_callback(self, callback) -> None:
        """
        Register connection status change callback function
        callback: Callback function
        """
        assert callable(callback), "Callback function must be callable"
        self._callback = callback

    def unregister_callback(self) -> None:
        """
        Unregister callback function
        """
        self._callback = None


if __name__ == "__main__":
    # For testing
    api = DP100()
    api.connect()
    print(api.get_device_info())
    api.set_settings(opp=150)  # overrided
    print(api.get_settings())
