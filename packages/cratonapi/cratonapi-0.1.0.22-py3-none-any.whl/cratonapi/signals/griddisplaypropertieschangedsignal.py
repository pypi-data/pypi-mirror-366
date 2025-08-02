from dataclasses import dataclass

from .abstractsignal import AbstractSignal


@dataclass
class GridDisplayPropertiesChangedSignal(AbstractSignal):
    grid_id: int
