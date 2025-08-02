import struct

from cratonapi.datacontainers import Cube
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> Cube:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 20:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")
    if len(message) < 97:
        raise DesmanaExecutionError(
            "Проект в Desmana не открыт или грида с таким идентификатором не существует"
        )
    else:
        (
            x_min_inl_min_xl,
            y_min_inl_min_xl,
            x_max_inl_min_xl,
            y_max_inl_min_xl,
            x_min_inl_max_xl,
            y_min_inl_max_xl,
            x_max_inl_max_xl,
            y_max_inl_max_xl,
            inline_count,
            xline_count,
            samples_count,
            dt,
            cube_type,
            min_idx_inline,
            min_idx_xline,
        ) = struct.unpack("<8d4HBII", message[16:97])
    return Cube(
        x_min_inl_min_xl,
        y_min_inl_min_xl,
        x_max_inl_min_xl,
        y_max_inl_min_xl,
        x_min_inl_max_xl,
        y_min_inl_max_xl,
        x_max_inl_max_xl,
        y_max_inl_max_xl,
        inline_count,
        xline_count,
        samples_count,
        dt,
        cube_type,
        min_idx_inline,
        min_idx_xline,
    )
