"""Kernel data parser.

The full kernel specifications are available on NAIF website:

https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html

"""

import datetime as dt
from collections import defaultdict
from pathlib import Path
from re import findall

import numpy as np

import spiceypy as sp

from .datetime import datetime
from ..misc import file_size


CONTINUATION = defaultdict(
    lambda: '//',
    **{
        'PATH_VALUES': '+',
        'KERNELS_TO_LOAD': '+',
    },
)

# SPICE constrains
KEY_MAX_LENGTH = 32
VALUE_MAX_LENGTH = 80
LINE_MAX_LENGTH = 132

KERNELS_TYPES = {
    # https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/kernel.html
    '.bc': 'CK',  # binary
    '.bds': 'DSK',  # binary
    '.bes': 'EK',  # binary
    '.bpc': 'PCK',  # binary
    '.bsp': 'SPK',  # binary
    '.tf': 'FK',  # text
    '.ti': 'IK',  # text
    '.tls': 'LSK',  # text
    '.tm': 'MK',  # text
    '.tpc': 'PCK',  # text
    '.tsc': 'SCLK',  # text
}

KERNELS_ICONS = {
    'CK': '📷',
    'DSK': '⛰️',
    'EK': '🎤',
    'FK': '🖼️',
    'IK': '🔬',
    'LSK': '⏱️',
    'MK': '📚',
    'PCK': '🪐',
    'SCLK': '🛰️',
    'SPK': '🚀',
}


# User home folder
HOME = str(Path.home())


def kernel_parser(fname):
    """Kernel content and data parser.

    Parameters
    ----------
    fname: str or pathlib.Path
        Kernel file name to parse.

    Returns
    -------
    str, dict
        Kernel whole content and parsed data.

    """
    content = Path(fname).read_text(encoding='utf-8')
    return content, get_data(content)


def get_data(content) -> dict:
    """Extract data from a kernel content.

    Support line continuation (``//`` or ``+``) and value assignment (``+=``).

    """
    data = {}
    last_key = False

    for line in extract_data(content):
        key, value = parse(line)

        if key is not None and key.endswith('+'):
            last_key = key[:-1].strip()
            key = None

            if last_key not in data:
                data[last_key] = []

            elif not isinstance(data[last_key], list):
                data[last_key] = [data[last_key]]

        if key is not None and value is not None:
            data[key] = value
            last_key = key

        elif last_key and value is not None:
            if isinstance(value, list):
                data[last_key].extend(value)
            else:
                data[last_key].append(value)

    return {key: concatenate(key, values) for key, values in data.items()}


def extract_data(content):
    """Extract data from content.

    Extract all the lines in the `\\begindata` sections.

    Parameters
    ----------
    content: str
        Kernel content.

    Returns
    -------
    [str]
        List of data lines.

    """
    begindata = False
    for line in content.splitlines():
        if r'\begindata' in line:
            begindata = True
        elif r'\begintext' in line:
            begindata = False
        elif begindata:
            yield line


def concatenate(key, values):
    """Concatenate string list with a continuation character(s).

    Parameters
    ----------
    key: str
        Kernel key
    values: [str, …]
        Parsed kernel values (list of strings).

    Returns
    -------
    any
        Concatenated value(s) if the continuation character was found.

    Note
    ----
    The continued string character is ``//`` except in
    metakernels for which the keys ``PATH_VALUES`` and ``KERNELS_TO_LOAD``
    are continued with the ``+`` marker.
    If the key is ``PATH_SYMBOLS``, no continuation marker is supported.

    """
    if not (isinstance(values, list) and isinstance(values[0], str)):
        return values

    sep = CONTINUATION[key]
    end = -len(sep)

    cat_values, continuation = [], False
    for value in values:
        val, _continue = (value[:end], True) if value.endswith(sep) else (value, False)

        if continuation:
            cat_values[-1] += val
        else:
            cat_values.append(val)

        continuation = _continue

    return cat_values


def parse(line):
    """Parse data line."""
    if match := findall(r'^(\s*[\w/]+\s*\+?)=(.*)', line):
        k, v = match[0]
        key, value = k.strip(), read(v)

        if '(' in line and not isinstance(value, list):
            value = [value]

        return key, value

    return None, read(line)


def read(value):  # noqa: PLR0911 (kernel value parser)
    """Read the kernel value value.

    - String must be single quoted.
    - Double single quote are replace by a unique single quote.
    - Trailing space in continued string (with ``//``) is removed.
    - Engineering notation with an ``E`` or a ``D`` is supported.

    """
    v = value.strip()

    if v in {'', ')'}:
        return None

    if v.endswith(',') or v.endswith(')'):
        return read(v[:-1])

    if v.startswith('('):
        if "'" in v:
            return read(v[1:])

        sep = ',' if ',' in v else None
        return [read(val) for val in v[1:].split(sep)]

    if v.startswith("'") and v.endswith("'"):
        s = v[1:-1]

        if "'" in s and "''" not in s:
            sep = ',' if ',' in s else None
            return [read(val) for val in v.split(sep)]

        s = s.replace("''", "'")

        if '//' in s:
            s = s.split('//', 1)[0] + '//'

        return s

    if ',' in v or ' ' in v:
        sep = ',' if ',' in v else None
        return [read(val) for val in v.split(sep)]

    if v.startswith('@'):
        return datetime(v[1:])

    return float(v.replace('D', 'E')) if '.' in v else int(v)


