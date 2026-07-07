"""Build a gempy model by hand, constructing StructuralElement/StructuralGroup/
StructuralFrame objects and SurfacePointsTable/OrientationsTable directly,
instead of using the add_surface_points/add_orientations convenience API. This
is the pattern to reach for when generating models programmatically."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

color_gen = gp.data.ColorsGenerator()

# One SurfacePointsTable/OrientationsTable per element, each scoped to a
# single repeated name, keeps gempy's auto-generated point IDs aligned
# between the two tables -- mixing multiple element names into one
# from_arrays() call can silently desync IDs.
sp_lower = gp.data.SurfacePointsTable.from_arrays(
    x=np.array([0, 500, 1000]), y=np.array([500, 500, 500]),
    z=np.array([200, 200, 200]), names="rock1")
elem_lower = gp.data.StructuralElement(
    name="rock1",
    surface_points=sp_lower,
    orientations=gp.data.OrientationsTable.from_arrays(
        x=np.array([500]), y=np.array([500]), z=np.array([200]),
        G_x=np.array([0.0]), G_y=np.array([0.0]), G_z=np.array([1.0]), names="rock1"),
    color=next(color_gen),
)

sp_upper = gp.data.SurfacePointsTable.from_arrays(
    x=np.array([0, 500, 1000]), y=np.array([500, 500, 500]),
    z=np.array([400, 400, 400]), names="rock2")
elem_upper = gp.data.StructuralElement(
    name="rock2",
    surface_points=sp_upper,
    orientations=gp.data.OrientationsTable.initialize_empty(),
    color=next(color_gen),
)

group = gp.data.StructuralGroup(
    name="Strat_Series",
    elements=[elem_upper, elem_lower],
    structural_relation=gp.data.StackRelationType.ERODE,
)
frame = gp.data.StructuralFrame(structural_groups=[group], color_gen=color_gen)

geo_model = gp.create_geomodel(
    project_name="Manual_Frame",
    extent=[0, 1000, 0, 1000, 0, 600],
    resolution=[40, 40, 40],
    structural_frame=frame,
)
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, cell_number="mid", show=False)
p2d.fig.savefig(OUTPUTS / "02_manual_structural_frame_2d.png", dpi=150)
