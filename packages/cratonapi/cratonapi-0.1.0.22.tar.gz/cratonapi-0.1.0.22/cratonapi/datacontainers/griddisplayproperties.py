from dataclasses import dataclass

from numpy import ndarray

from . import Color


@dataclass
class GridDisplayProperties:
    isoline_min_level: float
    isoline_max_level: float
    isoline_level_step: float
    minor_isoline_color: Color
    minor_isoline_thickness: float
    major_isoline_color: Color
    major_isoline_thickness: float
    major_isoline_step: int
    min_palette_level: float
    max_palette_level: float
    color_interpolation_type: int
    palette_values: ndarray
    palette_colors: ndarray
