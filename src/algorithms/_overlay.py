from typing import Optional
from src.structs import (
    Point,
    Vertex,
    VertexId,
    Edge,
    EdgeId,
    Face,
    FaceId,
)
from src.data import Feature, GeometryType, PolygonGeometry
import graphviz


class DoublyConnectedEdgeList:
    def __init__(self, features: list[Feature]) -> None:
        self._faces: dict[FaceId, Face] = {}
        self._edges: dict[EdgeId, Edge] = {}
        self._vertices: dict[VertexId, Vertex] = {}
        self._points: dict[Point, VertexId] = {}

        self._construct_dcel(features)

    def to_image(self, path: str) -> None:
        dot = graphviz.Digraph(comment="Overlay DCEL")
        for vertex in self._vertices.values():
            dot.node(
                vertex.vertex.id,
                f"({vertex.coordinates.x}, {vertex.coordinates.y})",
                shape="point",
            )

        for edge in self._edges.values():
            dot.edge(
                edge.origin.id,
                edge.twin.id,
                label=edge.edge.id,
                dir="both",
                arrowhead="none",
            )

        dot.render(path, format="png")

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
            boundary.append(self._construct_edge(origin, destination, face_id))

        holes: list[EdgeId] = []
        for i, inner_ring in enumerate(feature.geometry.inner):
            hole_id = FaceId(id=f"f_{len(self._faces) +1 +i}")
            hole: list[EdgeId] = []
            for i in range(len(inner_ring)):
                origin = inner_ring[i]
                destination = inner_ring[(i + 1) % n]
                hole.append(self._construct_edge(origin, destination, hole_id, face_id))
            holes.append(hole[0])

        face = Face(face_id, boundary[0], holes)
        self._faces[face_id] = face

    def _construct_edge(
        self,
        origin: tuple[float, float],
        destination: tuple[float, float],
        incident_face: FaceId,
        outer_face: Optional[FaceId] = None,
    ) -> EdgeId:
        origin_point = Point(x=origin[0], y=origin[1])
        destination_point = Point(x=destination[0], y=destination[1])

        if self._points.get(origin_point) is not None:
            origin_vertex_id = self._points[origin_point]
        else:
            origin_vertex_id = VertexId(id=f"v_{len(self._points)}")
            self._points[origin_point] = origin_vertex_id

        if self._points.get(destination_point) is not None:
            destination_vertex_id = self._points[destination_point]
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
