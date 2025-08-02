import struct
from typing import List

import numpy as np

from cratonapi.datacontainers import WellCurve
from cratonapi.exceptions import GISWellExecutionError

NAN_VALUE = -999.25


def parse(message: bytes) -> List[WellCurve]:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 3:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")

    n_curves = struct.unpack("<I", message[16:20])[0]
    start_idx = 20
    curve_list = []
    for n in range(n_curves):

        end_idx = start_idx + 4
        tag_id = struct.unpack("<I", message[start_idx:end_idx])[0]

        start_idx = end_idx
        end_idx += 2
        number_of_symbols_i = struct.unpack("<H", message[start_idx:end_idx])[0]

        start_idx = end_idx
        end_idx += number_of_symbols_i
        curve_name_i = message[start_idx:end_idx].decode("cp1251")

        start_idx = end_idx
        end_idx += 4
        number_of_counts_i = struct.unpack("<I", message[start_idx:end_idx])[0]

        point_values_i = np.empty(number_of_counts_i)
        point_depths_i = np.empty(number_of_counts_i)
        curve_shift = 16
        half_curve_shift = curve_shift // 2
        for j in range(number_of_counts_i):
            left_values_idx = end_idx + j * curve_shift
            right_values_idx = left_values_idx + half_curve_shift
            left_depth_idx = right_values_idx
            right_depth_idx = left_depth_idx + half_curve_shift
            point_values_i_j = struct.unpack(
                "<d", message[left_values_idx:right_values_idx]
            )[0]
            point_depths_i_j = struct.unpack(
                "<d", message[left_depth_idx:right_depth_idx]
            )[0]
            point_values_i[j] = point_values_i_j
            point_depths_i[j] = point_depths_i_j

        condition = point_values_i == NAN_VALUE
        point_values_i[condition] = np.nan

        curve_list.append(
            WellCurve(
                curve_type=tag_id,
                curve_name=curve_name_i,
                point_values=point_values_i,
                point_depths=point_depths_i,
            )
        )

        start_idx = right_depth_idx
    if len(curve_list) == 0:
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или скважины с таким идентификатором не существует"
        )
    return curve_list
