from dataclasses import dataclass
from typing import Optional, Self
from src.structs import Point
from src.utils import ClassComparisonError


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
