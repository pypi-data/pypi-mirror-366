from dataclasses import dataclass

from numpy import ndarray


@dataclass
class Curve:
    curve_id: int
    point_values: ndarray
    point_depths: ndarray
