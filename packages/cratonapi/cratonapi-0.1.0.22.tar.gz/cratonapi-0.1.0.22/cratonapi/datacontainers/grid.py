from dataclasses import dataclass

from numpy import ndarray


@dataclass
class Grid:
    n_id: int
    n_x: int
    n_y: int
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    blank_code: float
    data: ndarray
