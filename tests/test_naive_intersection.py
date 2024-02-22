import os

import pytest
from src.data import read_intersection_data
from src.algorithms import naive_intersection
from src.utils import CollinearityError


# Test files were adapted from:
# - https://github.com/the-hyp0cr1t3/sweepline-intersections
# - https://github.com/ideasman42/isect_segments-bentley_ottmann
def test_naive_intersection():
    files = os.listdir("data/intersections")
    for file in files:
        path = f"data/intersections/{file}"
        print(f"Testing {path}")
        segments, num_intersections = read_intersection_data(path)
        if num_intersections == -1:
            with pytest.raises(CollinearityError) as ex_info:
                naive_intersection(segments)
            assert type(ex_info.value) == CollinearityError
        else:
            assert len(naive_intersection(segments)) == num_intersections
