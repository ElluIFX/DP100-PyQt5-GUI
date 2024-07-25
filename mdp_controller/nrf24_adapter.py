import struct
import threading
import time
from dataclasses import dataclass
from typing import Callable, Literal, Optional

import serial
import serial.tools
import serial.tools.list_ports
from loguru import logger

from mdp_controller.serial_reader import SerialReaderBuffered


def _find_port_name(hwid):
    for ser in serial.tools.list_ports.comports():
        if hwid in ser.hwid:
            return ser.device
    return None


class RESPONSE:
    UNKNOWN_CMD = 0x00  # unknown command
    INVALID_CMD = 0x01  # invalid command length
    CMD_FAILED = 0x02  # command failed
    RESET_DONE = 0x03  # setting reset done
    BAUDRATE_SET = 0x04  # baudrate set
    NRF_SEND_OK = 0x10  # NRF24L01P send done
    NRF_SEND_FAIL = 0x11  # NRF24L01P send failed
    NRF_RECV_OK = 0x12  # NRF24L01P receive done
    NRF_RECV_FAIL = 0x13  # NRF24L01P receive failed
    NRF_FIFO_OVERFLOW = 0x15  # NRF24L01P FIFO overflow
    NRF_INIT = 0x20  # NRF24L01P init done
    NRF_SET_SAVED = 0x21  # NRF24L01P setting saved
    NRF_SET_QUERY = 0x22  # NRF24L01P setting query result
    ECHO = 0xFF  # echo


class CMD:
    REBOOT = 0x00  # reset system
    RESET = 0x03  # reset settings
    SET_BAUDRATE = 0x04  # set baudrate
    NRF_TX = 0x10  # nrf24l01p tx (variable length of payload)
    NRF_SET = 0x20  # nrf24l01p set setting (9 bytes see nrf24l01_init)
    NRF_SAVE = 0x21  # nrf24l01p save setting (no arg)
    NRF_QUERY = 0x22  # nrf24l01p query setting (same as nrf24l01_init)
    ECHO = 0xFF  # echo


class NRF24AdapterError(Exception):
    pass


@dataclass
class NRF24AdapterSetting:
    freq: int  # Mhz
    air_data_rate: Literal["250kbps", "1Mbps", "2Mbps"]
    tx_output_power: Literal[
        "7dBm", "4dBm", "3dBm", "1dBm", "0dBm", "-4dBm", "-6dBm", "-12dBm"
    ]
    crc_length: Literal["disable", "crc8", "crc16"]
    payload_length: int  # 1-32
    auto_retransmit_count: int  # 0-15
    auto_retransmit_delay: int  # 250us-4000us
    address_width: int  # 3-5
    address: bytes  # 5 bytes (fill shorter with 0x00)


ADR_DICT = {"250kbps": 2, "1Mbps": 0, "2Mbps": 1}
TOP_DICT = {
    "7dBm": 7,
    "4dBm": 6,
    "3dBm": 5,
    "1dBm": 4,
    "0dBm": 3,
    "-4dBm": 2,
    "-6dBm": 1,
    "-12dBm": 0,
}
CL_DICT = {"disable": 0, "crc8": 1, "crc16": 2}


def _inv_dict(d):
    return {v: k for k, v in d.items()}


