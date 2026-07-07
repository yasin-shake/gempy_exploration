"""Two near-vertical faults with opposing dip directions bounding a flat
layer -- the classic graben pattern, where the block between the two faults
drops down relative to the surrounding rock. Demonstrates
set_fault_relation's fault-fault interaction matrix, which is required
whenever more than one fault group exists."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Graben",
    extent=[0, 1000, 0, 200, 0, 500],
    resolution=[50, 10, 30],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "rock1"
gp.add_surface_points(geo_model=geo_model, x=[0, 1000], y=[100, 100], z=[300, 300],
                       elements_names=["rock1", "rock1"])
gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[300],
                     elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])

color_gen = geo_model.structural_frame.color_generator


def make_fault(name, x_pts, z_pts, dip_deg, azimuth_deg):
    dip, az = np.radians(dip_deg), np.radians(azimuth_deg)
    return gp.data.StructuralElement(
        name=name,
        color=next(color_gen),
        surface_points=gp.data.SurfacePointsTable.from_arrays(
            x=np.array(x_pts), y=np.array([50, 150]), z=np.array(z_pts), names=name),
        orientations=gp.data.OrientationsTable.from_arrays(
            x=np.array([np.mean(x_pts)]), y=np.array([100]), z=np.array([np.mean(z_pts)]),
            G_x=np.array([np.sin(dip) * np.sin(az)]),
            G_y=np.array([0.0]),
            G_z=np.array([np.cos(dip)]),
            names=name),
    )


fault_left = make_fault("fault_left", [350, 380], [450, 50], dip_deg=75, azimuth_deg=90)
fault_right = make_fault("fault_right", [650, 620], [450, 50], dip_deg=75, azimuth_deg=270)

geo_model.structural_frame.insert_group(0, gp.data.StructuralGroup(
    name="Fault_Series_1", elements=[fault_left], structural_relation=gp.data.StackRelationType.FAULT))
geo_model.structural_frame.insert_group(1, gp.data.StructuralGroup(
    name="Fault_Series_2", elements=[fault_right], structural_relation=gp.data.StackRelationType.FAULT))

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
