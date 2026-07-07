"""Compare gempy's available RBF kernel functions (cubic, exponential,
matern_5_2) used to interpolate the geological scalar field, and inspect the
resulting kernel matrix condition number for each."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv
from gempy_engine.core.data.kernel_classes.kernel_functions import AvailableKernelFunctions

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)


def build_model():
    geo_model = gp.create_geomodel(
        project_name="Kernel_Demo",
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
