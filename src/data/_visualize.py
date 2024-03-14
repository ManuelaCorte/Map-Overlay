import json
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


def plot_geojson(path: str) -> None:
    _, ax = plt.subplots(figsize=(15, 10))

    with open(path, "r") as f:
        data = json.load(f)
        for feature in data["features"]:
            type = feature["geometry"]["type"]
            if type == "Polygon":
                for polygon in feature["geometry"]["coordinates"]:
                    x, y = zip(*polygon)
                    ax.plot(x, y)
            elif type == "LineString":
                x, y = zip(*feature["geometry"]["coordinates"])
                ax.plot(x, y)
            elif type == "Point":
                x, y = feature["geometry"]["coordinates"]
                ax.plot(x, y, "o")

    plt.show()
