from pprint import pprint
from src.data import read_intersection_data, plot_intersections
from src.intersection import sweep_line_intersection

if __name__ == "__main__":
    segments, num_intersections = read_intersection_data(
        "data/intersections/sample_test3.txt"
    )
    intersections = sweep_line_intersection(segments)
    pprint(intersections)
    print(num_intersections, len(intersections))

    plot_intersections(segments, intersections)
