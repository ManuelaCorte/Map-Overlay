from src.data import read_geojson_file, plot_geojson
from src.algorithms import (
    DoublyConnectedEdgeList,
)

if __name__ == "__main__":
    features = read_geojson_file("data/overlays/grid.json")
    plot_geojson(
        "data/overlays/grid.json",
    )
    dcel = DoublyConnectedEdgeList(features)
    dcel.to_image("data/overlays/imgs/grid")
