import logging
from importlib.metadata import PackageNotFoundError, version

from .decorators import deprecated as deprecated
from .files import async_file_checksum as async_file_checksum
from .files import file_checksum as file_checksum

logger = logging.getLogger(__name__)


def get_app_version() -> str:
    """Get the current pakto version."""
    try:
        return version("pakto")
    except (ImportError, ModuleNotFoundError, PackageNotFoundError, Exception):
        logger.warning("Could not determine Pakto version, using 'unknown'")
        return "unknown"
