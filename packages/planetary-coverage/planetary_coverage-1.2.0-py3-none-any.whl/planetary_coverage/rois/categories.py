"""ROIs categories module."""

from .abstract import AbstractCollection, AbstractItem


class Category(AbstractItem):
    """ROI category.

    Parameters
    ----------
    key:
        Identification key.
    name: str, optional
        Category name.
    **kwargs: str, optional
        Region description/Science objective/Observation requirement/Color.

    """


class SubCategory(AbstractItem):
    """ROI sub-category.

    Parameters
    ----------
    key:
        Identification key.
    name: str, optional
        SubCategory name.
    category: planetary_coverage.rois.categories.Category
        Main category.
    **kwargs: str, optional
        Region description/Science objective/Observation requirement/Color.

    Raises
    ------
    AttributeError:
        If the :attr:`category` attribute is missing.

    """

    def __init__(self, key, name=None, category=None, **kwargs):
        if category is None or not isinstance(category, Category):
            raise AttributeError(f'Invalid category: `{category}`')

        super().__init__(key, name=name, **kwargs)
        self.category = category


class CategoriesCollection(AbstractCollection):
    """Categories collection."""

    ITEM = Category


class SubCategoriesCollection(AbstractCollection):
    """Sub-categories collection."""

    ITEM = SubCategory
