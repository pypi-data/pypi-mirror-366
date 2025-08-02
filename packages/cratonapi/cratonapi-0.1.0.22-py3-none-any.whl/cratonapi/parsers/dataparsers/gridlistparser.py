import struct

import numpy as np

from cratonapi.datacontainers import GridInfo
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 6:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    grids_count = struct.unpack("<I", message[16:20])[0]
    offset = 0
    grid_list = np.empty(grids_count, GridInfo)
    for grid_num in range(grids_count):
        grid_id, grid_type, grid_visibility, grid_name_symbols_count = struct.unpack(
            "<IBBH", message[20 + offset : 28 + offset]
        )
        grid_name_bytes = message[28 + offset : 28 + offset + grid_name_symbols_count]
        offset += grid_name_symbols_count + 8
        grid_name = grid_name_bytes.decode("cp1251")
        new_grid = GridInfo(grid_id, grid_name, grid_type, grid_visibility)
        grid_list[grid_num] = new_grid
    if len(grid_list) == 0:
        raise DesmanaExecutionError("Проект в Desmana не открыт")
    return grid_list
