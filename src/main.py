from src.data import read_overlay_data, plot_overlay
from src.structs import (
    DoublyConnectedEdgeList,
)

if __name__ == "__main__":
    file = "test_1"
    segments = read_overlay_data(f"data/overlays/{file}.txt")
    plot_overlay(segments)
    dcel = DoublyConnectedEdgeList(
        [[(segment.p1, segment.p2) for segment in face] for face in segments],
    )
    dcel.to_image(f"data/overlays/imgs/{file}")
