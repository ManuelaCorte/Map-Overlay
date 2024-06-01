from dataclasses import dataclass
from math import acos, pi
from typing import Optional, Self, TypeAlias

from src.structs import Point, Feature, GeometryType, PolygonGeometry
from src.utils import ClassComparisonError, DcelError
import graphviz


@dataclass(frozen=True)
class FaceId:
    id: str

    def __hash__(self) -> int:
        return hash(self.id)

    def is_null(self) -> bool:
        return self.id == "f_null"

    @classmethod
    def null(cls) -> Self:
        return cls(id="f_null")


@dataclass(frozen=True)
class VertexId:
    id: str

    def __hash__(self) -> int:
        return hash(self.id)

    def is_null(self) -> bool:
        return self.id == "v_null"

    @classmethod
    def null(cls) -> Self:
        return cls(id="v_null")


@dataclass(frozen=True)
class EdgeId:
    id: str

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq___(self, other: object) -> bool:
        if not isinstance(other, EdgeId):
            raise ClassComparisonError("Cannot compare EdgeId with non-EdgeId")
        return self.id == other.id

    def is_null(self) -> bool:
        return self.id == "e_null"

    @classmethod
    def from_vertices(cls, origin: VertexId, destination: VertexId) -> Self:
        return cls(id=f"e_{origin.id.split("_")[1]}_{destination.id.split("_")[1]}")

    @classmethod
    def null(cls) -> Self:
        return cls(id="e_null")


_Edge: TypeAlias = "Edge"


@dataclass(frozen=True)
class Face:
    """Representation of a face in the overlay of two planar subdivisions."""

    id: FaceId
    area: float
    is_external: bool
    outer_component: EdgeId
    inner_components: Optional[list[EdgeId]] = None

    def __hash__(self) -> int:
        return hash(self.id.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Face):
            raise ClassComparisonError("Cannot compare Face with non-Face")
        return self.id.id == other.id.id

    @property
    def is_null(self) -> bool:
        return self.id.is_null()

    @classmethod
    def null(cls) -> Self:
        return cls(
            id=FaceId.null(),
            area=0,
            is_external=False,
            outer_component=EdgeId.null(),
            inner_components=[],
        )


