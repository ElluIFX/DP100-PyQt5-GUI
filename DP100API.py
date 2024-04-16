from platform import architecture

if architecture()[0] == "32bit":
    dll_name = "ATK-DP100DLL(x86)_2.0"
elif architecture()[0] == "64bit":
    dll_name = "ATK-DP100DLL(x64)_2.0"
else:
    raise Exception("Unknown architecture")
print(f"Loading {dll_name}.dll")

import logging
import os
import sys
from threading import Lock

sys.path.append(os.path.dirname(__file__))
from pythonnet import load as load_pythonnet

load_pythonnet("netfx")
import clr

dll = clr.AddReference(dll_name)
print(f"Loaded dll info: {dll}, {dll.Location}, {dll.FullName}")

from typing import Optional

from ATK_DP100DLL import ATKDP100API  # type: ignore
from System import Array, Byte, String, UInt16  # type: ignore

UShort = UInt16

logger = logging.getLogger("ATK-DP100")


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
    def __init__(self) -> None:
        self._api = ATKDP100API()
        self._api_lock = Lock()

    def __enter__(self) -> "DP100":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.disconnect()
        except:
            pass

    def __del__(self):
        try:
            self.disconnect()
        except:
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
        Is the device connected?
        """
        return self._api.get_ConnState()

    def connect(self) -> None:
        """
        Connect device
        """
        if not self.connected:
            with self._api_lock:
                ret = self._api.DevOpenOrClose()
            assert ret, ConnectionError("Failed to connect to the device")
            # error_count = 0
            # while not self.connected:
            #     error_count += 1
            #     if error_count > 3:
            #         raise ConnectionError("Failed to connect to the device")
            #     logger.warning(f"Failed to connect to the device ({ret}), retrying: {error_count}")
            #     time.sleep(1)
            #     ret = self._api.DevOpenOrClose()
            logger.info("Device connected successfully")

    def disconnect(self) -> None:
        """
        Disconnect device
        """
        if self.connected:
            with self._api_lock:
                ret = self._api.DevOpenOrClose()
            assert not ret, "Failed to disconnect device"
            logger.info("Device disconnected successfully")

    def get_device_info(self) -> dict:
        """
        Retrieve device information

        return: dict(
            device_name: str, Device model
            hardware_version: str, Hardware version
            application_version: str, Software version
            device_SN: str, Device serial number
            device_status: str, Device status (APP/BOOT)
        """
        string_vars = [String(" " * 32) for _ in range(5)]
        with self._api_lock:
            ret = self._api.GetDevInfo(*string_vars)
        assert ret[0], "Failed to retrieve device information, the device may not be connected"
        return {
            "device_name": str(ret[1]).replace("\uf8f5", "").replace("\x00", ""),
            "hardware_version": str(ret[2]),
            "application_version": str(ret[3]),
            "device_SN": str(ret[4]),
            "device_status": str(ret[5]),
        }

    def get_state(self) -> dict:
        """
        Retrieve device status
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
        assert ret[0], "Failed to retrieve device status, the device may not be connected"
        return {
            "preset": int(ret[1]),
            "output": bool(ret[2]),
            "v_set": float(ret[3]) / 1000,
            "i_set": float(ret[4]) / 1000,
            "ovp": float(ret[5]) / 1000,
            "ocp": float(ret[6]) / 1000,
        }

    def get_preset(self, index: int) -> dict:
        """
        Retrieve preset group information
        index: Preset group index
        return: dict(
            v_set: float, Set voltage V
            i_set: float, Set current A
            ovp: float, Set overvoltage protection V
            ocp: float, Set overcurrent protection A
        )
        """
        assert 0 <= index <= 9, "Preset group index must be between 0 and 9"
        args = [Byte(index), UInt16(0), UInt16(0), UInt16(0), UInt16(0)]
        with self._api_lock:
            ret = self._api.GetGroupInfo(*args)
        assert ret[0], "Failed to retrieve preset group information"
        return {
            "v_set": float(ret[2]) / 1000,
            "i_set": float(ret[1]) / 1000,
            "ovp": float(ret[4]) / 1000,
            "ocp": float(ret[3]) / 1000,
        }

    def set_preset(
        self, index: int, v_set: float, i_set: float, ovp: float, ocp: float
    ) -> None:
        """
        Set preset group (must be an unused preset group)
        index: Preset group index
        v_set: Set voltage V
        i_set: Set current A
        ovp: Set overvoltage protection V
        ocp: Set overcurrent protection A
        """
        assert 0 <= index <= 9, "Index for the preset group must be between 0 and 9"
        args = [
            Byte(index),
            UInt16(round(i_set * 1000)),
            UInt16(round(v_set * 1000)),
            UInt16(round(ocp * 1000)),
            UInt16(round(ovp * 1000)),
        ]
        with self._api_lock:
            ret = self._api.SetGroupInfo(*args)
        assert ret, "Failed to set preset group information"

    def use_preset(self, index: int) -> None:
        """
        Using preset group
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
        assert ret, "Failed to use preset group"

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
        preset: Preset group used
        (The above parameters are optional. If not passed, they will not be modified)
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
            UShort(round(v_set * 1000)),
        ]
        if output:
            with self._api_lock:
                ret = self._api.OpenOut(*args)
        else:
            with self._api_lock:
                ret = self._api.CloseOut(*args)
        # logger.debug(f"Failed to set output: {output}, {v_set}, {i_set}, {preset}")
        assert ret, "Failed to set output status"

    def get_settings(self) -> dict:
        """
        Get system settings
        return: dict(
            backlight: int, Backlight level (0-4)
            volume: int, Volume level (0-4)
            opp: float, Over power protection value <=105W
            otp: int, Over temperature protection value 50-80C
            reverse_protect: bool, Reverse connection protection
            auto_output: bool, Automatically output on power up
        )
        """
        args = [Byte(0), Byte(0), UInt16(0), UInt16(0), Byte(0), Byte(0)]
        with self._api_lock:
            ret = self._api.GetSysPar(*args)
        assert ret[0], "获取系统设置失败"
        return {
            "backlight": int(ret[1]),
            "volume": int(ret[2]),
            "opp": float(ret[3]) / 10,
            "otp": int(ret[4]),
            "reverse_protect": bool(ret[5]),
            "auto_output": bool(ret[6]),
        }

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
        auto_output: bool, Automatically output on power up
        (The above parameters are all optional. If not passed, they will not be modified)
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
        assert ret, "Failed to set system settings"

    def register_output_info_callback(self, callback) -> None:
        """
        Register the output information callback function
        callback: Callback function, 传入参数为 Uint16: 电压 mV, Uint16: 电流 mA
        """
        assert callable(callback), "The callback function must be callable"
        self._api.ReceBasicInfoEvent += self._api.ReceBasicInfo(callback)

    def get_output_info(self) -> None:
        """
        Send a request to obtain output voltage and current information (callback function registration required)
        """
        self._api.GetBasicInfo()

    def register_state_change_callback(self, callback) -> None:
        """
        Register callback function for connection status changes.
        callback: Callback function
        """
        assert callable(callback), "The callback function must be callable"
        self._api.DevStateChanageEvent = self._api.DevStateChanage(callback)


if __name__ == "__main__":
    # For testing
    import time

    api = DP100()
    api.connect()
    print(api.get_device_info())
