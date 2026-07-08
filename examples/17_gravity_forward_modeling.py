"""Forward-model the gravity response of a real subsurface density contrast,
evaluated at a line of real surface gravity-survey stations -- the basis of
gravity-based geophysical exploration and inversion.

Data: examples/data/tut_SandStone/SandStone_Points.csv +
SandStone_Foliations.csv, filtered to the "EarlyGranite" formation (the same
real dataset used by script 15), plus a real profile of stations subsampled
from Sst_grav_500.xyz -- gempy's own real gravity survey grid for this
deposit."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import gempy as gp

HERE = Path(__file__).parent
DATA = HERE / "data" / "tut_SandStone"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

points = pd.read_csv(DATA / "SandStone_Points.csv")
points = points[points.formation == "EarlyGranite"]
orientations = pd.read_csv(DATA / "SandStone_Foliations.csv")
orientations = orientations[orientations.formation == "EarlyGranite"]

pad_xy, pad_z = 2000, 200
extent = [
    points.X.min() - pad_xy, points.X.max() + pad_xy,
    points.Y.min() - pad_xy, points.Y.max() + pad_xy,
    points.Z.min() - pad_z, points.Z.max() + pad_z,
]


def _pole_vector(dip_deg, azimuth_deg):
    dip, az = np.radians(dip_deg), np.radians(azimuth_deg)
    return np.sin(dip) * np.sin(az), np.sin(dip) * np.cos(az), np.cos(dip)


geo_model = gp.create_geomodel(
    project_name="Gravity_Demo",
    extent=extent,
    resolution=[60, 30, 15],
    structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
)
geo_model.structural_frame.structural_elements[0].name = "EarlyGranite"
gp.add_surface_points(geo_model=geo_model, x=points.X.to_numpy(), y=points.Y.to_numpy(),
                       z=points.Z.to_numpy(), elements_names=["EarlyGranite"] * len(points))
gx, gy, gz = zip(*(_pole_vector(d, a) for d, a in zip(orientations.dip, orientations.azimuth)))
gp.add_orientations(
    geo_model=geo_model, x=orientations.X.to_numpy(), y=orientations.Y.to_numpy(),
    z=orientations.Z.to_numpy(), elements_names=["EarlyGranite"] * len(orientations),
    pole_vector=[np.array(v) for v in zip(gx, gy, gz)])
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)

# Real gravity survey stations, subsampled to a single profile line running
# through the geological data's footprint.
gravity_survey = pd.read_csv(DATA / "Sst_grav_500.xyz", sep=r"\s+", header=None,
                              names=["X", "Y", "idx", "gravity"])
in_footprint = gravity_survey[(gravity_survey.Y >= points.Y.min()) & (gravity_survey.Y <= points.Y.max())]
profile_y = sorted(in_footprint.Y.unique())[len(in_footprint.Y.unique()) // 2]
profile = in_footprint[in_footprint.Y == profile_y].sort_values("X").iloc[::4]
station_x = profile.X.to_numpy()
stations = np.stack([station_x, np.full_like(station_x, profile_y),
                      np.full_like(station_x, points.Z.max() + 50)], axis=1)

# radius must stay within the model's actual extent per axis -- a radius
# that overshoots the domain samples outside valid model space and produces
# an unphysical, jagged gravity profile.
gp.set_centered_grid(geo_model.grid, centers=stations,
                      resolution=np.array([20, 20, 25]), radius=np.array([15000, 5000, 300]))
gravity_gradient = gp.calculate_gravity_gradient(geo_model.grid.centered_grid)

gp.compute_model(geo_model)
lith_ids = np.unique(geo_model.solutions.raw_arrays.lith_block)
print(f"Lithology ids present in the model: {lith_ids} -- densities below are ordered to match.")

# Densities in g/cm^3, one per lithology id (EarlyGranite, basement).
geo_model.geophysics_input = gp.data.GeophysicsInput(
    tz=gravity_gradient, densities=np.array([2.61, 2.9]))
sol = gp.compute_model(geo_model, engine_config=gp.data.GemPyEngineConfig(
    backend=gp.data.AvailableBackends.numpy, dtype="float64"))

fig, ax = plt.subplots()
ax.plot(station_x, sol.gravity, ".-")
ax.set_xlabel("Station X position (m, real survey coordinates)")
ax.set_ylabel("Forward-modeled gravity (mGal)")
ax.set_title("Gravity profile across the real EarlyGranite body")
fig.savefig(OUTPUTS / "17_gravity_profile.png", dpi=150)
