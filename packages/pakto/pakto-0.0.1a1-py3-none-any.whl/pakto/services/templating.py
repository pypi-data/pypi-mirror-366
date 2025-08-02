"""
Templating service for Pakto manifests.

This module provides templating functionality including variable processing,
merging, self-reference resolution, and Jinja2 template rendering.
"""

import re
from typing import Any, Dict, Optional, Tuple

from jinja2 import BaseLoader, Environment, StrictUndefined, TemplateError


class TemplatingError(Exception):
    """Exception raised during template processing."""

    pass


class TemplatingService:
    """
    Service for handling template operations in Pakto manifests.

    This service provides comprehensive templating functionality including:
    - CLI variable parsing
    - Variable merging with precedence rules
    - Self-referencing variable resolution for {{.key}}, {{variables.key}}, and {{metadata.key}}
    - Jinja2 template rendering
    """

    def __init__(self):
        """Initialize the templating service.
        Regex pattern:
            - Matches {{ optional_space CAPTURED_GROUP optional_space }}
            - CAPTURED_GROUP (group 1) can be:
            - .key_path (e.g., .base_name, .some.nested-key)
            - variables.key_path (e.g., variables.base_name, variables.some.nested-key)
            - metadata.key_path (e.g., metadata.name, metadata.some.nested-key)
            - alphanumeric characters, underscores, dots, and hyphens are allowed in the key_path.
        """
        self._self_ref_pattern = re.compile(
            r"\{\{\s*((?:\.|variables\.|metadata\.)[\w.-]+)\s*\}\}"
        )

    def parse_variables(self, var_options: Tuple[str, ...]) -> Dict[str, str]:
        """
        Parse --var key=value options into a dictionary.

        Args:
            var_options: Tuple of "key=value" strings from CLI options

        Returns:
            Dictionary of parsed variables

        Raises:
            TemplatingError: If any variable is malformed
        """
        variables = {}
        for var_option in var_options:
            if "=" not in var_option:
                msg = f"Invalid variable format '{var_option}'. Expected 'key=value'"
                raise TemplatingError(msg)

            key, value = var_option.split("=", 1)
            key = key.strip()
            # value = value.strip()

            if not key:
                msg = f"Empty variable key in '{var_option}'"
                raise TemplatingError(msg)

            if not value:
                msg = f"Empty variable value in '{var_option}'"
                raise TemplatingError(msg)

            variables[key] = value

        return variables

    def old_merge_variables(
        self,
        metadata_variables: Optional[Dict[str, Any]],
        manifest_variables: Optional[Dict[str, Any]],
        cli_variables: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Merge metadata_variables and manifest variables with CLI variables.
        CLI variables taking precedence.

        Args:
            metadata_variables: Variables defined in the metadata
            manifest_variables: Variables defined in the manifest
            cli_variables: Variables provided via CLI options

        Returns:
            Merged dictionary of variables
        """
        merged = {}

        # Start with metadata variables if they exist
        if metadata_variables:
            merged.update(metadata_variables)

        # Then add manifest variables if they exist
        if manifest_variables:
            merged.update(manifest_variables)

        # Override with CLI variables if they exist
        if cli_variables:
            merged.update(cli_variables)

        return merged

    def old_resolve_self_referencing_variables(
        self, variables: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve self-referencing variables using {{.variable_key}} syntax.

        Variables can reference other variables within the same variables section using
        the {{.variable_key}} syntax. This function iteratively resolves these references
        while detecting circular dependencies.

        Args:
            variables: Dictionary of variables that may contain self-references

        Returns:
            Dictionary with all self-references resolved, or None if input was None

        Raises:
            TemplatingError: If circular dependencies are detected or undefined variables are referenced
        """
        if variables is None:
            return None

        if not variables:
            return variables

        # Copy variables to avoid modifying the original
        resolved = variables.copy()
        max_iterations = 10  # Prevent infinite loops

        for _iteration in range(max_iterations):
            changes_made = False

            # Process each variable that might contain self-references
            for key, value in list(resolved.items()):
                # Only process string values
                if not isinstance(value, str):
                    continue

                # Check if this value contains any self-references
                if not self._self_ref_pattern.search(value):
                    continue

                # Define replacement function for regex substitution
                def replace_ref(match):
                    ref_key = match.group(1)

                    if ref_key not in resolved:
                        msg = f"Undefined variable reference '{{.{ref_key}}}' in variable '{key}'"
                        raise TemplatingError(msg)

                    # Check for direct circular reference
                    if ref_key == key:
                        msg = f"Circular reference detected: variable '{key}' references itself"
                        raise TemplatingError(msg)

                    # Get the reference value and convert to string if needed
                    ref_value = resolved[ref_key]
                    if not isinstance(ref_value, str):
                        ref_value = str(ref_value)

                    return ref_value

                # Replace all self-references in this value
                try:
                    new_value = self._self_ref_pattern.sub(replace_ref, value)
                except TemplatingError:
                    raise  # Re-raise TemplatingError from replace_ref

                # Update the resolved value if it changed
                if new_value != value:
                    resolved[key] = new_value
                    changes_made = True

            # If no changes were made this iteration, we're done
            if not changes_made:
                break
        else:
            # If we exhausted all iterations, there might be a complex circular dependency
            # Find variables that still have unresolved references
            unresolved = []
            for key, value in resolved.items():
                if isinstance(value, str) and self._self_ref_pattern.search(value):
                    unresolved.append(key)

            if unresolved:
                msg = f"Circular dependency detected in variables: {', '.join(unresolved)}"
                raise TemplatingError(msg)

        return resolved

    def merge_variables(
        self,
        metadata_variables: Optional[
            Dict[str, Any]
        ] = None,  # These are from the 'metadata:' block
        manifest_variables: Optional[
            Dict[str, Any]
        ] = None,  # These are from the 'variables:' block
        parsed_cli_options: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Merge metadata, manifest (variables block), and CLI variables.
        The resulting dictionary is structured for self-reference resolution,
        supporting {{.key}}, {{variables.key}}, and {{metadata.key}} syntaxes.
        Precedence: CLI > Manifest 'variables:' block > 'metadata:' block.

        Args:
            metadata_variables_yaml: Variables from the 'metadata:' section of YAML.
            manifest_variables_yaml: Variables from the 'variables:' section of YAML.
            cli_variables_parsed: Variables parsed from CLI options.

        Returns:
            A merged dictionary of variables prepared for self-reference resolution.
        """
        if parsed_cli_options is None:
            parsed_cli_options = {}
        if manifest_variables is None:
            manifest_variables = {}
        if metadata_variables is None:
            metadata_variables = {}
        merged = {}

        # 1. Metadata variables (lowest precedence for their specific keys)
        # These are primarily accessed via {{metadata.key}} during self-referencing.
        if metadata_variables:
            for k, v in metadata_variables.items():
                merged[f"metadata.{k}"] = v

        # 2. Manifest variables (from 'variables:' block in YAML)
        # These are accessible via {{.key}} and {{variables.key}}.
        # Store them under both forms of keys to ensure they resolve correctly.
        # Manifest variables override metadata if a direct key (for {{.key}}) collides,
        # or if a 'variables.key' collides with a 'metadata.variables.key' (unlikely).
        if manifest_variables:
            for k, v in manifest_variables.items():
                merged[k] = v  # For {{.key}}
                merged[f"variables.{k}"] = (
                    v  # For {{variables.key}} (ensures same value as {{.key}})
                )

        # 3. CLI variables (highest precedence)
        if parsed_cli_options:
            for k_cli, v_cli in parsed_cli_options.items():
                # Direct update for the key as specified in CLI (e.g., "foo", "variables.foo", "metadata.foo")
                merged[k_cli] = v_cli

                # If CLI updated a simple key (e.g., "myvar") that originated from manifest_variables_yaml,
                # ensure its 'variables.' prefixed alias is also updated to maintain consistency.
                if (
                    "." not in k_cli
                    and manifest_variables
                    and k_cli in manifest_variables
                ):
                    merged[f"variables.{k_cli}"] = v_cli

                # If CLI updated a 'variables.key' (e.g., "variables.myvar"),
                # ensure its simple key alias ('myvar') is also updated if it originated from manifest_variables_yaml.
                if k_cli.startswith("variables."):
                    simple_key = k_cli.split(".", 1)[1]
                    if manifest_variables and simple_key in manifest_variables:
                        merged[simple_key] = v_cli
        return merged

    def resolve_self_referencing_variables(
        self, variables: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve self-referencing variables using {{.key}}, {{variables.key}},
        or {{metadata.key}} syntax within the provided 'variables' dictionary.

        This function iteratively resolves references. The 'variables' dictionary
        is expected to be pre-processed (e.g., by 'merge_variables') to contain
        all necessary keys for lookup, such as "key" (for {{.key}}),
        "variables.key" (for {{variables.key}}), and "metadata.key" (for {{metadata.key}}).

        Args:
            variables: Dictionary of variables that may contain self-references.

        Returns:
            Dictionary with all self-references resolved, or None if input was None.

        Raises:
            TemplatingError: If circular dependencies are detected or undefined variables are referenced.
        """
        if variables is None:
            return None

        if not variables:
            return variables

        resolved = variables.copy()
        max_iterations = len(variables) + 5  # Max iterations to prevent infinite loops

        processing_path = []  # For detailed circular dependency tracking

        for _iteration in range(max_iterations):
            changes_made_in_iteration = False
            items_to_process = list(
                resolved.items()
            )  # Iterate over a copy as resolved might change

            for key_being_resolved, value_template in items_to_process:
                if not isinstance(value_template, str):
                    continue

                if not self._self_ref_pattern.search(value_template):
                    continue

                original_value_for_key = value_template

                def replace_ref(match):
                    nonlocal processing_path

                    raw_matched_reference = match.group(
                        1
                    )  # e.g., ".base_name", "variables.config_file", "metadata.name"
                    full_template_tag = match.group(
                        0
                    )  # e.g., "{{.base_name}}", "{{ variables.config_file }}"

                    ref_key_for_lookup = None
                    if raw_matched_reference.startswith("."):
                        ref_key_for_lookup = raw_matched_reference[1:]  # "base_name"
                    else:
                        # For "variables.config_file" or "metadata.name",
                        # this is the direct key in the `resolved` dictionary.
                        ref_key_for_lookup = raw_matched_reference

                    if ref_key_for_lookup == key_being_resolved:
                        msg = (
                            f"Circular reference detected: variable '{key_being_resolved}' directly references itself "
                            f"via '{full_template_tag}'."
                        )
                        raise TemplatingError(msg)
                    if ref_key_for_lookup in processing_path:
                        cycle = " -> ".join([*processing_path, ref_key_for_lookup])
                        msg = (
                            f"Circular reference detected: {cycle} in variable '{key_being_resolved}' "
                            f"referencing '{full_template_tag}'."
                        )
                        raise TemplatingError(msg)

                    if ref_key_for_lookup not in resolved:
                        msg = (
                            f"Undefined variable reference '{full_template_tag}' in variable '{key_being_resolved}'. "
                            f"Key '{ref_key_for_lookup}' not found in resolved variables."
                        )
                        raise TemplatingError(msg)

                    processing_path.append(ref_key_for_lookup)

                    referenced_value = resolved[ref_key_for_lookup]

                    if not isinstance(referenced_value, str):
                        resolved_ref_value_str = str(referenced_value)
                    else:
                        # If the referenced value itself still contains templates,
                        # it will be resolved in a subsequent pass or iteration if necessary.
                        resolved_ref_value_str = referenced_value

                    processing_path.pop()
                    return resolved_ref_value_str

                try:
                    processing_path = [key_being_resolved]
                    new_value = self._self_ref_pattern.sub(replace_ref, value_template)
                    processing_path = []

                    if new_value != original_value_for_key:
                        resolved[key_being_resolved] = new_value
                        changes_made_in_iteration = True
                except TemplatingError as e:
                    processing_path = []
                    raise e

            if not changes_made_in_iteration:
                break
        else:
            unresolved_keys = []
            for k, v_val in resolved.items():
                if isinstance(v_val, str) and self._self_ref_pattern.search(v_val):
                    unresolved_keys.append(k)
            if unresolved_keys:
                msg = (
                    f"Could not resolve all variables after {max_iterations} iterations. "
                    f"Potential complex circular dependency or unresolved nested references in: {', '.join(unresolved_keys)}"
                )
                raise TemplatingError(msg)
        return resolved

    def render_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the provided variables.

        Args:
            template_content: The template content as a string
            variables: Dictionary of variables to use in rendering

        Returns:
            Rendered template string

        Raises:
            TemplatingError: If template rendering fails
        """
        try:
            # Use StrictUndefined to catch undefined variables
            env = Environment(loader=BaseLoader(), undefined=StrictUndefined)
            template = env.from_string(template_content)
            # Make variables available both directly and wrapped in 'variables' object
            # This supports both {{ var_name }} and {{ variables.var_name }} syntax
            context = variables.copy()
            context["variables"] = variables
            return template.render(**context)
        except TemplateError as e:
            msg = f"Template rendering failed: {e}"
            raise TemplatingError(msg)
        except Exception as e:
            msg = f"Unexpected error during template rendering: {e}"
            raise TemplatingError(msg)
