import os

from src.algorithms import naive_intersection
from src.data import read_intersection_data


# Test files were adapted from:
# - https://github.com/the-hyp0cr1t3/sweepline-intersections
# - https://github.com/ideasman42/isect_segments-bentley_ottmann
def test_naive_intersection():
    files = os.listdir("data/intersections")
    for file in files:
        path = f"data/intersections/{file}"
        print(f"Testing {path}")
        segments, num_intersections = read_intersection_data(path)
        assert len(naive_intersection(segments)) == num_intersections
