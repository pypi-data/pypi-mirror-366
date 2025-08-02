import struct

import numpy as np

from cratonapi.datacontainers import Curve
from cratonapi.exceptions import GISWellExecutionError

NAN_VALUE = -999.25


def parse(message: bytes) -> Curve:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 29:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")

    curve_id, number_of_points = struct.unpack("<II", message[16:24])
    offset = 0
    point_values = np.empty(number_of_points)
    point_depths = np.empty(number_of_points)
    for i in range(number_of_points):
        point_values[i], point_depths[i] = struct.unpack(
            "<dd", message[24 + offset : 40 + offset]
        )
        offset += 16
    condition = point_values == NAN_VALUE
    point_values[condition] = np.nan
    if curve_id == 0 and len(point_values) == 0 and len(point_depths) == 0:
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или неверно заданы идентификаторы скважины и/или кривой"
        )
    return Curve(
        curve_id=curve_id, point_values=point_values, point_depths=point_depths
    )
