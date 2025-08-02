"""Event module."""

import contextlib
import re
from collections import UserDict, UserList
from operator import attrgetter
from pathlib import Path

import numpy as np

from ..html import table
from ..misc import logger
from ..spice.datetime import datetime, np_date_str, timedelta


warn, _ = logger('EventsFileParser')


class AbstractEvent(UserDict):
    """Single time event object."""

    def __init__(self, key, *args, **kwargs):
        self.key = key

        if 'contextual info' in kwargs:
            infos = kwargs.pop('contextual info')
            if infos:
                for info in infos.split(';'):
                    key, value = info.split('=', 1)
                    kwargs[key.strip()] = value.strip()

        super().__init__(*args, **kwargs)

        if ('t_start' in self and 't_end' in self) or (
            'start_time' in self and 'end_time' in self
        ):
            self.__class__ = EventWindow

        elif (
            'event time [utc]' in self
            or 'event utc apo' in self
            or 'event utc peri' in self
            or 'time' in self
        ):
            self.__class__ = Event

        else:
            raise ValueError(f'Event time(s) not found: {kwargs}')

    def __repr__(self):
        return '\n - '.join([
            f'<{self.__class__.__name__}> {self}:',
            *[f'{k}: {v}' for k, v in self.items()],
        ])

    def _repr_html_(self):
        return table(list(self.items()))

    def _ipython_key_completions_(self):
        return self.keys()

    def __contains__(self, utc):
        if isinstance(utc, str) and utc in self.data:
            return True

        try:
            return self.contains(utc).any()
        except ValueError:
            return False

    def __hash__(self):
        return hash(frozenset(self.items()))

    def __add__(self, other):
        """Add to stop time."""
        return self.stop + timedelta(other)

    def __sub__(self, other):
        """Subtract from start time."""
        return self.start - timedelta(other)

    def __gt__(self, other):
        return self.start > np.datetime64(str(other))

    def __ge__(self, other):
        return self.start >= np.datetime64(str(other))

    def __lt__(self, other):
        return self.stop < np.datetime64(str(other))

    def __le__(self, other):
        return self.stop <= np.datetime64(str(other))

    @property
    def start(self) -> np.datetime64:
        """Event start time."""
        raise NotImplementedError

    @property
    def stop(self) -> np.datetime64:
        """Event stop time."""
        raise NotImplementedError

    @property
    def start_date(self):
        """Event start date."""
        return np_date_str(self.start)

    @property
    def stop_date(self):
        """Event stop date."""
        return np_date_str(self.stop)

    def contains(self, pts):
        """Check if points are inside the temporal windows.

        Parameters
        ----------
        pts: numpy.ndarray
            List of temporal UTC point(s): ``utc`` or ``[utc_0, …]``.
            If an object with :attr:`utc` attribute/property is provided,
            the intersection will be performed on these points.

        Returns
        -------
        numpy.ndarray
            Return ``True`` if the point is inside the pixel corners, and
            ``False`` overwise.

        Note
        ----
        If the point is on the edge of the window it will be included.

        """
        if hasattr(pts, 'utc'):
            return self.contains(pts.utc)

        if isinstance(pts, str):
            return self.contains(np.datetime64(pts))

        if isinstance(pts, (list, tuple)):
            return self.contains(np.array(pts).astype('datetime64'))

        return (self.start <= pts) & (pts <= self.stop)

    def trim(self, *, before=None, after=None, by_event=None):
        """Trim the event with time boundaries.

        Parameters
        ----------
        before: str, datetime.datetime or numpy.datetime64
            Start time window to consider.
        after: str, datetime.datetime or numpy.datetime64
            Stop time window to consider.
        by_event: AbstractEvent or AbstractEventsCollection
            Event(s) that can be used as an time window range.

        Returns
        -------
        AbstractEvent
            Same event if the event is inside the time window considered.
        AbstractEvent
            A trimmed event if the event cross one or both boundaries.
        None
            If the event is outside the time window considered.

        """
        raise NotImplementedError


