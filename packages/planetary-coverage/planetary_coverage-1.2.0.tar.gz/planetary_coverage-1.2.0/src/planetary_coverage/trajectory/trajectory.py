"""Trajectory module."""

from pathlib import Path

import numpy as np

from .fovs import FovsCollection
from .mask_traj import MaskedInstrumentTrajectory, MaskedSpacecraftTrajectory
from ..events import EventsDict, EventsList, EventWindow
from ..math.vectors import angle, ell_norm, norm
from ..misc import cached_property, logger
from ..spice import (
    SpiceAbCorr,
    SpiceBody,
    SpiceInstrument,
    SpicePool,
    SpiceRef,
    SpiceSpacecraft,
    attitude,
    check_kernels,
    et,
    et_ca_range,
    quaternions,
    utc,
)
from ..spice.axes import AXES
from ..spice.toolbox import (
    angular_size,
    boresight_pt,
    groundtrack_velocity,
    illum_angles,
    local_time,
    pixel_scale,
    radec,
    rlonlat,
    sc_state,
    solar_longitude,
    station_azel,
    sub_obs_pt,
    sun_pos,
    target_position,
    target_separation,
    true_anomaly,
)


log_traj, debug_trajectory = logger('Trajectory')

TERMINATOR_INC = 90  # Terminator incidence angle (degrees)


