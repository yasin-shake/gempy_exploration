"""Build a gempy model by hand, constructing StructuralElement/StructuralGroup/
StructuralFrame objects and SurfacePointsTable/OrientationsTable directly,
instead of using the add_surface_points/add_orientations convenience API. This
is the pattern to reach for when generating models programmatically.

Data: examples/data/jan_models/model1_surface_points.csv +
model1_orientations.csv -- gempy's own two-flat-layer teaching model
(real coordinates, formations "rock1"/"rock2"), read here with pandas and
fed into from_arrays() by hand rather than via ImporterHelper, to keep the
"manual construction" pattern this script demonstrates."""
from pathlib import Path

import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "model1_surface_points.csv")
orientations = pd.read_csv(DATA / "model1_orientations.csv")


def _pole_vector(dip_deg, azimuth_deg):
    dip, az = np.radians(dip_deg), np.radians(azimuth_deg)
    return np.sin(dip) * np.sin(az), np.sin(dip) * np.cos(az), np.cos(dip)


def _element(name, color_gen):
    sp = points[points.formation == name]
    ori = orientations[orientations.formation == name]
    gx, gy, gz = zip(*(_pole_vector(d, a) for d, a in zip(ori.dip, ori.azimuth)))
    return gp.data.StructuralElement(
        name=name,
        surface_points=gp.data.SurfacePointsTable.from_arrays(
            x=sp.X.to_numpy(), y=sp.Y.to_numpy(), z=sp.Z.to_numpy(), names=name),
        orientations=gp.data.OrientationsTable.from_arrays(
            x=ori.X.to_numpy(), y=ori.Y.to_numpy(), z=ori.Z.to_numpy(),
            G_x=np.array(gx), G_y=np.array(gy), G_z=np.array(gz), names=name),
        color=next(color_gen),
    )


color_gen = gp.data.ColorsGenerator()

# One SurfacePointsTable/OrientationsTable per element, each scoped to a
# single repeated name, keeps gempy's auto-generated point IDs aligned
# between the two tables -- mixing multiple element names into one
# from_arrays() call can silently desync IDs.
elem_lower = _element("rock1", color_gen)
elem_upper = _element("rock2", color_gen)

group = gp.data.StructuralGroup(
    name="Strat_Series",
    elements=[elem_upper, elem_lower],
    structural_relation=gp.data.StackRelationType.ERODE,
)
frame = gp.data.StructuralFrame(structural_groups=[group], color_gen=color_gen)

pad_xy, pad_z = 200, 200
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]
geo_model = gp.create_geomodel(
    project_name="Manual_Frame",
    extent=extent,
    resolution=[40, 40, 40],
    structural_frame=frame,
)
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

p2d = gpv.plot_2d(geo_model, cell_number="mid", show=False)
p2d.fig.savefig(OUTPUTS / "02_manual_structural_frame_2d.png", dpi=150)