class Event(AbstractEvent):
    """Single time event object."""

    def __str__(self):
        return f'{self.key} ({self.start_date})'

    @property
    def _time_value(self) -> str:
        """Event time value."""
        if 'event time [utc]' in self:
            return str(self['event time [utc]']).removesuffix('Z')

        if 'event utc apo' in self:
            return self['event utc apo']

        if 'event utc peri' in self:
            return self['event utc peri']

        if 'time' in self:
            return self['time']

        raise KeyError('Event time not found')

    @property
    def start(self) -> np.datetime64:
        """Event start time."""
        return datetime(self._time_value)

    @property
    def stop(self) -> np.datetime64:
        """Event stop time (same as start time)."""
        return self.start

    def trim(self, *, before=None, after=None, by_event=None):
        """Discard the event if outside the time boundaries.

        Parameters
        ----------
        before: str, datetime.datetime or numpy.datetime64
            Start time window to consider.
        after: str, datetime.datetime or numpy.datetime64
            Stop time window to consider.
        by_event: AbstractEvent or AbstractEventsCollection
            Event(s) that can be used as an time window range.

        Returns
        -------
        Event
            Same event if the event is inside the time window considered.
        None
            If the event is outside the time window considered.

        """
        if by_event:
            return self.trim(before=by_event.start, after=by_event.stop)

        if before is not None and self.start < np.datetime64(str(before)):
            return None

        if after is not None and np.datetime64(str(after)) < self.stop:
            return None

        return self


class EventWindow(AbstractEvent):
    """Window time event object."""

    def __str__(self):
        return f'{self.key} ({self.start_date} -> {self.stop_date})'

    @property
    def start(self) -> np.datetime64:
        """Event start time."""
        for key in ['t_start', 'start_time']:
            if key in self:
                return np.datetime64(str(self[key]).removesuffix('Z'))

        raise KeyError('Start event time not found')

    @property
    def stop(self) -> np.datetime64:
        """Event stop time."""
        for key in ['t_end', 'end_time']:
            if key in self:
                return np.datetime64(str(self[key]).removesuffix('Z'))

        raise KeyError('Stop event time not found')

    def trim(self, *, before=None, after=None, by_event=None):
        """Trim the event with time boundaries.

        Parameters
        ----------
        before: str, datetime.datetime or numpy.datetime64
            Start time window to consider.
        after: str, datetime.datetime or numpy.datetime64
            Stop time window to consider.
        by_event: AbstractEvent or AbstractEventsCollection
            Event(s) that can be used as an time window range.

        Returns
        -------
        EventWindow
            Same event if the event is inside the time window considered.
        EventWindow
            A trimmed event if the event cross one or both boundaries.
        None
            If the event is outside the time window considered.

        """
        if by_event:
            return self.trim(before=by_event.start, after=by_event.stop)

        data = dict(self.data)

        if before is not None and self.start < np.datetime64(str(before)):
            data['t_start'] = str(before)

        if after is not None and np.datetime64(str(after)) < self.stop:
            data['t_end'] = str(after)

        if np.datetime64(data['t_start']) <= np.datetime64(data['t_end']):
            return EventWindow(self.key, data)

        return None


