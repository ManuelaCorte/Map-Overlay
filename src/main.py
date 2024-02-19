from pprint import pprint
from src.data import read_intersection_data, plot_intersections
from src.intersection import SweepLineIntersection

if __name__ == "__main__":
    segments, num_intersections = read_intersection_data(
        "data/intersections/sample_test3.txt"
    )
    sweep_line_intersection = SweepLineIntersection(segments)
    sweep_line_intersection.run()
    intersections = sweep_line_intersection.intersections
    pprint(intersections)
    print(num_intersections, len(intersections))

    plot_intersections(segments, intersections)
