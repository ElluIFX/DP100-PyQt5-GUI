import time
from typing import Optional, Self

from loguru import logger
from serial import Serial
from serial.tools import list_ports

from controller.serial_reader import SerialReader


def _find_port_name() -> str:
    PID = 0x5740
    VID = 0x0483
    for port in list_ports.comports():
        if PID == port.pid and VID == port.vid:
            return port.device
    listinfo = ""
    for port in list_ports.comports():
        if not port.pid or not port.vid:
            listinfo += f"{port.device}: {port.description}: No ID provided\n"
        else:
            listinfo += (
                f"{port.device}: {port.description} {port.vid:04X}:{port.pid:04X}\n"
            )
    if not listinfo:
        listinfo = "No device found"
    raise Exception(
        f"Cannot find PD Pocket (Target PID:VID = {PID:04X}:{VID:04X})\nDevice List:\n{listinfo}"
    )


class PDPocket:
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 921600,
    ):
        """
        Initialize PD Pocket Power Supply Controller.
        """
        if not port:
            port = _find_port_name()
        self._ser = Serial(port=port, baudrate=baudrate)
        self._reader = SerialReader(self._ser)
        self._last_readout_v = 0
        self._last_readout_i = 0

    def close(self):
        self._ser.close()
        logger.info("PD Pocket closed")

    def _read_until_ok(self, timeout: float = 1) -> bool:
        t0 = time.perf_counter()
        while not self._reader.read():
            if time.perf_counter() - t0 > timeout:
                raise TimeoutError("Timeout waiting for response")
            time.sleep(0.001)
        return self._reader.result.decode().strip()

    def get_output_voltage(self) -> float:
        """
        Get the output voltage of the PD Pocket.
        """
        self._reader.clear()
        self._ser.write(b"MEAS:VOLT?")
        val = float(self._read_until_ok())
        # if val < 0.1:
        #     logger.warning(f"Invalid voltage readout: {val}")
        val = val if val < 32 else 0  # 过滤非法值
        if val < 0.01 or val == 2.000:
            # logger.warning(f"Invalid voltage readout: {val}")
            fixed_val = self._last_readout_v
            self._last_readout_v = val
            return fixed_val
        self._last_readout_v = val
        return val

    def get_output_current(self) -> float:
        """
        Get the output current of the PD Pocket.
        """
        self._reader.clear()
        self._ser.write(b"MEAS:CURR?")
        val = float(self._read_until_ok())
        # if val > 10:
        #     logger.warning(f"Invalid current readout: {val}")
        val = val if val <= 10 else 0  # 过滤非法值
        if val < 0.01:
            fixed_val = self._last_readout_i
            self._last_readout_i = val
            return fixed_val
        self._last_readout_i = val
        return val

    def get_output_power(self) -> float:
        """
        Get the output power of the PD Pocket.
        """
        self._reader.clear()
        self._ser.write(b"MEAS:POW?")
        return float(self._read_until_ok())

    def set_voltage(self, voltage_set: float):
        """
        Set the output voltage of the PD Pocket.

        Args:
            voltage_set (float): The voltage to be set, in V, steps of 0.01V.
        """
        self._ser.write(f"VOLT {voltage_set:.2f}\r\n".encode())

    def set_current(self, current_set: float):
        """
        Set the output current of the PD Pocket.

        Args:
            current_set (float): The current to be set, in A, steps of 0.01A.
        """
        self._ser.write(f"CURR {current_set:.2f}\r\n".encode())

    def set_max_power(self, power_set: float):
        """
        Set the maximum power of the PD Pocket.
        """
        self._ser.write(f"setpower {power_set:.0f}\r\n".encode())

    def set_output(self, state: bool):
        """
        Set the output state of the PD Pocket.
        """
        self._ser.write(b"OUTP ON\r\n" if state else b"OUTP OFF\r\n")

    def set_short_protect(self, state: bool):
        """
        Set the short protection state of the PD Pocket.
        """
        self._ser.write(b"setSFB 1\r\n" if state else b"setSFB 0\r\n")

    def set_key_lock(self, state: bool):
        """
        Set the key lock state of the PD Pocket.
        """
        self._ser.write(b"lockkey 1\r\n" if state else b"lockkey 0\r\n")

    def calibrate_output(self):
        """
        Calibrate the output of the PD Pocket. (Use 7V)
        """
        self._ser.write(b"calibus 1\r\n")

    def calibrate_input(self):
        """
        Calibrate the input of the PD Pocket. (Use 20V)
        """
        self._ser.write(b"calibus 2\r\n")

    @property
    def a(self) -> Self:
        """
        Compatible with PDPocketQThread
        """
        return self


if __name__ == "__main__":

    def timed_print(func, *args, **kwargs):
        t0 = time.perf_counter()
        res = func(*args, **kwargs)
        t1 = time.perf_counter() - t0
        logger.info(f"Call {func.__name__}(), Return: {res}, Cost: {t1:.6f}s")

    device = PDPocket()
    timed_print(device.set_output, False)
    time.sleep(0.1)
    timed_print(device.get_output_voltage)
    timed_print(device.get_output_current)
    timed_print(device.get_output_power)
    timed_print(device.set_output, True)
    time.sleep(0.1)
    timed_print(device.get_output_voltage)
    timed_print(device.get_output_current)
    timed_print(device.get_output_power)
    # timed_print(device.set_voltage, 12)
    # timed_print(device.set_current, 1)
    # timed_print(device.set_max_power, 100)
    # timed_print(device.set_output_state, True)
    # time.sleep(1)
    # timed_print(device.get_output_voltage)
    # timed_print(device.get_output_current)
    # timed_print(device.get_output_power)
    # timed_print(device.set_output_state, False)
