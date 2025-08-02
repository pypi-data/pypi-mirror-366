"""SPICE toolbox helper module."""

import numpy as np

import spiceypy as sp

from .references import SpiceBody, SpiceInstrument, SpiceObserver, SpiceRef
from .times import et
from ..math.sphere import sph_pixel_scale
from ..math.vectors import norm, xyz


TWO_ELEMENTS = 2
THREE_ELEMENTS = 3
SIX_ELEMENTS = 6


def is_iter(value):
    """Check if a value is iterable."""
    return isinstance(value, (list, tuple, np.ndarray))


def type_check(value, dtype, func=None):
    """Check input type.

    Parameters
    ----------
    value: any
        Input value.
    dtype: type
        Expected type.
    func: function, optional
        Conversion function. Use dtype if `None` provided (default).

    Returns
    -------
    dtype
        Valid value type.

    """
    return (
        value
        if isinstance(value, dtype)
        else dtype(value)
        if func is None
        else func(value)
    )


def deg(rad):
    """Convert radian angle in degrees."""
    return np.multiply(rad, sp.dpr())


def rlonlat(pt):
    """Convert point location in planetocentric coordinates.

    Parameters
    ----------
    pt: tuple
        Input XYZ cartesian coordinates.

    Returns
    -------
    float, float, float
        - Point radius (in km).
        - East planetocentric longitude (in degree).
        - North planetocentric latitude (in degree).

    Note
    ----
    - If the X and Y components of `pt` are both zero, the longitude is set to zero.
    - If `pt` is the zero vector, longitude and latitude are both set to zero.

    See Also
    --------
    spiceypy.spiceypy.reclat

    """
    big = np.max(np.abs(pt), axis=0)

    if np.ndim(pt) < TWO_ELEMENTS:
        if big == 0:
            return 0, 0, 0

        xyz = np.divide(pt, big)
    else:
        xyz = np.zeros_like(pt, dtype=float)
        np.divide(pt, big, where=big > 0, out=xyz, casting='unsafe')
        xyz[..., np.isnan(big)] = np.nan

    radius = big * np.sqrt(np.sum(np.power(xyz, 2), axis=0))
    lat_rad = np.arctan2(xyz[2], np.sqrt(np.sum(np.power(xyz[:2], 2), axis=0)))

    lon_e_rad = np.zeros_like(radius)
    np.arctan2(xyz[1], xyz[0], out=lon_e_rad)

    return radius, deg(lon_e_rad) % 360, deg(lat_rad)


def planetographic(body, xyz):
    """Convert point location in planetographic coordinates.

    Parameters
    ----------
    body: str or SpiceBody
        SPICE reference name or object.
    xyz: tuple
        Input XYZ cartesian coordinates, one or multiple point(s).

    Returns
    -------
    float, float, float
        - Point altitude (in km).
        - East or West planetographic longitude (in degree).
        - North planetographic latitude (in degree).

    Raises
    ------
    ValueError
        If the shape of the point(s) provided is not (3,) or (N, 3).

    Note
    ----
    - Planetographic longitude can be positive eastward or westward.
      For bodies having prograde (aka direct) rotation, the direction
      of increasing longitude is positive west: from the +X axis of
      the rectangular coordinate system toward the -Y axis.
      For bodies having retrograde rotation, the direction of increasing
      longitude is positive east: from the +X axis toward the +Y axis.
      The Earth, Moon, and Sun are exceptions: planetographic longitude
      is measured positive east for these bodies.

    - Planetographic latitude is defined for a point P on the reference spheroid,
      as the angle between the XY plane and the outward normal vector at P.
      For a point P not on the reference spheroid, the planetographic latitude
      is that of the closest point to P on the spheroid.

    - You may need a `tpc` kernel loaded in to the SPICE pool to perform
      this type of calculation.

    See NAIF documentation for more details.

    See Also
    --------
    spiceypy.spiceypy.recpgr

    """
    body = type_check(body, SpiceBody)

    single = np.ndim(xyz) == 1

    if np.shape(xyz)[-1] != THREE_ELEMENTS:
        raise ValueError(
            f'Input dimension must be `(3,)` or `(N, 3)` not `{np.shape(xyz)}`.'
        )

    lon_w_rad, lat_rad, alt_km = np.transpose([
        sp.recpgr(str(body), [x, y, z], body.re, body.f)
        for x, y, z in ([xyz] if single else xyz)
    ])

    if single:
        lon_w_rad, lat_rad, alt_km = lon_w_rad[0], lat_rad[0], alt_km[0]

    return alt_km, deg(lon_w_rad), deg(lat_rad)


