from src.algorithms import overlay
from src.data import read_overlay_data
from src.structs import DoublyConnectedEdgeList


def test_sweep_line_intersection():
    path = "data/overlays"
    combinations = path + "/tests.txt"
    file1 = None
    file2 = None
    num_faces = None
    with open(combinations) as f:
        for line in f.readlines():
            if line.strip() == "":
                file1 = None
                file2 = None
                num_faces = None
            if len(line.split(" ")) == 1 and line.strip() != "":
                num_faces = int(line)
            if len(line.split(" ")) == 2:
                file1, file2 = line.split(" ")
                file1 = file1.strip()
                file2 = file2.strip()

            if file1 is not None and file2 is not None and num_faces is not None:
                path1 = f"{path}/test_{file1}.txt"
                path2 = f"{path}/test_{file2}.txt"
                segments1 = read_overlay_data(path1)
                segments2 = read_overlay_data(path2)
                dcel1 = DoublyConnectedEdgeList(segments1, "s1")
                dcel2 = DoublyConnectedEdgeList(segments2, "s2")
                overlay_dcel = overlay(dcel1, dcel2)
                print(f"{path1} {path2}")
                found_faces = len(
                    [
                        face
                        for face in overlay_dcel.faces.values()
                        if not face.is_external
                    ]
                )
                assert found_faces == num_faces

                path1 = f"{path}/test_{file2}.txt"
                path2 = f"{path}/test_{file1}.txt"
                segments1 = read_overlay_data(path1)
                segments2 = read_overlay_data(path2)
                dcel1 = DoublyConnectedEdgeList(segments1, "s1")
                dcel2 = DoublyConnectedEdgeList(segments2, "s2")
                overlay_dcel = overlay(dcel1, dcel2)
                print(f"{path1} {path2}")
                found_faces = len(
                    [
                        face
                        for face in overlay_dcel.faces.values()
                        if not face.is_external
                    ]
                )
                assert found_faces == num_faces