class AbstractEventsCollection:
    """Abstract collection of events."""

    def __repr__(self):
        return f'<{self.__class__.__name__}> {self}'

    def __contains__(self, utc):
        try:
            return self.contains(utc).any()
        except ValueError:
            return False

    def __hash__(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def _filter(self, func, err_msg):
        """Comparison filter."""
        elements = []
        for event in self:
            if isinstance(event, AbstractEventsCollection):
                with contextlib.suppress(LookupError):
                    elements.append(func(event))
            elif func(event):
                elements.append(event)

        if elements:
            if len(elements) == 1:
                return elements[0]

            if isinstance(self, EventsList):
                return EventsList(elements)

            return EventsDict(elements)

        raise LookupError(err_msg)

    def __gt__(self, other):
        return self._filter(lambda event: event > other, f'{self} <= {other}')

    def __ge__(self, other):
        return self._filter(lambda event: event >= other, f'{self} < {other}')

    def __lt__(self, other):
        return self._filter(lambda event: event < other, f'{self} >= {other}')

    def __le__(self, other):
        return self._filter(lambda event: event <= other, f'{self} > {other}')

    @property
    def starts(self) -> list:
        """Event start times."""
        return [event.start for event in self]

    @property
    def stops(self) -> list:
        """Event stop times."""
        return [event.stop for event in self]

    @property
    def windows(self) -> list:
        """Event windows."""
        return [(event.start, event.stop) for event in self]

    @property
    def start(self) -> np.datetime64:
        """Global events start time."""
        return min(self.starts)

    @property
    def stop(self) -> np.datetime64:
        """Global events stop time."""
        return max(self.stops)

    @property
    def start_date(self):
        """global events start date."""
        return np_date_str(self.start)

    @property
    def stop_date(self):
        """Global events stop date."""
        return np_date_str(self.stop)

    def contains(self, pts):
        """Check if points are inside any temporal window.

        Parameters
        ----------
        pts: numpy.ndarray
            List of temporal UTC point(s): ``utc`` or ``[utc_0, …]``.
            If an object with :attr:`utc` attribute/property is provided,
            the intersection will be performed on these points.

        Returns
        -------
        numpy.ndarray
            Return ``True`` if the point is inside the pixel corners, and
            ``False`` overwise.

        Note
        ----
        If the point is on the edge of the window it will be included.

        """
        return np.any([event.contains(pts) for event in self], axis=0)

    def before(self, date_stop, strict=False, as_dict=False):
        """Select all the events before the given date."""
        res = self < date_stop if strict else self <= date_stop
        return EventsDict(res) if as_dict else res

    def after(self, date_start, strict=False, as_dict=False):
        """Select all the events after the given date."""
        res = self > date_start if strict else self >= date_start
        return EventsDict(res) if as_dict else res

    def between(self, date_start, date_stop, strict=False, as_dict=False):
        """Select all the events between the given dates.

        Danger
        ------
        The parenthesis in the comparison are mandatory here.
        Comparison operator chains (``a < b < c``) will break
        due to short-circuit chain evaluation (``a < b and b < c``)
        where only ``a < b`` if the result is not `False` and
        ``b < c`` otherwise, not the intersection (``(a < b) & (b < c)``).

        """
        res = (
            (date_start < self) < date_stop
            if strict
            else (date_start <= self) <= date_stop
        )
        return EventsDict(res) if as_dict else res

    def trim(self, *, before=None, after=None, by_event=None):
        """Trim the events within time boundaries.

        Parameters
        ----------
        before: str, datetime.datetime or numpy.datetime64
            Start time window to consider.
        after: str, datetime.datetime or numpy.datetime64
            Stop time window to consider.
        by_event: AbstractEvent or AbstractEventsCollection
            Event(s) that can be used as an time window range.

        Returns
        -------
        AbstractEventsCollection
            Same events if the event is inside the time window considered.
        AbstractEventsCollection
            Trimmed events if the event cross one or both boundaries.
        None
            The events is outside the time window considered.

        """
        raise NotImplementedError


class EventsDict(AbstractEventsCollection, UserDict):
    """List of events items with different keys.

    Warning
    -------
    The iteration is performed on the values and not the dict keys.

    """

    def __init__(self, events, **kwargs):
        self.data = {}

        if isinstance(events, AbstractEvent):
            events = [events]

        for event in sorted(events, key=attrgetter('start')):
            self.append(event)

    def __str__(self):
        n_events = len(self)
        events = f'{n_events} key' + ('s' if n_events > 1 else '')

        if n_events > 0:
            events = f'({np_date_str(self.start)} -> {np_date_str(self.stop)} | {events})'

            events += '\n - '.join([':', *[str(event) for event in self]])

        return events

    def _repr_html_(self):
        rows = [
            [
                f'<em>{i}</em>',
                event.key,
                len(event) if isinstance(event, AbstractEventsCollection) else '-',
                event.start_date,
                event.stop_date,
            ]
            for i, event in enumerate(self)
        ]
        return table(rows, header=('', 'event', '#', 't_start', 't_stop'))

    def __iter__(self):
        return iter(self.data.values())

    def __getitem__(self, key):
        if isinstance(key, str) and key in self.keys():
            return self.data[key]

        if isinstance(key, int):
            return self.get_by_int(key)

        if isinstance(key, slice):
            return EventsDict(self.get_by_slice(key))

        if isinstance(key, tuple):
            return self.find(*key)

        return self.find(key)

    def _ipython_key_completions_(self):
        return self.keys()

    def __contains__(self, utc):
        if isinstance(utc, str) and utc in self.data.keys():  # noqa: SIM118 (__iter__ on values not keys)
            return True

        return super().__contains__(utc)

    def __hash__(self):
        return hash(frozenset(self.data.items()))

    def keys(self):
        """Dictionary keys."""
        return self.data.keys()

    def get_by_slice(self, key) -> list:
        """Get events by slice."""
        return list(self)[key]

    def get_by_int(self, key: int):
        """Get event by int."""
        if -len(self) <= key < len(self):
            return self.get_by_slice(key)

        raise IndexError('Event index out of range')

    def append(self, event):
        """Append a new event to the dict."""
        key = event.key

        if key not in self.keys():
            self.data[key] = event

        else:
            if not isinstance(self.data[key], EventsList):
                # Convert previous stored value into a new EventsList
                self.data[key] = EventsList([self.data[key]])

            self.data[key].append(event)

    def find(self, *regex, as_dict=False):
        """Find the events matching a regex expression.

        Parameters
        ----------
        *regex: str
            Search regex expression key(s).

        as_dict: bool, optional
            When a match exists returns the results as an ``EventsDict``.

        Returns
        -------
        Event, EventWindow, EventsList or EventsDict
            Event(s) matching the provided regex expression(s).

        Raises
        ------
        KeyError
            If none of the provided key was found.

        Note
        ----
        When multiple keys are provided, the duplicates
        will be discarded.

        """
        # Duplicates are removed with the list(set(...))
        res = list({
            event
            for expr in regex
            for key, event in self.data.items()
            if re.search(expr, key, flags=re.IGNORECASE)
        })

        if not res:
            raise KeyError(f'`{"`, `".join(regex)}` not found')

        return EventsDict(res) if as_dict or len(res) != 1 else res[0]

    def startswith(self, *keys, as_dict=False):
        """Find the events starting with a given key

        Parameters
        ----------
        *keys: str
            Search expression key(s).

        as_dict: bool, optional
            When a match exists returns the results as an ``EventsDict``.

        See Also
        --------
        find

        """
        return self.find(*[f'^{key}' for key in keys], as_dict=as_dict)

    def endswith(self, *keys, as_dict=False):
        """Find the events ending with a given key

        Parameters
        ----------
        *keys: str
            Search expression key(s).

        as_dict: bool, optional
            When a match exists returns the results as an ``EventsDict``.

        See Also
        --------
        find

        """
        return self.find(*[f'{key}$' for key in keys], as_dict=as_dict)

    def trim(self, *, before=None, after=None, by_event=None):
        """Trim the events dict within time boundaries.

        Parameters
        ----------
        before: str, datetime.datetime or numpy.datetime64
            Start time window to consider.
        after: str, datetime.datetime or numpy.datetime64
            Stop time window to consider.
        by_event: AbstractEvent or AbstractEventsCollection
            Event(s) that can be used as an time window range.

        Returns
        -------
        EventsDict
            Same events if the event is inside the time window considered.
        EventsDict
            Trimmed events if the event cross one or both boundaries.
        None
            The events is outside the time window considered.

        """
        events = [
            ev
            for event in self
            if (ev := event.trim(before=before, after=after, by_event=by_event))
        ]
        return EventsDict(events) if events else None


class EventsList(AbstractEventsCollection, UserList):
    """List of events with the same key."""

    def __str__(self):
        return f'{self.key} ({self.start_date} -> {self.stop_date} | {len(self)} events)'

    def __iter__(self):
        return iter(self.data)

    def _repr_html_(self):
        return table(
            [[f'<em>{i}</em>'] + list(event.values()) for i, event in enumerate(self)],
            header=('', *self[0]),
        )

    def __contains__(self, item):
        """Check datetime and secondary keys."""
        if isinstance(item, str):
            for keys in [self.crema_names, self.obs_names]:
                if item in keys:
                    return True

        return super().__contains__(item)

    def __getitem__(self, item):
        """Items can be queried by index or flyby crema name."""
        if isinstance(item, str):
            for keys in [self.crema_names, self.obs_names]:
                if item in keys:
                    return self[keys.index(item)]
            raise KeyError(item)

        if isinstance(item, slice):
            return EventsList(self.data[item])

        if isinstance(item, tuple):
            return EventsList([self[i] for i in item])

        return self.data[item]

    def _ipython_key_completions_(self):
        return self.crema_names + self.obs_names

    def __hash__(self):
        return hash(tuple(self.data))

    @property
    def key(self):
        """Events key."""
        return getattr(self[0], 'key', None)

    @property
    def crema_names(self) -> list:
        """Crema names when present in contextual info field."""
        return [name for item in self if (name := item.get('Crema name'))]

    @property
    def obs_names(self) -> list:
        """Observation names when present in contextual info field."""
        return [name for item in self if (name := item.get('observation name'))]

    def trim(self, *, before=None, after=None, by_event=None):
        """Trim the events list within time boundaries.

        Parameters
        ----------
        before: str, datetime.datetime or numpy.datetime64
            Start time window to consider.
        after: str, datetime.datetime or numpy.datetime64
            Stop time window to consider.
        by_event: AbstractEvent or AbstractEventsCollection
            Event(s) that can be used as an time window range.

        Returns
        -------
        EventsList
            Same events if the event is inside the time window considered.
        EventsList
            Trimmed events if the event cross one or both boundaries.
        None
            The events is outside the time window considered.

        """
        events = [
            ev
            for event in self
            if (ev := event.trim(before=before, after=after, by_event=by_event))
        ]
        return EventsList(events) if events else None


class AbstractEventsFile(EventsDict):
    """Abstract Events File object.

    Parameters
    ----------
    fname: str or pathlib.Path
        Input event filename.
    primary_key: str, optional
        Header primary key (default: `name`)
    header: str, optional
        Optional header definition (to be appended at the beginning of the file).


    """

    def __init__(self, fname, primary_key, header=None):
        super().__init__([])

        self.primary_key = primary_key.lower()
        self.header = header

        self.comments = []
        self.fields = []
        self.rows = []

        self.fname = fname

    def __str__(self):
        return self.fname.name

    def __repr__(self):
        events = super().__str__()
        return f'<{self.__class__.__name__}> {self} {events}'

    @property
    def fname(self):
        """Events filename."""
        return self.__fname

    @fname.setter
    def fname(self, fname):
        """Parse events file."""
        self.__fname = Path(fname)

        self._read_rows()
        self._parse_rows()

        # Check parsing validity
        try:
            _ = self.start_date
        except (KeyError, ValueError) as err:
            raise BufferError('Events parsing failed.') from err

    def _read_rows(self):
        """File row reader.

        This function need to feed the ``fields`` and ``rows``
        (and eventually the ``comments``) properties.

        Parameters
        ----------
        content: str
            File content to read.

        Returns
        -------
        list
            Columns fields.
        list
            Rows content split in columns.

        """
        raise NotImplementedError

    def _parse_rows(self):
        """Parse rows content as Events objects."""
        # Extract primary key values
        if self.primary_key not in self.fields:
            raise KeyError(f'Primary key `{self.primary_key}` not found')

        i = self.fields.index(self.primary_key)

        for row in self.rows:
            kwargs = dict(zip(self.fields, row, strict=False))
            key = row[i]
            k = key.upper()

            if k.endswith('_START') or k.endswith('_DESC'):
                key, _ = key.rsplit('_', 1)  # pop `_START` and `_DESC`

                start = kwargs.pop('event time [utc]')

                kwargs.update({
                    self.primary_key: key,
                    't_start': start,
                    't_end': 'NaT',
                })

            elif k.endswith('_END') or k.endswith('_ASCE'):
                key, _ = key.rsplit('_', 1)  # pop `_END` and `_ASCE`
                stop = kwargs['event time [utc]']

                if key not in self.keys():
                    missing = row[i].replace('_END', '_START').replace('_ASCE', '_DESC')
                    warn.warning(
                        'Found `%s` (at %s) without `%s`.', row[i], stop, missing
                    )
                    continue

                if isinstance(self.data[key], EventsList):
                    self.data[key][-1]['t_end'] = stop
                else:
                    self.data[key]['t_end'] = stop

                continue  # Go to the next row

            self.append(AbstractEvent(key, **kwargs))