def ocentric2ographic(body, lon_e, lat):
    """Convert planetocentric to planetographic coordinates.

    Parameters
    ----------
    body: str or SpiceBody
        SPICE reference name or object.
    lon_e: float
        East planetocentric longitude.
    lat: float
        North planetocentric latitude.

    Returns
    -------
    float, float
        Planetographic longitude and latitude (in degrees)

    Raises
    ------
    ValueError
        If the longitude and latitude inputs dimension are not the same.

    Note
    ----
    - You may need a `tpc` kernel loaded in to the SPICE pool to perform
      this type of calculation.

    - By default we use the body mean radius (harmonic mean on the ellipsoid).

    See Also
    --------
    SpiceBody.radius
    planetographic

    """
    if np.shape(lon_e) != np.shape(lat):
        raise ValueError(
            'East longitude and latitude inputs must have the same dimension: '
            f'{np.shape(lon_e)} vs. {np.shape(lat)}'
        )

    body = type_check(body, SpiceBody)

    return planetographic(body, xyz(lon_e, lat, r=body.radius))[1:]


def radec(vec):
    """Convert vector on the sky J2000 to RA/DEC coordinates.

    Parameters
    ----------
    vec: tuple
        Input XYZ cartesian vector coordinates in J200 frame.

    Returns
    -------
    float or numpy.ndarray, float or numpy.ndarray
        - Right-ascension (in degree).
        - Declination angle (in degree).

    See Also
    --------
    rlonlat

    """
    _, ra, dec = rlonlat(vec)
    return ra, dec


def azel(vec, az_spice=False, el_spice=True):
    """Convert vector in a reference frame into azimuth and elevation.

    Parameters
    ----------
    vec: tuple
        Input XYZ cartesian vector coordinates in the reference frame.
    az_spice: bool, optional
        Use SPICE azimuth convention (counted counterclockwise).
        Default: ``False`` (counted clockwise).
    el_spice: bool, optional
        Use SPICE elevation convention (counted positive above XY plane, toward +Z).
        Default: ``True``. Otherwise, counted positive below XY plane, toward -Z.

    Returns
    -------
    float, float, float
        - Azimuth angle from +X in XY plane (in degree).
        - Elevation angle above or below the XY plane (in degree).

    See Also
    --------
    rlonlat
    station_azel

    """
    _, az, el = rlonlat(vec)

    if not az_spice:
        az = (360 - az) % 360

    if not el_spice:
        el *= -1

    return az, el


