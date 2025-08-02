"""SPICE datetime module.

The full metakernel specifications are available on NAIF website:

https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/time.html

"""

import re
from datetime import datetime as dt_native
from operator import itemgetter

import numpy as np

import spiceypy as sp


MONTHS = [
    'JAN',
    'FEB',
    'MAR',
    'APR',
    'MAY',
    'JUN',
    'JUL',
    'AUG',
    'SEP',
    'OCT',
    'NOV',
    'DEC',
]


def datetime(string, *others):
    """Parse datetime with SPICE convention.

    Parameters
    ----------
    string: str
        Input datetime string. Many format are supported, see the NAIF docs:

        https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/time.html#Input%20String%20Conversion

        If the string starts with a ``@``, this character will be discarded
        before being parsed.

    *others: str, optional
        Addition input string(s) to parse.

    Returns
    -------
    numpy.datetime64 or [numpy.datetime64, …]
        Parsed string(s) as numpy datetime64 object(s).

    Raises
    ------
    TypeError
        If the input time a not a string.
    ValueError
        If the provided string is not recognized by SPICE.

    Note
    ----
    This routine is the simple parser and does not require
    any kernel to be loaded.

    Warning
    -------
    This routine does not implement time conversion from ``UTC``
    to ``TDB`` or ``TDT``. You need to load at least a leapsecond kernel
    to perform these conversions.

    """
    if others:
        return [datetime(s) for s in [string, *others]]

    if isinstance(string, (tuple, list, np.ndarray)):
        return [datetime(s) for s in string]

    if isinstance(string, np.datetime64):
        return string

    if isinstance(string, dt_native):
        string = str(string)

    if not isinstance(string, str):
        raise TypeError(f'Input time must be a string not `{type(string)}`')

    if string.strip() in {'NaT', 'N/A', 'Unable to determine'}:
        return np.datetime64('NaT')

    if string.startswith('@'):
        string = string[1:]

    if '_' in string:
        string = string.replace('_', ' ')

    # Extract date and time parts and reformat the string
    jdn, h, m, s, ms = jdn_hms(string)
    yy, mm, dd = ymd(jdn)

    time = f'{yy:02d}-{mm:02d}-{dd:02d}T{h:02d}:{m:02d}:{s:02d}.{ms:03d}'

    return np.datetime64(clean_time(time))


def jdn_hms(string):
    """Extract the julian day and the time from a string.

    Parameters
    ----------
    string: str
        Input string to parse.

    Returns
    -------
    int, int, int, int, int
        Julian date number, hours, minutes, seconds and milliseconds values.

    Raises
    ------
    ValueError
        If the string can not be parsed as a SPICE time.

    Note
    ----
    The precision output time is rounded at 1 millisecond.
    The Julian Day Number is always defined with respect to the Gregorian calendar.

    Warning
    -------
    This definition of the Julian Date does not date into account
    leapseconds. Use Ephemeris Time (``et``) if you need a 1 second
    precision.

    See Also
    --------
    :py:func:`ymd`
    :py:func:`jd`

    """
    # Parse the string with SPICE to get the number of seconds after 2000.
    sp2000, err = sp.tparse(string)

    if err:
        raise ValueError(err)

    # Extract the time part
    s = int(np.floor(sp2000))
    msec = int(np.round((sp2000 - s) * 1_000))
    m, second = s // 60, s % 60
    h, minute = m // 60, m % 60
    hour = (h + 12) % 24

    # Extract the Days past 2000
    dp2000 = (s - (3_600 * hour + 60 * minute + second)) / sp.spd() + 0.5
    jdn = int(sp.j2000() + dp2000)

    return jdn, hour, minute, second, msec


def jd(string):
    """Convert time from a string to decimal Julian Date.

    Parameters
    ----------
    string: str
        Input time string to convert.

    Returns
    -------
    float
        Julian day decimal value.

    Raises
    ------
    ValueError
        If the string can not be parsed as a SPICE time.

    Warning
    -------
    This definition of the Julian Date does not date into account
    leapseconds. Use Ephemeris Time (``et``) if you need a 1 second
    precision.

    See Also
    --------
    :py:func:`jdn_hms`

    """
    j, h, m, s, msec = jdn_hms(string)
    return j + ((h - 12) * 3600 + m * 60 + s + msec / 1000) / sp.spd()


def ymd(jdn):
    """SPICE conversion from Julian Day to the Gregorian Calendar.

    Parameters
    ----------
    jdn: int
        Julian Date Number (no decimal value).

    Returns
    -------
    int, int, int
        Parsed year, month and day in the Gregorian Calendar.

    Warning
    -------
    The dates before October 15th, 1582 are still represented in the Gregorian
    calendar and not in the Julian calendar. This is not strictly correct but
    it does correspond to the default behavior of SPICE and Numpy:

    >>> spiceypy.tparse('1582-10-14')
    >>> numpy.datetime64('1582-10-14')

    Don't throw errors even if theses date don't exists,
    although the day before 1582-10-15 should be 1582-10-04.

    >>> numpy.datetime64('1582-10-15') - numpy.datetime64('1582-10-04') == \
        numpy.timedelta64(1,'D')
    False

    """
    alpha = np.floor((jdn - 1_867_216.25) / 36_524.25)
    s = jdn + 1 + alpha - np.floor(alpha / 4)

    b = s + 1_524
    c = np.floor((b - 122.1) / 365.25)
    d = np.floor(365.25 * c)
    e = np.floor((b - d) / 30.6001)

    day = b - d - np.floor(30.6001 * e)
    month = e - 1 if e < 14 else e - 13  # noqa: PLR2004 (formula)
    year = c - 4_716 if month > 2 else c - 4_715  # noqa: PLR2004 (formula)

    return int(year), int(month), int(day)


