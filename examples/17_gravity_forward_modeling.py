"""Forward-model the gravity response of a simple single-layer subsurface
density model, evaluated at a line of synthetic surface stations -- the
basis of gravity-based geophysical exploration and inversion."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import gempy as gp

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="Gravity_Demo",
    extent=[0, 1000, 0, 200, 0, 1000],
    resolution=[60, 15, 60],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "rock1"
gp.add_surface_points(geo_model=geo_model, x=[0, 500, 1000], y=[100, 100, 100],
                       z=[400, 550, 400], elements_names=["rock1"] * 3)
gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[550],
                     elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)

station_x = np.linspace(50, 950, 20)
stations = np.stack(
    [station_x, np.full_like(station_x, 100), np.full_like(station_x, 1000)], axis=1)
# radius must stay within the model's actual extent per axis (here
# 1000 x 200 x 1000) -- a radius that overshoots the domain (e.g. 1000 on
# the 200-wide Y axis) samples outside valid model space and produces an
# unphysical, jagged gravity profile.
gp.set_centered_grid(geo_model.grid, centers=stations,
                      resolution=np.array([20, 20, 25]), radius=np.array([500, 100, 500]))
gravity_gradient = gp.calculate_gravity_gradient(geo_model.grid.centered_grid)

gp.compute_model(geo_model)
lith_ids = np.unique(geo_model.solutions.raw_arrays.lith_block)
print(f"Lithology ids present in the model: {lith_ids} -- densities below are ordered to match.")

# Densities in g/cm^3, one per lithology id (rock1, basement).
geo_model.geophysics_input = gp.data.GeophysicsInput(
    tz=gravity_gradient, densities=np.array([2.4, 2.9]))
sol = gp.compute_model(geo_model, engine_config=gp.data.GemPyEngineConfig(
    backend=gp.data.AvailableBackends.numpy, dtype="float64"))

fig, ax = plt.subplots()
ax.plot(station_x, sol.gravity, ".-")
ax.set_xlabel("Station X position (m)")
ax.set_ylabel("Forward-modeled gravity (mGal)")
ax.set_title("Synthetic gravity profile across a buried density contrast")
fig.savefig(OUTPUTS / "17_gravity_profile.png", dpi=150)
