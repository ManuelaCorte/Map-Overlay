from random import random
from typing import Optional

from src.algorithms import naive_intersection
from src.structs import Point, Segment


def generate_random_data(
    num_segments: int, max_x: float, max_y: float, path: Optional[str] = None
) -> tuple[list[Segment], int]:
    """Generate random segments fbetween 0 and the max coordinates sepcified for testing purposes.

    Params:
    -   num_segments - The number of segments to generate
    -   max_x - The maximum x coordinate for the segments
    -   max_y - The maximum y coordinate for the segments
    -   path - If specified, the path to save the generated segments and intersections

    Returns:
        A tuple containing the list of segments and the number of intersections
    """
    segments: list[Segment] = []
    for _ in range(num_segments):
        x1, y1 = random() * max_x, random() * max_y
        x2, y2 = random() * max_x, random() * max_y
        segments.append(Segment(Point(x1, y1), Point(x2, y2)))

    num_intersections = len(naive_intersection(segments))

    if path:
        with open(path, "w") as f:
            f.write(f"{num_intersections}\n")
            for segment in segments:
                f.write(
                    f"{segment.p1.x} {segment.p1.y} {segment.p2.x} {segment.p2.y}\n"
                )
    return segments, num_intersections
