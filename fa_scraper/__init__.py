try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # type: ignore

from .types import UserId, Lang, FACategory
from .fa_scraper import get_profile_data

__version__ = importlib_metadata.version(__name__)
