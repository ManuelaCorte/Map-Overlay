from src.data import read_overlay_data, plot_overlay
from src.algorithms import overlay
from src.structs import DoublyConnectedEdgeList

if __name__ == "__main__":
    segments1 = read_overlay_data("data/overlays/test_5.txt")
    dcel1 = DoublyConnectedEdgeList(segments1, "s1")

    segments2 = read_overlay_data("data/overlays/test_6.txt")
    dcel2 = DoublyConnectedEdgeList(segments2, "s2")

    overlay_dcel = overlay(dcel1, dcel2)
    overlay_dcel.to_image("data/overlays/imgs/test_5_6")
    plot_overlay(overlay_dcel.segments)

    # file = "polygons"
    # features = read_geojson_file(f"data/overlays/{file}.json")
    # plot_geojson(f"data/overlays/{file}.json")
    # dcel = DoublyConnectedEdgeList.from_features(features)
    # dcel.to_image(f"data/overlays/imgs/{file}")
    # plot_overlay(dcel.segments)
