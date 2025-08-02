"""Pakto configuration constants and defaults.

This module provides namespaced constants for directory paths, environment
variables, and configuration defaults.
"""

import os
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import ClassVar, Union

# Type alias for paths that can be either str or Path
StrPath = Union[str, PathLike]


@dataclass(frozen=True)
class DirectoryDefaults:
    """Default directory paths based on user context.

    Follows FHS (Filesystem Hierarchy Standard) for system paths
    and XDG Base Directory specification for user paths.
    """

    # Class variable to determine root vs user paths
    IS_ROOT: ClassVar[bool] = os.geteuid() == 0 if hasattr(os, "geteuid") else False

    # Instance fields with defaults based on IS_ROOT
    config: Path = Path("/etc/pakto") if IS_ROOT else Path.home() / ".config" / "pakto"
    cache: Path = (
        Path("/var/lib/pakto/cache")
        if IS_ROOT
        else Path.home() / ".local" / "share" / "pakto" / "cache"
    )
    data: Path = (
        Path("/var/lib/pakto")
        if IS_ROOT
        else Path.home() / ".local" / "share" / "pakto"
    )
    log: Path = (
        Path("/var/log/pakto")
        if IS_ROOT
        else Path.home() / ".local" / "state" / "pakto" / "log"
    )
    keys: Path = (
        Path("/etc/pakto/keys")
        if IS_ROOT
        else Path.home() / ".config" / "pakto" / "keys"
    )


@dataclass(frozen=True)
class EnvironmentVars:
    """Environment variable names for Pakto configuration."""

    ENV_PREFIX_BARE: str = "PAKTO"
    CONFIG_DIR: str = f"{ENV_PREFIX_BARE}_CONFIG_DIR"
    CACHE_DIR: str = f"{ENV_PREFIX_BARE}_CACHE_DIR"
    DATA_DIR: str = f"{ENV_PREFIX_BARE}_DATA_DIR"
    LOG_DIR: str = f"{ENV_PREFIX_BARE}_LOG_DIR"
    KEYS_DIR: str = f"{ENV_PREFIX_BARE}_KEYS_DIR"
    CONFIG_FILE: str = f"{ENV_PREFIX_BARE}_CONFIG"  # For --config flag equivalent

    # Registry environment variables
    REGISTRY_URL: str = f"{ENV_PREFIX_BARE}_REGISTRY_URL"
    REGISTRY_USERNAME: str = f"{ENV_PREFIX_BARE}_REGISTRY_USERNAME"
    REGISTRY_PASSWORD: str = f"{ENV_PREFIX_BARE}_REGISTRY_PASSWORD"
    REGISTRY_DEFAULT: str = f"{ENV_PREFIX_BARE}_REGISTRY_DEFAULT"
    OUTPUT_DEFAULT_DIR: str = f"{ENV_PREFIX_BARE}_OUTPUT_DEFAULT_DIR"
    SBOM_ENABLED: str = f"{ENV_PREFIX_BARE}_SBOM_ENABLED"
    SBOM_FORMAT: str = f"{ENV_PREFIX_BARE}_SBOM_FORMAT"


@dataclass(frozen=True)
class ConfigDefaults:
    """Default configuration values."""

    APP_ANNOTATION_DOMAIN: str = "com.warrical.pakto"
    APP_DOMAIN: str = "pakto.warrical.com"
    APP_MEDIA_TYPE: str = "application/vnd.pakto"
    SCHEMA_VERSION: str = "v1alpha1"
    SCHEMA_VERSION_KEY: str = "apiVersion"
    SCHEMA_VERSION_VALUE: str = f"{APP_DOMAIN}/{SCHEMA_VERSION}"
    SCHEMA_KIND_KEY: str = "kind"
    SCHEMA_KIND_VALUE: str = "Config"
    CONFIG_FILENAME: str = "pakto.yaml"
    CONFIG_EXAMPLE_FILENAME: str = "example-config.pakto.yaml"
    CONFIG_KIND: str = "Config"
    DEFAULT_REGISTRY: str = "docker.io"
    DEFAULT_TAG: str = "latest"
    DEFAULT_LOCKFILE_NAME: str = "pakto.lock.yaml"

    # File permissions
    CONFIG_FILE_MODE: int = 0o600  # Read/write for owner only
    DIRECTORY_MODE: int = 0o755  # Standard directory permissions


# Singleton instances
DIRS = DirectoryDefaults()
ENV = EnvironmentVars()
DEFAULTS = ConfigDefaults()
