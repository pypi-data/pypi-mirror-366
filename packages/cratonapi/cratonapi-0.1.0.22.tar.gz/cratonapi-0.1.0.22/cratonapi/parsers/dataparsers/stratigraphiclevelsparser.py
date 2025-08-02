import struct

import numpy as np

from cratonapi.datacontainers import StratigraphicLevel
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 4:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")
    levels_count = struct.unpack("<I", message[16:20])[0]
    offset = 0
    level_list = np.empty(levels_count, StratigraphicLevel)
    for level_num in range(levels_count):
        level_id, level_age, level_name_symbols_count = struct.unpack(
            "<IfH", message[20 + offset : 30 + offset]
        )
        level_name_bytes = message[30 + offset : 30 + offset + level_name_symbols_count]
        offset += level_name_symbols_count + 10
        level_name = level_name_bytes.decode("cp1251")
        new_level = StratigraphicLevel(level_id, level_age, level_name)
        level_list[level_num] = new_level
    if len(level_list) == 0:
        raise GISWellExecutionError("Проект в GISWell не открыт")
    return level_list
