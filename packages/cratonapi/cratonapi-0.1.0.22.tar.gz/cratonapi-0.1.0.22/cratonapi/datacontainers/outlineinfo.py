from dataclasses import dataclass

from cratonapi.datacontainers import Color


@dataclass
class OutlineInfo:
    outline_id: int
    outline_name: str
    pen_width: int
    pen_style: int
    pen_color: Color
    outline_width: int
    outline_style: int
    outline_color: Color
    fill_style: int
    fill_color: Color
