"""Three ways to persist a computed gempy model: (1) a genuine JSON
round-trip via JsonIO (geometry/configuration only), (2) gempy's own binary
.gempy save format (still marked "in development" upstream), and (3)
exporting computed surface meshes to VTK via pyvista for use in other 3D
tools."""
from pathlib import Path

import numpy as np
import gempy as gp
import pyvista as pv
from gempy.modules.json_io import JsonIO

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)

geo_model = gp.create_geomodel(
    project_name="IO_Demo",
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
