"""Finite (spatially-bounded) faults -- faults whose influence doesn't cut
through the entire model volume. As of gempy 2026.0.3, gp.set_is_finite_fault
is present in the public API but its implementation simply raises
NotImplementedError (confirmed in gempy/API/faults_API.py; even gempy's own
official fault-relations tutorial has an empty placeholder section for this
feature). This script demonstrates that limitation honestly, explains the
underlying concept, and shows the one practically-supported workaround:
constraining a fault's own surface-point data to a sub-region of the model
so its visible influence looks spatially bounded. This is NOT a true
finite-fault ellipsoid -- just the closest approximation available today."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Finite_Fault_Demo",
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

# The "real" finite-fault API -- currently unimplemented upstream. Caught
# broadly (not just NotImplementedError) since the exact failure mode of an
# unstable/experimental upstream call isn't guaranteed across versions; the
# point of this probe is to show the reader exactly what happens if they try.
try:
    gp.set_is_finite_fault(geo_model.structural_frame, series_fault=["Fault_Series"], toggle=True)
    print("set_is_finite_fault ran without error (unexpected for gempy 2026.0.3 -- "
          "check whether upstream has implemented it since this script was written).")
except Exception as e:
    print(f"gp.set_is_finite_fault raised {type(e).__name__}: {e}")
    print("Finite faults are not yet usable in gempy 2026.0.3. Falling back to the "
          "practical workaround below.")

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)
p_full = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
# fig.suptitle() overlaps plot_2d's own axes title -- prepend to the axes
# title instead, which matplotlib sizes correctly for multi-line text.
p_full.axes[0].set_title(f"Fault cuts the full model extent (default behaviour)\n{p_full.axes[0].get_title()}")
p_full.fig.savefig(OUTPUTS / "08_full_extent_fault.png", dpi=150)

# Workaround: shrink the fault's own surface points to a sub-region of the
# model's Y range so its geometric influence looks spatially bounded. This
# is an approximation of a finite fault, not a true bounded ellipsoid.
fault_elem.surface_points = gp.data.SurfacePointsTable.from_arrays(
    x=np.array([500, 450]), y=np.array([70, 130]), z=np.array([650, 200]), names="fault1")
gp.compute_model(geo_model)
p_bounded = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p_bounded.axes[0].set_title(
    f"Workaround: fault data confined to a sub-region (not a true finite fault)\n{p_bounded.axes[0].get_title()}")
p_bounded.fig.savefig(OUTPUTS / "08_bounded_workaround.png", dpi=150)
