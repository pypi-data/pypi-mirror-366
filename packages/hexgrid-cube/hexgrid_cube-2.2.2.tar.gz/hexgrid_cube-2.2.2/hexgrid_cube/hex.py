"""Class representing a single Hex."""
from typing import Optional, List
from .util import lerp


class Hex:
    """
    Class representing a single Hex in a Hexgrid.

    Attributes
    ----------
    q : int
        the q-axis coordinate of the Hex

    r : int
        the r-axis coordinate of the Hex

    s : int
        the s-axis coordinate of the Hex

    Methods
    -------
    from_tuple(t: tuple)
        Return a new Hex from a tuple

    fractional_hex(q_: float, r_: float, s_: float)
        Return a new Hex from fractional coordinates

    length
        Return the Hex's distance from origin point (0, 0).

    distance(other)
        Calculate distance between `self` and `other`

    direction(direction: int)
        Return a Hex in the passed `direction` from origin

    neighbour(direction: int)
        Return the neighbouring Hex to `self` in the passed `direction`

    hex_lerp(b: Hex, t: float)
        Return the linear interpolation between `self` and Hex `b` at `t`.

    draw_line(b: Hex)
        Return a list of Hexes in a line between `self` and Hex `b`.

    neighbours
        Return a list of neighbouring Hexes
    """

    def __init__(self, q: int, r: int, s: Optional[int] = None, /) -> None:
        """Class constructor."""
        if s is None:
            self.s = -q - r
        else:
            if q + r + s != 0:
                raise ValueError("Any Hex's cube coordinates must sum to 0.")
            self.s = s
        self.q = q
        self.r = r

    @classmethod
    def from_tuple(cls, t: tuple) -> "Hex":
        """
        Return a new Hex from a 2- or 3-tuple.

        Parameters
        ----------
        t: tuple
            the tuple holding the coordinates, either (q, r, s) or (q, r).

        Returns
        -------
        Hex
            A new instance of Hex at the coordinates represented by `t`.

        """
        if len(t) == 2:
            return Hex(t[0], t[1], -t[0] - t[1])
        elif len(t) == 3:
            if t[0] + t[1] + t[2] != 0:
                raise ValueError("Any Hex's cube coordinates must sum to 0.")
            return Hex(t[0], t[1], t[2])
        else:
            raise ValueError("Invalid value passed to constructor, tuple must "
                             "contain 2 or 3 values.")

    @classmethod
    def fractional_hex(cls, q_: float, r_: float, s_: float) -> "Hex":
        """
        Return a new Hex from floating point values.

        Parameters
        ----------
        q_ : float
            the Hex's floating point value q coordinates

        r_ : float
            the Hex's floating point value r coordinates

        s_ : float
            the Hex's floating point value s coordinates

        Returns
        -------
        Hex
            A new instance of Hex on the grid.
        """
        qi = round(q_)
        ri = round(r_)
        si = round(s_)
        q_diff = abs(qi - q_)
        r_diff = abs(ri - r_)
        s_diff = abs(si - s_)
        if q_diff > r_diff and q_diff > s_diff:
            qi = -ri - si
        elif r_diff > s_diff:
            ri = -qi - si
        else:
            si = -qi - ri
        return Hex(qi, ri, si)

    def __str__(self):
        return f"q: {self.q}, r: {self.r}, s: {self.s}"

    def __repr__(self):
        return f"{self.q}, {self.r}, {self.s}"

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def __eq__(self, other):
        """Implement equality."""
        if isinstance(other, Hex):
            return self.q == other.q and self.r == other.r and self.s == other.s
        else:
            raise ValueError("Comparison between Hexes and non-Hexes "
                             f"is not supported, other was : {other}")

    def __add__(self, other):
        """Implement addition."""
        if isinstance(other, Hex):
            return Hex(self.q + other.q, self.r + other.r, self.s + other.s)
        else:
            raise ValueError("Addition between Hexes and non-Hexes "
                             f"is not supported, other was : {other}")

    def __sub__(self, other):
        """Implement subtraction"""
        if isinstance(other, Hex):
            return Hex(self.q - other.q, self.r - other.r, self.s - other.s)
        else:
            raise ValueError("Subtraction between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __mul__(self, factor: int):
        """Implement multiplication."""
        if isinstance(factor, int):
            return Hex(self.q * factor, self.r * factor, self.s * factor)
        else:
            raise ValueError("Multiplication between Hexes and "
                             f"non-int is not supported, other was : {factor}")

    def __truediv__(self, factor: int):
        """Implement division."""
        if isinstance(factor, int):
            return Hex.fractional_hex(self.q / factor, self.r / factor, self.s / factor)
        else:
            raise ValueError("Division between Hexes and non-int is "
                             f"not supported, other was : {factor}")

    def __and__(self, other):
        """Implement logical 'and'."""
        if isinstance(other, Hex):
            return (self.q | self.r | self.s) & (other.q | other.r | other.s)
        else:
            raise ValueError("'and' operation between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __or__(self, other):
        """Implement logical 'or'."""
        if isinstance(other, Hex):
            return (self.q | self.r | self.s) | (other.q | other.r | other.s)
        else:
            raise ValueError("'or' operation between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __xor__(self, other):
        """Implement logical 'xor'."""
        if isinstance(other, Hex):
            return (self.q | self.r | self.s) ^ (other.q | other.r | other.s)
        else:
            raise ValueError("'xor' operation between Hexes and "
                             f"non-Hexes is not supported, other was : {other}")

    def __neg__(self):
        """Implement negation by returning additive inverse."""
        return Hex(-self.q, -self.r, -self.s)

    def __pos__(self):
        """Implement unary plus operator by returning a new value."""
        return Hex(self.q, self.r, self.s)

    def __abs__(self):
        """Implement 'abs()'."""
        return abs(self.q), abs(self.r), abs(self.s)

    def length(self):
        """Return the Hex's distance from origin point (0, 0)."""
        return int(sum(abs(self)) / 2)

    def distance(self, other):
        """Calculate distance between two Hex"""
        return (self - other).length()

    @staticmethod
    def direction(direction: int) -> "Hex":
        """
        Return a Hex representing a hexagonal cardinal direction.

        Parameters
        ----------
        direction : int
            The direction considered, clockwise starting from top left.

        Returns
        -------
        Hex
            An instance of a Hex neighbouring the origin in target direction.
        """
        dirs = (Hex(1, 0, -1), Hex(0, 1, -1), Hex(-1, 1, 0),
                Hex(-1, 0, 1), Hex(0, -1, 1), Hex(1, -1, 0))
        return dirs[direction % 6]

    def neighbour(self, direction: int) -> "Hex":
        """
        Return the neighbouring Hex in target direction.

        Parameters
        ----------
        direction : int
            The direction of the neighbour, clockwise starting from top left.

        Returns
        -------
        Hex
            A new Hex neighbouring self in target direction.
        """
        return self + Hex.direction(direction)

    def hex_lerp(self, b: "Hex", t: float) -> "Hex":
        """
        Return the linear interpolation between self and Hex `b` at `t`.

        Parameters
        ----------
        b : Hex
            the Hex to interpolate with
        t : float
            the interpolation step

        Returns
        -------
        Hex
            A Hex at whose coordinates is at `t` on the line between `self` and Hex `b`.
        """
        return Hex.fractional_hex(lerp(self.q, b.q, t),
                                  lerp(self.r, b.r, t),
                                  lerp(self.s, b.s, t))

    def draw_line(self, b: "Hex") -> List["Hex"]:
        """
        Return a list of Hexes in a line between `self` and Hex `b`.

        Parameters
        ----------
        b : Hex
            the endpoint of the line to draw.

        Returns
        -------
        List[Hex]
            A list of Hexes towards b.
        """
        n = self.distance(b)
        step = 1.0 / max(n, 1)
        return [self.hex_lerp(b, step * i) for i in range(n)]

    def neighbours(self) -> List["Hex"]:
        """
        Return a list of neighbouring Hexes.

        Returns
        -------
        List[Hex]
            A list of Hexes neighbour to self.
        """
        return [self + direction for direction in (Hex(1, 0, -1), Hex(0, 1, -1), Hex(-1, 1, 0),
                                                   Hex(-1, 0, 1), Hex(0, -1, 1), Hex(1, -1, 0))]

    def ring(self, radius: int) -> list["Hex"]:
        """
        Return the list of Hexes in a ring of size `radius` around `self`.

        Parameters
        ----------
        radius: int
            radius of the ring

        Returns
        -------
        list[Hex]
            Hexes in the ring.
        """
        if radius < 1:
            raise ValueError(f"Cannot take ring of radius {radius}.")
        parallel_to_q = ({Hex(self.q + radius, self.r - radius + k, self.s - k)
                          for k in range(radius + 1)}
                         | {Hex(self.q - radius, self.r + radius - k, self.s + k)
                            for k in range(radius + 1)})
        parallel_to_s = ({Hex(self.q - radius + k, self.r - k, self.s + radius)
                          for k in range(radius + 1)}
                         | {Hex(self.q + radius - k, self.r + k, self.s - radius)
                            for k in range(radius + 1)})
        parallel_to_r = ({Hex(self.q - radius + k, self.r + radius, self.s - k)
                          for k in range(radius + 1)}
                         | {Hex(self.q + radius - k, self.r - radius, self.s + k)
                            for k in range(radius + 1)})
        return list(parallel_to_q | parallel_to_r | parallel_to_s)
