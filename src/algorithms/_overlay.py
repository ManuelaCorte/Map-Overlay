from copy import deepcopy
from src.structs import (
    DoublyConnectedEdgeList,
    Segment,
    Point,
    VertexId,
    EdgeId,
    FaceId,
    Vertex,
    Edge,
    Face,
)
from ._intersection import sweep_line_intersection
from src.utils import DcelError


def overlay(
    s1: DoublyConnectedEdgeList, s2: DoublyConnectedEdgeList
) -> DoublyConnectedEdgeList:
    """Compute the overlay of two doubly connected edge lists."""
    dcel = _merge(s1, s2)

    segments: list[Segment] = []
    for edge_id, edge in dcel.edges.items():
        cw_prev = dcel.edges[edge.twin]
        origin = dcel.vertices[edge.origin].coordinates
        destination = dcel.vertices[cw_prev.origin].coordinates
        segments.append(Segment(origin, destination, edge_id.id))

    intersections = sweep_line_intersection(segments)
    edges_to_remove: list[EdgeId] = []
    for intersection_point, intersecting_segments in intersections.items():
        num_segments = len(intersecting_segments)
        intersecting_edges = [
            dcel.edges[EdgeId(segment.id)] for segment in intersecting_segments
        ]
        # for now we consider the simple case where only two segments intersect
        if num_segments != 2:
            print(intersection_point)
            print(intersecting_segments)

            raise NotImplementedError(
                "The algorithm only supports the case where two segments intersect"
            )
        edge1 = intersecting_edges[0]
        edge2 = intersecting_edges[1]
        if edge1.same_dcel(edge2):
            continue

        edges_to_remove.append(edge1.id)
        edges_to_remove.append(edge2.id)
        edges_to_remove.append(edge1.twin)
        edges_to_remove.append(edge2.twin)

        # create a new vertex at the intersection point
        vertex_id = VertexId(f"{dcel.prefix}_v_{len(dcel.vertices)}")
        dcel.points[intersection_point] = vertex_id
        dcel.vertices[vertex_id] = Vertex(vertex_id, intersection_point, [])

        # create new edges and update predecessors and successors
        e1, e2 = _split_edge_at_intersection(dcel, edge1, vertex_id)
        dcel.vertices[vertex_id].incident_edges.extend([e1, e2])
        e1, e2 = _split_edge_at_intersection(dcel, edge2, vertex_id)
        dcel.vertices[vertex_id].incident_edges.extend([e1, e2])

        # update intersection point incident edges
        intersection_vertex = dcel.sort_incident_edges(dcel.vertices[vertex_id])
        dcel.vertices[vertex_id] = intersection_vertex
        for i, edge_id in enumerate(intersection_vertex.incident_edges):
            edge = dcel.edges[edge_id]
            cw_prev = dcel.edges[
                dcel.edges[
                    intersection_vertex.incident_edges[
                        (i - 1) % len(intersection_vertex.incident_edges)
                    ]
                ].twin
            ]
            dcel.edges[edge_id] = Edge(
                edge.id,
                edge.origin,
                edge.twin,
                edge.incident_face,
                edge.next,
                cw_prev.id,
            )

            # update corresponding edge
            dcel.edges[cw_prev.id] = Edge(
                cw_prev.id,
                cw_prev.origin,
                cw_prev.twin,
                cw_prev.incident_face,
                edge_id,
                cw_prev.prev,
            )

    for edge_id in edges_to_remove:
        del dcel.edges[edge_id]

    # update faces
    dcel.assign_faces(deepcopy(dcel.edges))

    return dcel


def _merge(
    s1: DoublyConnectedEdgeList, s2: DoublyConnectedEdgeList
) -> DoublyConnectedEdgeList:
    """Merge two doubly connected edge lists."""
    if s1.prefix == s2.prefix:
        raise DcelError("The two DCELs have the same prefix")

    dcel = DoublyConnectedEdgeList([])
    points: dict[Point, VertexId] = s1.points.copy()
    vertices: dict[VertexId, Vertex] = s1.vertices.copy()
    edges: dict[EdgeId, Edge] = s1.edges.copy()
    faces: dict[FaceId, Face] = {}

    for point, vertex_id in s2.points.items():
        if point not in points:
            points[point] = vertex_id
        else:
            vertex = vertices[vertex_id]
            # replace the vertex id in the edges
            for edge_id in vertex.incident_edges:
                edge_to_update = s2.edges[edge_id]
                s2.edges[edge_id] = Edge(
                    edge_to_update.id,
                    vertex_id,
                    edge_to_update.twin,
                    edge_to_update.incident_face,
                    edge_to_update.next,
                    edge_to_update.prev,
                )
            del s2.vertices[vertex_id]

    points.update(s2.points)
    vertices.update(s2.vertices)
    edges.update(s2.edges)
    dcel.update(points, vertices, edges, faces)
    return dcel


