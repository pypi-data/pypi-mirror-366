import struct

import numpy as np

from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 18:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    horizons_count = struct.unpack("<H", message[16:18])[0]
    horizon_name_list = np.empty(horizons_count, dtype=object)
    offset = 0
    for horizon_num in range(horizons_count):
        horizon_name_symbols_count = struct.unpack(
            "<H", message[18 + offset : 20 + offset]
        )[0]
        horizon_name_bytes = message[
            20 + offset : 20 + offset + horizon_name_symbols_count
        ]
        offset += 2 + horizon_name_symbols_count
        horizon_name_list[horizon_num] = horizon_name_bytes.decode("cp1251")
    if len(horizon_name_list) != horizons_count:
        raise DesmanaExecutionError("Ошибка при чтении горизонтов")
    return horizon_name_list
