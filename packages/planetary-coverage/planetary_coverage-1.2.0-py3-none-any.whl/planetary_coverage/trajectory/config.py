"""Tour configuration module."""

from pathlib import Path

import numpy as np

from .trajectory import AltitudeTooHighError, Flyby, Trajectory
from ..esa import ESA_MK
from ..events.event import Event, EventsDict, EventsList, EventWindow
from ..misc import cached_property, getenv
from ..spice import MetaKernel, SpiceAbCorr, SpicePool, check_kernels
from ..spice.metakernel import MissingKernelError, MissingKernelsRemoteError


class TourConfig:
    """Orbital tour configuration object.

    Prepare the kernels configuration based on the selected
    spacecraft, target and metakernel setup.
    By default the SPICE kernel pool is purge and
    automatically loaded with the selected kernels.

    Parameters
    ----------
    mk: MetaKernel or str, optional
        Metakernel filename (``*.tm``) or ESA metakernel identifier key.
        You can provide your own or use the one provided by ESA based
        on the spacecraft selected (default: `None`).

        For example: ``'5.0'`` with the spacecraft ``JUICE``
        will load ``juice_crema_5_0.tm`` metakernel.

    kernels: str or pathlib.Path, optional
        Kernel filename or list of kernel filenames that will be loaded
        into the kernel pool.

        This could be use alone or complementary to a metakernel.
        If used with a metakernel, the kernels will be loaded at the end
        and will have the priority over the kernels in the metakernel.

    spacecraft: str, optional
        Name of the spacecraft selected (default: `JUICE`).

    instrument: str, optional
        Name of the instrument selected (default: `None`).

    target: str or SpiceBody, optional
        Name of the target selected (default: `Ganymede`).

    version: str, optional
        ESA metakernel SKD version / tag (default:`latest`).
        This parameter is only available for metakernel defined
        with a key/shortcut and available in :attr:`ESA_MK`.

    kernels_dir: str or pathlib.Path, optional
        Kernels directory location.

        This parameter is only used to substitute the ``$KERNELS``
        symbol value at runtime in the provided metakernel.
        This parameter has no effect on the :attr:`kernels` parameter.

        If no explicit value is provided (default), the tool will try to
        pull the kernel location from your environment variables configuration, i.e.
        it will use the `KERNELS_XXXX` env variable if you defined it on your system
        (with `XXXX` the name spacecraft).

    download_kernels: bool, optional
        Try to download the missing kernels in the metakernel if they are
        missing (default: `False`).
        This parameter has no effect on the :attr:`kernels` parameter.

    remote_kernels: str or int, optional
        Remote kernel source. If none is provided (default), the content of
        the file will be parsed to search for a remote base value (with ``://``).
        If multiple remotes are present, the first one will be used by default.
        You can provide an integer to choose which one you want to use.
        This value is not required if all the kernel are present locally (it is only
        used to download the missing kernels).

    load_kernels: bool, optional
        Explicitly force the load to the kernels in the SPICE pool (default: False).
        If forced, the content of the SPICE pool is checked, flushed and reloaded
        if needed. This can also be achieved with the `.load_kernels()` function.
        Any SPICE related calculation (decorated with `@check_kernels`) will performed
        this check.

    default_time_step: str, optional
        Default time step if a temporal slice is provided without
        a defined temporal step (default: ``1 minute``).

    abcorr: str, optional
        Aberration corrections to be applied when computing
        the target's position and orientation.
        Only the SPICE keys are accepted.

    exclude: EventWindow, EventsDict or EventsList
        Event window, dict or list of events to exclude from the analysis.

    Raises
    ------
    ValueError
        If the metakernel is provided as a key/shortcut but the associated
        spacecraft is not available in :attr:`ESA_MK`.

    KernelsDirectoryNotFoundError
        If not kernels directory is supplied and the kernels were
        not found in the metakernel location.

    KernelNotFoundError
        If some kernels are missing and :attr:`download_kernels`
        is set to ``False``.

    KernelRemoteNotFoundError
        If the source of the kernels in the metakernel is unknown.

    KeyError
        If the target name is unknown.

    Tip
    ---
    If you need to replace a custom ``PATH_SYMBOLS`` different from `KERNELS`
    you could provide a :class:`.MetaKernel` object with the substituted values
    in the initial call:

    >>> TourConfig(mk=MetaKernel('foo.tm', custom_symbol='CUSTOM_VALUE'))

    """

    kernels = ()

    def __init__(  # noqa: PLR0913 (too-many-arguments)
        self,
        *,
        mk=None,
        kernels=None,
        spacecraft='JUICE',
        instrument='',
        target='Ganymede',
        version='latest',
        kernels_dir=None,
        download_kernels=False,
        remote_kernels=0,
        load_kernels=False,
        default_time_step='1 minute',
        abcorr='NONE',
        exclude=None,
    ):
        # Properties
        self.spacecraft = spacecraft.upper()
        self.target = target.upper()
        self.instrument = instrument.upper()
        self.exclude = exclude

        # Kernel setup
        self.mk = mk, version, kernels_dir, download_kernels, remote_kernels
        self._add(kernels)

        if load_kernels:
            self.load_kernels()

        # Trajectory/Flyby default parameters
        self.default_time_step = default_time_step
        self.abcorr = SpiceAbCorr(abcorr)

    def __repr__(self):
        return f'<{self.__class__.__name__}> ' + ' | '.join(
            filter(
                lambda x: x is not None,
                [
                    f'Spacecraft: {self.spacecraft}',
                    f'Instrument: {self.instrument}' if self.instrument else None,
                    f'Target: {self.target}',
                    f'Metakernel: {self.mk_identifier}' if self.mk else None,
                    f'SKD version: {self.skd_version}' if self.skd_version else None,
                ],
            )
        )

    def __getitem__(self, times):
        traj = Trajectory(
            self.kernels,
            self.spacecraft,
            self.target,
            self._parse(times),
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

        if self.instrument:
            return traj.new_traj(instrument=self.instrument)

        return traj

    def __hash__(self):
        """Kernels hash."""
        return self._kernels_hash

    @cached_property
    def _kernels_hash(self):
        """Expected Spice Pool kernels hash."""
        return SpicePool.hash(self.kernels)

    @property
    def mk(self) -> MetaKernel:
        """Selected metakernel."""
        return self.__mk

    @mk.setter
    def mk(self, args):
        """Metakernel setter.

        Parameters
        ----------
        mk, kernels_dir, download: str or MetaKernel, str, bool
            Metakernel key or filename.
            The kernels directory that with be used to substitute the
            ``$KERNELS`` symbol value in the metakernel at runtime.

        Raises
        ------
        ValueError
            If the metakernel is provided as a key/shortcut but the associated
            spacecraft is not available in :attr:`ESA_MK`.

        KernelsDirectoryNotFoundError
            If not kernels directory is supplied and the kernels were
            not found in the metakernel location.

        KernelNotFoundError
            If some kernels are missing and :attr:`download_kernels`
            is set to ``False``.

        KernelRemoteNotFoundError
            If the source of the kernels in the metakernel is unknown.

        """
        mk, version, kernels_dir, download_kernels, remote_kernels = args

        # Store input mk parameters
        self._version, self._kernels_dir, self._download_kernels, self._remote_kernels = (
            version,
            kernels_dir,
            download_kernels,
            remote_kernels,
        )

        if not isinstance(mk, (type(None), MetaKernel)):
            # Defined metakernels keyword arguments
            kwargs = {'download': download_kernels, 'remote': remote_kernels}

            if kernels_dir is None:
                spacecraft = str(self.spacecraft).replace(' ', '_')
                kernels_dir = getenv(f'KERNELS_{spacecraft}')

            if kernels_dir:
                kwargs['kernels'] = kernels_dir

            # Load ESA metakernel from key/shortcut (if available)
            if not str(mk).lower().endswith('.tm'):
                if self.spacecraft not in ESA_MK:
                    raise ValueError(
                        f'The spacecraft provided (`{self.spacecraft}`) does not support '
                        'ESA metakernel shortcuts. '
                        'Please provide an explicit `metakernel.tm` file.'
                    )

                mk = ESA_MK[self.spacecraft, mk, version]

            # Load the metakernel content and catch errors
            try:
                mk = MetaKernel(mk, **kwargs)

            except MissingKernelError:
                if not kernels_dir:
                    raise KernelsDirectoryNotFoundError(
                        'You need to provide an explicit `kernels_dir` attribute '
                        f'or add an environment variable `KERNELS_{self.spacecraft}`'
                        ' with the path to your kernels directory.'
                    ) from None

                raise KernelNotFoundError(
                    'Some kernels are missing, use `download_kernels=True` '
                    'to download them.'
                ) from None

            except MissingKernelsRemoteError:
                raise KernelRemoteNotFoundError(
                    'The source of the kernels in the metakernel is unknown. '
                    'You can provide directly a `MetaKernel` object '
                    'with an explicit `remote` attribute to fix this issue.'
                ) from None

        # Cache the metakernel
        self.__mk = mk
        self.kernels = (mk,) if mk is not None else ()

    @property
    def metakernel(self) -> Path:
        """Metakernel filename."""
        return self.mk.fname if self.mk else None

    def _add(self, kernel):
        """Add custom kernels to the configuration.

        The additional kernels are loaded after the metakernel (if present)
        and will have the priority in the Spice Pool.

        """
        if kernel is not None:
            if hasattr(kernel, '__iter__') and not isinstance(kernel, str):
                for _kernel in kernel:
                    self._add(_kernel)
            else:
                self.kernels += (str(Path(kernel).expanduser()),)

    @property
    @check_kernels
    def skd_version(self) -> str:
        """ESA metakernel SKD version value."""
        try:
            return SpicePool['SKD_VERSION']
        except KeyError:
            return None

    @property
    @check_kernels
    def mk_identifier(self) -> str:
        """ESA metakernel ID identifier value."""
        try:
            return SpicePool['MK_IDENTIFIER']
        except KeyError:
            return self.mk

    def _parse(self, times):
        """Parse input times.

        Method used in :func:`__getitem__` to query a trajectory
        on a temporal grid.

        Parameters
        ----------
        times: str, int, float, slice, list, Event or EventWindow
            Different input times by types:

            - ``None`` or ``'all'`` for the whole tour (use the full
            coverage of the observer and the target loaded in the
            SPICE pool) with a regular temporal step of 30 minutes.
            If you need the full coverage with another time step,
            please consider using a slice with empty ``start`` and
            ``stop`` values (``[::'1 year']``).

            - ``'2033-01-01T12:34:56'`` time string with or without
            explicit time. All the SPICE time formats are supported.
            No change is performed in this method (conversion to ET
            is done in the :class:`Trajectory` initialization).

            - ``numpy.datetime64`` can be used (it will be converted
            as an ISO time string later, no change here).

            - ``int`` or ``float`` is considered to be an ephemeris
            time (ET). No change in this method.

            - ``slice(start, stop, step)`` times. All of them are
            optional.
            ``start`` can be replaced by ``None|'start'|'beg'|'begin'|'beginning'``
            to use the coverage first point.
            ``stop`` can be replaced by ``None|'stop'|'end'``
            to use the coverage last point.
            If no explicit ``step`` is provided, the :attr:`default_time_step`
            (provided in :func:`__init__`) will be used; if an ``int`` is
            provided, it will correspond to the total number of points (evenly
            space in time).

            - ``list``, ``tuple``, ``numpy.array`` are only modified
            when an :class:`Event` or an :class:`EventWindow`
            is provided (converted to ET later).

            - :class:`Event` will extract the event time (single value).

            - :class:`EvenWindow` will extract the start and stop time of
            the event window (the :attr:`default_time_step`)

            - ``'event-name'`` if a ``fk`` event kernel is provided,
            events can be loaded directly with their names.

        Returns
        -------
        int, float, str, slice, list, tuple or numpy.datetime64
            Parsed input time when necessary.

        """
        if isinstance(times, (tuple, list, np.ndarray, EventsDict, EventsList)):
            return [self._parse(t) for t in times]

        if isinstance(times, (Event, EventWindow)):
            return self._parse_event(times)

        if isinstance(times, slice):
            return self._parse_slice(times)

        if times in {None, 'all'}:
            return slice(*self.coverage, '30 minutes')

        if event := self._get_event(times):
            return self._parse(event)

        return times

    def _parse_event(self, event):
        """Parse event times."""
        if isinstance(event, Event):
            return event.start

        # EventWindow
        return slice(event.start, event.stop, self.default_time_step)

    def _parse_slice(self, t_slice):
        """Parse slice times."""
        start, stop, step = t_slice.start, t_slice.stop, t_slice.step

        if start in {None, 'start', 'beg', 'begin', 'beginning'}:
            start = self.coverage[0]

        elif isinstance(start, Event):
            start = start.start
            if not isinstance(stop, Event):
                return start

        elif isinstance(start, EventWindow):
            # EventWindow:'1h' -> the step is moved from `stop` to `step`
            start, stop, step = start.start, start.stop, stop

        elif isinstance(start, (EventsDict, EventsList)):
            # Events:'1h' -> the step is moved from `stop` to `step`
            events, step = start, stop
            return [self._parse_slice(slice(event, step)) for event in events]

        elif event := self._get_event(start):
            step = stop
            return self._parse_slice(slice(event, step))

        if stop in {None, 'stop', 'end'}:
            stop = self.coverage[1]

        elif isinstance(stop, Event):
            stop = stop.stop

        if step is None:
            step = self.default_time_step

        return slice(start, stop, step)

    @check_kernels
    def load_kernels(self):
        """Load the required kernels into the SPICE pool.

        Note
        ----
        If the SPICE pool already contains the required kernels, nothing
        will append. If not, the pool is flushed and only the required kernels
        are loaded.

        """

    @property
    @check_kernels
    def coverage(self):
        """Observer and Target intersection coverage.

        Overlapping windows of coverage from the observer
        and target data loaded in the SPICE pool.

        """
        start, stop = SpicePool.coverage(self.spacecraft, self.target)

        # Fix rounding issues
        start += np.timedelta64(1, 'ms')
        stop -= np.timedelta64(1, 'ms')

        return start, stop

    @check_kernels
    def gaps(self, *refs):  # noqa: PLR6301 (@check_kernels requires self)
        """Get temporal coverage gaps intervals by reference(s).

        Parameters
        ----------
        refs: str, int or SpiceRef
            Body(ies) reference(s).

        Returns
        -------
        EventsList
            Events list of gaps.

        """
        gaps = SpicePool.gaps(*refs, fmt='UTC')

        return EventsList([
            EventWindow('coverage-gap', t_start=start, t_end=stop) for start, stop in gaps
        ])

    @cached_property
    @check_kernels
    def phases(self):
        """Mission phases events list.

        The following properties needs to be present in the pool:
        - <SPACECRAFT>_MISSION_PHASE_NAME
        - <SPACECRAFT>_MISSION_PHASE_DESC
        - <SPACECRAFT>_MISSION_PHASE_STRT
        - <SPACECRAFT>_MISSION_PHASE_STOP

        """
        spacecraft = self.spacecraft.upper()

        # Load mission phases
        try:
            phases = np.transpose([
                SpicePool[f'{spacecraft}_MISSION_PHASE_NAME'],
                SpicePool[f'{spacecraft}_MISSION_PHASE_DESC'],
                SpicePool[f'{spacecraft}_MISSION_PHASE_STRT'],
                SpicePool[f'{spacecraft}_MISSION_PHASE_STOP'],
            ])
        except KeyError:
            return {}

        # Parse mission phases
        return EventsDict([
            EventWindow(desc, name=name, desc=desc, t_start=start, t_end=end)
            for name, desc, start, end in phases
        ])

    @cached_property
    @check_kernels
    def timeline(self):
        """Mission timeline events list.

        The following properties needs to be present in the pool:
        - <SPACECRAFT>_TIMELINE_EVENT_TYPE
        - <SPACECRAFT>_TIMELINE_EVENT_NAME
        - <SPACECRAFT>_TIMELINE_EVENT_TIME

        """
        spacecraft = self.spacecraft.upper()

        # Load mission phases
        try:
            timeline = np.transpose([
                SpicePool[f'{spacecraft}_TIMELINE_EVENT_TYPE'],
                SpicePool[f'{spacecraft}_TIMELINE_EVENT_NAME'],
                SpicePool[f'{spacecraft}_TIMELINE_EVENT_TIME'],
            ])
        except KeyError:
            return {}

        # Parse mission phases
        return EventsDict([
            Event(key, **{'Crema name': name, 'time': time})
            for key, name, time in timeline
        ])

    def get_event(self, name):
        """Get event by name from mission phases or timeline.

        Parameters
        ----------
        name: str
            Event name.

        Returns
        -------
        Event or EventWindow
            Queried event or event window from
            the mission phases or timeline, if present.

        Raises
        ------
        KeyError
            If the provided event name is invalid.

        """
        if event := self._get_event(name):
            return event

        raise KeyError(f'Unknown event `{name}`')

    def _get_event(self, name):
        """Internal get event by name from mission phases or timeline.

        See also
        --------
        get_event

        """
        if name in self.phases.keys():  # noqa: SIM118 (__iter__ on values not keys)
            return self.phases[name]

        if name in self.timeline.keys():  # noqa: SIM118 (__iter__ on values not keys)
            return self.timeline[name]

        for event in self.timeline:
            if isinstance(event, EventsList):
                if name in event.crema_names:
                    return event[name]

            elif name == event.get('Crema name'):
                return event

        return None

    def add_kernel(self, *kernels):
        """Create a new tour with additional kernels.

        Parameters
        ----------
        *kernels: str or pathlib.Path
            Kernel(s) to append.

        Returns
        -------
        TourConfig
            New tour configuration with a new set of kernels.

        """
        return TourConfig(
            mk=self.mk,
            kernels=self.kernels[slice(1 if self.mk else 0, None)] + tuple(kernels),
            spacecraft=self.spacecraft,
            instrument=self.instrument,
            target=self.target,
            version=self._version,
            kernels_dir=self._kernels_dir,
            download_kernels=self._download_kernels,
            remote_kernels=self._remote_kernels,
            default_time_step=self.default_time_step,
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

    def new_tour(self, *, spacecraft=None, instrument=None, target=None):
        """Create a new tour configuration for a different set of target/observer.

        You can provide either one or multiple parameters as once.

        Parameters
        ----------
        spacecraft: str or SpiceSpacecraft, optional
            New spacecraft name.
        instrument: str or SpiceInstrument, optional
            New instrument name (see note below).
        target: str or SpiceBody, optional
            New target name.

        Returns
        -------
        TourConfig
            New tour configuration with new parameters.

        Raises
        ------
        ValueError
            If no new parameter is provided.

        Note
        ----
        If a ``spacecraft`` is provided without an ``instrument``,
        the ``instrument`` will be reset to ``''``.

        """
        if not spacecraft and not instrument and not target:
            raise ValueError(
                'You need to provide at least a `spacecraft`, '
                'an `instrument` or a `target` parameter.'
            )

        inst = instrument if instrument else '' if spacecraft else self.instrument

        return TourConfig(
            mk=self.mk,
            kernels=self.kernels[slice(1 if self.mk else 0, None)],
            spacecraft=spacecraft if spacecraft else self.spacecraft,
            instrument=inst,
            target=target if target else self.target,
            version=self._version,
            kernels_dir=self._kernels_dir,
            download_kernels=self._download_kernels,
            remote_kernels=self._remote_kernels,
            default_time_step=self.default_time_step,
            abcorr=self.abcorr,
            exclude=self.exclude,
        )

    @property
    def flybys(self):
        """List of all the flybys on the target below 150,000 km.

        See Also
        --------
        :func:`get_flybys` if you need a different minimal altitude.

        """
        return self.get_flybys()

    def get_flybys(self, event=None, alt_min=150_000):
        """List of all the flybys on the target below a given altitude.

        Parameters
        ----------
        event: EventWindow, EventsDict or EventsList, optional
            Optional event. If none is provided (default), the full
            coverage window will be used with a time step of 30 minutes.
        default_time_step: str, optional
            Default time step grid to search the location of the minimum
            of altitude in the flyby (default: ``'30 mins'``).
        alt_min: float, optional
            Minimal altitude at closest approach (default: ``150,000`` km).

        Returns
        -------
        [Flyby, …]
            List of flybys below the required altitude.

        """
        if event is None:
            if events := self._get_event(f'FLYBY_{self.target.upper()}'):
                flybys = {}
                for ev in events:
                    try:
                        name = ev.get('Crema name')
                        flybys[name] = self.flyby(ev.start, alt_min=alt_min)
                    except AltitudeTooHighError:
                        pass
                return flybys

            # Take the whole tour if no event is provided
            event = 'all'

        return self[event].get_flybys(alt_min=alt_min)

    def flyby(self, approx_ca_date, *dt, alt_min=150_000):
        """Select a single flyby with an approximate date.

        Parameters
        ----------
        approx_ca_date: float, str or numpy.datetime64
            Approximate CA datetime (at day level).
            This value will be re-computed (at the second level).
            :class:`.Event`,
            :class:`.EventWindow`,
            :class:`.EventsDict` and
            :class:`.EventsList` can be used as well.

        *dt: tuple(s), optional
            Temporal sequence around closest approach:

            .. code-block:: text

                (duration, numpy.datetime unit, step value and unit)

            See :func:`.et_ca_range` for more details.

        alt_min: float, optional
            Minimal altitude at closest approach (default: 150,000 km).

        Returns
        -------
        SpacecraftFlyby or InstrumentFlyby
            Flyby trajectory.

        Note
        ----
        If an :class:`.EventWindow`, :class:`.EventsDict` or an :class:`.EventsList`
        is provided, the output will be a list of the flybys found in these intervals.

        """
        if isinstance(approx_ca_date, Event):
            approx_ca_date = approx_ca_date.start

        elif isinstance(approx_ca_date, EventWindow):
            return self.get_flybys(event=approx_ca_date, alt_min=alt_min)

        elif isinstance(approx_ca_date, (list, EventsDict, EventsList)):
            return [self.flyby(event, *dt, alt_min=alt_min) for event in approx_ca_date]

        elif event := self._get_event(approx_ca_date):
            return self.flyby(event, *dt, alt_min=alt_min)

        flyby = Flyby(
            self.kernels,
            self.spacecraft,
            self.target,
            approx_ca_date,
            *dt,
            abcorr=self.abcorr,
            exclude=self.exclude,
            alt_min=alt_min,
        )

        if self.instrument:
            return flyby.new_traj(instrument=self.instrument)

        return flyby


class KernelsDirectoryNotFoundError(FileNotFoundError):
    """Kernels directory not found error."""


class KernelNotFoundError(FileNotFoundError):
    """Kernels not found error."""


class KernelRemoteNotFoundError(KernelNotFoundError):
    """Kernels remote not found error."""
