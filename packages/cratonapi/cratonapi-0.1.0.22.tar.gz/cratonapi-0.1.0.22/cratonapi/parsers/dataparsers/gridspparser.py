import struct

import numpy as np

from cratonapi.datacontainers import Grid
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 16:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    grid_sp_identifier = struct.unpack("<I", message[16:20])[0]
    n_x, n_y, x_min, x_max, y_min, y_max, z_min, z_max, blank_code, ch_cnt = (
        struct.unpack("<2H6dfB", message[20:77])
    )
    offset = 0
    grid_list = np.empty(ch_cnt, Grid)
    for data_num in range(ch_cnt):
        data = struct.unpack(
            f"<{n_x * n_y}f", message[77 + offset : 77 + 4 * n_x * n_y + offset]
        )
        offset += 4 * n_x * n_y
        grid_list[data_num] = Grid(
            n_id=grid_sp_identifier,
            n_x=n_x,
            n_y=n_y,
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            z_min=z_min,
            z_max=z_max,
            blank_code=blank_code,
            data=np.asarray(data),
        )
    if len(grid_list) == 0:
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или грида с таким идентификатором не существует"
        )
    return grid_list
