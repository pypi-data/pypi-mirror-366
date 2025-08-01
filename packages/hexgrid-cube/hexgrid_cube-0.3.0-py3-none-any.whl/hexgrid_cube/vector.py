"""Class representing a vector of hexgrid coordinates."""
from typing import Optional, Union
from .hex import Hex


class Vector:

    def __init__(self, q: float, r: float, s: Optional[float] = None, /, start: Optional[Hex] = None) -> None:
        """Class constructor."""
        if s is None:
            self.s = -q - r
        else:
            if q + r + s != 0:
                raise ValueError("Any Hex's cube coordinates must sum to 0.")
            self.s = s
        self.q = q
        self.r = r
        self.start = start

    @classmethod
    def from_hexes(cls, start: Hex, end: Hex):
        return Vector(float(end.q - start.q), float(end.r - start.r), float(end.s - start.s), start=start)

    @classmethod
    def from_origin(cls, end: Hex):
        """Return the origin->`end` vector. Basically, a Hex->Vector converter."""
        return Vector(float(end.q), float(end.r), float(end.s), start=Hex(0, 0))

    def __str__(self):
        return f"q: {self.q}, r: {self.r}, s: {self.s}"

    def __repr__(self):
        return f"{self.q}, {self.r}, {self.s}"

    def __hash__(self):
        return hash((self.q, self.r, self.s))

    def __eq__(self, other):
        """Implement equality."""
        if isinstance(other, Vector):
            return self.q == other.q and self.r == other.r and self.s == other.s
        else:
            raise ValueError("Comparison between Vectors and non-Vectors "
                             f"is not supported, other was : {other}")

    def __add__(self, other):
        """Implement addition."""
        if isinstance(other, Vector):
            return Vector(self.q + other.q, self.r + other.r, self.s + other.s)
        else:
            raise ValueError("Addition between Vector and non-Vector "
                             f"is not supported, other was : {other}")

    def __sub__(self, other):
        """Implement subtraction"""
        if isinstance(other, Vector):
            return Vector(self.q - other.q, self.r - other.r, self.s - other.s)
        else:
            raise ValueError("Subtraction between Vectors and "
                             f"non-Vectors is not supported, other was : {other}")

    def __mul__(self, factor: Union[float, int]):
        """Implement multiplication."""
        if isinstance(factor, float) or isinstance(factor, int):
            return Vector(self.q * factor, self.r * factor, self.s * factor)
        else:
            raise ValueError("Multiplication is only supported between Vector "
                             f"and int or float, other was : {factor}")

    def __truediv__(self, factor: int):
        """Implement division."""
        return Vector(self.q / factor, self.r / factor, self.s / factor)

    def __and__(self, other):
        """Implement logical 'and'."""
        if isinstance(other, Vector):
            return (self.q or self.r or self.s) and (other.q or other.r or other.s)
        else:
            raise ValueError("'and' operation between Vector and "
                             f"non-Vector is not supported, other was : {other}")

    def __or__(self, other):
        """Implement logical 'or'."""
        if isinstance(other, Vector):
            return (self.q or self.r or self.s) or (other.q or other.r or other.s)
        else:
            raise ValueError("'or' operation between Vectors and "
                             f"non-Vectors is not supported, other was : {other}")

    def __xor__(self, other):
        """Implement logical 'xor'."""
        if isinstance(other, Vector):
            return bool(self.q or self.r or self.s) ^ bool(other.q or other.r or other.s)
        else:
            raise ValueError("'xor' operation between Vectors and "
                             f"non-Vectors is not supported, other was : {other}")

    def __neg__(self):
        """Implement negation by returning additive inverse."""
        return Vector(-self.q, -self.r, -self.s)

    def __pos__(self):
        """Implement unary plus operator by returning a new value."""
        return Vector(self.q, self.r, self.s)

    def __abs__(self):
        """Implement 'abs()'."""
        return abs(self.q), abs(self.r), abs(self.s)

    def __matmul__(self, other: "Vector") -> float:
        """Implement dot product `@`."""
        return (self.q*other.q + self.r*other.r + self.s*other.s)/2

    def rotate(self, degree: int):
        """Return a new vector, rotated by and angle of `degree`."""
        match degree % 360:
            case 0:
                return self
            case 60:
                return Vector(-self.r, -self.s, -self.q)
            case 120:
                return Vector(self.s, self.q, self.r)
            case 180:
                return Vector(-self.q, -self.r, -self.s)
            case 240:
                return Vector(self.r, self.s, self.q)
            case 300:
                return Vector(-self.s, -self.q, -self.r)
            case _:
                raise ValueError("Only multiples of 60° are supported.")

    def to_hex(self):
        """Vector->Hex converter function."""
        if self.start is None:
            return Hex.fractional_hex(self.q, self.r, self.s)
        else:
            target = self + Vector.from_origin(end=self.start)
            return Hex.fractional_hex(target.q, target.r, target.s)

    def length(self):
        """Return the Hex's distance from origin point (0, 0)."""
        return int(sum(abs(self)) / 2)
