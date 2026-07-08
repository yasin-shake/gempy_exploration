"""Topology analysis: compute the adjacency graph between distinct
geological bodies (here, the fault-separated blocks of a faulted two-layer
model) and visualize it both as an adjacency matrix and overlaid on a 2D
section. Not to be confused with script 10's topography (an elevation
surface) -- topology here means graph connectivity between rock volumes.

Data: examples/data/jan_models/model5_surface_points.csv +
model5_orientations.csv -- the same real single-fault dataset used by
script 06, loaded via ImporterHelper."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv
from gempy.core.data.options import InterpolationOptionsType
from gempy_plugins.topology_analysis import topology as tp

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

# create_geomodel's default interpolation options are octree-based even when
# a plain `resolution=` (dense grid) is requested -- that mismatch leaves the
# dense grid unpopulated internally and crashes compute_topology with
# "'NoneType' object has no attribute 'resolution'". Passing
# intpolation_options_tye=DENSE_GRID explicitly keeps grid type and
# interpolation options consistent, which topology analysis requires.
geo_model = gp.create_geomodel(
    project_name="Topology_Demo",
    extent=extent,
    resolution=[50, 10, 50],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model5_surface_points.csv"),
        path_to_orientations=str(DATA / "model5_orientations.csv"),
    ),
    intpolation_options_tye=InterpolationOptionsType.DENSE_GRID,
)
gp.map_stack_to_surfaces(
    gempy_model=geo_model,
    mapping_object={"Fault_Series": "fault", "Strat_Series": ("rock2", "rock1")},
)
geo_model.structural_frame.fault_relations = np.array([[0, 1], [0, 0]])
gp.set_is_fault(frame=geo_model, fault_groups=["Fault_Series"])

geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

edges, centroids = tp.compute_topology(geo_model)
adjacency = tp.get_adjacency_matrix(geo_model, edges, centroids)

tp.plot_adjacency_matrix(geo_model, adjacency)
# plot_adjacency_matrix sizes its own figure as (n // 2.5, n // 2.5) inches,
# where n is the lithology x fault-block count -- with this small a model
# that rounds down to a barely-visible figure, so force a readable size
# before saving.
plt.gcf().set_size_inches(6, 6)
plt.savefig(OUTPUTS / "13_adjacency_matrix.png", dpi=150, bbox_inches="tight")
plt.close("all")

p2d = gpv.plot_2d(geo_model, direction="y", cell_number="mid", show=False)
gpv.plot_topology(regular_grid=geo_model.grid.regular_grid, edges=edges,
                   centroids=centroids, ax=p2d.axes[0])
p2d.fig.savefig(OUTPUTS / "13_topology_graph.png", dpi=150)
