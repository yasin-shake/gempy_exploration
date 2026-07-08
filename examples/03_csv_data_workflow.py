"""Load real surface-points/orientations CSVs from disk through gempy's
ImporterHelper -- the pattern most real gempy projects use, where geological
data lives in CSV/spreadsheet form rather than being hard-coded in Python.

Data: examples/data/jan_models/model2_surface_points.csv +
model2_orientations.csv -- gempy's own anticline teaching dataset (formations
"rock1"/"rock2"), used unmodified straight off disk."""
from pathlib import Path

import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="CSV_Model",
    extent=[0, 1000, 0, 1000, 0, 1000],
    refinement=4,
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model2_surface_points.csv"),
        path_to_orientations=str(DATA / "model2_orientations.csv"),
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
