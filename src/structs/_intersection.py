from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Optional

from src.utils import ClassComparisonError

from ._constants import EPS
from ._geometry import Line, Point, Segment


#########################################
# Intersection data structures
#########################################
class EventType(Enum):
    START = 1
    INTERSECTION = 2
    END = 3


@dataclass(frozen=True)
@total_ordering
class EventPoint:
    """Event point for the sweep line algorithm. Event points are ordered by their y
    from top to bottom. If the y coordinate is the same, they are ordered based on their
    x coordinate, left to right."""

    type: EventType
    point: Point
    segments: list[Segment]

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, EventPoint):
            raise ClassComparisonError("Cannot compare EventPoint with non-EventPoint")
        return self.point == __value.point

    def __hash__(self) -> int:
        return hash((hash(self.type), hash(self.type), hash(self.segments)))

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, EventPoint):
            raise ClassComparisonError("Cannot compare EventPoint with non-EventPoint")

        if abs(self.point.y - __value.point.y) < EPS:
            return self.point.x > __value.point.x
        return self.point.y < __value.point.y

    def add_segments(self, segments: Segment | list[Segment]) -> None:
        """Add a list of segments to the event point. If the segment is already in the event point,
        it is not added again.

        Params:
        - segments: Segment | list[Segment]: The segments to add to the event point"""
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

        self.status, self._segments_scores = self._sort(status, sweep_line)

    def __iter__(self):
        return iter(self.status)

    def __getitem__(self, index: int) -> Segment:
        return self.status[index]

    def __setitem__(self, index: int, value: Segment) -> None:
        raise ClassComparisonError("Cannot set items in the sweep line")

    def __len__(self) -> int:
        return len(self.status)

    def add(self, segments: Segment | list[Segment], sweep_line: Line) -> None:
        """Add a segment to the sweep line. The segment is inserted
        in the correct position based on where it intersects the horizontal sweep line.
        For horizontal segments, the segment is inserted after the last element of the
        newly inserted segments.

        Params:
        - segments: Segment | list[Segment]: The segments to add to the sweep line
        """
        if isinstance(segments, Segment):
            segments = [segments]

        new_segments, new_scores = self._sort(segments, sweep_line)
        old_segments, old_scores = self._sort(
            self.status, sweep_line, previous_scores=self._segments_scores
        )

        self.status, self._segments_scores = self._merge(
            (old_segments, old_scores), (new_segments, new_scores)
        )

    def remove(self, segments: list[Segment] | Segment) -> None:
        """Remove a list of segments from the sweep line

        Params:
        - segments: list[Segment] | Segment: The segments to remove from the sweep line
        """
        if isinstance(segments, Segment):
            segments = [segments]
        for segment in segments:
            index = self.status.index(segment)
            self.status.pop(index)
            self._segments_scores.pop(index)

    def index(self, segment: Segment) -> int:
        """Return the index of a segment in the sweep line. If the segment is not in the sweep line,
        a ClassesComparisonError is raised.

        Params:
        - segment: Segment: The segment to find in the sweep line
        """
        return self.status.index(segment)

    def neighbours(self, point: Point) -> tuple[Optional[Segment], Optional[Segment]]:
        """Return the segments to the right and to the left of a point on the sweep line. If the point is
        to the left of the first segment or to the right of the last segment, the corresponding neighbour
        is None.

        Params:
        - point: Point: The point to find the neighbours for

        Returns:
        - tuple[Optional[Segment], Optional[Segment]]: The left and right segments of the point
        """
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

    def _sort(
        self,
        segments: list[Segment],
        sweep_line: Line,
        previous_scores: Optional[list[float]] = None,
    ) -> tuple[list[Segment], list[float]]:
        """Sort the segments in the sweep line based on their intersection with the sweep line. For horizontal
        segments, if previous scores are provided then they're used. If not, the horizontal segment is inserted
        at the end of the list."""
        status: list[tuple[Segment, float]] = []
        horizontal_segment_idx: Optional[int] = None
        for i, segment in enumerate(segments):
            if segment.is_horizontal:
                horizontal_segment_idx = i
                continue
            status.append((segment, self._sort_key(segment, sweep_line)))

        if horizontal_segment_idx is not None and previous_scores is not None:
            status.append(
                (
                    segments[horizontal_segment_idx],
                    previous_scores[horizontal_segment_idx],
                )
            )

        status = sorted(status, key=lambda x: x[1])

        if horizontal_segment_idx is not None and previous_scores is None:
            horizontal_segment = segments[horizontal_segment_idx]
            if len(status) > 0:
                max_segment = status[-1]
                status.append((horizontal_segment, max_segment[1] + EPS))
            else:
                start, _ = horizontal_segment.order_by_x()
                status.append((horizontal_segment, start.x - EPS))

        return [segment for segment, _ in status], [score for _, score in status]

    def _sort_key(self, segment: Segment, sweep_line: Line) -> float:
        return segment.intersection_with_line(sweep_line).x

    def _merge(
        self,
        l1: tuple[list[Segment], list[float]],
        l2: tuple[list[Segment], list[float]],
    ) -> tuple[list[Segment], list[float]]:
        """Merges two sorted lists of segments based on their intersection with the sweep line into a single list.

        Params:
        - l1: tuple[list[Segment], list[float]]: The first list of segments and their intersection with the sweep line
        - l2: tuple[list[Segment], list[float]]: The second list of segments and their intersection with the sweep line

        Returns:
        - tuple[list[Segment], list[float]]: The merged list of segments and their intersection with the sweep line
        """
        new_list: tuple[list[Segment], list[float]] = ([], [])

        i, j = 0, 0
        while i < len(l1[0]) and j < len(l2[0]):
            if l1[1][i] < l2[1][j]:
                new_list[0].append(l1[0][i])
                new_list[1].append(l1[1][i])
                i += 1
            else:
                new_list[0].append(l2[0][j])
                new_list[1].append(l2[1][j])
                j += 1

        while i < len(l1[0]):
            new_list[0].append(l1[0][i])
            new_list[1].append(l1[1][i])
            i += 1

        while j < len(l2[0]):
            new_list[0].append(l2[0][j])
            new_list[1].append(l2[1][j])
            j += 1

        return new_list
