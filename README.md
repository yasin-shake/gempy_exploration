# geoLLM — gempy example suite

A comprehensive, standalone collection of example scripts demonstrating the `gempy` 3D structural geological modeling library (v3 API, gempy 2026.0.3). Every script is self-contained, uses only synthetic/hand-crafted data, and can be run independently.

## Setup

```
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
```

Script 18 (`18_probabilistic_inversion.py`) additionally needs:

```
.venv\Scripts\pip install -r requirements-optional.txt
```

Run any script from the project root:

```
.venv\Scripts\python examples\01_getting_started.py
```

Figures are saved to `examples/outputs/` in addition to displaying interactively. To run headlessly (no blocking GUI windows), set `$env:MPLBACKEND="Agg"` before invoking a script.

## Examples at a glance

| # | Script | Demonstrates |
|---|---|---|
| 00 | verify_installation | Environment sanity check |
| 01 | getting_started | Minimal end-to-end model |
| 02 | manual_structural_frame | Building a model via raw StructuralFrame/Element/Group objects |
| 03 | csv_data_workflow | Loading surface points/orientations from CSV |
| 04 | synthetic_geometries_gallery | Anticline, syncline, recumbent fold, pinchout |
| 05 | unconformities_and_series_stacking | Erode vs onlap unconformities |
| 06 | single_fault | One normal fault |
| 07 | multiple_faults_and_graben | Fault-fault relations, graben structure |
| 08 | finite_faults | Spatially-bounded faults (and the current upstream limitation) |
| 09 | combination_model | Fault + unconformity + fold combined |
| 10 | grids_and_topography | Custom/section grids, random topography |
| 11 | visualization_2d | plot_2d deep dive |
| 12 | visualization_3d | plot_3d / pyvista deep dive |
| 13 | topology_analysis | Adjacency graph of geological bodies |
| 14 | interpolation_and_kernels | Kriging kernel functions |
| 15 | anisotropy_and_backend_config | Anisotropy modes, numpy vs PyTorch backend |
| 16 | point_evaluation | Querying the model at arbitrary XYZ points |
| 17 | gravity_forward_modeling | Forward gravity modeling |
| 18 | probabilistic_inversion | Bayesian inference with Pyro (experimental) |
| 19 | json_model_io_and_export | JSON/binary save-load, VTK mesh export |

## Script details

### 00 — `verify_installation.py`
**Capability:** environment sanity check, no model built.
Imports `gempy`, `gempy_viewer`, `pyvista`, prints their versions, and asserts the default computation backend is `AvailableBackends.numpy`. No output image — there's nothing to plot, so this is a deliberate exception to the "every script saves a figure" convention.

### 01 — `getting_started.py`
**Capability:** the smallest complete gempy workflow — `create_geomodel` → `add_surface_points`/`add_orientations` → `compute_model` → plot. Establishes the mandatory rename step after `StructuralFrame.initialize_default_structure()`.

`outputs/01_getting_started_2d.png` — a 2D cross-section of a single "Limestone" layer over basement, gently sagging between three control points.

![01_getting_started_2d](examples/outputs/01_getting_started_2d.png)

`outputs/01_getting_started_3d.png` — the same model in 3D, showing the Limestone/basement contact as a curved surface through the block.

![01_getting_started_3d](examples/outputs/01_getting_started_3d.png)

### 02 — `manual_structural_frame.py`
**Capability:** building a model by hand from `StructuralElement`/`StructuralGroup`/`StructuralFrame` and `SurfacePointsTable.from_arrays`/`OrientationsTable.from_arrays`, bypassing the `add_surface_points` convenience API — the pattern for programmatic model generation.

`outputs/02_manual_structural_frame_2d.png` — two flat horizontal layers (rock2 over rock1 over basement), confirming the hand-built frame interpolates correctly.

![02_manual_structural_frame_2d](examples/outputs/02_manual_structural_frame_2d.png)

