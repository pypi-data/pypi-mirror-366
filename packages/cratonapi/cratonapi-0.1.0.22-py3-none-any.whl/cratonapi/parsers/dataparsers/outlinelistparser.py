import struct

import numpy as np

from cratonapi.datacontainers import Color, OutlineInfo
from cratonapi.exceptions import DesmanaExecutionError


def parse(message: bytes) -> np.ndarray:
    if len(message) < 16:
        raise RuntimeError("Incomplete message!")
    signature = message[0:4].decode("utf-8")
    if signature != "WSPM":
        raise RuntimeError("Incorrect signature!")
    size, operation, request, uid = struct.unpack("<IHHI", message[4:16])
    if operation != 3 or request != 30:
        raise RuntimeError("Incorrect operation or request codes!")
    if len(message) - 8 != size:
        raise RuntimeError("Incomplete message!")
    if uid == 0:
        raise DesmanaExecutionError("Desmana is not open!")

    outlines_count = struct.unpack("<I", message[16:20])[0]
    print(outlines_count)
    offset = 0
    outline_list = np.empty(outlines_count, OutlineInfo)
    for outline_num in range(outlines_count):
        outline_id, outline_name_symbols_count = struct.unpack(
            "<IH", message[20 + offset : 26 + offset]
        )
        outline_name_bytes = message[
            26 + offset : 26 + offset + outline_name_symbols_count
        ]
        offset += outline_name_symbols_count + 6
        outline_name = outline_name_bytes.decode("cp1251")

        (
            pen_width,
            pen_style,
            pen_color_b,
            pen_color_g,
            pen_color_r,
            pen_color_a,
            outline_width,
            outline_style,
            outline_color_b,
            outline_color_g,
            outline_color_r,
            outline_color_a,
            fill_color_b,
            fill_color_g,
            fill_color_r,
            fill_color_a,
            fill_style,
            sz,
        ) = struct.unpack("<17BH", message[20 + offset : 39 + offset])
        offset += 19
        new_outline = OutlineInfo(
            outline_id=outline_id,
            outline_name=outline_name,
            pen_width=pen_width,
            pen_style=pen_style,
            pen_color=Color(
                red=pen_color_r, green=pen_color_g, blue=pen_color_b, alpha=pen_color_a
            ),
            outline_width=outline_width,
            outline_style=outline_style,
            outline_color=Color(
                red=outline_color_r,
                green=outline_color_g,
                blue=outline_color_b,
                alpha=outline_color_a,
            ),
            fill_style=fill_style,
            fill_color=Color(
                red=fill_color_r,
                green=fill_color_g,
                blue=fill_color_b,
                alpha=fill_color_a,
            ),
        )
        outline_list[outline_num] = new_outline

    if len(outline_list) != outlines_count:
        raise DesmanaExecutionError("Проект в Desmana не открыт")
    return outline_list
