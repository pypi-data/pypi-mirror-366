import struct

import numpy as np

from cratonapi.datacontainers import CubeInfo
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 17:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    cubes_count = struct.unpack("<H", message[16:18])[0]
    cube_list = np.empty(cubes_count, CubeInfo)
    offset = 0
    for cube_num in range(cubes_count):
        cube_id, cube_name_symbols_count = struct.unpack(
            "<IH", message[18 + offset : 24 + offset]
        )
        cube_name_bytes = message[24 + offset : 24 + offset + cube_name_symbols_count]
        offset += 6 + cube_name_symbols_count
        cube_name = cube_name_bytes.decode("cp1251")
        cube_list[cube_num] = CubeInfo(cube_id, cube_name)
    if len(cube_list) == 0:
        raise DesmanaExecutionError("Проект в Desmana не открыт")
    return cube_list
