from dataclasses import dataclass

from numpy import ndarray


@dataclass
class CurveInfo:
    curve_id: int
    curve_type: int
    curve_name: str
    curve_visibility: int
    start_depth: float
    end_depth: float
    dh: float
    min_value: float
    max_value: float
    intervals: ndarray
