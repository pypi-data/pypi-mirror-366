"""SPICE times module.

The full metakernel specifications are available on NAIF website:

https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/time.html

"""

import re

import numpy as np

import spiceypy as sp


TWO_ELEMENTS = 2


def et(utc, *times):
    """Convert utc time to ephemeris time.

    Parameters
    ----------
    utc: any
        Input UTC time. All SPICE time formats are accepted.

        For example:

        - ``YYYY-MM-DDThh:mm:ss[.ms][Z]``
        - ``YYYY-MON-DD hh:mm:ss``

        Multiple iterable input (:obj:`slice`, :obj:`list`,
        :obj:`tuple`, :obj:`numpy.ndarray`) are accepted as well.

        If an :obj:`int` or :obj:`float` is provided,
        the value is considered to be in ET and is not
        not converted.

    *times: str
        Addition input UTC time(s) to parse.

    Caution
    -------
    The value is rounded at 1e-3 precision to avoid
    conversion rounding error with datetime at ``ms``
    precisions values.

    """
    if times:
        return [et(t) for t in [utc, *times]]

    if utc is None:
        return utc

    if isinstance(utc, (int, float, np.int64, np.float64)):
        return utc

    if isinstance(utc, slice):
        return et_range(utc.start, utc.stop, utc.step)

    if isinstance(utc, (tuple, list, np.ndarray)):
        return np.hstack([et(t) for t in utc]) if any(utc) else np.array([])

    return np.round(sp.str2et(str(utc)), 3)


def sclk(sc, utc, *times):
    """Convert utc time to spacecraft.

    Parameters
    ----------
    sc: int
        NAIF spacecraft ID code.
    utc: str
        Input UTC time. All SPICE time formats are accepted.

        For example:

        - ``YYYY-MM-DDThh:mm:ss[.ms][Z]``
        - ``YYYY-MON-DD hh:mm:ss``

    *times: str
        Addition input UTC time(s) to parse.

    """
    if times:
        return [sclk(sc, t) for t in [utc, *times]]

    if isinstance(utc, (tuple, list, np.ndarray)):
        return [sclk(sc, t) for t in utc]

    utc = utc[:-1] if str(utc).endswith('Z') else str(utc)
    return sp.sce2c(sc, sp.str2et(utc))


def utc(et, *ets, unit='ms'):
    """Convert ephemeris time to UTC time(s) in ISOC format.

    Parameters
    ----------
    et: str
        Input Ephemeris time.
    *ets: str
        Addition input ET time(s) to parse.
    unit: str, optional
        Numpy datetime unit (default: 'ms').

    Returns
    -------
    numpy.datetime64 or [numpy.datetime64, …]
        Parsed time in ISOC format: ``YYYY-MM-DDThh:mm:ss.ms``
        as :obj:`numpy.datetime64` object.

    """
    if ets:
        return utc([et, *ets], unit=unit)

    if isinstance(et, (tuple, list, np.ndarray)):
        return np.array([utc(t, unit=unit) for t in et], dtype='datetime64')

    return np.datetime64(sp.et2utc(et, 'ISOC', 3), unit)


def tdb(et, *ets):
    """Convert ephemeris time to Barycentric Dynamical Time(s).

    Parameters
    ----------
    et: str
        Input Ephemeris time.
    *ets: str
        Addition input ET time(s) to parse.

    Returns
    -------
    str or list
        Parsed time in TDB format: ``YYYY-MM-DD hh:mm:ss.ms TDB``

    """
    if ets:
        return tdb([et, *ets])

    if isinstance(et, (tuple, list, np.ndarray)):
        return np.array([tdb(t) for t in et], dtype='<U27')

    return sp.timout(et, 'YYYY-MM-DD HR:MN:SC.### TDB ::TDB')


STEPS = re.compile(
    r'(?P<value>\d+(?:\.\d+)?)\s?(?P<unit>millisecond|month|ms|[smhdDMyY])s?'
)


DURATIONS = {
    'ms': 0.001,
    'millisecond': 0.001,
    's': 1,
    'sec': 1,
    'm': 60,
    'h': 3_600,  # 60 x 60
    'D': 86_400,  # 60 x 60 x 24
    'd': 86_400,  # 60 x 60 x 24
    'M': 2_635_200,  # 60 x 60 x 24 x 61 // 2
    'month': 2_635_200,  # 60 x 60 x 24 x 61 // 2
    'Y': 31_536_000,  # 60 x 60 x 24 x 365
    'y': 31_536_000,  # 60 x 60 x 24 x 365
}


