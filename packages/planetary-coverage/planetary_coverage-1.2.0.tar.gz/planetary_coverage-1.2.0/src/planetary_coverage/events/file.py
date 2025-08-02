"""Generic Events file reader module."""

from pathlib import Path

from .csv import CsvEventsFile
from .evf import EvfEventsFile
from .itl import ItlEventsFile
from .orb import OrbitEventsFile


def read_events(fname, **kwargs):
    """Read events file.

    Parameters
    ----------
    fname: str or pathlib.Path
        File name to parse
    **kwargs:
        Parsing properties.

    Returns
    -------
    CsvEventFile, EvfEventFile, ItlEventFile or OrbitEventsFile
        Parsed events list from the provided file.

    Raises
    ------
    FileNotFoundError
        If the filename provided does not exist.
    BufferError
        When it's not possible to parse the provided file.

    Note
    ----
    The function will try to guess the layout of the file based on
    the filename extension.

    See Also
    --------
    planetary_coverage.events.CsvEventsFile
    planetary_coverage.events.EvfEventsFile
    planetary_coverage.events.ItlEventsFile
    planetary_coverage.events.OrbitEventsFile

    """
    fname = Path(fname)

    if not fname.exists():
        raise FileNotFoundError(fname)

    ext = fname.suffix.lower()

    if ext == '.orb':
        return OrbitEventsFile(fname)

    if ext == '.evf':
        return EvfEventsFile(fname)

    if ext == '.itl':
        return ItlEventsFile(fname, evf=kwargs.get('evf'))

    if kwargs:
        return CsvEventsFile(fname, **kwargs)

    csv_kwargs = [
        # mission_phases.csv
        {'primary_key': 'Name'},
        # mission_timeline.csv
        {'primary_key': 'Event Name'},
        # opl_events.csv
        {'primary_key': 'type'},
        # mission_events.csv
        {
            'primary_key': 'name',
            'header': '# name, t_start, t_end, subgroup, working_group',
        },
    ]

    for _kwargs in csv_kwargs:
        try:
            return CsvEventsFile(fname, **_kwargs)
        except (KeyError, ValueError, BufferError):
            pass

    raise BufferError(f'Impossible to parse the events in: {fname}')
