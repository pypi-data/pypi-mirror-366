"""Vector module.

Warning
-------
All the longitude are defined eastward.

"""

import numpy as np


NDIM_3D = 3  # 3D data


def cs(angle):
    """Cosines and sines value of an angle (°).

    Parameters
    ----------
    angle: float or numpy.ndarray
        Input angle(s) (°).

    Returns
    -------
    float or numpy.ndarray
        Cosine and Sines of this angle(s).

    Examples
    --------
    >>> cs(0)
    1, 0
    >>> cs(45)
    0.707..., 0.707...


    """
    theta = np.radians(angle)
    return np.cos(theta), np.sin(theta)


def norm(v):
    """Vector norm.

    Parameters
    ----------
    v: numpy.ndarray
        Input vector to measure(s).

    Returns
    -------
    float or numpy.ndarray
        Input vector norm(s).

    Examples
    --------
    >>> norm([1, 0, 0])
    1
    >>> norm([1, 1, 1])
    1.732050...

    """
    return np.linalg.norm(v, axis=-1)


def hat(v):
    """Normalize vector.

    Parameters
    ----------
    v: numpy.ndarray
        Input vector to normalize.

    Returns
    -------
    numpy.ndarray
        Normalize input vector.

    Examples
    ---------
    >>> hat([1, 0, 0])
    array([1., 0., 0.])
    >>> hat([1, 1, 1])
    array([0.577..., 0.577..., 0.577...])

    """
    n = norm(v)
    inv = np.divide(1, n, out=np.zeros_like(n), where=n != 0)
    return np.multiply(np.expand_dims(inv, axis=-1), v)


def lonlat(xyz):
    """Convert cartesian coordinates into geographic coordinates.

    Parameters
    ----------
    xyz: numpy.ndarray
        XYZ cartesian vector.

    Return
    ------
    (float, float)
        East Longitude [0°, 360°[ and North Latitude (°).

    Examples
    --------
    >>> lonlat([1, 0, 0])
    (0, 0)
    >>> lonlat([0, 1, 0])
    (90, 0)
    >>> lonlat([1, 1, 0])
    (45, 0)
    >>> lonlat([1, 0, 1])
    (0, 45)

    """
    (x, y, z), n = np.transpose(xyz), norm(xyz)
    cond = n != 0
    lon_e = np.degrees(np.arctan2(y, x), where=cond, out=np.zeros_like(n)) % 360
    lat = np.degrees(np.arcsin(np.divide(z, n, where=cond, out=np.zeros_like(n))))
    return np.array([lon_e.T, lat.T])


def xyz(lon_e, lat, r=1):
    """Convert geographic coordinates in cartesian coordinates.

    Parameters
    ----------
    lon_e: float or numpy.ndarray
        Point(s) east longitude [0°, 360°[.
    lat: float or numpy.ndarray
        Point(s) latitude [-90°, 90°].
    r: float or numpy.ndarray, optional
        Point(s) distance/altitude [km].

    Return
    ------
    [float, float, float]
        Cartesian coordinates.

    Examples
    --------
    >>> xyz(0, 0)
    [1, 0, 0]
    >>> xyz(90, 0)
    [0, 1, 0]
    >>> xyz(45, 0)
    [0.707..., 0.707..., 0]
    >>> xyz(0, 45)
    [0.707..., 0, 0.707...]

    """
    _1d = np.ndim(lon_e) > 0 or np.ndim(lat) > 0 or np.ndim(r) > 0
    _2d = np.ndim(lon_e) > 1 or np.ndim(lat) > 1 or np.ndim(r) > 1

    if np.ndim(lon_e) > 0 and np.ndim(lat) == 0:
        lat = np.broadcast_to(lat, np.shape(lon_e))

    elif np.ndim(lon_e) == 0 and np.ndim(lat) > 0:
        lon_e = np.broadcast_to(lon_e, np.shape(lat))

    elif np.ndim(lon_e) == 0 and np.ndim(lat) == 0 and np.ndim(r) > 0:
        lon_e = np.broadcast_to(lon_e, np.shape(r))
        lat = np.broadcast_to(lat, np.shape(r))

    (clon_e, slon_e), (clat, slat) = cs(lon_e), cs(lat)

    v = np.multiply(r, [clon_e * clat, slon_e * clat, slat])

    return np.moveaxis(v, 0, 2) if _2d else v.T if _1d else v


def vdot(v1, v2):
    """Dot product between two vectors."""
    if np.ndim(v1) == 1 and np.ndim(v2) == 1:
        return np.dot(v1, v2)

    if np.ndim(v1) == 1:
        return np.dot(v2, v1)

    if np.ndim(v2) == 1:
        return np.dot(v1, v2)

    if np.shape(v1)[1:] == np.shape(v2)[1:]:
        return np.sum(np.multiply(v1, v2), axis=-1)

    raise ValueError('The two vectors must have the same number of points.')


