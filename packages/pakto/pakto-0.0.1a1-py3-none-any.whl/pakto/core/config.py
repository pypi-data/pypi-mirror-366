"""Configuration models and loader for Pakto."""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

from .constants import ConfigDefaults, DirectoryDefaults, EnvironmentVars


class RegistryAuth(BaseModel):
    """Registry authentication configuration."""

    username: str
    password: Optional[str] = None
    token: Optional[str] = None


class RegistryConfig(BaseModel):
    """Registry configuration."""

    default: Optional[str] = None
    auth: Dict[str, RegistryAuth] = Field(default_factory=dict)


class OutputConfig(BaseModel):
    """Output directory configuration."""

    default_dir: str = "./output"


class SbomConfig(BaseModel):
    """SBOM generation configuration."""

    enabled: bool = False
    format: str = "spdx"

    @field_validator("format")
    def validate_format(cls, v):  # noqa: N805
        allowed = ["spdx", "cyclonedx"]
        if v not in allowed:
            msg = f"SBOM format must be one of {allowed}"
            raise ValueError(msg)
        return v


class Config(BaseModel):
    """Main configuration model."""

    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    sbom: SbomConfig = Field(default_factory=SbomConfig)


class ConfigLoader:
    """Load and merge configuration from multiple sources."""

    def __init__(self):
        self.env_prefix = "PAKTO_"

    def load(self, config_path: Optional[Path] = None) -> Config:
        """Load configuration with proper precedence."""
        # Start with defaults
        config_dict = {}

        # Load from file if specified or check default location
        if config_path and config_path.exists():
            config_dict = self._load_file(config_path)
        else:
            default_path = DirectoryDefaults.config / ConfigDefaults.CONFIG_FILENAME
            config_dict = self._load_file(default_path)

        # Create config from file/defaults
        try:
            config = Config(**config_dict) if config_dict else Config()
        except ValidationError as e:
            msg = f"Config validation failed: {e}"
            raise ValueError(msg) from e

        # Apply environment variables (always)
        return self._apply_env_vars(config)

    def _load_file(self, path: Path) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            msg = f"Failed to load config from {path}: {e}"
            raise ValueError(msg) from e

    def _apply_env_vars(self, config: Config) -> Config:
        """Apply environment variables to config."""
        config_dict = config.model_dump()

        # Check for specific env vars we care about
        env_mappings = {
            EnvironmentVars.REGISTRY_DEFAULT: ("registry", "default"),
            EnvironmentVars.OUTPUT_DEFAULT_DIR: ("output", "default_dir"),
            EnvironmentVars.SBOM_ENABLED: ("sbom", "enabled"),
            EnvironmentVars.SBOM_FORMAT: ("sbom", "format"),
        }

        for env_var, (section, key) in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]

                # Convert boolean strings
                if key == "enabled" and isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes", "on")

                # Apply to config dict
                if section not in config_dict:
                    config_dict[section] = {}
                config_dict[section][key] = value

        # Re-validate with new values
        try:
            return Config(**config_dict)
        except ValidationError as e:
            msg = f"Config validation failed after env vars: {e}"
            raise ValueError(msg) from e