def format_data(indent=4, sep=', ', fmt=False, eq='=', **kwargs):
    """Format raw data into a text-kernel complaint string.

    SPICE constrains:

    - All assignments, or portions of an assignment, occurring
      on a line must not exceed 132 characters, including the
      assignment operator and any leading or embedded white space.

    Metakernel only:

    - When continuing the value field (a file name) over multiple lines,
      the continuation marker must be a single ``+`` character.

    - The maximum length of any file name, including any path specification,
      is 255 characters (not enforced here, see
      :func:`planetary_coverage.spice.Metakernel.check`
      for more details).

    Parameters
    ----------
    indent: int, optional
        Number of indentation
    sep: str, optional
        Separator character in vectors (default: ``', '``).
    fmt: bool, optional
        Optional value formatter (e.g. ``.3E`` for ``1.23E-3``).
    eq: str, optional
        Key-value equal sign (default: ``'='``).
    **kwargs: any
        Data keyword(s) and value(s) to format.

    Returns
    -------
    str
        Formatted key and value.

    Raises
    ------
    KeyError
        If a key length is larger than 32 characters.
    ValueError
        If a indentation will create a line larger than 132 characters.

    """
    key_max_length = max(map(len, kwargs))

    if key_max_length > KEY_MAX_LENGTH:
        raise KeyError(f'The keys length must be ≤ {KEY_MAX_LENGTH} ({key_max_length}).')

    indent_length = indent + key_max_length + len(eq) + 4  # len("   KEY = ( ")
    value_max_length = VALUE_MAX_LENGTH + 2  # len("'VALUE'")
    sep_length = max(2, len(sep.rstrip()))  # len(" )") or len(",")

    if indent_length + value_max_length + sep_length > LINE_MAX_LENGTH:
        raise ValueError(
            f'Indent will exceed the {LINE_MAX_LENGTH} character limit '
            f'({indent_length + value_max_length + sep_length}).'
        )

    lines_sep = f'{sep.rstrip()}\n{indent_length * " "}'

    data = []
    for key, value in kwargs.items():
        values = format_value(value, continuation=CONTINUATION[key.upper()], fmt=fmt)

        if isinstance(values, list):
            lines, line = [], values[0]
            for val in values[1:]:
                line_length = indent_length + len(line) + len(sep) + len(val) + sep_length

                if line_length < LINE_MAX_LENGTH and len(val) < VALUE_MAX_LENGTH // 4:
                    line += sep + val
                else:
                    lines.append(line)
                    line = val

            lines.append(line)

            # Suffix the last line with spaces based on the longest line
            suffix_spaces = max(map(len, lines))
            suffix_spaces += len(sep.rstrip()) if len(lines) > 1 else 0
            suffix_spaces -= len(lines[-1])

            values = f'( {lines_sep.join(lines)}{suffix_spaces * " "} )'

        indent_key = f'{indent * " "}{key.upper()}{(key_max_length - len(key)) * " "}'

        data.append(f'{indent_key} {eq} {values}')

    return '\n'.join(data)


def format_value(value, continuation='//', fmt=False):
    """Format kernel value.

    SPICE constrains:
    - String values are supplied by quoting the string using
      a single quote at each end of the string.
    - If you need to include a single quote in the string value,
      use the FORTRAN convention of `doubling` the quote.
    - Everything between the single quotes, including white space
    and the continuation marker, counts towards the limit of
    80 characters in the length of each string element.

    Parameters
    ----------
    value: any
        Data value(s) to format.
    continuation: str, optional
        Continuation character(s) (default: ``//``).
    fmt: bool, optional
        Optional value formatter (e.g. ``.3E`` for ``1.23E-3``).

    Returns
    -------
    str or [str, …]
        Data formatted for key and value.
        The value will be split if its length is larger than the
        80 characters limit. The values lengths ≤ 82.

    """
    if not isinstance(value, (list, tuple, np.ndarray)):
        if isinstance(value, np.datetime64):
            return f'@{value.item().strftime(fmt)}' if fmt else f'@{value}'

        if isinstance(value, (dt.datetime, dt.date)):
            return f'@{value:{fmt}}' if fmt else f'@{value}'

        if not isinstance(value, (str, Path)):
            return f'{value:{fmt}}' if fmt else f'{value}'

        value = str(value).replace("'", "''")

        # Replace tilde character with home directory
        value = value.replace('~', HOME)

        if len(value) <= VALUE_MAX_LENGTH:
            return f"'{value:{fmt}}'" if fmt else f"'{value}'"

        return list(
            chunk_string(value, length=VALUE_MAX_LENGTH, continuation=continuation)
        )

    values = []
    for val in value:
        v = format_value(val, continuation=continuation, fmt=fmt)

        if isinstance(v, list):
            values.extend(v)
        else:
            values.append(v)

    return values


