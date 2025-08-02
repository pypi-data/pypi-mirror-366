"""SPICE reference module."""

import re

import numpy as np

import spiceypy as sp

from .fov import SpiceFieldOfView
from .kernel import get_item
from .times import sclk
from ..misc import cached_property


# Spice frame classes
FRAME_CLASS_TYPES = {
    1: 'Inertial frame',
    2: 'PCK body-fixed frame',
    3: 'CK frame',
    4: 'Fixed offset frame',
    5: 'Dynamic frame',
    6: 'Switch frame',
}


class SpiceRefRegex:
    r"""SPICE regular expression for references.

    Tip
    ---
    To check the pattern you need to use the ``in``
    keyword:

    >>> 399 in SpiceRefRegex(r'[1-9]99')
    True

    Warning
    -------
    The match is only performed on the whole pattern,
    and the regular expression pattern is always prefixed
    with ``^`` and suffixed by ``$`` internally (if not
    already present).

    Note
    ----
    SpiceRefRegex patterns can be concatenated with the
    *OR* operator (``|``):

    >>> INNER_MOONS = SpiceRefRegex(r'301|401|402')
    >>> OUTER_MOONS = SpiceRefRegex(r'[5-9](?!00|99)\d{2}')
    >>> 501 in INNER_MOONS | OUTER_MOONS
    True

    """

    def __init__(self, re_exp):
        if not re_exp.startswith('^'):
            re_exp = rf'^{re_exp}'

        if not re_exp.endswith('$'):
            re_exp = rf'{re_exp}$'

        self.re_exp = re_exp

    def __str__(self):
        return self.re_exp

    def __contains__(self, ref):
        """Match SPICE code to a regular expression"""
        return bool(re.match(self.re_exp, str(int(ref))))

    def __or__(self, other):
        if isinstance(other, type(self)):
            return self.__class__(f'{self}|{other}')
        raise NotImplementedError


# Spice body code regular expressions
RE_SUN = SpiceRefRegex('10')
# Planets: 3 digits ending with 99
RE_PLANETS = SpiceRefRegex(r'[1-9]99')
# Satellites: Inner moons in solar system: Moon (301) / Phobos (401) / Deimos (402)
RE_INNER_MOONS = SpiceRefRegex(r'301|401|402')
# Satellites: Outer moons in solar system (501-598, 601-698, …)
RE_OUTER_MOONS = SpiceRefRegex(r'[5-9](?!00|99)\d{2}')
# Comets: 1,000,000 + JPL's Solar System Dynamics Group number
RE_COMETS = SpiceRefRegex(r'1(?!0{6})\d{6}')
# Comet fragments (from Shoemaker Levy-9): 50,000,001 to 50,000,023
RE_COMET_FRAGMENTS = SpiceRefRegex(r'50{5}(0[1-9]|1\d|2[0-3])')
# Asteroids original schema (permanently and provisional numbered)
RE_ASTEROIDS_ORIGINAL_SCHEMA = SpiceRefRegex(r'[2-3](?!0{6})\d{6}')
# Asteroids extended schema (permanently and provisional numbered)
RE_ASTEROIDS_EXTENDED_SCHEMA = SpiceRefRegex(r'(?![25]0{7})[2-9]\d{7}')
# Asteroid systems with two or more bodies (9-digits) primary body with 9 prefix
RE_ASTEROID_PRIMARIES = SpiceRefRegex(r'9(?![25]0{7})[2-9]\d{7}')
# Asteroid systems with two or more bodies (9-digits) excluding primary body with 9 prefix
RE_ASTEROID_SECONDARIES = SpiceRefRegex(r'[1-8](?![25]0{7})[2-9]\d{7}')
# Asteroid exceptions (Gaspra)
RE_ASTEROID_EXCEPTIONS = SpiceRefRegex('9511010')

# Spice DSN spacecraft (-1 to -999)
RE_SC_DSN = SpiceRefRegex(r'-(?!0{1,3})\d{1,3}')
# Spice NORAD spacecraft (-100,001 to -119,999)
RE_SC_NORAD = SpiceRefRegex(r'-1(?!0{5})[01]\d{4}')

# Spice instrument
CODE_INST_MAX = -1_000
CODE_INST_MIN = -1_000_000


