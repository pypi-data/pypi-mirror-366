"""SPICE instrument module."""

from itertools import cycle, repeat

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, Polygon

import spiceypy as sp
from spiceypy.utils.exceptions import SpiceFRAMEMISSING

from ..math.vectors import boresight_rot_m, cs, norm
from ..misc import cached_property


TWO_ELEMENTS = 2


class SpiceFieldOfView:
    """SPICE Instrument field of view object.

    Parameters
    ----------
    code: int
        SPICE instrument code.

    See Also
    --------
    spiceypy.spiceypy.getfov

    """

    MARGIN = 1.1  # X and Y limit margins

    def __init__(self, code):
        try:
            self.shape, self._frame, self.boresight, _, self.bounds = sp.getfov(
                int(code), 100
            )

        except SpiceFRAMEMISSING:
            raise ValueError(
                f'Instrument `{int(code)}` does not have a valid FOV.'
            ) from None

    def __repr__(self):
        s = f'<{self.__class__.__name__}> '
        s += f'Frame: {self.frame} | ' if self.frame else ''
        s += f'Boresight: {np.round(self.boresight, 3)} | '
        s += f'Shape: {self.shape} | '
        s += f'Bounds:\n{np.round(self.bounds, 3)}'
        return s

    @property
    def frame(self):
        """Field of view reference frame."""
        return self._frame

    @cached_property
    def m(self):
        """Boresight rotation matrix."""
        return boresight_rot_m(self.boresight)

    def to_boresight(self, *vec):
        """Rotate a vector in the plane orthogonal to the boresight.

        The vector(s) is/are rotated to be in the plane orthogonal to the boresight
        with a unit length in the z-direction.

        Parameters
        ----------
        *vec: tuple or numpy.ndarray
            Input vector(s) to rotate.

        """
        x, y, z = self.m @ np.transpose(vec)
        invalid = z == 0
        np.divide(x, z, out=x, where=~invalid)
        np.divide(y, z, out=y, where=~invalid)
        x[invalid] = np.nan
        y[invalid] = np.nan
        return np.array([x, y])

    @cached_property
    def corners(self):
        """Boundaries corners in the plane orthogonal to the boresight."""
        return self.to_boresight(*self.bounds)

    @cached_property(parent='corners')
    def extent(self):
        """Boundaries extent in the plane orthogonal to the boresight."""
        if self.shape == 'CIRCLE':
            r = norm(self.corners.T)[0]
            return [-r, r, -r, r]

        if self.shape == 'ELLIPSE':
            a, b = np.max(np.abs(self.corners), axis=1)
            return [-a, a, -b, b]

        xmin, ymin = np.min(self.corners, axis=1)
        xmax, ymax = np.max(self.corners, axis=1)

        return [xmin, xmax, ymin, ymax]

    @property
    def xlim(self):
        """Boundary x-limits in the plane orthogonal to the boresight."""
        return self.MARGIN * self.extent[0], self.MARGIN * self.extent[1]

    @property
    def ylim(self):
        """Boundary y-limits in the plane orthogonal to the boresight."""
        return self.MARGIN * self.extent[2], self.MARGIN * self.extent[3]

    def from_boresight(self, *xy):
        """Rotate a vector from the boresight plane to the instrument frame.

        Parameters
        ----------
        *xy: tuple or numpy.ndarray
            Input boresight unitary boresight vector(s).

        """
        vec = np.ones((3, len(xy)))
        vec[:2] = np.transpose(xy)
        return (self.m.T @ vec).T

    def rays(self, npt=24):
        """Interpolated rays around the FOV in the instrument frame.

        The points are interpolated in the plane orthogonal to the
        boresight at a unitary distance to the center and re-aligned
        with the boresight.

        Parameters
        ----------
        npt: int or tuple, optional
            Number of rays in the interpolated contour.

            If the FOV has a ``RECTANGULAR`` and ``POLYGON`` shape,
            it is possible to provide a tuple that will correspond
            to the number of points per edges (excluding the corners).
            If the tuple size is smaller than the number of edges,
            its values will be cycled.

        Returns
        -------
        numpy.ndarray
            Field of view contour rays, shape: (npt, 3).

            If npt is a tuple, you need to compute how many
            points were added per edge to get to total number
            of points in the contour.

        Note
        ----
        The points will be distributed evenly and the final number of
        points may be slightly lower than the requested count.

        """
        match self.shape:
            case 'CIRCLE':
                xy = self.rays_circle(self.extent[1], npt)
            case 'ELLIPSE':
                xy = self.rays_ellipse(self.extent[1], self.extent[3], npt)
            case 'RECTANGLE' | 'POLYGON':
                xy = self.rays_edges(self.corners.T, npt)

        return self.from_boresight(*xy)

    @staticmethod
    def rays_circle(r, npt):
        """Interpolated rays around a CIRCLE FOV.

        Parameters
        ----------
        r: float, optional
            Circle radius.
        npt: int
            Number of points in the interpolated contour.

        Returns
        -------
        numpy.ndarray
            Interpolated coordinates in the XY plane.

        """
        angle = np.linspace(0, 360, max(npt, 1), endpoint=False)
        return r * np.transpose(cs(angle))

    @staticmethod
    def rays_ellipse(a, b, npt):
        """Interpolated rays around a ELLIPSE FOV.

        Parameters
        ----------
        a: float, optional
            Ellipse primary axis.
        b: float, optional
            Ellipse secondary axis.
        npt: int
            Number of points in the interpolated contour.

        Returns
        -------
        numpy.ndarray
            Interpolated coordinates in the XY plane.

        """
        match npt:
            case 0 | 2:
                angles = np.array([0, 90])  # Points on primary axes only
            case _:
                angles = np.linspace(0, 360, max(npt, 1), endpoint=False)

        ct, st = cs(angles)
        e2 = 1 - (b / a) ** 2
        r = b / np.sqrt(1 - e2 * ct**2)
        return np.transpose([r * ct, r * st])

    @staticmethod
    def rays_edges(corners, npt):
        """Interpolated rays around a RECTANGULAR or POLYGON FOV.

        Parameters
        ----------
        corners: list
            List of FOV corners coordinates.
        npt: int or tuple
            Number of points around the contour **including the corners**.
            If npt <= len(corners), no interpolation will be performed.
            If npt > len(corners), they will be evenly distributed on each edge,
            then the final number of points on the contour may be smaller than npt.

            If npt is provided as a tuple, it will correspond to the number of
            **interpolation points** to be added on each edges between the corners.
            If len(npt) < len(corners) it will be cycled though each edges.

        Returns
        -------
        numpy.ndarray
            Interpolated coordinates in the XY plane.

        """
        n_corners = len(corners)

        if isinstance(npt, int):
            iter_npt = repeat((npt - n_corners) // n_corners)
        else:
            iter_npt = cycle(npt)

        return np.vstack([
            np.linspace(
                corners[i],
                corners[i + 1 if i + 1 < n_corners else 0],
                max(n, 0) + 1,
                endpoint=False,
            )
            for i, n in zip(range(n_corners), iter_npt, strict=False)
        ])

    def contour(self, npt=25):
        """FOV footprint contour.

        Parameters
        ----------
        npt: int or tuple, optional
            Number of points in the interpolated contour (default: `25`).
            The minimum of points is 9 to properly represent the CIRCLE
            and ELLIPSE shapes.

            If tuple is provided, it will be used to split the edges recursively.

        See Also
        --------
        .rays

        """
        ray = self.rays(npt=max(npt - 1, 8) if isinstance(npt, int) else npt)
        return np.transpose([*ray, ray[0]])

    def patch(self, **kwargs):
        """FOV patch in the plane orthogonal to the boresight.

        Parameters
        ----------
        **kwargs: any
            Matplotlib artist optional keywords.

        Returns
        -------
        matplotlib.patches.Circle or matplotlib.patches.PathPatch
            Matplotlib Patch.

        """
        if self.shape == 'CIRCLE':
            r = self.extent[0]
            return Circle((0, 0), r, **kwargs)

        if self.shape == 'ELLIPSE':
            a, b = self.extent[1], self.extent[3]
            return Ellipse((0, 0), 2 * a, 2 * b, **kwargs)

        return Polygon(self.corners.T, closed=False, **kwargs)

    def view(self, ax=None, fig=None, **kwargs):
        """2D display field of view in the plane perpendicular to the boresight.

        Parameters
        ----------
        ax: matplotlib.axes.Axes, optional
            Axis to incrust the plot.
        fig: matplotlib.figure.Figure, optional
            Main figure (if no :attr:`ax` is provided).
        **kwargs: any
            Matplotlib keyword attributes pass to
            :class:`matplotlib.patches.Patch`.

        Returns
        -------
        matplotlib.axes
            FOV view

        """
        if ax is None:
            if fig is None:
                fig = plt.figure(figsize=(10, 10))

            ax = fig.add_subplot()

        if 'alpha' not in kwargs:
            kwargs['alpha'] = 0.5

        ax.plot(0, 0, 'o', color='tab:red')
        ax.plot(*self.corners, 'o', color='tab:blue')
        ax.add_patch(self.patch(**kwargs))

        ax.set_aspect(1)
        ax.set_xlim(*self.xlim)
        ax.set_ylim(*self.ylim)
        ax.set_axis_off()

        ax.set_title(getattr(self, 'name', ''))

        return ax

    def display(self, ax=None, fig=None, npt=25, show_bounds=False, **kwargs):
        """3D display field of view with its the boresight.

        Parameters
        ----------
        ax: matplotlib.axes.Axes, optional
            Axis to incrust the plot.
        fig: matplotlib.figure.Figure, optional
            Main figure (if no :attr:`ax` is provided).
        npt: int, optional
            Number of points in the interpolated contour (default: ``25``).

        Returns
        -------
        matplotlib.axes
            FOV view

        """
        if ax is None:
            if fig is None:
                fig = plt.figure(figsize=(8, 8))

            ax = fig.add_subplot(projection='3d')

        if ax.name != '3d':
            raise KeyError('Axis must be a projection 3D axis.')

        ax.quiver(0, 0, 0, *self.boresight, color='tab:red', arrow_length_ratio=0)

        if show_bounds:
            for bound in self.bounds:
                ax.quiver(
                    0, 0, 0, *bound, color='tab:orange', ls='-', arrow_length_ratio=0
                )

        for ray in self.rays(0):
            ax.quiver(
                0, 0, 0, *ray, color='tab:orange', lw=1, ls='--', arrow_length_ratio=0
            )

        ax.plot(*self.contour(npt=npt), '-', color='tab:blue')

        ax.set_title(getattr(self, 'name', ''))

        return ax