def _split_edge_at_intersection(
    dcel: DoublyConnectedEdgeList,
    edge: Edge,
    intersection_vertex: VertexId,
) -> tuple[EdgeId, EdgeId]:
    """Split an edge into two separate edges with origin in the intersection point and destination in the original edge endpoints

    Params:
    -  dcel - The doubly connected edge list
    -  edge - The edge to split
    -  intersection_vertex - The intersection point
    """
    # create a new edge from the intersection point to the origin of the original edge
    twin = dcel.edges[edge.twin]

    edge1_id = EdgeId.from_vertices(
        intersection_vertex, edge.origin, f"{dcel.prefix}_{edge.id.id.split('_')[0]}"
    )
    edge1_twin_id = EdgeId.from_vertices(
        edge.origin, intersection_vertex, f"{edge.id.id.split('_')[0]}_{dcel.prefix}"
    )
    edge1 = Edge(
        edge1_id,
        intersection_vertex,
        edge1_twin_id,
        FaceId.null(),
        EdgeId.null(),
        EdgeId.null(),
    )
    dcel.edges[edge1_id] = edge1

    edge1_twin = Edge(
        edge1_twin_id,
        edge.origin,
        edge1_id,
        FaceId.null(),
        EdgeId.null(),
        EdgeId.null(),
    )
    dcel.edges[edge1_twin_id] = edge1_twin

    # create a new edge from the intersection point to the destination of the original edge
    edge2_id = EdgeId.from_vertices(
        intersection_vertex, twin.origin, f"{dcel.prefix}_{edge.id.id.split('_')[0]}"
    )
    edge2_twin_id = EdgeId.from_vertices(
        twin.origin, intersection_vertex, f"{edge.id.id.split('_')[0]}_{dcel.prefix}"
    )
    edge2 = Edge(
        edge2_id,
        intersection_vertex,
        edge2_twin_id,
        FaceId.null(),
        EdgeId.null(),
        EdgeId.null(),
    )
    dcel.edges[edge2_id] = edge2

    edge2_twin = Edge(
        edge2_twin_id,
        twin.origin,
        edge2_id,
        FaceId.null(),
        EdgeId.null(),
        EdgeId.null(),
    )
    dcel.edges[edge2_twin_id] = edge2_twin

    # update the predecessor and successor of the edge from intersection to origin
    dcel.edges[edge1_id] = Edge(
        edge1_id,
        edge1.origin,
        edge1.twin,
        FaceId.null(),
        dcel.edges[edge.prev].twin,
        edge2_twin_id,
    )
    dcel.edges[edge1_twin_id] = Edge(
        edge1_twin_id,
        edge1_twin.origin,
        edge1_twin.twin,
        FaceId.null(),
        edge2_id,
        edge.prev,
    )
    prev_edge = dcel.edges[edge.prev]
    dcel.edges[edge.prev] = Edge(
        prev_edge.id,
        prev_edge.origin,
        prev_edge.twin,
        FaceId.null(),
        edge1_twin_id,
        prev_edge.prev,
    )
    prev_edge_twin = dcel.edges[prev_edge.twin]
    dcel.edges[prev_edge.twin] = Edge(
        prev_edge_twin.id,
        prev_edge_twin.origin,
        prev_edge_twin.twin,
        FaceId.null(),
        prev_edge_twin.next,
        edge1_id,
    )

    # update the predecessor and successor of the edge from intersection to destination
    dcel.edges[edge2_id] = Edge(
        edge2_id,
        edge2.origin,
        edge2.twin,
        FaceId.null(),
        edge.next,
        edge1_twin_id,
    )
    dcel.edges[edge2_twin_id] = Edge(
        edge2_twin_id,
        edge2_twin.origin,
        edge2_twin.twin,
        FaceId.null(),
        edge1_id,
        dcel.edges[edge.next].twin,
    )
    next_edge = dcel.edges[edge.next]
    dcel.edges[edge.next] = Edge(
        next_edge.id,
        next_edge.origin,
        next_edge.twin,
        FaceId.null(),
        next_edge.next,
        edge2_id,
    )
    next_edge_twin = dcel.edges[next_edge.twin]
    dcel.edges[next_edge.twin] = Edge(
        next_edge_twin.id,
        next_edge_twin.origin,
        next_edge_twin.twin,
        FaceId.null(),
        edge2_twin_id,
        next_edge_twin.prev,
    )

    # update the incident edges of the endpoints
    dcel.vertices[edge.origin].incident_edges.append(edge1_id)
    dcel.vertices[edge.origin].incident_edges.remove(edge.id)
    dcel.vertices[twin.origin].incident_edges.append(edge2_id)
    dcel.vertices[twin.origin].incident_edges.remove(twin.id)

    return edge1_id, edge2_id
