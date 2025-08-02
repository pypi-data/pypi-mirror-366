"""Masked trajectory module."""

from functools import wraps

import numpy as np

from .fovs import MaskedFovsCollection, SegmentedFovsCollection
from ..misc import Segment, cached_property


def trajectory_property(func):
    """Parent trajectory property decorator."""

    @property
    @wraps(func)
    def original_property(_self):
        traj = _self.traj
        prop = func.__name__

        if not hasattr(traj, prop):
            raise AttributeError(
                f'The original trajectory does not have a `{prop}` attribute.'
            )

        return getattr(traj, prop)

    return original_property


def masked_trajectory_property(func):
    """Masked parent trajectory property decorator."""

    @property
    @wraps(func)
    def masked_property(_self):
        traj = _self.traj
        prop = func.__name__

        if not hasattr(traj, prop):
            raise AttributeError(
                f'The original trajectory does not have a `{prop}` attribute.'
            )

        dtype, nan = (
            (float, np.nan) if prop != 'utc' else (np.datetime64, np.datetime64('NaT'))
        )

        values = np.array(getattr(traj, prop), dtype=dtype)
        values[..., _self.mask] = nan

        return values

    return masked_property


def masked_trajectory_method(func):
    """Masked parent trajectory method decorator."""

    @wraps(func)
    def masked_method(_self, *args, **kwargs):
        traj = _self.traj
        method = func.__name__

        if not hasattr(traj, method):
            raise AttributeError(
                f'The original trajectory does not have a `{method}` method.'
            )

        dtype, nan = (
            (float, np.nan)
            if method != 'utc_at'
            else (np.datetime64, np.datetime64('NaT'))
        )

        values = np.array(getattr(traj, method)(*args, **kwargs), dtype=dtype)
        values[..., _self.mask] = nan

        return values

    return masked_method


def segment_trajectory_property(func):
    """Segment parent trajectory property decorator."""

    @property
    @wraps(func)
    def segment_property(_self):
        traj = _self.traj
        prop = func.__name__

        if not hasattr(traj, prop):
            raise AttributeError(
                f'The original trajectory does not have a `{prop}` attribute.'
            )

        return np.array(getattr(traj, prop))[..., _self.seg]

    return segment_property


def segment_trajectory_method(func):
    """Segment parent trajectory method decorator."""

    @wraps(func)
    def segment_method(_self, *args, **kwargs):
        traj = _self.traj
        method = func.__name__

        if not hasattr(traj, method):
            raise AttributeError(
                f'The original trajectory does not have a `{method}` attribute.'
            )

        return np.array(getattr(traj, method)(*args, **kwargs))[..., _self.seg]

    return segment_method


class MaskedTrajectory:
    """Generic masked trajectory object."""


