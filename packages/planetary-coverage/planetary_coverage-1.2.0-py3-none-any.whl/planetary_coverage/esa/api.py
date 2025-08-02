"""ESA API module."""

import json
from shutil import move
from urllib.parse import urlencode
from urllib.request import HTTPError, URLError, urlopen, urlretrieve

from .vars import ESA_MK_CACHE
from ..misc import logger


API = 'https://s2e2.cosmos.esa.int/bitbucket/rest/api/1.0/projects/SPICE_KERNELS/repos'
ESA_API_CACHE = {}

ESA_MK_PREFIXES = {
    'BEPICOLOMBO': 'bc',
    'ENVISION': 'envision',
    'COMET-INTERCEPTOR': 'interceptor',
    'EXOMARS2016': 'em16',
    'EXOMARSRSP': 'emrsp',
    'GAIA': 'gaia',
    'HERA': 'hera',
    'HUYGENS': 'HUYGENS',
    'INTEGRAL': 'integral',
    'JUICE': 'juice',
    'JWST': 'jwst',
    'LUNAR-GATEWAY': 'lg',
    'MARS-EXPRESS': 'MEX',
    'ROSETTA': 'ROS',
    'SMART-1': 'SMART1',
    'SOLAR-ORBITER': 'solo',
    'VENUS-EXPRESS': 'VEX',
}

SKD_LENGTH = len('vXXX_YYYYMMDD_YYY')

log_esa_api, debug_esa_api = logger('ESA API')


class EsaApiNotFoundError(Exception):
    """ESA API not found error message."""


class EsaApiNotAvailableError(Exception):
    """ESA API not available error message."""


def esa_api(uri, **params):
    """Retrieve the tags from ESA Cosmos Bitbucket repo.

    Parameters
    ----------
    uri: str
        Cosmos Bitbucket API entrypoint.
    **params:
        Optional entrypoint parameters.

    Returns
    -------
    list
        List of values return by the ESA API.

    Raises
    ------
    HTTPError
        If the API URL is invalid (usually 404 error code).
    EsaApiNotAvailableError
        If the API response does not contain a ``values`` field.

    Warning
    -------
    The API response must be in JSON and contains a `/children/values`
    or `/values` in its output.

    """

    url = uri + '?' + urlencode(params) if params else uri

    if url in ESA_API_CACHE:
        log_esa_api.debug('Use data from the cache: %s.', url)
        return ESA_API_CACHE[url]

    try:
        log_esa_api.debug('Downloading: %s', url)

        with urlopen(f'{API}/{url}') as resp:  # noqa: S310 (always prefixed with API url)
            data = json.loads(resp.read())

        log_esa_api.debug('Data: %s', data)

    except HTTPError as err:
        raise EsaApiNotFoundError(f'HTTP {err.code} error: `{url}`.') from None

    except URLError:
        raise EsaApiNotAvailableError('ESA server not available') from None

    # Extract the output values
    if 'children' in data:
        data = data['children']

    values = data['values']

    # Recursive search is limit and `nextPageStart` is present
    if 'limit' not in params and 'nextPageStart' in data:
        params['start'] = data['nextPageStart']
        values += esa_api(uri, **params)

    # Cache the response values
    log_esa_api.debug('Saved the values in the cache.')
    ESA_API_CACHE[url] = values

    return values


def get_tag(mission, version='latest', **params):
    """Get tag version(s) of the metakernels from ESA Cosmos repo.

    .. code-block:: text

        https://s2e2.cosmos.esa.int/bitbucket/rest/api/1.0/projects/SPICE_KERNELS/repos/juice/tags

    Parameters
    ----------
    mission: str
        Mission name in the cosmos repo.
    version: str, optional
        Version short key or ``latest`` or ``all`` (default: 'latest').
    **params
        API paging parameters (``limit``/``start``/``filterText``).

    Returns
    -------
    str or list
        Long SKD version key(s).

    Raises
    ------
    AttributeError
        If the mission name provided is invalid.
    ValueError
        If the requested version was not found.

    Note
    ----
    If multiple version have the same short version key, only
    the most recent will be returned. If you want a specific version
    you need to be as precise as possible.

    """
    if not mission:
        raise AttributeError('The mission name must be defined.')

    if version.lower() == 'all':
        log_esa_api.info('Get all the tags for `%s`.', mission)

    elif version.lower() == 'latest':
        log_esa_api.info('Get the latest tag for `%s`.', mission)
        params.update({'limit': 1})

    else:
        log_esa_api.info('Search for the tag closest to `%s` for `%s`.', version, mission)
        params.update({'filterText': version, 'limit': 1, 'orderBy': 'MODIFICATION'})

    try:
        values = esa_api(f'{mission.lower()}/tags', **params)

    except EsaApiNotAvailableError:
        log_esa_api.warning(
            'Impossible to fetch `%s` version online. Use local cache instead.', version
        )
        return get_tag_offline(mission, version)

    tags = [value.get('displayId') for value in values]

    if not tags:
        raise ValueError(f'Version `{version}` is not available.')

    return tags if version.lower() == 'all' else tags[0]


