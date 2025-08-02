from dataclasses import dataclass

from numpy import ndarray


@dataclass
class WellTrajectory:
    point_depths: ndarray
    point_x_shifts: ndarray
    point_y_shifts: ndarray
    point_z_shifts: ndarray
