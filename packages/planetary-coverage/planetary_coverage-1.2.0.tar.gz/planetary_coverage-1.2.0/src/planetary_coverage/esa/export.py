"""ESA export functions."""

import datetime
from collections import Counter
from json import dumps
from pathlib import Path

import numpy as np

from ..rois import ROI, ROIsCollection
from ..spice import iso, mapps_datetime, sorted_datetimes


def extract_segments(traj, roi=None, subgroup='', source='GENERIC'):
    """Extract trajectory and ROI(s) intersection segments windows.

    Segment format:

    ``[NAME, START_TIME, STOP_TIME, SUBGROUP, SOURCE]``

    Parameters
    ----------
    traj: Trajectory or MaskedTrajectory
        Trajectory to segment.
    roi: ROI or ROIsCollection, optional
        ROI or ROIsCollection to use to intersect the trajectory (default: None).
    subgroup: str, optional
        Subgroup keyword (default: ``<EMPTY>``).
    source: str, optional
        Source / working group entry (default: ``GENERIC``).

    Returns
    -------
    list
        List of segments.

    Raises
    ------
    TypeError
        If the input ``roi`` is not ``None``, a ``ROI`` nor a ``ROIsCollection``.

    Note
    ----
    - The ``NAME`` keyword is set to ``TRAJECTORY_SEGMENT`` if only a
      single trajectory is provided or ``ROI_INTERSECTION`` if a ROI or
      a ROIsCollection is provided.

    - ``START`` and ``STOP`` times are return as ISO format: ``2032-07-08T15:53:52.350Z``

    - The ``SUBGROUP`` is optional. If no ``subgroup`` is provided,
      the ROI key intersected will be used if available.

    - The ``SOURCE`` can be empty.

    - The output events are chronologically ordered by start time.
      If 2 events starts at the same time, the first one in the list will
      be the one with the shortest duration.

    See Also
    --------
    juice_timeline

    """
    segments = []

    # Trajectory only
    if roi is None:
        for segment in traj:
            segments.append([
                'TRAJECTORY_SEGMENT',
                iso(segment.start),
                iso(segment.stop),
                subgroup,
                source,
            ])

    # Trajectory and ROI intersection
    elif isinstance(roi, ROI):
        for traj_in_roi in traj & roi:
            segments.append([
                'ROI_INTERSECTION',
                iso(traj_in_roi.start),
                iso(traj_in_roi.stop),
                subgroup if subgroup else str(roi),
                source,
            ])

    # Trajectory and ROIsCollection intersection
    elif isinstance(roi, ROIsCollection):
        for current_roi in roi & traj:
            for traj_in_roi in traj & current_roi:
                segments.append([
                    'ROI_INTERSECTION',
                    iso(traj_in_roi.start),
                    iso(traj_in_roi.stop),
                    subgroup if subgroup else str(current_roi),
                    source,
                ])

    else:
        raise TypeError('Input `roi` must be a `None`, a `ROI` or a `ROIsCollection`.')

    # Sort segments by start time
    return sorted_datetimes(segments, index=(1, 2))


def export_timeline(
    fname, traj, roi=None, subgroup='', source='GENERIC', crema='CREMA_5_0'
):
    """Export a trajectory and ROI(s) intersection segments.

    CSV and JSON files are natively compatible with the Juice timeline tool:

    .. code-block:: text

        https://juicesoc.esac.esa.int/tm/?trajectory=CREMA_5_0

    EVF files can be used in MAPPS.

    Parameters
    ----------
    fname: str or pathlib.Path
        Output filename. Currently, only ``.json`` and ``.csv`` are supported.
        If you only need the intersection windows as a list you can force
        the ``fname`` to be set to ``None``.
    traj: Trajectory or MaskedTrajectory
        Trajectory to segment.
    roi: ROI or ROIsCollection, optional
        ROI or ROIsCollection to use to intersect the trajectory (default: None).
    subgroup: str, optional
        Subgroup keyword (default: ``<EMPTY>``).
    source: str, optional
        Source / working group entry (default: ``GENERIC``).
    crema: str, optional
        Input CReMA key (only used for JSON output).

    Returns
    -------
    pathlib.Path
        Output filename.

    Raises
    ------
    ValueError
        If the provided filename does not end with ``.json``, ``.csv`` or ``.evf``.

    See Also
    --------
    extract_segments
    format_csv
    format_json
    format_evf

    """
    # Extract segments list: [[NAME, START_TIME, STOP_TIME, SUBGROUP, SOURCE], ...]
    segments = extract_segments(traj, roi, subgroup=subgroup, source=source)

    # Export in a output file
    fname = Path(fname)
    ext = fname.suffix.lower()

    if ext == '.csv':
        content = format_csv(segments)

    elif ext == '.json':
        content = format_json(
            segments, fname.stem, crema=crema, timeline='LOCAL', overwritten=False
        )

    elif ext == '.evf':
        content = format_evf(segments)

    else:
        raise ValueError('The output file must be a JSON or a CSV file.')

    fname.write_text(content, encoding='utf-8')

    return fname


