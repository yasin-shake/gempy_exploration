"""Configure gempy's various grid types: a small set of custom query points,
a vertical section grid, and a randomly-generated topography surface -- on
top of the default regular grid used for full 3D interpolation. Not to be
confused with script 13's topology (graph connectivity between rock bodies)
-- this script is about topography, an elevation surface."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Grids_Demo",
    extent=[0, 1000, 0, 1000, 0, 1000],
    resolution=[20, 20, 20],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "surface1"
gp.add_surface_points(geo_model=geo_model, x=[100, 900], y=[500, 500], z=[500, 500],
                       elements_names=["surface1", "surface1"])
gp.add_orientations(geo_model=geo_model, x=[500], y=[500], z=[500],
                     elements_names=["surface1"], pole_vector=[np.array([0, 0, 1])])

# A handful of arbitrary query points, evaluated alongside the regular grid.
gp.set_custom_grid(geo_model.grid, xyz_coord=np.array([
    [100, 100, 500], [500, 500, 500], [900, 900, 500]]))

# A vertical north-south cross-section.
gp.set_section_grid(grid=geo_model.grid, section_dict={
    "section_ns": ([500, 0], [500, 1000], [100, 100])})

# Random fractal topography draped over the model.
gp.set_topography_from_random(
    grid=geo_model.grid, fractal_dimension=1.9,
    d_z=np.array([700, 1000]), topography_resolution=np.array([60, 60]))

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

gpv.plot_section_traces(geo_model)
plt.savefig(OUTPUTS / "10_section_traces.png", dpi=150)
plt.close("all")

p2d = gpv.plot_2d(geo_model, section_names=["section_ns", "topography"],
                   show_topography=True, show=False)
p2d.fig.savefig(OUTPUTS / "10_sections_and_topography.png", dpi=150)
