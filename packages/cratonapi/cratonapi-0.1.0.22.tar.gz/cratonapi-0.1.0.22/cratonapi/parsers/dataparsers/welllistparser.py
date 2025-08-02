import struct

import numpy as np

from cratonapi.datacontainers import WellInfo
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 1:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")
    wells_count = struct.unpack("<H", message[16:18])[0]
    offset = 0
    well_list = np.empty(wells_count, WellInfo)
    for well_num in range(wells_count):
        well_id, well_name_symbols_count = struct.unpack(
            "<IH", message[18 + offset : 24 + offset]
        )
        well_name_bytes = message[24 + offset : 24 + offset + well_name_symbols_count]
        offset += well_name_symbols_count + 6
        well_name = well_name_bytes.decode("cp1251")
        new_well = WellInfo(well_id, well_name)
        well_list[well_num] = new_well
    if len(well_list) == 0:
        raise GISWellExecutionError("Проект в GISWell не открыт")
    return well_list