def parse_step(step):
    """Parse temporal step in secondes.

    The value must be a `int` or a `float`
    followed by an optional space and
    a valid unit.

    Examples of valid units:

    - ``ms``, ``msec``, ``millisecond``
    - ``s``, ``sec``, ``second``
    - ``m``, ``min``, ``minute``
    - ``h``, ``hour``
    - ``D``, ``day``
    - ``M``, ``month``
    - ``Y``, ``year``

    Short unit version are accepted, but
    ``H`` and ``S`` are not accepted to avoid
    the confusion between ``m = minute``
    and ``M = month``.

    Plural units are also valid.

    Note
    ----
    Month step is based on the average month duration (30.5 days).
    No parsing of the initial date is performed.

    Parameters
    ----------
    step: str
        Step to parse.

    Returns
    -------
    int or float
        Duration step parsed in secondes

    Raises
    ------
    ValueError
        If the provided step format or unit is invalid.

    """
    match = STEPS.match(step)

    if not match:
        raise ValueError(f'Invalid step format: `{step}`')

    value, unit = match.group('value', 'unit')
    return (float(value) if '.' in value else int(value)) * DURATIONS[unit]


def et_range(start, stop, step='1s', endpoint=True):
    """Ephemeris temporal range.

    Parameters
    ----------
    start: str
        Initial start UTC time.

    stop: str
        Stop UTC time.

    step: int or str, optional
        Temporal step to apply between the start
        and stop UTC times (default: `1s`).
        If the :py:attr:`step` provided is an `int >= 2`
        it will correspond to the number of samples
        to generate.

    endpoint: bool, optional
        If True, :py:attr:`stop` is the last sample.
        Otherwise, it is not included (default: `True`).

    Returns
    -------
    numpy.array
        List of ephemeris times.

    Raises
    ------
    TypeError
        If the provided step is invalid.
    ValueError
        If the provided stop time is before the start time.

    See Also
    --------
    et_range
    et_ranges
    et_ca_range
    utc_range
    utc_ranges
    utc_ca_range

    """
    et_start, et_stop = et(start, stop)

    if et_stop < et_start:
        raise ValueError(f'Stop time ({stop}) should be after start time ({start})')

    if et_start == et_stop:
        return np.array([et_start])

    if isinstance(step, str):
        ets = np.round(np.arange(et_start, et_stop, parse_step(step)), 3)

        if endpoint and et_stop != ets[-1]:
            ets = np.append(ets, et_stop)

        elif not endpoint and et_stop == ets[-1]:
            ets = ets[:-1]

        return ets

    if isinstance(step, int) and step >= TWO_ELEMENTS:
        return np.linspace(et_start, et_stop, step, endpoint=endpoint)

    raise TypeError('Step must be a `str` or a `int ≥ 2`')


def et_ranges(*ranges):
    """Ephemeris times with a irregular sequence.

    Parameters
    ----------
    *ranges: tuple(s), optional
        Sequence(s) of (start, stop, step) tuples.

    Returns
    -------
    [float, …]
        Ephemeris times distribution.

    Note
    ----
    If a start time match the previous stop time, the two sequence will be merged.

    See Also
    --------
    et_range
    utc_ranges

    """
    starts, stops, steps = np.transpose(ranges)

    endpoints = [
        end != begin for end, begin in zip(stops[:-1], starts[1:], strict=False)
    ] + [True]

    return np.concatenate([
        et_range(start, stop, step, endpoint=endpoint)
        for start, stop, step, endpoint in zip(
            starts, stops, steps, endpoints, strict=False
        )
    ])


