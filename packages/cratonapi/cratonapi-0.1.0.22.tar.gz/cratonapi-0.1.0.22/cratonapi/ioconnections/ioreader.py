import sys
from typing import BinaryIO

from . import IOBase


class IOReader(IOBase):
    file: BinaryIO

    mode: str

    def __init__(self, path: str) -> None:
        self.path = path
        self.connect()

    def connect(self) -> None:
        try:
            self.file = open(self.path, "rb+")
        except OSError:
            print("Unable to open file!")
            sys.exit(-1)

    def read(self) -> bytes:
        return self.file.read()

    def write(self, message: bytes) -> None:
        pass

    def disconnect(self) -> None:
        self.file.close()
