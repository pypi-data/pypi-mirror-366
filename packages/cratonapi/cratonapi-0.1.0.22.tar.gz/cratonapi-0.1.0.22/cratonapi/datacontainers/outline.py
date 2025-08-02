from dataclasses import dataclass

from numpy import ndarray


@dataclass
class Outline:
    blanking_flag: int
    coordinates: ndarray