def spice_name_code(ref):
    """Get name and code from a reference.

    Parameters
    ----------
    ref: str or int
        Reference name or code id.

    Returns
    -------
    str, int
        Reference name and code id.

    Raises
    ------
    ValueError
        If this reference is not known in the kernel pool.

    """
    try:
        code = sp.bods2c(str(ref).upper())
        name = sp.bodc2n(code)

    except sp.stypes.NotFoundError:
        if re.match(r'-?\d+', str(ref)):
            code, name = int(ref), sp.frmnam(int(ref))
        else:
            code, name = sp.namfrm(ref), str(ref)

        if code == 0 or not name:
            raise ValueError(f'Unknown reference: `{ref}`') from None

    return str(name), int(code)


class AbstractSpiceRef:
    """SPICE reference helper.

    Parameters
    ----------
    ref: str or int
        Reference name or code id.

    Raises
    ------
    KeyError
        If this reference is not known in the kernel pool.

    """

    def __init__(self, ref):
        self.name, self.id = spice_name_code(ref)

        if not self.is_valid():
            raise KeyError(f'{self.__class__.__name__} invalid id: `{int(self)}`')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<{self.__class__.__name__}> {self} ({int(self):_})'

    def __int__(self):
        return self.id

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == other or int(self) == other

    def __getitem__(self, item):
        return get_item(item)

    @property
    def code(self):
        """SPICE reference ID as string."""
        return str(self.id)

    def encode(self, encoding='utf-8'):
        """Reference name encoded."""
        return str(self).encode(encoding=encoding)

    def is_valid(self):
        """Generic SPICE reference.

        Returns
        -------
        bool
            Generic SPICE reference should always ``True``.

        """
        return isinstance(int(self), int)

    @cached_property
    def frame(self):
        """Reference frame."""
        if hasattr(self, '_frame'):
            return SpiceFrame(self._frame)

        try:
            return SpiceFrame(sp.cidfrm(int(self))[1])
        except sp.stypes.NotFoundError:
            return SpiceFrame(get_item(f'FRAME_{int(self)}_NAME'))


class SpiceFrame(AbstractSpiceRef):
    """SPICE reference frame.

    Parameters
    ----------
    name: str or int
        Reference frame name or code id.

    """

    def is_valid(self):
        """Check if the code is a frame code."""
        return bool(sp.namfrm(str(self)))

    @property
    def class_type(self):
        """Frame class type."""
        _, _class, _ = sp.frinfo(int(self))
        return FRAME_CLASS_TYPES[_class]

    @property
    def center(self):
        """Frame center reference."""
        return SpiceRef(int(get_item(f'FRAME_{int(self)}_CENTER')))

    @property
    def sclk(self):
        """Frame SCLK reference."""
        return SpiceRef(int(get_item(f'CK_{int(self)}_SCLK')))

    @property
    def spk(self):
        """Frame SPK reference."""
        return SpiceRef(int(get_item(f'CK_{int(self)}_SPK')))

    @cached_property
    def frame(self):
        """Reference frame.

        Not implemented for a :class:`SpiceFrame`.

        """
        raise NotImplementedError


