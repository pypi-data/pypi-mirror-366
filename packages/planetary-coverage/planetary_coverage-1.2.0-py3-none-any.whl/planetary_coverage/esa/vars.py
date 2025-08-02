"""ESA variables."""

from pathlib import Path


ESA_MK_CACHE = Path.home() / '.planetary-coverage' / 'esa-mk'

ESA_MK_CACHE.mkdir(exist_ok=True, parents=True)
