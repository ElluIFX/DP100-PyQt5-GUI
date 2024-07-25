import time
from copy import deepcopy
from threading import Event
from typing import Callable, Literal, Optional, Tuple

from loguru import logger

import mdp_controller.mdp_protocal as mdp_protocal
from mdp_controller.nrf24_adapter import (
    NRF24Adapter,
    NRF24AdapterError,
    NRF24AdapterSetting,
)

try:
    import richuru

    richuru.install()
except ImportError:
    pass


def _convert_to_rgb565(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


class MDP_P906:
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 921600,
        address: bytes = b"\xaa\xbb\xcc\xdd\xee",
        freq: int = 2442,
        idcode: Optional[bytes] = None,
        m01_channel: int = 0,
        led_color: Tuple[int, int, int] = (0x66, 0xCC, 0xFF),
        com_timeout: Optional[float] = 0.04,
        com_retry: int = 5,
        tx_output_power: Literal[
            "7dBm", "4dBm", "3dBm", "1dBm", "0dBm", "-4dBm", "-6dBm", "-12dBm"
        ] = "4dBm",
        debug: bool = False,
    ):
        """
        MDP-P906 Digital Power Supply Controller Class

        Parameters
        ----------
        port
            port of the nrf24l01 adapter, None to autodetect
        baudrate
            baudrate of the nrf24l01 adapter
        address
            5bytes wireless address of the nrf24l01 adapter, can be any you want
        freq
            wireless frequency of the nrf24l01 adapter, 2400~2525 Mhz
        idcode
            idcode of the MDP-P906, set to None then call auto_match() to get idcode
        m01_channel
            simulate the MDP-M01, this number shows on top-right of P906's LCD
        led_color
            the color of the digital wheel of the P906, color in RGB format
        com_timeout
            communication timeout in secs between P906 and the adapter
        com_retry
            communication retry times when timeout occurs
        tx_output_power
            singal output power of the nrf24l01 adapter
        debug
            show debug info
        """

        self._adp = NRF24Adapter(port=port, baudrate=baudrate, debug=debug)
        self._address = address
        self._idcode = idcode
        self._m01_channel = m01_channel
        self._led_color = _convert_to_rgb565(*led_color)
        self._com_timeout = com_timeout
        self._com_retry = com_retry
        self._freq = freq
        self._status = {
            "HVzero16": 0.0,
            "HVgain16": 0.0,
            "HCzero04": 0.0,
            "HCgain04": 0.0,
            "Voltage": 0.0,
            "Current": 0.0,
            "InputVoltage": 0.0,
            "InputCurrent": 0.0,
            "ErrFlag": 0,
        }

        self._adp.nrf_register_recv_callback(self._callback)
        self._transfer_data = b""
        self._transfer_waiting = False
        self._transfer_event = Event()

        self._rtvalue_callback: Optional[Callable[[list], None]] = None

        self._adp.wait_connected()
        setting = NRF24AdapterSetting(
            freq=self._freq,
            air_data_rate="2Mbps",
            address_width=5,
            address=self._address,
            tx_output_power=tx_output_power,
            crc_length="crc16",
            payload_length=32,
            auto_retransmit_count=12,
            auto_retransmit_delay=250,
        )
        self._adp.nrf_set_settings(setting)
        time.sleep(0.1)

    def _callback(self, data: bytes):
        if data[0] == 7:
            errflag, input_volt, input_curr, voltage, current = (
                mdp_protocal.parse_type7_response(data)
            )
            self._status["ErrFlag"] = errflag
            self._status["InputVoltage"] = input_volt
            self._status["InputCurrent"] = input_curr
            self._status["Voltage"] = voltage
            self._status["Current"] = current
        elif data[0] == 9:
            idcode, HVzero16, HVgain16, HCzero04, HCgain04 = (
                mdp_protocal.parse_type9_response(data)
            )
            if idcode != self._idcode:
                logger.warning(f"ID code mismatch: {idcode}!={self._idcode}")
            self._status["HVzero16"] = HVzero16
            self._status["HVgain16"] = HVgain16
            self._status["HCzero04"] = HCzero04
            self._status["HCgain04"] = HCgain04
        if self._transfer_waiting:
            self._transfer_data = data
            self._transfer_waiting = False
            self._transfer_event.set()
        else:
            if data[0] == 8 and self._rtvalue_callback is not None:
                errflag, values = mdp_protocal.parse_type8_response(
                    data,
                    self._status["HVzero16"],
                    self._status["HVgain16"],
                    self._status["HCzero04"],
                    self._status["HCgain04"],
                )
                self._status["ErrFlag"] = errflag
                self._rtvalue_callback(values)

    def _transfer(
        self,
        packet: bytes,
        wait_response: bool = True,
        check_response_head: bool = True,
        _retry=None,
    ):
        if not wait_response:
            self._adp.nrf_send(packet, timeout=self._com_timeout)
            return b""
        if _retry is None:
            _retry = self._com_retry
        self._transfer_data = b""
        self._transfer_waiting = True
        self._transfer_event.clear()
        self._adp.nrf_send(packet, timeout=self._com_timeout)
        if (not self._transfer_event.wait(self._com_timeout)) or (
            check_response_head and self._transfer_data[0] != packet[0]
        ):
            if _retry > 0:
                return self._transfer(
                    packet, wait_response, check_response_head, _retry - 1
                )
            raise TimeoutError("NRF24 timeout")
        return self._transfer_data

    def set_led_color(self, rgb: Tuple[int, int, int]):
        """
        Set the led color of the digital wheel

        Parameters
        ----------
        rgb
            The color of the led, in the form of (R, G, B)
        """
        assert self._idcode is not None, "Please pair first"
        rgb565 = _convert_to_rgb565(*rgb)
        self._led_color = rgb565
        self._transfer(
            mdp_protocal.gen_set_led_color(
                self._idcode, self._led_color, self._m01_channel
            )
        )

    def get_gain_offset(self):
        """
        Get the gain and offset of the ADCs
        Call by connect(), dont need to call again
        Returns
        -------
            Tuple[int, int, int, int]
        """
        assert self._idcode is not None, "Please pair first"
        self._transfer(
            mdp_protocal.gen_set_led_color(
                self._idcode, self._led_color, self._m01_channel
            )
        )
        return (
            self._status["HVzero16"],
            self._status["HVgain16"],
            self._status["HCzero04"],
            self._status["HCgain04"],
        )

    def get_set_value(self):
        """
        Get the set value of output
        If Voltage and Current are -1, means device is locked

        Returns
        -------
            ErrorFlag, InputVoltage, InputCurrent, Voltage, Current
        """
        assert self._idcode is not None, "Please pair first"
        self._transfer(mdp_protocal.gen_get_type7(self._idcode, self._m01_channel))
        return (
            self._status["ErrFlag"],
            self._status["InputVoltage"],
            self._status["InputCurrent"],
            self._status["Voltage"],
            self._status["Current"],
        )

    def get_realtime_value(self):
        """
        Get the realtime values of output in sync mode

        Returns
        -------
            A list of (voltage in mV, current in mA)
        """
        assert self._idcode is not None, "Please pair first"
        try:
            data = self._transfer(
                mdp_protocal.gen_get_type8(self._idcode, self._m01_channel)
            )
            errflag, values = mdp_protocal.parse_type8_response(
                data,
                self._status["HVzero16"],
                self._status["HVgain16"],
                self._status["HCzero04"],
                self._status["HCgain04"],
            )
            self._status["ErrFlag"] = errflag
            return values
        except (TimeoutError, NRF24AdapterError):
            return []

    def request_realtime_value(self):
        """
        Request the realtime values of output in async mode
        Call register_realtime_value_callback() first
        """
        assert self._idcode is not None, "Please pair first"
        try:
            self._transfer(
                mdp_protocal.gen_get_type8(self._idcode, self._m01_channel),
                wait_response=False,
            )
        except (TimeoutError, NRF24AdapterError):
            pass

    def register_realtime_value_callback(self, callback: Callable[[list], None]):
        """
        Register a callback function to handle the realtime values of output in async mode

        Parameters
        ----------
        callback
            A function that takes a list of (voltage in mV, current in mA) as input
        """
        self._rtvalue_callback = callback

    def set_output(self, state: bool):
        """
        Set the output state of the MDP-P906

        Parameters
        ----------
        state
            True for on, False for off
        """
        assert self._idcode is not None, "Please pair first"
        self._transfer(
            mdp_protocal.gen_set_output(self._idcode, state, self._m01_channel)
        )

    def set_voltage(self, voltage_set: float):
        """
        Set the output voltage of the MDP-P906

        Parameters
        ----------
        voltage_set
            The voltage to be set, in V, steps 0.001V
        """
        assert self._idcode is not None, "Please pair first"
        self._transfer(
            mdp_protocal.gen_set_voltage(self._idcode, voltage_set, self._m01_channel),
            wait_response=False,
        )

    def set_current(self, current_set: float):
        """
        Set the output current of the MDP-P906

        Parameters
        ----------
        current_set
            The current to be set, in A, steps 0.001A
        """
        assert self._idcode is not None, "Please pair first"
        self._transfer(
            mdp_protocal.gen_set_current(self._idcode, current_set, self._m01_channel),
            wait_response=False,
        )

    def connect(self):
        """
        Connect to the MDP-P906, and prepare information for calibration

        Raises
        ------
        Exception
            If failed to connect to the MDP-P906
        """
        assert self._idcode is not None, "Please pair first"
        for i in range(5):
            try:
                self.get_gain_offset()
                self.get_set_value()
            except (NRF24AdapterError, TimeoutError, AssertionError) as e:
                if i == 4:
                    raise Exception("Failed to connect to MDP-P906") from e
                time.sleep(0.1)
                continue
            break
        logger.debug(f"Init status: {self._status}")
        logger.success("MDP-P906 Connected")

    def auto_match(self, try_times: int = 64):
        """
        Auto match with the MDP-P906

        Parameters
        ----------
        try_times
            The number of times to try to match with the MDP-P906

        Returns
        -------
        bytes | None
            The idcode of the MDP-P906, None if failed to match
        """
        setting = self._adp.nrf_get_settings()
        setting_old = deepcopy(setting)
        setting.address = b"\xff\xff\xff\xff\xff"  # broadcast address
        setting.freq = 2478
        self._adp.nrf_set_settings(setting)
        for i in range(try_times):
            logger.info(f"Auto matching - {i+1}/{try_times}")
            try:
                data = self._transfer(mdp_protocal.gen_call_for_id())
            except (NRF24AdapterError, TimeoutError):
                time.sleep(1)
                continue
            if data[0] == 0x05:
                self._idcode = mdp_protocal.parse_type5_response(data)
                logger.success(f"Matched device - 0x{self._idcode.hex().upper()}")
                break
            logger.warning(f"Unhandled response - {data.hex(' ').upper()}")
        else:
            logger.error("Failed to match device")
            self._idcode = None
        if self._idcode is not None:
            data = self._transfer(
                mdp_protocal.gen_dispatch_ch_addr(self._address, self._freq - 2400)
            )
            logger.info(
                f"Dispatched device to address 0x{self._address.hex().upper()} and freq {self._freq} Mhz"
            )
        self._adp.nrf_set_settings(setting_old)
        return self._idcode
