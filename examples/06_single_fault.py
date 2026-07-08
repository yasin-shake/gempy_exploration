"""A single normal fault offsetting two rock layers. The layer's surface
points are supplied already "pre-offset" on each side of the fault plane --
that's the standard gempy convention: you provide the observed depths on
either side, and the fault machinery introduces the discontinuity itself.

Data: examples/data/jan_models/model5_surface_points.csv +
model5_orientations.csv -- gempy's own real single-fault teaching dataset
(formations "rock1"/"rock2" plus a "fault" surface), loaded via
ImporterHelper."""
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

points = pd.read_csv(DATA / "model5_surface_points.csv")
pad_xy, pad_z = 150, 150
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]

geo_model = gp.create_geomodel(
    project_name="One_Fault",
    extent=extent,
    resolution=[50, 10, 50],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model5_surface_points.csv"),
        path_to_orientations=str(DATA / "model5_orientations.csv"),
    ),
)
gp.map_stack_to_surfaces(
    gempy_model=geo_model,
    mapping_object={"Fault_Series": "fault", "Strat_Series": ("rock2", "rock1")},
)
geo_model.structural_frame.fault_relations = np.array([[0, 1], [0, 0]])
gp.set_is_fault(frame=geo_model, fault_groups=["Fault_Series"])

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p2d.fig.savefig(OUTPUTS / "06_single_fault_2d.png", dpi=150)
plt.close(p2d.fig)

# image=True renders off-screen and leaves the screenshot as the current
# matplotlib figure -- combining it with fig_path triggers a bug in
# gempy_viewer 2026.0.3 (plot_3d calls .show() twice on the same pyvista
# plotter and the second call raises RuntimeError), so save with
# plt.savefig afterward instead.
gpv.plot_3d(geo_model, show_data=True, show_boundaries=True, show_lith=True, image=True)
plt.savefig(OUTPUTS / "06_single_fault_3d.png", dpi=150)
plt.close("all")