def sub_obs_pt(time, observer, target, abcorr='NONE', method='NEAR POINT/ELLIPSOID'):
    """Sub-observer point calculation.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer location.
    observer: str
        Observer name.
    target: str or SpiceBody
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')
    method: str, optional
        Computation method to be used. Possible values:

        - 'NEAR POINT/ELLIPSOID' (default)
        - 'INTERCEPT/ELLIPSOID'
        - 'NADIR/DSK/UNPRIORITIZED[/SURFACES = <surface list>]'
        - 'INTERCEPT/DSK/UNPRIORITIZED[/SURFACES = <surface list>]'

        (See NAIF :func:`spiceypy.spiceypy.subpnt` for more details).

    Returns
    -------
    (float, float, float) or numpy.ndarray
        Sub-observer XYZ coordinates in the target body fixed frame
        (expressed in km).

        If a list of time were provided, the results will be stored
        in a (3, N) array.

    See Also
    --------
    spiceypy.spiceypy.subpnt

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)

    # SPICE parameters
    targ = str(target)
    frame = str(target.frame)
    obs = str(observer)

    if is_iter(time):
        return np.transpose([
            __sub_obs_pt(method, targ, t, frame, abcorr, obs) for t in time
        ])

    return __sub_obs_pt(method, targ, time, frame, abcorr, obs)


def __sub_obs_pt(method, target, time, frame, abcorr, observer):
    """SPICE sub-observer point."""
    xyz, *_ = sp.subpnt(method, target, time, frame, abcorr, observer)
    return xyz


def target_position(time, observer, target, *, abcorr='NONE'):
    """Sun position relative to the target.

    The vector starts from the observer to the target body:

    .. code-block:: text

        observer ------> target
                  (km)

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer's center location.
    observer: str or SpiceRef
        Observer body name.
    target: str or SpiceRef
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')

    Returns
    -------
    (float, float, float) or numpy.ndarray
        Target XYZ coordinates in the target body fixed frame
        (expressed in km).

        If a list of time were provided, the results will be stored
        in a (3, N) array.

    See Also
    --------
    spiceypy.spiceypy.spkpos
    sun_pos
    ang_size
    station_azel

    """
    time = type_check(time, float, et)
    observer = type_check(observer, SpiceRef)
    target = type_check(target, SpiceRef)

    # SPICE parameters
    obs = str(observer)
    frame = str(observer.frame)
    targ = str(target)

    if is_iter(time):
        return np.transpose([__pos(targ, t, frame, abcorr, obs) for t in time])

    return __pos(targ, time, frame, abcorr, obs)


def __pos(target, time, frame, abcorr, observer):
    """SPICE body position."""
    xyz, _ = sp.spkpos(target, time, frame, abcorr, observer)
    return xyz


def sun_pos(time, target, *, abcorr='NONE'):
    """Sun position relative to the target.

    The vector starts from the target body to the Sun:

    .. code-block:: text

        target ------> Sun
                (km)

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the **target's center location**.
    target: str
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')

    Returns
    -------
    (float, float, float) or numpy.ndarray
        Sun XYZ coordinates in the target body fixed frame
        (expressed in km).

        If a list of time were provided, the results will be stored
        in a (3, N) array.

    See Also
    --------
    target_position

    """
    return target_position(time, target, SpiceBody('SUN'), abcorr=abcorr)


def angular_size(time, observer, target, *, abcorr='NONE'):
    """Angular size of a target as seen from an observer.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer's center location.
    observer: str or SpiceBody
        Observer body name.
    target: str or SpiceBody
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')

    Returns
    -------
    float or numpy.ndarray
        Target angular size seen from the observer (in degree).

        If a list of time were provided, the results will be stored
        in an array.

    See Also
    --------
    target_position

    """
    target = type_check(target, SpiceBody)
    r_max = np.max(target.radii)

    xyz = target_position(time, observer, target, abcorr=abcorr)
    dist = norm(np.transpose(xyz))

    return 2 * np.degrees(np.arcsin(r_max / dist))


def station_azel(time, target, station, *, abcorr='CN+S', az_spice=False, el_spice=True):
    """Compute azimuth and elevation of target seen from a station on Earth.

    .. code-block:: text

        station ------> target

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time **at the station location**.
    target: str or SpiceBody
        Target body name.
    station: str
        Name of the tracking station.
    abcorr: str, optional
        Aberration correction (default: 'NONE')
    az_spice: bool, optional
        Use SPICE azimuth convention (counted counterclockwise).
        Default: ``False`` (counted clockwise).
    el_spice: bool, optional
        Use SPICE elevation convention (counted positive above XY plane, toward +Z).
        Default: ``True``. Otherwise, counted positive below XY plane, toward -Z.

    Returns
    -------
    float, float, float
        - Azimuth angle from +X in XY plane (in degree).
        - Elevation angle above or below the XY plane (in degree).

    See Also
    --------
    target_position
    azel

    """
    xyz = target_position(time, station, target, abcorr=abcorr)
    return azel(xyz, az_spice=az_spice, el_spice=el_spice)


def sc_state(time, spacecraft, target, abcorr='NONE'):
    """Spacecraft position and velocity relative to the target.

    The position vector starts from the target body to the spacecraft:

    .. code-block:: text

        target ------> spacecraft
                (km)

    The velocity vector correspond to the spacecraft motion (in km/s).

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the **spacecraft location**.
    spacecraft: str or SpiceSpacecraft
        Spacecraft name.
    target: str or SpiceBody
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')

    Returns
    -------
    (float, float, float, float, float, float) or numpy.ndarray
        Spacecraft XYZ position and velocity coordinates in
        the target body fixed frame (expressed in km and km/s).

        If a list of time were provided, the results will be stored
        in a (6, N) array.

    See Also
    --------
    spiceypy.spiceypy.spkezr

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)

    # SPICE parameters
    targ = str(target)
    frame = str(target.frame)
    obs = str(spacecraft)

    if is_iter(time):
        return np.transpose([__state(targ, t, frame, abcorr, obs) for t in time])

    return __state(targ, time, frame, abcorr, obs)


def __state(target, time, frame, abcorr, obs):
    """SPICE spacecraft state."""
    state, _ = sp.spkezr(target, time, frame, abcorr, obs)
    return np.negative(state)


