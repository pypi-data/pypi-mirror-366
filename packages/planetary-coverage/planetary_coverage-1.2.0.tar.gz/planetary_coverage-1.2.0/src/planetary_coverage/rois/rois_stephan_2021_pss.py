"""Stephan 2021 ROIs module."""

import re
from pathlib import Path

import numpy as np

from matplotlib.patches import Rectangle

from .rois import ROIsCollectionWithCategories


DATA = Path(__file__).parent / 'data'

KEY = re.compile(r'\d+_\d+_\d+')


class Stephan2021ROIsCollection(ROIsCollectionWithCategories):
    """Abstract ROIs collection from Stephan et al. 2021 - PSS.

    Source:
        - Stephan et al. (2021) PSS, doi: 10.1016/j.pss.2021.105324

    Parameters
    ----------
    csv: str or pathlib.Path
        ROIs CSV file name.
    prefix: str, optional
        ROI key prefix.

    """

    DOI = 'https://doi.org/10.1016/j.pss.2021.105324'

    INSTRUMENTS = (
        'UVS',
        'JANUS HR',
        'JANUS COLOR',
        'JANUS STEREO',
        'MAJIS',
        'SWI',
        'RIME',
        'GALA',
        'PEP/RPWI',
        'J-MAG',
    )

    def __init__(self, csv=None, prefix=None, target=None):
        super().__init__()

        if csv is None:
            raise AttributeError('Missing `csv` attribute')

        self.csv = Path(csv)

        if not self.csv.exists():
            raise FileNotFoundError(self.csv)

        self.prefix = prefix
        self.target = str(target)

        self.load_csv()

    def __contains__(self, key):
        return super().__contains__(self.key(key))

    def __getitem__(self, key):
        return super().__getitem__(self.key(key))

    @property
    def doi(self):
        """Stephan et al (2021) PSS doi."""
        return self.DOI

    def key(self, cat, subcat=None, roi=None) -> str:
        """ROI key pattern formatter.

        Pattern:

        - ``C`` for category.
        - ``C.S`` for sub-category.
        - ``PREFIX_C_S_RR`` for a full ROI description.

        with:

        - `C` the category.
        - `S` the sub-category.
        - `R` the ROI id.
        - `PREFIX` the ROI prefix.

        Parameters
        ----------
        cat: int or str
            Main category.
        subcat: int or str, optional
            Sub-category. If ``0`` the sub-category will be omitted.
        roi: int or str, optional
            The ROI id.

        Returns
        -------
        str
            Formatted key.

        """
        if isinstance(cat, tuple):
            return self.key(*cat)

        if hasattr(cat, 'lonlat'):
            return cat

        if str(cat).startswith('# '):
            cat = cat[2:]

        if subcat in {0, '0'}:
            subcat = None

        if str(roi).startswith('#'):
            roi = None

        if subcat is None and roi is None:
            if KEY.fullmatch(str(cat)):
                return f'{self.prefix}{cat}'

            return str(cat)

        if roi is None:
            return f'{cat}.{subcat}'

        if subcat is None:
            subcat = 0

        return f'{self.prefix}{cat}_{subcat}_{int(roi):02d}'

    def load_csv(self):  # noqa: PLR0914 (heterogeneous csv lines)
        """Load ROIs from a CSV file."""
        lines = self.csv.read_text(encoding='utf-8').splitlines()

        for line in lines[1:]:
            (
                cat,
                subcat,
                roi,
                name,
                lat,
                lon_e,
                min_lat,
                max_lat,
                min_lon_e,
                max_lon_e,
                desc,
                sc_rat,
                *inst_req,
            ) = (val.strip() for val in line.split(','))

            key = self.key(cat=cat, subcat=subcat, roi=roi)

            attrs = {
                'name': name,
                'description': desc,
                'science_rationale': sc_rat,
            }

            if cat.startswith('#'):
                if subcat == '0':
                    self.add_category(
                        key, **attrs, color=roi, target=self.target, doi=self.DOI
                    )
                else:
                    self.add_subcategory(
                        key,
                        **attrs,
                        category=cat[2:],
                        color=roi,
                        target=self.target,
                        doi=self.DOI,
                    )

            else:
                if subcat == '0':
                    category = self.categories[self.key(cat=cat)]
                    cat_attrs = {
                        'category': category,
                        'color': category.color,
                        'target': category.target,
                        'doi': self.DOI,
                    }
                else:
                    subcategory = self.subcategories[self.key(cat=cat, subcat=subcat)]
                    cat_attrs = {
                        'category': subcategory.category,
                        'subcategory': subcategory,
                        'color': subcategory.category.color,
                        'target': subcategory.category.target,
                        'doi': self.DOI,
                    }

                lons_e = np.array(
                    [min_lon_e, max_lon_e, max_lon_e, min_lon_e], dtype=float
                )
                lats = np.array([min_lat, min_lat, max_lat, max_lat], dtype=float)

                instruments = {
                    inst: req == '1'
                    for inst, req in zip(self.INSTRUMENTS, inst_req, strict=False)
                }

                self.add_roi(
                    key,
                    lons_e,
                    lats,
                    lon_e=float(lon_e),
                    lat=float(lat),
                    **attrs,
                    **instruments,
                    **cat_attrs,
                )

    @property
    def handles(self):
        """ROIs legend category handles."""
        categories = {
            int(roi.category.key): (roi.category.color, roi.category.name)
            for roi in self.rois
        }
        return [
            Rectangle((0, 0), 1, 1, color=color, label=label)
            for color, label in categories.values()
        ]


# Ganymede ROIs from Stephan et al., PSS (2021) - Tab. 2.
GanymedeROIs = Stephan2021ROIsCollection(
    csv=DATA / 'Ganymede_ROIs-Stephan_2021_PSS-Tab_SM1.csv',
    prefix='JUICE_ROI_GAN_',
    target='Ganymede',
)

# Callisto ROIs from Stephan et al., PSS (2021) - Tab. 3.
CallistoROIs = Stephan2021ROIsCollection(
    csv=DATA / 'Callisto_ROIs-Stephan_2021_PSS-Tab_SM2.csv',
    prefix='JUICE_ROI_CAL_',
    target='Callisto',
)
