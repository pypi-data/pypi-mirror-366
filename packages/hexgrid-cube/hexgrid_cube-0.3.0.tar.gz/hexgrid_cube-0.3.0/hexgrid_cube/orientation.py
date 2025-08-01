"""Utility class containing constants relative to specific hexagonal grid orientations."""
from math import sqrt
from typing import Tuple


class Orientation:
    """Helper class to represent pointy-top and flat-top layouts."""

    def __init__(self, to_pixel: Tuple[float, float, float, float],
                 to_hex: Tuple[float, float, float, float],
                 start_angle: float):
        self.to_pixel = to_pixel
        self.to_hex = to_hex
        self.start_angle = start_angle


POINTY_TOP_ORIENTATION = Orientation((sqrt(3), sqrt(3) / 2, 0, 3.0 / 2.0),
                                     (sqrt(3) / 3.0, -1.0 / 3.0, 0, 2.0 / 3.0),
                                     0.5)

FLAT_TOP_ORIENTATION = Orientation((3.0 / 2.0, 0.0, sqrt(3) / 2.0, sqrt(3)),
                                   (2.0 / 3.0, 0.0, -1 / 3.0, sqrt(3) / 3.0),
                                   0.0)
