"""A small gallery of classic geological fold/layer geometries -- anticline,
syncline, recumbent fold, and pinchout -- each built from a handful of
hand-crafted synthetic surface points and orientations rather than gempy's
generate_example_model presets (which download real tutorial CSVs from
GitHub for every preset except a trivial flat-layer case, conflicting with
this suite's synthetic-only rule)."""
from pathlib import Path

import numpy as np
import gempy as gp
import gempy_viewer as gpv

OUTPUTS = Path(__file__).parent / "outputs"
OUTPUTS.mkdir(exist_ok=True, parents=True)


def _new_model(project_name):
    geo_model = gp.create_geomodel(
        project_name=project_name,
        extent=[0, 1000, 0, 200, 0, 900],
        resolution=[50, 10, 50],
        structural_frame=gp.data.StructuralFrame.initialize_default_structure(),
    )
    geo_model.structural_frame.structural_elements[0].name = "rock1"
    return geo_model


def _pole_vector(dip_deg, azimuth_deg):
    """Standard dip/azimuth -> unit normal-vector conversion (azimuth measured
    clockwise from the Y axis, dip measured from horizontal)."""
    dip, az = np.radians(dip_deg), np.radians(azimuth_deg)
    return np.array([np.sin(dip) * np.sin(az), np.sin(dip) * np.cos(az), np.cos(dip)])


def anticline():
    """Dome-shaped layer: points rise toward the model's middle then fall."""
    geo_model = _new_model("Anticline")
    x = [0, 250, 500, 750, 1000]
    z = [200, 400, 500, 400, 200]
    gp.add_surface_points(geo_model=geo_model, x=x, y=[100] * 5, z=z,
                           elements_names=["rock1"] * 5)
    gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[500],
                         elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    gp.compute_model(geo_model)
    return geo_model


def syncline():
    """Bowl-shaped layer: the mirror image of the anticline above. There is
    no official gempy example for this shape -- it is hand-designed here,
    not ported from an upstream reference."""
    geo_model = _new_model("Syncline")
    x = [0, 250, 500, 750, 1000]
    z = [600, 400, 300, 400, 600]
    gp.add_surface_points(geo_model=geo_model, x=x, y=[100] * 5, z=z,
                           elements_names=["rock1"] * 5)
    gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[300],
                         elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    gp.compute_model(geo_model)
    return geo_model


def recumbent_fold():
    """An overturned fold: the same X position yields two Z values (a normal
    limb and an overturned limb) converging toward a fold "nose". A dip
    greater than 90 degrees is gempy's way of encoding overturned bedding --
    the dip/azimuth pair used here (90/185.73 and 90/354.27) mirrors gempy's
    own recumbent-fold tutorial data."""
    geo_model = _new_model("Recumbent_Fold")
    x_normal = [0, 200, 400, 700]
    z_normal = [780, 600, 420, 220]
    x_overturned = [0, 200, 400, 700]
    z_overturned = [220, 260, 300, 320]
    gp.add_surface_points(geo_model=geo_model, x=x_normal, y=[100] * 4, z=z_normal,
                           elements_names=["rock1"] * 4)
    gp.add_surface_points(geo_model=geo_model, x=x_overturned, y=[100] * 4, z=z_overturned,
                           elements_names=["rock1"] * 4)
    gp.add_orientations(
        geo_model=geo_model, x=[200, 200], y=[100, 100], z=[600, 260],
        elements_names=["rock1", "rock1"],
        pole_vector=[_pole_vector(90, 185.73), _pole_vector(90, 354.27)],
    )
    geo_model.update_transform(gp.data.GlobalAnisotropy.NONE)
    gp.compute_model(geo_model)
    return geo_model


def pinchout():
    """Two surfaces that converge in thickness (400 -> 100) toward one end
    of the model without ever crossing -- a classic stratigraphic
    pinchout."""
    geo_model = _new_model("Pinchout")
    x = [0, 500, 1000]
    z_bottom = [300, 375, 450]
    z_top = [700, 625, 550]
    gp.add_surface_points(geo_model=geo_model, x=x, y=[100] * 3, z=z_bottom,
                           elements_names=["rock1"] * 3)
    gp.add_orientations(geo_model=geo_model, x=[500], y=[100], z=[375],
                         elements_names=["rock1"], pole_vector=[np.array([0, 0, 1])])

    color_gen = geo_model.structural_frame.color_generator
    rock2 = gp.data.StructuralElement(
        name="rock2",
        surface_points=gp.data.SurfacePointsTable.from_arrays(
            x=np.array(x), y=np.array([100] * 3), z=np.array(z_top), names="rock2"),
        orientations=gp.data.OrientationsTable.from_arrays(
            x=np.array([500]), y=np.array([100]), z=np.array([625]),
            G_x=np.array([0.0]), G_y=np.array([0.0]), G_z=np.array([1.0]), names="rock2"),
        color=next(color_gen),
    )
    geo_model.structural_frame.structural_groups[0].elements.append(rock2)

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
