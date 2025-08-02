"""SPICE light time aberration correction module."""

import numpy as np


C_LIGHT = 299_792.458  # Light speed in the vacuum (km/s)


class SpiceAbCorr(str):
    """SPICE light time aberration correction checker.

    Parameters
    ----------
    abcorr: str, optional
        SPICE Aberration correction flag (default: ``'NONE'``).
    restrict: tuple or list, optional
        List of the valid values.

    Returns
    -------
    str
        Valid SPICE Aberration Correction string.

    Raises
    ------
    KeyError
        If the provided key is invalid.

    See Also
    --------
    `SPICE aberration corrections
    <https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/abcorr.html>`_
    required reading.

    """

    DEFAULTS = [
        'NONE',
        'LT',
        'LT+S',
        'CN',
        'CN+S',
        'XLT',
        'XLT+S',
        'XCN',
        'XCN+S',
    ]

    def __new__(cls, abcorr='NONE', restrict=None):
        if not abcorr:
            abcorr = 'NONE'

        abcorr = str(abcorr).upper()

        if not restrict:
            restrict = cls.DEFAULTS

        if abcorr not in restrict:
            raise KeyError(
                f'Invalid abcorr: `{abcorr}`. Available: ' + '|'.join(restrict)
            )

        return str.__new__(cls, abcorr)

    def __call__(self, ets, dist):
        return self.dist_corr(ets, dist)

    @property
    def reception(self):
        """Transmission case."""
        return self.startswith('L') or self.startswith('C')

    @property
    def transmission(self):
        """Transmission case."""
        return self.startswith('X')

    @property
    def stellar(self):
        """Stellar aberration."""
        return self.endswith('+S')

    @property
    def oneway(self):
        """One-way light time correction / planetary aberration."""
        return self.startswith('LT') or self.startswith('XLT')

    @property
    def converged(self):
        """Converged Newtonian correction."""
        return self.startswith('CN') or self.startswith('XCN')

    def lt_corr(self, ets, lt):
        """Apply light time correction.

        Parameters
        ----------
        ets: float or [float, …]
            Input Ephemeris Time(s).
        lt: float or [float, …]
            Light time correction to apply if the aberration is not ``NONE``.

        Return
        ------
        float or [float, …]
            Corrected Ephemeris Time(s).

        """
        s = 0 if self == 'NONE' else -1 if self.reception else 1
        return np.add(ets, np.multiply(s, lt))

    def dist_corr(self, ets, dist):
        """Compute light time correction from source distance.

        Parameters
        ----------
        ets: float or [float, …]
            Input ephemeris time(s).
        lt: float or [float, …]
            Source distance (km).

        Return
        ------
        float or [float, …]
            Light time corrected values.

        """
        lt = np.divide(dist, C_LIGHT)
        return self.lt_corr(ets, lt)
