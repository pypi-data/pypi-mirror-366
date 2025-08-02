import struct

import numpy as np

from cratonapi.datacontainers import CubeDataSlice
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> CubeDataSlice:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 19:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    samples_count, start_idx, t_count = struct.unpack("<HHI", message[16:24])
    inlines = np.empty(t_count)
    xlines = np.empty(t_count)
    data = np.empty((t_count, samples_count))
    if samples_count > 0:
        offset = 0
        for i in range(t_count):
            inlines[i], xlines[i] = struct.unpack(
                "<HH", message[24 + offset : 28 + offset]
            )
            data[i] = struct.unpack(
                f"<{samples_count}f",
                message[28 + offset : 28 + 4 * samples_count + offset],
            )
            offset += 4 + 4 * samples_count
    if (
        samples_count == 0
        and start_idx == 0
        and len(inlines) == 0
        and len(xlines) == 0
        and len(data) == 0
    ):
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или входные параметры были заданы неверно"
        )
    return CubeDataSlice(
        samples_count, start_idx, inlines, xlines, data.astype("float32")
    )
