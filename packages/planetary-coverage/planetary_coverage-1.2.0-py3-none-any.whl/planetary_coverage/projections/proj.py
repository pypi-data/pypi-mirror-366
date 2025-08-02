"""Abstract projection module."""

import numpy as np

from matplotlib.collections import PatchCollection, PathCollection
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from ..math import cs


TWO_ELEMENTS = 2
THREE_ELEMENTS = 3


class Projection:
    """Abstract ground projection object."""

    EPSILON = 1e-10
    PROJ4 = None  # Proj4 projection key

    def __str__(self):
        return self.__class__.__name__

    def __call__(self, *args, invert=False, **kwargs):
        """Project geographic point in X-Y coordinates (or reverse)."""
        if len(args) == 1:
            if isinstance(args[0], (PatchCollection, PathCollection)):
                return self.xy_collection(args[0])

            if isinstance(args[0], PathPatch):
                return self.xy_patch(args[0])

            if isinstance(args[0], Path):
                return self.xy_path(args[0])

        if len(args) == TWO_ELEMENTS or (
            len(args) == THREE_ELEMENTS and self.PROJ4 == 'ortho'
        ):
            return self.lonlat(*args) if invert else self.xy(*args, **kwargs)

        raise ValueError(
            'A `PatchCollection`, `PathPatch`, `Patch` '
            'or (lon_e, lat) attributes are required.'
        )

    @property
    def extent(self):
        """Projection extent."""
        raise NotImplementedError

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

        """
        raise NotImplementedError

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
        raise NotImplementedError

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
        return self.xy(lons_e, lats, value=values)

    def vc(self, path):
        """Get projected vertices and codes (and close the polygon if needed).

        Parameters
        ----------
        path: matplotlib.path.Path
            Matplotlib path in east-longitude and latitude coordinates.

        Returns
        -------
        [float], [float], [int]
            X and Y vertices and path code.

        """
        x, y = self.xy(*path.vertices.T)

        # Add codes if missing
        if path.codes is None and len(x) > 1:
            codes = [Path.MOVETO] + [Path.LINETO] * (len(x) - 2) + [Path.CLOSEPOLY]
        else:
            codes = path.codes

        n_polygons = np.equal(codes, Path.MOVETO).sum()

        # Close the path (only if 1 polygon present)
        if n_polygons == 1 and (x[0] != x[-1] or y[0] != y[-1]):
            x = np.concatenate([x, [x[0]]])
            y = np.concatenate([y, [y[0]]])

            if codes[-1] == Path.CLOSEPOLY:
                codes = np.concatenate([codes[:-1], [Path.LINETO, Path.CLOSEPOLY]])
            else:
                codes = np.concatenate([codes, [Path.CLOSEPOLY]])

        return np.transpose([x, y]), codes

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

        """
        return None if path is None else Path(*self.vc(path))

    def xy_patch(self, patch):
        """Convert patch vertices in map coordinates.

        Parameters
        ----------
        patch: matplotlib.patches.Patch
            Matplotlib patch in east-longitude and latitude coordinates.

        Returns
        -------
        matplotlib.patches.Patch
            Patch in map coordinates.

        Note
        ----
        Only face and edge colors are preserved.

        """
        return PathPatch(
            self.xy_path(patch.get_path()),
            alpha=patch.get_alpha(),
            facecolor=patch.get_fc(),
            edgecolor=patch.get_ec(),
            linewidth=patch.get_linewidth(),
            linestyle=patch.get_linestyle(),
            zorder=patch.get_zorder(),
            label=patch.get_label(),
        )

    def xy_collection(self, collection):
        """Convert collection vertices in map coordinates.

        Parameters
        ----------
        collection: matplotlib.collections.PatchCollection or \
                    matplotlib.collections.PathCollection
            Matplotlib collection in west-longitude and latitude coordinates.

        Returns
        -------
        PatchCollection or PathCollection
            Collection in map coordinates.

        """
        kwargs = {
            'alpha': collection.get_alpha(),
            'facecolors': collection.get_facecolor(),
            'edgecolors': collection.get_edgecolor(),
            'linewidth': collection.get_linewidth(),
            'linestyle': collection.get_linestyle(),
            'zorder': collection.get_zorder(),
            'label': collection.get_label(),
        }

        if isinstance(collection, PathCollection):
            paths = collection.get_paths()
            offsets = collection.get_offsets()
            sizes = collection.get_sizes()

            # Reshape paths and offsets
            if len(paths) == 1 and len(offsets) > 1:
                paths = len(offsets) * list(paths)

            elif len(paths) > 1 and len(offsets) == 1:
                offsets = len(paths) * list(offsets)

            elif len(paths) != len(offsets):
                raise ValueError(
                    'Paths and offsets must have the same size: '
                    f'{len(paths)} vs. {len(offsets)}'
                )

            # Set default sizes, if not provided
            if sizes.size == 0:
                sizes = np.full((len(paths),), 4)

            elif len(sizes) == 1 and len(paths) > 1:
                sizes = len(paths) * list(sizes)

            elif len(paths) != len(sizes):
                raise ValueError(
                    'Paths and sizes must have the same size: '
                    f'{len(paths)} vs. {len(sizes)}'
                )

            coll = PathCollection(
                [
                    self.xy_path(
                        Path(path.vertices * np.sqrt(size) / 2 + offset, codes=path.codes)
                    )
                    if path is not None
                    else None
                    for path, offset, size in zip(paths, offsets, sizes, strict=False)
                ],
                **kwargs,
            )

            if collection.get_array() is not None:
                coll.set_array(collection.get_array())
                coll.set_cmap(collection.get_cmap())
                coll.set_norm(collection.norm)
                coll.set_edgecolor(None)

            return coll

        # Regular PatchCollection object
        return PatchCollection(
            [PathPatch(self.xy_path(path)) for path in collection.get_paths()], **kwargs
        )

    def meridians(
        self,
        lons_e=None,
        exclude=None,
        lon_e_min=0,
        lon_e_max=360,
        dlon_e=30,
        lat_min=-80,
        lat_max=80,
        nlat=65,
    ):
        """Projected meridians grid."""
        if lons_e is None:
            nlon_e = int((lon_e_max - lon_e_min) / dlon_e)
            lons_e = np.linspace(lon_e_min, lon_e_max, nlon_e + 1)

        elif isinstance(lons_e, (int, float)):
            lons_e = [lons_e]

        if exclude is None or isinstance(exclude, (int, float)):
            exclude = [] if exclude is None else [exclude]

        lats = np.linspace(lat_min, lat_max, nlat)

        return np.moveaxis(
            [self(lon_e, lats) for lon_e in lons_e if lon_e not in exclude], 0, 2
        )

    def parallels(
        self,
        lats=None,
        exclude=None,
        lat_min=-80,
        lat_max=80,
        dlat=10,
        lon_e_min=0,
        lon_e_max=360,
        nlon_e=73,
    ):
        """Projected parallels grid."""
        if lats is None:
            nlat = int((lat_max - lat_min) / dlat)
            lats = np.linspace(lat_min, lat_max, nlat + 1)

        elif isinstance(lats, (int, float)):
            lats = [lats]

        if exclude is None or isinstance(exclude, (int, float)):
            exclude = [] if exclude is None else [exclude]

        lons_e = np.linspace(lon_e_min, lon_e_max, nlon_e)

        return np.moveaxis(
            [self(lons_e, lat) for lat in lats if lat not in exclude], 0, 2
        )


