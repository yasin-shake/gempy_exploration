"""Write small synthetic surface-points/orientations CSVs to disk and load
them back through gempy's ImporterHelper -- the pattern most real gempy
projects use, where geological data lives in CSV/spreadsheet form rather
than being hard-coded in Python."""
from pathlib import Path

import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data"
OUTPUTS = HERE / "outputs"
DATA.mkdir(exist_ok=True, parents=True)
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.DataFrame({
    "X": [0, 500, 1000, 0, 500, 1000],
    "Y": [500] * 6,
    "Z": [200, 250, 300, 500, 550, 600],
    "formation": ["rock1"] * 3 + ["rock2"] * 3,
})
points.to_csv(DATA / "points.csv", index=False)

orientations = pd.DataFrame({
    "X": [500], "Y": [500], "Z": [200],
    "azimuth": [90], "dip": [5], "polarity": [1],
    "formation": ["rock1"],
})
orientations.to_csv(DATA / "orientations.csv", index=False)

geo_model = gp.create_geomodel(
    project_name="CSV_Model",
    extent=[0, 1000, 0, 1000, 0, 700],
    refinement=4,
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "points.csv"),
        path_to_orientations=str(DATA / "orientations.csv"),
    ),
)

# CSV-loaded models land in a single auto-created "default_formation" group --
# map_stack_to_surfaces is mandatory here, not optional, to split rock1/rock2
# into a real series.
gp.map_stack_to_surfaces(
    gempy_model=geo_model,
    mapping_object={"Strat_Series": ("rock2", "rock1")},
)
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, cell_number="mid", show=False)
p2d.fig.savefig(OUTPUTS / "03_csv_data_workflow_2d.png", dpi=150)
