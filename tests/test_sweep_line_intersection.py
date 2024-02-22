import os
from src.data import read_intersection_data
from src.algorithms import SweepLineIntersection
import pytest
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
                sweep_line_intersection = SweepLineIntersection(segments)
                sweep_line_intersection.run()
            assert type(ex_info.value) == CollinearityError
        else:
            sweep_line_intersection = SweepLineIntersection(segments)
            sweep_line_intersection.run()
            assert len(sweep_line_intersection.intersections) == num_intersections
