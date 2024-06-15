from src.data import read_geojson_file, plot_geojson
from src.structs import (
    DoublyConnectedEdgeList,
)

if __name__ == "__main__":
    file = "polygons"
    features = read_geojson_file(f"data/overlays/{file}.json")
    plot_geojson(f"data/overlays/{file}.json")
    dcel = DoublyConnectedEdgeList.from_features(features)
    dcel.to_image(f"data/overlays/imgs/{file}")
