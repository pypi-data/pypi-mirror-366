import struct

from cratonapi.datacontainers import TransformMatrix
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> TransformMatrix:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 27:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise RuntimeError("Desmana is not open!")
        raise DesmanaExecutionError("Desmana is not open!")

    a, b, c, d, e, f, g, h = struct.unpack("<8d", message[16:80])
    if (
        a == 0
        and b == 0
        and c == 0
        and d == 0
        and e == 0
        and f == 0
        and g == 0
        and h == 0
    ):
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или куба с таким идентификатором не существует"
        )
    return TransformMatrix(a, b, c, d, e, f, g, h)