class Trajectory:  # noqa: PLR0904 (too-many-public-methods)
    """Spacecraft trajectory object.

    Parameters
    ----------
    kernels: str or tuple
        List of kernels to be loaded in the SPICE pool.

    observer: str or SpiceSpacecraft or SpiceInstrument
        Observer (spacecraft or instrument) SPICE reference.

    target: str or SpiceBody
        Target SPICE reference.

    ets: float or str or list
        Ephemeris time(s).

    abcorr: str, optional
        Aberration corrections to be applied when computing
        the target's position and orientation.
        Only the SPICE keys are accepted.

    exclude: EventWindow, EventsDict or EventsList
        Event window, list or dict of events to exclude from the analysis.

    Raises
    ------
    ValueError
        If the provided observer is not a valid spacecraft or instrument.

    """

    TOO_MANY_POINTS_WARNING = 1_000_000

    def __init__(self, kernels, observer, target, ets, abcorr='NONE', exclude=None):
        self.kernels = (
            (str(kernels),) if isinstance(kernels, (str, Path)) else tuple(kernels)
        )

        # Init SPICE references and times
        self.target = target
        self.observer = observer
        self.exclude = exclude
        self.ets = ets

        # Optional parameters
        self.abcorr = SpiceAbCorr(abcorr)

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}> '
            f'Observer: {self.observer} | '
            f'Target: {self.target}'
            f'\n - UTC start time: {self.start}'
            f'\n - UTC stop time: {self.stop}'
            f'\n - Nb of pts: {len(self):,d}'
        )

    def __len__(self):
        return len(self.ets)

    def __and__(self, other):
        """And ``&`` operator."""
        return self.mask(self.intersect(other))

    def __xor__(self, other):
        """Hat ``^`` operator."""
        return self.mask(self.intersect(other, outside=True))

    def __getitem__(self, item):
        if item.upper() in {'SUN', 'SS'}:
            log_traj.warning(
                'Querying `SUN` or `SS` from a Trajectory is depreciated. '
                'We recommend to use `.ss` or `.sun_lonlat` properties instead.'
            )
            return self.ss

        try:
            observer = (
                self.observer.instr(item)
                if isinstance(self, SpacecraftTrajectory)
                else SpiceRef(item)
            )

            log_traj.warning(
                'Observer name change should be performed with '
                '`.new_traj(spacecraft=..., instrument=...)` method.'
            )

            return Trajectory(
                self.kernels,
                observer,
                self.target,
                self.ets,
                abcorr=self.abcorr,
                exclude=self.exclude,
            )

        except (ValueError, KeyError):
            pass

        try:
            log_traj.warning(
                'Target name change should be performed with '
                '`.new_traj(target=...)` method.'
            )

            return Trajectory(
                self.kernels,
                self.observer,
                SpiceBody(item),
                self.ets,
                abcorr=self.abcorr,
                exclude=self.exclude,
            )
        except KeyError:
            pass

        raise KeyError(
            'The item must be a spacecraft, an instrument, a target body or the SUN.'
        )

    def __iter__(self):
        yield self

    def __hash__(self):
        """Kernels hash."""
        return self._kernels_hash

    @cached_property
    def _kernels_hash(self):
        """Expected Spice Pool kernels hash."""
        return SpicePool.hash(self.kernels)

    @check_kernels
    def load_kernels(self):
        """Load the required kernels into the SPICE pool.

        Note
        ----
        If the SPICE pool already contains the required kernels, nothing
        will append. If not, the pool is flushed and only the required kernels
        are loaded.

        """

    def add_kernel(self, *kernels):
        """Create a new trajectory with additional kernels.

        Parameters
        ----------
        *kernels: str or pathlib.Path
            Kernel(s) to append.

        Returns
        -------
        TourConfig
            New trajectory with a new set of kernels.

        """
        return self.__class__(
            self.kernels + tuple(str(kernel) for kernel in kernels),
            self.observer,
            self.target,
            self.ets,
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

    def new_traj(self, *, spacecraft=None, instrument=None, target=None):
        """Create a new trajectory for a different set of target/observer.

        You can provide either one or multiple parameters as once.

        Parameters
        ----------
        spacecraft: str or SpiceSpacecraft, optional
            New spacecraft name.
        instrument: str or SpiceInstrument, optional
            New instrument name (see note below).
        target: str or SpiceBody, optional
            New target name.

        Returns
        -------
        Trajectory
            New trajectory object with new parameters.

        Raises
        ------
        ValueError
            If no new parameter is provided.

        Note
        ----
        - The instrument name, can be either the instrument full name
          or just a suffix (ie. ``<SPACECRAFT>_<INSTRUMENT>``).

        - If the original trajectory has a instrument selected , you can
          discard it selected either by providing the ``spacecraft`` parameter
          alone or with ``instrument='none'`` syntax.

        """
        if not spacecraft and not instrument and not target:
            raise ValueError(
                'You need to provide at least a `spacecraft`, '
                'an `instrument` or a `target` parameter.'
            )

        # Select the correct observer based on spacecraft and instrument
        if spacecraft or instrument:
            observer = SpiceSpacecraft(spacecraft) if spacecraft else self.spacecraft

            if str(instrument).upper() != 'NONE':
                observer = observer.instr(instrument)
        else:
            observer = self.observer

        return self.__class__(
            self.kernels,
            observer,
            SpiceBody(target) if target else self.target,
            self.ets,
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

    @property
    def target(self):
        """Trajectory target."""
        return self.__target

    @target.setter
    @check_kernels
    def target(self, target):
        """Set target as a SpiceBody."""
        log_traj.debug('Set Spice Target.')
        self.__target = SpiceBody(target)

        # Clear all cached properties (added by `@cached_property` decorators)
        self.clear_cache()

    @property
    def observer(self):
        """Trajectory observer."""
        return self.__observer

    @observer.setter
    @check_kernels
    def observer(self, observer):
        """Set observer as a SpiceSpace or SpiceInstrument."""
        log_traj.debug('Set Spice Observer.')
        self.__observer = SpiceRef(observer)

        if isinstance(self.observer, SpiceSpacecraft):
            self.__class__ = SpacecraftTrajectory

        elif isinstance(self.observer, SpiceInstrument):
            self.__class__ = InstrumentTrajectory

        else:
            raise ValueError(
                f'The observer `{self.observer}` must be a'
                '`spacecraft` or an `instrument` reference.'
            )

        # Clear all cached properties (added by `@cached_property` decorators)
        self.clear_cache()

    @property
    def spacecraft(self):
        """Observer spacecraft SPICE reference."""
        return self.observer.spacecraft

    @property
    def ets(self):
        """Ephemeris Times (ET)."""
        return self.__ets

    @ets.setter
    @check_kernels
    def ets(self, ets):
        """Set Ephemeris Times (ET) array.

        See Also
        --------
        TourConfig._parse for details.

        """
        log_traj.debug('Set ephemeris times array.')

        if isinstance(ets, (str, int, float, np.datetime64)):
            self.__ets = np.array([et(ets)])

        elif isinstance(ets, (tuple, list, slice, np.ndarray)):
            self.__ets = np.sort(et(ets))

        else:
            raise ValueError('Invalid input Ephemeris Time(s).')

        if isinstance(self.exclude, (EventWindow, EventsDict, EventsList)):
            cond = self.exclude.contains(self.utc)
            self.__ets = self.__ets[~cond]
            del self.utc

        if len(self.ets) > self.TOO_MANY_POINTS_WARNING:
            log_traj.warning(
                'You have selected more than %s points. '
                'SPICE computation can take a while. '
                'It may be relevant to reduce the temporal '
                'resolution or the time range.',
                f'{self.TOO_MANY_POINTS_WARNING:,d}',
            )

        # Clear all cached properties (added by `@cached_property` decorators)
        self.clear_cache()

    @cached_property
    @check_kernels
    def utc(self):
        """UTC times."""
        log_traj.info('Compute UTC times.')
        return utc(self.ets)

    @cached_property
    @check_kernels
    def start(self):
        """UTC start time."""
        return utc(self.ets[0])

    @cached_property
    @check_kernels
    def stop(self):
        """UTC stop time."""
        return utc(self.ets[-1])

    @property
    def boresight(self):
        """Observer boresight pointing vector."""
        return self.observer.boresight

    @boresight.setter
    def boresight(self, boresight):
        """Observer boresight setter."""
        if isinstance(self.observer, SpiceInstrument):
            raise AttributeError('SpiceInstrument boresight can not be changed')

        log_traj.info('Change boresight from %r to %r.', self.boresight, boresight)

        # Invalided cached values that require the previous boresight
        del self.boresight_pts
        del self.radec

        # Change observer boresight
        self.observer.BORESIGHT = boresight

    @property
    def inertial_frame(self):
        """Target parent inertial frame."""
        return (
            'JUICE_JUPITER_IF_J2000'
            if self.spacecraft == 'JUICE'
            and (self.target == 'JUPITER' or self.target.parent == 'JUPITER')
            else 'ECLIPJ2000'
        )

    @cached_property
    @check_kernels
    def sc_pts(self):
        """Sub-spacecraft surface intersection vector.

        Returns
        -------
        numpy.ndarray
            Spacecraft XYZ intersection on the target body fixed frame
            (expressed in km).

        Note
        ----
        Currently the intersection method is fixed internally
        as ``method='NEAR POINT/ELLIPSOID'``.

        """
        log_traj.info('Compute sub-spacecraft points.')
        res = sub_obs_pt(
            self.ets,
            self.spacecraft,
            self.target,
            abcorr=self.abcorr,
            method='NEAR POINT/ELLIPSOID',
        )

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent='sc_pts')
    def sc_rlonlat(self):
        """Sub-spacecraft coordinates.

        Returns
        -------
        numpy.ndarray
            Sub-spacecraft planetocentric coordinates:
            radii, east longitudes and latitudes.

        Note
        ----
        Currently the intersection method is fixed internally
        as ``method='NEAR POINT/ELLIPSOID'``.

        See Also
        --------
        .sc_pts

        """
        log_traj.debug('Compute sub-observer point in planetocentric coordinates.')
        return rlonlat(self.sc_pts)

    @property
    def lonlat(self):
        """Groundtrack or surface intersect (not implemented here)."""

    @cached_property
    @check_kernels
    def boresight_pts(self):
        """Boresight surface intersection vector.

        Returns
        -------
        numpy.ndarray
            Boresight XYZ intersection on the target body fixed frame
            (expressed in km).

        Note
        ----
        Currently the intersection method is fixed internally
        as ``method='ELLIPSOID'``.

        """
        log_traj.info('Compute boresight intersection points.')
        res = boresight_pt(
            self.ets,
            self.observer,
            self.target,
            limb=False,
            abcorr=self.abcorr,
            method='ELLIPSOID',
        )[:-1]  # since limb is always False

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent='boresight_pts')
    def boresight_rlonlat(self):
        """Boresight surface intersect coordinates.

        Returns
        -------
        numpy.ndarray
            Boresight surface intersect planetocentric coordinates:
            radii, east longitudes and latitudes.

        See Also
        --------
        .boresight_pts

        """
        log_traj.debug('Compute boresight intersect in planetocentric coordinates.')
        return rlonlat(self.boresight_pts)

    @property
    def surface(self):
        """Boolean array when the boresight intersect the target surface."""
        return ~np.isnan(self.boresight_pts[0])

    @property
    def limb(self):
        """Boolean array when the boresight is above the limb."""
        return ~self.surface

    @cached_property
    @check_kernels
    def sc_state(self):
        """Spacecraft position and velocity.

        In the target body fixed frame (km and km/s).

        """
        log_traj.info('Compute spacecraft position and velocity in the target frame.')
        res = sc_state(self.ets, self.spacecraft, self.target, abcorr=self.abcorr)

        log_traj.debug('Result: %r', res)
        return res

    @property
    def sc_pos(self):
        """Spacecraft position in the target body fixed frame (km).

        See Also
        --------
        .sc_state

        """
        return self.sc_state[:3]

    @property
    def sc_velocity(self):
        """Spacecraft velocity vector in the target body fixed frame (km/s).

        See Also
        --------
        .sc_speed

        """
        return self.sc_state[3:]

    @cached_property(parent='sc_state')
    def sc_speed(self):
        """Observer speed in the target body fixed frame (km/s).

        See Also
        --------
        .sc_velocity

        """
        return norm(self.sc_velocity.T)

    @cached_property(parent='sc_state')
    def dist(self):
        """Spacecraft distance to the body target center (km).

        This distance is computed to the center of the targeted body.

        See Also
        --------
        .sc_state

        """
        log_traj.debug('Compute spacecraft distance in the target frame.')
        return norm(self.sc_pos.T)

    @cached_property(parent=('sc_pts', 'sc_state'))
    def alt(self):
        """Spacecraft altitude to the sub-spacecraft point (km).

        The intersect on the surface is computed on the reference
        ellipsoid.

        See Also
        --------
        .sc_pts
        .sc_state

        """
        log_traj.debug('Compute spacecraft distance in the target frame.')
        return norm(self.sc_pos.T - self.sc_pts.T)

    @cached_property(parent='dist')
    def target_size(self):
        """Target angular size (degrees).

        See Also
        --------
        .angular_size

        """
        log_traj.debug('Compute target angular size.')
        return self.angular_size(self.target)

    @cached_property(parent='dist')
    def ets_target_center(self):
        """Ephemeris Time (ET) at the target center.

        The light time correction is only apply if :attr:`abcorr` in not ``NONE``.

        See Also
        --------
        Trajectory.dist
        .SpiceAbCorr.dist_corr

        """
        return self.abcorr.dist_corr(self.ets, self.dist)

    @cached_property(parent='sc_state')
    @check_kernels
    def groundtrack_velocity(self):
        """Spacecraft groundtrack velocity (km/s).

        It correspond to the motion speed of the sub-spacecraft point
        on the surface.

        See Also
        --------
        .sc_state

        """
        log_traj.info('Compute groundtrack velocity.')
        res = groundtrack_velocity(self.target, self.sc_state)

        log_traj.debug('Result: %r', res)
        return res

    @cached_property
    @check_kernels
    def sc_attitude(self):
        """[Depreciated] Spacecraft attitude c-matrix in J2000 frame.

        .. versionchanged:: 1.1.0

            Fix C-matrix definition. The previous version was incorrect
            and returned the transpose of the C-matrix and not the C-matrix.
            See `issue #73
            <https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/issues/73>`_
            for details.

        .. deprecated:: 1.1.0

            ``.sc_attitude`` is depreciated in favor of ``.attitude``.

        """
        log_traj.info('Compute spacecraft attitude.')
        log_traj.warning('`.sc_attitude` has been replaced by `.attitude`.')
        log_traj.warning(
            '`.sc_attitude` previously returned the transpose of the C-matrix '
            'and not the C-matrix. If you use this property, '
            'please, update your code accordingly.'
        )
        return attitude(self.ets, self.observer)

    @cached_property
    @check_kernels
    def attitude(self):
        """Observer attitude c-matrix in J2000 frame."""
        log_traj.info('Compute observer attitude.')
        return attitude(self.ets, self.observer)

    @cached_property(parent='attitude')
    def quaternions(self):
        """Observer quaternions in J2000 frame."""
        log_traj.info('Compute observer quaternions.')
        return quaternions(self.attitude)

    @cached_property(parent='attitude')
    def radec(self):
        """Observer boresight RA/DEC pointing in J2000 frame."""
        log_traj.info('Compute spacecraft pointing (RA/DEC).')
        return radec(np.einsum('ijk,i->jk', self.attitude, self.boresight, optimize=True))

    @property
    def ra(self):
        """Boresight pointing right ascension angle (degree)."""
        return self.radec[0]

    @property
    def dec(self):
        """Boresight pointing declination angle (degree)."""
        return self.radec[1]

    @cached_property(parent='ets_target_center')
    @check_kernels
    def sun_pos(self):
        """Sun position in the target body fixed frame (km).

        Note
        ----
        Currently the intersection method is fixed on a sphere.

        See Also
        --------
        .ets_target_center

        """
        log_traj.info('Compute Sun coordinates in the target frame.')
        res = sun_pos(self.ets_target_center, self.target, abcorr=self.abcorr)

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent='sun_pos')
    def sun_rlonlat(self):
        """Sub-solar coordinates.

        Returns
        -------
        numpy.ndarray
            Sub-solar planetocentric coordinates:
            radii, east longitudes and longitudes.

        See Also
        --------
        .sun_pos

        """
        log_traj.debug('Compute sub-solar point in planetocentric coordinates.')
        return rlonlat(self.sun_pos)

    @property
    def sun_lon_e(self):
        """Sub-solar point east longitude (degree)."""
        return self.sun_rlonlat[1]

    @property
    def sun_lat(self):
        """Sub-solar point latitude (degree)."""
        return self.sun_rlonlat[2]

    @property
    def sun_lonlat(self):
        """Sub-solar point groundtrack (degree)."""
        return self.sun_rlonlat[1:]

    @property
    def ss(self):
        """Alias on the sub-solar point groundtrack (degree)."""
        return self.sun_lonlat

    @cached_property(parent='ets_target_center')
    @check_kernels
    def solar_longitude(self):
        """Target seasonal solar longitude (degrees).

        Warning
        -------
        The seasonal solar longitude is computed on the main parent body
        for the moons (`spiceypy.lspcn` on the moon will not return
        the correct expected value).

        """
        log_traj.info('Compute the target seasonal solar longitude.')
        res = solar_longitude(self.ets_target_center, self.target, abcorr=self.abcorr)

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent='ets_target_center')
    @check_kernels
    def true_anomaly(self):
        """Target orbital true anomaly (degree)."""
        log_traj.debug('Compute true anomaly angle.')

        res = true_anomaly(
            self.ets_target_center,
            self.target,
            abcorr=self.abcorr,
            frame=self.inertial_frame,
        )

        log_traj.debug('Result: %r', res)
        return res

    @check_kernels
    def position_of(self, target):
        """Position vector of target body in spacecraft frame (km).

        Parameters
        ----------
        target: str or SpiceRef
            Target body name.

        Returns
        -------
        numpy.ndarray
            Target position in spacecraft frame in km.

        """
        log_traj.info('Compute position to %s in %s frame.', target, self.spacecraft)
        res = target_position(
            self.ets,
            self.spacecraft,
            target,
            abcorr=self.abcorr,
        )

        log_traj.debug('Result: %r', res)
        return res

    def distance_to(self, target):
        """Distance to a target body (km).

        Parameters
        ----------
        target: str or SpiceRef
            Target body name.

        Returns
        -------
        numpy.ndarray
            Distance between the spacecraft and the provided target in km.

        """
        return norm(self.position_of(target).T)

    def ets_at(self, target):
        """Ephemeris time at target location with light-time corrections.

        Parameters
        ----------
        target: str or SpiceBody
            Target body name.

        Returns
        -------
        numpy.ndarray
            Light-time correction ephemeris time at the target location.

        """
        log_traj.info('Compute ETs at %s.', target)
        res = self.abcorr.dist_corr(self.ets, self.distance_to(target))

        log_traj.debug('Result: %r', res)
        return res

    @check_kernels
    def utc_at(self, target):
        """UTC time at target location with light-time corrections.

        Parameters
        ----------
        target: str or SpiceBody
            Target body name.

        Returns
        -------
        numpy.ndarray
            Light-time correction UTC time at the target location.

        """
        log_traj.info('Compute UTC at %s.', target)
        res = utc(self.ets_at(target))

        log_traj.debug('Result: %r', res)
        return res

    def angular_size(self, target):
        """Angle size of a given target (in degrees) seen from the spacecraft.

        Parameters
        ----------
        target: str or SpiceBody
            Second ray (see above).

        Returns
        -------
        numpy.ndarray
            Angular separation between the targets in degrees.

        See Also
        --------
        target_separation

        """
        log_traj.info('Compute %s angular size.', target)
        res = angular_size(
            self.ets,
            self.spacecraft,
            target,
            abcorr=self.abcorr,
        )

        log_traj.debug('Result: %r', res)
        return res

    def _vec(self, ray):
        """Get vector direction in target frame from ray.

        Parameters
        ----------
        ray: str or list or tuple
            Ray name (``'+Z'``), ray vector (``(0, 0, 1)``) or
            target name (``'JUPITER'``). You can also use ``'boresight'
            to use the instrument boresight (if defined).

        """
        if not isinstance(ray, str):
            if np.shape(ray) == (3,):
                return np.full((len(self), 3), ray)

            raise ValueError(f'Ray should be a 3D vector not `{np.shape(ray)}`')

        if axis := AXES.get(ray):
            return self._vec(axis)

        if ray.lower() == 'boresight':
            return self._vec(self.boresight)

        return self.position_of(ray).T

    def angle_between(self, ray_1, ray_2):
        """Angle between 2 rays in spacecraft frame (degrees).

        Parameters
        ----------
        ray_1: str or list or tuple
            First ray name (``'+Z'``), ray vector (``(0, 0, 1)``) or
            target name (``'JUPITER'``).
        ray_2: str or list or tuple
            Second ray (see above).

        Returns
        -------
        numpy.ndarray
            Angular separation between the targets in degrees.

        See Also
        --------
        .target_separation (for 2 target bodies with known radii).

        """
        log_traj.info('Compute angle between %r and %r.', ray_1, ray_2)

        res = angle(self._vec(ray_1), self._vec(ray_2))

        log_traj.debug('Result: %r', res)
        return res

    @check_kernels
    def target_separation(
        self, target_1, target_2=None, *, shape_1='POINT', shape_2='POINT'
    ):
        """Angular separation between two target bodies (degrees).

        Parameters
        ----------
        target_1: str or SpiceBody
            First target body name.
        target_2: str or SpiceBody
            Second target body name. If none provided (default), the trajectory main
            target will be used as the first target and the target provided as
            the secondary target.
        shape_1: str, optional
            First target body shape model. Only ``'POINT'`` and ``'SPHERE'`` are accepted.
            If POINT selected (default) the target is considered to have no radius.
            If SPHERE selected the calculation will take into account the target radii
            (max value used).
        shape_2: str, optional
            Second target body shape model. See ``shape_1`` for details.

        Returns
        -------
        numpy.ndarray
            Angular separation between the targets in degrees.

        See Also
        --------
        .angle_between

        """
        log_traj.info('Compute angular separation between %s and %s.', target_1, target_2)

        res = target_separation(
            self.ets,
            self.spacecraft,
            target_1 if target_2 is not None else self.target,
            target_2 if target_2 is not None else target_1,
            shape_1=shape_1,
            shape_2=shape_2,
            abcorr=self.abcorr,
        )

        log_traj.debug('Result: %r', res)
        return res

    @check_kernels
    def station_azel(self, station, *, az_spice=False, el_spice=True):
        """Spacecraft azimuth and elevation seen from an earth-based tracking station.

        Warning
        -------
        It is highly recommended to use ``abcorr='CN+S'`` to perform this calculation.

        Danger
        ------
        If you apply light-time corrections (``abcorr``), you need to represent
        the result in the correct time reference. Here you should use
        ``Trajectory.utc_at('EARTH')`` instead of `Trajectory.utc``.

        Parameters
        ----------
        station: str
            Name of the tracking station.
        az_spice: bool, optional
            Use SPICE azimuth convention (counted counterclockwise).
            Default: ``False`` (counted clockwise).
        el_spice: bool, optional
            Use SPICE elevation convention (counted positive above XY plane, toward +Z).
            Default: ``True``. Otherwise, counted positive below XY plane, toward -Z.

        Returns
        -------
        numpy.ndarray, numpy.ndarray
            Azimuth and elevation angles of the spacecraft seen from
            the tracking station in degrees.

        """
        log_traj.info(
            'Compute %s azimuth and elevation at %s station.', self.spacecraft, station
        )

        if self.abcorr == 'NONE':
            log_traj.warning(
                'You are computing station azimuth/elevation without light-time '
                "correction (`abcorr='NONE'`). "
                "We recommend to use `abcorr='CN+S'` instead."
            )

        res = station_azel(
            self.ets_at(station),
            station,
            self.spacecraft,
            abcorr=self.abcorr,
            az_spice=az_spice,
            el_spice=el_spice,
        )

        log_traj.debug('Result: %r', res)
        return res

    def mask(self, cond):
        """Create a masked trajectory only where the condition invalid."""
        if isinstance(self, InstrumentTrajectory):
            return MaskedInstrumentTrajectory(self, cond)

        return MaskedSpacecraftTrajectory(self, cond)

    def where(self, cond):
        """Create a masked trajectory only where the condition is valid."""
        return self.mask(~cond)

    def intersect(self, obj, outside=False):
        """Intersection mask between the trajectory and an object.

        Parameters
        ----------
        obj: any
            ROI-like object to intersect the trajectory.
        outside: bool, optional
            Return the invert of the intersection (default: `False`).

        Returns
        -------
        numpy.ndarray
            Mask to apply on the trajectory.

        Raises
        ------
        AttributeError
            If the comparison object doest have a :func:`contains` test function.

        """
        if not hasattr(obj, 'contains'):
            raise AttributeError(f'Undefined `contains` intersection in {obj}.')

        cond = obj.contains(self)
        return cond if outside else ~cond

    def approx_ca_utc(self, alt_min):
        """List of approximate closest approach UTC times to the target.

        Parameters
        ----------
        alt_min: float
            Minimal altitude at closest approach [km].

        Danger
        ------
        These values may not be accurate depending on the
        :class:`Trajectory` temporal resolution.

        """
        dist_min = self.target.radius + alt_min
        return [
            self.utc[seg][np.argmin(self.dist[seg])]
            for seg in self.where(self.dist <= dist_min).seg
        ]

    def get_flybys(self, alt_min=150_000):
        """List of all the flybys on the target below a given altitude.

        Parameters
        ----------
        alt_min: float, optional
            Minimal altitude at closest approach (default: 150,000 km).

        Returns
        -------
        [Flyby, …]
            List of flybys below the required altitude.

        """
        return [
            Flyby(
                self.kernels,
                self.observer,
                self.target,
                ca_utc,
                abcorr=self.abcorr,
                exclude=self.exclude,
                alt_min=alt_min,
            )
            for ca_utc in self.approx_ca_utc(alt_min)
        ]

    @property
    def flybys(self):
        """Get all the flybys for this trajectory below 150,000 km.

        See Also
        --------
        :func:`get_flybys` if you need a different minimal altitude.

        """
        return self.get_flybys()