class NRF24Adapter:
    def __init__(
        self, port: Optional[str] = None, baudrate: int = 921600, debug: bool = False
    ):
        self._port_name = port
        if self._port_name is None:
            self._port_name = _find_port_name("1A86:7523")
        if not self._port_name:
            raise Exception("NRF24-Adapter not found")
        self._serial = serial.Serial(self._port_name, baudrate, timeout=None)
        self._ser_wr_lock = threading.Lock()
        self._reader = SerialReaderBuffered(
            self._serial, start_bit=[0xAA, 0x66], checksum=False
        )
        self._running = True
        self._debug = debug
        self._connect_event = threading.Event()
        self._send_event = threading.Event()
        self._recv_callback: Optional[Callable[[bytes], None]] = None
        self._query_event = threading.Event()
        self._query_data = b""
        self._action_event = threading.Event()
        self._work_thread = threading.Thread(target=self._worker, daemon=True)
        self._work_thread.start()

    def close(self):
        self._running = False
        self._work_thread.join()
        self._reader.close()

    def wait_connected(self, timeout: Optional[float] = 2):
        self._connect_event.clear()
        if not self._connect_event.wait(timeout):
            raise Exception("NRF24-Adapter wait timeout")

    @property
    def connected(self):
        return self._connect_event.is_set()

    def _write(self, cmd: int, data: bytes):
        send = bytes([0xAA, 0x55, cmd, len(data)]) + data
        with self._ser_wr_lock:
            self._serial.write(send)
        if self._debug:
            logger.debug(f"Sent {send.hex(' ')}")

    def _action(self, cmd: int, data: bytes, timeout: Optional[float]) -> bool:
        self._action_event.clear()
        self._write(cmd, data)
        if self._action_event.wait(timeout):
            self._action_event.clear()
            return True
        else:
            return False

    def _query(
        self, cmd: int, data: bytes, timeout: Optional[float]
    ) -> Optional[bytes]:
        self._query_event.clear()
        self._query_data = b""
        self._write(cmd, data)
        if self._query_event.wait(timeout):
            self._query_event.clear()
            return self._query_data
        else:
            return None

    def _worker(self):
        logger.info("NRF24-Adapter thread started")
        last_recv_ping = time.perf_counter()
        last_send_ping = time.perf_counter()
        while self._running:
            try:
                if time.perf_counter() - last_send_ping > 1:
                    self._write(CMD.ECHO, b"")
                    last_send_ping = time.perf_counter()
                if not self._reader.read():
                    time.sleep(0.001)
                    if (
                        self._connect_event.is_set()
                        and time.perf_counter() - last_recv_ping > 3
                    ):
                        self._connect_event.clear()
                        logger.warning("NRF24-Adapter disconnected")
                    continue
                cmd, data = self._reader.result
                if self._debug:
                    logger.debug(f"Received: {cmd:02X} - {data.hex(' ')}")
                if cmd == RESPONSE.ECHO:
                    last_recv_ping = time.perf_counter()
                    if not self._connect_event.is_set():
                        self._connect_event.set()
                        logger.success("NRF24-Adapter connected")
                else:
                    self._parse_data(cmd, data)
            except Exception as e:
                if "PermissionError" in str(e):
                    logger.error("NRF24-Adapter port disconnected")
                    self._running = False
                else:
                    logger.exception("NRF24-Adapter thread error")

    def _parse_data(self, cmd: int, data: bytes):
        if cmd == RESPONSE.UNKNOWN_CMD:
            logger.warning("NRF Response: Unknown command")
        elif cmd == RESPONSE.INVALID_CMD:
            logger.warning("NRF Response: Invalid command")
        elif cmd == RESPONSE.CMD_FAILED:
            logger.warning("NRF Response: Command failed")
        elif cmd == RESPONSE.RESET_DONE:
            logger.info("NRF Response: Setting reset success")
            self._action_event.set()
        elif cmd == RESPONSE.BAUDRATE_SET:
            logger.info("NRF Response: Baudrate set success")
            self._action_event.set()
        elif cmd == RESPONSE.NRF_SEND_OK:
            self._send_event.set()
            if self._debug:
                logger.debug("NRF Response: NRF send success")
        elif cmd == RESPONSE.NRF_SEND_FAIL:
            logger.warning("NRF Response: NRF send no ack")
        elif cmd == RESPONSE.NRF_RECV_OK:
            if self._recv_callback is not None:
                self._recv_callback(data)
            if self._debug:
                logger.debug(f"NRF Response: NRF received {data.hex(' ')}")
        elif cmd == RESPONSE.NRF_RECV_FAIL:
            logger.warning("NRF Response: NRF receive failed")
        elif cmd == RESPONSE.NRF_FIFO_OVERFLOW:
            logger.warning("NRF Response: NRF FIFO overflow")
        elif cmd == RESPONSE.NRF_INIT:
            logger.info("NRF Response: NRF configure success")
            self._action_event.set()
        elif cmd == RESPONSE.NRF_SET_SAVED:
            logger.info("NRF Response: NRF setting saved")
            self._action_event.set()
        elif cmd == RESPONSE.NRF_SET_QUERY:
            self._query_data = data
            self._query_event.set()
            if self._debug:
                logger.debug(f"NRF Response: NRF setting {data.hex(' ')}")
        else:
            logger.error(f"NRF Response: Unknown cmd {cmd:02X}")

    def reboot(self, timeout: Optional[float] = 2):
        if not self._action(CMD.REBOOT, b"", timeout):
            raise NRF24AdapterError("Reboot failed")

    def reset_settings(self, timeout: Optional[float] = 2):
        if not self._action(CMD.RESET, b"", timeout):
            raise NRF24AdapterError("Reset setting failed")

    def set_baudrate(self, baudrate: int, timeout: Optional[float] = 2):
        data1 = baudrate // 10000
        data2 = (baudrate % 10000) // 100
        data3 = baudrate % 100
        if not self._action(CMD.SET_BAUDRATE, bytes([data1, data2, data3]), timeout):
            raise NRF24AdapterError("Set baudrate failed")
        else:
            self._serial.baudrate = baudrate
            logger.info(f"NRF24-Adapter baudrate set to {baudrate}")

    def nrf_send(
        self, data: bytes, wait_response: bool = True, timeout: Optional[float] = 2
    ):
        if wait_response:
            self._send_event.clear()
        self._write(CMD.NRF_TX, data)
        if wait_response:
            if not self._send_event.wait(timeout):
                raise NRF24AdapterError("NRF send timeout")
            else:
                self._send_event.clear()

    def nrf_register_recv_callback(self, callback: Callable[[bytes], None]):
        self._recv_callback = callback

    def nrf_get_settings(self, timeout: Optional[float] = 2) -> NRF24AdapterSetting:
        self._query_event.clear()
        if ret := self._query(CMD.NRF_QUERY, b"", timeout):
            data = struct.unpack("<" + "B" * 13, ret)
            return NRF24AdapterSetting(
                freq=data[0] + 2400,
                air_data_rate=_inv_dict(ADR_DICT)[data[1]],  # type:ignore
                tx_output_power=_inv_dict(TOP_DICT)[data[2]],  # type:ignore
                crc_length=_inv_dict(CL_DICT)[data[3]],  # type:ignore
                payload_length=data[4],
                auto_retransmit_count=data[5],
                auto_retransmit_delay=data[6] * 250,
                address_width=data[7],
                address=bytes(data[8:]),
            )
        else:
            raise NRF24AdapterError("NRF get settings failed")

    def nrf_set_settings(
        self, settings: NRF24AdapterSetting, timeout: Optional[float] = 2
    ):
        assert (
            isinstance(settings.address, bytes) and len(settings.address) == 5
        ), "Address must be bytes and length must be 5"
        assert (
            2400 <= settings.freq <= 2525
        ), "Frequency must be between 2400 and 2525 Mhz"
        assert (
            1 <= settings.payload_length <= 32
        ), "Payload length must be between 1 and 32"
        assert (
            0 <= settings.auto_retransmit_count <= 15
        ), "Auto retransmit count must be between 0 and 15"
        assert 3 <= settings.address_width <= 5, "Address width must be between 3 and 5"
        data = struct.pack(
            "<" + "B" * 13,
            settings.freq - 2400,
            ADR_DICT[settings.air_data_rate],
            TOP_DICT[settings.tx_output_power],
            CL_DICT[settings.crc_length],
            settings.payload_length,
            settings.auto_retransmit_count,
            settings.auto_retransmit_delay // 250,
            settings.address_width,
            *settings.address,
        )
        if not self._action(CMD.NRF_SET, data, timeout):
            raise NRF24AdapterError("NRF set settings failed")

    def nrf_save_settings(self, timeout: Optional[float] = 2):
        if not self._action(CMD.NRF_SAVE, b"", timeout):
            raise NRF24AdapterError("NRF save settings failed")


if __name__ == "__main__":
    adapter = NRF24Adapter(debug=False)
    setting = adapter.nrf_get_settings()
    setting.auto_retransmit_count = 12
    setting.auto_retransmit_delay = 250
    adapter.nrf_set_settings(setting)
    logger.info(f"{adapter.nrf_get_settings()}")
