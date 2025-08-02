"""Orbit number event file module."""

from .event import AbstractEventsFile, EventsList
from ..html import table


class OrbitEventsFile(AbstractEventsFile):
    """Orbit event file object.

    Parameters
    ----------
    fname: str or pathlib.Path
        ORB filename to parse.

    """

    def __init__(self, fname):
        super().__init__(fname, 'No.')  # primary_key='No.'

    def _repr_html_(self):
        return table([list(event.values()) for event in self], header=self.fields)

    def __getitem__(self, item):
        """Items can be queried orbit number.

        Note
        ----
        If a slice is provided, the 2nd argument (stop orbit)
        will be included in the query (if present and positive).

        """
        orbits = list(self.data.values())

        if isinstance(item, int):
            return orbits[self._index(item)]

        if isinstance(item, (tuple, list)):
            return EventsList([orbits[self._index(i)] for i in item])

        if isinstance(item, slice):
            start = self._index(item.start)
            stop = self._index(item.stop)

            if item.stop is not None:
                stop = (stop + 1) if stop != -1 else None

            return EventsList(orbits[slice(start, stop, item.step)])

        raise TypeError(
            'Only `int`, `tuple`, `list` and `slice` are accepted. '
            f'`{item.__class__.__name__}` provided.'
        )

    def _index(self, i):
        """Compute orbit index."""
        if i is None or i < 0:
            return i

        orbits = list(map(int, self.data.keys()))
        if i in orbits:
            return orbits.index(i)

        raise IndexError(
            f'{i} out of range. Orbit available: {orbits[0]} to {orbits[-1]}'
        )

    def _ipython_key_completions_(self):
        return list(map(int, self.keys()))

    def _read_rows(self):
        """Read orbit rows content."""
        content = self.fname.read_text(encoding='utf-8')

        # Orbit columns
        header, _, *lines = content.splitlines()  # skip the 2nd line

        # Parse header columns
        self.fields = [field.lower().strip() for field in header.split('  ') if field]

        # Extract orbit row values
        self.rows = [
            tuple(field.strip() for field in line.split('  ') if field) for line in lines
        ]
