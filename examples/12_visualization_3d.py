"""A deep dive into gempy_viewer's plot_3d: rendering static screenshots via
image=True/fig_path (useful for headless/automated runs), and checking which
pyvista plotter_type backends are actually implemented in this version.

Data: examples/data/jan_models/model2_surface_points.csv +
model2_orientations.csv -- the same real anticline dataset used by script 04,
loaded via ImporterHelper."""
from pathlib import Path

import matplotlib.pyplot as plt
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
    project_name="Viz3D_Demo",
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

# image=True renders off-screen and leaves the screenshot as the current
# matplotlib figure -- the cleanest way to get a 3D view without a blocking
# interactive window. Note: combining image=True with the fig_path kwarg
# triggers a bug in gempy_viewer 2026.0.3 (plot_3d ends up calling .show()
# twice on the same pyvista plotter and the second call raises RuntimeError),
# so fig_path is deliberately not used here -- save with plt.savefig instead.
gpv.plot_3d(geo_model, show=True, image=True)
plt.savefig(OUTPUTS / "12_static_screenshot.png", dpi=150)
plt.close("all")

# Only 'basic' is actually implemented in gempy_viewer 2026.0.3; 'background'
# and 'notebook' both raise NotImplementedError. Checked here WITHOUT
# image=True, because image=True silently forces plotter_type='basic' before
# this check would ever run, hiding the very thing being demonstrated.
for plotter_type in ("basic", "background", "notebook"):
    try:
        gpv.plot_3d(geo_model, plotter_type=plotter_type, show=False)
        print(f"plotter_type={plotter_type!r}: OK")
    except NotImplementedError:
        print(f"plotter_type={plotter_type!r}: not implemented in this gempy_viewer version")
