from typing import Callable

from cratonapi.ioconnections import IOBase
from cratonapi.parsers.signalparsers import *
from cratonapi.requests.utilityrequests import listenergreetingrequest


class SignalConnector:
    connection: IOBase
    signals_to_listen: tuple
    continue_listening: bool

    def __init__(self, signals_to_listen: tuple, connection: IOBase):
        self.connection = connection
        self.signals_to_listen = signals_to_listen
        self.continue_listening = True
        self.__greeting()

    def __greeting(self) -> None:
        message = listenergreetingrequest.request(self.signals_to_listen)
        self.connection.write(message)

    def listen(self, callback: Callable) -> None:
        answer: bytes
        while self.continue_listening:
            try:
                answer = self.connection.read()
                signal = signalcodeparser.parse(answer)
                callback(signal)
            except RuntimeError:
                continue

    def disconnect(self) -> None:
        self.continue_listening = False
        self.connection.disconnect()
