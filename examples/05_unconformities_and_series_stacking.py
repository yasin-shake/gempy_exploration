"""Two depositional series separated by an unconformity: a folded base pair
overlain by a near-flat "cover" layer. Toggling the cover group's
StackRelationType between ERODE and ONLAP shows the two classic unconformity
relationships -- erosional truncation of what lies beneath versus onlap
draping over existing topography.

Data: examples/data/jan_models/model6_surface_points.csv +
model6_orientations.csv -- gempy's own real unconformity teaching dataset
(a folded rock1/rock2 pair capped by a near-flat rock3), loaded via
ImporterHelper."""
from pathlib import Path

import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "model6_surface_points.csv")
pad_xy, pad_z = 150, 100
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]

geo_model = gp.create_geomodel(
    project_name="Unconformity",
    extent=extent,
    resolution=[50, 10, 50],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model6_surface_points.csv"),
        path_to_orientations=str(DATA / "model6_orientations.csv"),
    ),
)
gp.map_stack_to_surfaces(
    gempy_model=geo_model,
    mapping_object={"Cover_Series": "rock3", "Strat_Series": ("rock2", "rock1")},
)
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)

# Cover_Series (index 0 = youngest) starts out ERODE by default -- compute
# once for each relation and compare.
geo_model.structural_frame.structural_groups[0].structural_relation = gp.data.StackRelationType.ERODE
gp.compute_model(geo_model)
p_erode = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p_erode.axes[0].set_title(f"StackRelationType.ERODE\n{p_erode.axes[0].get_title()}")
p_erode.fig.savefig(OUTPUTS / "05_erode.png", dpi=150)

geo_model.structural_frame.structural_groups[0].structural_relation = gp.data.StackRelationType.ONLAP
gp.compute_model(geo_model)
p_onlap = gpv.plot_2d(geo_model, direction="y", show_data=True, show=False)
p_onlap.axes[0].set_title(f"StackRelationType.ONLAP\n{p_onlap.axes[0].get_title()}")
p_onlap.fig.savefig(OUTPUTS / "05_onlap.png", dpi=150)