@dataclass(frozen=True)
class Edge:
    """Representation of an edge in the overlay of two planar subdivisions."""

    id: EdgeId
    origin: VertexId
    twin: EdgeId
    incident_face: FaceId
    next: EdgeId
    prev: EdgeId

    def __hash__(self) -> int:
        return hash(self.id.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            raise ClassComparisonError("Cannot compare Edge with non-Edge")
        return self.id.id == other.id.id

    @property
    def is_null(self) -> bool:
        return self.id.is_null()

    @classmethod
    def null(cls) -> Self:
        return cls(
            id=EdgeId.null(),
            origin=VertexId.null(),
            twin=EdgeId.null(),
            incident_face=FaceId.null(),
            next=EdgeId.null(),
            prev=EdgeId.null(),
        )


@dataclass(frozen=True)
class Vertex:
    """Representation of a vertex in the overlay of two planar subdivisions."""

    id: VertexId
    coordinates: Point
    incident_edges: list[EdgeId]

    @property
    def x(self) -> float:
        return self.coordinates.x

    @property
    def y(self) -> float:
        return self.coordinates.y

    @property
    def is_null(self) -> bool:
        return self.id.is_null()

    def __hash__(self) -> int:
        return hash(self.id.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vertex):
            raise ClassComparisonError("Cannot compare Vertex with non-Vertex")
        return self.id.id == other.id.id and self.coordinates == other.coordinates

    def add_incident_edge(self, edge: EdgeId) -> None:
        if edge not in self.incident_edges:
            self.incident_edges.append(edge)

    @classmethod
    def null(cls) -> Self:
        return cls(
            id=VertexId.null(),
            coordinates=Point(0, 0),
            incident_edges=[],
        )


class DoublyConnectedEdgeList:
    def __init__(
        self,
        points_list: list[Point],
        edge_list: list[tuple[Point, Point]],
    ) -> None:
        self._faces: dict[FaceId, Face] = {}
        self._edges: dict[EdgeId, Edge] = {}
        self._vertices: dict[VertexId, Vertex] = {}
        self._points: dict[Point, VertexId] = {}

        self._build_dcel(points_list, edge_list)
        print("DCEL created")

    # def __post_init__(self) -> None:
    #     self._features = self._check_correctness(self._features)

    #     self._build_dcel(self._features)

    @classmethod
    def from_features(cls, features: list[Feature]) -> Self:
        points: list[Point] = []
        edges: list[tuple[Point, Point]] = []
        for feature in features:
            if not isinstance(feature.geometry, PolygonGeometry):
                raise DcelError(
                    "The algorithm does not support geometries other than polygons"
                )
            if len(feature.geometry.inner) > 0:
                raise NotImplementedError(
                    "The algorithm does not support polygons with holes"
                )
            border = list(dict.fromkeys(feature.geometry.outer))

            for i in range(len(border)):
                origin = Point(*border[i])
                destination = Point(*border[(i + 1) % len(border)])
                points.append(origin)
                points.append(destination)
                edges.append((origin, destination))

        return cls(points, edges)

    def boundary(self, current_edge: EdgeId) -> list[EdgeId]:
        """Return the boundary of the face incident to the given edge."""
        boundary: list[EdgeId] = []
        boundary.append(current_edge)
        next_edge = self._edges[current_edge].next
        while next_edge != current_edge:
            boundary.append(next_edge)
            next_edge = self._edges[next_edge].next
        return boundary

    def to_image(self, path: str) -> None:
        dot = graphviz.Digraph(name="DCEL", format="png", engine="neato")
        dot.attr(overlap="false")
        for node in self._vertices.values():
            dot.node(
                node.id.id,
                label=node.id.id,
                pos=f"{node.coordinates.x},{node.coordinates.y}",
            )

        for edge in self._edges.values():
            origin = self._vertices[edge.origin].id.id
            destination = self._edges[edge.twin].origin.id
            dot.edge(origin, destination, label=edge.incident_face.id)

        dot.render(path, overwrite_source=True, cleanup=True)

    def _build_dcel(
        self, points: list[Point], edges: list[tuple[Point, Point]]
    ) -> None:
        # Add all points
        for point in points:
            vertex = VertexId(id=f"v_{len(self._points)}")
            if self._points.get(point) is None:
                self._points[point] = vertex
                self._vertices[vertex] = Vertex(vertex, point, [])

        # Add all edges and their twins
        for origin, destination in edges:
            origin_vertex = self._vertices[self._points[origin]]
            destination_vertex = self._vertices[self._points[destination]]

            edge_id = EdgeId.from_vertices(origin_vertex.id, destination_vertex.id)
            twin_id = EdgeId.from_vertices(destination_vertex.id, origin_vertex.id)
            edge = Edge(
                edge_id,
                origin_vertex.id,
                twin_id,
                FaceId.null(),
                EdgeId.null(),
                EdgeId.null(),
            )
            twin = self._edges.get(twin_id)
            if twin is None:
                twin = Edge(
                    twin_id,
                    destination_vertex.id,
                    edge_id,
                    FaceId.null(),
                    EdgeId.null(),
                    EdgeId.null(),
                )
            self._edges[edge_id] = edge
            self._edges[twin_id] = twin

            # fix vertex incident edges
            origin_vertex.add_incident_edge(edge_id)
            destination_vertex.add_incident_edge(twin_id)
            self._vertices[origin_vertex.id] = origin_vertex
            self._vertices[destination_vertex.id] = destination_vertex

        # Sort the incident edges of each vertex and connect prev and next pointer
        for vertex_id in self._vertices.keys():
            self._sort_incident_edges(vertex_id)

            incident_edges = self._vertices[vertex_id].incident_edges
            n = len(incident_edges)
            if n < 2:
                raise DcelError("Vertex has less than 2 incident half edges")

            for i in range(n):
                e1 = self._edges[incident_edges[i]]
                e2 = self._edges[incident_edges[(i + 1) % n]]
                # e1.twin.next = e2.id
                twin = self._edges[e1.twin]
                self._edges[twin.id] = Edge(
                    id=twin.id,
                    origin=twin.origin,
                    twin=twin.twin,
                    incident_face=twin.incident_face,
                    next=e2.id,
                    prev=twin.prev,
                )
                # e2.prev = e1.twin
                self._edges[e2.id] = Edge(
                    id=e2.id,
                    origin=e2.origin,
                    twin=e2.twin,
                    incident_face=e2.incident_face,
                    next=e2.next,
                    prev=e1.twin,
                )

        # Assign face to each cycle
        # for feature in features:
        #     assert isinstance(feature.geometry, PolygonGeometry)

        #     origin_vertex = self._points[Point(*feature.geometry.outer[0])]
        #     destination_vertex = self._points[Point(*feature.geometry.outer[1])]
        #     incident_edge = EdgeId.from_vertices(origin_vertex, destination_vertex)

        #     face_id = FaceId(f"f_{len(self._faces)}")
        #     self._faces[face_id] = Face(face_id, self._compute_area(feature.geometry.outer), incident_edge, None)

        #     for i in range(len(feature.geometry.outer)):
        #         origin_vertex = self._points[Point(*feature.geometry.outer[i])]
        #         destination_vertex = self._points[Point(*feature.geometry.outer[(i + 1) % len(feature.geometry.outer)])]
        #         incident_edge = self._edges[EdgeId.from_vertices(origin_vertex, destination_vertex)]
        #         self._edges[incident_edge.id] = Edge(
        #             id=incident_edge.id,
        #             origin=incident_edge.origin,
        #             twin=incident_edge.twin,
        #             incident_face=face_id,
        #             next=incident_edge.next,
        #             prev=incident_edge.prev
        #         )

        # self._faces[FaceId.null()] = Face(FaceId.null(), 0, EdgeId.null())

        for edge_id, edge in self._edges.items():
            if edge.incident_face.is_null():
                boundary = self.boundary(edge_id)
                area = self._compute_area(boundary)
                face_id = FaceId(f"f_{len(self._faces)}")
                self._faces[face_id] = Face(face_id, area, area < 0, edge_id, [])

                self._edges[edge_id] = Edge(
                    id=edge.id,
                    origin=edge.origin,
                    twin=edge.twin,
                    incident_face=face_id,
                    next=edge.next,
                    prev=edge.prev,
                )

                for e in boundary:
                    edge = self._edges[e]
                    self._edges[e] = Edge(
                        id=edge.id,
                        origin=edge.origin,
                        twin=edge.twin,
                        incident_face=face_id,
                        next=edge.next,
                        prev=edge.prev,
                    )

    def _compute_area(self, boundary: list[EdgeId]) -> float:
        area = 0
        for i in range(len(boundary)):
            edge = self._edges[boundary[i]]
            origin = self._vertices[edge.origin].coordinates
            destination = self._vertices[self._edges[edge.twin].origin].coordinates
            area += origin.x * destination.y - origin.y * destination.x
        return area / 2

    def _check_correctness(self, features: list[Feature]) -> list[Feature]:
        for feature in features:
            match feature.geometry.type:
                case GeometryType.POLYGON:
                    # remove duplicate points
                    assert isinstance(feature.geometry, PolygonGeometry)
                    feature.geometry.outer = self._remove_duplicate_points_from_ring(
                        feature.geometry.outer
                    )
                    feature.geometry.inner = [
                        self._remove_duplicate_points_from_ring(inner)
                        for inner in feature.geometry.inner
                    ]

                    # check if traversal is counterclockwise
                    # area = self._compute_area(feature.geometry.outer)
                    # if area > 0:
                    #     feature.geometry.outer = feature.geometry.outer[::-1]
                    #     feature.geometry.inner = [inner[::-1] for inner in feature.geometry.inner]
                case _:
                    raise DcelError(
                        "The algorithm does not support geometries other than polygons"
                    )

        return features

    def _remove_duplicate_points_from_ring(
        self, ring: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        return list(dict.fromkeys(ring))

    def _sort_incident_edges(self, vertex_id: VertexId) -> None:
        """Sort the incident edges of the vertex by angle in clockwise order."""
        vertex = self._vertices[vertex_id]
        edges = [self._edges[edge_id] for edge_id in vertex.incident_edges]

        angles: dict[EdgeId, float] = {}
        for edge in edges:
            origin = self._vertices[edge.origin].coordinates
            destination = self._vertices[self._edges[edge.twin].origin].coordinates
            dx = destination.x - origin.x
            dy = destination.y - origin.y

            length = (dx**2 + dy**2) ** 0.5
            if dy > 0:
                angle = acos(dx / length)
            else:
                angle = 2 * pi - acos(dx / length)
            angles[edge.id] = angle

        # edges sorted in clockwise order
        sorted_edges = sorted(angles.keys(), key=lambda edge_id: angles[edge_id])
        self._vertices[vertex_id] = Vertex(
            id=vertex.id,
            coordinates=vertex.coordinates,
            incident_edges=sorted_edges,
        )
