from dataclasses import dataclass

from numpy import ndarray


@dataclass
class WellCurve:
    curve_type: int
    curve_name: str
    point_values: ndarray
    point_depths: ndarray