def attitude(time, observer, ref='J2000'):
    """C-matrix attitude.

    Based on `SPICE documentation
    <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/ck.html>`_
    C-matrix (camera matrix) transforms the coordinates
    of a point in a reference frame (like J2000) into
    the instrument fixed coordinates:

    .. code-block:: text

        [ x_inst]     [          ] [ x_J2000 ]
        | y_inst|  =  | C-matrix | | y_J2000 |
        [ z_inst]     [          ] [ z_J2000 ]

    The transpose of a C-matrix rotates vectors from
    the instrument-fixed frame to the base frame:

    .. code-block:: text

        [ x_J2000]     [          ]T [ x_inst ]
        | y_J2000|  =  | C-matrix |  | y_inst |
        [ z_J2000]     [          ]  [ z_inst ]

    .. versionchanged:: 1.1.0

        Fix C-matrix definition. The previous version was incorrect
        and returned the transpose of the C-matrix and not the C-matrix.
        See `issue #73
        <https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/issues/73>`_
        for details.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer location.
    observer: str or SpiceSpacecraft or SpiceInstrument
        Spacecraft or instrument name.
    ref: str, optional
        Reference for the return pointing.

    Returns
    -------
    numpy.ndarray
        C-matrix relative to the reference frame.

        If a list of time were provided, the results will be stored
        in a (3, 3, N) array.

    Raises
    ------
    ValueError
        If the observer provided is not a Spacecraft or an instrument.

    See Also
    --------
    spiceypy.spiceypy.pxform

    """
    time = type_check(time, float, et)
    observer = type_check(observer, SpiceObserver)
    frame = str(observer.frame)

    if is_iter(time):
        return np.moveaxis([__attitude(ref, frame, t) for t in time], 0, -1)

    return __attitude(ref, frame, time)


def __attitude(ref, frame, time):
    """SPICE attitude matrix."""
    return sp.pxform(ref, frame, time)


def quaternions(attitude_matrix):
    """Compute the SPICE rotation quaternions.

    Parameters
    ----------
    attitude_matrix: numpy.ndarray
        Attitude rotation matrix

    Returns
    -------
    (float, float, float, float) or numpy.ndarray
        SPICE quaternions equivalent to the provided rotation
        matrix.

        If a list of attitude matrix was provided, the results will be stored
        in a (4, N) array.

    Raises
    ------
    ValueError
        If the attitude matrix shape is not (3, 3) or (3, 3, N).

    See Also
    --------
    attitude
    spiceypy.spiceypy.pxform

    """
    shape = np.shape(attitude_matrix)

    if len(shape) < TWO_ELEMENTS or len(shape) > THREE_ELEMENTS or shape[:2] != (3, 3):
        raise ValueError(f'Input matrix shape: (3, 3) or (3, 3, N). {shape} provided')

    if len(shape) == THREE_ELEMENTS:
        return np.transpose([
            __quaternions(m.tolist()) for m in np.moveaxis(attitude_matrix, -1, 0)
        ])

    return __quaternions(attitude_matrix)


def __quaternions(mat):
    """SPICE matrix to quaternion."""
    return sp.m2q(mat)


