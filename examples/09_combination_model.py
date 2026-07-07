"""A capstone model combining three structural features covered separately
in scripts 05-07: a fault, an unconformity, and a folded multi-surface
series -- all in one geomodel, mirroring gempy's own official
g07_combination.py example. Demonstrates how independently-understood
features compose."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Combination",
    extent=[0, 1000, 0, 200, 0, 1000],
    resolution=[50, 10, 50],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)

color_gen = geo_model.structural_frame.color_generator

# Strat_Series2: a gentle anticline made of two conformable surfaces (rock1, rock2)
geo_model.structural_frame.structural_elements[0].name = "rock1"
gp.add_surface_points(geo_model=geo_model, x=[0, 250, 500, 750, 1000], y=[100] * 5,
                       z=[300, 380, 420, 380, 300], elements_names=["rock1"] * 5)
gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[420],
                     elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])

rock2 = gp.data.StructuralElement(
    name="rock2",
    color=next(color_gen),
    surface_points=gp.data.SurfacePointsTable.from_arrays(
        x=np.array([0, 250, 500, 750, 1000]), y=np.array([100] * 5),
        z=np.array([550, 630, 670, 630, 550]), names="rock2"),
    orientations=gp.data.OrientationsTable.initialize_empty(),
)
geo_model.structural_frame.structural_groups[0].elements.append(rock2)
geo_model.structural_frame.structural_groups[0].name = "Strat_Series2"

# Strat_Series1: rock3, a near-flat unconformity-bounded capping layer (ERODE)
rock3 = gp.data.StructuralElement(
    name="rock3",
    color=next(color_gen),
    surface_points=gp.data.SurfacePointsTable.from_arrays(
        x=np.array([0, 1000]), y=np.array([100, 100]), z=np.array([800, 800]), names="rock3"),
    orientations=gp.data.OrientationsTable.from_arrays(
        x=np.array([500]), y=np.array([100]), z=np.array([800]),
        G_x=np.array([0.0]), G_y=np.array([0.0]), G_z=np.array([1.0]), names="rock3"),
)
cap_group = gp.data.StructuralGroup(
    name="Strat_Series1", elements=[rock3], structural_relation=gp.data.StackRelationType.ERODE)
geo_model.structural_frame.insert_group(0, cap_group)

# Fault_Series: a fault cutting through the left side of the model
fault_elem = gp.data.StructuralElement(
    name="fault",
    color=next(color_gen),
    surface_points=gp.data.SurfacePointsTable.from_arrays(
        x=np.array([300, 260]), y=np.array([50, 150]), z=np.array([950, 50]), names="fault"),
    orientations=gp.data.OrientationsTable.from_arrays(
        x=np.array([280]), y=np.array([100]), z=np.array([500]),
        G_x=np.array([0.87]), G_y=np.array([0.0]), G_z=np.array([0.5]), names="fault"),
)
fault_group = gp.data.StructuralGroup(
    name="Fault_Series", elements=[fault_elem], structural_relation=gp.data.StackRelationType.FAULT)
geo_model.structural_frame.insert_group(0, fault_group)

geo_model.structural_frame.fault_relations = np.array([
    [0, 1, 1],
    [0, 0, 0],
    [0, 0, 0],
])
gp.set_is_fault(frame=geo_model, fault_groups=["Fault_Series"])

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p2d.fig.savefig(OUTPUTS / "09_combination_2d.png", dpi=150)
plt.close(p2d.fig)

# image=True renders off-screen and leaves the screenshot as the current
# matplotlib figure -- combining it with fig_path triggers a bug in
# gempy_viewer 2026.0.3 (plot_3d calls .show() twice on the same pyvista
# plotter and the second call raises RuntimeError), so save with
# plt.savefig afterward instead.
gpv.plot_3d(geo_model, show_data=True, image=True)
plt.savefig(OUTPUTS / "09_combination_3d.png", dpi=150)
plt.close("all")