def clean_time(time):
    """Clean time string (discard null leading values)."""
    if '.' in time:
        time = time.rstrip('0')
        time = time.rstrip('.')

    for _ in range(2):  # :MM:SS
        if time.endswith(':00'):
            time = time[:-3]

    if time.endswith('T00'):  # THH
        time = time[:-3]

    for _ in range(2):  # -MM-DD
        if time.endswith('-01'):
            time = time[:-3]

    return time


def sorted_datetimes(times, index=None, reverse=False):
    """Sort a list of datetimes.

    Parameters
    ----------
    times: list
        List of datetimes to sort.
    index: int or tuple, optional
        Index (or indexes) to use when a list of tuple/list is provided
        (default: None).
    reverse: bool, optional
        Sort the list in reverse order.

    Returns
    -------
    list
        Sorted list of datetimes.

    Raises
    ------
    TypeError
        If the provided ``index`` is not ``None``, ``int``, ``list`` or ``tuple``.

    Note
    ----
    - The input ``times`` don't need to be pre-formatted.
    - The output list is only reordered, the input ``times`` are not post-formatted.

    """
    # Extract the datetime elements
    if index is None:
        elements = times
    elif isinstance(index, int):
        elements = [t[index] for t in times]
    elif isinstance(index, (list, tuple)):
        elements = [[t[i] for i in index] for t in times]
    else:
        raise TypeError('Invalid `index`. It should be `None`, `int`, `list` or `tuple`.')

    indexes = sorted(
        enumerate(datetime(elements)), key=itemgetter(slice(1, None)), reverse=reverse
    )

    return [times[i] for i, _ in indexes]


def iso(time):
    """Reformat datetime to ISO format."""
    if isinstance(time, str):
        return iso(datetime(time))

    if isinstance(time, np.datetime64):
        time = time.item()

    s = f'{time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]}Z'

    return s[:-5] + 'Z' if s.endswith('.000Z') else s


def mapps_datetime(time):
    """Reformat datetime in MAPPS format.

    .. code-block:: text

        2001-JAN-01_12:34:56.789

    Warning
    -------
    MAPPS datetime is not natively compatible with
    the SPICE time patterns.

    """
    t = iso(time)
    year, month, day, hms = t[:4], t[5:7], t[8:10], t[11:-1]
    return f'{year}-{MONTHS[int(month) - 1]}-{day}_{hms}'


def np_datetime_str(numpy_datetime64) -> str:
    """Convert datetime from numpy.datetime64 to ISO string."""
    if np.isnat(numpy_datetime64):
        return 'NaT'

    dt = numpy_datetime64.item()
    stime = dt.isoformat() + ('' if isinstance(dt, dt_native) else 'T00:00:00')

    if '.' in stime:
        stime = stime.rstrip('0')  # Remove trailing zeros for the decimal values
        stime = stime.rstrip('.')

    return stime


def np_date_str(numpy_datetime64) -> str:
    """Extract date from numpy.datetime64 as a string."""
    if np.isnat(numpy_datetime64):
        return 'NaT'

    dt = numpy_datetime64.item()

    return str(dt.date()) if isinstance(dt, dt_native) else str(dt)


DT_TIMEDELTA = re.compile(
    r'(?P<sign>[+-])?(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})(?:\.(?P<ms>\d+))?'
)

NP_TIMEDELTA = re.compile(
    r'(?P<value>\d+)\s?(?P<unit>millisecond|month|ms|[smhHdDMyY])s?'
)

NP_TIMEDELTA_UNITS = {
    'millisecond': 'ms',
    'H': 'h',
    'd': 'D',
    'month': 'M',
    'y': 'Y',
}


def timedelta(step):
    """Parse step as :class:`numpy.timedelta64` object.

    The value must be a :obj:`int` followed by an optional
    space and a valid unit.

    Examples of valid units:

    - ``ms``, ``msec``, ``millisecond``
    - ``s``, ``sec``, ``second``
    - ``m``, ``min``, ``minute``
    - ``h``, ``hour``
    - ``D``, ``day``
    - ``M``, ``month``
    - ``Y``, ``year``

    Parameters
    ----------
    step: str
        Step to parse.

    Returns
    -------
    numpy.timedelta64
        Parsed numpy.timedelta64 step.

    Raises
    ------
    ValueError
        If the provided step format or unit is invalid.

    """
    if isinstance(step, np.timedelta64):
        return step

    if match := DT_TIMEDELTA.match(step):
        sign, h, m, s, ms = match.groups()
        return (-1 if sign == '-' else 1) * (
            np.timedelta64(int(h), 'h')
            + np.timedelta64(int(m), 'm')
            + np.timedelta64(int(s), 's')
            + (np.timedelta64(int(1_000 * float(f'0.{ms}')), 'ms') if ms else 0)
        )

    if match := NP_TIMEDELTA.match(step):
        value, unit = match.groups()
        return np.timedelta64(int(value), NP_TIMEDELTA_UNITS.get(unit, unit))

    raise ValueError(f'Invalid step format: `{step}`')
