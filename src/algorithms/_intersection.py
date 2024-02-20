from typing import Optional
from src.structs import (
    Segment,
    Point,
    Status,
    EventPoint,
    RedBlackTree,
    EventType,
    EPS,
    Line,
)
from src.utils import lists_union


def naive_intersection(segments: list[Segment]) -> list[Point]:
    """Find the intersection points of a list of segments using the naive algorithm. This algorithm
    has a time complexity of O(n^2) where n is the number of segments."""
    intersections: list[Point] = []
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if segments[i].intersect(segments[j]):
                intersection = segments[i].intersection(segments[j])
                if intersection not in intersections:
                    intersections.append(segments[i].intersection(segments[j]))

    return intersections


class SweepLineIntersection:
    """Find the intersection points of a list of segments using the sweep line algorithm. The algorithm
    works by sweeping a horizontal line from top to bottom and checking for intersections at each event point.
    """

    def __init__(self, segments: list[Segment]):
        self.segments = segments
        self._event_queue = self._initialize_event_queue(segments)
        top_event_point = self._event_queue.maximum(self._event_queue.root).value.point

        self._status = Status([], Line(0, top_event_point.y + 1))
        self._intersections: list[Point] = []

        self._has_run = False

    @property
    def intersections(self) -> list[Point]:
        if not self._has_run:
            raise ValueError("The algorithm has not been run yet")
        return self._intersections

    def run(self) -> None:
        """Run the sweep line algorithm to find the intersection points of the segments."""
        while not self._event_queue.is_empty:
            event: EventPoint = self._event_queue.maximum(self._event_queue.root).value
            self._event_queue.delete(event)

            sweep_line = Line(0, event.point.y)

            # Get the segments that start at the event point
            upper_endpoint_segments: list[Segment] = []
            for segment in event.segments:
                start, _ = segment.order_by_y()
                if start == event.point:
                    upper_endpoint_segments.append(segment)

            # Get the segments already in the status that end at the event point or contain the event point
            contained_segments: list[Segment] = []
            lower_endpoint_segments: list[Segment] = []
            for segment in self._status:
                if segment.contains(event.point):
                    _, end = segment.order_by_y()
                    if end == event.point:
                        lower_endpoint_segments.append(segment)
                    else:
                        contained_segments.append(segment)

            all_segments = lists_union(
                lists_union(upper_endpoint_segments, lower_endpoint_segments),
                contained_segments,
            )
            if len(all_segments) > 1:
                self._intersections.append(event.point)

            self._status.remove(
                lists_union(contained_segments, lower_endpoint_segments)
            )
            self._status.add(
                lists_union(upper_endpoint_segments, contained_segments),
                Line.from_line_offset(sweep_line, -EPS),
            )

            segments_to_check = lists_union(upper_endpoint_segments, contained_segments)
            if len(segments_to_check) == 0:
                left_neighbor, right_neighbor = self._status.neighbours(event.point)
                self._find_new_event(
                    left_neighbor, right_neighbor, sweep_line, event.point
                )

            else:
                leftmost_segment: Optional[Segment] = None
                for segment in self._status:
                    if segment in segments_to_check:
                        leftmost_segment = segment
                        break
                if leftmost_segment is not None:
                    left_neighbor = (
                        self._status[self._status.index(leftmost_segment) - 1]
                        if self._status.index(leftmost_segment) - 1 >= 0
                        else None
                    )
                    self._find_new_event(
                        left_neighbor, leftmost_segment, sweep_line, event.point
                    )

                rightmost_segment: Optional[Segment] = None
                for i in range(len(self._status) - 1, -1, -1):
                    if self._status[i] in segments_to_check:
                        rightmost_segment = self._status[i]
                        break
                if rightmost_segment is not None:
                    right_neighbor = (
                        self._status[self._status.index(rightmost_segment) + 1]
                        if self._status.index(rightmost_segment) + 1 < len(self._status)
                        else None
                    )
                    self._find_new_event(
                        rightmost_segment, right_neighbor, sweep_line, event.point
                    )
        self._has_run = True

    def _initialize_event_queue(
        self, segments: list[Segment]
    ) -> RedBlackTree[EventPoint]:
        """Adds the start and end points of each segment as an event point to the event queue. If the event
        point already exist in the event queue, then it's deleted and a new intersection event point is added
        with all the segments

        Params:
        - segments - The segments to add to the event queue

        Returns:
        - The event queue with all the event points added"""
        event_queue = RedBlackTree[EventPoint]()
        for segment in segments:
            start, end = segment.order_by_y()

            start_event = EventPoint(EventType.START, start, [segment])
            existing_event = event_queue.search(start_event)
            if existing_event is not None:
                new_event = EventPoint(
                    EventType.INTERSECTION, start, existing_event.value.segments
                )
                new_event.add_segments(segment)

                event_queue.delete(existing_event.value)
                event_queue.insert(new_event)
            else:
                event_queue.insert(start_event)

            end_event = EventPoint(EventType.END, end, [segment])
            existing_event = event_queue.search(end_event)
            if existing_event is not None:
                new_event = EventPoint(
                    EventType.INTERSECTION, end, existing_event.value.segments
                )
                new_event.add_segments(segment)

                event_queue.delete(existing_event.value)
                event_queue.insert(new_event)
            else:
                event_queue.insert(end_event)

        return event_queue

    def _find_new_event(
        self,
        left_segment: Optional[Segment],
        right_segment: Optional[Segment],
        sweep_line: Line,
        event_point: Point,
    ) -> None:
        """Checks if the intersection between the two segments exists and if it's below the sweep line (thus we
        haven't considered it yet). If it is, then it's added to the event queue. If the intersection already exists
        in the event queue, then the segments are added to the event point."""
        if left_segment is None or right_segment is None:
            return None

        intersection: Optional[Point] = None
        if left_segment.intersect(right_segment):
            intersection_point = left_segment.intersection(right_segment)
            if intersection_point.y < sweep_line.q:
                intersection = intersection_point
            elif (
                intersection_point.y == sweep_line.q
                and intersection_point.x > event_point.x
            ):
                intersection = intersection_point

        if intersection is not None:
            existing_intersection = self._event_queue.search(
                EventPoint(EventType.INTERSECTION, intersection, [])
            )
            if existing_intersection is not None:
                new_event = EventPoint(
                    EventType.INTERSECTION,
                    intersection,
                    existing_intersection.value.segments,
                )
                new_event.add_segments([left_segment, right_segment])
                self._event_queue.delete(existing_intersection.value)
                self._event_queue.insert(new_event)
            else:
                self._event_queue.insert(
                    EventPoint(
                        EventType.INTERSECTION,
                        intersection,
                        [left_segment, right_segment],
                    )
                )
