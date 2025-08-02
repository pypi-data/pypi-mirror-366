from dataclasses import dataclass

from numpy import ndarray

from . import Color


@dataclass
class CurveDisplayProperties:
    tag_name: str
    tag_id: int
    description: str
    tag_priority: int
    type_interpolation: int
    type_display: int
    type_scale: int
    auto_scaling: int
    manual_scaling_interval: ndarray
    manual_scaling_step: int
    line_width: float
    line_color: Color
    filling: int
    filling_direction: int
    filling_color1: Color
    filling_color2: Color
    filling_interval: ndarray
