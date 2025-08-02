"""GeoJson ROI module."""

from json import loads
from pathlib import Path as PathFile

from matplotlib.path import Path

from .rois import ROI


class GeoJsonROI(ROI):
    """GeoJson ROI object.

    Parameters
    ----------
    key: str
        Identification key.
    geojson: str, pathlib.Path
        GeoJson file.
    **kwargs: str, optional
        Region attribute.

    Note
    ----
    Only a limited number of `geojson` types are
    supported at the moment: ``FeatureCollection``,
    ``Feature`` and ``Polygon``.

    """

    def __init__(self, key, geojson, **kwargs):
        super().__init__(key, lons_e=None, lats=None, **kwargs)

        # Remove `lons_e` and `lats` attributes
        delattr(self, 'lons_e')
        delattr(self, 'lats')

        del self._attrs['lons_e']
        del self._attrs['lats']

        self.geojson = geojson

    @property
    def vertices(self):
        """ROI vertices."""
        return self.__vertices

    @vertices.setter
    def vertices(self, vertices):
        """ROI vertices setter."""
        self.__vertices = vertices

    @property
    def codes(self):
        """ROI path codes."""
        return self.__codes

    @codes.setter
    def codes(self, codes):
        """ROI path codes setter."""
        self.__codes = codes

    @property
    def geojson(self):
        """GeoJson file."""
        return self.__geojson

    @geojson.setter
    def geojson(self, geojson):
        """GeoJson file setter."""
        self.__geojson = PathFile(geojson)

        json = loads(self.geojson.read_text())
        self.load_geojson(json)

    def load_geojson(self, json):
        """Load GeoJson content."""
        if json['type'] == 'FeatureCollection':
            self._load_feature_collection(json)

        elif json['type'] == 'Feature':
            self._load_feature(json)

        elif json['type'] == 'Polygon':
            self._load_geometry(json)

        else:
            raise NotImplementedError(f'Type: `{json["type"]}`')

    def _load_feature_collection(self, json):
        """Load GeoJson feature collection."""
        if 'features' not in json:
            raise ValueError('The geojson is invalid: `features` key is missing.')

        if not json['features']:
            raise ValueError('No features found.')

        if len(json['features']) > 1:
            raise NotImplementedError('No many features. Only 1 is supported.')

        self._load_feature(json['features'][0])

    def _load_feature(self, json):
        """Load GeoJson feature."""
        if 'geometry' not in json:
            raise ValueError('The geojson is invalid: `geometry` key is missing.')

        self._load_geometry(json['geometry'])

        if 'properties' in json:
            self._attrs.update(json['properties'])
            for key, value in json['properties'].items():
                setattr(self, key, value)

    def _load_geometry(self, json):
        """Load GeoJson geometry."""
        if json['type'] != 'Polygon':
            raise NotImplementedError(
                f'Invalid type: `{json["type"]}` (only the Polygon is supported)'
            )

        if 'coordinates' not in json:
            raise ValueError('The geojson is invalid: `coordinates` key is missing.')

        self._load_coordinates(json['coordinates'])

    def _load_coordinates(self, polygons):
        """Load GeoJson coordinates."""
        if not isinstance(polygons, list):
            raise ValueError('The geojson is invalid: `coordinates` value is not a list.')

        vertices, codes = [], []
        for polygon in polygons:
            for lon_e, lat in polygon:
                vertices.append((lon_e, lat))

            npts = len(polygon)
            codes += [Path.MOVETO] + (npts - 2) * [Path.LINETO] + [Path.CLOSEPOLY]

        self.vertices = vertices
        self.codes = codes
