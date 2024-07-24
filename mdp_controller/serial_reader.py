import threading
import time
from queue import Queue
from typing import Tuple, Union

from loguru import logger
from serial import Serial


class SerialReader:
    def __init__(self, serial_instance: Serial, start_bit, checksum: bool = True):
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
        self._reading_flag = False
        self._pack_length = -1
        self._pack_cmd = -1
        self._checksum = checksum
        self._read_start_bit = bytes(start_bit)
        self._read_start_bit_sum = sum(self._read_start_bit) & 0xFF

    def read(self) -> bool:
        """
        轮询读取串口数据。

        Returns:
            bool: 是否读取到完整的一包数据。
        """
        while self._ser.in_waiting > 0:
            if not self._reading_flag:
                self._in_waiting_buffer += self._ser.read(1)
                if (
                    self._in_waiting_buffer[-len(self._read_start_bit) :]
                    == self._read_start_bit
                ):
                    self._reading_flag = True
                    self._pack_length = -1
                    self._pack_cmd = -1
                    self._in_waiting_buffer = bytes()
            else:
                if self._pack_cmd == -1:
                    self._pack_cmd = self._ser.read(1)[0]
                if self._pack_length == -1:
                    self._pack_length = self._ser.read(1)[0]
                if self._ser.in_waiting >= self._pack_length or self._pack_length == 0:
                    data = self._ser.read(self._pack_length)
                    self._reading_flag = False
                    if self._checksum:
                        checksum = (
                            sum(data) + self._pack_length + self._read_start_bit_sum
                        ) & 0xFF
                        received_checksum = self._ser.read(1)[0]
                        if checksum == received_checksum:
                            self._data = data
                            return True
                        else:
                            logger.warning("[SerialReader] Checksum error")
                            return False
                    else:
                        return True
        return False

    @property
    def result(self) -> Tuple[int, bytes]:
        """
        获取读取到的命令字和数据。

        Returns:
            Tuple[int, bytes]: 读取到的命令字和数据。
        """
        return self._pack_cmd, self._data

    def close(self):
        """
        关闭串口连接。

        Returns:
            None
        """
        self._ser.close()


class SerialReaderBuffered:
    """
    类似于SerialReader, 但在内部维护一个缓冲区, 以尝试提高读取效率。
    """

    def __init__(self, serial_instance: Serial, start_bit, checksum=True):
        """
        初始化串口读取器。

        Args:
            serial_instance (Serial): 串口实例。
            start_bit (list): 读取起始位。
            checksum (bool): 是否启用校验。

        Returns:
            None
        """
        self._data = bytes()
        self._ser = serial_instance
        self._buffer = bytes()
        self._reading_flag = False
        self._pack_length = -1
        self._pack_cmd = -1
        self._read_pos = 0
        self._checksum = checksum
        self._read_start_bit = bytes(start_bit)
        self._read_start_bit_sum = sum(self._read_start_bit) & 0xFF
        self._read_start_bit_length = len(self._read_start_bit)

    def read(self) -> bool:
        """
        轮询读取串口数据。

        Returns:
            bool: 是否读取到完整的一包数据。
        """
        self._buffer += self._ser.read(self._ser.in_waiting)
        if not self._reading_flag:
            idx = self._buffer.find(self._read_start_bit)
            if idx != -1:
                self._read_pos = idx + self._read_start_bit_length
                self._reading_flag = True
                self._pack_length = -1
                self._pack_cmd = -1
        if self._reading_flag:
            if self._pack_length == -1 or self._pack_cmd == -1:
                if len(self._buffer) > self._read_pos:
                    if self._pack_cmd == -1:
                        self._pack_cmd = self._buffer[self._read_pos]
                        self._read_pos += 1
                    else:
                        self._pack_length = self._buffer[self._read_pos]
                        self._read_pos += 1
            elif len(self._buffer) >= self._read_pos + self._pack_length:
                self._reading_flag = False
                if self._checksum:
                    data_e = self._buffer[
                        self._read_pos : self._read_pos + self._pack_length + 1
                    ]
                    self._buffer = self._buffer[
                        self._read_pos + self._pack_length + 1 :
                    ]
                    if (
                        sum(data_e[:-1]) + self._pack_length + self._read_start_bit_sum
                    ) & 0xFF == data_e[-1]:
                        self._data = data_e[:-1]
                        return True
                    else:
                        logger.warning("[SerialReader] Checksum error")
                        return False
                else:
                    self._data = self._buffer[
                        self._read_pos : self._read_pos + self._pack_length
                    ]
                    self._buffer = self._buffer[self._read_pos + self._pack_length :]
                    return True
        return False

    @property
    def result(self) -> Tuple[int, bytes]:
        """
        获取读取到的命令字和数据。

        Returns:
            Tuple[int, bytes]: 读取到的命令字和数据。
        """
        return self._pack_cmd, self._data

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

    def __init__(
        self, serial_instance: Serial, start_bit, checksum=True, buffered=True
    ):
        """
        初始化串口读取器。
        """
        self._queue: Queue[Tuple[int, bytes]] = Queue()
        self._serial_reader = (
            SerialReaderBuffered(serial_instance, start_bit, checksum)
            if buffered
            else SerialReader(serial_instance, start_bit, checksum)
        )
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
    def result(self) -> Tuple[int, bytes]:
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


SerialReaderLike = Union[SerialReader, SerialReaderBuffered, SerialReaderThreaded]
