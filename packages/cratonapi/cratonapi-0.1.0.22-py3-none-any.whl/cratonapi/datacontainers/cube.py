from dataclasses import dataclass


@dataclass
class Cube:
    x_min_inl_min_xl: float
    y_min_inl_min_xl: float
    x_max_inl_min_xl: float
    y_max_inl_min_xl: float
    x_min_inl_max_xl: float
    y_min_inl_max_xl: float
    x_max_inl_max_xl: float
    y_max_inl_max_xl: float
    inline_count: int
    xline_count: int
    samples_count: int
    dt: int
    cube_type: int
    min_idx_inline: int
    min_idx_xline: int
