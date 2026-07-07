"""Topology analysis: compute the adjacency graph between distinct
geological bodies (here, the two fault-separated blocks of a faulted layer)
and visualize it both as an adjacency matrix and overlaid on a 2D section.
Not to be confused with script 10's topography (an elevation surface) --
topology here means graph connectivity between rock volumes."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp
import gempy_viewer as gpv
from gempy.core.data.options import InterpolationOptionsType
from gempy_plugins.topology_analysis import topology as tp

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

# create_geomodel's default interpolation options are octree-based even when
# a plain `resolution=` (dense grid) is requested -- that mismatch leaves the
# dense grid unpopulated internally and crashes compute_topology with
# "'NoneType' object has no attribute 'resolution'". Passing
# intpolation_options_tye=DENSE_GRID explicitly keeps grid type and
# interpolation options consistent, which topology analysis requires.
geo_model = gp.create_geomodel(
    project_name="Topology_Demo",
    extent=[0, 1000, 0, 20, 0, 1000],
    resolution=[50, 5, 50],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
    intpolation_options_tye=InterpolationOptionsType.DENSE_GRID,
)
geo_model.structural_frame.structural_elements[0].name = "surface1"
gp.add_surface_points(geo_model=geo_model, x=[0, 1000], y=[10, 10], z=[600, 600],
                       elements_names=["surface1", "surface1"])
gp.add_orientations(geo_model=geo_model, x=[500], y=[10], z=[600],
                     elements_names=["surface1"], pole_vector=[np.array([0, 0, 1])])

color_gen = geo_model.structural_frame.color_generator
fault_elem = gp.data.StructuralElement(
    name="fault1",
    color=next(color_gen),
    surface_points=gp.data.SurfacePointsTable.from_arrays(
        x=np.array([500, 500]), y=np.array([0, 20]), z=np.array([200, 800]), names="fault1"),
    orientations=gp.data.OrientationsTable.from_arrays(
        x=np.array([500]), y=np.array([10]), z=np.array([500]),
        G_x=np.array([1.0]), G_y=np.array([0.0]), G_z=np.array([0.0]), names="fault1"),
)
fault_group = gp.data.StructuralGroup(
    name="Fault_Series", elements=[fault_elem], structural_relation=gp.data.StackRelationType.FAULT)
geo_model.structural_frame.insert_group(0, fault_group)
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

p2d = gpv.plot_2d(geo_model, cell_number="mid", show=False)
gpv.plot_topology(regular_grid=geo_model.grid.regular_grid, edges=edges,
                   centroids=centroids, ax=p2d.axes[0])
p2d.fig.savefig(OUTPUTS / "13_topology_graph.png", dpi=150)