class SpiceBody(AbstractSpiceRef):
    """SPICE body reference.

    It can be either:

    - Sun
    - Planet
    - Satellite
    - Comet (including fragments)
    - Asteroid (permanently or provisional numbered)

    Parameters
    ----------
    name: str or int
        Body name or code id.

    """

    def __getitem__(self, item):
        return get_item(f'BODY{int(self)}_{item.upper()}')

    def is_valid(self):
        """Check if the code is valid for a SPICE body.

        Refer to the `NAIF Integer ID codes
        <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/req/naif_ids.html>`_
        in section `Planets and Satellites`/`Comets`/`Asteroids` for more details.

        - Sun: ``10``
        - Planets: ``N99``
        - Satellites: ``NMM`` with ``MM`` not ``00`` or ``99`` (*)

        (*): No satellites for Mercury nor Venus, only the Moon (``301``) for the Earth
        and Phobos (``401``) and Deimos (``402``) for Mars.

        - Commets: ``1,000,000 + JPL's Solar System Dynamics Group number``

        - Asteroid original schema (7-digits):

            - Permanently numbered: ``2,000,000 + Permanent Asteroid Number``
              (2,000,001 to 2,999,999)
            - Provisional numbered: ``3,000,000 + Provisional Asteroid Number``
              (3,000,001 to 3,999,999)

        - Asteroid extended schema (8 or 9-digits):

            - Permanently numbered: ``20,000,000 + Permanent Asteroid Number``
              (20,000,001 to 49,999,999)
            - Provisional numbered: ``50,000,000 + Provisional Asteroid Number``
              (20,000,001 to 49,999,999)

        Warning
        -------
        For asteroid systems with two or more bodies the 8-digit NAIF ID code
        represents the barycenter. Individual satellites have a prepended
        number ``1`` through ``8``, while the primary body uses the *last available*
        prefix ``9``, resulting in 9-digit NAIF ID codes.
        For example, asteroids Didymos (``65,803``) and its satellite Dimorphos
        can be accommodated only using the extended schema with IDs ``920,065,803``
        and ``120,065,803``, and Didymos system barycenter with ID ``20,065,803``.

        Note
        ----
        Asteroid barycenter will not be considered as ``SpiceBody`` but
        as a regular ``SpiceRef``.

        Returns
        -------
        bool
            Valid body ids are listed above.

        """
        if 'BARYCENTER' in str(self):
            return False

        return (
            self
            in RE_SUN
            | RE_PLANETS
            | RE_INNER_MOONS
            | RE_OUTER_MOONS
            | RE_COMETS
            | RE_COMET_FRAGMENTS
            | RE_ASTEROIDS_ORIGINAL_SCHEMA
            | RE_ASTEROIDS_EXTENDED_SCHEMA
            | RE_ASTEROID_PRIMARIES
            | RE_ASTEROID_SECONDARIES
            | RE_ASTEROID_EXCEPTIONS
        )

    @property
    def is_planet(self):
        """Check if the body is a planet."""
        return self in RE_PLANETS

    @property
    def is_satellite(self):
        """Check if the body is a planet, asteroid or commet's satellite."""
        return (
            self
            in RE_INNER_MOONS
            | RE_OUTER_MOONS
            | RE_COMET_FRAGMENTS
            | RE_ASTEROID_SECONDARIES
        )

    @property
    def is_comet(self):
        """Check if the body is a comet."""
        return self in RE_COMETS | RE_COMET_FRAGMENTS

    @property
    def is_asteroid(self):
        """Check if the body is an asteroid."""
        return (self not in RE_COMET_FRAGMENTS) and (
            self
            in RE_ASTEROIDS_ORIGINAL_SCHEMA
            | RE_ASTEROIDS_EXTENDED_SCHEMA
            | RE_ASTEROID_PRIMARIES
            | RE_ASTEROID_SECONDARIES
            | RE_ASTEROID_EXCEPTIONS
        )

    @cached_property
    def parent(self):
        """Parent body."""
        if self in RE_INNER_MOONS | RE_OUTER_MOONS:
            parent = f'{self.code[0]}99'
        elif self in RE_COMET_FRAGMENTS:
            parent = 'JUPITER'
        elif self in RE_ASTEROID_SECONDARIES:
            parent = f'9{self.code[1:]}'
        else:
            parent = 'SUN'

        return SpiceBody(parent)

    @cached_property
    def barycenter(self):
        """Body barycenter."""
        if self in RE_SUN | RE_PLANETS:
            return SpiceRef(int(self) // 100)
        if self in RE_ASTEROID_PRIMARIES:
            return SpiceRef(f'{self.code[1:]}')

        return self.parent.barycenter

    @cached_property
    def radii(self):
        """Body radii, if available (km)."""
        return self['RADII']

    @property
    def radius(self):
        """Body mean radius, if available (km)."""
        return np.cbrt(np.prod(self.radii))

    @property
    def r(self):
        """Body mean radius alias."""
        return self.radius

    @property
    def re(self):
        """Body equatorial radius, if available (km)."""
        return self.radii[0]

    @property
    def rp(self):
        """Body polar radius, if available (km)."""
        return self.radii[2]

    @property
    def f(self):
        """Body flattening coefficient, if available (km)."""
        re, _, rp = self.radii
        return (re - rp) / re

    @cached_property
    def mu(self):
        """Gravitational parameter (GM, km³/sec²)."""
        return self['GM']


class SpiceObserver(AbstractSpiceRef):
    """SPICE observer reference.

    Parameters
    ----------
    ref: str or int
        Reference name or code id.

    Raises
    ------
    KeyError
        If the provided key is neither spacecraft nor an instrument.

    """

    def __init__(self, ref):
        super().__init__(ref)

        # Spacecraft object promotion
        if SpiceSpacecraft.is_valid(self):
            self.__class__ = SpiceSpacecraft

        # Instrument object promotion
        elif SpiceInstrument.is_valid(self):
            self.__class__ = SpiceInstrument

        else:
            raise KeyError('A SPICE observer must be a valid Spacecraft or Instrument')


class SpiceSpacecraft(SpiceObserver):
    """SPICE spacecraft reference.

    Parameters
    ----------
    name: str or int
        Spacecraft name or code id.

    """

    BORESIGHT = [0, 0, 1]

    def is_valid(self):
        """Check if the code is valid for a SPICE spacecraft.

        Refer to the `NAIF Integer ID codes
        <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/req/naif_ids.html>`_
        in sections `Spacecraft` and `Earth Orbiting Spacecraft` for more details.

        - Interplanetary spacecraft is normally the negative of the code assigned
          to the same spacecraft by JPL's Deep Space Network (DSN) as determined
          the NASA control authority at Goddard Space Flight Center.

        - Earth orbiting spacecraft are defined as: ``-100000 - NORAD ID code``

        Returns
        -------
        bool
            Valid spacecraft ids are between -999 and -1 and between
            -119,999 and -100,001.

        """
        return self in RE_SC_DSN | RE_SC_NORAD

    @cached_property
    def instruments(self):
        """SPICE instruments in the pool associated with the spacecraft."""
        keys = sp.gnpool(f'INS{int(self)}*_FOV_FRAME', 0, 1_000)

        codes = sorted([int(key[3:-10]) for key in keys], reverse=True)

        return list(map(SpiceInstrument, codes))

    def instr(self, name):
        """SPICE instrument from the spacecraft."""
        try:
            return SpiceInstrument(f'{self}_{name}')
        except ValueError:
            return SpiceInstrument(name)

    @property
    def spacecraft(self):
        """Spacecraft SPICE reference."""
        return self

    def sclk(self, *time):
        """Continuous encoded spacecraft clock ticks.

        Parameters
        ----------
        *time: float or str
            Ephemeris time (ET)  or UTC time inputs.

        """
        return sclk(int(self), *time)

    @cached_property
    def frame(self):
        """Spacecraft frame (if available)."""
        try:
            return super().frame
        except (ValueError, KeyError):
            return SpiceFrame(self[f'FRAME_{int(self) * 1_000}_NAME'])

    @property
    def boresight(self):
        """Spacecraft z-axis boresight.

        For an orbiting spacecraft, the Z-axis points from the
        spacecraft to the closest point on the target body.

        The component of inertially referenced spacecraft velocity
        vector orthogonal to Z is aligned with the -X axis.

        The Y axis is the cross product of the Z axis and the X axis.

        You can change the :attr:`SpiceSpacecraft.BORESIGHT` value manually.

        """
        return np.array(self.BORESIGHT)


class SpiceInstrument(SpiceObserver, SpiceFieldOfView):
    """SPICE instrument reference.

    Parameters
    ----------
    name: str or int
        Instrument name or code id.

    """

    def __getitem__(self, item):
        return get_item(f'INS{int(self)}_{item.upper()}')

    def is_valid(self):
        """Check if the code is valid for a SPICE instrument.

        Refer to the `NAIF Integer ID codes
        <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/FORTRAN/req/naif_ids.html>`_
        in section `Instruments` for more details.

        .. code-block:: text

            NAIF instrument code = (s/c code)*(1000) - instrument number

        This allows for 1000 instrument assignments on board a spacecraft.

        Danger
        ------
        Based on the SPICE documentation, and instrument should have a NAIF code
        between  -1,000,000. For some mission (Juice, EnVision), this rule is not
        enforced because some instrument requires more ids. For examples:

        - ``juice_pep_v15.ti`` has ``JUICE_PEP_JDC_PIXEL_000 (ID: -2_851_000)``
        - ``envision_vensar_v00.ti`` has ``ENVISION_VENSAR_SAR_20_220 (ID: -668_110_001)``

        Returns
        -------
        bool
            Valid instrument ids are below -1,000 and have a valid
            field of view definition.

        """
        if (
            int(self) >= CODE_INST_MAX
        ):  # MIN value (-1,000,000) is not enforced (see above)
            return False

        try:
            # Check if the FOV is valid and init the value if not an `int`.
            if isinstance(self, int):
                _ = SpiceFieldOfView(self)
            else:
                SpiceFieldOfView.__init__(self, int(self))  # noqa: PLC2801 (init on self)

            return True
        except ValueError:
            return False

    @cached_property
    def spacecraft(self):
        """Parent spacecraft.

        Warning
        -------
        Some mission don't enforce NAIF rule on instrument id definition.
        Therefore, the preferred method to guess the parent of the spacecraft
        name is to extract the first part of the instrument name.
        If this method fails, the instrument id is divided by 1,000 to get
        the space id.

        Raises
        ------
        ValueError
            If the SpiceSpacecraft is not found.

        """
        try:
            return SpiceSpacecraft(str(self).split('_', 1)[0])
        except ValueError:
            return SpiceSpacecraft(-(-int(self) // 1_000))

    def sclk(self, *time):
        """Continuous encoded parent spacecraft clock ticks.

        Parameters
        ----------
        *time: float or str
            Ephemeris time (ET)  or UTC time inputs.

        """
        return sclk(int(self.spacecraft), *time)

    @property
    def ns(self):
        """Instrument number of samples."""
        try:
            return int(self['PIXEL_SAMPLES'])
        except KeyError:
            return 1

    @property
    def nl(self):
        """Instrument number of lines."""
        try:
            return int(self['PIXEL_LINES'])
        except KeyError:
            return 1

    def _rad_fov(self, key):
        """Get FOV angle value in radians"""
        angle = self[f'FOV_{key}']

        return angle if self['FOV_ANGLE_UNITS'] == 'RADIANS' else np.radians(angle)

    @property
    def fov_along_track(self):
        """Instrument field of view along-track angle (radians)."""
        if self.shape == 'POLYGON':
            return np.nan

        return 2 * self._rad_fov('REF_ANGLE')

    @property
    def fov_cross_track(self):
        """Instrument field of view cross-track angle (radians)."""
        if self.shape in {'CIRCLE', 'POLYGON'}:
            return self.fov_along_track

        return 2 * self._rad_fov('CROSS_ANGLE')

    @property
    def ifov(self):
        """Instrument instantaneous field of view angle (radians).

        Danger
        ------
        This calculation expect that the sample direction is
        aligned with the cross-track direction (ie. 1-line acquisition
        in push-broom mode should be in the direction of flight).

        Warning
        -------
        ``JUICE_JANUS`` instrument in ``v06`` does not follow this convention.
        We manually manage this exception for the moment.
        See `MR !27
        <https://gitlab.esa.int/juice-soc-public/python/planetary-coverage/-/merge_requests/27>`_
        for more details.

        """
        if self != 'JUICE_JANUS':
            along_track = self.fov_along_track / self.nl
            cross_track = self.fov_cross_track / self.ns
        else:
            along_track = self.fov_along_track / self.ns
            cross_track = self.fov_cross_track / self.nl

        return along_track, cross_track

    @property
    def ifov_along_track(self):
        """Instrument instantaneous along-track field of view angle (radians)."""
        return self.ifov[0]

    @property
    def ifov_cross_track(self):
        """Instrument instantaneous cross-track field of view angle (radians)."""
        return self.ifov[1]


class SpiceRef(AbstractSpiceRef):
    """SPICE reference generic helper.

    Parameters
    ----------
    ref: str or int
        Reference name or code id.

    """

    def __init__(self, ref):
        super().__init__(ref)

        # Body object promotion
        if SpiceBody.is_valid(self):
            self.__class__ = SpiceBody

        # Spacecraft object promotion
        elif SpiceSpacecraft.is_valid(self):
            self.__class__ = SpiceSpacecraft

        # Instrument object promotion
        elif SpiceInstrument.is_valid(self):
            self.__class__ = SpiceInstrument

        # Frame object promotion
        elif SpiceFrame.is_valid(self):
            self.__class__ = SpiceFrame

    @property
    def spacecraft(self):
        """Spacecraft SPICE reference.

        Not implemented for a :class:`SpiceRef`.

        """
        raise NotImplementedError

    def sclk(self, *time):
        """Continuous encoded parent spacecraft clock ticks.

        Not implemented for a :class:`SpiceRef`.

        """
        raise NotImplementedError
