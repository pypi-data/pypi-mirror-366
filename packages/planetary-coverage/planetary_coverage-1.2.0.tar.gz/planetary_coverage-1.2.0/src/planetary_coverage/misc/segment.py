"""Miscellaneous segment module."""

import numpy as np


class Segment:
    """Segments object on conditional list.

    Parameters
    ----------
    arr: numpy.ndarray
        Conditional list.

    """

    OUT = 0
    IN = 1
    START = 2
    STOP = 3
    SINGLE = 4

    def __init__(self, arr):
        cond = np.array([False, *arr, False], dtype=np.int64)

        self.codes = np.max(
            [np.zeros_like(arr), 4 * cond[1:-1] - cond[:-2] - 2 * cond[2:]], axis=0
        )

    def __repr__(self):
        return f'<{self.__class__.__name__}> {len(self)} ({len(self.codes)} npts)'

    def __len__(self):
        return int(np.sum(self.starts))

    def __iter__(self):
        return iter(self.slices)

    @property
    def starts(self):
        """Get segment starts."""
        return (self.codes == self.START) | self.singles

    @property
    def stops(self):
        """Get segment stops."""
        return (self.codes == self.STOP) | self.singles

    @property
    def singles(self):
        """Get segment isolated single points."""
        return self.codes == self.SINGLE

    @property
    def inside(self):
        """Get segment inside points."""
        return (self.codes == self.IN) | self.starts | self.stops

    @property
    def outside(self):
        """Get segment outside points."""
        return self.codes == self.OUT

    @property
    def istarts(self):
        """Segment starts indexes."""
        return np.argwhere(self.starts).ravel()

    @property
    def istops(self):
        """Segment stops indexes."""
        return np.argwhere(self.stops).ravel()

    @property
    def slices(self):
        """Segment slices."""
        for i, j in zip(self.istarts, self.istops, strict=False):
            yield slice(i, j + 1)
