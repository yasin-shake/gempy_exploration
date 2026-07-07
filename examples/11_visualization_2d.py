"""A deep dive into gempy_viewer's plot_2d: multiple orthogonal slices
through the same model, and the various show_* toggles that control which
layers (lithology, scalar field, boundaries, raw data) appear on the plot."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Viz2D_Demo",
    extent=[0, 1000, 0, 1000, 0, 1000],
    resolution=[30, 30, 30],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "surface1"
gp.add_surface_points(geo_model=geo_model, x=[100, 500, 900], y=[500, 500, 500],
                       z=[300, 600, 300], elements_names=["surface1"] * 3)
gp.add_orientations(geo_model=geo_model, x=[500], y=[500], z=[600],
                     elements_names=["surface1"], pole_vector=[np.array([0, 0, 1])])
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

# Two orthogonal slices through the same model in one figure.
p1 = gpv.plot_2d(geo_model, cell_number=[15, 15], direction=['x', 'y'], show=False)
p1.fig.savefig(OUTPUTS / "11_orthogonal_slices.png", dpi=150)

# The interpolated scalar field instead of discretized lithology.
p2 = gpv.plot_2d(geo_model, cell_number=['mid'], show_scalar=True, show_lith=False, show=False)
p2.fig.savefig(OUTPUTS / "11_scalar_field.png", dpi=150)

# Surface boundaries only, no raw input data, no filled lithology.
p3 = gpv.plot_2d(geo_model, cell_number=['mid'], show_boundaries=True,
                  show_lith=False, show_data=False, show=False)
p3.fig.savefig(OUTPUTS / "11_boundaries_only.png", dpi=150)
