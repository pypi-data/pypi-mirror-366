"""
Implementation of the `pakto init` command.

This module implements the CLI command for scaffolding a starter manifest file
with commented examples and sensible defaults.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from pakto.cli.context import AppContext


def _generate_entrypoint_script(config):
    return (
        """#!/bin/bash
# Entry point for the container
# Adjust the following lines to suit your application's needs

echo "Running entrypoint script..."
"""
        if config.get("include_entrypoint", False)
        else None
    )


@click.command()
@click.argument("name", required=False)
@click.option(
    "-C",
    "--directory",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Run command in a specific directory.",
)
@click.option(
    "--version",
    "-v",
    help="Bundle version",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Accept all defaults (non-interactive mode)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--template",
    type=click.Choice(["standard", "basic", "basic-entrypoint", "full"]),
    default="standard",
    help="Template type (default: standard)",
)
@click.option(
    "--artifacts",
    "-a",
    type=int,
    help="Number of artifacts to include",
)
@click.option(
    "--artifact-types",
    help="Comma-separated list of artifact types (local,http,oci)",
)
@click.pass_context
def init(
    ctx: click.Context,
    name: Optional[str],
    directory: Optional[Path],
    version: Optional[str],
    yes: bool,
    force: bool,
    template: str,
    artifacts: Optional[int],
    artifact_types: Optional[str],
):
    """
    Scaffold a starter manifest file with commented examples.

    This command initializes a new Pakto bundle. It can be run in an existing
    directory or create a new one.

    Examples:

    # Create a new bundle named 'my-app' in a new 'my-app/' directory
    pakto init my-app

    # Initialize a bundle in the current directory
    pakto init

    # Initialize a bundle in a specific directory
    pakto init -C /path/to/project

    # Create a new bundle with a specific name and version
    pakto init my-app --version 1.2.3

    # Use a different template
    pakto init my-app --template basic
    """
    # Get the pakto context object
    cc: AppContext = ctx.obj or AppContext()

    # Determine the base directory for initialization
    base_dir = (directory or cc.calling_dir).resolve()

    # Determine the project name. If not provided, prompt for it in interactive mode.
    if not name and not yes:
        name = click.prompt("Bundle name", default=base_dir.name)

    # If we have a project name, the project directory is a subdirectory.
    # Otherwise (e.g., --yes with no name), it's the base directory.
    project_dir = base_dir / name if name else base_dir

    # Now we have a definitive project_dir, let's proceed.
    project_dir.mkdir(parents=True, exist_ok=True)

    # Determine bundle name for the manifest file.
    bundle_name = name or _get_default_bundle_name(project_dir)

    # Determine output filename
    output_file = project_dir / f"{bundle_name}.pakto.yml"

    # Check if file exists and handle force flag
    if output_file.exists() and not force:
        try:
            rel_path = output_file.relative_to(cc.calling_dir)
        except ValueError:
            rel_path = output_file
        msg = f"File '{rel_path}' already exists. Use --force to overwrite."
        raise click.ClickException(msg)

    # Collect manifest configuration
    config = _collect_manifest_config(
        bundle_name=bundle_name,
        version=version,
        template=template,
        artifacts=artifacts,
        artifact_types=artifact_types,
        yes=yes,
    )

    # Generate the manifest template
    template_content = _generate_manifest_template(config)
    entrypoint_content = _generate_entrypoint_script(config)

    # Write the template to file
    try:
        output_file.write_text(template_content)
        display_path = (
            output_file.relative_to(cc.calling_dir)
            if output_file.is_relative_to(cc.calling_dir)
            else output_file
        )
        click.echo(f"✅ Created manifest template: {display_path}")
    except OSError as e:
        msg = f"Failed to write manifest file: {e}"
        raise click.ClickException(msg)

    # Write the entrypoint script if needed
    if entrypoint_content and config.get("include_entrypoint", False):
        entrypoint_script = project_dir / "scripts" / "install.sh"
        try:
            entrypoint_script.parent.mkdir(parents=True, exist_ok=True)
            entrypoint_script.write_text(entrypoint_content)
            entrypoint_script.chmod(0o755)
            display_path = (
                entrypoint_script.relative_to(cc.calling_dir)
                if entrypoint_script.is_relative_to(cc.calling_dir)
                else entrypoint_script
            )
            click.echo(f"✅ Created entrypoint script: {display_path}")
        except OSError as e:
            msg = f"Failed to write entrypoint script: {e}"
            raise click.ClickException(msg)

    click.echo("📝 Edit the file to customize your bundle configuration.")


def _get_default_bundle_name(directory: Path) -> str:
    """Get default bundle name from directory name."""
    if directory.resolve() == Path.cwd().resolve():
        return "manifest"
    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "-", directory.name)
    clean_name = re.sub(r"-+", "-", clean_name).strip("-")
    return clean_name or "manifest"


def _collect_manifest_config(
    bundle_name: str,
    version: Optional[str],
    template: str,
    artifacts: Optional[int],
    artifact_types: Optional[str],
    yes: bool,
) -> Dict[str, Any]:
    """Collect manifest configuration through CLI options and interactive prompts."""
    config: Dict[str, Any] = {
        "name": bundle_name,
        "template": template,
    }

    # Version
    if version:
        config["version"] = version
    elif yes:
        config["version"] = "1.0.0"
    else:
        config["version"] = _prompt_with_defaults(
            "Bundle version",
            default="1.0.0",
            type=str,
        )

    # Description (always prompt unless yes)
    if yes:
        config["description"] = ""
    else:
        config["description"] = _prompt_with_defaults(
            "Bundle description (optional)",
            default="",
            type=str,
        )

    # Entrypoint configuration
    config["include_entrypoint"] = _should_include_entrypoint(template, yes)

    # Artifact configuration
    artifact_config = _collect_artifact_config(
        template=template,
        artifacts=artifacts,
        artifact_types=artifact_types,
        yes=yes,
    )
    config.update(artifact_config)

    return config


def _prompt_with_defaults(prompt_text: str, default: Any, type: Any = str):  # noqa: A002
    """Prompt with ability to use defaults for remaining prompts."""
    try:
        result = click.prompt(prompt_text, default=default, type=type)
        # Check if user wants to use defaults for remaining prompts
        if isinstance(result, str) and result.lower() in ["defaults", "d", "default"]:
            return default
        return result
    except click.Abort:
        # If user aborts, use default
        return default


def _should_include_entrypoint(template: str, yes: bool) -> bool:
    """Determine if entrypoint should be included."""
    if template in ["basic-entrypoint", "full"]:
        return True
    if template == "basic":
        return False
    if yes:
        return True  # standard template default
    return click.confirm(
        "Include entrypoint script?",
        default=True,
    )


def _collect_artifact_config(
    template: str,
    artifacts: Optional[int],
    artifact_types: Optional[str],
    yes: bool,
) -> Dict[str, Any]:
    """Collect artifact configuration."""
    config = {}

    # Parse artifact types
    parsed_types = []
    if artifact_types:
        parsed_types = [t.strip().lower() for t in artifact_types.split(",")]
        # Map aliases to standard types
        type_mapping = {
            "file": "local",
            "url": "http",
            "image": "oci",
        }
        parsed_types = [type_mapping.get(t, t) for t in parsed_types]

    # Determine artifact count
    if artifacts:
        config["artifact_count"] = artifacts
    elif parsed_types:
        # If artifact types are specified but count is not, use the count from types
        config["artifact_count"] = len(parsed_types)
    elif yes:
        config["artifact_count"] = _get_default_artifact_count(template)
    else:
        default_count = _get_default_artifact_count(template)
        config["artifact_count"] = _prompt_with_defaults(
            "Number of artifacts to include",
            default=default_count,
            type=int,
        )

    # Determine artifact types
    if parsed_types:
        config["artifact_types"] = parsed_types
    elif yes:
        config["artifact_types"] = _get_default_artifact_types(
            template, config["artifact_count"]
        )
    else:
        config["artifact_types"] = _prompt_artifact_types(config["artifact_count"])

    return config


def _get_default_artifact_count(template: str) -> int:
    """Get default artifact count based on template."""
    template_counts = {
        "basic": 1,
        "basic-entrypoint": 2,
        "standard": 3,
        "full": 5,
    }
    return template_counts.get(template, 3)


def _get_default_artifact_types(template: str, count: int) -> List[str]:
    """Get default artifact types based on template and count."""
    if template == "basic":
        return ["oci"]
    if template == "basic-entrypoint":
        return ["oci", "oci"]
    if template == "standard":
        return ["oci", "oci", "oci"]
    if template == "full":
        return ["oci", "oci", "oci", "oci", "oci"]
    # Fallback: all oci
    return ["oci"] * count


def _prompt_artifact_types(count: int) -> List[str]:
    """Prompt user for artifact types with single letter support."""
    available_types = ["local", "http", "oci"]
    type_descriptions = {
        "local": "Local file",
        "http": "HTTP URL",
        "oci": "OCI container image",
    }

    click.echo("\nAvailable artifact types:")
    for t in available_types:
        click.echo(f"  {t[0].upper()}/{t}: {type_descriptions[t]}")

    types = []
    for i in range(count):
        if i == 0:
            prompt = f"Artifact {i + 1} type"
        else:
            prompt = f"Artifact {i + 1} type (or press Enter for default)"
            default = types[0] if types else "oci"

        # Custom choice function that accepts single letters
        def validate_choice(value):
            if not value:
                return default if i > 0 else "oci"
            value = value.lower()
            # Check for single letter input
            if len(value) == 1:
                for t in available_types:
                    if t.startswith(value):
                        return t
            # Check for full name
            if value in available_types:
                return value
            msg = f"Invalid choice: {value}. Choose from {', '.join(available_types)}"
            raise click.BadParameter(msg)

        artifact_type = click.prompt(
            prompt,
            default=default if i > 0 else "oci",
            value_proc=validate_choice,
        )
        types.append(artifact_type)

    return types


def _generate_manifest_template(config: Dict[str, Any]) -> str:
    """Generate a manifest template based on configuration."""
    template_type = config["template"]

    if template_type == "basic":
        return _generate_basic_template(config)
    if template_type == "basic-entrypoint":
        return _generate_basic_entrypoint_template(config)
    if template_type == "full":
        return _generate_full_template(config)
    # standard
    return _generate_standard_template(config)


def _generate_basic_template(config: Dict[str, Any]) -> str:
    """Generate a basic template with minimal content."""
    artifacts = _generate_artifacts_from_config(config)

    return f'''# Pakto Manifest Template
# This file defines a bundle of software artifacts for deployment
# See https://github.com/warrical/pakto for documentation

apiVersion: pakto.warrical.com/v1alpha1
kind: Manifest

# Bundle metadata - required information about your bundle
metadata:
  name: "{config["name"]}"
  version: "{config["version"]}"
  description: "{config["description"] or "Basic application bundle"}"

# List of artifacts to include in this bundle
artifacts:
{artifacts}
'''


def _generate_basic_entrypoint_template(config: Dict[str, Any]) -> str:
    """Generate a basic template with entrypoint."""
    artifacts = _generate_artifacts_from_config(config)

    return f'''# Pakto Manifest Template
# This file defines a bundle of software artifacts for deployment
# See https://github.com/warrical/pakto for documentation

apiVersion: pakto.warrical.com/v1alpha1
kind: Manifest

# Bundle metadata - required information about your bundle
metadata:
  name: "{config["name"]}"
  version: "{config["version"]}"
  description: "{config["description"] or "Application bundle with entrypoint"}"

# Entrypoint script that runs when the bundle is applied
entrypoint:
  script: "./scripts/install.sh"
  mode: "0755"

# List of artifacts to include in this bundle
artifacts:
{artifacts}
'''


def _generate_standard_template(config: Dict[str, Any]) -> str:
    """Generate a standard template with balanced features."""
    artifacts = _generate_artifacts_from_config(config)

    entrypoint_section = ""
    if config.get("include_entrypoint"):
        entrypoint_section = """
