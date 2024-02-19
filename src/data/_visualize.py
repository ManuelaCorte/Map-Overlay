import matplotlib.pyplot as plt
from src.structs import Segment, Point


def plot_intersections(segments: list[Segment], intersections: list[Point]):
    """
    Plot the segments and their intersections

    Params:
    -  segments - The list of segments to plot"""
    f, ax = plt.subplots(figsize=(10, 10))
    for segment in segments:
        ax.plot(
            [segment.p1.x, segment.p2.x],
            [segment.p1.y, segment.p2.y],
            marker=".",
        )

    for intersection in intersections:
        ax.plot(intersection.x, intersection.y, "ro")

    f.tight_layout()
    plt.show()
