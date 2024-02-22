import os
from src.data import (
    read_intersection_data,
    plot_intersections,
)
from src.algorithms import (
    SweepLineIntersection,
    naive_intersection,
)

if __name__ == "__main__":
    files = os.listdir("data/intersections")
    skip = ["test_degenerate_colinear_01.txt", "test_degenerate_colinear_02.txt"]
    for file in files:
        if file in skip:
            continue
        segments, num_intersections = read_intersection_data(
            f"data/intersections/{file}"
        )
        print(file)
        sweep_line = SweepLineIntersection(segments)
        sweep_line.run()

        naive_intersections = naive_intersection(segments)
        print(
            "gt",
            num_intersections,
            "sweep line",
            len(sweep_line.intersections),
            "naive",
            len(naive_intersections),
        )
        plot_intersections(segments, naive_intersections)
