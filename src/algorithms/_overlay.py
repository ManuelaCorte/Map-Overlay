from copy import deepcopy

from src.structs import (
    DoublyConnectedEdgeList,
    Edge,
    EdgeId,
    Face,
    FaceId,
    Point,
    Segment,
    Vertex,
    VertexId,
)
from src.utils import DcelError

from ._intersection import sweep_line_intersection


def overlay(
    s1: DoublyConnectedEdgeList, s2: DoublyConnectedEdgeList
) -> DoublyConnectedEdgeList:
    """Compute the overlay of two doubly connected edge lists."""
    dcel = _merge(s1, s2)

    segments: set[Segment] = set()
    for _, edge in dcel.edges.items():
        # Add the segments to the list so that they're ordered by y
        twin = dcel.edges[edge.twin]
        origin = dcel.vertices[edge.origin].coordinates
        destination = dcel.vertices[twin.origin].coordinates
        segment = Segment(
            Point(origin.x, origin.y), Point(destination.x, destination.y)
        )
        p1, p2 = segment.order_by_y()
        new_id = EdgeId.from_vertices(
            dcel.points[p1],
            dcel.points[p2],
            edge.id.prefix,
        )
        segments.add(Segment(p1, p2, new_id.id))

    intersections, splitted_segments = sweep_line_intersection(list(segments))

    # Add new vertices for the intersection points
    for intersection_point in intersections.keys():
        if intersection_point not in dcel.points:
            vertex_id = VertexId(f"{dcel.prefix}_v_{len(dcel.vertices)}")
            dcel.points[intersection_point] = vertex_id
            dcel.vertices[vertex_id] = Vertex(vertex_id, intersection_point, [])

    splitted_edges: dict[EdgeId, list[tuple[EdgeId, EdgeId]]] = (
        _split_segments_into_edges(dcel, splitted_segments)
    )

    # Remove the original edges and add the new ones
    for original_edge, new_edges in splitted_edges.items():
        _update_original_edge(dcel, original_edge, new_edges)

    for intersection_point, intersecting_segments in intersections.items():
        # check if the all intersecting segments belong to the same overlay
        intersecting_overlays = (
            len(
                set(
                    map(lambda segment: segment.id.split("_")[0], intersecting_segments)
                )
            )
            > 1
        )
        if not intersecting_overlays:
            continue

        # check if the intersection point is an endpoint for all the intersecting segments
        intersection_at_endpoint = map(
            lambda segment: segment.p1 == intersection_point
            or segment.p2 == intersection_point,
            intersecting_segments,
        )
        if all(intersection_at_endpoint):
            intersection_vertex = dcel.vertices[dcel.points[intersection_point]]
            sorted_edges = dcel.sort_incident_edges(intersection_vertex.incident_edges)
            dcel.vertices[intersection_vertex.id] = Vertex(
                intersection_vertex.id, intersection_vertex.coordinates, sorted_edges
            )
            _update_intersection_incident_edges(dcel, intersection_vertex)

        if not all(intersection_at_endpoint):
            # TODO: handle the case where the intersection is the enpoint only for
            # the segments in one of the overlays

            intersection_vertex = dcel.vertices[dcel.points[intersection_point]]
            _update_intersection_incident_edges(dcel, intersection_vertex)

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
    edges: dict[EdgeId, Edge] = {
        edge_id: Edge(
            edge.id, edge.origin, edge.twin, FaceId.null(), edge.next, edge.prev
        )
        for edge_id, edge in s1.edges.items()
    }
    faces: dict[FaceId, Face] = {}

    for point, vertex_id in s2.points.items():
        if point not in points:
            points[point] = vertex_id
        else:
            s1_vertex = vertices[points[point]]
            s2_vertex = s2.vertices[vertex_id]
            points[point] = s2_vertex.id
            del vertices[s1_vertex.id]

            new_vertex = Vertex(
                s2_vertex.id,
                s2_vertex.coordinates,
                s2_vertex.incident_edges,
            )
            # update incident edges of the vertices
            for edge_id in s1_vertex.incident_edges:
                edge = edges[edge_id]
                edges[edge_id] = Edge(
                    edge.id,
                    s2_vertex.id,
                    edge.twin,
                    edge.incident_face,
                    edge.next,
                    edge.prev,
                )
            new_vertex.incident_edges.extend(s1_vertex.incident_edges)
            vertices[s2_vertex.id] = new_vertex

    for vertex_id, vertex in s2.vertices.items():
        if vertex_id not in vertices:
            vertices[vertex_id] = vertex

    for edge_id, edge in s2.edges.items():
        if edge_id not in edges:
            edges[edge_id] = Edge(
                edge.id,
                edge.origin,
                edge.twin,
                FaceId.null(),
                edge.next,
                edge.prev,
            )
        else:
            raise DcelError("The two DCELs have the same edge id")

    dcel.populate(points, vertices, edges, faces)
    return dcel


