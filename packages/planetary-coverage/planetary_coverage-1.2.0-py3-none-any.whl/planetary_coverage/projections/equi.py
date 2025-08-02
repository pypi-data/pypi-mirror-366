"""Equirectangular projection module."""

import numpy as np

from matplotlib.path import Path

from .proj import GroundProjection
from ..misc import rindex


np.seterr(invalid='ignore')


BEZIER_CODES = (
    Path.CURVE3,  # Bézier curves with 3 control points
    Path.CURVE4,  # Bézier curves with 4 control points
)


class Equirectangular(GroundProjection):
    """Equirectangular projection object.

    a.k.a. `Plate Carrée` and `Equidistant Cylindrical`.

    Sources:

    - https://proj.org/operations/projections/eqc.html
    - https://github.com/proj4js/proj4js/blob/master/lib/projections/eqc.js

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

    Note
    ----
    Here, by default the longitudes are defined eastward in [0°, 360°],
    The false easting ``x_0``, if not provided, is automatically adjusted
    to make projected coordinates and real coordinates consistent.
    You can fall back to the Earth convention (±180°) with ``lon_e_0=0``
    attribute.

    """

    DEFAULT_RADIUS_KM = 180e-3 / np.pi  # Unitary degree representation

    PROJ4 = 'eqc'  # Proj4 projection key

    def __init__(
        self, lon_e_0=180, lat_0=0, lat_ts=0, x_0=None, y_0=0, target=None, radius=None
    ):
        self.lon_e_0 = lon_e_0
        self.lat_0 = lat_0
        self.target = target
        self.radius = radius
        self.lat_ts = lat_ts

        self.x_0 = x_0 if x_0 is not None else self.r * np.radians(self.lon_e_0)
        self.y_0 = y_0

    @property
    def lat_ts(self):
        """Latitude of true scale [degree]."""
        return self.__lat_ts

    @lat_ts.setter
    def lat_ts(self, value):
        """Set latitude of true scale value."""
        self.__lat_ts = value
        self.__rc = np.cos(np.radians(value))
        self.__xc = np.pi * self.r * self.__rc
        self.__yc = np.pi / 2 * self.r

    @property
    def rc(self):
        """Cosine of latitude of origin."""
        return self.__rc

    @property
    def xc(self):
        """Projected x crossing meridian value."""
        return self.__xc

    @property
    def yc(self):
        """Projected y pole value."""
        return self.__yc

    @property
    def extent(self):
        """Projection extent."""
        return [
            self.x_0 - self.xc,
            self.x_0 + self.xc,
            self.y_0 - self.yc,
            self.y_0 + self.yc,
        ]

    @property
    def proj4(self):
        """Proj4 definition."""
        return ' '.join([
            f'+proj={self.PROJ4}',
            f'+lat_0={self.lat_0}',
            f'+lon_0={self.lon_e_0}',
            f'+lat_ts={self.lat_ts}',
            f'+x_0={self.x_0:.3f}',
            f'+y_0={self.y_0:.3f}',
            f'+a={self.r}',
            f'+b={self.r}',
            '+units=m',
            '+no_defs',
        ])

    @property
    def wkt(self):
        """WKT definition."""
        return (
            f'PROJCS["PROJCS_{self.target}_{self}",'
            f'GEOGCS["GCS_{self.target}",'
            f'DATUM["D_{self.target}",'
            f'SPHEROID["{self.target}_Mean_Sphere", {int(self.r)}, 0]],'
            'PRIMEM["Greenwich",0],'
            'UNIT["Degree",0.017453292519943295]],'
            f'PROJECTION["{self}"],'
            f'PARAMETER["false_easting", {self.x_0:.3f}],'
            f'PARAMETER["false_northing", {self.y_0:.3f}],'
            f'PARAMETER["standard_parallel_1", {self.lat_ts}],'
            f'PARAMETER["central_meridian", {self.lon_e_0}],'
            f'PARAMETER["latitude_of_origin", {self.lat_0}],'
            'UNIT["Meter", 1]]'
        )

    def xy(self, lon_e, lat, value=None):
        """Convert latitude/longitude coordinates in map coordinates.

        Parameters
        ----------
        lon_e: float or array
            East longitude [degree].
        lat: float or array
            Latitude [degree].
        value: float or array
            Value associated with the point.

        Returns
        -------
        float or array, float or array
            X-Y map coordinates.

        Note
        ----
        The right side edge is kept during the warp of the longitudes.

        """
        dlon = np.radians(np.subtract(lon_e, self.lon_e_0))
        dlat = np.radians(np.subtract(lat, self.lat_0))

        x = self.x_0 + self.r * dlon * self.rc
        y = self.y_0 + self.r * dlat

        # Right side edge
        edge = np.abs(x % (4 * self.xc) - (self.x_0 + self.xc)) < self.EPSILON

        # Warp longitudes
        x = (x + (self.xc - self.x_0)) % ((edge + 1) * 2 * self.xc) - (self.xc - self.x_0)

        if np.ndim(x) == 0 and np.ndim(y) > 0:
            x = np.broadcast_to(x, y.shape)
        elif np.ndim(x) > 0 and np.ndim(y) == 0:
            y = np.broadcast_to(y, x.shape)

        return np.array([x, y]) if value is None else np.array([x, y, value])

    def lonlat(self, x, y):
        """Convert map coordinates in latitude/longitude coordinates.

        Parameters
        ----------
        x: float or array
            X-coordinate on the map [m].
        y: float or array
            Y-coordinate on the map [m].

        Returns
        -------
        float or array, float or array
            East longitude and latitude [degree].

        """
        lon_e = np.degrees(np.subtract(x, self.x_0) / self.r * self.rc) + 180
        lat = self.lat_0 + np.degrees(np.subtract(y, self.y_0) / self.r)

        # Fix rounding issues
        lon_e = np.round(lon_e, int(-np.log10(self.EPSILON)))

        # Right side edge
        edge = np.abs(lon_e % (2 * 360) - 360) < self.EPSILON

        # Warp longitudes
        lon_e = lon_e % ((edge + 1) * 360) - 180 + self.lon_e_0

        if np.ndim(lon_e) == 0 and np.ndim(lat) > 0:
            lon_e = np.broadcast_to(lon_e, lat.shape)
        elif np.ndim(lon_e) > 0 and np.ndim(y) == 0:
            lat = np.broadcast_to(lat, lon_e.shape)

        return lon_e, lat

    def xy_plot(self, lons_e, lats, values=None):
        """Plot latitude/longitude coordinates in a map.

        Parameters
        ----------
        lons_e: float or array
            East longitude [degree].
        lats: float or array
            Latitude [degree].
        values: float or array
            Values associated with the points.

        Returns
        -------
        float or array, float or array
            X-Y map coordinates.

        """
        x, y, v = self.xy(lons_e, lats, value=lats if values is None else values)
        cross = np.abs(x[1:] - x[:-1]) > self.xc  # Larger than half the map: [i+1] - [i]

        if cross.any():
            verts = [[x[0], y[0], v[0]]]
            for i, crossed in enumerate(cross):
                if crossed:
                    if x[i] > self.x_0:
                        _x1, _x2 = self.x_0 + self.xc, self.x_0 - self.xc  # Right cross
                        _f = (self.xc + self.x_0 - x[i]) / (2 * self.xc + x[i + 1] - x[i])
                    else:
                        _x1, _x2 = self.x_0 - self.xc, self.x_0 + self.xc  # Left cross
                        _f = (self.xc - self.x_0 + x[i]) / (2 * self.xc + x[i] - x[i + 1])

                    _y = (y[i + 1] - y[i]) * _f + y[i]
                    _v = (v[i + 1] - v[i]) * _f + v[i]

                    verts.append([_x1, _y, _v])
                    verts.append([np.nan, np.nan, np.nan])
                    verts.append([_x2, _y, _v])

                verts.append([x[i + 1], y[i + 1], v[i + 1]])

            x, y, v = np.transpose(verts)

        return (x, y) if values is None else (x, y, v)

    def xy_path(self, path):
        """Convert path vertices in map coordinates.

        Parameters
        ----------
        path: matplotlib.path.Path
            Matplotlib path in east-longitude and latitude coordinates.

        Returns
        -------
        matplotlib.path.Path
            Path in map coordinates.

        Raises
        ------
        ValueError
            If the polygon cross more than 2 times the anti-meridian.

        Note
        ----
        Bézier curves control points are replaced by regular polygons.

        """
        if path is None:
            return None

        vertices, codes = self.vc(path)

        # Replace Bézier codes by lineto codes
        codes = [code if code not in BEZIER_CODES else Path.LINETO for code in codes]

        x, y = vertices.T
        cross = np.abs(x[1:] - x[:-1]) > self.xc  # Larger than half the map: [i+1] - [i]
        n_cross = np.sum(cross)

        if n_cross == 1:
            vertices, codes = self._cross_pole(x, y, cross)
        elif n_cross > 0 and n_cross % 2 == 0:
            vertices, codes = self._cross_antimeridian(x, y, cross, codes)
        elif n_cross % 2 == 1:
            raise ValueError('Path vertices cross more than 2 time the anti-meridian.')

        return Path(vertices, codes)

    def _cross_pole(self, x, y, cross):
        """Redraw vertices path around the North/South Pole.

        Parameters
        ----------
        x: [float]
            Map x coordinate.
        y: [float]
            Map y coordinate.
        cross: [bool]
            Bool list if the vertices crossed the anti-meridian.

        Returns
        -------
        matplotlib.path.Path
            New vertex surrounding the pole.

        """
        pole = self.yc if y[np.argmax(np.abs(y))] >= 0 else -self.yc

        verts = [[x[0], y[0]]]
        for i, crossed in enumerate(cross):
            if crossed:
                if x[i] > self.x_0:
                    _x1, _x2 = self.x_0 + self.xc, self.x_0 - self.xc  # Right cross
                    _f = (self.x_0 + self.xc - x[i]) / ((x[i + 1] + 2 * self.xc) - x[i])
                else:
                    _x1, _x2 = self.x_0 - self.xc, self.x_0 + self.xc  # Left cross
                    _f = (x[i] - (self.x_0 - self.xc)) / (x[i] - (x[i + 1] - 2 * self.xc))

                _y = (y[i + 1] - y[i]) * _f + y[i]

                if not np.isnan(_f):
                    verts.append([_x1, _y])

                verts.append([_x1, pole])
                verts.append([_x2, pole])

                if not np.isnan(_f):
                    verts.append([_x2, _y])

            # Avoid duplicated endpoint
            if verts[-1] != [x[i + 1], y[i + 1]]:
                verts.append([x[i + 1], y[i + 1]])

        codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 2) + [Path.CLOSEPOLY]

        return verts, codes

    def _cross_antimeridian(self, x, y, cross, codes):
        """Redraw vertices path around the anti-meridian.

        Parameters
        ----------
        x: [float]
            Map x coordinate.
        y: [float]
            Map y coordinate.
        cross: [bool]
            Bool list if the vertices crossed the anti-meridian.
        codes: [bool]
            List of path codes.

        Returns
        -------
        matplotlib.path.Path
            New vertices (in 2 pieces) splitted by the anti-meridian.

        """
        npt = len(x) - 1

        # Left and right polygons vertices and codes
        lv, rv, lc, rc = [], [], [], []
        for i in range(npt):
            if x[i] <= self.x_0:
                lv.append([x[i], y[i]])
                lc += [codes[i]]
            else:
                rv.append([x[i], y[i]])
                rc += [codes[i]]

            if cross[i]:
                # Select the correct additional vertex code
                lv, lc = self._code_cross_antimeridian(lv, lc, codes[i])
                rv, rc = self._code_cross_antimeridian(rv, rc, codes[i])

                # Compute the anti-crossing left and right vertices
                _xl = self.x_0 - self.xc
                _xr = self.x_0 + self.xc

                if x[i] <= self.x_0:
                    _f = (x[i] - _xl) / (x[i] - x[i + 1] + 2 * self.xc)
                else:
                    _f = (_xr - x[i]) / (x[i + 1] - x[i] + 2 * self.xc)

                _y = (y[i + 1] - y[i]) * _f + y[i]

                lv.append([_xl, _y])
                rv.append([_xr, _y])

        # Close the polygon with the last opening vertex
        li = rindex(lc, Path.MOVETO)
        ri = rindex(rc, Path.MOVETO)

        lv += [lv[li]]
        rv += [rv[ri]]
        lc += [Path.CLOSEPOLY] if lc else []
        rc += [Path.CLOSEPOLY] if rc else []

        return np.vstack([lv, rv]), lc + rc

    @staticmethod
    def _code_cross_antimeridian(vertices, codes, code):
        """Add the new vertex code on a crossing point.

        Parameters
        ----------
        vertices: list
            List of the vertices
        codes: list
            List of already previous vertex codes.
        code: int
            Current vertex code.

        Returns
        -------
        list
            Updated vertex values.
        list
            Updated vertex codes.

        Note
        ----
        An extra vertex is added when the next vertex is
        new polygon (in order to correctly manage holes).

        """
        if not codes:
            codes = [Path.MOVETO]

        elif code == Path.MOVETO and codes[-1] != Path.MOVETO:
            # Close the polygon with the last opening vertex
            i = rindex(codes, Path.MOVETO)
            vertices += [vertices[i]]
            codes += [Path.CLOSEPOLY, Path.MOVETO]

        else:
            codes += [Path.LINETO]

        return vertices, codes