def angle(v1, v2):
    """Angular separation between two vectors."""
    dot = vdot(hat(v1), hat(v2))
    n1, n2 = norm(v1), norm(v2)  # locate for null vector(s)

    if np.ndim(dot) == 0 and (dot >= 1 or n1 == 0 or n2 == 0):
        return 0

    if np.ndim(dot) > 0:
        # Remove invalid values and null vectors
        dot[(dot > 1) | (n1 == 0) | (n2 == 0)] = 1

    return np.degrees(np.arccos(dot))


def dist(v1, v2):
    """Distance between two vectors."""
    return np.sqrt(np.sum(np.power(np.subtract(v1, v2), 2), axis=-1))


def scalar_proj(v, n):
    r"""Scalar projection.

    .. code-block:: text

        s   `n`
        o---|---->
        \
        \ `v`
        x

            `v` · `n`
        s = ---------
              ||n||

    Parameters
    ----------
    v: list or numpy.ndarray
        Vector to project on the plane.
    n: list or numpy.ndarray
        Plane normal vector.

    Returns
    -------
    float or numpy.ndarray
        Scalar resolute of v in the direction of n.

    """
    return vdot(v, hat(n))


def scalar_rejection(v, n):
    r"""Scalar rejection.

    Orthogonal component u of the vector `v`
    in the plane of normal `n`.
    Also known as perpendicular dot product.

    .. code-block:: text

                `n`
            o-------->
            |\
        `u` | \ `v`
            v  x

                    `v` · `n`
        `u` = `v` - --------- `n`
                      ||n||


        p² = ||u||² = ||v||² - [(`v` · `n`) / ||n||]²

    Parameters
    ----------
    v: list or numpy.ndarray
        Vector to project on the plane.
    n: list or numpy.ndarray
        Plane normal vector.

    Returns
    -------
    float or numpy.ndarray
        Scalar resolute of v orthogonal to the direction of n.

    """
    return np.sqrt(norm(v) ** 2 - scalar_proj(v, n) ** 2)


def vector_rejection(v, n):
    r"""Vector rejection.

    Orthogonal vector `u` of the vector `v`
    in the plane of normal `n`.

    .. code-block:: text

                `n`
            o-------->
            |\
        `u` | \ `v`
            v  x

                    `v` · `n`
        `u` = `v` - --------- `n`
                      ||n||

    Parameters
    ----------
    v: list or numpy.ndarray
        Vector(s) to project on the plane.
    n: list or numpy.ndarray
        Plane normal vector.

    Returns
    -------
    float or numpy.ndarray
        Scalar resolute of v orthogonal to the direction of n.

    """
    proj = scalar_proj(v, n)

    if np.ndim(n) == 1:
        proj = np.transpose([proj])
    else:
        proj = np.broadcast_to(proj[..., None], np.shape(n))

    return np.subtract(v, proj * hat(n))


def ell_norm(xyz, radii):
    """Normal vector on a ellipsoid.

    Parameters
    ----------
    xyz: numpy.ndarray
        Cartesian coordinates input point.
    radii: [float, float, float]
        Ellipsoid (a, b, c) radii.

    Returns
    -------
    numpy.ndarray
        Normalized vector pointing away from the ellipsoid
        and normal to the ellipsoid at input point.

    """
    m = np.min(radii)

    if m <= 0:
        raise ValueError('Radii must be positives.')

    # Scaled inverted squared radii
    inv_abc_2 = np.power(np.divide(m, radii), 2)

    # Normal vector to the ellipsoid
    v = np.multiply(xyz, inv_abc_2)

    return hat(v)


def rot_axis(angle, axis):
    """Rotation matrix around an axis.

    Parameters
    ----------
    angle: float or list
        Angle(s) of the rotation (degrees).
    axis: tuple
        Axis of rotation.

    Returns
    -------
    numpy.ndarray
        Rotation matrix around the axis.

    """
    ux, uy, uz = hat(axis)
    c, s = cs(angle)
    _c = 1 - c

    m = np.array([
        [c + ux**2 * _c, ux * uy * _c - uz * s, ux * uz * _c + uy * s],
        [uy * ux * _c + uz * s, c + uy**2 * _c, uy * uz * _c - ux * s],
        [uz * ux * _c - uy * s, uz * uy * _c + ux * s, c + uz**2 * _c],
    ])

    return m if np.ndim(m) < NDIM_3D else np.moveaxis(m, -1, 0)


def boresight_rot_m(vec):
    """Rotation matrix to align the boresight to the z-axis."""
    x, y, z = hat(vec)

    if x == y == z == 0:
        raise ValueError('The boresight can not be a null vector')

    w = np.sqrt(1 - z**2)
    r = norm([x, y])
    c, s = (x / r, y / r) if r != 0 else (1, 0)

    return np.array([
        [c * z, s * z, -w],
        [-s, c, 0],
        [c * w, s * w, z],
    ])
