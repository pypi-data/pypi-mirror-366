"""
Context object for Pakto CLI.
"""

from pathlib import Path
from typing import Optional

from ..security.keys import KeyStore
from ..services.config import ConfigService, get_config_service

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "max_content_width": 120,
    "auto_envvar_prefix": "PAKTO",
}


class AppContext:
    """
    Context object for Pakto CLI.

    This class holds the configuration and state for the CLI commands.
    It is passed around to commands to access shared resources like config.
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        verbosity: int = 0,
        calling_dir: Optional[Path] = None,
    ):
        self.verbosity = verbosity
        self.config_service: ConfigService = get_config_service(config_path)
        self.config_service.load()
        self.calling_dir = calling_dir or Path.cwd()
        self.keystore = KeyStore(Path(self.config_service.get("keys_dir")))
