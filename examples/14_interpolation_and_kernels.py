"""Compare gempy's available RBF kernel functions (cubic, exponential,
matern_5_2) used to interpolate the geological scalar field, and inspect the
resulting kernel matrix condition number for each.

Data: examples/data/jan_models/model2_surface_points.csv +
model2_orientations.csv -- the same real anticline dataset used by script 04,
loaded via ImporterHelper."""
from pathlib import Path

import pandas as pd
import gempy as gp
import gempy_viewer as gpv
from gempy_engine.core.data.kernel_classes.kernel_functions import AvailableKernelFunctions

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "model2_surface_points.csv")
pad_xy, pad_z = 150, 150
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]


def build_model():
    geo_model = gp.create_geomodel(
        project_name="Kernel_Demo",
        extent=extent,
        resolution=[30, 30, 30],
        importer_helper=gp.data.ImporterHelper(
            path_to_surface_points=str(DATA / "model2_surface_points.csv"),
            path_to_orientations=str(DATA / "model2_orientations.csv"),
        ),
    )
    gp.map_stack_to_surfaces(gempy_model=geo_model, mapping_object={"Strat_Series": ("rock2", "rock1")})
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    return geo_model


# gpv.plot_2d owns its own matplotlib figure (no ax= kwarg), so each kernel
# gets its own saved figure rather than being placed in a shared subplot grid.
for kernel in (AvailableKernelFunctions.cubic, AvailableKernelFunctions.exponential,
               AvailableKernelFunctions.matern_5_2):
    geo_model = build_model()
    geo_model.interpolation_options.kernel_options.kernel_function = kernel
    geo_model.interpolation_options.kernel_options.compute_condition_number = True
    gp.compute_model(geo_model)
    print(f"{kernel.name}: condition number = "
          f"{geo_model.interpolation_options.kernel_options.condition_number}")

    p = gpv.plot_2d(geo_model, cell_number=['mid'], show_scalar=True, show_lith=False, show=False)
    # fig.suptitle() overlaps plot_2d's own axes title -- prepend to the
    # axes title instead, which matplotlib sizes correctly for multi-line text.
    p.axes[0].set_title(f"{kernel.name}\n{p.axes[0].get_title()}")
    p.fig.savefig(OUTPUTS / f"14_kernel_{kernel.name}.png", dpi=150)
