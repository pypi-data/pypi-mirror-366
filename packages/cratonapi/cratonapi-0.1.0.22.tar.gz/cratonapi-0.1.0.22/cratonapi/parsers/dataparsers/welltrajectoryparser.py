import struct

import numpy as np

from cratonapi.datacontainers import WellTrajectory
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> WellTrajectory:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 9:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")
    points_count = struct.unpack("<I", message[16:20])[0]
    point_depths = np.empty(points_count)
    point_x_shifts = np.empty(points_count)
    point_y_shifts = np.empty(points_count)
    point_z_shifts = np.empty(points_count)
    offset = 0
    for point in range(points_count):
        depth, shift_x, shift_y, shift_z = struct.unpack(
            "<4f", message[20 + offset : 36 + offset]
        )
        point_depths[point] = depth
        point_x_shifts[point] = shift_x
        point_y_shifts[point] = shift_y
        point_z_shifts[point] = shift_z
        offset += 16
    if (
        len(point_depths) == 0
        and len(point_x_shifts) == 0
        and len(point_y_shifts) == 0
        and len(point_z_shifts) == 0
    ):
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или скважины с таким идентификатором не существует"
        )
    return WellTrajectory(point_depths, point_x_shifts, point_y_shifts, point_z_shifts)
