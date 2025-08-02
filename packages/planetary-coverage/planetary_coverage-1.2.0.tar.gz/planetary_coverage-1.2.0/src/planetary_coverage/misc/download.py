"""Generic web download method."""

import certifi
import ssl
from pathlib import Path
from urllib.request import urlopen

from .logger import logger


log_download, debug_download = logger('Download', info_stdout=True)

# Fix CERTIFICATE_VERIFY_FAILED error in python 3.13 (https://stackoverflow.com/q/79123649)
CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
CONTEXT.load_verify_locations(cafile=certifi.where())


def wget(url, fout, skip=False, force=False):
    """Web download.

    Parameters
    ----------
    url: str
        URL to download
    fout: str or pathlib.Path
        Output file.
    skip: bool, optional
        Skip download if the output file already exists (default: `False`).
        Has the priority over :py:attr:`force`.
    force: bool, optional
        Force download even if the file exists (default: `False`).

    Returns
    -------
    pathlib.Path
        Downloaded file path.

    Raises
    ------
    ValueError
        If the URL provided is not starting with `http[s]://`.
    FileExistsError
        If the file already exists and `force` is `False` (default).

    Note
    ----
    The missing sub-directories will be created.

    By default, logging is set at INFO level.
    Use :py:func:`debug_download` function to
    increase or disable the logging output.

    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError(f'URL must start with `http[s]://` not `{url}`')

    fname = Path(fout)

    if fname.exists() and skip:
        return fname

    if not fname.exists() or force:
        # Create sub directories (if missing)
        fname.parent.mkdir(parents=True, exist_ok=True)

        # Download the content and save it in `fname`
        log_download.info(url)

        with urlopen(url, context=CONTEXT) as resp:  # noqa: S310 (URL audited above)
            fname.write_bytes(resp.read())

        log_download.debug('Saved in: %s', fname)

    else:  # when file exists and not forced
        raise FileExistsError(fname)

    return fname
