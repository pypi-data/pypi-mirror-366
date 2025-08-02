import struct

import numpy as np

from cratonapi.datacontainers import Well
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 2:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")
    wells_count = struct.unpack("<H", message[16:18])[0]
    well_list = np.empty(wells_count, Well)
    offset = 0
    for well_num in range(wells_count):
        well_id, well_name_symbols_count = struct.unpack(
            "<IH", message[18 + offset : 24 + offset]
        )
        well_name_bytes = message[24 + offset : 24 + offset + well_name_symbols_count]
        well_name = well_name_bytes.decode("cp1251")
        offset += well_name_symbols_count
        x, y = struct.unpack("<dd", message[24 + offset : 40 + offset])
        altitude, bottom = struct.unpack("<ff", message[40 + offset : 48 + offset])
        well_list[well_num] = Well(well_id, well_name, x, y, altitude, bottom)
        offset += 30
    if len(well_list) == 0:
        raise GISWellExecutionError("Проект в GISWell не открыт")
    return well_list
