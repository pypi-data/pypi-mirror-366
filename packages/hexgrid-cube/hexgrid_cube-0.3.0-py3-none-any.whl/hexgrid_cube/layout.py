"""Helper class to represent hexagonal grids in various orientations on the screen."""
from math import sin, cos, pi
from typing import List
from hexgrid_cube import Hex
from hexgrid_cube import Point
from .orientation import Orientation


class Layout:
    """Helper class to convert to and from positions on the screen."""

    def __init__(self, orientation: Orientation, scaler: Point, origin: Point, hex_border=Point(1, 1)):
        if not isinstance(scaler, Point) or not isinstance(origin, Point):
            raise ValueError(f"scaler and origin must be Points, were : {type(scaler)} and {type(origin)} respectively")
        self.orientation = orientation
        self.scaler = scaler  # should default to (side length, side length)
        self.origin = origin
        self.hex_border = hex_border  # scales the black delimiter between hexes on the grid

    def to_pixel(self, h: Hex) -> Point:
        """
        Convert a Hex to screen coordinates.

        Parameters
        ----------
        h : Hex
            The Hex to convert.

        Returns
        -------
        Point
            The screen coordinates of the Hex.
        """
        x = (self.orientation.to_pixel[0]*h.q
             + self.orientation.to_pixel[1]*h.r) * self.scaler.x
        y = (self.orientation.to_pixel[2]*h.q
             + self.orientation.to_pixel[3]*h.r) * self.scaler.y
        return Point(x + self.origin.x, y + self.origin.y)

    def to_hex(self, p: Point) -> Hex:
        """
        Converts a point on the screen to a Hex on the grid.

        Parameters
        ----------
        p : the point to convert to a Hex.

        Returns
        -------
        Hex
            A Hex that fits on the grid.
        """
        corrected_pt = Point((p.x - self.origin.x) / self.scaler.x,
                             (p.y - self.origin.y) / self.scaler.y)
        q = self.orientation.to_hex[0] * corrected_pt.x + self.orientation.to_hex[1]
        r = self.orientation.to_hex[2] * corrected_pt.x + self.orientation.to_hex[3] * corrected_pt.y
        return Hex.fractional_hex(q, r, -q - r)

    def hex_corner_offset(self, corner: int) -> Point:
        """
        Return the point whose coordinates match the Hex's passed `corner` with an offset.

        Initialize layout with hex_border=(0, 0) to get exact coordinates of every corner.

        Parameters
        ----------
        corner : int
            the corner to consider.

        Returns
        -------
        Point
            The point whose coordinates match the Hex's passed `corner`, offset by `self.hex_border`.
        """
        angle = 2.0 * pi * (self.orientation.start_angle + corner) / 6
        # scaler is equal side length, which is also equal to distance between center and corner
        # we subtract hex_border to show black lines in between Hexes
        return Point((self.scaler.x - self.hex_border.x) * cos(angle),
                     (self.scaler.y - self.hex_border.y) * sin(angle))

    def polygon_corners(self, h: Hex) -> List[Point]:
        """
        Takes a Hex `h` and returns a list of Points at its corners.

        Parameters
        ----------
        h : Hex
            the hex whose corners coordinates to calculate.

        Returns
        -------
        List[Point]
            A list of 6 Points representing corners.
        """
        center = self.to_pixel(h)
        corners = [center.add(self.hex_corner_offset(i)) for i in range(6)]
        return corners
