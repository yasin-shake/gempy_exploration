"""A deep dive into gempy_viewer's plot_2d: multiple orthogonal slices
through the same model, and the various show_* toggles that control which
layers (lithology, scalar field, boundaries, raw data) appear on the plot.

Data: examples/data/jan_models/model2_surface_points.csv +
model2_orientations.csv -- the same real anticline dataset used by script 04,
loaded via ImporterHelper."""
from pathlib import Path

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

geo_model = gp.create_geomodel(
    project_name="Viz2D_Demo",
    extent=extent,
    resolution=[30, 30, 30],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model2_surface_points.csv"),
        path_to_orientations=str(DATA / "model2_orientations.csv"),
    ),
)
gp.map_stack_to_surfaces(gempy_model=geo_model, mapping_object={"Strat_Series": ("rock2", "rock1")})
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

# Two orthogonal slices through the same model in one figure.
p1 = gpv.plot_2d(geo_model, cell_number=[15, 15], direction=['x', 'y'], show=False)
p1.fig.savefig(OUTPUTS / "11_orthogonal_slices.png", dpi=150)

# The interpolated scalar field instead of discretized lithology.
p2 = gpv.plot_2d(geo_model, cell_number=['mid'], show_scalar=True, show_lith=False, show=False)
p2.fig.savefig(OUTPUTS / "11_scalar_field.png", dpi=150)

# Surface boundaries only, no raw input data, no filled lithology.
p3 = gpv.plot_2d(geo_model, cell_number=['mid'], show_boundaries=True,
                  show_lith=False, show_data=False, show=False)
p3.fig.savefig(OUTPUTS / "11_boundaries_only.png", dpi=150)
