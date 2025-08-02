"""Trajectory instrument field of view (FOV) module."""

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from matplotlib.colors import Normalize
from matplotlib.path import Path

from ..misc import cached_property, logger, warn
from ..spice import check_kernels
from ..spice.toolbox import fov_pts, rlonlat


log_fovs, debug_fovs = logger('Trajectory FOVs')


class FovsCollection:
    """Instrument field of views collection.

    Parameters
    ----------
    traj: InstrumentTrajectory
        Input instrument trajectory.
    npts: int or tuple, optional
        Number of points in the FOV contour (default: 25).
        If the FOV has a ``RECTANGULAR`` and ``POLYGON`` shape,
        it is possible to provide a tuple that will correspond
        to the number of points per edges (excluding the corners).
        If the tuple size is smaller than the number of edges,
        its values will be cycled.
    limb_contour: bool, optional
        Compute the intersection on the limb impact parameter
        if no intersection with the surface was found (default: True)

    .. deprecated:: 1.2.0
        `limb` parameter was replaced with `limb_contour`.

    """

    def __init__(self, traj, npts=25, limb_contour=True, limb=None):
        self.traj = traj
        self.npts = npts

        # Depreciated since 1.2.0
        if limb is not None:
            warn.warning('`limb` parameter is depreciated. Use `limb_contour` instead. ')
            limb_contour = limb

        self.limb_contour = limb_contour

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}> '
            f'Observer: {self.observer} | '
            f'Target: {self.target} | '
            f'Nb of pts: {len(self.traj)} | '
            f'Contour pts: {self.npts} | '
            f'Limb contour: {self.limb_contour}'
        )

    def __call__(self, *args, **kwargs):
        return self.collection(*args, **kwargs)

    def __hash__(self):
        """Kernels hash."""
        return hash(self.traj)

    @property
    def kernels(self):
        """Trajectory required kernels."""
        return self.traj.kernels

    @property
    def observer(self):
        """Trajectory observer."""
        return self.traj.observer

    @property
    def target(self):
        """Trajectory target."""
        return self.traj.target

    @property
    def npts(self):
        """Number of points in the FOV contour."""
        return self.__npts

    @npts.setter
    def npts(self, n):
        """FOV contour number of points setter.

        If the FOV has a ``RECTANGULAR`` and ``POLYGON`` shape,
        it is possible to provide a tuple that will correspond
        to the number of points per edges (excluding the corners).
        If the tuple size is smaller than the number of edges,
        its values will be cycled.

        """
        del self.pts
        self.__npts = n

    @property
    def limb_contour(self):
        """Is the FOV should include the intersection points above the limb."""
        return self.__limb_contour

    @limb_contour.setter
    def limb_contour(self, cond):
        """Limb intersecting setter."""
        del self.pts
        self.__limb_contour = cond

    @cached_property
    @check_kernels
    def pts(self):
        """Instrument FOV points.

        Note
        ----
        Currently the intersection method is fixed internally
        as ``method='ELLIPSOID'``.

        """
        log_fovs.debug('Compute FOV intersection points.')
        res = fov_pts(
            self.traj.ets,
            self.observer,
            self.target,
            limb=self.limb_contour,
            npt=self.npts - 1 if isinstance(self.npts, int) else self.npts,
            abcorr=self.traj.abcorr,
            method='ELLIPSOID',
        )

        # Close the polygon
        res = np.dstack([res, res[..., 0]])

        log_fovs.debug('Result: %r', res)
        return res

    @cached_property(parent='pts')
    def rlonlat(self):
        """Instrument FOV intersect coordinates.

        Returns
        -------
        np.ndarray
            Boresight surface intersect planetocentric coordinates:
            radii, east longitudes and latitudes.

        See Also
        --------
        .pts

        """
        log_fovs.debug('Compute FOV intersects planetocentric coordinates.')
        return rlonlat(self.pts[:-1])

    @property
    def surface(self):
        """Boolean array when the contour points intersect the target surface."""
        return self.pts[-1].astype(np.bool)

    @property
    def surface_any(self):
        """Boolean array when at least one point intersects the target surface."""
        return self.surface.any(axis=-1)

    @property
    def surface_all(self):
        """Boolean array when at all points intersect the target surface."""
        return self.surface.all(axis=-1)

    @property
    def limb(self):
        """Boolean array when the contour points are above the limb."""
        return ~self.surface

    @property
    def limb_any(self):
        """Boolean array when at least one point is above the limb."""
        return self.limb.any(axis=-1)

    @property
    def limb_all(self):
        """Boolean array when at all points are above the limb."""
        return self.limb.all(axis=-1)

    @cached_property(parent='rlonlat')
    def paths(self):
        """Instrument FOV surface paths.

        Note
        ----
        If all the points are above the limb the path is set to ``None``.

        See Also
        --------
        .rlonlat

        """
        log_fovs.debug('Compute FOV paths.')

        return np.where(
            self.surface_any,
            [Path(lonlat[..., 1:]) for lonlat in np.moveaxis(self.rlonlat, 0, -1)],
            None,
        )

    def get_colors(self, attr, cmap='turbo_r', vmin=None, vmax=None):
        """Get colors for a given attribute and an optional range.

        Parameters
        ----------
        attr: str
            Attribute to color.
        vmin: int or float, optional
            Color scaling min value. If ``None`` is provided (default)
            the data are scaled to the lowest (not-NaN) value.
        vmax: int or float, optional
            Color scaling max value. If ``None`` is provided (default)
            the data are scaled to the lowest (not-NaN) value.
        cmap: str, optional
            Matplotlib colormap name (default: ``turbo_r``)

        Returns
        -------
        str
            If the attribute is not part of the trajectory (e.g. pure color string).

        numpy.ndarray
            Normalized RGB color array.

        Raises
        ------
        ValueError
            If the data to represent is not a 1D array.

        """
        if not isinstance(attr, str) or not hasattr(self.traj, attr):
            return attr

        data = getattr(self.traj, attr)

        if np.ndim(data) != 1:
            raise ValueError('The data need to be a 1D array.')
        if vmin is None:
            vmin = np.nanmin(data)
        if vmax is None:
            vmax = np.nanmax(data)

        cmap = plt.get_cmap(cmap)
        norm = Normalize(vmin, vmax)

        return cmap(norm(data))

    def isort(self, attr, reverse=None):
        """Get sorting indexes for a given attribute."""
        if not isinstance(attr, str) or not hasattr(self.traj, attr):
            raise KeyError(f'Unknown attribute `{attr}` in Trajectory.')

        order = np.argsort(getattr(self.traj, attr))

        if reverse is None:
            # The order is reversed by default for `inc`, `dist` and `alt`
            reverse = attr in {'inc', 'dist', 'alt'}

        return order[::-1] if reverse else order

    def collection(
        self,
        edgecolors=None,
        facecolors='none',
        vmin=None,
        vmax=None,
        cmap='turbo_r',
        label=None,
        sort=None,
        reverse=None,
        **kwargs,
    ) -> PathCollection:
        """Instrument field of view paths collection.

        Parameters
        ----------
        edgecolors: str, optional
            Color of the patch contours.
            This could be a :class:`.Trajectory` property.
        facecolors: str, optional
            Color of the patch face.
            This could be a :class:`.Trajectory` property.
        vmin: int or float
            Color scaling min value. If ``None`` is provided (default)
            the data are scaled to the lowest (not-NaN) value.
        vmax: int or float
            Color scaling max value. If ``None`` is provided (default)
            the data are scaled to the lowest (not-NaN) value.
        cmap: str, optional
            Matplotlib colormap name (default: ``turbo_r``)
        label: str, optional
            Collection legend label (default: observer name).
        sort: str, optional
            Patches sorting on display (default: ``utc``).
        reverse: bool, optional
            Reverse patches sorting (default: ``False``).
        **kwargs:
            Keyword attributes for :class:`matplotlib.collections.PathCollection`.

        """
        paths = self.paths

        colors = {'cmap': cmap, 'vmin': vmin, 'vmax': vmax}
        facecolors = self.get_colors(facecolors, **colors)
        edgecolors = self.get_colors(edgecolors, **colors)

        if sort:
            ind = self.isort(sort, reverse=reverse)
            paths = np.array(paths)[ind]
            if isinstance(facecolors, np.ndarray):
                facecolors = facecolors[ind, ...]
            if isinstance(edgecolors, np.ndarray):
                edgecolors = edgecolors[ind, ...]

        if label is None:
            label = str(self.observer).replace('_', ' ')

        kwargs.update({
            'paths': paths,
            'facecolors': facecolors,
            'edgecolors': edgecolors,
            'label': label,
        })

        return PathCollection(**kwargs)

    def get_paths(self):
        """Collection paths."""
        return self.paths

    @staticmethod
    def get_alpha(default=None):
        """Default transparencies."""
        return default

    @staticmethod
    def get_facecolor(default='tab:orange'):
        """Default facecolors."""
        return default

    @staticmethod
    def get_edgecolor(default=None):
        """Default edgecolors."""
        return default

    @staticmethod
    def get_linewidth(default=1.5):
        """Default linewidth."""
        return default

    @staticmethod
    def get_linestyle(default='solid'):
        """Default linestyle."""
        return default

    @staticmethod
    def get_zorder(default=1):
        """Default zorder."""
        return default

    @staticmethod
    def get_label(default=''):
        """Default label."""
        return default


class MaskedFovsCollection(FovsCollection):
    """Masked field of views collection."""

    def __init__(self, fovs, mask):
        super().__init__(fovs.traj, npts=fovs.npts, limb=fovs.limb)
        self.mask = mask

    @cached_property
    def paths(self):
        """Masked instrument FOV surface paths.

        Note
        ----
        If all the points are above the limb the path is set to ``None``.

        """
        return [
            None if masked else path
            for path, masked in zip(self.traj.fovs.paths, self.mask, strict=False)
        ]


class SegmentedFovsCollection(FovsCollection):
    """Segmented field of views collection."""