def _split_segments_into_edges(
    dcel: DoublyConnectedEdgeList, splitted_segments: dict[Segment, list[Point]]
) -> dict[EdgeId, list[tuple[EdgeId, EdgeId]]]:
    """Split the segments into edges and create the corresponding twin edges

    Params:
    -  dcel - The doubly connected edge list
    -  splitted_segments - The segments that have been split

    Returns:
    -  The splitted edges
    """
    splitted_edges: dict[EdgeId, list[tuple[EdgeId, EdgeId]]] = {}
    for segment, points in splitted_segments.items():
        if len(points) <= 2:
            continue

        for i in range(0, len(points) - 1):
            edge_id = EdgeId.from_vertices(
                dcel.points[points[i]],
                dcel.points[points[i + 1]],
                f"{dcel.prefix}_{segment.id.split('_')[0]}",
            )
            twin_id = EdgeId.from_vertices(
                dcel.points[points[i + 1]],
                dcel.points[points[i]],
                f"{segment.id.split('_')[0]}_{dcel.prefix}",
            )
            if splitted_edges.get(EdgeId(segment.id)) is None:
                splitted_edges[EdgeId(segment.id)] = [(edge_id, twin_id)]
            else:
                splitted_edges[EdgeId(segment.id)].extend([(edge_id, twin_id)])

            edge = Edge(
                edge_id,
                dcel.points[points[i]],
                twin_id,
                FaceId.null(),
                EdgeId.null(),
                EdgeId.null(),
            )
            dcel.edges[edge_id] = edge

            twin = Edge(
                twin_id,
                dcel.points[points[i + 1]],
                edge_id,
                FaceId.null(),
                EdgeId.null(),
                EdgeId.null(),
            )
            dcel.edges[twin_id] = twin

    return splitted_edges


