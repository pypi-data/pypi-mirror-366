"""HTML formatter module."""

from collections import UserDict

import numpy as np


NDIM_2D = 2  # 2D data


def tag(tag, content=None, **kwargs):
    """HTML tag with a content."""
    attrs = ''.join([f' {key}="{value}"' for key, value in kwargs.items()])
    return f'<{tag}{attrs}/>' if content is None else f'<{tag}{attrs}>{content}</{tag}>'


def table(data, header=None, **kwargs):
    """Create HTML table from data."""
    if isinstance(data, (dict, UserDict)):
        return table(np.transpose(list(data.values())), header=tuple(data))

    if header:
        content = tag('thead', _rows(header, cell='th'))
        content += tag('tbody', _rows(data))

    else:
        content = _rows(data)

    return tag('table', content, **kwargs)


def _rows(data, cell='td'):
    """Create table content from an iterable."""
    if np.ndim(data) == 0:
        return tag('tr', tag(cell, data))

    if np.ndim(data) == 1:
        data = [data]

    if np.ndim(data) == NDIM_2D:
        return ''.join([tag('tr', _cells(values, cell=cell)) for values in data])

    raise TypeError(f'Invalid input: {data}')


def _cells(data, cell='td'):
    """Create table cells from an iterable."""
    return ''.join([tag(cell, value) for value in data])


class Html:
    """HTML object to display in Jupyter."""

    def __init__(self, html):
        self.html = html

    def _repr_html_(self):
        return self.html


def display_html(obj):
    """Display object in HTML."""
    return obj._repr_html_()
