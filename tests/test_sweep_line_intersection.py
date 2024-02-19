import os
from src.data import read_intersection_data
from src.intersection import SweepLineIntersection


# Test files were taken from: https://github.com/the-hyp0cr1t3/sweepline-intersections
def test_sweep_line_intersection():
    files = os.listdir("data/intersections")
    for file in files:
        path = f"data/intersections/{file}"
        print(f"Testing {path}")
        segments, num_intersections = read_intersection_data(path)
        sweep_line_intersection = SweepLineIntersection(segments)
        sweep_line_intersection.run()
        assert len(sweep_line_intersection.intersections) == num_intersections
