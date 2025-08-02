"""Dot environment files helper module."""

import re
from os import environ, sys
from pathlib import Path

from .logger import logger


log_env, debug_env = logger('VarEnv')


def getenv(
    key: str, default: str = None, max_parents: int = None, dotenv: str = '.env'
) -> str:
    """Get environnement variables from dotenv file or globally.

    Parameters
    ----------
    key: str
        Key to query on the environment
    default: str, optional
        Optional value if not found.
    max_parents: int, optional
        Max number of parent to check recursively for a ``.env`` file.
        To search only the current parent set ``max_parents=0``.
        Default: ``None``.
    dotenv: str, optional
        Dotenv file to search (default: ``'.env'``).
        To load only the global variables set ``dotenv=None``.

    Returns
    -------
    str
        Environment variable value. None, if not found.

    Note
    ----
    The function first search for a ``.env`` file in the
    current working directory, then in its parents up to
    the root. If a ``.env`` file is found, the search is
    stopped and the file is parsed for key-values.
    If not present, the function will search globally if
    the value is present.

    """
    if dotenv and (env := find_dotenv(max_parents=max_parents, fname=dotenv)):
        data = parse_dotenv(env)
        if key in data:
            value = data[key]
            log_env.info('Search for `%s`. Found value: `%s` (in %s)', key, value, env)
            return value

    if key in environ:
        value = environ.get(key)
        log_env.info('Search for `%s`. Found value: `%s` (globally)', key, value)
        return value

    log_env.info('Search for `%s`. Not found, use default: `%s`', key, default)
    return default


def find_dotenv(max_parents: int = None, fname: str = '.env') -> Path:
    """Search for .env file in the working directory and its parents.

    Parameters
    ----------
    max_parents: int, optional
        Max number of parent to check recursively for a ``.env`` file.
        To search only the current parent set ``max_parents=0``.
        Default: ``None``.
    fname: str, optional
        Dotenv file to search (default: ``'.env'``).

    Returns
    -------
    pathlib.Path or None
        File path object.

    Note
    ----
    Only the first parent with a ``.env`` if returned.

    """
    cwd = Path().resolve()

    for parent in [cwd, *list(cwd.parents)[:max_parents]]:
        if (env := parent / fname).exists():
            log_env.debug('%s found', env)
            return env
    return None


KEY = re.compile(r'[a-zA-Z_]+[a-zA-Z0-9_]*')
KEY_VALUE = re.compile(rf'^({KEY.pattern})\s*=\s*(.*)')
INTERP = re.compile(rf'\${{({KEY.pattern})}}')


def parse_dotenv(dot_file: str) -> dict:
    """Read dotenv file.

    Parameters
    ----------
    fname: str or pathlib.Path
        Dot environment file to parse.

    Returns
    -------
    dict
        Parsed environment file as a dict.

    """
    fname = Path(dot_file)

    data, values = {}, []
    for line in fname.read_text(encoding='utf-8').splitlines():
        if values:
            if line.endswith('"""') or line.endswith("'''"):
                key = values[0]
                value = '\n'.join(values[1:] + [line[:-3]])
                data[key] = env_interpolation(value, data, skip=line.endswith("'"))
                values = []
            else:
                values.append(line)

            continue

        _line = line.strip()

        if not _line or _line.startswith('#'):
            continue

        if match := KEY_VALUE.findall(_line):
            key, value = match[0]

            # Start multi-lines
            if value.startswith('"""') or value.startswith("'''"):
                values = [key, value[3:]]
                continue

            # Remove single/double quotes
            if is_quoted(value):
                value = value[1:-1]

            # Remove comment (in not quoted strings only)
            elif '#' in value:
                value, _ = value.split('#', 1)
                value = value.strip()

            data[key] = env_interpolation(value, data, skip=_line.endswith("'"))

    return data


def is_quoted(string: str) -> bool:
    """Check if the string is quoted (single or double)."""
    return (string.startswith("'") and string.endswith("'")) or (
        string.startswith('"') and string.endswith('"')
    )


def env_interpolation(string: str, data: dict, skip: bool = False) -> str:
    """Environment variable interpolation."""
    if skip or not (matches := INTERP.findall(string)):
        return string

    for key in matches:
        if key in data:
            string = string.replace(f'${{{key}}}', data[key])

        elif key in environ:
            string = string.replace(f'${{{key}}}', environ[key])

    return string


def print_kernels_dir(dotenv: str = '.env') -> None:
    """Print kernels folders defined with ENV variables.

    Parameters
    ----------
    dotenv: str, optional
        Dotenv file to search (default: ``'.env'``).
        To load only the global variables set ``dotenv=None``.

    """
    kernels = {k: (v, '') for k, v in environ.items() if k.startswith('KERNELS_')}

    if fname := find_dotenv(fname=dotenv):
        sys.stdout.write(f'Dotenv file found:\n- {fname}\n\n')

        for k, v in parse_dotenv(fname).items():
            if k.startswith('KERNELS_'):
                kernels[k] = (v, ' (.env)')

    sys.stdout.write('Kernels ENV variables:\n')

    if kernels:
        n = max(map(len, kernels))
        for mission, (path, loc) in kernels.items():
            sys.stdout.write(f'- {mission:{n}s}: {path}{loc}\n')

    else:
        sys.stdout.write('- None\n')
