"""Two depositional series separated by an unconformity: a base layer
overlain by a "cover" layer. Toggling the cover group's StackRelationType
between ERODE and ONLAP shows the two classic unconformity relationships --
erosional truncation of what lies beneath versus onlap draping over existing
topography."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Unconformity",
    extent=[0, 1000, 0, 200, 0, 700],
    resolution=[50, 10, 50],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "rock1"

gp.add_surface_points(geo_model=geo_model, x=[0, 500, 1000], y=[100, 100, 100],
                       z=[200, 350, 200], elements_names=["rock1"] * 3)
gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[350],
                     elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])

color_gen = geo_model.structural_frame.color_generator
# The cover surface (flat at z=320) is placed BELOW the rock1 dome's peak
# (z=350) but above its flanks (z=200) so it actually intersects the dome --
# a flat cover sitting entirely above the dome's highest point would make
# ERODE and ONLAP produce identical results, since there'd be nothing for
# either relation to truncate or drape around.
cover = gp.data.StructuralElement(
    name="cover",
    color=next(color_gen),
    surface_points=gp.data.SurfacePointsTable.from_arrays(
        x=np.array([0, 1000]), y=np.array([100, 100]), z=np.array([320, 320]), names="cover"),
    orientations=gp.data.OrientationsTable.from_arrays(
        x=np.array([500]), y=np.array([100]), z=np.array([320]),
        G_x=np.array([0.0]), G_y=np.array([0.0]), G_z=np.array([1.0]), names="cover"),
)
cover_group = gp.data.StructuralGroup(
    name="Cover_Series", elements=[cover], structural_relation=gp.data.StackRelationType.ERODE)
geo_model.structural_frame.insert_group(0, cover_group)  # index 0 = youngest, cuts into rock1 below

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)
p_erode = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p_erode.fig.suptitle("StackRelationType.ERODE")
p_erode.fig.savefig(OUTPUTS / "05_erode.png", dpi=150)

geo_model.structural_frame.structural_groups[0].structural_relation = gp.data.StackRelationType.ONLAP
gp.compute_model(geo_model)
p_onlap = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p_onlap.fig.suptitle("StackRelationType.ONLAP")
p_onlap.fig.savefig(OUTPUTS / "05_onlap.png", dpi=150)
