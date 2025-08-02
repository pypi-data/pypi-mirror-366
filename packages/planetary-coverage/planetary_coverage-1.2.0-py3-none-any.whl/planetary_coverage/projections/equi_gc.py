"""Equirectangular projection module."""

import numpy as np

from matplotlib.path import Path

from .equi import Equirectangular as EquirectangularProjection
from ..math import great_circle_arc


class Equirectangular(EquirectangularProjection):
    """Equirectangular projection with great circle object.

    a.k.a. `Plate Carrée` and `Equidistant Cylindrical`.

    Parameters
    ----------
    lon_e_0: float, optional
        Center east longitude.
    lat_0: float, optional
        Center latitude (North Pole by default).
    lat_ts: float, optional
        Latitude of true scale.
    x_0: float, optional
        False easting (default: r * lambda_0). See note below.
    y_0: float, optional
        False northing (default: 0).
    target: str
        Planet name.
    radius: float, optional
        Planet radius [km]. Use the target mean radius if
        the target is a `Planet` object.

    See Also
    --------
    planetary_coverage.projections.equi.Equirectangular
    planetary_coverage.projections.proj.GroundProjection

    """

    def __init__(
        self,
        lon_e_0=180,
        lat_0=0,
        lat_ts=0,
        x_0=None,
        y_0=0,
        target=None,
        radius=None,
        npt_gc=8,
    ):
        self.lon_e_0 = lon_e_0
        self.lat_0 = lat_0
        self.target = target
        self.radius = radius
        self.lat_ts = lat_ts
        self.npt_gc = npt_gc

        self.x_0 = x_0 if x_0 is not None else self.r * np.radians(self.lon_e_0)
        self.y_0 = y_0

    def vc(self, path):
        """Get projected vertices and codes (and close the polygon if needed).

        Add new intermediate points along great circles to get defined the shape
        of the polygons.

        Parameters
        ----------
        path: matplotlib.path.Path
            Matplotlib path in east-longitude and latitude coordinates.

        Returns
        -------
        [float], [float], [int]
            X and Y vertices and path code.

        """
        lon_e, lat = path.vertices.T

        # Add codes if missing
        if path.codes is None:
            codes = [Path.MOVETO] + [Path.LINETO] * (len(lon_e) - 2) + [Path.CLOSEPOLY]
        else:
            codes = path.codes

        # Close the path
        if lon_e[0] != lon_e[-1] or lat[0] != lat[-1]:
            lon_e = np.concatenate([lon_e, [lon_e[0]]])
            lat = np.concatenate([lat, [lat[0]]])

            if codes[-1] == Path.CLOSEPOLY:
                codes = np.concatenate([codes[:-1], [Path.LINETO, Path.CLOSEPOLY]])
            else:
                codes = np.concatenate([codes, [Path.CLOSEPOLY]])

        # Add additional Great Circles points
        nv = len(lon_e) - 1

        gc_lons_e, gc_lats = np.transpose(
            [
                (_lon_e, _lat)
                for i in range(nv)
                for _lon_e, _lat in great_circle_arc(
                    lon_e[i], lat[i], lon_e[i + 1], lat[i + 1], npt=self.npt_gc
                ).T[:-1]
            ]
            + [(lon_e[-1], lat[-1])]
        )

        # Convert to projected coordinates
        gc_vertices = self.xy(gc_lons_e, gc_lats).T

        gc_codes = [
            code for c in codes[:-1] for code in [c] + (self.npt_gc - 2) * [Path.LINETO]
        ] + [Path.CLOSEPOLY]

        return gc_vertices, gc_codes
