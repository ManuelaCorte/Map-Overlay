from typing import Optional
from src.structs import Segment, Point
from random import random
from src.intersection import naive_intersection


def read_intersection_data(path: str) -> tuple[list[Segment], int]:
    """Read the segments contained in a file. The file is expected to have the following format:
    <num_intersections>

    <x11> <y11> <x12> <y12>

    ...

    <xN1> <yN1> <xN2> <yN2>

    Where <num_intersections> is the number of intersections in the set of segments, and each line
    after that represents a segment with its two endpoints.

    Params:
    -   path - The path to the file

    Returns:
        A tuple containing the list of segments and the number of intersections
    """
    segments: list[Segment] = []
    num_intersections: int = 0
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if len(line.split()) == 1:
                if i == 0:
                    num_intersections = int(line)
                    continue
                else:
                    raise ValueError(
                        """Invalid file format. The first line should contain the number of intersections.
                        The following lines should contain the segments in the format <x1> <y1> <x2> <y2>"""
                    )

            if line.strip() == "":
                continue

            x1, y1, x2, y2 = map(float, line.split())
            segments.append(Segment(Point(x1, y1), Point(x2, y2)))

    return segments, num_intersections


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