class GroundProjection(Projection):
    """Abstract ground projection object.

    Parameters
    ----------
    lon_e_0: float, optional
        Center east longitude.
    lat_0: float, optional
        Center latitude.
    target: str
        Body name.
    radius: float, optional
        Body radius [km].

    """

    DEFAULT_RADIUS_KM = 1e-3  # = 1 [m]

    def __init__(self, lon_e_0=0, lat_0=0, target=None, radius=None):
        self.lon_e_0 = lon_e_0
        self.lat_0 = lat_0
        self.target = target
        self.radius = radius

    def __repr__(self):
        return f'<{self}> Target: {self.target}\n\tProj4: `{self.proj4}`'

    @property
    def lat_0(self):
        """Latitude of origin [degree]."""
        return self.__lat_0

    @lat_0.setter
    def lat_0(self, value):
        """Set latitude of origin value."""
        self.__lat_0 = value
        self.__clat0, self.__slat0 = cs(value)

    @property
    def clat0(self):
        """Cosine of latitude of origin."""
        return self.__clat0

    @property
    def slat0(self):
        """Sine of latitude of origin."""
        return self.__slat0

    @property
    def lon_e_0(self):
        """East central meridian [degree]."""
        return self.__lon_e_0

    @lon_e_0.setter
    def lon_e_0(self, value):
        """Set east central meridian value."""
        self.__lon_e_0 = value % 360
        self.__clon0_e, self.__slon0_e = cs(value)

    @property
    def clon0_e(self):
        """Cosine of west central meridian."""
        return self.__clon0_e

    @property
    def slon0_e(self):
        """Sine of west central meridian."""
        return self.__slon0_e

    @property
    def target(self):
        """Body target."""
        return self.__target

    @target.setter
    def target(self, name):
        """Set target name."""
        self.__target = 'Undefined' if name is None else name

    @property
    def radius(self):
        """Target body radius [km]."""
        return self.__r * 1e-3

    @radius.setter
    def radius(self, value_km):
        """Set radius and convert from [km] to [m]."""
        if value_km is None:
            self.__r = self.DEFAULT_RADIUS_KM * 1e3
        else:
            self.__r = value_km * 1e3

    @property
    def r(self):
        """Target body radius [m]."""
        return self.__r

    @property
    def proj4(self):
        """Proj4 definition."""
        return ' '.join([
            f'+proj={self.PROJ4}',
            f'+lat_0={self.lat_0}',
            f'+lon_0={self.lon_e_0}',
            '+k=1',
            '+x_0=0',
            '+y_0=0',
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
            'PARAMETER["false_easting", 0],'
            'PARAMETER["false_northing", 0],'
            'PARAMETER["scale_factor", 1],'
            f'PARAMETER["central_meridian", {self.lon_e_0}],'
            f'PARAMETER["latitude_of_origin", {self.lat_0}],'
            'UNIT["Meter", 1]]'
        )
