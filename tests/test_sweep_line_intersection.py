import os

from src.algorithms import sweep_line_intersection
from src.data import read_intersection_data


# Test files were taken from: https://github.com/the-hyp0cr1t3/sweepline-intersections
def test_sweep_line_intersection():
    files = os.listdir("data/intersections")
    for file in files:
        path = f"data/intersections/{file}"
        print(f"Testing {path}")
        segments, num_intersections = read_intersection_data(path)

        intersections, _ = sweep_line_intersection(segments)
        assert len(intersections.keys()) == num_intersections