def format_csv(segments, header='# name, t_start, t_end, subgroup, source'):
    """Format segments as a CSV string.

    Parameters
    ----------
    segments: list
        List of events as: ``[NAME, START_TIME, STOP_TIME, SUBGROUP, SOURCE]``
    header: str, optional
        Optional file header.

    Returns
    -------
    str
        Formatted CSV string.

    Note
    ----
    The delimiter is a comma character (``,``).

    """
    if header:
        segments = [header.split(', ')] + segments

    return '\n'.join([','.join(event) for event in segments])


def format_json(segments, fname, crema='CREMA_5_0', timeline='LOCAL', overwritten=False):
    """Format segments as a JSON string.

    Parameters
    ----------
    segments: list
        List of events as: ``[NAME, START_TIME, STOP_TIME, SUBGROUP, SOURCE]``
    crema: str, optional
        Top level ``crema`` keyword.
    timeline: str, optional
        Top level ``timeline`` keyword.
    overwritten: bool, optional
        Segment event ``overwritten`` keyword.

    Returns
    -------
    str
        Formatted JSON string.

    Note
    ----
    The ``SUBGROUP`` field is used to store the name that will be displayed in the
    Juice timeline tool. If none is provided, the ``NAME`` field will be used instead.

    """
    return dumps({
        'creationDate': iso(datetime.datetime.now()),
        'name': fname,
        'segments': [
            {
                'start': start,
                'end': stop,
                'segment_definition': name,
                'name': subgroup if subgroup else name,
                'overwritten': overwritten,
                'timeline': timeline,
                'source': source,
                'resources': [],
            }
            for name, start, stop, subgroup, source in segments
        ],
        'segmentGroups': [],
        'trajectory': crema,
        'localStoragePk': '',
    })


def format_evf(segments):
    """Format segments as a EVF string (for MAPPS).

    Parameters
    ----------
    segments: list
        List of events as: ``[NAME, START_TIME, STOP_TIME, SUBGROUP, SOURCE]``

    Returns
    -------
    str
        Formatted EVF string.

    Note
    ----
    - The ``SUBGROUP`` field is used as the main key.
      If none is provided, the ``NAME`` field will be used instead.

    - ``SOURCE`` field are not used in EVF formatting.

    """
    # Find the most common subgroup entry (to adjust the COUNT length)
    counter = Counter([subgroup for _, _, _, subgroup, _ in segments])

    n = int(np.log10(counter.most_common(1)[0][1])) + 1 if counter else ''

    # Split the time windows as START and END events
    elements, counter = [], Counter()
    for name, start, stop, subgroup, _ in segments:
        key = subgroup if subgroup else name
        counter[key] += 1

        elements.append([
            start,
            f'{mapps_datetime(start):24s}  {key}_START  (COUNT = {counter[key]:{n}d})',
        ])

        elements.append([
            stop,
            f'{mapps_datetime(stop):24s}  {key}_END    (COUNT = {counter[key]:{n}d})',
        ])

    # Sort the elements by time and add the header with the creation time
    now = mapps_datetime(datetime.datetime.now())
    lines = [f'# Events generated by the planetary-coverage on {now}']

    lines += [desc for _, desc in sorted_datetimes(elements, index=0)]

    return '\n'.join(lines)
