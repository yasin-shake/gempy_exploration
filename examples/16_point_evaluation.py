"""Query an already-computed gempy model at arbitrary XYZ points, rather than
only reading values off the regular grid. Useful for evaluating a model along
a borehole trace or at specific sample locations."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Point_Eval_Demo",
    extent=[0, 1000, 0, 1000, 0, 1000],
    resolution=[30, 30, 30],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "surface1"
gp.add_surface_points(geo_model=geo_model, x=[100, 500, 900], y=[500, 500, 500],
                       z=[300, 600, 300], elements_names=["surface1"] * 3)
gp.add_orientations(geo_model=geo_model, x=[500], y=[500], z=[600],
                     elements_names=["surface1"], pole_vector=[np.array([0, 0, 1])])
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)  # full regular-grid solution, for reference

p2d = gpv.plot_2d(geo_model, cell_number=['mid'], show=False)
p2d.fig.savefig(OUTPUTS / "16_reference_model.png", dpi=150)

# compute_model_at replaces the model's active grids with a CUSTOM grid built
# from `at` as a side effect -- restore the regular grid afterward if further
# full-grid work follows.
query_points = np.array([[500, 500, 800], [500, 500, 600], [500, 500, 300]])
values_at_points = gp.compute_model_at(gempy_model=geo_model, at=query_points)
print("Interpolated lithology values at query points:")
for point, value in zip(query_points, values_at_points):
    print(f"  {point} -> {value}")

# This model was built with an explicit resolution=..., which creates a
# DENSE grid (not an octree one) -- restore to DENSE, matching however the
# model was actually built, not OCTREE.
gp.set_active_grid(geo_model.grid, [gp.data.Grid.GridTypes.DENSE], reset=True)
gp.compute_model(geo_model)
