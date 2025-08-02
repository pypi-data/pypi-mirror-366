"""Miscellaneous logger module."""

import logging
import sys


class InfoFilter(logging.Filter):
    """Filter only record with level INFO."""

    @staticmethod
    def filter(record):
        return record.levelno == logging.INFO


class NotInfoFilter(logging.Filter):
    """Filter only record not with level INFO."""

    @staticmethod
    def filter(record):
        return record.levelno != logging.INFO


def logger(name, info_stdout=False):
    """Create a custom logger with its debugger."""
    snake_name = name.replace(' ', '_').lower()
    logger = logging.getLogger(f'{__package__}.{snake_name}')

    if logger.hasHandlers():
        logger.handlers.clear()

    stderr = logging.StreamHandler()
    logger.addHandler(stderr)

    fmt = logging.Formatter(f'[{name}] %(message)s')
    stderr.setFormatter(fmt)

    if info_stdout:
        stdout = logging.StreamHandler(sys.stdout)
        stdout.setLevel(logging.INFO)
        stdout.setFormatter(fmt)
        logger.addHandler(stdout)

        # Filter INFO to send them to stdout
        stdout.addFilter(InfoFilter())
        stderr.addFilter(NotInfoFilter())
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    return logger, debug(logger, default=logger.level)


def debug(logger, default=logging.WARNING):
    """Custom debug toggler."""

    def _debug(enabled=True):
        """Change logger level."""
        if enabled == 'info':
            logger.setLevel(logging.INFO)
        elif enabled == 'warning':
            logger.setLevel(logging.WARNING)
        elif enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(default)

        logger.info('Change logger level to %s', logging.getLevelName(logger.level))

    return _debug
