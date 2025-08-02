import struct
from typing import List, Tuple

from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> Tuple[int, List[int]]:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 21:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    number_of_cubes = struct.unpack("<H", message[16:18])[0]
    start = 18
    end = 22
    cube_ids = []
    for i in range(number_of_cubes):
        cube_ids.append(struct.unpack("<I", message[start:end])[0])
        start += 4
        end += 4
    if number_of_cubes == 0 and len(cube_ids) == 0:
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или нет кубов находящихся в данном радиусе заданной точки"
        )
    return (number_of_cubes, cube_ids)