class SpacecraftTrajectory(Trajectory):
    """Spacecraft trajectory object."""

    @property
    def lon_e(self):
        """Sub-spacecraft east longitude (degree)."""
        return self.sc_rlonlat[1]

    @property
    def lat(self):
        """Sub-spacecraft latitude (degree)."""
        return self.sc_rlonlat[2]

    @property
    def lonlat(self):
        """Sub-spacecraft groundtrack east longitudes and latitudes (degree)."""
        return self.sc_rlonlat[1:]

    @property
    def slant(self):
        """Spacecraft line-of-sight distance to the sub-spacecraft point (km).

        This is not the distance the distance to the target body center,
        but an alias of the altitude of the spacecraft.

        See Also
        --------
        Trajectory.dist
        Trajectory.alt

        """
        return self.alt

    @cached_property(parent='alt')
    def ets_surface_intersect(self):
        """Ephemeris Time (ET) at the surface intersect point.

        The light time correction is only apply if :attr:`abcorr` in not ``NONE``.

        See Also
        --------
        Trajectory.alt
        .SpiceAbCorr.dist_corr

        """
        return self.abcorr.dist_corr(self.ets, self.alt)

    @cached_property(parent=('sc_rlonlat', 'ets_surface_intersect'))
    @check_kernels
    def local_time(self):
        """Sub-spacecraft local time (decimal hours).

        See Also
        --------
        .sc_rlonlat
        .ets_surface_intersect

        """
        log_traj.info('Compute sub-spacecraft local time.')
        return local_time(self.ets_surface_intersect, self.lon_e, self.target)

    @cached_property(parent=('sc_pts', 'ets_surface_intersect'))
    @check_kernels
    def illum_angles(self):
        """Sub-spacecraft illumination angles (degree).

        Incidence, emission and phase angles.

        See Also
        --------
        .sc_pts
        .ets_surface_intersect

        """
        log_traj.info('Compute sub-spacecraft illumination geometry.')
        return illum_angles(
            self.ets_surface_intersect,
            self.spacecraft,
            self.target,
            self.sc_pts,
            abcorr=self.abcorr,
            method='ELLIPSOID',
        )

    @property
    def inc(self):
        """Sub-spacecraft incidence angle (degree)."""
        return self.illum_angles[0]

    @property
    def emi(self):
        """Sub-spacecraft emission angle (degree)."""
        return self.illum_angles[1]

    @property
    def phase(self):
        """Sub-spacecraft phase angle (degree)."""
        return self.illum_angles[2]

    @cached_property(parent='illum_angles')
    def day(self):
        """Day side, sub-spacecraft incidence lower than 90°."""
        return self.inc <= TERMINATOR_INC

    @cached_property(parent='illum_angles')
    def night(self):
        """Night side, sub-spacecraft incidence larger than 90°."""
        return self.inc > TERMINATOR_INC

    @cached_property(parent='illum_angles')
    def nadir(self):
        """Nadir viewing, always True for the sub-spacecraft point."""
        return np.full_like(self.ets, True, dtype=bool)

    @cached_property(parent='illum_angles')
    def off_nadir(self):
        """Off-nadir viewing, always False for the sub-spacecraft point."""
        return np.full_like(self.ets, False, dtype=bool)

    @cached_property(parent='sc_pts')
    def ell_norm(self):
        """Sub-spacecraft local normal.

        Unitary vector pointing upward from the surface of the ellipsoid.

        See Also
        --------
        .sc_pts

        """
        log_traj.debug('Compute sub-observer local normal.')
        res = ell_norm(self.sc_pts.T, self.target.radii).T

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent=('sc_pts', 'sun_pos', 'ell_norm'))
    def solar_zenith_angle(self):
        """Sub-spacecraft solar zenith angle (degree).

        The angle is computed from the local normal
        on the ellipsoid. If the targeted body is a sphere,
        this value much be equal to the incidence angle.

        See Also
        --------
        Trajectory.sun_pos
        .sc_pts
        .ell_norm

        """
        log_traj.debug('Compute sub-observer solar zenith angle.')
        res = angle(self.sun_pos.T - self.sc_pts.T, self.ell_norm.T)

        log_traj.debug('Result: %r', res)
        return res


