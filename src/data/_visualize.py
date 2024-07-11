import json
import os
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from src.structs import Point, Segment


def plot_intersections(
    segments: list[Segment],
    intersections: list[Point],
    file_path: Optional[str] = None,
):
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
    if file_path:
        output_folder = "/".join(file_path.split("/")[:-1])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        f.savefig(file_path)
    plt.show()


def plot_geojson(input: str) -> None:
    _, ax = plt.subplots(figsize=(15, 10))

    with open(input, "r") as f:
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


def plot_overlay(
    overlay: list[list[tuple[Point, Point]]], file_path: Optional[str] = None
):
    """
    Plot the segments and their intersections

    Params:
    -  segments - The list of segments to plot"""
    f, ax = plt.subplots(figsize=(10, 10))

    linspace = np.linspace(0, 1, len(overlay))
    np.random.shuffle(linspace)
    colors = plt.cm.tab20b_r(linspace)  # type: ignore
    for face, color in zip(overlay, colors, strict=True):  # type: ignore
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
    if file_path:
        output_folder = "/".join(file_path.split("/")[:-1])
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        f.savefig(file_path)
    plt.show()


def plot_dcels(
    s1: list[list[tuple[Point, Point]]],
    s2: Optional[list[list[tuple[Point, Point]]]] = None,
):
    f, ax = plt.subplots(figsize=(10, 10))
    for face in s1:
        for p1, p2 in face:
            ax.plot(
                [p1.x, p2.x],
                [p1.y, p2.y],
                marker=".",
                color="blue",
                linewidth=3,
            )

    if s2 is not None:
        for face in s2:
            for p1, p2 in face:
                ax.plot(
                    [p1.x, p2.x],
                    [p1.y, p2.y],
                    marker=".",
                    color="red",
                    linewidth=3,
                )

    f.tight_layout()
    plt.show()
