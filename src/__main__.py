import argparse
from typing import Optional
from src.algorithms import overlay, sweep_line_intersection
from src.data import (
    read_overlay_data,
    plot_dcels,
    plot_overlay,
    read_intersection_data,
    plot_intersections,
)
from src.structs import DoublyConnectedEdgeList


def run_intersection(files: list[str], output_folder: Optional[str], plot: bool):
    if len(files) != 1:
        print("Only one file can be passed for intersection algorithm")
        return

    file = files[0]
    segments, _ = read_intersection_data(file)
    sweep_intersections, _ = sweep_line_intersection(segments)
    print("Number of intersections found: ", len(sweep_intersections))
    file_path: Optional[str] = None
    if output_folder:
        file_path = output_folder + "/" + file.split("/")[-1].split(".")[0]

    if plot:
        plot_intersections(segments, list(sweep_intersections.keys()), file_path)


def run_overlay(files: list[str], output_folder: Optional[str], plot: bool):
    if len(files) != 2:
        print("Only two files can be passed for overlay algorithm")
        return

    segments1 = read_overlay_data(files[0])
    dcel1 = DoublyConnectedEdgeList(segments1, "s1")
    segments2 = read_overlay_data(files[1])
    dcel2 = DoublyConnectedEdgeList(segments2, "s2")

    if plot:
        plot_dcels(segments1, segments2)

    overlay_dcel = overlay(dcel1, dcel2)
    print(
        "Number of faces in overlay: ",
        len([face for face in overlay_dcel.faces.values() if not face.is_external]),
    )
    file_path: Optional[str] = None
    if output_folder:
        file_path = (
            files[0].split("/")[-1].split(".")[0]
            + "_"
            + files[1].split("/")[-1].split(".")[0]
        )
        file_path = output_folder + "/" + file_path

    if plot:
        plot_overlay(overlay_dcel.segments, file_path)

    if output_folder:
        overlay_dcel.to_image(f"{file_path}_graph")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run overlay or intersection algorithm"
    )
    parser.add_argument(
        "--overlay",
        action="store_true",
        help="Run overlay algorithm",
    )
    parser.add_argument(
        "--intersection",
        action="store_true",
        help="Run intersection algorithm",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Files to run. For overlay two files are needed. For intersection only one file is needed.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output folder to save the results",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot the results",
    )

    args = parser.parse_args()

    if args.overlay:
        run_overlay(args.files, args.output, args.plot)
    elif args.intersection:
        run_intersection(args.files, args.output, args.plot)
    else:
        print("Please specify either --overlay or --intersection flag")
