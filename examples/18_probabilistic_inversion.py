"""[ADVANCED / EXPERIMENTAL] Bayesian inference on a gempy model using Pyro.
Puts a prior on one surface point's (transformed-space) Z-coordinate,
forward-runs the gempy interpolator inside the probabilistic model, and uses
NUTS to infer a posterior from a single synthetic observation.

This deliberately depends only on pyro/torch plus gempy's own public
internals -- NOT on the `gempy_probability` package, whose PyPI release
(2024.1.1) is a near-empty shell; its real Pyro-based helpers only exist,
unreleased, on that package's `main` branch. This script reimplements the
core mechanics directly against gempy 2026.0.3 instead of depending on that
unstable package. Posterior plots use plain matplotlib rather than arviz --
arviz 1.2.0 dropped `from_pyro` (only `from_numpyro` remains), so pulling
it in for this alone isn't worth the dependency.

Requires: pip install -r requirements-optional.txt
This is the highest-risk script in the suite -- budget time to debug if the
underlying gempy_engine internals it touches have shifted since this was
written.

Unlike every other script in this suite, this one deliberately keeps its
tiny hand-crafted model rather than loading one of the real datasets under
examples/data/: the prior/forward/NUTS wiring below is indexed against a
specific surface point (index 0) and a specific custom-grid position (index
50), both tuned by hand against this exact geometry. Swapping in a larger
real dataset would shift those indices and risk silently breaking the
already-fragile autodiff chain for no benefit to what this script teaches."""
from pathlib import Path

import numpy as np
import gempy as gp

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

try:
    import torch
    import pyro
    import pyro.distributions as dist
    from pyro.infer import MCMC, NUTS
    from pyro.infer.autoguide import init_to_mean
except ImportError as e:
    raise SystemExit(
        f"Missing optional dependency '{e.name}'. Install with:\n"
        f"    pip install -r requirements-optional.txt"
    )

import matplotlib.pyplot as plt
import gempy_engine
from gempy_engine.core.backend_tensor import BackendTensor
from gempy.modules.data_manipulation import interpolation_input_from_structural_frame


def build_model():
    geo_model = gp.create_geomodel(
        project_name="Probabilistic_Demo",
        extent=[0, 1000, 0, 200, 0, 1000],
        resolution=[20, 5, 20],
        structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
    )
    geo_model.structural_frame.structural_elements[0].name = "rock1"
    gp.add_surface_points(geo_model=geo_model, x=[0, 500, 1000], y=[100, 100, 100],
                           z=[400, 500, 400], elements_names=["rock1"] * 3)
    gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[500],
                         elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    return geo_model


# grads=True (aka GemPyEngineConfig.compute_grads) is required for NUTS --
# the default (grads=False) enters a global torch.no_grad() context
# internally, which silently breaks autodiff between the sampled prior and
# gempy_engine's output. Every gp.compute_model call below must pass this
# same engine_config explicitly -- calling gp.compute_model without one
# defaults to a fresh numpy-backend GemPyEngineConfig() and silently resets
# the backend set here.
engine_config = gp.data.GemPyEngineConfig(
    backend=gp.data.AvailableBackends.PYTORCH, dtype="float64", compute_grads=True)
BackendTensor.change_backend_gempy(engine_backend=engine_config.backend,
                                    dtype=engine_config.dtype, grads=engine_config.compute_grads)
geo_model = build_model()

# A single vertical line of custom query points -- our synthetic "borehole".
query_points = np.array([[500.0, 100.0, z] for z in np.linspace(0, 1000, 100)])
gp.set_custom_grid(geo_model.grid, xyz_coord=query_points)
geo_model.grid.active_grids = gp.data.Grid.GridTypes.CUSTOM
gp.compute_model(geo_model, engine_config=engine_config)

# The prior lives in gempy's internal RESCALED coordinate space, not
# real-world meters -- this is the space add_surface_points' Z values get
# transformed into, and what interpolation_input_from_structural_frame
# operates on below.
prior_mean = torch.as_tensor(geo_model.surface_points_copy_transformed.xyz[0, 2], dtype=torch.float64)
prior = dist.Normal(loc=prior_mean, scale=torch.tensor(0.05, dtype=torch.float64))


def forward(z_sample, geo_model):
    interp_input = interpolation_input_from_structural_frame(geo_model)
    # sp_coords comes back as a plain numpy array regardless of the active
    # backend (structural_frame data is stored backend-agnostically) -- it
    # must be a tensor before torch.index_put will accept it.
    sp_coords = torch.as_tensor(interp_input.surface_points.sp_coords, dtype=torch.float64)
    interp_input.surface_points.sp_coords = torch.index_put(
        sp_coords,
        (torch.tensor([0]), torch.tensor([2])),
        z_sample.reshape(1),
    )
    return gempy_engine.compute_model(
        interpolation_input=interp_input,
        options=geo_model.interpolation_options,
        data_descriptor=geo_model.input_data_descriptor,
        geophysics_input=geo_model.geophysics_input,
    )


def pyro_model(geo_model, y_obs):
    z_top = pyro.sample("z_top", prior)
    solution = forward(z_top, geo_model)
    simulated = solution.octrees_output[0].last_output_center.custom_grid_values[50]
    pyro.sample("obs", dist.Normal(simulated, 0.2), obs=y_obs)


# A synthetic "observed" lithology value at the middle of the borehole.
y_obs = torch.tensor(1.3, dtype=torch.float64)

nuts_kernel = NUTS(pyro_model, init_strategy=init_to_mean)
mcmc = MCMC(nuts_kernel, num_samples=200, warmup_steps=50)
mcmc.run(geo_model, y_obs)

z_top_samples = mcmc.get_samples()["z_top"].detach().cpu().numpy()

fig, (ax_trace, ax_hist) = plt.subplots(1, 2, figsize=(10, 4))
ax_trace.plot(z_top_samples)
ax_trace.set_title("Trace: z_top")
ax_trace.set_xlabel("Sample")
ax_hist.hist(z_top_samples, bins=30)
ax_hist.set_title("Posterior: z_top")
ax_hist.set_xlabel("z_top (rescaled coordinate space)")
fig.tight_layout()
fig.savefig(OUTPUTS / "18_trace.png", dpi=150)

print("Posterior summary for z_top (gempy's internal rescaled coordinate space):")
print(f"  mean = {z_top_samples.mean():.5f}, std = {z_top_samples.std():.5f}")
