"""
Manifest service for Pakto workflows.

This module provides manifest loading, validation, and processing functionality
including variable resolution and template rendering integration.
"""

from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import ValidationError

from ..core.models import Manifest
from .templating import TemplatingService
from .validation import SchemaValidationError, SchemaValidationService


class ManifestError(Exception):
    """Exception raised during manifest processing."""

    pass


class ManifestService:
    """
    Service for handling manifest operations in Pakto workflows.

    This service provides comprehensive manifest functionality including:
    - Manifest file loading and validation
    - Variable processing and template rendering
    - Integration with templating services
    - Error handling and validation
    """

    def __init__(self):
        """Initialize the manifest service."""
        self.schema_validator = SchemaValidationService()
        self.templating_service = TemplatingService()

    def load_manifest_from_file(
        self,
        manifest_path: str,
        templating_service: Optional[TemplatingService] = None,
        cli_variables: Optional[Dict[str, str]] = None,
    ) -> Manifest:
        """
        Load and validate a manifest from a YAML file, with optional Jinja2 templating.

        Args:
            manifest_path: Path to the manifest YAML file
            templating_service: Optional Service for handling templating operations
            cli_variables: Optional dictionary of CLI variables for template rendering

        Returns:
            Parsed and validated Manifest model

        Raises:
            ManifestError: If the manifest cannot be loaded or validated
        """
        templating_service = templating_service or self.templating_service
        # populate the variables so that they can be accessed by any third party cli libraries
        try:
            manifest_file = Path(manifest_path)
            if not manifest_file.exists():
                msg = f"Manifest file not found: {manifest_path}"
                raise ManifestError(msg)

            # Read raw content
            with open(manifest_file, "r", encoding="utf-8") as f:
                raw_content = f.read()

            if not raw_content.strip():
                msg = f"Manifest file is empty: {manifest_path}"
                raise ManifestError(msg)

            # First, parse the raw YAML to extract manifest variables (without any template rendering)
            # This assumes the variables section itself doesn't contain templates initially
            try:
                raw_manifest_data = yaml.safe_load(raw_content)
                if raw_manifest_data is None:
                    msg = f"Manifest file is empty: {manifest_path}"
                    raise ManifestError(msg)

                # Get variables from manifest
                manifest_variables = raw_manifest_data.get("variables", {})
                # Get metadata from manifest
                manifest_metadata = raw_manifest_data.get("metadata", {})
            except yaml.YAMLError as e:
                msg = f"Invalid YAML in manifest file {manifest_path}: {e}"
                raise ManifestError(msg)

            # Merge manifest variables with CLI variables first (CLI takes precedence)
            merged_variables = templating_service.merge_variables(
                manifest_metadata, manifest_variables, cli_variables
            )

            # Then resolve self-referencing variables in the merged result
            resolved_variables = templating_service.resolve_self_referencing_variables(
                merged_variables
            )

            # If we have resolved variables, we need to update the raw content to replace
            # the variables section with resolved values before Jinja2 rendering
            if resolved_variables and resolved_variables != manifest_variables:
                # Handle metadata.* keys by updating the metadata section
                metadata_updates = {
                    k.split(".", 1)[1]: v
                    for k, v in resolved_variables.items()
                    if k.startswith("metadata.")
                }
                raw_manifest_data.get("metadata", {}).update(metadata_updates)

                # Update the variables section in the raw content with resolved values
                variables_updates = {
                    k.split(".", 1)[1]: v
                    for k, v in resolved_variables.items()
                    if k.startswith("variables.")
                }
                raw_manifest_data.get("variables", {}).update(variables_updates)

                # Regenerate the raw content with resolved self-references
                raw_content = yaml.dump(
                    raw_manifest_data, default_flow_style=False, sort_keys=False
                )
                # Update merged_variables to reflect the resolved values
                merged_variables = resolved_variables

            # Render the template with merged variables if we have any, or if template syntax is detected
            # This ensures undefined variables are caught even when no variables are explicitly provided
            has_template_syntax = "{{" in raw_content and "}}" in raw_content
            if merged_variables or has_template_syntax:
                # Ensure we have a dictionary for template rendering
                template_variables = merged_variables or {}

                # Include metadata in template context for {{metadata.name}} access
                template_context = template_variables.copy()
                if "metadata" in raw_manifest_data:
                    template_context["metadata"] = raw_manifest_data["metadata"]

                rendered_content = templating_service.render_template(
                    raw_content, template_context
                )
            else:
                rendered_content = raw_content

            # Parse final YAML
            try:
                manifest_data = yaml.safe_load(rendered_content)
            except yaml.YAMLError as e:
                msg = f"Invalid YAML after template rendering in {manifest_path}: {e}"
                raise ManifestError(msg)

            if manifest_data is None:
                msg = f"Manifest file is empty after processing: {manifest_path}"
                raise ManifestError(msg)

            # In order to make sure cli variables that were added to the manifest were not lost, we add them to the manifest data in the variables section. This will produce duplicate keys from the metadata section and the variables section but will capture the cli variables with or without the variables or metadata prefix.
            if cli_variables:
                # Handle CLI variables that may or may not have prefixes using dict comprehension
                cli_vars_dict = {
                    k.split(".", 1)[1]
                    if "." in k and k.split(".", 1)[0] == "variables"
                    else k: v
                    for k, v in cli_variables.items()
                    if not ("." in k and k.split(".", 1)[0] == "metadata")
                }

                # Add metadata prefixed variables to variables section with full key
                metadata_vars_dict = {
                    k: v
                    for k, v in cli_variables.items()
                    if "." in k and k.split(".", 1)[0] == "metadata"
                }

                manifest_data["variables"] = {
                    **manifest_data.get("variables", {}),
                    **cli_vars_dict,
                    **metadata_vars_dict,
                }

            # Validate against JSON schema before creating Pydantic model
            try:
                self.schema_validator.validate_manifest(manifest_data)
            except SchemaValidationError as e:
                msg = f"Manifest validation failed in {manifest_path}: {e}"
                raise ManifestError(msg)

            # Set the CLI variables for access in the Manifest model
            # self.cli_variables = cli_variables
            # Validate and create Manifest model
            try:
                return Manifest(**manifest_data)
            except ValidationError as e:
                msg = f"Invalid manifest structure in {manifest_path}: {e}"
                raise ManifestError(msg)

        except ManifestError:
            raise
        except Exception as e:
            msg = f"Failed to load manifest from {manifest_path}: {e}"
            raise ManifestError(msg)
