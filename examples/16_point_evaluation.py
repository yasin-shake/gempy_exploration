"""Query an already-computed gempy model at arbitrary XYZ points, rather than
only reading values off the regular grid. Useful for evaluating a model along
a borehole trace or at specific sample locations.

Data: examples/data/jan_models/model2_surface_points.csv +
model2_orientations.csv -- the same real anticline dataset used by script 04,
loaded via ImporterHelper."""
from pathlib import Path

import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "model2_surface_points.csv")
pad_xy, pad_z = 150, 150
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]
x_mid, y_mid = (points.X.min() + points.X.max()) / 2, (points.Y.min() + points.Y.max()) / 2

geo_model = gp.create_geomodel(
    project_name="Point_Eval_Demo",
    extent=extent,
    resolution=[30, 30, 30],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model2_surface_points.csv"),
        path_to_orientations=str(DATA / "model2_orientations.csv"),
    ),
)
gp.map_stack_to_surfaces(gempy_model=geo_model, mapping_object={"Strat_Series": ("rock2", "rock1")})
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)  # full regular-grid solution, for reference

p2d = gpv.plot_2d(geo_model, cell_number=['mid'], show=False)
p2d.fig.savefig(OUTPUTS / "16_reference_model.png", dpi=150)

# compute_model_at replaces the model's active grids with a CUSTOM grid built
# from `at` as a side effect -- restore the regular grid afterward if further
# full-grid work follows. Query a vertical line through the middle of the
# dome, from near the top surface down into the lower rock1 layer.
query_points = np.array([
    [x_mid, y_mid, points.Z.max() - 50],
    [x_mid, y_mid, (points.Z.min() + points.Z.max()) / 2],
    [x_mid, y_mid, points.Z.min() + 50],
])
values_at_points = gp.compute_model_at(gempy_model=geo_model, at=query_points)
print("Interpolated lithology values at query points:")
for point, value in zip(query_points, values_at_points):
    print(f"  {point} -> {value}")

# This model was built with an explicit resolution=..., which creates a
# DENSE grid (not an octree one) -- restore to DENSE, matching however the
# model was actually built, not OCTREE.
gp.set_active_grid(geo_model.grid, [gp.data.Grid.GridTypes.DENSE], reset=True)
gp.compute_model(geo_model)
