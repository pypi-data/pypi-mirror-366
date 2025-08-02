"""Events csv file module."""

from .event import AbstractEventsFile
from ..html import Html, table


class CsvEventsFile(AbstractEventsFile):
    """CSV events file object.

    Parameters
    ----------
    fname: str or pathlib.Path
        Input CSV event filename.
    primary_key: str, optional
        Header primary key (default: `name`)
    header: str, optional
        Optional header definition (to be appended at the beginning of the file).

    .. versionadded:: 1.2.0
       CSV reader now support uncommented header.

    """

    fields, rows = [], []

    def __init__(self, fname, primary_key='name', header=None):
        super().__init__(fname, primary_key, header)

    def __getitem__(self, key):
        if isinstance(key, str) and key.lower() in self.fields:
            i = self.fields.index(key.lower())
            return [row[i] for row in self.rows]

        return super().__getitem__(key)

    def _ipython_key_completions_(self):
        return list(self.keys()) + self.fields

    def _read_rows(self):
        """Read CSV rows content.

        By default, the content of the file is expected to have a description
        header at it's first line if no explicit header is provided in ``__init__``.

        All other the following lines commented or empty will be discarded.

        """
        content = self.fname.read_text(encoding='utf-8')

        if self.header:
            header, lines = self.header, content.splitlines()
        else:
            header, *lines = content.splitlines()

        # Parse header columns
        self.fields = [
            field.lower().strip() if field else f'column_{i}'
            for i, field in enumerate(header.lstrip('# ').split(','))
        ]

        # Strip rows content
        self.rows = [
            tuple(value.strip() for value in line.split(','))
            for line in lines
            # Remove commented and empty lines
            if not line.startswith('#') and line.strip()
        ]

    @property
    def csv(self):
        """Formatted CSV content."""
        return Html(table(self.rows, header=self.fields))
