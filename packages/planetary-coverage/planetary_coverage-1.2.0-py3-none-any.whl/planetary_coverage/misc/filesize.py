"""File size module"""

from pathlib import Path

import numpy as np


UNITS = [
    'B',
    'kB',
    'MB',
    'GB',
    'TB',
    'PB',
]


def file_size(*fname, fmt=',.0f', skip=False) -> str:
    """Get filesize as human string.

    Parameters
    ----------
    *fname: str or pathlib.Path
        Filename(s) to measure.
    fmt: str, optional
        Size format. Default: ``',.0f'``.
    skip: bool, optional
        Skip error handling and return zero-size
        if the file does not exists. Default: ``False``.

    Returns
    -------
    str
        Filesize human string.
        If multiple files are provided, it returns the sum of their
        combined sizes.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.

    """
    return as_bytes(sum(get_size(f, skip=skip) for f in fname), fmt=fmt)


def get_size(fname, skip=False) -> int:
    """Get filename size.

    Parameters
    ----------
    fname: str or pathlib.Path
        File name to measure.
    skip: bool, optional
        Skip error handling and return zero-size
        if the file does not exists. Default: ``False``.

    Returns
    -------
    int
        Filesize as bytes.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.

    """
    fname = Path(fname)

    if not fname.is_file():
        if not skip:
            raise FileNotFoundError(fname)
        return 0

    return fname.stat().st_size


def as_bytes(size, fmt=',.0f'):
    """Convert filesize as compressed bytes units.

    Parameters
    ----------
    size: int or float
        File size to convert.
    fmt: str, optional
        Size format to adjust the precision.
        Default: ``',.0f'``.

    Returns
    -------
    str
        File size human string.

    """
    i = int(np.ceil(np.log2(size) // 10)) if size != 0 else 0

    if i >= len(UNITS):
        i = len(UNITS) - 1

    return f'{size / 2 ** (10 * i):{fmt}} {UNITS[i]}'
