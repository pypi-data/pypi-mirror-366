from dataclasses import dataclass


@dataclass
class StratigraphicLevel:
    level_id: int
    level_age: float
    level_name: str
