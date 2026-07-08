"""Three ways to persist a computed gempy model: (1) a genuine JSON
round-trip via JsonIO (geometry/configuration only), (2) gempy's own binary
.gempy save format (still marked "in development" upstream), and (3)
exporting computed surface meshes to VTK via pyvista for use in other 3D
tools.

Data: examples/data/jan_models/model2_surface_points.csv +
model2_orientations.csv -- the same real anticline dataset used by script 04,
loaded via ImporterHelper."""
from pathlib import Path

import numpy as np
import pandas as pd
import gempy as gp
import pyvista as pv
from gempy.modules.json_io import JsonIO

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

geo_model = gp.create_geomodel(
    project_name="IO_Demo",
    extent=extent,
    resolution=[30, 30, 30],
    importer_helper=gp.data.ImporterHelper(
        path_to_surface_points=str(DATA / "model2_surface_points.csv"),
        path_to_orientations=str(DATA / "model2_orientations.csv"),
    ),
)
gp.map_stack_to_surfaces(gempy_model=geo_model, mapping_object={"Strat_Series": ("rock2", "rock1")})
geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
gp.compute_model(geo_model)

# 1. Genuine JSON round-trip -- geometry/config only, no cached solution, so
# recompute after loading.
json_path = str(OUTPUTS / "19_model.json")
JsonIO.save_model_to_json(geo_model, json_path)
reloaded = JsonIO.load_model_from_json(json_path)
gp.compute_model(reloaded)
print(f"JSON round-trip OK: reloaded model has "
      f"{len(reloaded.structural_frame.structural_elements)} structural element(s).")

# 2. gempy's own binary save/load format. Both emit a "still in development"
# warning upstream -- treat as a convenience snapshot, not a stable format.
gempy_path = gp.save_model(geo_model, path=str(OUTPUTS / "19_model.gempy"))
reloaded_binary = gp.load_model(gempy_path)
print(f"Binary .gempy round-trip OK: saved to {gempy_path}")

# 3. Export each computed surface as a VTK mesh via pyvista.
for element in geo_model.structural_frame.structural_elements:
    if element.vertices is None or len(element.vertices) == 0:
        continue
    faces = np.hstack([np.full((element.edges.shape[0], 1), 3), element.edges]).astype(np.int64)
    mesh = pv.PolyData(element.vertices, faces)
    mesh.save(str(OUTPUTS / f"19_{element.name}.vtk"))
    print(f"Exported {element.name} mesh: {mesh.n_points} vertices, {mesh.n_cells} faces")

# gempy_plugins.utils.export.export_moose_input(geo_model, path=...) and a
# PFLOTRAN .in template also exist for users of that external reservoir-
# simulation software -- not exercised here since they require software
# this suite doesn't assume you have installed.