def intersect_pt(
    time,
    observer,
    target,
    frame,
    ray,
    limb=False,
    abcorr='NONE',
    corloc='TANGENT POINT',
    method='ELLIPSOID',
):
    """Intersection point on a target from a ray at the observer position.

    The intersection is primarily computed with the target surface.
    If no intersection was found and the :py:attr:`limb` flag is set to ``TRUE``,
    the intersection will be search on the target limb (defined as the impact parameter).
    When no value was find, a NaN array will be return.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer location.
    observer: str or SpiceSpacecraft or SpiceInstrument
        Spacecraft of instrument observer name.
    target: str or SpiceBody
        Target body name.
    frame: str
        Reference frame relative to which the ray's direction vector is expressed.
    ray: tuple or list of tuple
        Ray direction vector emanating from the observer.
        The intercept with the target body's surface of the ray defined by
        the observer and ray is sought.
    limb: bool, optional
        Compute the intersection on the limb impact parameter
        if no intersection with the surface was found.
    abcorr: str, optional
        Aberration correction (default: 'NONE').
    corloc: str, optional
        Aberration correction locus (default: 'TANGENT POINT').
        Used only if ``limb=True``.
    method: str, optional
        Computation method to be used.
        (See NAIF :func:`spiceypy.spiceypy.sincpt` for more details).

    Returns
    -------
    (float, float, float, float) or numpy.ndarray
        Surface/limb intersection XYZ position on the target body
        fixed frame (expressed in km), plus a surface intersection flag.

        If a list of time/ray were provided, the results will be stored
        in a (4, N) array.

    Warning
    -------
    Currently the limb intersection parameter is only available for
    ``abcorr='NONE'`` (an ``NotImplementedError`` will be raised).

    See Also
    --------
    spiceypy.spiceypy.sincpt
    spiceypy.spiceypy.tangpt

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)
    observer = type_check(observer, SpiceObserver)

    # SPICE parameters
    targ = str(target)
    targ_frame = str(target.frame)
    obs = str(observer)

    if is_iter(time) and np.ndim(ray) > 1:
        if len(time) != np.shape(ray)[0]:
            raise ValueError(
                'The ephemeris times and ray vectors must have the same size: '
                f'{len(time)} vs {len(ray)}'
            )

        return np.transpose([
            __intersect_pt(
                method, targ, t, targ_frame, abcorr, corloc, obs, frame, r, limb
            )
            for t, r in zip(time, ray, strict=False)
        ])

    if is_iter(time):
        return intersect_pt(
            time,
            observer,
            target,
            frame,
            [ray] * len(time),
            limb=limb,
            abcorr=abcorr,
            corloc=corloc,
            method=method,
        )

    if np.ndim(ray) > 1:
        return intersect_pt(
            [time] * np.shape(ray)[0],
            observer,
            target,
            frame,
            ray,
            limb=limb,
            abcorr=abcorr,
            corloc=corloc,
            method=method,
        )

    return __intersect_pt(
        method, targ, time, targ_frame, abcorr, corloc, obs, frame, ray, limb
    )


def __intersect_pt(
    method, target, time, targ_frame, abcorr, corloc, obs, ref_frame, ray, limb
):
    """SPICE intersection point.

    Use surface intersect point first and if no intersection and ``limb=True``,
    use tangent point method.

    Returns
    -------
    (float, float, float, float)
        Surface/limb intersection XYZ position on the target body
        fixed frame (expressed in km), plus a surface intersection flag.

    """
    try:
        xyz, *_ = sp.sincpt(method, target, time, targ_frame, abcorr, obs, ref_frame, ray)
        return *xyz, True

    except sp.stypes.NotFoundError:
        if limb:
            xyz, *_ = sp.tangpt(
                method, target, time, targ_frame, abcorr, corloc, obs, ref_frame, ray
            )
            return *xyz, False

    return np.array([np.nan, np.nan, np.nan, False])


def boresight_pt(
    time,
    observer,
    target,
    limb=False,
    abcorr='NONE',
    corloc='TANGENT POINT',
    method='ELLIPSOID',
):
    """Surface intersection on a target from an instrument/spacecraft boresight.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer location.
    observer: str or SpiceSpacecraft or SpiceInstrument
        Spacecraft or instrument name.
    target: str or SpiceBody
        Target body name.
    limb: bool, optional
        Compute the intersection on the limb impact parameter
        if no intersection with the surface was found.
    abcorr: str, optional
        Aberration correction (default: 'NONE')
    corloc: str, optional
        Aberration correction locus (default: 'TANGENT POINT').
        Used only if ``limb=True``.
    method: str, optional
        Computation method to be used.
        (See NAIF :func:`spiceypy.spiceypy.sincpt` for more details).

    Returns
    -------
    (float, float, float, float) or numpy.ndarray
        Boresight intersection XYZ position on the target surface body
        fixed frame (expressed in km), plus a surface intersection flag.

        If a list of time were provided, the results will be stored
        in a (4, N) array.

    See Also
    --------
    intersect_pt

    """
    observer = type_check(observer, SpiceObserver)

    return intersect_pt(
        time,
        observer.spacecraft,
        target,
        str(observer.frame),
        observer.boresight,
        limb=limb,
        abcorr=abcorr,
        corloc=corloc,
        method=method,
    )


def fov_pts(
    time,
    inst,
    target,
    limb=False,
    npt=24,
    abcorr='NONE',
    corloc='TANGENT POINT',
    method='ELLIPSOID',
):
    """Surface intersection on a target from an instrument FOV rays.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer location.
    inst: str or SpiceInstrument
        Instrument name.
    target: str or SpiceBody
        Target body name.
    limb: bool, optional
        Compute the intersection on the limb impact parameter
        if no intersection with the surface was found.
    npt: int or tuple, optional
        Number of points in the field of view contour (default: 24).
        Usually, this does not include the last point to close the polygon
        (to avoid to compute it twice).
        If the FOV has a ``RECTANGULAR`` and ``POLYGON`` shape,
        it is possible to provide a tuple that will correspond
        to the number of points per edges (excluding the corners).
        If the tuple size is smaller than the number of edges,
        its values will be cycled.
    abcorr: str, optional
        Aberration correction (default: 'NONE'),
    corloc: str, optional
        Aberration correction locus (default: 'TANGENT POINT').
        Used only if ``limb=True``.
    method: str, optional
        Computation method to be used.
        (See NAIF :func:`spiceypy.spiceypy.sincpt` for more details).

    Returns
    -------
    (float, float, float, float) or numpy.ndarray
        Field of View intersection XYZ positions on the target surface body
        fixed frame (expressed in km), plus a surface intersection flag.

        If a list of time were provided, the results will be stored
        in a (4, N, M) array. `M` being the number of bound in the FOV.

    See Also
    --------
    intersect_pt

    Note
    ----
    In the general case, the last point should be different from the 1st one.
    You need to add the 1st point to the end of the list if you want to close
    the polygon of the footprint.

    """
    inst = type_check(inst, SpiceInstrument)

    return np.moveaxis(
        [
            intersect_pt(
                time,
                inst.spacecraft,
                target,
                str(inst.frame),
                ray.copy(),
                limb=limb,
                abcorr=abcorr,
                corloc=corloc,
                method=method,
            )
            for ray in inst.rays(npt=npt)
        ],
        0,
        -1,
    )


def target_separation(
    time, observer, target_1, target_2, *, shape_1='POINT', shape_2='POINT', abcorr='NONE'
):
    """Angular target separation between two bodies seen from an observer.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the observer location.
    observer: str or SpiceSpacecraft or SpiceInstrument
        Spacecraft or instrument name.
    target_1: str or SpiceBody
        First target body name.
    target_2: str or SpiceBody
        Second target body name.
    shape_1: str, optional
        First target body shape model. Only ``'POINT'`` and ``'SPHERE'`` are accepted.
        If POINT selected (default) the target is considered to have no radius.
        If SPHERE selected the calculation will take into account the target radii
        (max value used).
    shape_2: str, optional
        Second target body shape model. See ``shape_1`` for details.
    target_2: str or SpiceBody
        Second target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE'),

    Returns
    -------
    float or numpy.ndarray
        Angular separation between the two targets (in degrees).

        If a list of :py:attr:`time` was provided, the results will
        be stored in an array.

    Note
    ----
    At the moment (N0067), DSK shape are not supported and
    ``frame_1`` and ``frame_2`` are always set to ``'NULL'``.

    See Also
    --------
    spiceypy.spiceypy.trgsep

    """
    time = type_check(time, float, et)
    observer = type_check(observer, SpiceObserver)
    target_1 = type_check(target_1, SpiceBody)
    target_2 = type_check(target_2, SpiceBody)

    # SPICE parameters
    obs = str(observer)
    targ_1 = str(target_1)
    targ_2 = str(target_2)

    if is_iter(time):
        return np.transpose([
            __target_separation(t, obs, targ_1, shape_1, targ_2, shape_2, abcorr)
            for t in time
        ])

    return __target_separation(time, obs, targ_1, shape_1, targ_2, shape_2, abcorr)


def __target_separation(time, obs, targ_1, shape_1, targ_2, shape_2, abcorr):
    """SPICE angular target separation in degrees."""
    rad = sp.trgsep(time, targ_1, shape_1, 'NULL', targ_2, shape_2, 'NULL', obs, abcorr)
    return np.degrees(rad)


def local_time(time, lon, target, lon_type='PLANETOCENTRIC'):
    """Local solar time.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the target surface point location.
    lon: float or list or tuple
        Longitude of surface point (degree).
    target: str
        Target body name.
    lon_type: str, optional
        Form of longitude supplied by the variable :py:attr:`lon`.
        Possible values:

        - `PLANETOCENTRIC` (default)
        - `PLANETOGRAPHIC`

        (See NAIF :func:`spiceypy.spiceypy.et2lst` for more details).

    Returns
    -------
    float or numpy.ndarray
        Local solar time (expressed in decimal hours).

        If a list of :py:attr:`time` or :py:attr:`lon`
        were provided, the results will be stored
        in an array.

    Raises
    ------
    ValueError
        If the :py:attr:`time` and :py:attr:`lon` are both
        arrays but their size don't match.

    See Also
    --------
    spiceypy.spiceypy.et2lst

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)

    # SPICE parameters
    targ_id = int(target)
    lon_rad = np.radians(lon)

    if is_iter(time) and is_iter(lon):
        if len(time) != len(lon):
            raise ValueError(
                'The ephemeris times and longitudes must have the same size: '
                f'{len(time)} vs {len(lon)}'
            )

        return np.transpose([
            __local_time(_time, targ_id, _lon_rad, lon_type)
            for _time, _lon_rad in zip(time, lon_rad, strict=False)
        ])

    if is_iter(time):
        return local_time(time, [lon] * len(time), target, lon_type)

    if is_iter(lon):
        return local_time([time] * len(lon), lon, target, lon_type)

    return __local_time(time, targ_id, lon_rad, lon_type)


