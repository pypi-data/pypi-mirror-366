"""KML ROI module."""

from collections import defaultdict
from defusedxml.ElementTree import XMLParser
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from .rois import ROIsCollectionWithCategories


def kml_tag(func):
    """KML clean tag decorator."""

    def wrapper(_self, tag, *args):
        """Clean tag from kml prefix."""
        key = tag.rsplit('}', 1)[-1] if tag.startswith('{') else tag
        return func(_self, key, *args)

    return wrapper


def strip_data(func):
    """KML data strip decorator"""

    def wrapper(_self, data):
        """Strip kml data."""
        _data = data.strip()
        return func(_self, _data) if _data else None

    return wrapper


class KmlParser:
    """KML parser."""

    GEOMETRIES = [
        'Point',
        'LineString',
        'LinearRing',
        'Polygon',
    ]

    PROPERTIES = {
        'drawOrder': ('zorder', int),
    }

    def __init__(self):
        self._tag = None
        self._style = None
        self._style_tag = None
        self._style_map = None
        self._style_map_normal = False
        self._folder = None
        self._placemark = None

        self.styles = {}
        self.styles_map = {}
        self.folders = []

    @kml_tag
    def start(self, tag, attrib):
        """Tag reader."""
        self._tag = tag

        if tag == 'Folder':
            self._folder = defaultdict(list)

        elif tag == 'Placemark':
            self._placemark = {}

        elif self._placemark is not None and tag in self.GEOMETRIES:
            self._placemark['geometry'] = tag

        elif tag == 'Style':
            self._style = {'id': '#' + attrib['id']}

        elif tag in {'LineStyle', 'PolyStyle'}:
            self._style_tag = tag

        elif tag == 'StyleMap':
            self._style_map = {'id': '#' + attrib['id']}

    @kml_tag
    def end(self, tag):
        """Tag closer."""
        if tag == 'Folder' and self._folder:
            self.folders.append(dict(self._folder))
            self._folder = None

        elif tag == 'Placemark' and self._placemark:
            if self._folder:
                self._folder['placemarks'].append(self._placemark)
            else:
                self.folders.append({
                    'name': self._placemark.get('name'),
                    'description': self._placemark.get('description'),
                    'placemarks': [dict(self._placemark)],
                })

            self._placemark = None

        elif tag == 'Style' and self._style:
            style_id = self._style.pop('id')
            self.styles[style_id] = dict(self._style)
            self._style = None

        elif tag in {'LineStyle', 'PolyStyle'}:
            self._style_tag = None

        elif tag == 'StyleMap' and self._style_map:
            self.styles_map[self._style_map['id']] = self._style_map['style']
            self._style_map = None

    @strip_data
    def data(self, data):
        """Tag parser."""
        if self._placemark is not None:
            if self._tag == 'coordinates':
                self._add_coordinates(data)
            elif self._tag == 'styleUrl' and data in self.styles_map:
                self._placemark.update(self.styles[self.styles_map[data]])
            elif self._tag in self.PROPERTIES:
                key, fmt = self.PROPERTIES[self._tag]
                self._placemark[key] = fmt(data)
            else:
                self._placemark[self._tag] = data

        elif self._folder is not None:
            self._folder[self._tag] = data

        elif self._style is not None:
            self._add_style(data)

        elif self._style_map is not None:
            if self._tag == 'key' and data == 'normal':
                self._style_map_normal = True

            elif self._style_map_normal and self._tag == 'styleUrl':
                self._style_map['style'] = data
                self._style_map_normal = False

    def _add_coordinates(self, data):
        """Parse coordinate and store them in the placemark."""
        is_line = self._placemark['geometry'] == 'LineString'

        lons_e, lats, alts = self.coordinates(data, line=is_line)

        self._placemark |= {
            'lons_e': lons_e,
            'lats': lats,
            'alts': alts,
        }

    def _add_style(self, data):
        """Parse style and store it in the style."""
        if self._style_tag == 'PolyStyle' and self._tag == 'color':
            self._style['facecolor'] = self.rgb(data)

        elif self._style_tag == 'LineStyle' and self._tag == 'color':
            self._style['edgecolor'] = self.rgb(data)

        elif self._style_tag == 'LineStyle' and self._tag == 'width':
            self._style['linewidth'] = int(data)

    @classmethod
    def coordinates(cls, data, line=False):
        """Parse KML coordinates."""
        if line:
            data = cls.coordinates(data, line=False)
            return np.hstack([data, data[..., ::-1]])

        return np.transpose([
            (float(lon_e) % 360, float(lat), float(alt))
            for coordinate in data.split()
            for lon_e, lat, alt in [coordinate.split(',')]
        ])

    @staticmethod
    def rgb(color):
        """Convert AaBbGgRr kml color to #RrGgBbAa code."""
        return '#' + ''.join([
            i + j for i, j in zip(color[-2::-2], color[::-2], strict=False)
        ])


