"""Two near-vertical faults with opposing dip directions bounding a
six-layer stratigraphic pile -- the classic graben pattern, where the block
between the two faults drops down relative to the surrounding rock.
Demonstrates set_fault_relation's fault-fault interaction matrix, which is
required whenever more than one fault group exists.

Data: examples/data/lisa_models/interfaces7.csv + foliations7.csv -- gempy's
own real graben teaching dataset (Fault_1/Fault_2 plus six stratigraphic
formations), loaded via ImporterHelper. These files carry a few extra
bookkeeping columns (series, isFault, annotations, ...) beyond the minimal
X/Y/Z/formation schema -- ImporterHelper looks columns up by name, so the
extras are simply ignored."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "lisa_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "interfaces7.csv")
pad_xy, pad_z = 250, 300
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]

geo_model = gp.create_geomodel(
    project_name="Graben",
    extent=extent,
    resolution=[50, 10, 40],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "interfaces7.csv"),
        path_to_orientations=str(DATA / "foliations7.csv"),
    ),
)

# Six real stratigraphic formations, youngest (shallowest) to oldest
# (deepest), plus the two real graben-bounding faults.
gp.map_stack_to_surfaces(
    gempy_model=geo_model,
    mapping_object={
        "Fault_Series_1": "Fault_1",
        "Fault_Series_2": "Fault_2",
        "Strat_Series": ("Sandstone", "Siltstone", "Shale", "Sandstone_2", "Schist", "Gneiss"),
    },
)
gp.set_is_fault(frame=geo_model, fault_groups=["Fault_Series_1", "Fault_Series_2"])
gp.set_fault_relation(frame=geo_model.structural_frame,
                       rel_matrix=np.array([[0, 0, 1], [0, 0, 1], [0, 0, 0]]))

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p2d.fig.savefig(OUTPUTS / "07_graben_2d.png", dpi=150)
plt.close(p2d.fig)

# image=True renders off-screen and leaves the screenshot as the current
# matplotlib figure -- combining it with fig_path triggers a bug in
# gempy_viewer 2026.0.3 (plot_3d calls .show() twice on the same pyvista
# plotter and the second call raises RuntimeError), so save with
# plt.savefig afterward instead.
gpv.plot_3d(geo_model, show_data=True, image=True)
plt.savefig(OUTPUTS / "07_graben_3d.png", dpi=150)
plt.close("all")