class MaskedSpacecraftTrajectory(MaskedTrajectory):  # noqa: PLR0904 (too-many-public-methods)
    """Masked spacecraft trajectory object.

    Parameters
    ----------
    traj:
        Original trajectory.
    mask: numpy.ndarray
        Bool list of the points to mask.

    """

    def __init__(self, traj, mask):
        self.traj = traj
        self.mask = mask
        self.seg = Segment(np.invert(mask))

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}> '
            f'Observer: {self.observer} | '
            f'Target: {self.target}'
            f'\n - First UTC start time: {self.start}'
            f'\n - Last UTC stop time: {self.stop}'
            f'\n - Nb of pts: {len(self):,d} (+{self.nb_masked:,d} masked)'
            f'\n - Nb of segments: {self.nb_segments}'
        )

    def __len__(self):
        """Number of point in the trajectory."""
        return len(self.traj) - self.nb_masked

    def __and__(self, other):
        """And ``&`` operator."""
        return self.traj.mask(self.traj.intersect(other) | self.mask)

    def __xor__(self, other):
        """Hat ``^`` operator."""
        return self.traj.mask(self.traj.intersect(other, outside=True) | self.mask)

    def __getitem__(self, _):
        raise ReferenceError(
            'Change of target or observer should be performed '
            'on the original trajectory not on the masked trajectory.'
        )

    def __iter__(self):
        for seg in self.seg:
            yield SegmentedSpacecraftTrajectory(self.traj, seg)

    @property
    def nb_masked(self):
        """Number of point masked."""
        return np.sum(self.mask)

    @property
    def nb_segments(self):
        """Number of segment(s)."""
        return len(self.seg)

    @property
    def starts(self):
        """UTC start time segments."""
        return self.utc[self.seg.istarts]

    @property
    def stops(self):
        """UTC stop time segments."""
        return self.utc[self.seg.istops]

    @property
    def start(self):
        """UTC start time of the initial segment."""
        return self.starts[0] if len(self) != 0 else np.datetime64('NaT')

    @property
    def stop(self):
        """UTC stop time of the last segment."""
        return self.stops[-1] if len(self) != 0 else np.datetime64('NaT')

    @property
    def windows(self):
        """Segmented windows (UTC start and stop times)."""
        return np.vstack([self.starts, self.stops]).T

    @trajectory_property
    def observer(self):
        """Observer SPICE reference for the trajectory."""

    @trajectory_property
    def target(self):
        """Target SPICE reference for the trajectory."""

    @masked_trajectory_property
    def ets(self):
        """Masked ephemeris times."""

    @masked_trajectory_property
    def utc(self):
        """Masked UTC times."""

    @masked_trajectory_property
    def lon_e(self):
        """Masked sub-observer ground track east longitudes (degree)."""

    @masked_trajectory_property
    def lat(self):
        """Masked sub-observer ground track east latitudes (degree)."""

    @masked_trajectory_property
    def lonlat(self):
        """Masked sub-observer ground track east longitudes and latitudes (degree)."""

    @masked_trajectory_property
    def local_time(self):
        """Masked sub-observer local time (decimal hours)."""

    @masked_trajectory_property
    def inc(self):
        """Masked sub-observer incidence angle (degree)."""

    @masked_trajectory_property
    def emi(self):
        """Masked sub-observer emission angle (degree)."""

    @masked_trajectory_property
    def phase(self):
        """Masked sub-observer phase angle (degree)."""

    @masked_trajectory_property
    def day(self):
        """Masked day side."""

    @masked_trajectory_property
    def night(self):
        """Masked night side."""

    @masked_trajectory_property
    def dist(self):
        """Masked spacecraft distance to target body center (km)."""

    @masked_trajectory_property
    def alt(self):
        """Masked spacecraft altitude to the sub-observer point (km)."""

    @masked_trajectory_property
    def target_size(self):
        """Masked target angular size (degrees)."""

    @masked_trajectory_property
    def slant(self):
        """Masked spacecraft line-of-sight distance to the sub-observer point (km)."""

    @masked_trajectory_property
    def quaternions(self):
        """Masked observer quaternions (degree)."""

    @masked_trajectory_property
    def ra(self):
        """Masked boresight right ascension pointing (degree)."""

    @masked_trajectory_property
    def dec(self):
        """Masked boresight declination pointing (degree)."""

    @masked_trajectory_property
    def radec(self):
        """Masked boresight RA/DEC pointing (degree)."""

    @masked_trajectory_property
    def sun_lonlat(self):
        """Masked sub-solar ground track coordinates (degree)."""

    @masked_trajectory_property
    def solar_zenith_angle(self):
        """Masked sub-observer solar zenith angle (degree)."""

    @masked_trajectory_property
    def solar_longitude(self):
        """Masked target seasonal solar longitude (degree)."""

    @masked_trajectory_property
    def true_anomaly(self):
        """Masked target orbital true anomaly (degree)."""

    @masked_trajectory_property
    def groundtrack_velocity(self):
        """Masked groundtrack velocity (km/s)."""

    @masked_trajectory_method
    def distance_to(self, *args, **kwargs):
        """Masked distance to a target body (km)."""

    @masked_trajectory_method
    def ets_at(self, *args, **kwargs):
        """Masked ephemeris time at target location with light-time corrections."""

    @masked_trajectory_method
    def utc_at(self, *args, **kwargs):
        """Masked UTC time at target location with light-time corrections."""

    @masked_trajectory_method
    def angular_size(self, *args, **kwargs):
        """Masked Angle size of a given target seen from the spacecraft (degrees)."""

    @masked_trajectory_method
    def angle_between(self, *args, **kwargs):
        """Masked angle between 2 rays in spacecraft frame (degrees)."""

    @masked_trajectory_method
    def station_azel(self, *args, **kwargs):
        """Masked spacecraft azimuth and elevation seen from a tracking station."""

    @masked_trajectory_method
    def target_separation(self, *args, **kwargs):
        """Masked angular target separation (degrees)."""


