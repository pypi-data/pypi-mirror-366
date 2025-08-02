"""ESA metakernel module."""

import re
from collections import UserDict

from .api import get_mk, get_tag
from ..misc import cached_property


TWO_ELEMENTS = 2
THREE_ELEMENTS = 3


class EsaMetakernels:
    """ESA mission metakernels.

    Parameters
    ----------
    mission: str
        Name of the mission.
    doi: str, optional
        DOI of the dataset.
    sc_alias: str

    """

    def __init__(self, mission, doi=None, alias=None):
        self.mission = mission
        self.doi = doi
        self.alias = (
            alias if isinstance(alias, (list, tuple)) else [alias] if alias else []
        )

    def __str__(self):
        return ' / '.join([self.mission] + list(self.alias))

    def __repr__(self):
        s = f'<{self.__class__.__name__}> mission: {self} '

        if self.doi:
            s += f'(doi:{self.doi}) '

        s += f'| latest version: {self.latest} | '

        n = len(self)
        if n == 0:
            s += 'No metakernel is available.'
        else:
            s += '\n - '.join([f'{n} metakernel{"s" if n > 1 else ""}:', *self.mks])
        return s

    def __len__(self):
        return len(self.mks)

    def __iter__(self):
        return iter(self.mks)

    def __contains__(self, other):
        return other in self.mks

    def __getitem__(self, item):
        """Get a single metakernel for the latest or a specific version."""
        version = None

        if isinstance(item, tuple) and len(item) == TWO_ELEMENTS:
            mk, version = item
        elif isinstance(item, (int, float, str)):
            mk = item
        else:
            raise KeyError(
                'You need to provide a `mk` key (with an optional `version` key).'
            )

        # SKD VERSION suffix pattern
        if match := re.findall(r'(.*)_([vV]\d{3}_\d{8}_\d{3})(?:\.(?:tm|TM))?$', str(mk)):
            mk, version = match[0]

        # Use 'latest' version if not provided
        if version is None:
            version = self.latest

        return get_mk(self.mission, mk=str(mk), version=version.lower())

    @cached_property
    def latest(self) -> str:
        """Latest version."""
        return get_tag(self.mission, version='latest')

    @property
    def versions(self) -> list:
        """Get all the releases available for a given mission."""
        return get_tag(self.mission, version='all')

    def version(self, version) -> list:
        """List of all the metakernels for a given version."""
        return get_mk(self.mission, mk='all', version=version)[::-1]

    @cached_property
    def mks(self) -> list:
        """List of all the latest metakernels."""
        return self.version(self.latest)


class EsaMetakernelsCollection(UserDict):
    """ESA metakernels collection."""

    def __init__(self, *esa_kernels):
        self.data = {esa_kernel.mission: esa_kernel for esa_kernel in esa_kernels}

        self.aliases = {
            alias: esa_kernel.mission
            for esa_kernel in esa_kernels
            for alias in esa_kernel.alias
        }

    def __repr__(self):
        n = len(self.data)
        return '\n - '.join([
            f'<{self.__class__.__name__}> {n} mission{"s" if n > 1 else ""}:',
            *map(str, self.values()),
        ])

    def __contains__(self, mission):
        m = str(mission).upper()
        return m in self.data or m in self.aliases

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if len(item) == TWO_ELEMENTS:
                return self[item[0]][item[1]]
            if len(item) == THREE_ELEMENTS:
                return self[item[0]][item[1], item[2]]
            raise KeyError(item)

        mission = str(item).upper()
        if mission in self.data:
            return self.data[mission]

        if mission in self.aliases:
            return self.data[self.aliases[mission]]

        raise KeyError(item)


# ESA missions metakernels
ESA_MK = EsaMetakernelsCollection(
    EsaMetakernels(
        'BEPICOLOMBO',
        doi='10.5270/esa-dwuc9bs',
        alias=(
            'MPO',
            'BEPICOLOMBO MPO',
            'MERCURY PLANETARY ORBITER',
            'MTM',
            'BEPICOLOMBO MTM',
            'MERCURY TRANSFER MODULE',
            'MMO',
            'BEPICOLOMBO MMO',
            'MERCURY MAGNETOSPHERIC ORBITER',
        ),
    ),
    EsaMetakernels('ENVISION'),
    EsaMetakernels('COMET-INTERCEPTOR'),
    EsaMetakernels(
        'EXOMARS2016',
        doi='10.5270/esa-pwviqkg',
        alias=(
            'TGO',
            'EXOMARS 2016 TGO',
            'TRACE GAS ORBITER',
            'EDM',
            'EXOMARS 2016 EDM',
            'EDL DEMONSTRATOR MODULE',
        ),
    ),
    EsaMetakernels(
        'EXOMARSRSP',
        doi='10.5270/esa-uvyv4w5',
        alias=(
            'RM',
            'EXM RSP RM',
            'EXM ROVER',
            'EXOMARS ROVER',
            'SP',
            'EXM RSP SP',
            'EXM SURFACE PLATFORM',
            'EXOMARS SP',
            'CM',
            'EXM RSP SCC',
            'EXM SPACECRAFT COMPOSITE',
            'EXOMARS SCC',
        ),
    ),
    EsaMetakernels('GAIA'),
    EsaMetakernels('HERA'),
    EsaMetakernels(
        'HUYGENS',
        doi='10.5270/esa-ssem3np',
        alias=(
            'CASP',
            'CASSINI PROBE',
            'HUYGENS PROBE',
        ),
    ),
    EsaMetakernels('INTEGRAL', doi='10.5270/esa-p54lhqn'),
    EsaMetakernels('JUICE', doi='10.5270/esa-ybmj68p'),
    EsaMetakernels('JWST'),
    # EsaMetakernels('LUNAR-GATEWAY'),  # no SKD tag in the repo
    EsaMetakernels(
        'MARS-EXPRESS',
        doi='10.5270/esa-trn5vp1',
        alias=(
            'MEX',
            'MARS EXPRESS',
            'BEAGLE2',
            'BEAGLE 2',
            'BEAGLE-2',
        ),
    ),
    EsaMetakernels('ROSETTA', doi='10.5270/esa-tyidsbu', alias=('PHILAE',)),
    EsaMetakernels(
        'SMART-1',
        doi='10.5270/esa-um8r1n0',
        alias=(
            'S1',
            'SM1',
            'SMART1',
        ),
    ),
    EsaMetakernels(
        'SOLAR-ORBITER',
        doi='10.5270/esa-kt1577e',
        alias=(
            'SOLO',
            'SOLAR ORBITER',
        ),
    ),
    EsaMetakernels(
        'VENUS-EXPRESS',
        doi='10.5270/esa-h3zbs8s',
        alias=(
            'VEX',
            'VENUS EXPRESS',
        ),
    ),
)