class InstrumentTrajectory(Trajectory):
    """Instrument trajectory object."""

    @property
    def lon_e(self):
        """Instrument surface intersect east longitude (degree)."""
        return self.boresight_rlonlat[1]

    @property
    def lat(self):
        """Instrument surface intersect latitude (degree)."""
        return self.boresight_rlonlat[2]

    @property
    def lonlat(self):
        """Instrument surface intersect east longitudes and latitudes (degree)."""
        return self.boresight_rlonlat[1:]

    @cached_property(parent=('sc_pts', 'boresight_pts'))
    def slant(self):
        """Line-of-sight distance to the boresight surface intersection (km).

        See Also
        --------
        .sc_pts
        .boresight_pts

        """
        log_traj.debug('Compute slant range to the boresight surface intersection.')
        return norm(self.sc_pos.T - self.boresight_pts.T)

    @cached_property(parent='slant')
    def ets_surface_intersect(self):
        """Ephemeris Time (ET) at the surface intersect point.

        The light time correction is only apply if :attr:`abcorr` in not ``NONE``.

        See Also
        --------
        .slant
        .SpiceAbCorr.dist_corr

        """
        return self.abcorr.dist_corr(self.ets, self.slant)

    @cached_property(parent=('boresight_rlonlat', 'ets_surface_intersect'))
    @check_kernels
    def local_time(self):
        """Instrument surface intersect local time (decimal hours)."""
        log_traj.info('Compute boresight intersection local time.')
        return local_time(self.ets_surface_intersect, self.lon_e, self.target)

    @cached_property(parent=('boresight_pts', 'ets_surface_intersect'))
    @check_kernels
    def illum_angles(self):
        """Instrument surface intersect illumination angles (degree).

        Incidence, emission and phase angles.

        See Also
        --------
        .boresight_pts
        .ets_surface_intersect

        """
        log_traj.info('Compute boresight intersection illumination geometry.')
        return illum_angles(
            self.ets_surface_intersect,
            self.spacecraft,
            self.target,
            self.boresight_pts,
            abcorr=self.abcorr,
            method='ELLIPSOID',
        )

    @property
    def inc(self):
        """Instrument surface intersect incidence angle (degree)."""
        return self.illum_angles[0]

    @property
    def emi(self):
        """Instrument surface intersect emission angle (degree)."""
        return self.illum_angles[1]

    @property
    def phase(self):
        """Instrument surface intersect phase angle (degree)."""
        return self.illum_angles[2]

    @cached_property(parent='illum_angles')
    def day(self):
        """Day side, boresight intersection incidence lower than 90°."""
        return self.inc <= TERMINATOR_INC

    @cached_property(parent='illum_angles')
    def night(self):
        """Night side, boresight intersection incidence larger than 90°."""
        return self.inc > TERMINATOR_INC

    @cached_property(parent='illum_angles')
    def nadir(self):
        """Nadir viewing, boresight intersection emission angle is lower than 1°."""
        return self.emi < 1

    @cached_property(parent='illum_angles')
    def off_nadir(self):
        """Off-nadir viewing, boresight intersection emission angle is larger than 1°."""
        return self.emi >= 1

    @cached_property(parent='boresight_pts')
    def ell_norm(self):
        """Instrument surface intersect local normal.

        Unitary vector pointing upward from the surface of the ellipsoid.

        See Also
        --------
        .boresight_pts

        """
        log_traj.debug('Compute sub-observer local normal.')
        res = ell_norm(self.boresight_pts.T, self.target.radii).T

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent=('boresight_pts', 'sun_pos', 'ell_norm'))
    def solar_zenith_angle(self):
        """Instrument surface intersect solar zenith angle (degree).

        The angle is computed from the local normal
        on the ellipsoid. If the targeted body is a sphere,
        this value much be equal to the incidence angle.

        See Also
        --------
        Trajectory.sun_pos
        .boresight_pts
        .ell_norm

        """
        log_traj.debug('Compute sub-observer solar zenith angle.')
        res = angle(self.sun_pos.T - self.boresight_pts.T, self.ell_norm.T)

        log_traj.debug('Result: %r', res)
        return res

    @cached_property(parent=('emi', 'dist'))
    @check_kernels
    def pixel_scale(self):
        """Instrument pixel scale (km/pix).

        Cross-track iFOV projected on the target body.

        See Also
        --------
        .emi
        Trajectory.dist

        """
        log_traj.debug('Compute pixel scale.')
        res = pixel_scale(
            self.observer,  # SpiceInstrument
            self.target,
            self.emi,
            self.dist,
        )

        log_traj.debug('Result: %r', res)
        return res

    @cached_property
    def fovs(self):
        """Instrument field of views collection."""
        return FovsCollection(self)


