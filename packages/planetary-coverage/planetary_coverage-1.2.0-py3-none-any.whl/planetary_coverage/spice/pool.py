"""Spice kernel pool module."""

from collections import defaultdict, namedtuple
from functools import wraps
from pathlib import Path

import numpy as np

import spiceypy as sp

from ._abc import ABCMetaKernel as MetaKernel
from .kernel import get_details, get_item, get_summary
from .references import SpiceRef
from .times import tdb, utc
from ..html import Html, table
from ..misc import group_by_2, logger


log_spice_pool, debug_spice_pool = logger('Spice Pool')


class MetaSpicePool(type):
    """Meta Spice kernel pool object."""

    MK_HASH = {}

    def __repr__(cls):
        n = int(cls)
        if n == 0:
            desc = 'EMPTY'
        else:
            desc = f'{n} kernel'
            desc += 's' if n > 1 else ''
            desc += ' loaded:\n - '
            desc += '\n - '.join(cls.kernels)

        return f'<{cls.__name__}> {desc}'

    def _repr_html_(cls):
        if int(cls) == 0:
            return (
                '<p><span style="color: #d62728">⌀</span> '
                '<em>No kernel in the pool</em></p>'
            )
        return cls.details.html

    def __int__(cls):
        return cls.count()

    def __len__(cls):
        return cls.count()

    def __hash__(cls):
        return cls.hash(cls.kernels)

    def __eq__(cls, other):
        if isinstance(other, (str, tuple, list)):
            return hash(cls) == cls.hash(other)

        return hash(cls) == other

    def __iter__(cls):
        return iter(cls.kernels)

    def __contains__(cls, kernel):
        return cls.contains(kernel)

    def __add__(cls, kernel):
        return cls.add(kernel)

    def __sub__(cls, kernel):
        return cls.remove(kernel)

    def __getitem__(cls, item):
        return get_item(item)

    @staticmethod
    def count() -> int:
        """Count the number of kernels in the pool."""
        return int(sp.ktotal('ALL'))

    @property
    def kernels(cls):
        """Return the list of kernels loaded in the pool."""
        return tuple(sp.kdata(i, 'ALL')[0] for i in range(cls.count()))

    def hash(cls, kernels) -> int:
        """Hash a (meta)kernel or a list of (meta)kernels."""
        if isinstance(kernels, (str, MetaKernel)):
            return cls.hash((kernels,))

        kernels_hash = ()
        for kernel in kernels:
            if isinstance(kernel, MetaKernel):
                mk = kernel
                # Hash of the metakernel and all the `kernels` loaded with it
                kernels_hash += (hash(mk), *(hash(k) for k in mk.kernels))

            elif kernel in cls.MK_HASH:  # Check if the kernel is in mk hash cached
                kernels_hash += (cls.MK_HASH[kernel],)

            elif kernel is not None:  # If not found, use the kernel hash if not None
                kernels_hash += (hash(kernel),)

        return hash(kernels_hash)

    def contains(cls, kernel):
        """Check if the kernel is in the pool."""
        return kernel in cls.kernels or hash(kernel) in cls.MK_HASH.values()

    def add(cls, kernel, *, purge=False):
        """Add a kernel to the pool."""
        if purge:
            cls.purge()

        if isinstance(kernel, (tuple, list)):
            for _kernel in kernel:
                cls.add(_kernel, purge=False)

        elif kernel in cls:
            raise ValueError(f'Kernel `{kernel}` is already in the pool.')

        elif kernel is not None:
            log_spice_pool.debug('Add `%s` in the SPICE pool', kernel)

            if isinstance(kernel, MetaKernel):
                with kernel as mk:
                    # `mk` is the name of a `NamedTemporaryFile` (see `MetaKernel`)
                    sp.furnsh(mk)

                    log_spice_pool.debug('Cache metakernel original hash.')
                    cls.MK_HASH[mk] = hash(kernel)
            else:
                sp.furnsh(str(Path(kernel).expanduser()))

    def remove(cls, kernel):
        """Remove the kernel from the pool if present."""
        if kernel not in cls:
            raise ValueError(f'Kernel `{kernel}` is not in the pool.')

        if isinstance(kernel, MetaKernel):
            mk_hash = hash(kernel)
            for key, value in cls.MK_HASH.items():
                if value == mk_hash and key in cls.kernels:
                    cls.remove(key)
        else:
            log_spice_pool.debug('Remove %s', kernel)
            sp.unload(kernel)

    def purge(cls):
        """Purge the pool from all its content."""
        log_spice_pool.info('Purge the pool')
        sp.kclear()
        cls.MK_HASH = {}

    @property
    def summary(cls):
        """Pool content summary."""
        return Html(table(get_summary(cls.kernels)))

    @property
    def details(cls):
        """Pool content summary."""
        return Html(table(get_details(cls.kernels)))

    @staticmethod
    def _time_convert(fmt):
        """Time format convertor."""
        if fmt.upper() == 'UTC':
            return utc

        if fmt.upper() == 'TDB':
            return tdb

        if fmt.upper() == 'ET':
            return lambda x: x

        raise TypeError(
            f'Output format unknown: `{fmt}`, only [`UTC`|`TDB`|`ET`] are accepted.'
        )

    @staticmethod
    def _ck_cov(ck, ref: int):
        """Get CK coverage for given body."""
        covers = sp.ckcov(ck, ref, False, 'SEGMENT', 0.0, 'TDB')
        ets = group_by_2(covers)

        log_spice_pool.debug('ET CK cover windows: %r', ets)
        return ets

    @staticmethod
    def _pck_cov(pck, ref: int):
        """Get PCK coverage for given body."""
        cell = sp.cell_double(2000)
        sp.pckcov(pck, ref, cell)
        covers = list(cell)
        ets = group_by_2(covers)

        log_spice_pool.debug('ET PCK cover coverage: %r', ets)
        return ets

    @staticmethod
    def _spk_cov(spk, ref: int):
        """Get SPK coverage for given body."""
        covers = list(sp.spkcov(spk, ref))
        ets = group_by_2(covers)

        log_spice_pool.debug('ET SPK coverage: %r', ets)
        return ets

    def _cov(cls, kernel, ext):
        """Kernel covered ids and method."""
        if ext == 'CK':
            ids = set(sp.ckobj(kernel))
            cov = cls._ck_cov

        elif ext == 'PCK':
            ids = sp.cell_int(1000)
            sp.pckfrm(kernel, ids)
            ids = set(ids)
            cov = cls._pck_cov

        elif ext == 'SPK':
            ids = set(sp.spkobj(kernel))
            cov = cls._spk_cov

        else:
            ids = set()
            cov = None

        return ids, cov

    def windows(cls, *refs, fmt='UTC'):
        """Get kernels windows on a collection of bodies in the pool.

        Based on CK, PCK and SPK files.

        Parameters
        ----------
        refs: str, int or SpiceRef
            Body(ies) reference(s).
        fmt: str, optional
            Output time format:

            - ``UTC`` (default)
            - ``TDB``
            - ``ET``

        Returns
        -------
        {SpiceRef: {str: numpy.ndarray([[float|str, float|str], …]), …}, …}
            Start and stop times windows in the requested format.

        Raises
        ------
        KeyError
            If the requested reference does not have a specific coverage
            range in the pool.

        See Also
        --------
        .coverage
        .gaps
        .brief

        """
        t_fmt = cls._time_convert(fmt)

        refs = {int(ref): ref for ref in map(SpiceRef, refs)}

        windows = defaultdict(dict)
        for i in range(cls.count()):
            kernel, ext, *_ = sp.kdata(i, 'ALL')
            ids, cov = cls._cov(kernel, ext)

            for ref in ids & set(refs):
                log_spice_pool.debug('Found `%s` in %s', refs[ref], kernel)

                if ets := cov(kernel, ref):
                    # Coverage per references and kernels
                    windows[refs[ref]][kernel] = ets

        if not windows:
            values = list(refs.values())
            err = 'The windows for '
            err += f'{values[0]} was' if len(values) == 1 else f'{values} were'
            err += ' not found.'
            raise KeyError(err)

        return {
            ref: {kernel: t_fmt(ets) for kernel, ets in kernels.items()}
            for ref, kernels in windows.items()
        }

    def coverage(cls, *refs, fmt='UTC'):
        """Get coverage for a collection of bodies in the pool.

        Parameters
        ----------
        refs: str, int or SpiceRef
            Body(ies) reference(s).
        fmt: str, optional
            Output time format:

            - ``UTC`` (default)
            - ``TDB``
            - ``ET``

        Returns
        -------
        [str, str] or [float, float]
            Start and stop times covered for the requested format.

        Note
        ----
        If multiple values are available, only the ``max(start)``
        and ``min(stop)`` are kept.

        Raises
        ------
        TypeError
            If the output time format is invalid.
        ValueError
            If the start time is after the stop time

        See Also
        --------
        .coverage
        .gaps

        """
        t_fmt = cls._time_convert(fmt)

        # Get all the temporal windows per references and kernels
        ets_windows = cls.windows(*refs, fmt='ET')

        # Flatten all ET boundaries grouped by references
        ets_refs = [
            [ets for windows in kernels.values() for window in windows for ets in window]
            for kernels in ets_windows.values()
        ]

        # Get starts and stops ET per references
        # and intersect the reference coverage windows
        start = np.max([np.min(ets) for ets in ets_refs])
        stop = np.min([np.max(ets) for ets in ets_refs])

        if start > stop:
            raise ValueError(
                f'MAX start time ({tdb(start)}) is after MIN stop time ({tdb(stop)}).'
            )

        return t_fmt(start), t_fmt(stop)

    def gaps(cls, *refs, fmt='UTC'):
        """Get coverage caps (if any) for a collection of bodies in the pool.

        Parameters
        ----------
        refs: str, int or SpiceRef
            Body(ies) reference(s).
        fmt: str, optional
            Output time format:

            - ``UTC`` (default)
            - ``TDB``
            - ``ET``

        Returns
        -------
        [[str, str], …] or [[float, float], …]
            Start and stop times of coverage gaps intervals in the requested format.


        See Also
        --------
        .windows
        .coverage
        .brief

        """
        t_fmt = cls._time_convert(fmt)

        # Get all the temporal windows per references and kernels
        ets_windows = cls.windows(*refs, fmt='ET')

        return t_fmt(
            sorted([
                [et_start, et_stop]
                for kernels in ets_windows.values()
                for windows in kernels.values()
                if len(windows) > 1
                for (_, et_start), (et_stop, _) in zip(
                    windows[:-1], windows[1:], strict=False
                )
            ])
        )

    def brief(cls, fmt='UTC'):
        """Bodies temporal coverage from CK, PCK and SPK kernels.

        Similar to NAIF `brief -t -a` method.

        Parameters
        ----------
        fmt: str, optional
            Output time format:

            - ``UTC`` (default)
            - ``TDB``
            - ``ET``

        Returns
        -------
        {SpiceRef: (float|str, float|str)}
            Bodies reference dictionary of start and stop times
            covered for the requested format.

        Raises
        ------
        TypeError
            If the output time format is invalid.

        See Also
        --------
        .windows
        .coverage
        .gaps

        """
        t_fmt = cls._time_convert(fmt)

        Interval = namedtuple(
            'Interval', ('start', 'stop'), defaults=(float('inf'), -float('inf'))
        )

        bodies = defaultdict(Interval)

        for i in range(cls.count()):
            kernel, ext, *_ = sp.kdata(i, 'ALL')
            ids, cov = cls._cov(kernel, ext)

            for ref in ids:
                log_spice_pool.debug('Found body `%s` in %s', ref, kernel)
                for start, stop in cov(kernel, ref):
                    bodies[ref] = Interval(
                        min(bodies[ref].start, start),
                        max(bodies[ref].stop, stop),
                    )

        # Sort codes by decreasing negative and increasing positive
        # values to be consistent with NAIF `brief` ordering
        bodies = sorted(bodies.items(), key=lambda x: x[0] if x[0] > 0 else 1 / x[0])

        brief = {}
        for code, (start, stop) in bodies:
            try:
                ref = SpiceRef(code)
                brief[ref] = (t_fmt(start), t_fmt(stop))
            except ValueError:
                # Discard codes with unknown name
                continue

        return brief


class SpicePool(metaclass=MetaSpicePool):
    """Spice kernel pool singleton.

    See: :class:`.MetaSpicePool` for details.

    """


def check_kernels(func):
    """Spice Pool kernels checker decorator.

    The parent object must implement a :func:`__hash__`
    function and have a :attr:`kernels` attribute.

    """

    @wraps(func)
    def wrapper(_self, *args, **kwargs):
        """Check if the content of pool have changed.

        If the content changed, the pool will be purge and the kernels reloaded.

        """
        if SpicePool != hash(_self):
            log_spice_pool.info(
                'The content of the pool changed -> the kernels will be reloaded.'
            )
            SpicePool.add(_self.kernels, purge=True)

        return func(_self, *args, **kwargs)

    return wrapper