def chunk_string(string, length=VALUE_MAX_LENGTH, continuation='//'):
    """Chunk value string to a specific length.

    The continuation character is included in the length
    of the final string.

    Parameters
    ----------
    string: str
        String to chunk.
    length: int, optional
        Max string length (default: 80).
    continuation: str, optional
        Continuation character(s) (default: ``//``).

    Returns
    -------
    list
        List of chunks of the string.

    """
    if len(string) > length:
        n = length - len(continuation)
        beg, end = string[:n] + continuation, string[n:]

        yield f"'{beg}'"
        yield from chunk_string(end, length=length, continuation=continuation)

    else:
        yield f"'{string}'"


def get_item(item, start=0, chunk_size=1_000):
    """Item getter from the SPICE pool.

    Warning
    -------
    If a wild string (``*``) or wild character (``%``) is
    provided, the return value will corresponding to matching
    key(s) and not its value(s).

    Parameters
    ----------
    item: str
        Item key to query.
    start: int, optional
        Get the items giving a starting position.
    chunk_size: int, optional
        Pool search chunk length (default: 1,000).

    Returns
    -------
    any
        Item value from the SPICE pool or the matching key(s)
        if a wildcard is requested.

    Raises
    ------
    KeyError
        If no value is not present in the SPICE pool or the item does
        not match any key.

    See Also
    --------
    find_item

    """
    # Wildcard
    if '*' in item or '%' in item:
        return find_item(item, start=start, chunk_size=chunk_size)

    # Value(s) query
    try:
        arr = list(sp.gdpool(item, start, chunk_size))

    except sp.stypes.NotFoundError:
        try:
            arr = list(sp.gcpool(item, start, chunk_size))

        except sp.stypes.NotFoundError:
            raise KeyError(f'`{item}` was not found in the kernel pool.') from None

    # Large chunks
    if len(arr) == chunk_size:
        elements = get_item(item, start=start + chunk_size, chunk_size=chunk_size)
        if isinstance(elements, list):
            arr.extend(elements)
        else:
            arr.append(elements)

    return arr if len(arr) > 1 else arr[0]


def find_item(item, start=0, chunk_size=1_000):
    """Find item key in the SPICE pool content.

    You need to provide an item with a wild string (``*``)
    or wild character (``%``).

    Parameters
    ----------
    item: str
        Item key with a wildcard to search in the pool.
    start: int, optional
        Get the items giving a starting position.
    chunk_size: int, optional
        Pool search chunk length (default: 1,000).

    Returns
    -------
    any
        Item key(s) matching the provided pattern.

    Raises
    ------
    KeyError
       If no key in the pool match the provided item.

    See Also
    --------
    get_item

    """
    try:
        keys = list(sp.gnpool(item, start, chunk_size))

    except sp.stypes.NotFoundError:
        raise KeyError(f'No item matching `{item}` found in the kernel pool.') from None

    # Large chunks
    if len(keys) == chunk_size:
        keys.extend(get_item(item, start=start + chunk_size, chunk_size=chunk_size))

    return sorted(keys)


def get_type(kernel, default_txt='UNKNOWN', default_icon='❓') -> str:
    """Get kernel type icon.

    Parameters
    ----------
    kernel: str or pathlib.Path
        Kernel filename.
    default_txt: str, optional
        Optional default type if the extension is unknown.
    default_icon: str, optional
        Optional default type if the kernel type is unknown.

    Returns
    -------
    str
        Kernel icon based on it extension.


    """
    ext = Path(kernel).suffix
    ktype = KERNELS_TYPES.get(ext, default_txt)
    icon = KERNELS_ICONS.get(ktype, default_icon)

    return f'{icon} {ktype}'.strip()


def get_summary(kernels):
    """Get kernels summary description.

    Parameters
    ----------
    kernels: [str or pathlib.Path, ...]
        List of kernel file names.

    Returns
    -------
    list
        Summary of kernels count and sizes grouped by types.

    """
    groups = defaultdict(list)
    for k in kernels:
        groups[get_type(k)].append(k)

    # Append the total to the end
    groups['<b>Total</b>'] = kernels

    return {
        'Types': list(groups.keys()),
        'Count': [len(k) for k in groups.values()],
        'Size': [file_size(*k, skip=True) for k in groups.values()],
    }


def get_details(kernels):
    """Get kernels detailed description.

    Parameters
    ----------
    kernels: [str or pathlib.Path, ...]
        List of kernel file names.

    Returns
    -------
    list
        Detailed list of kernels types and sizes.

    """
    return {
        'Kernels': kernels,
        'Type': [get_type(k) for k in kernels],
        'Size': [file_size(k, skip=True) for k in kernels],
    }