def __local_time(time, targ_id, rad_lon, lon_type):
    """SPICE solar local time."""
    if np.isnan(rad_lon):
        return np.nan

    h, m, s, *_ = sp.et2lst(time, targ_id, rad_lon, lon_type)
    return h + m / 60 + s / 3600


def illum_angles(time, spacecraft, target, pt, abcorr='NONE', method='ELLIPSOID'):
    """Illumination angles.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the target surface point location.
    spacecraft: str
        Spacecraft name.
    target: str
        Target body name.
    pt: numpy.ndarray
        Surface point (XYZ coordinates).
    abcorr: str, optional
        Aberration correction (default: 'NONE')
    method: str, optional
        Form of longitude supplied by the variable :py:attr:`lon`.
        Possible values:

        - `ELLIPSOID` (default)
        - `DSK/UNPRIORITIZED[/SURFACES = <surface list>]`

        (See NAIF :func:`spiceypy.spiceypy.ilumin` for more details).

    Returns
    -------
    float or numpy.ndarray
        Solar incidence, emission and phase angles at the surface point (degrees).

        If a list of time were provided, the results will be stored in a (3, N) array.

    Raises
    ------
    ValueError
        If the :py:attr:`time` and :py:attr:`lon` are both
        arrays but their size don't match.

    See Also
    --------
    spiceypy.spiceypy.ilumin

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)

    # SPICE parameters
    targ = str(target)
    frame = str(target.frame)
    obs = str(spacecraft)

    if is_iter(time) and np.ndim(pt) > 1:
        if len(time) != np.shape(pt)[1]:
            raise ValueError(
                'The ephemeris times and surface point must have the same size: '
                f'{len(time)} vs {len(pt)}'
            )

        return np.transpose([
            __illum_angles(method, targ, t, frame, abcorr, obs, _pt)
            for t, _pt in zip(time, np.transpose(pt), strict=False)
        ])

    if is_iter(time):
        return illum_angles(
            time,
            spacecraft,
            target,
            np.transpose([pt] * len(time)),
            abcorr=abcorr,
            method=method,
        )

    if np.ndim(pt) > 1:
        return illum_angles(
            [time] * np.shape(pt)[1], spacecraft, target, pt, abcorr=abcorr, method=method
        )

    return __illum_angles(method, targ, time, frame, abcorr, obs, pt)


def __illum_angles(method, target, time, frame, abcorr, obs, pt):
    """SPICE illumination angles."""
    if np.isnan(np.max(pt)):
        return np.array([np.nan, np.nan, np.nan])

    *_, p, i, e = sp.ilumin(method, target, time, frame, abcorr, obs, pt)
    return np.degrees([i, e, p])


def solar_longitude(time, target, abcorr='NONE'):
    """Seasonal solar longitude (degrees).

    Compute the angle from the vernal equinox of the main parent
    body.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the target's center location.
    target: str
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')

    Returns
    -------
    float or numpy.ndarray
        Solar longitude angle(s) (degrees).

        If a list of :py:attr:`time` were provided,
        the results will be stored in an array.

    Note
    ----
    If the target parent is not the SUN the target will be change
    for its own parent.

    See Also
    --------
    spiceypy.spiceypy.lspcn

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)

    # SPICE parameters
    targ = str(target)

    if target.parent != 'SUN':
        solar_longitude(time, target.parent, abcorr=abcorr)

    if is_iter(time):
        return np.transpose([__ls(targ, t, abcorr) for t in time])

    return __ls(targ, time, abcorr)


