from dataclasses import dataclass
from typing import Optional, Self
from src.structs import Point, Feature, GeometryType, PolygonGeometry
from src.utils import ClassComparisonError
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

    @classmethod
    def from_vertices(cls, origin: VertexId, destination: VertexId) -> Self:
        return cls(id=f"e_{origin.id.split("_")[1]}_{destination.id.split("_")[1]}")

    def is_null(self) -> bool:
        return self.id == "e_null"

    @classmethod
    def null(cls) -> Self:
        return cls(id="e_null")


@dataclass(frozen=True)
class Face:
    """Representation of a face in the overlay of two planar subdivisions."""

    face: FaceId
    outer_component: Optional[EdgeId] = None
    inner_components: Optional[list[EdgeId]] = None

    def __hash__(self) -> int:
        return hash(self.face.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Face):
            raise ClassComparisonError("Cannot compare Face with non-Face")
        return self.face.id == other.face.id

    def is_null(self) -> bool:
        return self.face.is_null()


@dataclass(frozen=True)
class Vertex:
    """Representation of a vertex in the overlay of two planar subdivisions."""

    vertex: VertexId
    coordinates: Point
    incident_edge: EdgeId

    @property
    def x(self) -> float:
        return self.coordinates.x

    @property
    def y(self) -> float:
        return self.coordinates.y

    def __hash__(self) -> int:
        return hash(self.vertex.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vertex):
            raise ClassComparisonError("Cannot compare Vertex with non-Vertex")
        return (
            self.vertex.id == other.vertex.id and self.coordinates == other.coordinates
        )


@dataclass
class Edge:
    """Representation of an edge in the overlay of two planar subdivisions."""

    edge: EdgeId
    origin: VertexId
    twin: EdgeId
    incident_face: FaceId
    next: EdgeId
    prev: EdgeId

    def __hash__(self) -> int:
        return hash(self.edge.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            raise ClassComparisonError("Cannot compare Edge with non-Edge")
        return self.edge.id == other.edge.id

    def is_null(self) -> bool:
        return self.edge.is_null()


class DoublyConnectedEdgeList:
    def __init__(self, features: list[Feature]) -> None:
        self._faces: dict[FaceId, Face] = {}
        self._edges: dict[EdgeId, Edge] = {}
        self._vertices: dict[VertexId, Vertex] = {}
        self._points: dict[Point, VertexId] = {}

        self._construct_dcel(features)

    def to_image(self, path: str) -> None:
        dot = graphviz.Digraph(name="DCEL", format="png", engine="neato")
        dot.attr(overlap="false")
        for node in self._vertices.values():
            dot.node(
                node.vertex.id,
                label=node.vertex.id,
                pos=f"{node.coordinates.x},{node.coordinates.y}",
            )

        for edge in self._edges.values():
            origin = self._vertices[edge.origin].vertex.id
            destination = self._edges[edge.twin].origin.id
            dot.edge(origin, destination)

        dot.render(path, overwrite_source=True, cleanup=True)

    def _construct_dcel(self, features: list[Feature]) -> None:
        for feature in features:
            match feature.geometry.type:
                case GeometryType.POLYGON:
                    self._construct_face(feature)
                case GeometryType.LINESTRING:
                    raise NotImplementedError(
                        "The algorithm does not support line strings"
                    )
                case GeometryType.POINT:
                    raise NotImplementedError("The algorithm does not support points")

    def _construct_face(self, feature: Feature) -> None:
        assert isinstance(feature.geometry, PolygonGeometry)
        face_id = FaceId(id=f"f_{len(self._faces)}")

        n = len(feature.geometry.outer)
        boundary: list[EdgeId] = []
        for i in range(n):
            origin = feature.geometry.outer[i]
            destination = feature.geometry.outer[(i + 1) % n]
            origin_point = Point(x=origin[0], y=origin[1])
            destination_point = Point(x=destination[0], y=destination[1])
            boundary.append(
                self._construct_edge(origin_point, destination_point, face_id)
            )

        # Set the next and previous pointers for the boundary edges
        for i in range(n):
            self._connect_edges(boundary[i], boundary[(i + 1) % n])

        holes: list[EdgeId] = []
        for i, inner_ring in enumerate(feature.geometry.inner):
            hole_id = FaceId(id=f"f_{len(self._faces) +1 +i}")
            hole: list[EdgeId] = []
            m = len(inner_ring)
            for i in range(m):
                origin = inner_ring[i]
                destination = inner_ring[(i + 1) % m]
                origin_point = Point(x=origin[0], y=origin[1])
                destination_point = Point(x=destination[0], y=destination[1])
                hole.append(
                    self._construct_edge(
                        origin_point, destination_point, hole_id, face_id
                    )
                )
            holes.append(hole[0])

            for i in range(m):
                self._connect_edges(hole[i], hole[(i + 1) % m])

        face = Face(face_id, boundary[0], holes)
        self._faces[face_id] = face

    def _construct_edge(
        self,
        origin_point: Point,
        destination_point: Point,
        incident_face: FaceId,
        outer_face: Optional[FaceId] = None,
    ) -> EdgeId:
        origin_vertex_id = VertexId.null()
        destination_vertex_id = VertexId.null()

        origin_vertex = self._points.get(origin_point)
        if origin_vertex is not None:
            origin_vertex_id = origin_vertex
        else:
            origin_vertex_id = VertexId(id=f"v_{len(self._points)}")
            self._points[origin_point] = origin_vertex_id

        destination_vertices = self._points.get(destination_point)
        if destination_vertices is not None:
            destination_vertex_id = destination_vertices
        else:
            destination_vertex_id = VertexId(id=f"v_{len(self._points)}")
            self._points[destination_point] = destination_vertex_id

        incident_edge_id = EdgeId.from_vertices(origin_vertex_id, destination_vertex_id)
        twin_edge_id = EdgeId.from_vertices(destination_vertex_id, origin_vertex_id)
        self._vertices[origin_vertex_id] = Vertex(
            vertex=origin_vertex_id,
            coordinates=origin_point,
            incident_edge=incident_edge_id,
        )
        self._vertices[destination_vertex_id] = Vertex(
            vertex=destination_vertex_id,
            coordinates=destination_point,
            incident_edge=twin_edge_id,
        )

        existing_edge = self._edges.get(incident_edge_id)
        if existing_edge is None:
            edge = Edge(
                incident_edge_id,
                origin_vertex_id,
                twin_edge_id,
                incident_face,
                EdgeId.null(),
                EdgeId.null(),
            )
            self._edges[incident_edge_id] = edge
        elif existing_edge.incident_face.is_null():
            existing_edge.incident_face = incident_face
            self._edges[existing_edge.edge] = existing_edge

        if self._edges.get(twin_edge_id) is None:
            twin_edge = Edge(
                twin_edge_id,
                destination_vertex_id,
                incident_edge_id,
                FaceId.null() if outer_face is None else outer_face,
                EdgeId.null(),
                EdgeId.null(),
            )
            self._edges[twin_edge_id] = twin_edge

        return incident_edge_id

    def _connect_edges(self, edge1: EdgeId, edge2: EdgeId) -> None:
        self._edges[edge1].next = edge2
        self._edges[edge2].prev = edge1

