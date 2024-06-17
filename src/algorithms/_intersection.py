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
from src.utils import lists_union, CollinearityError


def naive_intersection(segments: list[Segment]) -> list[Point]:
    """Find the intersection points of a list of segments using the naive algorithm. This algorithm
    has a time complexity of O(n^2) where n is the number of segments."""
    intersections: list[Point] = []
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            intersection = segments[i].intersection(segments[j])
            if intersection is not None and intersection not in intersections:
                intersections.append(intersection)

    return intersections


def sweep_line_intersection(segments: list[Segment]) -> dict[Point, list[Segment]]:
    event_queue = _initialize_event_queue(segments)
    top_event_point = event_queue.maximum(event_queue.root).value.point

    status = Status([], Line(0, top_event_point.y + 1))
    intersections: dict[Point, list[Segment]] = {}

    while not event_queue.is_empty:
        event: EventPoint = event_queue.maximum(event_queue.root).value
        event_queue.delete(event)

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
        for segment in status:
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

        for i in range(len(all_segments)):
            for j in range(i + 1, len(all_segments)):
                if all_segments[i].is_collinear(all_segments[j]):
                    shared_endpoint = all_segments[i].shared_endpoint(all_segments[j])
                    if shared_endpoint is None:
                        raise CollinearityError(
                            f"""The algorithm does not support collinear segments.
                            Segment {all_segments[i]} and {all_segments[j]} are collinear."""
                        )
        if len(all_segments) > 1:
            intersections[event.point] = all_segments

        status.remove(lists_union(contained_segments, lower_endpoint_segments))
        status.add(
            lists_union(upper_endpoint_segments, contained_segments),
            Line.from_line_offset(sweep_line, -EPS),
        )

        segments_to_check = lists_union(upper_endpoint_segments, contained_segments)
        if len(segments_to_check) == 0:
            left_neighbor, right_neighbor = status.neighbours(event.point)
            new_event, existing_intersection = _find_new_event(
                event_queue, left_neighbor, right_neighbor, sweep_line, event.point
            )
            if existing_intersection is not None:
                event_queue.delete(existing_intersection)
            if new_event is not None:
                event_queue.insert(new_event)

        else:
            leftmost_segment: Optional[Segment] = None
            for segment in status:
                if segment in segments_to_check:
                    leftmost_segment = segment
                    break
            if leftmost_segment is not None:
                left_neighbor = (
                    status[status.index(leftmost_segment) - 1]
                    if status.index(leftmost_segment) - 1 >= 0
                    else None
                )
                new_event, existing_intersection = _find_new_event(
                    event_queue,
                    left_neighbor,
                    leftmost_segment,
                    sweep_line,
                    event.point,
                )
                if existing_intersection is not None:
                    event_queue.delete(existing_intersection)
                if new_event is not None:
                    event_queue.insert(new_event)

            rightmost_segment: Optional[Segment] = None
            for i in range(len(status) - 1, -1, -1):
                if status[i] in segments_to_check:
                    rightmost_segment = status[i]
                    break
            if rightmost_segment is not None:
                right_neighbor = (
                    status[status.index(rightmost_segment) + 1]
                    if status.index(rightmost_segment) + 1 < len(status)
                    else None
                )
                new_event, existing_intersection = _find_new_event(
                    event_queue,
                    rightmost_segment,
                    right_neighbor,
                    sweep_line,
                    event.point,
                )
                if existing_intersection is not None:
                    event_queue.delete(existing_intersection)
                if new_event is not None:
                    event_queue.insert(new_event)

    return intersections


def _initialize_event_queue(segments: list[Segment]) -> RedBlackTree[EventPoint]:
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
    event_queue: RedBlackTree[EventPoint],
    left_segment: Optional[Segment],
    right_segment: Optional[Segment],
    sweep_line: Line,
    event_point: Point,
) -> tuple[Optional[EventPoint], Optional[EventPoint]]:
    """Checks if the intersection between the two segments exists and if it's below the sweep line (thus we
    haven't considered it yet). If it is, then it's added to the event queue. If the intersection already exists
    in the event queue, then the segments are added to the event point."""
    if left_segment is None or right_segment is None:
        return None, None

    intersection: Optional[Point] = None
    intersection_point = left_segment.intersection(right_segment)
    if intersection_point is None:
        return None, None

    if intersection_point.y < sweep_line.q:
        intersection = intersection_point
    elif (
        abs(intersection_point.y - sweep_line.q) < EPS
        and intersection_point.x > event_point.x
    ):
        intersection = intersection_point

    new_event = None
    existing_intersection = None
    if intersection is not None:
        existing_intersection = event_queue.search(
            EventPoint(EventType.INTERSECTION, intersection, [])
        )
        if existing_intersection is not None:
            new_event = EventPoint(
                EventType.INTERSECTION,
                intersection,
                existing_intersection.value.segments,
            )
            new_event.add_segments([left_segment, right_segment])
            # self._event_queue.delete(existing_intersection.value)
            # self._event_queue.insert(new_event)
        else:
            new_event = EventPoint(
                EventType.INTERSECTION,
                intersection,
                [left_segment, right_segment],
            )
            # self._event_queue.insert(
            #     EventPoint(
            #         EventType.INTERSECTION,
            #         intersection,
            #         [left_segment, right_segment],
            #     )
            # )
    return new_event, (
        existing_intersection.value if existing_intersection is not None else None
    )
