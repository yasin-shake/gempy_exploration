"""A deep dive into gempy_viewer's plot_3d: rendering static screenshots via
image=True/fig_path (useful for headless/automated runs), and checking which
pyvista plotter_type backends are actually implemented in this version."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Viz3D_Demo",
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
