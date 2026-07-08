"""A small gallery of classic geological fold/layer geometries -- anticline,
syncline, recumbent fold, and pinchout.

Data: examples/data/jan_models/model2 (anticline), model3 (recumbent fold),
and model4 (pinchout) -- gempy's own real synthetic teaching geometries,
loaded via ImporterHelper. syncline has no direct real-data equivalent
upstream, so it is derived here by mirroring model2's real Z values, rather
than hand-crafted from scratch. Not using gp.generate_example_model, since
its presets download the same underlying CSVs from GitHub at call time for
every case except a trivial flat-layer one."""
from pathlib import Path

import numpy as np
import pandas as pd
import gempy as gp
import gempy_viewer as gpv

HERE = Path(__file__).parent
DATA = HERE / "data" / "jan_models"
OUTPUTS = HERE / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)


def _pole_vector(dip_deg, azimuth_deg):
    dip, az = np.radians(dip_deg), np.radians(azimuth_deg)
    return np.sin(dip) * np.sin(az), np.sin(dip) * np.cos(az), np.cos(dip)


def _extent_from(points, pad_xy=150, pad_z=150):
    return [
        points.X.min() - pad_xy, points.X.max() + pad_xy,
        points.Y.min() - pad_xy, points.Y.max() + pad_xy,
        points.Z.min() - pad_z, points.Z.max() + pad_z,
    ]


def _from_csv(project_name, stem):
    points = pd.read_csv(DATA / f"{stem}_surface_points.csv")
    geo_model = gp.create_geomodel(
        project_name=project_name,
        extent=_extent_from(points),
        resolution=[50, 10, 50],
        importer_helper=gp.data.ImporterHelper(
            path_to_surface_points=str(DATA / f"{stem}_surface_points.csv"),
            path_to_orientations=str(DATA / f"{stem}_orientations.csv"),
        ),
    )
    gp.map_stack_to_surfaces(gempy_model=geo_model, mapping_object={"Strat_Series": ("rock2", "rock1")})
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    gp.compute_model(geo_model)
    return geo_model


def anticline():
    """Dome-shaped two-layer stack (rock2 over rock1) -- gempy's real
    'model2' teaching geometry, loaded straight off disk."""
    return _from_csv("Anticline", "model2")


def recumbent_fold():
    """An overturned fold: gempy's real 'model3' teaching geometry. A dip
    greater than 90 degrees (185.73 / 354.27 here) is gempy's way of
    encoding overturned bedding."""
    return _from_csv("Recumbent_Fold", "model3")


def pinchout():
    """Two surfaces converging in thickness toward one end without ever
    crossing -- gempy's real 'model4' teaching geometry."""
    return _from_csv("Pinchout", "model4")


def syncline():
    """Bowl-shaped mirror image of the anticline. There is no official
    gempy dataset for this shape, so it is derived here by mirroring
    model2's real Z values top-to-bottom (and flipping dip accordingly),
    rather than hand-crafted independently."""
    points = pd.read_csv(DATA / "model2_surface_points.csv")
    orientations = pd.read_csv(DATA / "model2_orientations.csv")
    z_mid = (points.Z.min() + points.Z.max()) / 2
    points = points.assign(Z=2 * z_mid - points.Z)
    orientations = orientations.assign(dip=180 - orientations.dip)

    color_gen = gp.data.ColorsGenerator()
    groups_elements = []
    for name in ("rock2", "rock1"):
        sp = points[points.formation == name]
        ori = orientations[orientations.formation == name]
        gx, gy, gz = zip(*(_pole_vector(d, a) for d, a in zip(ori.dip, ori.azimuth)))
        groups_elements.append(gp.data.StructuralElement(
            name=name,
            surface_points=gp.data.SurfacePointsTable.from_arrays(
                x=sp.X.to_numpy(), y=sp.Y.to_numpy(), z=sp.Z.to_numpy(), names=name),
            orientations=gp.data.OrientationsTable.from_arrays(
                x=ori.X.to_numpy(), y=ori.Y.to_numpy(), z=ori.Z.to_numpy(),
                G_x=np.array(gx), G_y=np.array(gy), G_z=np.array(gz), names=name),
            color=next(color_gen),
        ))
    group = gp.data.StructuralGroup(
        name="Strat_Series", elements=groups_elements, structural_relation=gp.data.StackRelationType.ERODE)
    frame = gp.data.StructuralFrame(structural_groups=[group], color_gen=color_gen)

    geo_model = gp.create_geomodel(
        project_name="Syncline", extent=_extent_from(points), resolution=[50, 10, 50],
        structural_frame=frame)
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    gp.compute_model(geo_model)
    return geo_model


if __name__ == "__main__":
    for build in (anticline, syncline, recumbent_fold, pinchout):
        model = build()
        p2d = gpv.plot_2d(model, cell_number="mid", show=False)
        # fig.suptitle() overlaps plot_2d's own axes title (both land at the
        # same figure-relative y-position) -- prepend to the axes title
        # instead, which matplotlib sizes correctly for multi-line text.
        p2d.axes[0].set_title(f"{build.__name__}\n{p2d.axes[0].get_title()}")
        p2d.fig.savefig(OUTPUTS / f"04_{build.__name__}.png", dpi=150)
