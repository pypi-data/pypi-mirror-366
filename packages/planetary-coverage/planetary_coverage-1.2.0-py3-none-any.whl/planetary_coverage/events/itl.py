"""ITL events file module."""

import re

from .event import AbstractEventsCollection, AbstractEventsFile
from .evf import EvfEventsFile
from ..html import table
from ..spice.datetime import np_datetime_str, timedelta


ITL_ROW = r'\s+(\w+)\s+(\w+|\*)\s+(\w+)(?:\s+\((\w+)=([\w\s\[\]]+)\))?'

ITL_ROW_DT = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?)Z?' + ITL_ROW)

ITL_ROW_EVF = re.compile(
    r'(\w+\s+\(COUNT\s+=\s+\d+\))\s+([+-]\d{2}:\d{2}:\d{2}(?:\.\d+)?)' + ITL_ROW
)


def itl_rows(content):
    """Read ITL content to extract comments and data."""
    comments = []
    rows = []
    for line in content.splitlines():
        if line.startswith('# ') or line.startswith('#\t'):
            # Block comment
            comments.append(line[2:].replace(';', ',').replace('=', '＝'))
            continue

        if line.startswith('#') or not line.strip():
            # Commented line (skipped)
            continue

        if match := ITL_ROW_DT.findall(line):
            dt, inst, event_type, name, key, value = match[0]

            context_info = f'instrument={inst}'

            if event_type == '*':
                event_type = name
            else:
                context_info += f';observation name={name}'

            if key and value:
                context_info += f';{key.lower()}={value.lower()}'

            context_info += ';comments=' + ('\n'.join(comments) if comments else '--')

            rows.append((event_type, dt, context_info))

        elif match := ITL_ROW_EVF.findall(line):
            ref, td, inst, event_type, name, key, value = match[0]

            context_info = f'instrument={inst}'

            if event_type == '*':
                event_type = name
            else:
                context_info += f';observation name={name}'

            if key and value:
                context_info += f';{key.lower()}={value.lower()}'

            context_info += ';comments=' + ('\n'.join(comments) if comments else '--')

            rows.append((event_type, (ref, td), context_info))

        comments = []

    return rows


class ItlEventsFile(AbstractEventsFile):
    """ITL event file object.

    Instrument timeline.

    Parameters
    ----------
    fname: str or pathlib.Path
        ITL filename to parse.
    evf: str or pathlib.Path
        Supporting EVF events file (for relative timelines).

    """

    def __init__(self, fname, evf=None):
        self.evf = EvfEventsFile(evf) if evf else {}

        super().__init__(fname, 'event')  # primary_key='event'

    def _repr_html_(self):
        rows = [
            [
                event.key,
                len(event) if isinstance(event, AbstractEventsCollection) else '-',
                event.start_date,
                event.stop_date,
            ]
            for event in self
        ]
        return table(rows, header=('event', '#', 't_start', 't_stop'))

    def __contains__(self, key):
        if key in self.observations:
            return True

        return super().__contains__(key)

    def __getitem__(self, key):
        if key in self.observations:
            return self.observations[key]

        return super().__getitem__(key)

    def _ipython_key_completions_(self):
        return list(self.keys()) + self.observations.obs_names

    def _read_rows(self):
        """Read ITL rows content."""
        content = self.fname.read_text(encoding='utf-8')

        # ITL columns
        self.fields = ['event', 'event time [utc]', 'contextual info']

        # Extract rows and reconstruct relative timeline events
        self.rows = [
            (name, self.datetime(time), context)
            for (name, time, context) in itl_rows(content)
        ]

    def datetime(self, time):
        """Absolute datetime for an event."""
        if not isinstance(time, tuple):
            return time

        ref, delta = time

        if not self.evf:
            raise FileNotFoundError(f'Missing supporting EVF file: `{ref}` is unknown.')

        if ref not in self.evf:
            raise KeyError(f'`{ref}` is unknown.')

        return np_datetime_str(self.evf[ref] + timedelta(delta))

    @property
    def observations(self):
        """List of observation windows."""
        return self.data['OBS']
