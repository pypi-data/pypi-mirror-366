from dataclasses import dataclass


@dataclass
class GridInfo:
    grid_id: int
    grid_name: str
    grid_type: int
    grid_visibility: int
