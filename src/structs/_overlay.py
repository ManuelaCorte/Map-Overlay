import math as m
from copy import deepcopy
from dataclasses import dataclass
from typing import Self, TypeAlias

import graphviz

from src.structs import Feature, Point, PolygonGeometry
from src.utils import ClassComparisonError, DcelError


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

    @property
    def prefix(self) -> str:
        return self.id.split("_")[0]

    @classmethod
    def from_vertices(
        cls, origin: VertexId, destination: VertexId, prefix: str
    ) -> Self:
        return cls(
            id=f"{prefix}_e_{origin.id.split("_")[2]}_{destination.id.split("_")[2]}"
        )

    @classmethod
    def null(cls) -> Self:
        return cls(id="e_null")


_Edge: TypeAlias = "Edge"


@dataclass(frozen=True)
class Face:
    """Representation of a face in the overlay of two planar subdivisions."""

    id: FaceId
    outer_component: EdgeId
    inner_components: list[EdgeId]

    def __hash__(self) -> int:
        return hash(self.id.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Face):
            raise ClassComparisonError("Cannot compare Face with non-Face")
        return self.id.id == other.id.id

    @property
    def is_external(self) -> bool:
        return self.outer_component.is_null()

    @property
    def is_null(self) -> bool:
        return self.id.is_null()

    @classmethod
    def null(cls) -> Self:
        return cls(
            id=FaceId.null(),
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

    def same_dcel(self, other: Self) -> bool:
        """Check if the two edges belong to the same DCEL by comparing the prefixes."""
        return self.id.id.split("_")[0] == other.id.id.split("_")[0]


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
        polygons_list: list[list[tuple[Point, Point]]],
        prefix: str = "dcel",
    ) -> None:
        self.faces: dict[FaceId, Face] = {}
        self.edges: dict[EdgeId, Edge] = {}
        self.vertices: dict[VertexId, Vertex] = {}
        self.points: dict[Point, VertexId] = {}
        self.prefix = prefix

        if len(polygons_list) > 0:
            self._build_dcel(polygons_list)

    @property
    def segments(self) -> list[list[tuple[Point, Point]]]:
        segments: list[list[tuple[Point, Point]]] = []
        for face in self.faces.values():
            if face.is_external:
                continue
            boundary = self.boundary(face.outer_component)
            face_segments: list[tuple[Point, Point]] = []
            for edge_id in boundary:
                edge = self.edges[edge_id]
                origin = self.vertices[edge.origin].coordinates
                destination = self.vertices[self.edges[edge.next].origin].coordinates
                face_segments.append((origin, destination))
            segments.append(face_segments)
        return segments

    @classmethod
    def from_features(cls, features: list[Feature]) -> Self:
        points: list[Point] = []
        polygons: list[list[tuple[Point, Point]]] = []
        for feature in features:
            if not isinstance(feature.geometry, PolygonGeometry):
                raise DcelError(
                    "The algorithm does not support geometries other than polygons"
                )
            if len(feature.geometry.inner) > 0:
                raise NotImplementedError(
                    "The algorithm does not support polygons with holes"
                )
            border = deepcopy(feature.geometry.outer)

            polygon: list[tuple[Point, Point]] = []
            for i in range(len(border)):
                origin = Point(*border[i])
                destination = Point(*border[(i + 1) % len(border)])
                points.append(origin)
                points.append(destination)
                polygon.append((origin, destination))

            polygons.append(polygon)

        return cls(polygons)

    def boundary(self, edge: EdgeId) -> list[EdgeId]:
        next_edge = self.edges[edge].next
        boundary = [edge]
        while next_edge != edge:
            boundary.append(next_edge)
            next_edge = self.edges[next_edge].next
        return boundary

    def to_image(self, path: str) -> None:
        dot = graphviz.Digraph(name="DCEL", format="png", engine="neato")
        dot.attr(overlap="false")
        for node in self.vertices.values():
            dot.node(
                node.id.id,
                label=node.id.id,
                pos=f"{node.coordinates.x},{node.coordinates.y}",
            )

        for face in self.faces.values():
            if face.is_external:
                for inner_component in face.inner_components:
                    boundary = self.boundary(inner_component)
                    for edge_id in boundary:
                        edge = self.edges[edge_id]
                        dot.edge(
                            edge.origin.id,
                            self.edges[edge.next].origin.id,
                            label=edge.incident_face.id,
                        )
            else:
                boundary = self.boundary(face.outer_component)
                for edge_id in boundary:
                    edge = self.edges[edge_id]
                    dot.edge(
                        edge.origin.id,
                        self.edges[edge.next].origin.id,
                        label=edge.incident_face.id,
                    )

        dot.render(path, overwrite_source=True, cleanup=True)

    def populate(
        self,
        points: dict[Point, VertexId],
        vertices: dict[VertexId, Vertex],
        edges: dict[EdgeId, Edge],
        faces: dict[FaceId, Face],
    ) -> None:
        """Populate the DCEL with the provided data. Note that all previous data will be lost.

        Params:
        -  points: dict[Point, VertexId] - The points of the DCEL
        -  vertices: dict[VertexId, Vertex] - The vertices of the DCEL
        -  edges: dict[EdgeId, Edge] - The edges of the DCEL
        -  faces: dict[FaceId, Face] - The faces of the DCEL"""
        self.points = points
        self.vertices = vertices
        self.edges = edges
        self.faces = faces

    ###############################
    ## Private methods
    ###############################

    # Algorithm inspired by the description provided in
    # https://cs.stackexchange.com/questions/2450/how-do-i-construct-a-doubly-connected-edge-list-given-a-set-of-line-segments
    def _build_dcel(self, polygons: list[list[tuple[Point, Point]]]) -> None:
        # Create vertices
        for border in polygons:
            for origin, destination in border:
                if origin not in self.points:
                    vertex_id = VertexId(id=f"{self.prefix}_v_{len(self.vertices)}")
                    self.vertices[vertex_id] = Vertex(
                        id=vertex_id,
                        coordinates=origin,
                        incident_edges=[],
                    )
                    self.points[origin] = vertex_id

                if destination not in self.points:
                    vertex_id = VertexId(id=f"{self.prefix}_v_{len(self.vertices)}")
                    self.vertices[vertex_id] = Vertex(
                        id=vertex_id,
                        coordinates=destination,
                        incident_edges=[],
                    )
                    self.points[destination] = vertex_id

        # Create edges
        for _, border in enumerate(polygons):
            for origin, destination in border:
                origin_id = self.points[origin]
                destination_id = self.points[destination]
                edge_id = EdgeId.from_vertices(origin_id, destination_id, self.prefix)
                twin_id = EdgeId.from_vertices(destination_id, origin_id, self.prefix)

                self.edges[edge_id] = Edge(
                    id=edge_id,
                    origin=origin_id,
                    twin=twin_id,
                    incident_face=FaceId.null(),
                    next=EdgeId.null(),
                    prev=EdgeId.null(),
                )
                self.vertices[origin_id].add_incident_edge(edge_id)

                if self.edges.get(twin_id) is None:
                    self.edges[twin_id] = Edge(
                        id=twin_id,
                        origin=destination_id,
                        twin=edge_id,
                        incident_face=FaceId.null(),
                        next=EdgeId.null(),
                        prev=EdgeId.null(),
                    )
                    self.vertices[destination_id].add_incident_edge(twin_id)

        # Connect edges
        for border in polygons:
            for i, (start, end) in enumerate(border):
                border_len = len(border)
                edge_id = EdgeId.from_vertices(
                    self.points[start],
                    self.points[end],
                    self.prefix,
                )
                edge = self.edges[edge_id]
                next_edge_id = EdgeId.from_vertices(
                    self.points[end],
                    self.points[border[(i + 1) % border_len][1]],
                    self.prefix,
                )
                prev_edge_id = EdgeId.from_vertices(
                    self.points[border[(i - 1 % border_len)][0]],
                    self.points[start],
                    self.prefix,
                )
                self.edges[edge_id] = Edge(
                    id=edge_id,
                    origin=edge.origin,
                    twin=edge.twin,
                    incident_face=edge.incident_face,
                    next=next_edge_id,
                    prev=prev_edge_id,
                )

                twin_id = self.edges[edge_id].twin
                twin = self.edges[twin_id]
                next_twin_id = EdgeId.from_vertices(
                    self.points[start],
                    self.points[border[(i - 1) % border_len][0]],
                    self.prefix,
                )
                prev_twin_id = EdgeId.from_vertices(
                    self.points[border[(i + 1) % border_len][1]],
                    self.points[end],
                    self.prefix,
                )
                self.edges[twin_id] = Edge(
                    id=twin_id,
                    origin=twin.origin,
                    twin=twin.twin,
                    incident_face=twin.incident_face,
                    next=next_twin_id,
                    prev=prev_twin_id,
                )

        # Sort incident edges
        for vertex in self.vertices.values():
            ordered_edges = self.sort_incident_edges(vertex.incident_edges)
            self.vertices[vertex.id] = Vertex(
                id=vertex.id,
                coordinates=vertex.coordinates,
                incident_edges=ordered_edges,
            )

        for vertex in self.vertices.values():
            # For every pair of half-edges e1, e2 in clockwise order,
            # assign e1->twin->next = e2 and e2->prev = e1->twin.
            for i in range(len(vertex.incident_edges)):
                e1 = vertex.incident_edges[i]
                e2 = vertex.incident_edges[(i + 1) % len(vertex.incident_edges)]

                e1_twin = self.edges[self.edges[e1].twin]
                self.edges[e1_twin.id] = Edge(
                    id=e1_twin.id,
                    origin=e1_twin.origin,
                    twin=e1_twin.twin,
                    incident_face=e1_twin.incident_face,
                    next=e2,
                    prev=e1_twin.prev,
                )

                e2_edge = self.edges[e2]
                self.edges[e2] = Edge(
                    id=e2,
                    origin=e2_edge.origin,
                    twin=e2_edge.twin,
                    incident_face=e2_edge.incident_face,
                    next=e2_edge.next,
                    prev=e1_twin.id,
                )

        # for each cycle of half-edges, create a face
        edges_copy = deepcopy(self.edges)
        self.assign_faces(edges_copy)
        # TODO: merge all external faces into one ?

    def assign_faces(self, edges_copy: dict[EdgeId, Edge]) -> None:
        # for each cycle of half-edges, create a face
        while edges_copy:
            edge = edges_copy.popitem()[1]
            if edge.incident_face.is_null():
                face_id = FaceId(id=f"f_{len(self.faces)}")
                face = Face(
                    id=face_id,
                    outer_component=edge.id,
                    inner_components=[],
                )
                self.faces[face_id] = face
                self.edges[edge.id] = Edge(
                    id=edge.id,
                    origin=edge.origin,
                    twin=edge.twin,
                    incident_face=face_id,
                    next=edge.next,
                    prev=edge.prev,
                )

                next_edge = self.edges[edge.next]
                while next_edge != edge:
                    self.edges[next_edge.id] = Edge(
                        id=next_edge.id,
                        origin=next_edge.origin,
                        twin=next_edge.twin,
                        incident_face=face_id,
                        next=next_edge.next,
                        prev=next_edge.prev,
                    )
                    edges_copy.pop(next_edge.id)
                    next_edge = self.edges[next_edge.next]

        # Find external face as the one with negative area
        external_face = None
        for face in self.faces.values():
            if self._face_area(face) < 0:
                external_face = deepcopy(face)
                self.faces[external_face.id] = Face(
                    id=external_face.id,
                    outer_component=EdgeId.null(),
                    inner_components=[external_face.outer_component],
                )
        if external_face is None:
            raise DcelError("No external face found")

    def sort_incident_edges(
        self, incident_edges: list[EdgeId], clockwise: bool = True
    ) -> list[EdgeId]:
        """Sort the incident edges of a vertex

        Params:
        -  vertex: Vertex - The vertex to sort
        -  clockwise: bool - Whether to sort the edges in clockwise or counterclockwise order

        Returns:
        -  Vertex - The vertex with the sorted incident edges"""

        return sorted(
            incident_edges,
            key=lambda e: self._angle(self.edges[e]),
            reverse=clockwise,
        )

    def _angle(self, edge: Edge) -> float:
        # calculate angle between edge and x-axis in degrees
        x1, y1 = self.vertices[edge.origin].coordinates
        x2, y2 = self.vertices[self.edges[edge.twin].origin].coordinates

        angle = m.degrees(m.atan2(y2 - y1, x2 - x1))
        return angle if angle >= 0 else angle + 360

    def _face_area(self, face: Face) -> float:
        # compute the signed area of a face
        area = 0
        perimeter = self.boundary(face.outer_component)
        for edge_id in perimeter:
            edge = self.edges[edge_id]
            origin = self.vertices[edge.origin].coordinates
            destination = self.vertices[self.edges[edge.next].origin].coordinates
            area += origin.x * destination.y - origin.y * destination.x

        return area / 2
