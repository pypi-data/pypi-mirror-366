import platform

current_platform = platform.system()

from .iobase import IOBase
from .iofile import IOFile
from .ioreader import IOReader

if current_platform == "Linux":
    from .iosocket import IOSocket
elif current_platform == "Windows":
    from .iopipe import IOPipe
