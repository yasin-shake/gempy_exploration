"""Sanity-check the geoLLM environment: confirm gempy, gempy_viewer, and
pyvista import cleanly, report their versions, and confirm the default
computation backend (numpy) gempy will use unless explicitly reconfigured."""
import gempy as gp
import gempy_viewer as gpv
import pyvista as pv

print(f"gempy version:        {gp.__version__}")
print(f"gempy_viewer version: {gpv.__version__}")
print(f"pyvista version:      {pv.__version__}")

cfg = gp.data.GemPyEngineConfig()
print(f"Default backend:      {cfg.backend}")
assert cfg.backend == gp.data.AvailableBackends.numpy, "expected numpy as the default backend"

print("geoLLM environment OK.")
