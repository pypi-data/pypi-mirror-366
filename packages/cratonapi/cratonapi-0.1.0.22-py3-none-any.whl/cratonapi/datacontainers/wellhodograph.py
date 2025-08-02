from dataclasses import dataclass

from numpy import ndarray


@dataclass
class WellHodograph:
    time_shift: float
    point_times: ndarray
    point_depths: ndarray