def __ls(target, time, abcorr):
    """SPICE solar longitude."""
    return np.degrees(sp.lspcn(target, time, abcorr))


def true_anomaly(time, target, abcorr='NONE', frame='ECLIPJ2000'):
    """Target orbital true anomaly (degrees).

    The angular position of the target in its orbit
    compare to its periapsis.

    Parameters
    ----------
    time: float or list or tuple
        Ephemeris Time or UTC time input(s).
        It refers to time at the target's center location.
    target: str
        Target body name.
    abcorr: str, optional
        Aberration correction (default: 'NONE')
    frame: str, optional
        Inertial frame to compute the state vector
        (default: `ECLIPJ2000`).

    Returns
    -------
    float or numpy.ndarray
        True anomaly angle (degrees).

        If a list of :py:attr:`time` were provided,
        the results will be stored in an array.

    See Also
    --------
    spiceypy.spiceypy.spkezr
    spiceypy.spiceypy.oscltx

    """
    time = type_check(time, float, et)
    target = type_check(target, SpiceBody)

    # SPICE parameters
    parent = str(target.parent)
    targ = str(target)
    mu = target.parent.mu

    if is_iter(time):
        return np.transpose([
            __true_anomaly(parent, t, frame, abcorr, targ, mu) for t in time
        ])

    return __true_anomaly(parent, time, frame, abcorr, targ, mu)


