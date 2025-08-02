from dataclasses import dataclass

from .abstractsignal import AbstractSignal


@dataclass
class GridListChangedSignal(AbstractSignal):
    pass
