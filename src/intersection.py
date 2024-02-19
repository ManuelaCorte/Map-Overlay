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
    intersections: list[Point] = []
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if segments[i].intersect(segments[j]):
                intersection = segments[i].intersection(segments[j])
                if intersection not in intersections:
                    intersections.append(segments[i].intersection(segments[j]))

    return intersections


def sweep_line_intersection(segments: list[Segment]) -> list[Point]:
    event_queue = _initialize(segments)

    top_event_point = event_queue.maximum(event_queue.root).value.point
    sweep_line = Line(0, top_event_point.y + 1)
    status = Status([], sweep_line)
    intersections: list[Point] = []
    # event_queue.print_tree()
    while not event_queue.is_empty:
        event: EventPoint = event_queue.maximum(event_queue.root).value
        event_queue.delete(event)

        sweep_line = Line(0, event.point.y)

        upper: list[Segment] = []
        for segment in event.segments:
            start, _ = segment.order_by_y()
            if start == event.point:
                upper.append(segment)

        contains: list[Segment] = []
        lower: list[Segment] = []
        for segment in status:
            if segment.contains(event.point):
                _, end = segment.order_by_y()
                if end == event.point:
                    lower.append(segment)
                else:
                    contains.append(segment)

        union = lists_union(lists_union(upper, lower), contains)
        if len(union) > 1:
            intersections.append(event.point)

        status.remove(lists_union(contains, lower))
        status.add(
            lists_union(upper, contains), Line.from_line_offset(sweep_line, -10 * EPS)
        )

        to_check = lists_union(upper, contains)
        if len(to_check) == 0:
            left_neighbor, right_neighbor = status.neighbours(event.point)
            intersection = _find_new_event(
                left_neighbor, right_neighbor, sweep_line, event.point
            )
            if (
                intersection is not None
                and left_neighbor is not None
                and right_neighbor is not None
            ):
                existing_intersection = event_queue.search(
                    EventPoint(EventType.INTERSECTION, intersection, [])
                )
                if existing_intersection is not None:
                    new_event = EventPoint(
                        EventType.INTERSECTION,
                        intersection,
                        existing_intersection.value.segments,
                    )
                    new_event.add_segments([left_neighbor, right_neighbor])
                    event_queue.delete(existing_intersection.value)
                    event_queue.insert(new_event)
                else:
                    event_queue.insert(
                        EventPoint(
                            EventType.INTERSECTION,
                            intersection,
                            [left_neighbor, right_neighbor],
                        )
                    )
        else:
            leftmost_segment: Optional[Segment] = None
            for segment in status:
                if segment in to_check:
                    leftmost_segment = segment
                    break
            if leftmost_segment is not None:
                left_neighbor = (
                    status[status.index(leftmost_segment) - 1]
                    if status.index(leftmost_segment) - 1 >= 0
                    else None
                )
                intersection = _find_new_event(
                    left_neighbor, leftmost_segment, sweep_line, event.point
                )
                if intersection is not None and left_neighbor is not None:
                    existing_intersection = event_queue.search(
                        EventPoint(EventType.INTERSECTION, intersection, [])
                    )
                    if existing_intersection is not None:
                        new_event = EventPoint(
                            EventType.INTERSECTION,
                            intersection,
                            existing_intersection.value.segments,
                        )
                        new_event.add_segments([left_neighbor, leftmost_segment])
                        event_queue.delete(existing_intersection.value)
                        event_queue.insert(new_event)
                    else:
                        event_queue.insert(
                            EventPoint(
                                EventType.INTERSECTION,
                                intersection,
                                [left_neighbor, leftmost_segment],
                            )
                        )

            rightmost_segment: Optional[Segment] = None
            for i in range(len(status) - 1, -1, -1):
                if status[i] in to_check:
                    rightmost_segment = status[i]
                    break
            if rightmost_segment is not None:
                right_neighbor = (
                    status[status.index(rightmost_segment) + 1]
                    if status.index(rightmost_segment) + 1 < len(status)
                    else None
                )
                intersection = _find_new_event(
                    rightmost_segment, right_neighbor, sweep_line, event.point
                )
                if intersection is not None and right_neighbor is not None:
                    existing_intersection = event_queue.search(
                        EventPoint(EventType.INTERSECTION, intersection, [])
                    )
                    if existing_intersection is not None:
                        new_event = EventPoint(
                            EventType.INTERSECTION,
                            intersection,
                            existing_intersection.value.segments,
                        )
                        new_event.add_segments([rightmost_segment, right_neighbor])

                        event_queue.delete(existing_intersection.value)
                        event_queue.insert(new_event)
                    else:
                        event_queue.insert(
                            EventPoint(
                                EventType.INTERSECTION,
                                intersection,
                                [rightmost_segment, right_neighbor],
                            )
                        )

    return intersections


def _initialize(segments: list[Segment]) -> RedBlackTree[EventPoint]:
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
    left_segment: Optional[Segment],
    right_segment: Optional[Segment],
    sweep_line: Line,
    event_point: Point,
) -> Optional[Point]:
    if left_segment is None or right_segment is None:
        return None

    if left_segment.intersect(right_segment):
        intersection = left_segment.intersection(right_segment)
        if intersection.y < sweep_line.q:
            return intersection
        elif intersection.y == sweep_line.q and intersection.x > event_point.x:
            return intersection

    return None
