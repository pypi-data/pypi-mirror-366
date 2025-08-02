from dataclasses import dataclass

from numpy import ndarray


@dataclass
class CubeDataSlice:
    samples_count: int
    start_idx: int
    inlines: ndarray
    xlines: ndarray
    data: ndarray
