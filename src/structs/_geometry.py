from dataclasses import dataclass
from typing import Self

EPS = 1e-6


@dataclass
class Point:
    x: float
    y: float

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Point):
            raise ValueError("Cannot compare Point with non-Point")
        return abs(self.x - __value.x) < EPS and abs(self.y - __value.y) < EPS

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


class Segment:
    def __init__(self, p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2
        self._line = Line.from_points(p1, p2)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Segment):
            raise ValueError("Cannot compare Segment with non-Segment")
        return self.p1 == __value.p1 and self.p2 == __value.p2

    @property
    def is_vertical(self) -> bool:
        """Check if the segment is vertical"""
        return self._line.is_vertical

    def contains(self, p: Point) -> bool:
        """Check if a point is contained in the segment, including endpoints"""
        if self.is_vertical:
            return (
                min(self.p1.y, self.p2.y) - EPS
                <= p.y
                <= max(self.p1.y, self.p2.y) + EPS
            )
        return min(self.p1.x, self.p2.x) - EPS <= p.x <= max(self.p1.x, self.p2.x) + EPS

    def intersect(self, other: Self) -> bool:
        """Check if two segments intersect"""
        if not self._line.intersect(other._line):
            return False
        line_intersection = self._line.intersection(other._line)
        return self.contains(line_intersection) and other.contains(line_intersection)

    def intersection(self, other: Self) -> Point:
        """Calculate the intersection point of two segments. Assumes that the segments intersect."""
        if not self.intersect(other):
            raise ValueError("Segments do not intersect")
        return self._line.intersection(other._line)


@dataclass
class Line:
    m: float
    q: float

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Line):
            raise ValueError("Cannot compare Line with non-Line")
        return abs(self.m - __value.m) < EPS and abs(self.q - __value.q) < EPS

    @property
    def is_vertical(self) -> bool:
        """Check if the line is vertical"""
        return self.m == float("inf")

    def intersect(self, other: Self) -> bool:
        """Check if two lines intersect"""
        if self.m == other.m and self.q == other.q:
            print("Lines are the same")
        return self.m != other.m

    def intersection(self, other: Self) -> Point:
        """Calculate the intersection point of two lines. Assumes that the lines intersect."""
        if not self.intersect(other):
            raise ValueError("Lines do not intersect")

        if self.is_vertical and other.is_vertical:
            raise ValueError("Lines are parallel")
        elif self.is_vertical:
            return Point(self.q, other.m * self.q + other.q)
        elif other.is_vertical:
            return Point(other.q, self.m * other.q + self.q)

        x = (other.q - self.q) / (self.m - other.m)
        y = self.m * x + self.q
        return Point(x, y)

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> Self:
        """Create a line from two points"""
        if p1.x == p2.x:
            return cls(float("inf"), p1.x)
        m = (p2.y - p1.y) / (p2.x - p1.x)
        q = p1.y - m * p1.x
        return cls(m, q)
