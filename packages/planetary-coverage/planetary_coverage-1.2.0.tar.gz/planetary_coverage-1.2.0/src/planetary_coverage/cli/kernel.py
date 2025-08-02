"""CLI kernel module."""

import sys
from argparse import ArgumentParser
from pathlib import Path
from urllib.error import HTTPError

from ..misc import wget


REMOTES = {
    'generic': 'https://naif.jpl.nasa.gov/pub/naif/generic_kernels/',
    'nasa': 'https://naif.jpl.nasa.gov/pub/naif',
    'esa': 'https://spiftp.esac.esa.int/data/SPICE',
    'jaxa': 'https://data.darts.isas.jaxa.jp/pub/spice',
}


def cli_kernel_download(argv=None):
    """CLI to download kernel(s) from a kernel registry.

    The user can provide an agency + mission argument
    (eg. `--esa JUICE`) to point to the known kernel registry
    or provide directly the URL (`-r/--remote`). If none is
    provided, the cli will attempt to download it from NAIF
    generic kernels.

    Note: only one remote is accepted. Otherwise an ERROR is raised.

    The user can also specify where to store the kernels (with
    `-o/--kernels-dir`).

    If the requested kernel is already present locally, the cli
    will raise an ERROR, unless the user provide a `-f/--force` flag
    (to overwrite it) or `-s/--skip` flag (to continue).

    Hint: the user can provide a list a kernels to download them
    in a batch.

    Tip: if no kernels is provided, the cli will return the remote
    location url.

    """
    parser = ArgumentParser(description='Planetary-coverage kernel downloader.')
    parser.add_argument('kernel', nargs='*', help='One or multiple kernel file(s).')

    parser.add_argument(
        '-r',
        '--remote',
        help='Kernel remote location (HTTPS/FTP). Some shortcuts are available.',
    )
    parser.add_argument(
        '--nasa', metavar='MISSION', help='NASA mission (hosted on NAIF website).'
    )
    parser.add_argument(
        '--esa', metavar='MISSION', help='ESA mission (hosted on ESAC website).'
    )
    parser.add_argument(
        '--jaxa', metavar='MISSION', help='JAXA mission (hosted on ISAS website).'
    )

    parser.add_argument(
        '-o', '--kernels-dir', default='.', help='Output kernel directory.'
    )

    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Overwrite the file if they are already present locally.',
    )
    parser.add_argument('-s', '--skip', action='store_true', help='Skip existing files.')

    args, _ = parser.parse_known_args(argv)

    # Check remotes duplicates
    remotes = {
        agency: mission
        for agency, mission in {
            'url': args.remote,
            'nasa': args.nasa,
            'esa': args.esa,
            'jaxa': args.jaxa,
        }.items()
        if mission is not None
    }

    n_remotes = len(remotes)

    if n_remotes > 1:
        sys.stderr.write(
            f'>>> ERROR: {n_remotes} remotes provided ({", ".join(remotes.keys())}). '
            'Only one is accepted.\n'
        )
        sys.exit(1)

    # Extract the selected remote
    if not remotes:
        remote = REMOTES['generic']
    elif 'url' in remotes:
        remote = remotes['url']
        remote += '' if remote.endswith('/') else '/'
    else:
        for agency, mission in remotes.items():
            remote = f'{REMOTES[agency]}/{mission}/kernels/'

    # Kernel output folder
    kernel_dir = Path(args.kernels_dir)

    # Download the kernels
    for kernel in args.kernel:
        fname = kernel_dir / kernel

        try:
            wget(remote + kernel, fname, skip=args.skip, force=args.force)

        except FileExistsError:
            sys.stderr.write(
                f'>>> ERROR: {fname} is already present locally. '
                'Use `--force` to overwrite it or `--skip` to continue.\n'
            )
            sys.exit(1)

        except HTTPError:
            sys.stderr.write('>>> ERROR: kernel not found.\n')
            sys.exit(1)

    # Display remote location if no kernel is provided
    if not args.kernel:
        _ = sys.stdout.write(remote + '\n') if remotes else parser.print_help()