### 03 — `csv_data_workflow.py`
**Capability:** the CSV-driven workflow most real gempy projects use. Writes synthetic `points.csv`/`orientations.csv` to `examples/data/` at runtime, loads them via `gp.data.ImporterHelper`, then calls the (mandatory, for CSV-loaded models) `map_stack_to_surfaces`.

`outputs/03_csv_data_workflow_2d.png` — two gently dipping layers (5° dip), matching the orientation encoded in the synthetic CSV.

![03_csv_data_workflow_2d](examples/outputs/03_csv_data_workflow_2d.png)

### 04 — `synthetic_geometries_gallery.py`
**Capability:** a gallery of four classic fold/layer geometries built from hand-crafted coordinates (not `generate_example_model`, which downloads real tutorial data). Each geometry is its own function.

`outputs/04_anticline.png` — a symmetric dome (upward fold).

![04_anticline](examples/outputs/04_anticline.png)

`outputs/04_syncline.png` — a symmetric bowl (downward fold), the mirror image of the anticline.

![04_syncline](examples/outputs/04_syncline.png)

`outputs/04_recumbent_fold.png` — an overturned fold, built using `dip > 90°` orientations to encode overturned bedding.

![04_recumbent_fold](examples/outputs/04_recumbent_fold.png)

`outputs/04_pinchout.png` — two surfaces converging in thickness (400 → 100) toward one end without crossing, a classic stratigraphic pinchout.

![04_pinchout](examples/outputs/04_pinchout.png)

### 05 — `unconformities_and_series_stacking.py`
**Capability:** the two classic unconformity relationships. A "cover" layer's `StructuralGroup.structural_relation` is toggled between `StackRelationType.ERODE` and `.ONLAP` against a domed "rock1" layer below, then recomputed for each.

`outputs/05_erode.png` — the cover erosively truncates the rock1 dome flat wherever the dome pokes above the cover's elevation.

![05_erode](examples/outputs/05_erode.png)

`outputs/05_onlap.png` — the same dome, but now poking up through the cover instead of being cut off — onlap drapes around high points rather than truncating them.

![05_onlap](examples/outputs/05_onlap.png)

### 06 — `single_fault.py`
**Capability:** one normal fault offsetting a flat layer, via a `FAULT`-type `StructuralGroup`, a `fault_relations` matrix, and `gp.set_is_fault`.

`outputs/06_single_fault_2d.png` — a clear vertical offset in the rock1/basement contact across the fault trace.

![06_single_fault_2d](examples/outputs/06_single_fault_2d.png)

`outputs/06_single_fault_3d.png` — the same fault surface and offset rendered in 3D.

![06_single_fault_3d](examples/outputs/06_single_fault_3d.png)

### 07 — `multiple_faults_and_graben.py`
**Capability:** two faults with opposing dip directions plus `gp.set_fault_relation`'s fault-fault interaction matrix — the classic graben pattern.

`outputs/07_graben_2d.png` — the block between the two faults visibly dropped down relative to the flanks.

![07_graben_2d](examples/outputs/07_graben_2d.png)

`outputs/07_graben_3d.png` — the same graben structure in 3D.

![07_graben_3d](examples/outputs/07_graben_3d.png)

### 08 — `finite_faults.py`
**Capability:** an honest look at a real upstream limitation. `gp.set_is_finite_fault` is present in gempy 2026.0.3's public API but its implementation is a bare `raise NotImplementedError`. The script calls it inside a `try/except`, prints what happens, then demonstrates the only practical workaround — confining a fault's own surface-point data to a sub-region of the model.

`outputs/08_full_extent_fault.png` — the default behavior: the fault cuts the entire model extent.

![08_full_extent_fault](examples/outputs/08_full_extent_fault.png)

`outputs/08_bounded_workaround.png` — the workaround: the fault's influence confined to a sub-region (visibly not the same as a true bounded ellipsoid).

![08_bounded_workaround](examples/outputs/08_bounded_workaround.png)

### 09 — `combination_model.py`
**Capability:** a capstone combining everything from scripts 05–07 — a fault, an unconformity-bounded capping layer, and a two-surface folded series — in one geomodel, mirroring gempy's own `g07_combination.py` example.

