import json

import matplotlib.pyplot as plt
import numpy as np

from src.structs import Point, Segment


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


def plot_overlay(overlay: list[list[tuple[Point, Point]]]):
    """
    Plot the segments and their intersections

    Params:
    -  segments - The list of segments to plot"""
    f, ax = plt.subplots(figsize=(10, 10))

    colors = plt.cm.viridis(np.linspace(0, 1, len(overlay)))  # type: ignore
    for face, color in zip(overlay, colors, strict=True):
        x: list[float] = []
        y: list[float] = []
        for p1, p2 in face:
            x.append(p1.x)
            y.append(p1.y)
            x.append(p2.x)
            y.append(p2.y)
            ax.plot(
                [p1.x, p2.x],
                [p1.y, p2.y],
                marker=".",
                color="black",
                linewidth=1,
            )
        # color the face
        ax.fill(x, y, color=color)
    f.tight_layout()
    plt.show()