def _update_original_edge(
    dcel: DoublyConnectedEdgeList,
    original_edge_id: EdgeId,
    new_edges: list[tuple[EdgeId, EdgeId]],
) -> None:
    """Update the original edge with the new edges

    Params:
    -  dcel - The doubly connected edge list
    -  original_edge - The original edge
    -  new_edges - The new edges
    """

    # Remove the original edge from the incident edges of the origin vertex
    original_edge = dcel.edges[original_edge_id]
    dcel.vertices[original_edge.origin] = Vertex(
        original_edge.origin,
        dcel.vertices[original_edge.origin].coordinates,
        list(
            filter(
                lambda edge_id: edge_id != original_edge.id,
                dcel.vertices[original_edge.origin].incident_edges,
            )
        ),
    )

    # Remove the twin edge from the incident edges of the destination vertex
    original_twin_edge = dcel.edges[original_edge.twin]
    dcel.vertices[original_twin_edge.origin] = Vertex(
        original_twin_edge.origin,
        dcel.vertices[original_twin_edge.origin].coordinates,
        list(
            filter(
                lambda edge_id: edge_id != original_twin_edge.id,
                dcel.vertices[original_twin_edge.origin].incident_edges,
            )
        ),
    )

    # Update predecessor of the original edge
    first_new_edge, first_new_edge_twin = new_edges[0]
    prev_edge = dcel.edges[original_edge.prev]
    prev_edge_twin = dcel.edges[prev_edge.twin]
    dcel.edges[prev_edge.id] = Edge(
        prev_edge.id,
        prev_edge.origin,
        prev_edge.twin,
        prev_edge.incident_face,
        first_new_edge,
        prev_edge.prev,
    )
    dcel.edges[prev_edge_twin.id] = Edge(
        prev_edge_twin.id,
        prev_edge_twin.origin,
        prev_edge_twin.twin,
        prev_edge_twin.incident_face,
        prev_edge_twin.next,
        first_new_edge_twin,
    )

    # Update successor of the original edge
    last_new_edge, last_new_edge_twin = new_edges[-1]
    next_edge = dcel.edges[original_edge.next]
    next_edge_twin = dcel.edges[next_edge.twin]

    dcel.edges[next_edge.id] = Edge(
        next_edge.id,
        next_edge.origin,
        next_edge.twin,
        next_edge.incident_face,
        next_edge.next,
        last_new_edge,
    )
    dcel.edges[next_edge_twin.id] = Edge(
        next_edge_twin.id,
        next_edge_twin.origin,
        next_edge_twin.twin,
        next_edge_twin.incident_face,
        last_new_edge_twin,
        next_edge_twin.prev,
    )

    # Link the new edges
    for i in range(len(new_edges)):
        new_edge = dcel.edges[new_edges[i][0]]
        new_edge_twin = dcel.edges[new_edges[i][1]]

        # Add the new edges to the incident edges of the origin and destination vertices
        origin_vertex = dcel.vertices[new_edge.origin]
        dcel.vertices[new_edge.origin] = Vertex(
            new_edge.origin,
            origin_vertex.coordinates,
            origin_vertex.incident_edges + [new_edge.id],
        )

        destination_vertex = dcel.vertices[new_edge_twin.origin]
        dcel.vertices[new_edge_twin.origin] = Vertex(
            new_edge_twin.origin,
            destination_vertex.coordinates,
            destination_vertex.incident_edges + [new_edge_twin.id],
        )

        # Update the predecessor and successor of the new edges
        if i == 0:
            dcel.edges[new_edge.id] = Edge(
                new_edge.id,
                new_edge.origin,
                new_edge.twin,
                new_edge.incident_face,
                new_edges[i + 1][0],
                original_edge.prev,
            )
            dcel.edges[new_edge_twin.id] = Edge(
                new_edge_twin.id,
                new_edge_twin.origin,
                new_edge_twin.twin,
                new_edge_twin.incident_face,
                original_twin_edge.next,
                new_edges[i + 1][1],
            )
        elif i == len(new_edges) - 1:
            dcel.edges[new_edge.id] = Edge(
                new_edge.id,
                new_edge.origin,
                new_edge.twin,
                new_edge.incident_face,
                original_edge.next,
                new_edges[i - 1][0],
            )
            dcel.edges[new_edge_twin.id] = Edge(
                new_edge_twin.id,
                new_edge_twin.origin,
                new_edge_twin.twin,
                new_edge_twin.incident_face,
                new_edges[i - 1][1],
                original_twin_edge.prev,
            )
        else:
            dcel.edges[new_edge.id] = Edge(
                new_edge.id,
                new_edge.origin,
                new_edge.twin,
                new_edge.incident_face,
                new_edges[i + 1][0],
                new_edges[i - 1][0],
            )
            dcel.edges[new_edge_twin.id] = Edge(
                new_edge_twin.id,
                new_edge_twin.origin,
                new_edge_twin.twin,
                new_edge_twin.incident_face,
                new_edges[i - 1][1],
                new_edges[i + 1][1],
            )

    # Remove the original edge and its twin from the edges
    del dcel.edges[original_edge.id]
    del dcel.edges[original_twin_edge.id]


def _update_intersection_incident_edges(
    dcel: DoublyConnectedEdgeList,
    intersection_vertex: Vertex,
) -> None:
    """Update the incident edges of the intersection vertex so that the previous edge
    is the twin of the previous clockwise incident edge

    Params:
    -  dcel - The doubly connected edge list
    -  intersection_vertex - The intersection vertex
    """

    sorted_edges = dcel.sort_incident_edges(intersection_vertex.incident_edges)
    for i, edge_id in enumerate(sorted_edges):
        edge = dcel.edges[edge_id]
        cw_prev = dcel.edges[dcel.edges[sorted_edges[(i - 1) % len(sorted_edges)]].twin]
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

    dcel.vertices[intersection_vertex.id] = Vertex(
        intersection_vertex.id, intersection_vertex.coordinates, sorted_edges
    )