# Optional entrypoint script that runs when the bundle is applied
entrypoint:
  script: "./scripts/install.sh"
  mode: "0755"
"""

    return f'''# Pakto Manifest Template
# This file defines a bundle of software artifacts for deployment
# See https://github.com/warrical/pakto for documentation

apiVersion: pakto.warrical.com/v1alpha1
kind: Manifest

# Bundle metadata - required information about your bundle
metadata:
  name: "{config["name"]}"
  version: "{config["version"]}"
  description: "{config["description"] or "Standard application bundle"}"

# Optional variables for templating - can be overridden via CLI --var flags
variables:
  environment: "development"
  install_path: "/opt/{config["name"]}"
  config_path: "/etc/{config["name"]}"
{entrypoint_section}
# List of artifacts to include in this bundle
artifacts:
{artifacts}
'''


def _generate_full_template(config: Dict[str, Any]) -> str:
    """Generate a full template with comprehensive features."""
    artifacts = _generate_artifacts_from_config(config)

    return f'''# Pakto Manifest Template
# This file defines a bundle of software artifacts for deployment
# See https://github.com/warrical/pakto for documentation

apiVersion: pakto.warrical.com/v1alpha1
kind: Manifest

# Bundle metadata - required information about your bundle
metadata:
  name: "{config["name"]}"
  version: "{config["version"]}"
  description: "{config["description"] or "Comprehensive application bundle"}"

# Optional variables for templating - can be overridden via CLI --var flags
variables:
  environment: "development"
  app_version: "{config["version"]}"
  database_version: "15.2"
  install_path: "/opt/{config["name"]}"
  config_path: "/etc/{config["name"]}"
  log_path: "/var/log/{config["name"]}"

# Optional entrypoint script that runs when the bundle is applied
entrypoint:
  script: "./scripts/install.sh"
  mode: "0755"
  uid: "{config["name"]}"
  gid: "{config["name"]}"

# List of artifacts to include in this bundle
artifacts:
{artifacts}

# Common artifact types and their usage:
#
# Local files:
#   origin: "./path/to/local/file"
#   target: "/destination/path"
#
# HTTP URLs:
#   origin: "https://example.com/file.zip"
#   target: "/opt/file.zip"
#
# OCI images:
#   origin: "oci://docker.io/library/nginx:latest"
#   target: "nginx.tar"
#
# Template variables can be used in both origin and target paths:
#   origin: "https://api.example.com/v{{ variables.api_version }}/config"
#   target: "{{ variables.config_path }}/config.json"
'''


def _generate_artifacts_from_config(config: Dict[str, Any]) -> str:
    """Generate artifact definitions based on configuration."""
    artifact_count = config.get("artifact_count", 3)
    artifact_types = config.get("artifact_types", ["oci", "oci", "oci"])

    # Ensure we have enough types for the count
    while len(artifact_types) < artifact_count:
        artifact_types.extend(artifact_types[: artifact_count - len(artifact_types)])

    # Truncate if we have too many types
    artifact_types = artifact_types[:artifact_count]

    artifacts = []
    for i, artifact_type in enumerate(artifact_types):
        if artifact_type == "local":
            artifacts.append(f'''  - name: "artifact-{i + 1}"
    origin: "./file-{i + 1}"
    target: "/opt/{config["name"]}/file-{i + 1}"''')
        elif artifact_type == "http":
            artifacts.append(f'''  - name: "artifact-{i + 1}"
    origin: "https://example.com/file-{i + 1}"
    target: "/opt/{config["name"]}/file-{i + 1}"''')
        elif artifact_type == "oci":
            artifacts.append(f'''  - name: "artifact-{i + 1}"
    origin: "oci://docker.io/library/example:{i + 1}.0"
    target: "artifact-{i + 1}.tar"''')
        else:
            # Fallback to oci
            artifacts.append(f'''  - name: "artifact-{i + 1}"
    origin: "oci://docker.io/library/example:{i + 1}.0"
    target: "artifact-{i + 1}.tar"''')

    return "\n".join(artifacts)
