import json
from src.structs import Segment, Point, Feature


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
    with open(path, mode="r") as f:
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
            p1 = Point(x1, y1)
            p2 = Point(x2, y2)
            segment = Segment(p1, p2)

            # Degenerate cases with duplicate and overlapping segments
            if p1 == p2 or segment in segments:
                continue

            segments.append(segment)

    return segments, num_intersections


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


def read_overlay_data(path: str) -> list[list[Segment]]:
    """Read the segments contained in a file. The file is expected to have the following format:
    <x11> <y11> <x12> <y12>

    ...

    <xN1> <yN1> <xN2> <yN2>

    <x11> <y11> <x12> <y12>

    ...

    <xM1> <yM1> <xM2> <yM2>

    Where the different faces are separated by an empty line, and each line represents a segment with its two endpoints.
    Params:
    -   path - The path to the file

    Returns:
        A tuple containing the list of segments divided by faces
    """
    segments: list[list[Segment]] = []
    face_segments: list[Segment] = []
    with open(path, mode="r") as f:
        for line in f.readlines():
            if line.strip() == "":
                segments.append(face_segments)
                face_segments = []
            else:
                x1, y1, x2, y2 = map(float, line.split())
                p1 = Point(x1, y1)
                p2 = Point(x2, y2)
                face_segments.append(Segment(p1, p2))
    segments.append(face_segments)
    return segments
