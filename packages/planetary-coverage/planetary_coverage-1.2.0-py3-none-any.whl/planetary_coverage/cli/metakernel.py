"""CLI metakernel module."""

from argparse import ArgumentParser

from ..spice import MetaKernel


def cli_metakernel_download(argv=None):
    """CLI to download the missing kernel in a metakernel.

    If a remote location is provided in the file header it will be used
    by default, unless if the user provide a custom `-r/--remote` location.

    By default, the kernels will be stored at the location defined in the metakernel.
    This parameter can be override with `-o/--kernels-dir`.

    """
    parser = ArgumentParser(description='Planetary-coverage metakernel downloader')
    parser.add_argument('mk', help='Metakernel file.')
    parser.add_argument(
        '-r',
        '--remote',
        help='Kernel remote location (HTTPS/FTP). '
        'By default, if a remote is provided in the metakernel, '
        'text header, this remote will be used',
    )
    parser.add_argument(
        '-o',
        '--kernels-dir',
        help='Override the $KERNELS variable in the metakernel '
        'in order to choose where your kernels will be stored.',
    )

    args, _ = parser.parse_known_args(argv)

    # Set default parameters
    kwargs = {'download': True}

    if args.remote:
        kwargs['remote'] = args.remote

    if args.kernels_dir:
        kwargs['kernels'] = args.kernels_dir

    # Download the missing kernels
    MetaKernel(args.mk, **kwargs)
