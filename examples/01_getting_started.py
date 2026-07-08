"""Minimal end-to-end gempy model: a single flat rock layer built from real
surface points and orientation measurements, interpolated and plotted in 2D
and 3D. This is the smallest complete gempy workflow and the starting point
for every other example in this suite.

Data: examples/data/tut-ch1-7/onelayer_interfaces.csv +
onelayer_orient.csv -- gempy's own single-layer tutorial dataset (real
survey-style coordinates, formation "layer1")."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "tut-ch1-7"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "onelayer_interfaces.csv")
orientations = pd.read_csv(DATA / "onelayer_orient.csv")

# Pad the real data's coordinate range generously so the interpolated
# surface has room to curve within the model volume.
pad_xy, pad_z = 3000, 300
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]

geo_model = gp.create_geomodel(
    project_name="Getting_Started",
    extent=extent,
    resolution=(50, 50, 50),
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)

# initialize_default_structure() creates one element named "surface1" -- it
# must be renamed before add_surface_points/add_orientations reference a
# custom name, otherwise those calls raise ValueError. The real dataset's
# formation is called "layer1".
geo_model.structural_frame.structural_elements[0].name = "layer1"
geo_model.structural_frame.structural_elements[0].color = "#33ABFF"
geo_model.structural_frame.structural_groups[0].name = "Deposit_Series"

gp.add_surface_points(
    geo_model=geo_model,
    x=points.X.to_numpy(), y=points.Y.to_numpy(), z=points.Z.to_numpy(),
    elements_names=["layer1"] * len(points),
)
gp.add_orientations(
    geo_model=geo_model,
    x=orientations.X.to_numpy(), y=orientations.Y.to_numpy(), z=orientations.Z.to_numpy(),
    elements_names=["layer1"] * len(orientations),
    pole_vector=[np.array([0, 0, 1])] * len(orientations),
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
