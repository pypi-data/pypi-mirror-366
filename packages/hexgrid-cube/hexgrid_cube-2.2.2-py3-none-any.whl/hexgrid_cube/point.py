"""Class representing a point on the screen."""
from __future__ import annotations
from collections import namedtuple


class Point(namedtuple("Point", "x y")):
    """A basic point on the screen. No direct relation to Hexes."""

    def __new__(cls, x, y):
        return super().__new__(cls, x, y)

    def add(self, p: Point):
        """
        Return a new Point whose coordinates are the sum of self and the point passed as argument.

        Parameters
        ----------
        p : Point
            the point whose coordinates to add.

        Returns
        -------
        A new point.
        """
        return Point(self.x + p.x, self.y + p.y)
