from dataclasses import dataclass
from typing import Self

from ._constants import EPS


@dataclass
class Point:
    x: float
    y: float

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Point):
            raise ValueError("Cannot compare Point with non-Point")
        return abs(self.x - __value.x) < EPS and abs(self.y - __value.y) < EPS

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


@dataclass(frozen=True)
class Line:
    m: float
    q: float

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Line):
            raise ValueError("Cannot compare Line with non-Line")
        return abs(self.m - __value.m) < EPS and abs(self.q - __value.q) < EPS

    def __hash__(self) -> int:
        return hash((self.m, self.q))

    def __repr__(self) -> str:
        return f"Line({self.m}, {self.q})"

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

    @classmethod
    def from_line_offset(cls, line: Self, offset: float) -> Self:
        """Create a line from another line with an offset"""
        return cls(line.m, line.q + offset)


class Segment:
    def __init__(self, p1: Point, p2: Point) -> None:
        self.p1 = p1
        self.p2 = p2
        self._line = Line.from_points(p1, p2)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Segment):
            raise ValueError("Cannot compare Segment with non-Segment")
        return self.p1 == __value.p1 and self.p2 == __value.p2

    def __hash__(self) -> int:
        return hash((hash(self.p1), hash(self.p2), hash(self._line)))

    def __repr__(self) -> str:
        return f"Segment({self.p1}, {self.p2})"

    @property
    def is_vertical(self) -> bool:
        """Check if the segment is vertical"""
        return self._line.is_vertical

    @property
    def is_horizontal(self) -> bool:
        """Check if the segment is horizontal"""
        return self.p1.y == self.p2.y

    def order_by_y(self) -> tuple[Point, Point]:
        """Order the segment points by their y coordinate"""
        if self.p1.y > self.p2.y:
            return self.p1, self.p2
        elif self.p1.y < self.p2.y:
            return self.p2, self.p1
        elif self.p1.x < self.p2.x:
            return self.p1, self.p2
        return self.p2, self.p1

    def order_by_x(self) -> tuple[Point, Point]:
        """Order the segment points by their x coordinate"""
        if self.p1.x < self.p2.x:
            return self.p1, self.p2
        elif self.p1.x > self.p2.x:
            return self.p2, self.p1
        elif self.p1.y < self.p2.y:
            return self.p1, self.p2
        return self.p2, self.p1

    def contains(self, point: Point) -> bool:
        """Check if a point is contained in the segment, including endpoints"""
        if point == self.p1 or point == self.p2:
            return True

        cross_product = (point.y - self.p1.y) * (self.p2.x - self.p1.x) - (
            point.x - self.p1.x
        ) * (self.p2.y - self.p1.y)
        if abs(cross_product) > EPS:
            return False

        dot_product = (point.x - self.p1.x) * (self.p2.x - self.p1.x) + (
            point.y - self.p1.y
        ) * (self.p2.y - self.p1.y)
        if dot_product < 0:
            return False

        squared_length = (self.p2.x - self.p1.x) * (self.p2.x - self.p1.x) + (
            self.p2.y - self.p1.y
        ) * (self.p2.y - self.p1.y)
        if dot_product > squared_length:
            return False
        return True

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

    def intersection_with_line(self, line: Line) -> Point:
        """Calculate the intersection point of a segment with a line. Assumes that the segment intersects the line."""
        if not self._line.intersect(line):
            raise ValueError("Segment does not intersect line")
        return self._line.intersection(line)
