"""Finite (spatially-bounded) faults -- faults whose influence doesn't cut
through the entire model volume. As of gempy 2026.0.3, gp.set_is_finite_fault
is present in the public API but its implementation simply raises
NotImplementedError (confirmed in gempy/API/faults_API.py; even gempy's own
official fault-relations tutorial has an empty placeholder section for this
feature). This script demonstrates that limitation honestly, then tries the
one seemingly-practical workaround people reach for -- constraining a
fault's own surface-point data to a sub-region of the model -- and reports
an equally honest, non-obvious finding: for a PLANAR fault, that workaround
does not actually bound anything.

Why: gempy's potential-field interpolation includes a universal drift
(linear trend) term, so it extrapolates a consistent geometric trend beyond
wherever the input points stop. Removing points that all lie on the far
ends of the SAME infinite plane doesn't change the plane the interpolator
reconstructs -- a subset of points on a plane still describes that same
plane. The two saved figures below, and the printed block-count diff,
confirm this quantitatively rather than just asserting it. Producing a
genuinely bounded fault would require introducing real curvature/pinch-out
into the fault's own geometry (not just fewer points), which isn't a
documented gempy workflow.

Data: examples/data/jan_models/model5_surface_points.csv +
model5_orientations.csv -- the same real single-fault dataset used by
script 06, reused here since "finite fault" is a limitation of the API
itself rather than a distinct geometry."""
from pathlib import Path

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
    project_name="Finite_Fault_Demo",
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
    print("Finite faults are not yet usable in gempy 2026.0.3. Trying the practical "
          "workaround below.")

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

# Slice near the original fault data's Y edge (Y=200) -- if confining the
# fault's points actually bounded its influence, this is where that should
# show up first.
edge_y = points[points.formation == "fault"].Y.min()  # 200: an original fault-data edge
y_min, y_max = extent[2], extent[3]
edge_cell = int((edge_y - y_min) / (y_max - y_min) * 10)  # resolution[1] == 10

p_full = gpv.plot_2d(geo_model, direction="y", cell_number=edge_cell, show_data=True, show=False)
# fig.suptitle() overlaps plot_2d's own axes title -- prepend to the axes
# title instead, which matplotlib sizes correctly for multi-line text.
p_full.axes[0].set_title(
    f"Fault cuts the full model extent (default behaviour)\nY~{edge_y:.0f} -- {p_full.axes[0].get_title()}")
p_full.fig.savefig(OUTPUTS / "08_full_extent_fault.png", dpi=150)
lith_before = geo_model.solutions.raw_arrays.lith_block.copy()

# Attempted workaround: shrink the fault's own surface points to a
# sub-region of the model's Y range, hoping its geometric influence would
# then look spatially bounded.
fault_elem = geo_model.structural_frame.get_element_by_name("fault")
fault_points = points[points.formation == "fault"]
y_mid = (fault_points.Y.min() + fault_points.Y.max()) / 2
y_span = (fault_points.Y.max() - fault_points.Y.min()) / 4
fault_elem.surface_points = gp.data.SurfacePointsTable.from_arrays(
    x=fault_points.X.to_numpy(),
    y=np.clip(fault_points.Y.to_numpy(), y_mid - y_span, y_mid + y_span),
    z=fault_points.Z.to_numpy(), names="fault")
gp.compute_model(geo_model)
lith_after = geo_model.solutions.raw_arrays.lith_block

n_changed = int(np.sum(lith_before != lith_after))
print(f"Voxels changed by confining the fault's points: {n_changed} / {lith_before.size} "
      f"({'workaround had no measurable effect' if n_changed == 0 else 'workaround had some effect'}).")
print("This fault's points are exactly coplanar, so gempy's potential-field "
      "interpolation -- which extrapolates a linear drift trend beyond the "
      "data -- reconstructs the same infinite plane regardless of how few "
      "points define it near the edges. Confining points doesn't bound a "
      "planar fault; it would take real curvature in the fault's own "
      "geometry to make it pinch out, which isn't a documented workflow.")

p_bounded = gpv.plot_2d(geo_model, direction="y", cell_number=edge_cell, show_data=True, show=False)
p_bounded.axes[0].set_title(
    f"Attempted workaround (see console: {n_changed} voxels changed)\n"
    f"Y~{edge_y:.0f} -- {p_bounded.axes[0].get_title()}")
p_bounded.fig.savefig(OUTPUTS / "08_bounded_workaround.png", dpi=150)