class MaskedInstrumentTrajectory(MaskedSpacecraftTrajectory):
    """Masked instrument trajectory."""

    def __iter__(self):
        for seg in self.seg:
            yield SegmentedInstrumentTrajectory(self.traj, seg)

    @masked_trajectory_property
    def lon_e(self):
        """Masked instrument surface intersect east longitudes (degree)."""

    @masked_trajectory_property
    def lat(self):
        """Masked instrument surface intersect east latitudes (degree)."""

    @masked_trajectory_property
    def lonlat(self):
        """Masked instrument surface intersect east longitudes and latitudes (degree)."""

    @masked_trajectory_property
    def local_time(self):
        """Masked instrument surface intersect local time (decimal hours)."""

    @masked_trajectory_property
    def inc(self):
        """Masked instrument surface intersect incidence angle (degree)."""

    @masked_trajectory_property
    def emi(self):
        """Masked instrument surface intersect emission angle (degree)."""

    @masked_trajectory_property
    def phase(self):
        """Masked instrument surface intersect phase angle (degree)."""

    @masked_trajectory_property
    def slant(self):
        """Masked line-of-sight distance to the boresight surface intersection (km)."""

    @masked_trajectory_property
    def solar_zenith_angle(self):
        """Masked instrument surface intersect solar zenith angle (degree)."""

    @masked_trajectory_property
    def pixel_scale(self):
        """Masked instrument pixel scale (km/pix)."""

    @cached_property
    def fovs(self):
        """Masked instrument field of view paths collection."""
        return MaskedFovsCollection(self.traj.fovs, self.mask)


class SegmentedTrajectory:
    """Generic segmented trajectory object."""


