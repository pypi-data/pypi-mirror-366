import struct

import numpy as np

from cratonapi.datacontainers import CurveInfo
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 28:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise RuntimeError("GISWell is not open!")
    curves_count = struct.unpack("<I", message[16:20])[0]
    start = 20
    curve_list = np.empty(curves_count, CurveInfo)
    for curve_num in range(curves_count):
        end = start + 31
        (
            curve_id,
            curve_tag_id,
            start_depth,
            end_depth,
            dh,
            min_value,
            max_value,
            visibility,
            existence_intervals_num,
        ) = struct.unpack("<2I5fBH", message[start:end])
        intervals = np.empty((existence_intervals_num, 2))
        for interval_num in range(existence_intervals_num):
            start = end
            end += 8
            start_interval_depth, end_interval_depth = struct.unpack(
                "<ff", message[start:end]
            )
            intervals[interval_num][0] = start_interval_depth
            intervals[interval_num][1] = end_interval_depth
        start = end
        end += 2
        curve_name_symbols_count = struct.unpack("<H", message[start:end])[0]
        curve_name_bytes = message[start + 2 : end + curve_name_symbols_count]
        start = end + curve_name_symbols_count
        curve_name = curve_name_bytes.decode("cp1251")
        new_curve = CurveInfo(
            curve_id=curve_id,
            curve_type=curve_tag_id,
            start_depth=start_depth,
            end_depth=end_depth,
            dh=dh,
            min_value=min_value,
            max_value=max_value,
            curve_visibility=visibility,
            intervals=intervals,
            curve_name=curve_name,
        )
        curve_list[curve_num] = new_curve
    if len(curve_list) == 0:
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или скважины с таким идентификатором не существует"
        )
    return curve_list