def __true_anomaly(parent, time, frame, abcorr, target, mu):
    """SPICE true_anomaly."""
    state = __state(parent, time, frame, abcorr, target)
    nu = sp.oscltx(state, time, mu)[8]
    return np.degrees(nu)


def groundtrack_velocity(target, state):
    """Groundtrack velocity (km/s).

    Speed motion of the sub-observer point along the groundtrack.

    .. versionchanged:: 1.1.0

        Fix the formula. The previous one was incorrect.
        See `issue #35
        <https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/issues/35>`_
        for details.

    Caution
    -------
    This speed does not correspond to the norm of the rejection
    of the velocity vector of the observer in the target fixed frame.

    Warning
    -------
    This formula is only valid for a spheroid elongated along the
    axis of rotation (``c``). It is not correct for a generic ellipsoid.

    No aberration correction is applied.

    Parameters
    ----------
    target: str
        Target body name.
    state: str
        Target -> observer state position and velocity vectors.
        Computed at the observer time.

    Returns
    -------
    float or numpy.ndarray
        Ground track velocity (km/s).

        If a list of :py:attr:`state` is provided,
        the results will be stored in an array.

    Raises
    ------
    ValueError
        If the :py:attr:`state` arrays doesn't have the good shape.

    Note
    ----
    The tangential speed is obtained as product of the local radius of the
    observed body with the tangential angular speed:

    .. code-block:: text

        latitudinal
        component
            ^   x
            |  /
            | / <- tangential component
            |/
            o----> longitudinal component

                (the cos is to compensate the 'shrinking' of
                 longitude increasing the latitude)

    See Also
    --------
    spiceypy.spiceypy.recgeo
    spiceypy.spiceypy.dgeodr
    spiceypy.spiceypy.mxv

    """
    target = type_check(target, SpiceBody)

    # SPICE parameters
    re, _, rp = target.radii  # target equatorial and polar radii
    f = (re - rp) / re  # target flattening factor

    shape = np.shape(state)

    if len(shape) < 1 or len(shape) > TWO_ELEMENTS or shape[0] != SIX_ELEMENTS:
        raise ValueError(f'Input matrix shape: (6,) or (6, N). {shape} provided')

    if len(shape) == TWO_ELEMENTS:
        return np.transpose([__gt_speed(s, re, rp, f) for s in np.transpose(state)])

    return __gt_speed(state, re, rp, f)


def __gt_speed(state, re, rp, f):
    """SPICE groundtrack velocity."""
    xyz, v = state[:3], state[3:]

    # Local radius
    _, lat, _ = sp.recgeo(xyz, re, f)
    r = re * rp / (np.sqrt((re**2 * np.sin(lat) ** 2) + (rp**2 * np.cos(lat) ** 2)))

    # Geodetic speed
    jacobi = sp.dgeodr(*xyz, re, f)
    vlon, vlat, _ = sp.mxv(jacobi, v)  # Longitudinal, latitudinal and radial components

    # Groundtrack speed
    return np.sqrt(r**2 * ((vlon * np.cos(lat)) ** 2 + vlat**2))


def pixel_scale(inst, target, emi, dist):
    """Instrument pixel resolution (km/pixel).

    Only the cross-track iFOV is used and projected
    on the target body in spherical geometry (corrected
    from the local emission angle).

    Parameters
    ----------
    target: str or SpiceBody
        Target body name.
    inst: str or SpiceInstrument
        Instrument name.
    emi: float, list or numpy.ndarray
        Local emission angle (in degrees).
    dist: float, list or numpy.ndarray
        Distance from the observer to the target body center (in km).

    Returns
    -------
    float or numpy.ndarray
        Local instrument pixel resolution (km/pix).

    See Also
    --------
    planetary_coverage.math.sphere.sph_pixel_scale

    """
    target = type_check(target, SpiceBody)
    inst = type_check(inst, SpiceInstrument)

    return sph_pixel_scale(emi, inst.ifov_cross_track, dist, target.radius)
