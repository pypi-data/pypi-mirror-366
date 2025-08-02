"""Auxiliary spherical formula."""

import numpy as np


def hav(theta):
    """Trigonometric half versine function.

    Parameters
    ----------
    theta: float or numpy.ndarray
        Angle in radians

    Returns
    -------
    float or numpy.ndarray
        Half versine value.

    """
    return 0.5 * (1 - np.cos(theta))


def hav_dist(lon_e_1, lat_1, lon_e_2, lat_2, r=1):
    """Calculate distance between 2 points on a sphere.

    Parameters
    ----------
    lon_e_1: float or numpy.ndarray
        Point 1 east longitude (°).
    lat_1: float or numpy.ndarray
        Point 1 north latitude (°).
    lon_e_2: float or numpy.ndarray
        Point 2 east longitude (°).
    lat_2: float or numpy.ndarray
        Point 2 north latitude (°).
    r: float, optional
        Planet radius.

    Returns
    -------
    float or numpy.ndarray
        Haversine distance between the 2 points.

    """
    lambda_1, phi_1 = np.radians([lon_e_1, lat_1])
    lambda_2, phi_2 = np.radians([lon_e_2, lat_2])
    return (
        2
        * r
        * np.arcsin(
            np.sqrt(
                hav(phi_2 - phi_1)
                + np.cos(phi_1) * np.cos(phi_2) * hav(lambda_2 - lambda_1)
            )
        )
    )


def sph_pixel_scale(e, ifov, d, r):
    """Compute pixel scale in spherical geometry.

    Project both sides of the pixel iFOV on the sphere
    and measure its extend on the surface.

    If the pixel extend above the limb, a ``NaN`` will be return.

    .. image:: https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/\
        uploads/3427e7f9b8950cb9b672053a0d42d11c/sph_pixel_scale.png
       :alt: Pixel scale spherical geometry calculation.

    Parameters
    ----------
    e: float, list or numpy.ndarray
        Local emission angle (in degrees).
    ifov: float
        Pixel instantaneous field of view (in radians).
    d: float, list or numpy.ndarray
        Distance from the observer to the target body center (in km).
    r: float
        Target body radius (in km).

    Returns
    -------
    float
        Pixel scale on the surface (in km) and ``NaN`` if the pixel
        extend above the limb.

    Raises
    ------
    ValueError
        If the observer distance is smaller than the target radius.

    """
    if np.any(np.less_equal(d, r)):
        raise ValueError('Observer distance must be larger than the target radius.')

    # Off-nadir angles
    alpha = np.arcsin(np.divide(r * np.sin(np.radians(e)), d))

    # Find all the valid pixels
    cond = alpha + ifov / 2 <= np.arcsin(np.divide(r, d))

    # iFOV off-nadir angles
    alpha_2 = np.add(alpha, ifov / 2, where=cond, out=np.full_like(alpha, np.nan))
    alpha_1 = alpha - ifov / 2

    # Emergence angles
    e_1 = np.arcsin(np.multiply(d, np.sin(alpha_1) / r))
    e_2 = np.arcsin(np.multiply(d, np.sin(alpha_2) / r))

    return r * (e_2 - e_1 - ifov)
