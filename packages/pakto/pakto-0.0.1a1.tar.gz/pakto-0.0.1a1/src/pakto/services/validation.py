"""
Schema validation service for Pakto manifests and lock files.

This module provides JSON Schema validation functionality to ensure
manifests and lock files conform to their official specifications
before processing with Pydantic models.
"""

import json
from importlib import resources
from typing import Any, Dict, List, Optional

from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate

from pakto.core.constants import DEFAULTS


class SchemaValidationError(Exception):
    """Exception raised during schema validation."""

    def __init__(self, message: str, validation_errors: Optional[List[str]] = None):
        """
        Initialize schema validation error.

        Args:
            message: Main error message
            validation_errors: List of specific validation error details
        """
        if validation_errors is None:
            validation_errors = []
        super().__init__(message)
        self.validation_errors = validation_errors


class SchemaValidationService:
    """
    Service for JSON Schema validation of Pakto manifests and lock files.

    This service provides validation against the official JSON schemas to ensure
    data integrity and specification compliance before Pydantic model creation.
    Supports version-aware schema loading based on apiVersion field.
    """

    def __init__(
        self,
        manifest_schema_version: Optional[str] = DEFAULTS.SCHEMA_VERSION,
        lockfile_schema_version: Optional[str] = DEFAULTS.SCHEMA_VERSION,
        config_schema_version: Optional[str] = DEFAULTS.SCHEMA_VERSION,
    ):
        """Initialize the schema validation service."""
        self.manifest_schema_version = (
            manifest_schema_version or DEFAULTS.SCHEMA_VERSION
        )
        self.lockfile_schema_version = (
            lockfile_schema_version or DEFAULTS.SCHEMA_VERSION
        )
        self.config_schema_version = config_schema_version or DEFAULTS.SCHEMA_VERSION

        # Load default schemas by default
        self.manifest_schema = self._load_schema(
            "manifest.json", self.manifest_schema_version
        )
        self.lockfile_schema = self._load_schema(
            "lock.json", self.lockfile_schema_version
        )
        self.config_schema = self._load_schema(
            "config.json", self.config_schema_version
        )

    def _get_schema_version(self, data: Dict[str, Any]) -> str:
        """
        Determine schema version from the apiVersion field.

        Args:
            data: Parsed manifest or lockfile data

        Returns:
            Schema version string ('/v1alpha1')
        """
        api_version = data.get(DEFAULTS.SCHEMA_VERSION_KEY, "")
        if api_version == DEFAULTS.SCHEMA_VERSION_VALUE:
            return DEFAULTS.SCHEMA_VERSION
        return api_version

    def _load_schema(
        self, schema_name: str, version: str = DEFAULTS.SCHEMA_VERSION
    ) -> Dict[str, Any]:
        """
        Load a JSON schema from the package resources.

        Args:
            schema_name: Name of the schema file (e.g., 'manifest.json')
            version: Schema version ('/v1alpha1')

        Returns:
            Loaded JSON schema as dictionary

        Raises:
            SchemaValidationError: If schema cannot be loaded
        """
        try:
            # Load schema from version-specific package resources
            schema_text = resources.read_text(
                f"pakto.core.schemas.{version}", schema_name
            )
            return json.loads(schema_text)
        except Exception as e:
            msg = f"Failed to load schema {schema_name} (version {version}): {e}"
            raise SchemaValidationError(msg)

    def _format_validation_error(self, error: JsonSchemaValidationError) -> str:
        """
        Format a jsonschema validation error into a human-readable message.

        Args:
            error: JsonSchema validation error

        Returns:
            Formatted error message
        """
        path = (
            " -> ".join([str(p) for p in error.absolute_path])
            if error.absolute_path
            else "root"
        )
        return f"Validation error at '{path}': {error.message}"

    def validate_manifest(self, manifest_data: Dict[str, Any]) -> None:
        """
        Validate manifest data against the appropriate version-specific JSON schema.

        Args:
            manifest_data: Parsed manifest data as dictionary

        Raises:
            SchemaValidationError: If validation fails
        """
        try:
            # Determine schema version and load appropriate schema
            version = self._get_schema_version(manifest_data)
            manifest_schema = self._load_schema("manifest.json", version)

            validate(instance=manifest_data, schema=manifest_schema)
        except JsonSchemaValidationError as e:
            error_message = self._format_validation_error(e)

            # Collect additional validation errors if present
            validation_errors = [error_message]

            # Check for additional context from the error
            if hasattr(e, "context") and e.context:
                validation_errors.extend(
                    self._format_validation_error(context_error)
                    for context_error in e.context
                )

            msg = f"Manifest validation failed: {error_message}"
            raise SchemaValidationError(msg, validation_errors)
        except Exception as e:
            msg = f"Schema validation error: {e}"
            raise SchemaValidationError(msg)

    def validate_lockfile(self, lockfile_data: Dict[str, Any]) -> None:
        """
        Validate lockfile data against the appropriate version-specific JSON schema.

        Args:
            lockfile_data: Parsed lockfile data as dictionary

        Raises:
            SchemaValidationError: If validation fails
        """
        try:
            # Determine schema version and load appropriate schema
            version = self._get_schema_version(lockfile_data)
            lockfile_schema = self._load_schema("lock.json", version)

            validate(instance=lockfile_data, schema=lockfile_schema)
        except JsonSchemaValidationError as e:
            error_message = self._format_validation_error(e)

            # Collect additional validation errors if present
            validation_errors = [error_message]

            # Check for additional context from the error
            if hasattr(e, "context") and e.context:
                validation_errors.extend(
                    self._format_validation_error(context_error)
                    for context_error in e.context
                )

            msg = f"Lockfile validation failed: {error_message}"
            raise SchemaValidationError(msg, validation_errors)
        except Exception as e:
            msg = f"Schema validation error: {e}"
            raise SchemaValidationError(msg)

    def validate_config(self, config_data: Dict[str, Any]) -> None:
        """
        Validate config data against the appropriate version-specific JSON schema.

        Args:
            config_data: Parsed config data as dictionary
        """
        try:
            # Determine schema version and load appropriate schema
            version = self._get_schema_version(config_data)
            config_schema = self._load_schema("config.json", version)

            validate(instance=config_data, schema=config_schema)
        except JsonSchemaValidationError as e:
            error_message = self._format_validation_error(e)

            # Collect additional validation errors if present
            validation_errors = [error_message]

            # Check for additional context from the error
            if hasattr(e, "context") and e.context:
                validation_errors.extend(
                    self._format_validation_error(context_error)
                    for context_error in e.context
                )

            msg = f"Config validation failed: {error_message}"
            raise SchemaValidationError(msg, validation_errors)
        except Exception as e:
            msg = f"Schema validation error: {e}"
            raise SchemaValidationError(msg)
