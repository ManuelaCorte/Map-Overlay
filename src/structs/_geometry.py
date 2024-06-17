from dataclasses import dataclass
from typing import Optional, Self

from ._constants import EPS, SIGNIFICANT_DIGITS
from src.utils import ClassComparisonError, CollinearityError, trunc_float


@dataclass
class Point:
    """A point in 2d space. Two points are considered equal if their coordinates are within EPS of each other"""

    x: float
    y: float

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Point):
            raise ClassComparisonError("Cannot compare Point with non-Point")
        return abs(self.x - __value.x) < EPS and abs(self.y - __value.y) < EPS

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __hash__(self) -> int:
        return hash(
            (
                trunc_float(self.x, SIGNIFICANT_DIGITS),
                trunc_float(self.y, SIGNIFICANT_DIGITS),
            )
        )

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"

    def __iter__(self):
        return iter((self.x, self.y))


@dataclass(frozen=True)
class Line:
    """A infinite line in 2d space, represented by the equation y = mx + q. For vertical lines,
    m is inf and q is the x coordinate of the line."""

    m: float
    q: float

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Line):
            raise ClassComparisonError("Cannot compare Line with non-Line")
        return abs(self.m - __value.m) < EPS and abs(self.q - __value.q) < EPS

    def __hash__(self) -> int:
        return hash((self.m, self.q))

    def __repr__(self) -> str:
        return f"Line({self.m}, {self.q})"

    @property
    def is_vertical(self) -> bool:
        """Check if the line is vertical"""
        return self.m == float("inf")

    @property
    def is_horizontal(self) -> bool:
        """Check if the line is horizontal"""
        return self.m < EPS

    def is_collinear(self, other: Self) -> bool:
        """Check if two lines are collinear (they're parallel and lie on the same line)"""
        return abs(self.m - other.m) < EPS and abs(self.q - other.q) < EPS

    def intersection(self, other: Self) -> Optional[Point]:
        """Calculate the intersection point of two lines. If the two lines overlap then
        no intersection point is returned.

        Returns:
            Point: The intersection point of the two lines"""
        if self.is_vertical and other.is_vertical:
            return None

        if self.is_vertical:
            return Point(self.q, other.m * self.q + other.q)

        if other.is_vertical:
            return Point(other.q, self.m * other.q + self.q)

        if abs(self.m - other.m) < EPS:
            return None

        x = (other.q - self.q) / (self.m - other.m)
        y = self.m * x + self.q
        return Point(x, y)

    @classmethod
    def from_points(cls, p1: Point, p2: Point) -> Self:
        """Create a line from two points as follows:
        - m = (y2 - y1) / (x2 - x1)
        - q = y1 - m * x1

        If the line is vertical, m is inf and q is the x coordinate of the line."""
        if abs(p1.x - p2.x) < EPS:
            return cls(float("inf"), p1.x)
        m = (p2.y - p1.y) / (p2.x - p1.x)
        q = p1.y - m * p1.x
        return cls(m, q)

    @classmethod
    def from_line_offset(cls, line: Self, offset: float) -> Self:
        """Create a line by adding an offset to the q parameter of another line. This is useful for
        creating parallel lines."""
        return cls(line.m, line.q + offset)


class Segment:
    """A line segment in 2d space, represented by two points. Two segments are considered equal if their endpoints are
    equal."""

    def __init__(self, p1: Point, p2: Point, id: str = "") -> None:
        self.p1 = p1
        self.p2 = p2
        self._line = Line.from_points(p1, p2)
        self.id = id

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Segment):
            raise ClassComparisonError("Cannot compare Segment with non-Segment")
        return (self.p1 == __value.p1 and self.p2 == __value.p2) or (
            self.p1 == __value.p2 and self.p2 == __value.p1
        )

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
        return abs(self.p1.y - self.p2.y) < EPS

    def is_collinear(self, other: Self) -> bool:
        """Check if two segments are collinear (they're parallel and lie on the same line) and they
        overlap in at least one point (endpoints included)"""
        is_contained = (
            self.contains(other.p1)
            or self.contains(other.p2)
            or other.contains(self.p1)
            or other.contains(self.p2)
        )
        return self._line.is_collinear(other._line) and is_contained

    def order_by_y(self) -> tuple[Point, Point]:
        """Order the segment points by their y coordinate where the start point is the one with the highest y coordinate.
        If both points have the same y coordinate, the start point is the one with the x coordinate most to the left.

        Returns:
            tuple[Point, Point]: The start and end points of the segment
        """
        if self.p1.y > self.p2.y:
            return self.p1, self.p2
        elif self.p1.y < self.p2.y:
            return self.p2, self.p1
        elif self.p1.x < self.p2.x:
            return self.p1, self.p2
        return self.p2, self.p1

    def order_by_x(self) -> tuple[Point, Point]:
        """Order the segment points by their x coordinate where the start point is the one with the x coordinate most to the
        left. If both points have the same x coordinate, the start point is the one with the highest y coordinate.

        Returns:
            tuple[Point, Point]: The start and end points of the segment
        """
        if self.p1.x < self.p2.x:
            return self.p1, self.p2
        elif self.p1.x > self.p2.x:
            return self.p2, self.p1
        elif self.p1.y > self.p2.y:
            return self.p1, self.p2
        return self.p2, self.p1

    def contains(self, point: Point) -> bool:
        """Check if a point is contained in the segment, endpoints included. The procedure is described
        in https://lucidar.me/en/mathematics/check-if-a-point-belongs-on-a-line-segment/
        """
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

    def shared_endpoint(self, other: Self) -> Optional[Point]:
        """Check if two segments share an endpoint"""
        if self.p1 == other.p1 or self.p1 == other.p2:
            return self.p1
        if self.p2 == other.p1 or self.p2 == other.p2:
            return self.p2
        return None

    def intersection(self, other: Self) -> Optional[Point]:
        """Calculate the intersection point of two segments. Collinear segments that only share the
        endpoint are considered as intersecting"""
        if self.is_collinear(other):
            shared_endpoint = self.shared_endpoint(other)
            if shared_endpoint is not None:
                return shared_endpoint
            else:
                raise CollinearityError(
                    f"Segments {self} and {other} are collinear but don't share an endpoint"
                )

        line_intersection = self._line.intersection(other._line)
        if line_intersection is not None:
            if self.contains(line_intersection) and other.contains(line_intersection):
                return line_intersection
        return None

    def intersection_with_line(self, line: Line) -> Point:
        """Calculate the intersection point of a segment with a line. Assumes that the segment doesn't lie
        on the line."""
        if self._line.is_collinear(line):
            raise CollinearityError(f"Segment {self} is collinear with line {line}")

        intersection = self._line.intersection(line)
        if intersection is None:
            raise ValueError(f"Segment {self} doesn't intersect line {line}")
        return intersection
