"""Configure gempy's various grid types: a small set of custom query points,
a vertical section grid, and a randomly-generated topography surface -- on
top of the default regular grid used for full 3D interpolation. Not to be
confused with script 13's topology (graph connectivity between rock bodies)
-- this script is about topography, an elevation surface.

Data: examples/data/jan_models/model1_surface_points.csv +
model1_orientations.csv -- gempy's own real two-flat-layer teaching model,
loaded via ImporterHelper. The topography surface itself stays synthetic
(set_topography_from_random): a real DEM can be loaded via
gp.set_topography_from_file, but that requires the optional `subsurface`
package, which this suite doesn't otherwise depend on."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "model1_surface_points.csv")
pad_xy = 150
x_min, x_max = points.X.min() - pad_xy, points.X.max() + pad_xy
y_min, y_max = points.Y.min() - pad_xy, points.Y.max() + pad_xy
z_min, z_top = points.Z.min() - 200, points.Z.max() + 400  # extra headroom above the data for topography

geo_model = gp.create_geomodel(
    project_name="Grids_Demo",
    extent=[x_min, x_max, y_min, y_max, z_min, z_top],
    resolution=[20, 20, 20],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model1_surface_points.csv"),
        path_to_orientations=str(DATA / "model1_orientations.csv"),
    ),
)
gp.map_stack_to_surfaces(gempy_model=geo_model, mapping_object={"Strat_Series": ("rock2", "rock1")})

x_mid, y_mid = (x_min + x_max) / 2, (y_min + y_max) / 2
z_mid = (points.Z.min() + points.Z.max()) / 2

# A handful of arbitrary query points, evaluated alongside the regular grid.
gp.set_custom_grid(geo_model.grid, xyz_coord=np.array([
    [x_min + pad_xy, y_min + pad_xy, z_mid],
    [x_mid, y_mid, z_mid],
    [x_max - pad_xy, y_max - pad_xy, z_mid]]))

# A vertical north-south cross-section.
gp.set_section_grid(grid=geo_model.grid, section_dict={
    "section_ns": ([x_mid, y_min], [x_mid, y_max], (100, 100))})

# Random fractal topography draped over the model.
gp.set_topography_from_random(
    grid=geo_model.grid, fractal_dimension=1.9,
    d_z=np.array([z_mid + 150, z_top]), topography_resolution=np.array([60, 60]))

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

gpv.plot_section_traces(geo_model)
plt.savefig(OUTPUTS / "10_section_traces.png", dpi=150)
plt.close("all")

p2d = gpv.plot_2d(geo_model, section_names=["section_ns", "topography"],
                   show_topography=True, show=False)
p2d.fig.savefig(OUTPUTS / "10_sections_and_topography.png", dpi=150)
