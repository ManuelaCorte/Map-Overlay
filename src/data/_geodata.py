from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from typing import Any, Self
from enum import Enum
import matplotlib.pyplot as plt


class GeometryType(Enum):
    """Enum to represent the type of geometry in a geoJSON file."""

    POINT = "Point"
    LINESTRING = "LineString"
    POLYGON = "Polygon"


@dataclass
class Geometry(ABC):
    """Representation of a geometry in geoJSON."""

    type: GeometryType

    @classmethod
    @abstractmethod
    def from_json(cls, data: dict[str, Any]) -> Self: ...


@dataclass
class PointGeometry(Geometry):
    """Representation of a point geometry in geoJSON."""

    type: GeometryType = GeometryType.POINT
    coordinates: tuple[float, float] = field(default_factory=tuple)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(coordinates=(data["coordinates"][0], data["coordinates"][1]))


@dataclass
class LineStringGeometry(Geometry):
    """Representation of a line string geometry in geoJSON."""

    type: GeometryType = GeometryType.LINESTRING
    coordinates: list[tuple[float, float]] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(coordinates=[(x, y) for x, y in data["coordinates"]])


@dataclass
class PolygonGeometry(Geometry):
    """Representation of a polygon geometry in geoJSON."""

    type: GeometryType = GeometryType.POLYGON
    outer: list[tuple[float, float]] = field(default_factory=list)
    inner: list[list[tuple[float, float]]] = field(default_factory=list)

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        # We ignore the last point as it is the same as the first
        return cls(
            outer=[(x, y) for x, y in data["coordinates"][0][:-1]],
            inner=[[(x, y) for x, y in ring] for ring in data["coordinates"][1:][:-1]],
        )


@dataclass
class Feature:
    """Representation of a  set of features in geoJSON."""

    geometry: Geometry
    properties: dict[str, str]

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        type = GeometryType(data["geometry"]["type"])

        match type:
            case GeometryType.POINT:
                geometry = PointGeometry.from_json(data["geometry"])
            case GeometryType.LINESTRING:
                geometry = LineStringGeometry.from_json(data["geometry"])
            case GeometryType.POLYGON:
                geometry = PolygonGeometry.from_json(data["geometry"])

        return cls(geometry=geometry, properties=data["properties"])


def read_geojson_file(path: str) -> list[Feature]:
    """Read the features contained in a geojson file. The file is expected to have the following format:
    {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [x11, y11],
                            [x12, y12],
                            ...
                        ]
                    ]
                },
                "properties": {}
            },
            ...
        ]
    }

    Params:
    -   path - The path to the file

    Returns:
        A list of Features objects
    """

    data: list[Feature] = []
    with open(path, "r") as f:
        for feature in json.load(f)["features"]:
            data.append(Feature.from_json(feature))
    return data


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
