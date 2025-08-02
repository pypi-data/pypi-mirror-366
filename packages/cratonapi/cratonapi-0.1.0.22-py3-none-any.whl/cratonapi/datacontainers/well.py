from dataclasses import dataclass


@dataclass
class Well:
    well_id: int
    well_name: str
    outfall_x: float
    outfall_y: float
    altitude: float
    bottom: float