def read_kml(filename):
    """Read KML file.

    Parameters
    ----------
    filename: str or pathlib.Path
        KML filename.

    Returns
    -------
    list
        KML folders contents.

    Raises
    ------
    FileNotFoundError
        If the provided file is missing.
    ValueError
        If the file is not a `.kml` file.

    """
    f = Path(filename)

    if not f.exists():
        raise FileNotFoundError(f)

    if not f.suffix.lower().endswith('.kml'):
        raise ValueError('Only `.kml` files are supported.')

    # Parse KML files
    kml = KmlParser()
    parser = XMLParser(target=kml)
    parser.feed(f.read_text(encoding='utf-8'))

    return kml.folders


def read_kmz(filename):
    """Read KMZ file.

    Parameters
    ----------
    filename: str or pathlib.Path
        KMZ filename.

    Returns
    -------
    list
        KMZ folders contents.

    Raises
    ------
    FileNotFoundError
        If the provided file is missing.
    ValueError
        If the file is not a `.kmz` file.

    """
    f = Path(filename)

    if not f.exists():
        raise FileNotFoundError(f)

    if not f.suffix.lower().endswith('.kmz'):
        raise ValueError('Only `.kmz` files are supported.')

    folders = []
    with ZipFile(f) as archive:
        for kml_file in archive.namelist():
            if kml_file.endswith('.kml'):
                # Extract KML file content
                content = archive.read(kml_file).decode(encoding='utf-8')

                # Parse KML files
                kml = KmlParser()
                parser = XMLParser(target=kml)
                parser.feed(content)

                folders.extend(kml.folders)

    return folders


class KmlROIsCollection(ROIsCollectionWithCategories):
    """KML ROIs collection object.

    Parameters
    ----------
    *kml: str or pathlib.Path
        KML or KMZ file(s) name.
    target: str, optional
        Target body name.

    """

    def __init__(self, *files, target=None):
        super().__init__()

        self.filenames = []
        self.target = str(target) if target else None

        for filename in files:
            self.load_data(filename)

    def load_data(self, filename):
        """Load KML/KMZ ROIs."""
        _, ext = str(filename).lower().rsplit('.', 1)

        reader = read_kmz if ext == 'kmz' else read_kml

        for folder in reader(filename):
            category = self._load_folder(folder, filename)

            for placemark in folder['placemarks']:
                self._load_placemark(placemark, category)

        self.filenames.append(filename)

    def _load_folder(self, folder, filename):
        """Add the folder content as a category."""
        key = folder['name']

        if key in self.categories.keys():  # noqa: SIM118 (__iter__ on values not keys)
            raise KeyError(f'Folder `{key}` must be unique.')

        attrs = {
            'name': key,
            'description': folder.get('description'),
            'filename': filename,
        }

        if self.target:
            attrs['target'] = self.target

        self.add_category(key, **attrs)

        return self.categories[key]

    def _load_placemark(self, placemark, category):
        """Add placemark content as a ROI."""
        key = f'({len(self) + 1:d}) {placemark["name"]}'

        attrs = dict(placemark)

        # Add category and target (if present)
        attrs['category'] = category

        if self.target:
            attrs['target'] = self.target

        self.add_roi(key, **attrs)
