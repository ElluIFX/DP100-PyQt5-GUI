import threading
import time
from queue import Queue
from typing import Tuple, Union

from loguru import logger
from serial import Serial


def is_digit(s: int) -> bool:
    return 48 <= s <= 57 or s == 46  # 0-9, .


class SerialReader:
    def __init__(self, serial_instance: Serial):
        """
        初始化串口读取器。

        Args:
            serial_instance (Serial): 串口实例。
            start_bit (list): 读取起始位。
            checksum (bool, optional): 是否启用校验。Defaults to True。

        Returns:
            None
        """
        self._data = bytes()
        self._ser = serial_instance
        self._in_waiting_buffer = bytes()
        while self._ser.in_waiting > 0:  # 清空缓冲区
            self._ser.read(self._ser.in_waiting)

    def read(self) -> bool:
        """
        轮询读取串口数据。

        Returns:
            bool: 是否读取到完整的一包数据。
        """
        while self._ser.in_waiting > 0:
            data = self._ser.read(self._ser.in_waiting)
            for d in data:
                if is_digit(d):
                    self._in_waiting_buffer += bytes([d])
                else:
                    if self._in_waiting_buffer:
                        self._data = self._in_waiting_buffer
                        self._in_waiting_buffer = bytes()
                        logger.debug(f"Read data: {self._data}")
                        return True
        return False

    def clear(self):
        """
        清空缓冲区。
        """
        self._in_waiting_buffer = bytes()
        self._data = bytes()

    @property
    def result(self) -> bytes:
        """
        获取读取到的数据。

        Returns:
            bytes: 读取到的数据。
        """
        return self._data

    def close(self):
        """
        关闭串口连接。

        Returns:
            None
        """
        self._ser.close()


class SerialReaderThreaded:
    """
    多线程的串口读取器
    """

    def __init__(self, serial_instance: Serial):
        """
        初始化串口读取器。
        """
        self._queue: Queue[Tuple[int, bytes]] = Queue()
        self._serial_reader = SerialReader(serial_instance)
        self._thread_running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while self._thread_running:
            if self._serial_reader.read():
                self._queue.put(self._serial_reader.result)
            else:
                time.sleep(0.001)

    def read(self) -> bool:
        """
        是否有数据可读
        """
        return not self._queue.empty()

    @property
    def result(self) -> bytes:
        """
        读取数据(阻塞,一个数据仅能读取一次)
        """
        return self._queue.get()

    def close(self, join=True):
        """
        关闭串口连接。

        Returns:
            None
        """
        self._thread_running = False
        if join:
            self._thread.join()
        self._serial_reader.close()


SerialReaderLike = Union[SerialReader, SerialReaderThreaded]
