import os
import select
import socket
import time
from typing import Optional

from cratonapi.exceptions import UDSConnectionError

from . import IOBase

BUFFER_SIZE = 262144
TIME_SLEEP = 0.005


class IOSocket(IOBase):
    def __init__(self, path: str) -> None:
        """
        Инициализация объекта для работы с Unix Domain Socket.
        :param path: Путь до файла сокета.
        """
        self.path = path
        self.socket: Optional[socket.socket] = None
        self.continue_work = True
        self.connect()

    def connect(self) -> None:
        """
        Устанавливает соединение с Unix Domain Socket.
        """
        # Проверяем существование файла сокета
        if not os.path.exists(self.path):
            raise UDSConnectionError(f"Сокет-файл '{self.path}' не существует.")

        # Создаем сокет
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)  # type: ignore[attr-defined]
            self.socket.connect(self.path)
        except (socket.error, FileNotFoundError) as e:
            raise UDSConnectionError(f"Не удалось подключиться к сокету: {e}")

    def read(self) -> bytes:
        """
        Читает данные из сокета. Работает, пока соединение активно.
        :return: Считанные данные в виде набора байт.
        """
        if not self.socket:
            raise RuntimeError("Сокет не инициализирован.")

        buffer = b""
        # Блокирующее чтение до тех пор, пока данные не будут доступны
        while self.continue_work:
            try:
                readable, _, _ = select.select([self.socket], [], [], 20)
                if readable:
                    data = self.socket.recv(BUFFER_SIZE)
                    if not data:
                        self.continue_work = False
                        break
                    buffer += data
                    time.sleep(TIME_SLEEP)
                else:
                    break
            except socket.error as e:
                raise RuntimeError(f"Ошибка при чтении из сокета: {e}")

        return buffer if buffer else b""

    def write(self, message: bytes) -> None:
        """
        Отправляет данные в сокет.
        :param message: Сообщение в виде набора байт.
        """
        if not self.socket:
            raise RuntimeError("Сокет не инициализирован.")

        try:
            self.socket.sendall(message)  # Отправка всего сообщения
        except socket.error as e:
            raise RuntimeError(f"Ошибка при записи в сокет: {e}")

    def disconnect(self) -> None:
        """
        Закрывает соединение и завершает работу.
        """
        self.continue_work = False
        if self.socket:
            try:
                self.socket.close()
            except socket.error as e:
                raise RuntimeError(f"Ошибка при закрытии сокета: {e}")
            finally:
                self.socket = None
