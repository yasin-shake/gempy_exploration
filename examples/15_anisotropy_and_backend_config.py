"""Compare gempy's global anisotropy transforms (CUBE vs NONE) and its two
computation backends (numpy vs PyTorch)."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)


def build_model():
    # A deliberately elongated (4:1) extent -- on a perfectly cubic extent,
    # GlobalAnisotropy.CUBE has nothing to normalize and looks identical to
    # NONE. Stretching X relative to Z is what makes the two visibly differ:
    # CUBE rescales all axes into a unit cube before interpolating (so the
    # kriging kernel's range is isotropic in rescaled space), while NONE
    # interpolates directly in the elongated coordinate system.
    geo_model = gp.create_geomodel(
        project_name="Anisotropy_Demo",
        extent=[0, 2000, 0, 200, 0, 500],
        resolution=[60, 10, 30],
        structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
    )
    geo_model.structural_frame.structural_elements[0].name = "surface1"
    gp.add_surface_points(geo_model=geo_model, x=[200, 1000, 1800], y=[100, 100, 100],
                           z=[150, 350, 150], elements_names=["surface1"] * 3)
    gp.add_orientations(geo_model=geo_model, x=[1000], y=[100], z=[350],
                         elements_names=["surface1"], pole_vector=[np.array([0, 0, 1])])
    return geo_model


# MANUAL anisotropy needs an additional anisotropy_limit whose exact shape
# isn't well documented, so only CUBE and NONE are demonstrated here.
for mode in (gp.data.GlobalAnisotropy.CUBE, gp.data.GlobalAnisotropy.NONE):
    geo_model = build_model()
    geo_model.update_transform(mode)
    gp.compute_model(geo_model)
    p = gpv.plot_2d(geo_model, cell_number=['mid'], show=False)
    # fig.suptitle() overlaps plot_2d's own axes title -- prepend to the
    # axes title instead, which matplotlib sizes correctly for multi-line text.
    p.axes[0].set_title(f"GlobalAnisotropy.{mode.name}\n{p.axes[0].get_title()}")
    p.fig.savefig(OUTPUTS / f"15_anisotropy_{mode.name}.png", dpi=150)

# Compare backends. use_gpu is left False for portability across machines.
model_numpy = build_model()
model_numpy.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(model_numpy, engine_config=gp.data.GemPyEngineConfig(
    backend=gp.data.AvailableBackends.numpy, dtype="float64"))
print("numpy backend: computed OK")

model_torch = build_model()
model_torch.update_transform(gp.data.GlobalAnisotropy.NONE)
try:
    gp.compute_model(model_torch, engine_config=gp.data.GemPyEngineConfig(
        backend=gp.data.AvailableBackends.PYTORCH, dtype="float32", use_gpu=False))
    print("PyTorch backend: computed OK")
except ImportError as e:
    print(f"PyTorch backend unavailable ({e}); install torch to try it "
          f"(see requirements-optional.txt).")
