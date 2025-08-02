from dataclasses import dataclass

from .abstractsignal import AbstractSignal


@dataclass
class WellListChangedSignal(AbstractSignal):
    pass