`outputs/09_combination_2d.png` — four lithologies (fault, rock1, rock2, rock3) visible together: a folded rock1/rock2 pair, a near-flat rock3 cap, and a fault cutting through the left side.

![09_combination_2d](examples/outputs/09_combination_2d.png)

`outputs/09_combination_3d.png` — the same combined model in 3D.

![09_combination_3d](examples/outputs/09_combination_3d.png)

### 10 — `grids_and_topography.py`
**Capability:** gempy's non-default grid types layered onto the standard regular grid: `set_custom_grid` (arbitrary query points), `set_section_grid` (a named vertical cross-section), and `set_topography_from_random` (a fractal elevation surface).

`outputs/10_section_traces.png` — the section trace line plotted alone (matches the `("section_ns", [500,0]→[500,1000])` definition).

![10_section_traces](examples/outputs/10_section_traces.png)

`outputs/10_sections_and_topography.png` — left: the `section_ns` cross-section with the area above the topography surface masked out; right: a map view of the random topography with contour lines and the section trace overlaid.

![10_sections_and_topography](examples/outputs/10_sections_and_topography.png)

### 11 — `visualization_2d.py`
**Capability:** a deep dive into `gpv.plot_2d`'s options: multiple orthogonal slices in one call, the interpolated scalar field instead of discretized lithology, and boundaries-only rendering.

`outputs/11_orthogonal_slices.png` — the same anticline sliced along both X and Y directions side by side.

![11_orthogonal_slices](examples/outputs/11_orthogonal_slices.png)

`outputs/11_scalar_field.png` — the continuous interpolated scalar field (contoured) instead of discrete lithology colors.

![11_scalar_field](examples/outputs/11_scalar_field.png)

`outputs/11_boundaries_only.png` — just the surface contact line, no fill and no raw data points — `show_boundaries=True, show_lith=False, show_data=False`.

![11_boundaries_only](examples/outputs/11_boundaries_only.png)

### 12 — `visualization_3d.py`
**Capability:** `gpv.plot_3d`'s static-image rendering path (`image=True`, off-screen, safe for headless runs) and a check of which `plotter_type` backends are actually implemented.

`outputs/12_static_screenshot.png` — an off-screen-rendered 3D view of the anticline, captured via `image=True` and saved through matplotlib. The script also prints that only `plotter_type='basic'` works in this gempy_viewer version; `'background'`/`'notebook'` both raise `NotImplementedError`.

![12_static_screenshot](examples/outputs/12_static_screenshot.png)

### 13 — `topology_analysis.py`
**Capability:** computing the adjacency graph between distinct fault-separated rock volumes via `gempy_plugins.topology_analysis`. Requires `intpolation_options_tye=DENSE_GRID` explicitly — mixing a plain `resolution=` grid with the default octree-based interpolation options crashes `compute_topology`.

`outputs/13_adjacency_matrix.png` — a small adjacency matrix showing which lithology/fault-block combinations (FB1, FB2) touch each other.

![13_adjacency_matrix](examples/outputs/13_adjacency_matrix.png)

`outputs/13_topology_graph.png` — the same adjacency graph, overlaid as numbered nodes on a 2D cross-section of the faulted model.

![13_topology_graph](examples/outputs/13_topology_graph.png)

### 14 — `interpolation_and_kernels.py`
**Capability:** comparing gempy's RBF kernel functions (`cubic`, `exponential`, `matern_5_2`) used to interpolate the scalar field, including each kernel's condition number.

`outputs/14_kernel_cubic.png`, `outputs/14_kernel_exponential.png`, `outputs/14_kernel_matern_5_2.png` — the same anticline's scalar field under each kernel; the contour smoothness/shape varies subtly between kernels.

![14_kernel_cubic](examples/outputs/14_kernel_cubic.png)
![14_kernel_exponential](examples/outputs/14_kernel_exponential.png)
![14_kernel_matern_5_2](examples/outputs/14_kernel_matern_5_2.png)

