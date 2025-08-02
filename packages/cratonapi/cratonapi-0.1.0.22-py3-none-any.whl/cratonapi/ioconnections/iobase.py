from abc import ABC, abstractmethod


class IOBase(ABC):
    @abstractmethod
    def __init__(self, path: str) -> None:
        pass

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def read(self) -> bytes:
        pass

    @abstractmethod
    def write(self, message: bytes) -> None:
        pass
