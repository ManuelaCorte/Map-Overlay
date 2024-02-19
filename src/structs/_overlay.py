from dataclasses import dataclass
from typing import Optional
from ._constants import EventType, EPS
from ._geometry import Point, Segment, Line
from functools import total_ordering


#########################################
# Intersection data structures
#########################################


@dataclass
@total_ordering
class EventPoint:
    """Event point fro the sweep line algorithm. Event points are ordered by their y
    from top to bottom. If the y coordinate is the same, they are ordered based on their
    x coordinate, left to right."""

    type: EventType
    point: Point
    segments: list[Segment]

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, EventPoint):
            raise ValueError("Cannot compare EventPoint with non-EventPoint")
        return self.point == __value.point

    def __hash__(self) -> int:
        return hash((hash(self.type), hash(self.type), hash(self.segments)))

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, EventPoint):
            raise ValueError("Cannot compare EventPoint with non-EventPoint")

        if abs(self.point.y - __value.point.y) < EPS:
            return self.point.x > __value.point.x
        return self.point.y < __value.point.y

    def add_segments(self, segments: Segment | list[Segment]) -> None:
        """Add a list of segments to the event point. If the segment is already in the event point,
        it is not added again."""
        if isinstance(segments, Segment):
            segments = [segments]
        for segment in segments:
            if segment not in self.segments:
                self.segments.append(segment)


class Status:
    """Horizontal sweep line for segments intersection. Contains the segments currently intersecting the line
    ordered by their x coordinate from left to right."""

    def __init__(self, status: list[Segment], sweep_line: Line) -> None:
        self.status: list[Segment] = []
        self._segments_scores: list[float] = []

        self.status, self._segments_scores = self.sort(status, sweep_line)

        self._horizontal_segment: Optional[Segment] = None
        self._last_segment_before_horizontal: Optional[Segment] = None

    def __iter__(self):
        return iter(self.status)

    def __getitem__(self, index: int) -> Segment:
        return self.status[index]

    def __setitem__(self, index: int, value: Segment) -> None:
        raise ValueError("Cannot set items in the sweep line")

    def __len__(self) -> int:
        return len(self.status)

    def add(self, segments: Segment | list[Segment], sweep_line: Line) -> None:
        """Add a segment to the sweep line. The segment is inserted
        in the correct position based on where it intersects the horizontal sweep line.
        """
        if isinstance(segments, Segment):
            segments = [segments]

        new_segments, _ = self.sort(segments, sweep_line, find_horizontal=True)

        self.status.extend(new_segments)
        self.status, self._segments_scores = self.sort(self.status, sweep_line)
        if self._horizontal_segment is not None:
            if self._last_segment_before_horizontal is not None:
                index = self.status.index(self._last_segment_before_horizontal)
                self.status.insert(index + 1, self._horizontal_segment)
                self._segments_scores.insert(
                    index + 1, self._segments_scores[index] + EPS
                )
            else:
                index = 0
                start, _ = self._horizontal_segment.order_by_x()
                horizontal_segment_score = start.x - EPS
                for i in range(len(self._segments_scores)):
                    if self._segments_scores[i] > horizontal_segment_score:
                        index = i
                        break
                self.status.insert(index, self._horizontal_segment)
                self._segments_scores.insert(index, horizontal_segment_score)

    def remove(self, segments: list[Segment] | Segment) -> None:
        """Remove a list of segments from the sweep line"""
        if isinstance(segments, Segment):
            segments = [segments]
        for segment in segments:
            if (
                self._horizontal_segment is not None
                and segment == self._horizontal_segment
            ):
                self._horizontal_segment = None
                self._last_segment_before_horizontal = None
            index = self.status.index(segment)
            self.status.pop(index)
            self._segments_scores.pop(index)

    def index(self, segment: Segment) -> int:
        """Return the index of a segment in the sweep line"""
        return self.status.index(segment)

    def neighbours(self, point: Point) -> tuple[Optional[Segment], Optional[Segment]]:
        """Return the left and right neighbours of a point in the sweep line"""
        segments_intersection: list[tuple[Segment, float]] = []
        for segment in self.status:
            intersection = self._sort_key(segment, Line(0, point.y))
            segments_intersection.append((segment, intersection))

        segments_intersection = sorted(segments_intersection, key=lambda x: x[1])
        left: Optional[Segment] = None
        right: Optional[Segment] = None
        for i in range(0, len(segments_intersection) - 1):
            if (
                segments_intersection[i][1]
                <= point.x
                <= segments_intersection[i + 1][1]
            ):
                left = segments_intersection[i][0]
                right = segments_intersection[i + 1][0]
                break
        return left, right

    def sort(
        self, segments: list[Segment], sweep_line: Line, find_horizontal: bool = False
    ) -> tuple[list[Segment], list[float]]:
        """Sort the segments in the sweep line based on their intersection with the sweep line"""
        status: list[tuple[Segment, float]] = []
        for segment in segments:
            if segment.is_horizontal:
                if find_horizontal:
                    self._horizontal_segment = segment
                continue
            status.append((segment, self._sort_key(segment, sweep_line)))
        status = sorted(status, key=lambda x: x[1])
        if find_horizontal:
            if len(status) > 0:
                self._last_segment_before_horizontal = status[-1][0]
            else:
                self._last_segment_before_horizontal = None
        return [segment for segment, _ in status], [score for _, score in status]

    def _sort_key(self, segment: Segment, sweep_line: Line) -> float:
        return segment.intersection_with_line(sweep_line).x


#########################################
# Overlay data structures
#########################################
