from typing import Optional

from src.structs import (
    EPS,
    EventPoint,
    EventType,
    Line,
    Point,
    RedBlackTree,
    Segment,
    Status,
)
from src.utils import lists_union


def naive_intersection(segments: list[Segment]) -> list[Point]:
    """Find the intersection points of a list of segments using the naive algorithm. This algorithm
    has a time complexity of O(n^2) where n is the number of segments."""
    intersections: list[Point] = []
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if segments[i].is_colinear(segments[j]) and segments[i]:
                colinear_intersections = segments[i].colinear_intersection(segments[j])
                for intersection in colinear_intersections:
                    if intersection not in intersections:
                        intersections.append(intersection)
                continue

            intersection = segments[i].intersection(segments[j])
            if intersection is not None and intersection not in intersections:
                intersections.append(intersection)

    return intersections


def sweep_line_intersection(
    segments: list[Segment],
) -> tuple[dict[Point, list[Segment]], dict[Segment, list[Point]]]:
    event_queue = _initialize_event_queue(segments)
    top_event_point = event_queue.maximum(event_queue.root).value.point

    status = Status([], Line(0, top_event_point.y + 1))
    intersections: dict[Point, list[Segment]] = {}
    splitted_segments: dict[Segment, list[Point]] = {}

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
        if len(all_segments) > 1:
            intersections[event.point] = all_segments
            for segment in all_segments:
                if segment not in splitted_segments:
                    splitted_segments[segment] = []
                (
                    splitted_segments[segment].append(event.point)
                    if event.point not in splitted_segments[segment]
                    else None
                )

            # Hack: manually handle colinear intersections for horizontal segments
            for i in range(len(all_segments)):
                for j in range(i + 1, len(all_segments)):
                    if (
                        all_segments[i].is_colinear(all_segments[j])
                        and all_segments[i].is_horizontal
                        and all_segments[j].is_horizontal
                    ):
                        s1, s2 = (
                            (all_segments[i], all_segments[j])
                            if all_segments[i].p1.x < all_segments[j].p1.x
                            else (all_segments[j], all_segments[i])
                        )
                        s1 = Segment(*s1.order_by_x())
                        s2 = Segment(*s2.order_by_x())
                        i1, i2 = s1.colinear_intersection(s2)
                        splitted_segments[s1] = [s1.p1, i1, s1.p2]
                        splitted_segments[s2] = [s2.p1, i2, s2.p2]
                        if intersections.get(i1) is None:
                            intersections[i1] = [s1, s2]
                        else:
                            (
                                intersections[i1].append(s1)
                                if s1 not in intersections[i1]
                                else None
                            )
                            (
                                intersections[i1].append(s2)
                                if s2 not in intersections[i1]
                                else None
                            )
                        if intersections.get(i2) is None:
                            intersections[i2] = [s1, s2]
                        else:
                            (
                                intersections[i2].append(s1)
                                if s1 not in intersections[i2]
                                else None
                            )
                            (
                                intersections[i2].append(s2)
                                if s2 not in intersections[i2]
                                else None
                            )

        status.remove(lists_union(contained_segments, lower_endpoint_segments))
        status.add(
            lists_union(upper_endpoint_segments, contained_segments),
            Line.from_line_offset(sweep_line, -EPS),
        )

        segments_to_check = lists_union(upper_endpoint_segments, contained_segments)
        if len(segments_to_check) == 0:
            left_neighbor, right_neighbor = status.neighbours(event.point)
            _find_new_event(
                event_queue, left_neighbor, right_neighbor, sweep_line, event.point
            )

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
                _find_new_event(
                    event_queue,
                    left_neighbor,
                    leftmost_segment,
                    sweep_line,
                    event.point,
                )

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
                _find_new_event(
                    event_queue,
                    rightmost_segment,
                    right_neighbor,
                    sweep_line,
                    event.point,
                )

    return intersections, splitted_segments


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
) -> None:
    """Checks if the intersection between the two segments exists and if it's below the sweep line (thus we
    haven't considered it yet). If it is, then it's added to the event queue. If the intersection already exists
    in the event queue, then the segments are added to the event point."""
    if left_segment is None or right_segment is None:
        return

    intersection: Optional[Point] = None
    intersection_point = left_segment.intersection(right_segment)
    if intersection_point is None:
        return

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
            event_queue.delete(existing_intersection.value)
            event_queue.insert(new_event)
        else:
            new_event = EventPoint(
                EventType.INTERSECTION,
                intersection,
                [left_segment, right_segment],
            )
            event_queue.insert(new_event)
