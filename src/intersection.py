from src.structs import Segment, Point


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
    raise NotImplementedError("sweep_line_intersection not implemented yet")
