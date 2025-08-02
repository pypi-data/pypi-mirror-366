import struct

import numpy as np

from cratonapi.datacontainers import Color, CurveDisplayProperties
from cratonapi.exceptions import GISWellExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 12:
        print()
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise GISWellExecutionError("GISWell is not open!")

    count = struct.unpack("<I", message[16:20])[0]
    offset = 20
    curve_display_properties_list = np.empty(count, dtype=CurveDisplayProperties)
    for num in range(count):
        (
            tag_id,
            tag_priority,
            type_interpolation,
            type_display,
            type_scale,
            auto_scaling,
            start_manual_scaling,
            end_manual_scaling,
            manual_scaling_step,
            line_width,
            line_b,
            line_g,
            line_r,
            line_alpha,
            filling,
            filling_direction,
            filling_b_1,
            filling_g_1,
            filling_r_1,
            filling_alpha_1,
            filling_b_2,
            filling_g_2,
            filling_r_2,
            filling_alpha_2,
            start_filling,
            end_filling,
            tag_name_symbols_count,
        ) = struct.unpack("<IH4BffHf16BH", message[offset : offset + 42])
        offset += 42
        tag_name_bytes = message[offset : offset + tag_name_symbols_count]
        tag_name = tag_name_bytes.decode("cp1251")
        offset += tag_name_symbols_count
        description_symbols_count = struct.unpack("<H", message[offset : offset + 2])[0]
        description_bytes = message[offset + 2 : offset + 2 + description_symbols_count]
        description = description_bytes.decode("cp1251")
        offset += 2 + description_symbols_count
        curve_display_properties_list[num] = CurveDisplayProperties(
            tag_id=tag_id,
            tag_priority=tag_priority,
            type_interpolation=type_interpolation,
            type_display=type_display,
            type_scale=type_scale,
            auto_scaling=auto_scaling,
            manual_scaling_interval=np.array(
                [start_manual_scaling, end_manual_scaling]
            ),
            manual_scaling_step=manual_scaling_step,
            line_width=line_width,
            line_color=Color(alpha=line_alpha, red=line_r, green=line_g, blue=line_b),
            filling=filling,
            filling_direction=filling_direction,
            filling_color1=Color(
                alpha=filling_alpha_1,
                red=filling_r_1,
                green=filling_g_1,
                blue=filling_b_1,
            ),
            filling_color2=Color(
                alpha=filling_alpha_2,
                red=filling_r_2,
                green=filling_g_2,
                blue=filling_b_2,
            ),
            filling_interval=np.array([start_filling, end_filling]),
            tag_name=tag_name,
            description=description,
        )
    if count == 0:
        raise GISWellExecutionError(
            "Проект в GISWell не открыт или неверно заданы идентификаторы скважины и/или кривой"
        )
    return curve_display_properties_list