def get_tag_offline(mission, version='latest'):
    """Get tag version(s) of the metakernels available in the local cache.

    Parameters
    ----------
    mission: str
        Mission name in the cosmos repo.
    version: str, optional
        Version short key or ``latest`` or ``all`` (default: 'latest').
    **params
        API paging parameters (``limit``/``start``/``filterText``).

    Returns
    -------
    str or list
        Long SKD version key(s).

    Raises
    ------
    AttributeError
        If the mission name provided is not in the cache.
    ValueError
        If the requested version is not in the cache.

    """
    tags = sorted(tag.name for tag in (ESA_MK_CACHE / mission.lower()).glob('v*'))

    if not tags:
        raise AttributeError(
            f'No version found in the cache for mission `{mission}`.'
        ) from None

    if version.lower() == 'all':
        return tags[::-1]

    if version.lower() == 'latest':
        return tags[-1]

    for tag in tags:
        if tag.startswith(version.lower()):
            return tag

    raise ValueError(f'Version `{version}` not found in the cache.') from None


class EsaMissionMetakernels(dict):
    """ESA mission metakernels.

    The metakernels are sorted by versions.

    The list of the metakernels for a given version
    is only computed when it is requested.

    """

    def __init__(self, mission):
        self.mission = mission

    def __repr__(self):
        n = len(self.versions)

        return '\n - '.join([
            f'<{self.__class__.__name__}> Mission: {self.mission} | {n} versions:',
            *self.versions,
        ])

    def __contains__(self, version):
        return version in self.versions

    def __missing__(self, version):
        if version not in self.versions:
            raise KeyError(version)

        mks = get_mk(self.mission, mk='all', version=version)

        self[version] = mks
        return mks

    @property
    def versions(self) -> list:
        """Available tag versions."""
        return get_tag(self.mission, version='all')


def get_mk(mission, mk='latest', version='latest'):
    """Get metakernel file(s) from ESA Cosmos repo for a given tag.

    .. code-block:: text

        https://s2e2.cosmos.esa.int/bitbucket/rest/api/1.0/projects/SPICE_KERNELS/repos/juice/browse/kernels/mk/?at=refs/tags/v270_20201113_001
        https://s2e2.cosmos.esa.int/bitbucket/rest/api/1.0/projects/SPICE_KERNELS/repos/juice/raw/kernels/mk/juice_crema_3_0.tm?at=refs/tags/v270_20201113_001

    Parameters
    ----------
    mission: str
        Mission name in the cosmos repo.
    mk: str, optional
        Metakernel name/shortcut to download.
        If `latest` is provided (default), the lastest metakernel will be selected.
        If `all` is provided, the function will search all the available metakernel(s)
        for the provided tag.
    version: str, optional
        Tagged version `latest` (default) or `all`.
        If the version provided is not fully defined, the API will be query
        to search for the closest version.
        If `all` is provided, the function will list all the available metakernel(s)
        for all the tags.

    Returns
    -------
    str, list or EsaMissionMetakernels
        Metakernel file name.

    Raises
    ------
    AttributeError
        If the mission name provided is invalid.
    ValueError
        If not metakernel was found for the requested arguments.
    FileNotFoundError
        If the file is not found on the cosmos repo.

    """
    if not mission:
        raise AttributeError('The mission name must be defined.')

    # Get one or all the metakernel(s) for all the available versions
    if version.lower() == 'all':
        return EsaMissionMetakernels(mission)

    # Check if the version provided is a valid tag
    tag = get_tag(mission, version=version) if len(version) != SKD_LENGTH else version

    # Get all the metakernel for a given version
    if str(mk).lower() in {'latest', 'all'}:
        log_esa_api.info('Get all the metakernel at `%s`.', tag)
        try:
            values = esa_api(
                f'{mission.lower()}/browse/kernels/mk/', at=f'refs/tags/{tag}'
            )

        except EsaApiNotAvailableError:
            return get_mk_offline(mission, mk=mk, version=version)

        mks = [
            mk_file
            for value in values
            for mk_file in value['path']['components']
            if mk_file.lower().endswith('.tm')
        ]

        if str(mk).lower() == 'all':
            return mks

        # Select only the latest metakernel for the selected tag.
        mk = mks[-1]

    # Get a single metakernel
    if not str(mk).lower().endswith('.tm'):
        mk = esa_mk_name(mission, mk)

    return _mk_fname(mission, tag, mk)