class Flyby(Trajectory):
    """Trajectory flyby object.

    The location of the closest approach point is
    recomputed internally to ensure that the flyby is correctly
    center on its lowest altitude with a resolution of 1 sec.

    To ensure better performances, the CA location is found
    in a 3 steps process:

    - 1st stage with a coarse resolution (20 min at CA ± 12h)
    - 2nd stage with a medium resolution (1 min at CA ± 30 min)
    - 3rd stage with a fine resolution (1 sec at CA ± 2 min)

    By default the final sampling temporal steps are irregular
    with a high resolution only around CA:

    - 1 pt from CA -12 h to CA  -2 h every 10 min
    - 1 pt from CA  -2 h to CA  -1 h every  1 min
    - 1 pt from CA  -1 h to CA -10 m every 10 sec
    - 1 pt from CA -10 m to CA +10 m every  1 sec
    - 1 pt from CA +10 m to CA  +1 h every 10 sec
    - 1 pt from CA  +1 h to CA  +2 h every  1 min
    - 1 pt from CA  +2 h to CA +12 h every 10 min

    = ``2,041 points`` around the CA point.

    Parameters
    ----------
    kernels: str or tuple
        List of kernels to be loaded in the SPICE pool.

    observer: str or spice.SpiceSpacecraft
        Observer SPICE reference.

    target: str or spice.SpiceBody
        Target SPICE reference.

    approx_ca_utc: float, string or numpy.datetime64
        Approximate CA datetime. This value will be re-computed.

    *dt: tuple(s), optional
        Temporal sequence around closest approach:

        `(duration, numpy.datetime unit, step value and unit)`

        See :func:`.et_ca_range` for more details.

    abcorr: str, optional
        Aberration corrections to be applied when computing
        the target's position and orientation.
        Only the SPICE keys are accepted.

    exclude: EventWindow, EventsDict or EventsList
        Event window, dict or list of events to exclude from the analysis.

    alt_min: float, optional
        Altitude minimal to a given target [km] (default: 150,000 km).

    See Also
    --------
    Trajectory
    .et_ca_range

    """

    def __init__(
        self,
        kernels,
        observer,
        target,
        approx_ca_utc,
        *dt,
        abcorr='NONE',
        exclude=None,
        alt_min=150_000,
    ):
        # Init with an empty temporal grid
        super().__init__(kernels, observer, target, [], abcorr=abcorr, exclude=exclude)

        if isinstance(self, SpacecraftTrajectory):
            self.__class__ = SpacecraftFlyby
        else:
            self.__class__ = InstrumentFlyby

        # Create the flyby temporal grid (symmetrical around CA)
        self.ets = self._flyby_ca_ets(approx_ca_utc, alt_min, dt)

    @check_kernels
    def _flyby_ca_ets(self, approx_ca_utc, alt_min, dt):
        """Closest Approach (CA) Ephemeris Times for a flyby.

        Parameters
        ----------
        approx_ca_utc: float, string or numpy.datetime64
            Approximate CA datetime, used as an initial step.

        alt_min: float, optional
            Altitude minimal to a given target [km] (default: 150,000 km).

        dt: tuple(s), optional
            Temporal sequence around closest approach:

            `(duration, numpy.datetime unit, step value and unit)`

            See :func:`planetary_coverage.spice.et_ca_range` for more details.

        Returns
        -------
        numpy.ndarray
            Ephemeris times around CA.

        Raises
        ------
        AltitudeTooHighError
            If the target altitude at CA is too high (above ``alt_min``).

        Note
        ----
        The light time correction (``abcorr``) is only apply in the lastest
        search stage.

        """
        # Check the pool coverage
        et_min, et_max = SpicePool.coverage(self.observer, self.target, fmt='ET')
        ets_coverage = {'et_min': et_min, 'et_max': et_max}

        # 1 - Coarse stage (20 min at CA ± 12h)
        coarse_ets = et_ca_range(approx_ca_utc, (24, 'h', '20 min'), **ets_coverage)
        log_traj.info('Coarse UTC window: %s', utc(coarse_ets[0], coarse_ets[-1]))

        coarse_traj = Trajectory(self.kernels, self.observer, self.target, coarse_ets)
        coarse_ca_utc = coarse_traj.utc[np.argmin(coarse_traj.dist)]
        log_traj.info('Coarse CA UTC: %s', coarse_ca_utc)

        # 2 - Medium stage (1 min at CA ± 30 min)
        medium_ets = et_ca_range(coarse_ca_utc, (30, 'm', '1 min'), **ets_coverage)
        log_traj.info('Medium UTC window: %s', utc(medium_ets[0], medium_ets[-1]))

        medium_traj = Trajectory(self.kernels, self.observer, self.target, medium_ets)
        medium_ca_utc = medium_traj.utc[np.argmin(medium_traj.dist)]
        log_traj.info('Medium CA UTC: %s', medium_ca_utc)

        # 3 - Fine stage (1 sec at CA ± 2 min)
        fine_ets = et_ca_range(medium_ca_utc, (2, 'm', '1 sec'), **ets_coverage)
        log_traj.info('Fine UTC window: %s', utc(fine_ets[0], fine_ets[-1]))

        fine_traj = Trajectory(
            self.kernels,
            self.observer,
            self.target,
            fine_ets,
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

        # Locate CA as min `alt` (not `dist` this time)
        i_ca = np.argmin(fine_traj.alt)

        # Check min altitude to make sure its valid flyby
        if fine_traj.alt[i_ca] > alt_min:
            raise AltitudeTooHighError(
                f'{fine_traj.alt[i_ca]:,.1f} km > {alt_min:,.1f} km at CA '
                f'(target: {self.target}).'
            )

        # Round [ms] digits to 1 sec precision
        fine_ca_utc = (fine_traj.utc[i_ca] + np.timedelta64(500, 'ms')).astype(
            'datetime64[s]'
        )
        log_traj.info('Fine CA UTC: %s', fine_ca_utc)

        # Compute the point around CA with `dt` time steps
        return et_ca_range(fine_ca_utc, *dt, **ets_coverage)

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}> '
            f'Observer: {self.observer} | '
            f'Target: {self.target}'
            f'\n - Altitude at CA: {self.alt_ca:,.1f} km'
            f'\n - UTC at CA: {self.utc_ca}'
            f'\n - Duration: {self.duration}'
            f'\n - Nb of pts: {len(self):,d}'
        )

    def __getitem__(self, item):
        traj = super().__getitem__(item)

        if isinstance(traj, SpacecraftTrajectory):
            traj.__class__ = SpacecraftFlyby

        elif isinstance(traj, InstrumentTrajectory):
            traj.__class__ = InstrumentFlyby

        return traj

    def new_traj(self, *, spacecraft=None, instrument=None, target=None):
        """Create a new flyby for a different observer.

        You can provide either one or multiple parameters as once.

        Parameters
        ----------
        spacecraft: str or SpiceSpacecraft, optional
            New spacecraft name.
        instrument: str or SpiceInstrument, optional
            New instrument name (see note below).
        target: str or SpiceBody, optional
            New target name (can not be changed).

        Returns
        -------
        Trajectory
            New trajectory object with new parameters.

        Raises
        ------
        ValueError
            If a target name change is requested.

        Note
        ----
        - The instrument name, can be either the instrument full name
          or just a suffix (ie. ``<SPACECRAFT>_<INSTRUMENT>``).

        - If the original trajectory has a instrument selected , you can
          discard it selected either by providing the ``spacecraft`` parameter
          alone or with ``instrument='none'`` syntax.

        """
        if target and target != self.target:
            raise ValueError(f'{self.__class__.__name__} can not change target name.')

        traj = Trajectory(
            self.kernels,
            spacecraft if spacecraft else self.spacecraft,
            self.target,
            self.ets,
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

        if instrument:
            traj = traj.new_traj(instrument=instrument)

        if isinstance(traj, SpacecraftTrajectory):
            traj.__class__ = SpacecraftFlyby

        elif isinstance(traj, InstrumentTrajectory):
            traj.__class__ = InstrumentFlyby

        return traj

    @property
    def duration(self):
        """Flyby duration."""
        return (self.stop - self.start).item()

    @cached_property
    def _i_ca(self):
        """Closest approach index."""
        return np.argmin(self.alt)

    @property
    def et_ca(self):
        """Closest approach ET time."""
        return self.ets[self._i_ca]

    @property
    def utc_ca(self):
        """Closest approach UTC time."""
        return self.utc[self._i_ca].astype('datetime64[s]')

    @property
    def date_ca(self):
        """Closest approach date."""
        return np.datetime64(self.utc_ca, 'D')

    @property
    def t_ca(self):
        """Time to closest approach."""
        return (self.utc - self.utc_ca).astype('timedelta64[s]')

    @property
    def lon_e_ca(self):
        """Sub-spacecraft west longitude at closest approach."""
        return self.lonlat[0][self._i_ca]

    @property
    def lat_ca(self):
        """Sub-spacecraft latitude at closest approach."""
        return self.lonlat[1][self._i_ca]

    @property
    def alt_ca(self):
        """Altitude at closest approach (km)."""
        return self.alt[self._i_ca]

    @property
    def inc_ca(self):
        """Incidence angle at closest approach (degree)."""
        return self.inc[self._i_ca]

    @property
    def emi_ca(self):
        """Emission angle at closest approach (degree)."""
        return self.emi[self._i_ca]

    @property
    def phase_ca(self):
        """Phase angle at closest approach (degree)."""
        return self.phase[self._i_ca]

    @cached_property
    def ca(self):
        """Closest approach point."""
        return Trajectory(self.kernels, self.observer, self.target, self.et_ca)

    @staticmethod
    def _interp(alt, alts, ets):
        """Interpolate UTC time for a given altitude."""
        if len(ets) > 1:
            if alt < alts.min():
                raise AltitudeTooLowError(f'{alt:,.1f} km < {alts.min():,.1f} km at CA')

            if alt > alts.max():
                raise AltitudeTooHighError(f'{alt:,.1f} km > {alts.max():,.1f} km at CA')

            if np.sum(alts[1:] >= alts[:-1]) != len(alts) - 1:
                raise ValueError('The function is not strictly increasing.')

            et_alt = np.interp(alt, alts, ets)
        else:
            et_alt = ets[0]

        return utc(et_alt, unit='s')

    @property
    def inbound(self):
        """Inbound part of the flyby, before CA."""
        return slice(self._i_ca, None, -1)

    @property
    def outbound(self):
        """Outbound part of the flyby, after CA."""
        return slice(self._i_ca, None)

    def alt_window(self, alt):
        """Interpolated altitude window during the flyby.

        Parameters
        ----------
        alt: float
            Altitude reach to start and stop the window (in km).

        Return
        ------
        numpy.datetime64, numpy.datetime64, numpy.timedelta64
            UTC start, stop times and duration.

        Raises
        ------
        AltitudeTooLowError
            If the altitude provided is lower than the CA altitude.
        AltitudeTooHighError
            If the altitude provided is higher than the
            max altitude of the flyby.

        """
        start = self._interp(alt, self.alt[self.inbound], self.ets[self.inbound])
        stop = self._interp(alt, self.alt[self.outbound], self.ets[self.outbound])

        return start, stop, (stop - start).item()


class SpacecraftFlyby(Flyby, SpacecraftTrajectory):
    """Spacecraft flyby object."""


class InstrumentFlyby(Flyby, InstrumentTrajectory):
    """Instrument flyby object."""

    @property
    def pixel_scale_ca(self):
        """Instrument pixel scale e at closest approach (km/pixel)."""
        return self.pixel_scale[self._i_ca]


class AltitudeTooLowError(Exception):
    """Min value is too low and never reach during the flyby."""


class AltitudeTooHighError(Exception):
    """Min value is too high and not sampled during the flyby."""
