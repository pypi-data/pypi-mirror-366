"""Miscellaneous list toolbox module."""

from operator import indexOf


def rindex(lst, value):
    """Search the last index reference of a value in a list.

    Solution from Stackoverflow: https://stackoverflow.com/a/63834895

    """
    return len(lst) - indexOf(reversed(lst), value) - 1


def group_by_2(lst):
    """Group list as start/stop lists of size 2."""
    return [[start, stop] for start, stop in zip(lst[::2], lst[1::2], strict=False)]