### 15 — `anisotropy_and_backend_config.py`
**Capability:** `GlobalAnisotropy.CUBE` vs `.NONE` transforms, plus the `numpy` vs `PyTorch` compute backends. Uses a deliberately elongated (4:1) extent, since a perfectly cubic extent gives `CUBE` nothing to normalize.

`outputs/15_anisotropy_CUBE.png` / `outputs/15_anisotropy_NONE.png` — the same elongated anticline under each anisotropy mode (the visual difference is subtle for this sparse 3-point dataset — a known limitation of the toy example, not a bug).

![15_anisotropy_CUBE](examples/outputs/15_anisotropy_CUBE.png)
![15_anisotropy_NONE](examples/outputs/15_anisotropy_NONE.png)

### 16 — `point_evaluation.py`
**Capability:** querying an already-computed model at arbitrary XYZ points via `gp.compute_model_at`, rather than only reading the regular grid — useful for evaluating a model along a borehole trace. Demonstrates restoring the grid type afterward, since `compute_model_at` replaces the active grid as a side effect.

`outputs/16_reference_model.png` — the reference anticline model the query points are evaluated against.

![16_reference_model](examples/outputs/16_reference_model.png)

### 17 — `gravity_forward_modeling.py`
**Capability:** forward-modeling the gravity response of a domed density contrast at a line of synthetic surface stations, via `set_centered_grid` + `calculate_gravity_gradient` + `GeophysicsInput`.

`outputs/17_gravity_profile.png` — a smooth U-shaped gravity trough centered over the dome (denser material bulging closer to the surface produces a stronger anomaly at the center), with minor voxel-scale texture inherent to gempy's discretized block-model approach at this resolution.

![17_gravity_profile](examples/outputs/17_gravity_profile.png)

### 18 — `probabilistic_inversion.py` — *[advanced/experimental]*
**Capability:** Bayesian inference with Pyro directly against gempy's internals (not the unstable `gempy_probability` package). Puts a prior on a surface point's rescaled Z-coordinate, forward-runs the interpolator inside the probabilistic model, and uses NUTS to infer a posterior from one synthetic observation. Requires `compute_grads=True` on every `gp.compute_model` call in the chain, or PyTorch autodiff silently breaks.

`outputs/18_trace.png` — the NUTS sample trace (left) and posterior histogram (right) for the sampled parameter, in gempy's internal rescaled coordinate space.

![18_trace](examples/outputs/18_trace.png)

### 19 — `json_model_io_and_export.py`
**Capability:** three ways to persist a computed model: (1) genuine JSON round-trip via `gempy.modules.json_io.JsonIO` (geometry/config only), (2) gempy's own binary `.gempy` save format (still "in development" upstream), and (3) exporting computed surface meshes to VTK via pyvista.

No standalone figure — outputs are data files: `outputs/19_model.json`, `outputs/19_model.gempy`, `outputs/19_surface1.vtk` (open the `.vtk` in ParaView or pyvista to inspect the exported mesh).

## Notes

- Targets gempy's current v3 API only (`gp.create_geomodel`, `gp.data.*`) — not the legacy v2 API (`gempy_legacy`).
- All models use small hand-crafted synthetic data; nothing is downloaded at runtime except script 03, which generates its own CSVs locally before reading them back.
- Script 18 depends only on `pyro`/`torch` directly rather than the `gempy_probability` package, whose PyPI release lags far behind its API, and uses plain matplotlib rather than `arviz` for posterior plots (arviz 1.2.0 dropped Pyro support in favor of NumPyro-only).
- Every output image in `examples/outputs/` was regenerated and visually spot-checked as part of building this suite, which is what caught and fixed a handful of geometry/rendering issues in scripts 04, 05, 08, 13, 14, 15, and 17 (overlapping titles, an unconformity example with no visible ERODE/ONLAP difference, an illegibly small plot, a cube-extent anisotropy comparison with nothing to compare, and an out-of-bounds gravity sampling radius).
