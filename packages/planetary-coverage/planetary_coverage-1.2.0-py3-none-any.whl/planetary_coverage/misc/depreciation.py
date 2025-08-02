"""Depreciation decorator."""

from functools import wraps
from inspect import getmro

from .logger import logger


warn, _ = logger('DepreciationWarning')


def depreciated(version, new_name=None):
    """Depreciation class decorator."""

    def wrapper(cls):
        """Depreciation class wrapper."""

        @wraps(cls, updated=())
        class Deprecation(cls):
            """Depreciation new class."""

            def __init__(self, *args, **kwargs):
                warn.warning(
                    '`%s` is depreciated. Use `%s` instead. ',
                    cls.__name__,
                    new_name if new_name else getmro(cls)[1].__name__,
                )

                super().__init__(*args, **kwargs)

        Deprecation.__doc__ = (
            '[Depreciated] '
            + cls.__doc__.strip()
            + f'\n\n.. deprecated:: {version}\n'
            + f'    `{cls.__name__}` is depreciated in favor of '
            + f'`{new_name if new_name else getmro(cls)[1].__name__}`.'
        )

        return Deprecation

    return wrapper


def depreciated_replaced(func):
    """Depreciation replaced function decorator."""

    @wraps(func)
    def wrapper(_self, *args, **kwargs):
        """Depreciation replaced function."""
        if not (func.__name__ == '__getattr__' and args and args[0].startswith('_')):
            warn.warning(
                '`%s` has been replaced by `%s`. ', _self.old_name, _self.new_name
            )

        return func(_self, *args, **kwargs)

    return wrapper


class DepreciationHelper:
    """Depreciation helper.

    Parameters
    ----------
    old_name: str
        Original object name.
    new_name: str
        New object name.
    new_target: object
        New object target.

    """

    def __init__(self, old_name, new_name, new_target):
        self.old_name = old_name
        self.new_name = new_name
        self.new_target = new_target

    @depreciated_replaced
    def __repr__(self):
        return repr(self.new_target)

    @depreciated_replaced
    def __call__(self, *args, **kwargs):
        return self.new_target(*args, **kwargs)

    @depreciated_replaced
    def __getitem__(self, item):
        return self.new_target[item]

    @depreciated_replaced
    def __getattr__(self, attr):
        return getattr(self.new_target, attr)

    @depreciated_replaced
    def __len__(self):
        return len(self.new_target)

    @depreciated_replaced
    def __iter__(self):
        return iter(self.new_target)

    @depreciated_replaced
    def __contains__(self, item):
        return item in self.new_target
