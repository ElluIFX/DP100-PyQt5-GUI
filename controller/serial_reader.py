import queue
import threading
import time
from queue import Queue
from typing import Tuple, Union

from loguru import logger
from numpy import byte
from serial import Serial


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
        self.ascii_queue = queue.Queue()
        self.binary_queue = queue.Queue()
        self._ser = serial_instance
        self._ascii_buffer = bytes()
        self._binary_buffer = bytes()
        while self._ser.in_waiting > 0:  # 清空缓冲区
            self._ser.read(self._ser.in_waiting)

    def read(self) -> int:
        """
        轮询读取串口数据。

        Returns:
            int: 读取到的数据类型。
        """
        ret = 0
        while self._ser.in_waiting > 0:
            data = self._ser.read(self._ser.in_waiting)
            # logger.info(f"Read data: {data}")
            for d in data:
                if 48 <= d <= 57 or d == 46:
                    self._ascii_buffer += bytes([d])
                else:
                    if len(self._ascii_buffer) > 4 and 46 in self._ascii_buffer:
                        self.ascii_queue.put(self._ascii_buffer)
                        logger.info(f"Read ascii data: {self._ascii_buffer}")
                        self._binary_buffer = bytes()
                        ret |= 1
                    self._ascii_buffer = bytes()
                self._binary_buffer += bytes([d])
                if len(self._binary_buffer) >= 24:
                    rstrip = self._binary_buffer[len(self._binary_buffer) - 24 :]
                    if all(rstrip[i] == 0 for i in [0, 1, 4, 5]):
                        self.binary_queue.put(rstrip)
                        # logger.info(f"Read binary data: {rstrip}")
                        self._binary_buffer = bytes()
                        self._ascii_buffer = bytes()
                        ret |= 2
            if len(self._ascii_buffer) > 2 and 46 in self._ascii_buffer:
                self.ascii_queue.put(self._ascii_buffer)
                logger.info(f"Read ascii data: {self._ascii_buffer}")
                self._ascii_buffer = bytes()
                self._binary_buffer = bytes()
                ret |= 1
        return ret

    def clear(self):
        """
        清空缓冲区。
        """
        self._ascii_buffer = bytes()

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
                self._queue.put(self._serial_reader.ascii_result)
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
