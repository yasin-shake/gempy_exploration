"""Minimal end-to-end gempy model: a single flat rock layer built from a
handful of surface points and one orientation measurement, interpolated and
plotted in 2D and 3D. This is the smallest complete gempy workflow and the
starting point for every other example in this suite."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Getting_Started",
    extent=[0, 780, -200, 200, -582, 0],
    resolution=(50, 50, 50),
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)

# initialize_default_structure() creates one element named "surface1" -- it
# must be renamed before add_surface_points/add_orientations reference a
# custom name, otherwise those calls raise ValueError.
geo_model.structural_frame.structural_elements[0].name = "Limestone"
geo_model.structural_frame.structural_elements[0].color = "#33ABFF"
geo_model.structural_frame.structural_groups[0].name = "Deposit_Series"

gp.add_surface_points(
    geo_model=geo_model,
    x=[225, 460, 617],
    y=[0, 0, 0],
    z=[-95, -100, -10],
    elements_names=["Limestone", "Limestone", "Limestone"],
)
gp.add_orientations(
    geo_model=geo_model,
    x=[350],
    y=[0],
    z=[-120],
    elements_names=["Limestone"],
    pole_vector=[np.array([0, 0, 1])],
)

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, cell_number="mid", show=False)
p2d.fig.savefig(OUTPUTS / "01_getting_started_2d.png", dpi=150)
plt.close(p2d.fig)

# image=True renders off-screen and leaves the screenshot as the current
# matplotlib figure. Combining image=True with fig_path triggers a bug in
# gempy_viewer 2026.0.3 (plot_3d ends up calling .show() twice on the same
# pyvista plotter, and the second call raises "This plotter has been closed
# and cannot be shown") -- so save via plt.savefig afterward instead.
gpv.plot_3d(geo_model, show_surfaces=True, image=True)
plt.savefig(OUTPUTS / "01_getting_started_3d.png", dpi=150)
plt.close("all")
