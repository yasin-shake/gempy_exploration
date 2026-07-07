"""A single normal fault offsetting a flat rock layer. The layer's surface
points are supplied already "pre-offset" on each side of the fault plane --
that's the standard gempy convention: you provide the observed depths on
either side, and the fault machinery introduces the discontinuity itself."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="One_Fault",
    extent=[0, 1000, 0, 200, 0, 900],
    resolution=[50, 10, 50],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "rock1"
gp.add_surface_points(geo_model=geo_model, x=[0, 1000], y=[100, 100], z=[500, 300],
                       elements_names=["rock1", "rock1"])
gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[400],
                     elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])

color_gen = geo_model.structural_frame.color_generator
fault_elem = gp.data.StructuralElement(
    name="fault1",
    color=next(color_gen),
    surface_points=gp.data.SurfacePointsTable.from_arrays(
        x=np.array([500, 450]), y=np.array([50, 150]), z=np.array([700, 100]), names="fault1"),
    orientations=gp.data.OrientationsTable.from_arrays(
        x=np.array([475]), y=np.array([100]), z=np.array([400]),
        G_x=np.array([0.87]), G_y=np.array([0.0]), G_z=np.array([0.5]), names="fault1"),
)
fault_group = gp.data.StructuralGroup(
    name="Fault_Series", elements=[fault_elem], structural_relation=gp.data.StackRelationType.FAULT)
geo_model.structural_frame.insert_group(0, fault_group)
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
