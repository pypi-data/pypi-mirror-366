import struct

import numpy as np

from cratonapi.datacontainers import Grid
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> Grid:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 7:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    grid_identifier = struct.unpack("<I", message[16:20])[0]
    n_x, n_y, x_min, x_max, y_min, y_max, z_min, z_max, blank_code = struct.unpack(
        "<2H7d", message[20:80]
    )
    data = struct.unpack(f"<{n_x * n_y}d", message[80 : 80 + (8 * n_x * n_y)])
    if (
        grid_identifier == 0
        and n_x == 0
        and n_y == 0
        and x_min == 0.0
        and x_max == 0.0
        and y_min == 0.0
        and y_max == 0.0
        and z_min == 0.0
        and z_max == 0.0
        and blank_code == 0.0
        and len(data) == 0
    ):
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или грида с таким идентификатором не существует"
        )
    return Grid(
        grid_identifier,
        n_x,
        n_y,
        x_min,
        x_max,
        y_min,
        y_max,
        z_min,
        z_max,
        blank_code,
        np.asarray(data),
    )
