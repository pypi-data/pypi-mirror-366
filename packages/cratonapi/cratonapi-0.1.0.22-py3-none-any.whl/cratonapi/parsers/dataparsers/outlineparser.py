import struct

import numpy as np

from cratonapi.datacontainers import Outline
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 31:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")
    polys_count = struct.unpack("<I", message[16:20])[0]
    offset = 0
    outline_list = np.empty(polys_count, Outline)
    for polys_num in range(polys_count):
        blanking_flag, points_count = struct.unpack(
            "<BI", message[20 + offset : 25 + offset]
        )
        offset += 5
        coordinates = np.empty((points_count, 3))
        for point_num in range(points_count):
            x, y, z = struct.unpack("<3d", message[20 + offset : 44 + offset])
            coordinates[point_num] = (x, y, z)
            offset += 24
        outline_list[polys_num] = Outline(
            blanking_flag=blanking_flag, coordinates=coordinates
        )
    if len(outline_list) == 0:
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или контура с таким идентификатором не существует"
        )
    return outline_list
