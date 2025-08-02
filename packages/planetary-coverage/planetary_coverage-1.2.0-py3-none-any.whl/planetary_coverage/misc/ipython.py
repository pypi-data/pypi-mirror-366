"""IPython module."""

import contextlib
from importlib.metadata import PackageNotFoundError, version
from os import sys

from .dotenv import print_kernels_dir


def load_ipython_extension(ipython):
    """Print the list of installed packages and kernels directories.

    IPython/Jupyter magic line: ``%load_ext planetary_coverage``

    """
    print_package(
        'planetary-coverage',
        'esa-ptr',
        'numpy',
        'matplotlib',
        'spiceypy',
    )

    sys.stdout.write('\n')

    print_kernels_dir()


def print_package(*packages):
    """Print packages versions.

    Note
    ----
    Only the available packages are printed in stdout.

    """
    sys.stdout.write('Installed packages:\n')

    n = max(map(len, packages))
    for package in packages:
        with contextlib.suppress(PackageNotFoundError):
            sys.stdout.write(f'- {package:{n}s}: {version(package.lower())}\n')
