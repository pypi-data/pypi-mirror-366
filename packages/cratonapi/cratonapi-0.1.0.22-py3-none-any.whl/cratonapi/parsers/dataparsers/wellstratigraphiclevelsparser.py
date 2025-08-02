import struct

import numpy as np

from cratonapi.datacontainers import WellStratigraphicLevel
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 5:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")
    levels_count = struct.unpack("<I", message[16:20])[0]
    offset = 0
    level_list = np.empty(levels_count, WellStratigraphicLevel)
    for level_num in range(levels_count):
        level_id, level_depth = struct.unpack("<If", message[20 + offset : 28 + offset])
        new_level = WellStratigraphicLevel(level_id, level_depth)
        level_list[level_num] = new_level
        offset += 8
    if len(level_list) == 0:
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или скважины с таким идентификатором не существует"
        )
    return level_list