class SegmentedSpacecraftTrajectory(SegmentedTrajectory):  # noqa: PLR0904 (too-many-public-methods)
    """Segmented spacecraft trajectory object.

    Parameters
    ----------
    traj:
        Original trajectory.
    segment: slice
        Segment to extract.

    """

    def __init__(self, traj, segment):
        self.traj = traj
        self.seg = segment
        self.mask = np.full(len(self.traj), True)
        self.mask[self.seg] = False

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}> '
            f'Observer: {self.observer} | '
            f'Target: {self.target}'
            f'\n - First UTC start time: {self.start}'
            f'\n - Last UTC stop time: {self.stop}'
            f'\n - Nb of pts: {len(self):,d}'
        )

    def __len__(self):
        """Number of point in the trajectory."""
        return len(self.ets)

    def __and__(self, other):
        """And ``&`` operator."""
        return self.traj.mask(self.traj.intersect(other) | self.mask)

    def __xor__(self, other):
        """Hat ``^`` operator."""
        return self.traj.mask(self.traj.intersect(other, outside=True) | self.mask)

    def __getitem__(self, _):
        raise ReferenceError(
            'Change of target or observer should be performed '
            'on the original trajectory not on the segmented trajectory.'
        )

    def __iter__(self):
        yield self

    def __hash__(self):
        """Kernels hash."""
        return hash(self.traj)

    @trajectory_property
    def kernels(self):
        """Trajectory required kernels."""

    @trajectory_property
    def observer(self):
        """Observer SPICE reference for the trajectory."""

    @trajectory_property
    def target(self):
        """Target SPICE reference for the trajectory."""

    @trajectory_property
    def abcorr(self):
        """Trajectory aberration correction."""

    @segment_trajectory_property
    def ets(self):
        """Segment Ephemeris Times."""

    @segment_trajectory_property
    def utc(self):
        """Segment UTC times."""

    @property
    def start(self):
        """Segment UTC start time."""
        return self.utc[0]

    @property
    def stop(self):
        """Segment UTC stop time."""
        return self.utc[-1]

    @segment_trajectory_property
    def lon_e(self):
        """Segment sub-observer ground track east longitudes (degree)."""

    @segment_trajectory_property
    def lat(self):
        """Segment sub-observer ground track east latitudes (degree)."""

    @segment_trajectory_property
    def lonlat(self):
        """Segment sub-observer ground track coordinates (degree)."""

    @segment_trajectory_property
    def local_time(self):
        """Segment sub-observer local time (decimal hours)."""

    @segment_trajectory_property
    def inc(self):
        """Segment sub-observer incidence angle (degree)."""

    @segment_trajectory_property
    def emi(self):
        """Segment sub-observer emission angle (degree)."""

    @segment_trajectory_property
    def phase(self):
        """Segment sub-observer phase angle (degree)."""

    @segment_trajectory_property
    def day(self):
        """Segment day side."""

    @segment_trajectory_property
    def night(self):
        """Segment night side."""

    @segment_trajectory_property
    def dist(self):
        """Segment spacecraft distance to target body center (km)."""

    @segment_trajectory_property
    def alt(self):
        """Segment spacecraft altitude to the sub-observer point (km)."""

    @segment_trajectory_property
    def target_size(self):
        """Segment target angular size (degrees)."""

    @segment_trajectory_property
    def slant(self):
        """Segment spacecraft line-of-sight distance to the sub-observer point (km)."""

    @segment_trajectory_property
    def quaternions(self):
        """Segment observer quaternions (degree)."""

    @segment_trajectory_property
    def ra(self):
        """Segment boresight right ascension pointing (degree)."""

    @segment_trajectory_property
    def dec(self):
        """Segment boresight declination pointing (degree)."""

    @segment_trajectory_property
    def radec(self):
        """Segment boresight RA/DEC pointing (degree)."""

    @segment_trajectory_property
    def sun_lonlat(self):
        """Segment sub-solar ground track coordinates (degree)."""

    @segment_trajectory_property
    def solar_zenith_angle(self):
        """Segment sub-observer solar zenith angle (degree)."""

    @segment_trajectory_property
    def solar_longitude(self):
        """Segment target seasonal solar longitude (degree)."""

    @segment_trajectory_property
    def true_anomaly(self):
        """Segment target orbital true anomaly (degree)."""

    @segment_trajectory_property
    def groundtrack_velocity(self):
        """Segment groundtrack velocity (km/s)."""

    @segment_trajectory_method
    def distance_to(self, *args, **kwargs):
        """Segment distance to a target body (km)."""

    @segment_trajectory_method
    def ets_at(self, *args, **kwargs):
        """Segment ephemeris time at target location with light-time corrections."""

    @segment_trajectory_method
    def utc_at(self, *args, **kwargs):
        """Segment UTC time at target location with light-time corrections."""

    @segment_trajectory_method
    def angular_size(self, *args, **kwargs):
        """Segment Angle size of a given target seen from the spacecraft (degrees)."""

    @segment_trajectory_method
    def angle_between(self, *args, **kwargs):
        """Segment angle between 2 rays in spacecraft frame (degrees)."""

    @segment_trajectory_method
    def station_azel(self, *args, **kwargs):
        """Segment spacecraft azimuth and elevation seen from a tracking station."""

    @segment_trajectory_method
    def target_separation(self):
        """Segment angular target separation (degrees)."""


class SegmentedInstrumentTrajectory(SegmentedSpacecraftTrajectory):
    """Segmented instrument trajectory."""

    @segment_trajectory_property
    def lon_e(self):
        """Segment instrument surface intersect east longitudes (degree)."""

    @segment_trajectory_property
    def lat(self):
        """Segment instrument surface intersect east latitudes (degree)."""

    @segment_trajectory_property
    def lonlat(self):
        """Segment instrument surface intersect east longitudes and latitudes (degree)."""

    @segment_trajectory_property
    def local_time(self):
        """Segment instrument surface intersect local time (decimal hours)."""

    @segment_trajectory_property
    def inc(self):
        """Segment instrument surface intersect incidence angle (degree)."""

    @segment_trajectory_property
    def emi(self):
        """Segment instrument surface intersect emission angle (degree)."""

    @segment_trajectory_property
    def phase(self):
        """Segment instrument surface intersect phase angle (degree)."""

    @segment_trajectory_property
    def slant(self):
        """Segment line-of-sight distance to the boresight surface intersection (km)."""

    @segment_trajectory_property
    def solar_zenith_angle(self):
        """Segment instrument surface intersect solar zenith angle (degree)."""

    @segment_trajectory_property
    def pixel_scale(self):
        """Segment instrument pixel scale (km/pix)."""

    @cached_property
    def fovs(self):
        """Segment instrument field of view paths collection."""
        return SegmentedFovsCollection(self)
