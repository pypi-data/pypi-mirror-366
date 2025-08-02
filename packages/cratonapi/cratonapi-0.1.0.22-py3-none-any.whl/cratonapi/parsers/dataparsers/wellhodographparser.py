import struct

import numpy as np

from cratonapi.datacontainers import WellHodograph
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> WellHodograph:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 8:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")
    points_count = struct.unpack("<I", message[16:20])[0]
    point_times = np.empty(points_count)
    point_depths = np.empty(points_count)
    offset = 0
    for point in range(points_count):
        point_depth, point_time = struct.unpack(
            "<2d", message[20 + offset : 36 + offset]
        )
        point_times[point] = point_time
        point_depths[point] = point_depth
        offset += 16
    time_shift = struct.unpack("<d", message[20 + offset : 28 + offset])[0]
    if points_count == 0:
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или неверно заданы идентификаторы скважины и/или кривой"
        )
    return WellHodograph(time_shift, point_times, point_depths)
