"""Maps ticks helpers."""

from matplotlib.dates import AutoDateLocator, ConciseDateFormatter
from matplotlib.ticker import Formatter, FuncFormatter


# Datetime ticker
date_ticks = ConciseDateFormatter(AutoDateLocator(maxticks=24))

# Astronomical unit
AU = 149_597_870.7  # km


class UnitFormatter(Formatter):
    """Format numbers with a unit.

    Parameters
    ----------
    unit: str, optional
        A string that will be appended to the label. It may be
        ``None`` or empty to indicate that no unit should be used. LaTeX
        special characters are escaped in ``unit`` whenever latex mode is
        enabled, unless `is_latex` is ``True``.

    sep: str, optional
        Separator used between the value and the unit.
        Default is a ``space`` but it can be remove with empty value.

    scale: float, optional
        Scaling factor (default: ``1``).

    offset: float, optional
        Base offset (default: ``0``).

    fmt: str, optional
        Number formatter (default: ``',g'``).

    """

    def __init__(self, unit='', sep=' ', scale=1, offset=0, fmt=',g'):
        self.unit = unit
        self.sep = sep
        self.scale = scale
        self.offset = offset
        self.fmt = fmt

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}> Unit: `{self.unit}` | '
            f'Sep: `{self.sep}` | Scale: {self.scale} | Offset: {self.offset} | '
            f'Format: `{self.fmt}`'
        )

    def __call__(self, x, pos=None):
        """Format the tick as a number with the appropriate scaling and a unit."""
        s = f'{x * self.scale + self.offset:{self.fmt}}{self.sep}{self.unit}'
        if self.sep and s.endswith(self.sep):
            s = s[: -len(self.sep)]
        return self.fix_minus(s)

    def __add__(self, other):
        """Add offset factor."""
        new_offset = self.offset + other
        return self.__class__(
            unit=self.unit,
            sep=self.sep,
            scale=self.scale,
            offset=new_offset,
            fmt=self.fmt,
        )

    def __radd__(self, other):
        """Add offset factor."""
        return self + other

    def __sub__(self, other):
        """Subtract offset factor."""
        new_offset = self.offset - other
        return self.__class__(
            unit=self.unit,
            sep=self.sep,
            scale=self.scale,
            offset=new_offset,
            fmt=self.fmt,
        )

    def __rsub__(self, other):
        """Subtract offset factor."""
        return -self + other

    def __mul__(self, other):
        """Multiplication scaling factor."""
        new_scale = self.scale * other
        return self.__class__(
            unit=self.unit,
            sep=self.sep,
            scale=new_scale,
            offset=self.offset,
            fmt=self.fmt,
        )

    def __rmul__(self, other):
        """Multiplication scaling factor."""
        return self * other

    def __neg__(self):
        """Negative factor."""
        return self * -1

    def __truediv__(self, other):
        """Divide scaling factor."""
        new_scale = self.scale / other
        return self.__class__(
            unit=self.unit,
            sep=self.sep,
            scale=new_scale,
            offset=self.offset,
            fmt=self.fmt,
        )

    def __matmul__(self, tick):
        """Reverse ticks location."""
        if isinstance(tick, list):
            return [self @ t for t in tick]
        return (tick - self.offset) / self.scale


km_ticks = UnitFormatter('km', fmt=',.10g')
au_ticks = UnitFormatter('AU', scale=1 / AU)  # Input in [km]
km_s_ticks = UnitFormatter('km/s')
m_s_ticks = UnitFormatter('m/s', scale=1_000)  # Input in [km]
deg_ticks = UnitFormatter('°', sep='')
hr_ticks = UnitFormatter('h')
km_pix_ticks = UnitFormatter('km/pix')
m_pix_ticks = UnitFormatter('m/pix', scale=1_000, fmt=',.0f')  # Input in [km/pix]


@FuncFormatter
def lat_ticks(lat, pos=None):
    """Latitude ticks formatter."""
    match lat:
        case 90:
            return 'N.P.'
        case 0:
            return 'Eq.'
        case -90:
            return 'S.P.'
        case _:
            return f'{-lat}°S' if lat < 0 else f'{lat}°N'


@FuncFormatter
def lon_e_ticks(lon_e, pos=None):
    """East longitude ticks formatter."""
    return f'{lon_e % 360}°' + ('' if lon_e % 180 == 0 else 'E')


@FuncFormatter
def lon_w_ticks(lon_w, pos=None):
    """West longitude ticks formatter."""
    return f'{lon_w % 360}°' + ('' if lon_w % 180 == 0 else 'W')


@FuncFormatter
def lon_west_ticks(lon_e, pos=None):
    """West longitude ticks formatter with East longitude input."""
    return lon_w_ticks(-lon_e % 360)
