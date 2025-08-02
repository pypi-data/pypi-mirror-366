import time
from ctypes.wintypes import HANDLE

import win32con
import win32event
import win32file
import win32pipe
from win32ctypes.pywin32.pywintypes import error

from cratonapi.exceptions import ApplicationExecutionError

from . import IOBase


class IOPipe(IOBase):
    handler: HANDLE
    overlapped: win32file.OVERLAPPED
    continue_work: bool
    path: str

    def __init__(self, path: str) -> None:
        self.overlapped = win32file.OVERLAPPED()
        self.overlapped.hEvent = win32event.CreateEvent(None, True, 0, None)
        self.continue_work = True
        self.path = path
        self.connect()

    def connect(self) -> None:
        try:
            self.handler = win32file.CreateFile(
                self.path,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                win32con.FILE_FLAG_OVERLAPPED,
                None,
            )
            if self.handler != win32file.INVALID_HANDLE_VALUE:
                win32pipe.SetNamedPipeHandleState(
                    self.handler, win32pipe.PIPE_READMODE_BYTE, None, None
                )
                self.continue_work = True
            else:
                raise RuntimeError("Connection failed!")
        except error:
            raise RuntimeError("Connection failed!")
        except Exception as e:
            if e.args[0] == 2:
                raise ApplicationExecutionError("W-SEIS is not open!")

    def read(self) -> bytes:
        buf = b""
        try:
            _, available_data, _ = win32pipe.PeekNamedPipe(self.handler, 0)
            while available_data == 0 and self.continue_work:
                _, available_data, _ = win32pipe.PeekNamedPipe(self.handler, 0)
            if not self.continue_work:
                return bytes()
            result, data = win32file.ReadFile(
                self.handler, available_data, self.overlapped
            )
            buf = data.obj
            available_data = 0
            while available_data == 0:
                _, available_data, _ = win32pipe.PeekNamedPipe(self.handler, 0)
            while available_data != 0:
                result, data = win32file.ReadFile(
                    self.handler, available_data, self.overlapped
                )
                buf += data.obj
                time.sleep(0.1)
                _, available_data, _ = win32pipe.PeekNamedPipe(self.handler, 0)
        except error:
            raise RuntimeError("Listening has been stopped")
        except Exception as e:
            if e.args[0] == 233:
                raise ApplicationExecutionError("W-SEIS is not open!")
        return buf

    def write(self, message: bytes) -> None:
        try:
            win32file.WriteFile(self.handler, message)
        except Exception as e:
            if e.args[0] == 233:
                raise ApplicationExecutionError("W-SEIS is not open!")

    def disconnect(self) -> None:
        self.continue_work = False
        win32file.CloseHandle(self.handler)
