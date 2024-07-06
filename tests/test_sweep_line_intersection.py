import os

import pytest

from src.algorithms import sweep_line_intersection
from src.data import read_intersection_data
from src.utils import CollinearityError


# Test files were taken from: https://github.com/the-hyp0cr1t3/sweepline-intersections
def test_sweep_line_intersection():
    files = os.listdir("data/intersections")
    for file in files:
        path = f"data/intersections/{file}"
        print(f"Testing {path}")
        segments, num_intersections = read_intersection_data(path)

        if num_intersections == -1:
            with pytest.raises(CollinearityError) as ex_info:
                intersections = sweep_line_intersection(segments)
            assert type(ex_info.value) == CollinearityError
        else:
            intersections, _ = sweep_line_intersection(segments)
            assert len(intersections.keys()) == num_intersections
