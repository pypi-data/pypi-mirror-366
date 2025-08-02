"""Miscellaneous cache module."""

from .logger import logger


log_cache, debug_cache = logger('Cache Property')


def _get_registry(self):
    """Get object cache registry.

    Create a new register is not already exists
    and add clear cache function.

    """
    if not hasattr(self, '__cache_registry'):
        self.__cache_registry = {}
        self.clear_cache = lambda: _clear_cache(self)

        log_cache.debug('`__cache_registry` and `clear_cache()` were added')

    return getattr(self, '__cache_registry')


def _register(self, attr, parents):
    """Register a property and its parents."""
    register = _get_registry(self)
    register[attr] = parents

    log_cache.debug('`%s` parent(s) are registered in the cache', attr)


def _clear_cache(self):
    """Clear all the cached properties."""
    for key in _get_registry(self):
        delattr(self, key)

    delattr(self, '__cache_registry')
    delattr(self, 'clear_cache')

    log_cache.debug('`__cache_registry` and `clear_cache()` were removed')
    log_cache.info('The cache is now clean')


def _clear_children(self, attr):
    """Clear property children from the cache."""
    for key, parents in _get_registry(self).items():
        if (isinstance(parents, str) and attr == parents) or (
            isinstance(parents, (set, list, tuple)) and attr in parents
        ):
            delattr(self, key)


def cached_property(method=None, *, parent=None):
    """Cached class property decorator attribute.

    Can be used in the following forms:

    - ``@cached_property``
    - ``@cached_property()``
    - ``@cached_property(parent='my_parent')``
    - ``@cached_property(parent=('my_parent_1', ...))``
    - ``@cached_property(parent=['my_parent_1', ...])``
    - ``@cached_property(parent={'my_parent_1', ...})``

    Parameters
    ----------
    method: callable, optional
        Method to memoizes.
    parent: str or set or tuple or list
        List of parents cached properties, for garbage collection.

    Note
    ----
    To remove a single cached attributed, use the :py:func:`delattr`
    function or the ``del`` keyword. In that case, all the child
    cached property will also be cleared.

    To clear the cache globally on this object, use the
    :py:func:`clear_cache()` method.

    Warning
    -------
    This caching strategy is not thread-safe contrary to the functools
    method.

    """

    def decorator(method):
        attr = method.__name__
        prop = f'_{attr}_cached'

        def fget(self):
            try:
                value = getattr(self, prop)
                log_cache.info('`%s` is loaded from the cache', attr)

            except AttributeError:
                log_cache.info('`%s` is not in the cache', attr)

                # Load the value from the method
                value = method(self)
                log_cache.debug('`%s` value is %r', attr, value)

                # Cache the value
                setattr(self, prop, value)
                log_cache.info('`%s` is now saved in the cache', attr)

                # Register the attribute's parent(s)
                _register(self, attr, parent)

            return value

        def fdel(self):
            if hasattr(self, prop):
                delattr(self, prop)
                log_cache.info('`%s` was removed from the cache', attr)

                _clear_children(self, attr)

        doc = '[Cached] ' + method.__doc__

        return property(fget, fdel=fdel, doc=doc)

    return decorator(method) if callable(method) else decorator