def et_ca_range(t, *dt, et_min=None, et_max=None):
    """Ephemeris times around closest approach with a redefined sequence.

    Parameters
    ----------
    t: str or numpy.datetime64
        Closest approach UTC time.

    *dt: tuple(s), optional
        Temporal sequence around closest approach:

        .. code-block:: text

            (duration, numpy.datetime unit, step value and unit)

        By default, the pattern is:

        .. code-block::

            [
                (10, 'm', '1 sec'),
                (1, 'h', '10 sec'),
                (2, 'h', '1 min'),
                (12, 'h', '10 min'),
            ]

        With will lead to the following sampling:

        - 1 pt from CA -12 h to CA  -2 h every 10 min
        - 1 pt from CA  -2 h to CA  -1 h every  1 min
        - 1 pt from CA  -1 h to CA -10 m every 10 sec
        - 1 pt from CA -10 m to CA +10 m every  1 sec
        - 1 pt from CA +10 m to CA  +1 h every 10 sec
        - 1 pt from CA  +1 h to CA  +2 h every  1 min
        - 1 pt from CA  +2 h to CA +12 h every 10 min

        = 2,041 points around the CA point.

    et_min: float, optional
        Smallest valid value of ET (default: `None`).

    et_max: float, optional
        Largest valid value of ET (default: `None`).

    Returns
    -------
    [float, …]
        Ephemeris times distribution around CA.

    Note
    ----
    The distribution of ET is symmetrical around CA.

    See Also
    --------
    et_range
    et_ranges
    utc_ca_range

    """
    if not dt:
        dt = [
            # Default temporal pattern
            (10, 'm', '1 sec'),
            (1, 'h', '10 sec'),
            (2, 'h', '1 min'),
            (12, 'h', '10 min'),
        ]

    if not isinstance(t, np.datetime64):
        t = np.datetime64(t)

    starts = [t - np.timedelta64(v, u) for v, u, _ in dt[::-1]] + [
        t + np.timedelta64(v, u) for v, u, _ in dt[:-1]
    ]

    stops = [t - np.timedelta64(v, u) for v, u, _ in dt[-2::-1]] + [
        t + np.timedelta64(v, u) for v, u, _ in dt
    ]

    steps = [s for _, _, s in dt[::-1] + dt[1:]]

    ranges = np.transpose([starts, stops, steps])

    ets = et_ranges(*ranges)

    if et_min:
        if et_max:
            return ets[(et_min <= ets) & (ets <= et_max)]

        return ets[et_min <= ets]

    if et_max:
        return ets[ets <= et_max]

    return ets


def utc_range(start, stop, step='1s', endpoint=True):
    """UTC temporal range.

    Parameters
    ----------
    start: str
        Initial start UTC time.

    stop: str
        Stop UTC time.

    step: int or str, optional
        Temporal step to apply between the start
        and stop UTC times (default: `1s`).
        If the :py:attr:`step` provided is an `int >= 2`
        it will correspond to the number of samples
        to generate.

    endpoint: bool, optional
        If True, :py:attr:`stop` is the last sample.
        Otherwise, it is not included (default: `True`).

    Returns
    -------
    numpy.array
        List of UTC times.

    Raises
    ------
    TypeError
        If the provided step is invalid.
    ValueError
        If the provided stop time is before the start time.

    See Also
    --------
    et_range

    """
    return utc(et_range(start, stop, step=step, endpoint=endpoint))


def utc_ranges(*ranges):
    """UTC times with a irregular sequence.

    Parameters
    ----------
    *ranges: tuple(s), optional
        Sequence(s) of (start, stop, step) tuples.

    Returns
    -------
    [float, …]
        UTC times distribution.

    Note
    ----
    If a start time match the previous stop time, the two sequence will be merged.

    See Also
    --------
    et_ranges

    """
    return utc(et_ranges(*ranges))


def utc_ca_range(t, *dt, utc_min=None, utc_max=None):
    """UTC times around closest approach with a redefined sequence.

    Parameters
    ----------
    t: str or numpy.datetime64
        Closest approach UTC time.

    *dt: tuple(s), optional
        Temporal sequence around closest approach (see ``et_ca_range`` for details).

    utc_min: float, optional
        Smallest valid value in UTC (default: `None`).

    utc_max: float, optional
        Largest valid value in UTC (default: `None`).

    Returns
    -------
    [float, …]
        UTC times distribution around CA.

    Note
    ----
    The distribution of ET is symmetrical around CA.

    See Also
    --------
    et_ca_range

    """
    return utc(et_ca_range(t, *dt, et_min=et(utc_min), et_max=et(utc_max)))
