# Map-Overlay

Maps overlay algorithm as described in Computational Geometry: Algorithms and Applications by De Berg Mark, Cheong Otfried, Van Kreveld Marc, and Overmars Mark.

## Setting up the project

To get the project up and running, you need to clone the repository and navigate to the project directory.

```
git clone https://github.com/ManuelaCorte/Map-Overlay.git
cd Map-Overlay
```

The required dependencies can be installed using [Poetry](https://python-poetry.org/docs/). Once Poetry is installed, run the following command to install the dependencies:

```
poetry install --no-root
```

Alternatively, you can install the dependencies system-wise using pip:

```
pip install -r requirements.txt
```

## Running the project

First, you need to activate the virtual environment created by Poetry:

```
poetry shell
```

Then, you can run the project using the following command:

```
python -m src [--overlay] [--intersection] [--files FILES [FILES ...]] [--output OUTPUT] [--plot]
```

The arguments are as follows:

- `--intersection`: Compute the intersections using the sweep line algorithm.
- `--overlay`: Compute the overlay of the two maps.
- `--files FILES [FILES ...]`: The files containing the input. To run the intersection algorithm, one file is required. To run the overlay algorithm, two files are required. Some files are provided in the `data` directory.
- `--output OUTPUT`: The output directory wher the results will be saved. If not specified, the results won't be saved.
- `--plot`: Whether to plot the results or not. If not specified, the results won't be plotted.

For example, to compute the overlay of two maps and plot the results, you can run the following command:

```
python -m src --overlay --files "data/overlays/test_1.txt" "data/overlays/test_2.txt" --plot --save "data/results/"
```

To run the tests, you can simply run the following command:

```
pytest
```