def _mk_fname(mission, tag, mk):
    """Get metakernel filename and download it if missing."""
    fname = ESA_MK_CACHE / mission.lower() / tag / str(mk)

    if not fname.exists():
        log_esa_api.info('Get %s at `%s`.', mk, tag)

        url = f'{API}/{mission.lower()}/raw/kernels/mk/{mk}?at=refs/tags/{tag}'

        try:
            log_esa_api.debug('Download mk at: %s.', url)
            fout, _ = urlretrieve(url)  # noqa: S310 (always prefixed with API url)

        except HTTPError:
            raise FileNotFoundError(f'`{mk}` at `{tag}` does not exist.') from None

        except URLError:
            log_esa_api.warning(
                'Impossible to fetch `%s` metakernel at `%s` version online. '
                'Use local cache instead.',
                mk,
                tag,
            )
            return get_mk_offline(mission=mission, mk=mk, version=tag)

        fname.parent.mkdir(parents=True, exist_ok=True)
        move(fout, fname)

    return fname


def get_mk_offline(mission, mk='latest', version='latest'):
    """Get metakernel file(s) for a given tag in the local cache.

    Parameters
    ----------
    mission: str
        Mission name in the cosmos repo.
    mk: str, optional
        Metakernel name/shortcut to download.
        If `latest` is provided (default), the lastest metakernel will be selected.
        If `all` is provided, the function will search all the available metakernel(s)
        for the provided tag.
    version: str, optional
        Tagged version `latest` (default) or `all`.
        If the version provided is not fully defined, the API will be query
        to search for the closest version.
        If `all` is provided, the function will list all the available metakernel(s)
        for all the tags.

    Returns
    -------
    str, list or dict
        Metakernel file(s) name.

    Raises
    ------
    AttributeError
        If the mission and version provided are not in the cache.
    FileNotFoundError
        If the file is not found in the cache.

    """
    if version.lower() == 'all':
        return {
            tag: get_mk_offline(mission, mk=mk, version=tag)
            for tag in get_tag_offline(mission, version='all')
        }

    tag = get_tag_offline(mission, version=version)

    mks = sorted(mk for mk in (ESA_MK_CACHE / mission.lower() / tag).glob('*.tm'))

    if not mks:
        raise AttributeError(
            f'No metakernel found locally for mission `{mission}` at version `{version}`.'
        ) from None

    if str(mk).lower() == 'all':
        return mks[::-1]

    if str(mk).lower() == 'latest':
        return mks[-1]

    # Check if the mk name is in the mks list
    mks = [metakernel for metakernel in mks[::-1] if str(mk).lower() in metakernel.name]

    if not mks:
        raise FileNotFoundError(
            f'`{mk}` metakernel at `{version}` is not in the cache.'
        ) from None

    return mks if len(mks) > 1 else mks[0]


def esa_mk_name(mission, ref):
    """ESA metakernel name shortcuts.

    Parameters
    ----------
    mission: str
        ESA mission name.
    ref: str
        Mission metakernel reference. This could be a MK_IDENTIFIER
        (implicit versioned metakernel filename without ``.tm``),
        a shortcut name (without the mission name prefix) or a
        crema pattern (if it starts with a digit, see ``crema_ref()`` for details).

    Returns
    -------
    str
        Formatted mission metakernel filename.


    """
    mission_name = ESA_MK_PREFIXES.get(mission.upper(), None)

    if not mission_name:
        raise ValueError(
            f'SPICE metakernel not found for mission {mission} on ESA SPICE repository.'
        )

    if str(ref)[0].isdigit():
        mk = f'{mission_name}_crema_{crema_ref(ref)}.tm'
    elif str(ref).lower().startswith(mission_name.lower()):
        mk = f'{ref}.tm'
    else:
        mk = f'{mission_name}_{ref}.tm'

    return mk.upper() if mission_name.isupper() else mk


def crema_ref(ref):
    """Get CReMA ref formatter."""
    crema = str(ref)

    # Replace with underscores
    for c in '.- ':
        crema = crema.replace(c, '_')

    # Special cases
    return crema.replace('(', '').replace('_only)', '')  # `(cruise only)` -> `cruise`
