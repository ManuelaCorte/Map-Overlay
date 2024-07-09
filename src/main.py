from src.algorithms import overlay
from src.data import (
    read_overlay_data,
    plot_dcels,
    plot_overlay,
)
from src.structs import DoublyConnectedEdgeList

if __name__ == "__main__":
    segments1 = read_overlay_data("data/overlays/test_2.txt")
    dcel1 = DoublyConnectedEdgeList(segments1, "s1")
    dcel1.to_image("data/overlays/imgs/test_9")
    segments2 = read_overlay_data("data/overlays/test_3.txt")
    dcel2 = DoublyConnectedEdgeList(segments2, "s2")

    plot_dcels(segments1, segments2)
    overlay_dcel = overlay(dcel1, dcel2)
    overlay_dcel.to_image("data/overlays/imgs/2_3")
    plot_overlay(overlay_dcel.segments)
    print(len([face for face in overlay_dcel.faces.values() if not face.is_external]))

    # file = "polygons"
    # features = read_geojson_file(f"data/overlays/{file}.json")
    # plot_geojson(f"data/overlays/{file}.json")
    # dcel = DoublyConnectedEdgeList.from_features(features)
    # dcel.to_image(f"data/overlays/imgs/{file}")
    # plot_overlay(dcel.segments)

    # segments, _ = read_intersection_data(
    #     "data/intersections/test_degenerate_colinear_02.txt"
    # )
    # sweep_intersections, _ = sweep_line_intersection(segments)
    # plot_intersections(segments, list(sweep_intersections.keys()))
    # print(len(sweep_intersections))
