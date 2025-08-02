"""Configuration service for managing config lifecycle."""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Set

import click
import yaml

from pakto.core.config import Config
from pakto.core.constants import DEFAULTS, DIRS, ENV
from pakto.services.validation import SchemaValidationService


class ConfigService:
    """Simple configuration service that loads config with validation.

    Loads configuration from file, environment variables, and defaults,
    with automatic schema validation through the validation service.
    """

    def __init__(
        self,
        config_file: Optional[Path] = None,
        validation_service: Optional[SchemaValidationService] = None,
    ):
        """Initialize config service.

        Args:
            config_file: Explicit config file path (from --config flag)
            validation_service: Validation service for schema validation
        """
        self._validation_service = validation_service or SchemaValidationService()
        self._config_file = config_file
        self._config_data = self._load_config()
        self._runtime_overrides: Dict[str, Any] = {}
        self.config_path = self._find_config_file()

    @property
    def config_file(self) -> Optional[Path]:
        """Return the path to the loaded config file."""
        return self.config_path

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value with precedence: Runtime > ENV > File > Default.

        Args:
            key: Configuration key (e.g., 'cache_dir', 'registry.default')
            default: Default value if not found elsewhere

        Returns:
            Resolved configuration value
        """
        # 0. Check runtime overrides (from set())
        if key in self._runtime_overrides:
            return self._runtime_overrides[key]

        # 1. Check environment variables
        env_value = self._get_from_env(key)
        if env_value is not None:
            return env_value

        # 2. Check config file
        file_value = self._get_from_config(key)
        if file_value is not None:
            return file_value

        # 3. Return provided default or built-in default
        return default if default is not None else self._get_builtin_default(key)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value and save it to the config file."""
        config_path = self._find_config_file()
        if not config_path:
            # If no config file exists, create one at the default user location
            config_path = DIRS.config / DEFAULTS.CONFIG_FILENAME
            if not click.confirm(
                f"No config file found. Create one at '{config_path}'?",
                default=True,
            ):
                click.echo("Config set aborted.")
                return
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

        # Load existing config or initialize an empty dict
        with config_path.open("r") as f:
            config_data = yaml.safe_load(f) or {}

        # Update the value
        keys = key.split(".")
        d = config_data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

        # Write the updated config back to the file
        with config_path.open("w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, sort_keys=False)

        click.echo(f"Updated '{key}' in {config_path}")

        # Reload the in-memory config to reflect the change
        self.load(config_path)

    def list(self) -> Dict[str, Any]:
        """List all configuration values with resolved precedence.

        Returns:
            Dictionary of all configuration keys and their resolved values
        """
        all_keys = set()

        # Collect all possible keys
        # all_keys.update(self._get_env_keys())
        # all_keys.update(self._get_config_keys())
        # all_keys.update(self._get_default_keys())
        # all_keys.update(self._runtime_overrides.keys())

        # old way
        all_keys.update(self._get_env_keys())
        all_keys.update(self._get_config_keys())
        all_keys.update(self._get_default_keys())
        all_keys.update(self._runtime_overrides.keys())

        # Build resolved config
        resolved = {}
        for key in sorted(all_keys):
            value = self.get(key)
            if value is not None:
                resolved[key] = value

        # Filter out parent keys that have nested values
        keys_to_remove = set()
        for key in resolved:
            if isinstance(resolved[key], dict):
                keys_to_remove.add(key)

        for key in keys_to_remove:
            del resolved[key]

        return resolved

    @property
    def config(self) -> Config:
        """Get the config object as a Pydantic model."""
        config_data = self.list()
        return Config(**config_data)

    def load(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from file (CLI compatibility method).

        Args:
            config_path: Path to config file (optional)
        """
        if config_path:
            self._config_file = config_path
        self._config_data = self._load_config()

    def _load_config(self, config_file: Optional[Path] = None) -> dict:
        """Load configuration from file with validation.

        Args:
            config_file: Optional explicit config file path

        Returns:
            Loaded and validated config data

        Raises:
            SchemaValidationError: If config file is invalid
        """
        # Start with defaults from schema
        config_data = self._get_default_config()

        # Load from file if specified or check default location
        config_path = config_file or self._find_config_file()
        if config_path and config_path.exists():
            with config_path.open(encoding="utf-8") as f:
                file_data = yaml.safe_load(f) or {}
                # Merge file data with defaults (file takes precedence)
                config_data.update(file_data)

        # Validate the complete config data
        self._validation_service.validate_config(config_data)

        return config_data

    def _get_default_config(self) -> dict:
        """Get default configuration from JSON schema with XDG-aware paths."""
        schema = self._validation_service._load_schema(
            "config.json", DEFAULTS.SCHEMA_VERSION
        )

        def extract_nested_defaults(schema_node):
            if "default" in schema_node:
                return schema_node["default"]
            if "properties" in schema_node:
                result = {}
                for key, subschema in schema_node["properties"].items():
                    value = extract_nested_defaults(subschema)
                    if value is not None:
                        result[key] = value
                return result if result else None
            return None

        config = extract_nested_defaults(schema) or {}

        # Add required fields for config schema
        config[DEFAULTS.SCHEMA_VERSION_KEY] = DEFAULTS.SCHEMA_VERSION_VALUE
        config[DEFAULTS.SCHEMA_KIND_KEY] = DEFAULTS.SCHEMA_KIND_VALUE

        # Override path defaults with XDG-aware values
        if "paths" not in config:
            config["paths"] = {}

        # Set XDG-aware path defaults
        data_dir = self._get_xdg_path("XDG_DATA_HOME", "~/.local/share/pakto")
        config["paths"]["data_dir"] = data_dir
        config["paths"]["cache_dir"] = str(Path(data_dir) / "cache")
        config["paths"]["config_dir"] = self._get_xdg_path(
            "XDG_CONFIG_HOME", "~/.config/pakto"
        )
        config["paths"]["log_dir"] = self._get_xdg_path(
            "XDG_STATE_HOME", "~/.local/state/pakto"
        )
        config["paths"]["keys_dir"] = str(DIRS.keys)
        return config

    def _get_xdg_path(self, xdg_var: str, fallback: str) -> str:
        """Get XDG-aware path with fallback."""
        xdg_value = os.environ.get(xdg_var)
        if xdg_value:
            return str(Path(xdg_value) / "pakto")
        return str(Path(fallback).expanduser())

    def _find_config_file(self) -> Optional[Path]:
        """Find config file in order: explicit > system > user."""
        # 1. Explicit path from constructor
        if self._config_file and self._config_file.exists():
            return self._config_file

        # 2. Check standard locations
        search_paths = [
            DIRS.config / DEFAULTS.CONFIG_FILENAME,
        ]

        for path in search_paths:
            if path.exists():
                return path

        # If it doesn't exist, create a default config file
        default_config_path = DIRS.config / DEFAULTS.CONFIG_FILENAME
        if not default_config_path.exists():
            default_config_path.parent.mkdir(parents=True, exist_ok=True)
            with default_config_path.open("w") as f:
                yaml.safe_dump(self._get_default_config(), f, default_flow_style=False)
            return default_config_path
        return None

    def _get_from_env(self, key: str) -> Optional[Any]:
        """Check environment variables."""
        env_mapping = {
            "cache_dir": ENV.CACHE_DIR,
            "data_dir": ENV.DATA_DIR,
            "log_dir": ENV.LOG_DIR,
            "config_dir": ENV.CONFIG_DIR,
            "keys_dir": ENV.KEYS_DIR,
            "registry.url": ENV.REGISTRY_URL,
            "registry.username": ENV.REGISTRY_USERNAME,
            "registry.password": ENV.REGISTRY_PASSWORD,
            "registry.default": ENV.REGISTRY_DEFAULT,
            "sbom.enabled": ENV.SBOM_ENABLED,
            "sbom.format": ENV.SBOM_FORMAT,
        }

        # 1. Check for PAKTO_ prefixed environment variables first
        env_var = env_mapping.get(key)
        if env_var and (value := os.environ.get(env_var)):
            # Convert booleans
            if key == "sbom.enabled":
                return value.lower() in ("true", "1", "yes", "on")
            # Return string values for paths (tests expect strings)
            return value

        # 2. If not found, check XDG environment variables for path-related keys
        if key == "paths.data_dir":
            return self._get_xdg_path("XDG_DATA_HOME", "~/.local/share/pakto")
        if key == "paths.config_dir":
            return self._get_xdg_path("XDG_CONFIG_HOME", "~/.config/pakto")
        if key == "paths.log_dir":
            return self._get_xdg_path("XDG_STATE_HOME", "~/.local/state/pakto")
        if key == "paths.cache_dir":
            # Cache dir is derived from data_dir, so we need to get data_dir first
            data_home = self._get_xdg_path("XDG_DATA_HOME", "~/.local/share/pakto")
            return str(Path(data_home) / "cache")
        if key == "paths.keys_dir":
            # Keys dir is derived from config_dir
            config_home = self._get_xdg_path("XDG_CONFIG_HOME", "~/.config/pakto")
            return str(Path(config_home) / "keys")

        return None

    def _get_from_config(self, key: str) -> Optional[Any]:
        """Get value from loaded config file."""
        parts = key.split(".")
        value = self._config_data

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value

    def _get_builtin_default(self, key: str) -> Any:
        """Get built-in defaults from constants."""
        defaults = {
            "cache_dir": str(DIRS.cache),
            "data_dir": str(DIRS.data),
            "config_dir": str(DIRS.config),
            "log_dir": str(DIRS.log),
            "keys_dir": str(DIRS.keys),
            "registry.default": DEFAULTS.DEFAULT_REGISTRY,
            "registry.default_tag": DEFAULTS.DEFAULT_TAG,
            "sbom.enabled": False,
            "sbom.format": "spdx",
        }
        return defaults.get(key)

    def _get_env_keys(self) -> Set[str]:
        """Get all configuration keys that have environment variables set."""
        keys = set()
        env_mapping = {
            "cache_dir": ENV.CACHE_DIR,
            "data_dir": ENV.DATA_DIR,
            "log_dir": ENV.LOG_DIR,
            "config_dir": ENV.CONFIG_DIR,
            "keys_dir": ENV.KEYS_DIR,
            "registry.url": ENV.REGISTRY_URL,
            "registry.username": ENV.REGISTRY_USERNAME,
            "registry.password": ENV.REGISTRY_PASSWORD,
            "registry.default": ENV.REGISTRY_DEFAULT,
            "sbom.enabled": ENV.SBOM_ENABLED,
            "sbom.format": ENV.SBOM_FORMAT,
        }

        for config_key, env_var in env_mapping.items():
            if env_var in os.environ:
                keys.add(config_key)

        return keys

    def _get_config_keys(self) -> Set[str]:
        """Get all keys from config file."""
        keys = set()

        def extract_keys(data: dict, prefix: str = "") -> None:
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.add(full_key)
                if isinstance(value, dict):
                    extract_keys(value, full_key)

        if self._config_data:
            extract_keys(self._config_data)

        return keys

    def _get_default_keys(self) -> Set[str]:
        """Get all keys that have defaults."""
        return {
            "cache_dir",
            "data_dir",
            "config_dir",
            "log_dir",
            "keys_dir",
            "registry.default",
            "registry.default_tag",
            "sbom.enabled",
            "sbom.format",
        }


# Global instance for commands to use
_config_service: Optional[ConfigService] = None


def get_config_service(config_file: Optional[Path] = None) -> ConfigService:
    """Get the global config service instance."""
    global _config_service  # noqa: PLW0603
    if _config_service is None:
        _config_service = ConfigService(config_file)
    return _config_service
