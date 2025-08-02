"""Great circle module."""

import numpy as np

from matplotlib.patches import PathPatch
from matplotlib.path import Path

from .vectors import angle, lonlat, xyz


MIN_LON_E_POLE = 90  # Pole min east-longitude for great_circle_pole_pts


def great_circle_arc(lon_e_1, lat_1, lon_e_2, lat_2, npt=361):
    """Great circle arc coordinates between 2 anchor points.

    Use Slerp interpolation.

    Parameters
    ----------
    lon_e_1: float
        East longitude of the first point (°).
    lat_1: float
        Latitude of the first point (°).
    lon_e_2: float
        East longitude of the second point (°).
    lat_2: float
        Latitude of the second point (°).
    npt: int, option
        Number of points in the great circle.

    Raises
    ------
    ValueError
        If the two longitudes are on the same meridian (±180°).

    """
    pt1 = xyz(lon_e_1, lat_1)
    pt2 = xyz(lon_e_2, lat_2)
    omega = np.radians(angle(pt1, pt2))
    s = np.sin(omega)

    if s == 0:
        raise ValueError(
            'Infinity of solutions. Point 1 and 2 are aligned (0° or ±180°).'
        )

    t = np.transpose([np.linspace(0, 1, npt)])
    v = (np.sin((1 - t) * omega) * pt1 + np.sin(t * omega) * pt2) / s

    return lonlat(v)


def great_circle_lat(lon_e, lon_e_1, lat_1, lon_e_2, lat_2):
    """Great circle latitude through 2 points.

    Source: https://edwilliams.org/avform.htm

    Parameters
    ----------
    lon_e: float or numpy.array
        Input east longitude on the great circle (°).
    lon0: float
        East longitude of the first point (°).
    lat0: float
        Latitude of the first point (°).
    lon_e_1: float
        East longitude of the second point (°).
    lat_1: float
        Latitude of the second point (°).

    Returns
    -------
    float or numpy.array
        Great circle latitude for the longitude provided.

    Raises
    ------
    ValueError
        If the two longitudes are on the same meridian (±180°).

    """
    if (lon_e_2 - lon_e_1) % 180 == 0:
        raise ValueError(
            'Infinity of solutions. Longitudes 1 and 2 are on the same meridian (±180°).'
        )

    lon_e = np.asarray(lon_e)
    s1, s2 = np.sin(np.radians([lon_e_1 - lon_e, lon_e_2 - lon_e]))
    s12 = np.sin(np.radians(lon_e_2 - lon_e_1))
    t1, t2 = np.tan(np.radians([lat_1, lat_2]))
    return np.degrees(np.arctan((t1 * s2 - t2 * s1) / s12))


def great_circle(lon_e_1, lat_1, lon_e_2, lat_2, npt=361):
    """Great circle through 2 points.

    Parameters
    ----------
    lon0: float
        East longitude of the first point (°).
    lat0: float
        Latitude of the first point (°).
    lon_e_1: float
        East longitude of the second point (°).
    lat_1: float
        Latitude of the second point (°).
    npt: int, optional
        Number of points on the great circle.

    Returns
    -------
    numpy.array
        Great circle coordinates.

    """
    lons_e = np.linspace(0, 360, npt)
    lats = great_circle_lat(lons_e, lon_e_1, lat_1, lon_e_2, lat_2)

    return np.array([lons_e, lats])


def great_circle_pole_pts(lon_e_p, lat_p):
    """Find two orthogonal points on the great circle from its polar axis.

    Parameters
    ----------
    lon_e_p: float
        Polar axis east longitude (°).
    lat_p: float
        Polar axis latitude (°).

    Returns
    -------
    float
        East longitude of first orthogonal point (with the same longitude).
    float
        Latitude of first orthogonal point (with the same longitude).
    float
        East longitude of second orthogonal point (crossing the equator).
    float
        Latitude of second orthogonal point (crossing the equator).

    """
    lon_1 = lon_e_p
    lon_2 = (lon_e_p + 90) % 360 if lon_e_p >= MIN_LON_E_POLE else (lon_e_p - 90) % 360

    lat_1 = lat_p - 90 if lat_p >= 0 else lat_p + 90
    lat_2 = 0

    return lon_1, lat_1, lon_2, lat_2


def great_circle_pole_lat(lon_e, lon_e_p, lat_p):
    """Great circle latitude from its polar axis.

    Parameters
    ----------
    lon_e: float or numpy.array
        Input east longitude on the great circle (°).
    lon_e_p: float
        Polar axis east longitude (°).
    lat_p: float
        Polar axis latitude (°).

    Returns
    -------
    float or numpy.array
        Great circle latitude for the longitude provided.

    """
    return great_circle_lat(lon_e, *great_circle_pole_pts(lon_e_p, lat_p))


def great_circle_pole(lon_e_p, lat_p, npt=361):
    """Great circle from its polar axis.

    Parameters
    ----------
    lon_e_p: float
        Polar axis east longitude (°).
    lat_p: float
        Polar axis latitude (°).
    npt: int, optional
        Number of points on the great circle.

    Returns
    -------
    numpy.array
        Great circle coordinates.

    """
    lons_e = np.linspace(0, 360, npt)
    lats = great_circle_pole_lat(lons_e, lon_e_p, lat_p)

    return np.array([lons_e, lats])


def great_circle_path(lon_e_p, lat_p, npt=361, inside=True):
    """Great circle path from its polar axis.

    Parameters
    ----------
    lon_e_p: float
        Polar axis east longitude (°).
    lat_p: float
        Polar axis latitude (°).
    npt: int, optional
        Number of points on the great circle.
    inside: bool, optional
        Close polygon around the polar point if ``TRUE`` (default),
        or around the anti-pole if ``FALSE``.

    Returns
    -------
    matplotlib.path.Path
        Great circle path.

    """
    lons_e, lats = great_circle_pole(lon_e_p, lat_p, npt=npt)

    pole = 90 if (inside and lat_p >= 0) or (not inside and lat_p <= 0) else -90

    vertices = np.vstack([
        [*lons_e, lons_e[-1], lons_e[0], lons_e[0]],
        [*lats, pole, pole, lats[0]],
    ])

    codes = [Path.MOVETO] + [Path.LINETO] * (npt + 1) + [Path.CLOSEPOLY]

    return Path(vertices.T, codes)


def great_circle_patch(lon_p, lat_p, npt=361, inside=True, **kwargs):
    """Great circle patch from its polar axis.

    Parameters
    ----------
    lon_p: float
        Polar axis east longitude (°).
    lat_p: float
        Polar axis latitude (°).
    npt: int, optional
        Number of points on the great circle.
    inside: bool, optional
        Close polygon around the polar point if ``TRUE`` (default),
        or around the anti-pole if ``FALSE``.

    Returns
    -------
    matplotlib.patches.PathPatch
        Great circle patch.

    """
    path = great_circle_path(lon_p, lat_p, npt=npt, inside=inside)
    return PathPatch(path, **kwargs)
