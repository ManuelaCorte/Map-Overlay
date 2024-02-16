from typing import Optional
from src.structs import Segment, Point
from random import random
from src.intersection import naive_intersection


def read_intersection_data(path: str) -> tuple[list[Segment], Optional[int]]:
    segments: list[Segment] = []
    num_intersections: Optional[int] = None
    with open(path, "r") as f:
        for line in f:
            if len(line.split()) == 1:
                num_intersections = int(line)
                continue

            if line.strip() == "":
                continue

            x1, y1, x2, y2 = map(float, line.split())
            segments.append(Segment(Point(x1, y1), Point(x2, y2)))

    return segments, num_intersections


def generate_random_data(
    num_segments: int, max_x: float, max_y: float
) -> tuple[list[Segment], int]:
    segments: list[Segment] = []
    for _ in range(num_segments):
        x1, y1 = random() * max_x, random() * max_y
        x2, y2 = random() * max_x, random() * max_y
        segments.append(Segment(Point(x1, y1), Point(x2, y2)))

    num_intersections = len(naive_intersection(segments))
    return segments, num_intersections
