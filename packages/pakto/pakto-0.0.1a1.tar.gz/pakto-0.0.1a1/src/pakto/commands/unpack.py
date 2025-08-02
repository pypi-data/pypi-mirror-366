"""
Implementation of the `pakto unpack` command.

Extracts artifacts from OCI bundles stored in registries.
"""

import asyncio
from typing import Optional

import click

from ..services.unpack import UnpackService


@click.command(name="fetch")
@click.argument("registry_url")
@click.option(
    "--output", "-o", required=True, help="Output directory for extracted artifacts"
)
@click.option(
    "--registry-username", envvar="PAKTO_REGISTRY_USERNAME", help="Registry username"
)
@click.password_option(
    "--registry-password", envvar="PAKTO_REGISTRY_PASSWORD", help="Registry password"
)
@click.option(
    "--insecure", is_flag=True, help="Allow insecure HTTP registry connections"
)
@click.pass_context
def unpack(
    ctx: click.Context,
    registry_url: str,
    output: str,
    registry_username: Optional[str] = None,
    registry_password: Optional[str] = None,
    insecure: bool = False,
):
    """
    Fetch a Pakto Bundle from a registry

    REGISTRY_URL is the OCI registry URL (e.g., oci://ghcr.io/org/bundle:v1.0)

    Examples:

        pakto unpack oci://ghcr.io/org/tools:v1.0 -o ./tools

        pakto unpack oci://localhost:8080/bundle:latest -o ./extracted --insecure
    """
    click.echo(f"Fetching bundle from: {registry_url}")

    # Get config service from context
    config_service = ctx.obj.get("config_service") if ctx.obj else None

    # Use config for auth if not provided via CLI
    if config_service and not registry_username and not registry_password:
        config = config_service.get()

        # Extract registry hostname from URL
        # Handle both 'oci://registry.io/path' and 'registry.io/path' formats
        url = registry_url
        url = url.removeprefix("oci://")  # Remove 'oci://' prefix

        registry_host = url.split("/")[0].split(":")[0]

        # Check if we have auth for this registry
        if registry_host in config.registry.auth:
            auth = config.registry.auth[registry_host]
            registry_username = registry_username or auth.username
            registry_password = registry_password or auth.password or auth.token

    # Prompt for password if username provided but password missing
    if registry_username and not registry_password:
        registry_password = click.prompt("Registry password", hide_input=True)

    # Progress callback
    def progress_callback(event):
        event_type = event.get("type", "")

        if event_type == "unpack_start":
            click.echo(f"🔍 {event['message']}")
        elif event_type == "pull_start":
            click.echo("📦 Pulling bundle from registry...")
        elif event_type == "pull_complete":
            click.echo("✓ Bundle pulled successfully")
        elif event_type == "extract_metadata":
            click.echo("📖 Reading bundle metadata...")
        elif event_type == "lockfile_extracted":
            click.echo(f"  ✓ {event['name']} (lockfile)")
        elif event_type == "extract_artifacts":
            click.echo(f"🗃️  Extracting {event['total']} artifacts...")
        elif event_type == "artifact_extracted":
            click.echo(f"  ✓ {event['name']} ({event['count']}/{event['total']})")
        elif event_type == "artifact_missing":
            click.echo(f"  ⚠️  {event['message']}", err=True)
        elif event_type == "checksum_error":
            click.echo(f"  ❌ Checksum mismatch for {event['name']}", err=True)
        elif event_type == "unpack_complete":
            click.echo(f"\n✓ {event['message']}")

    # Create service and unpack
    service = UnpackService()

    try:
        # Run the async unpack operation
        output_path, count = asyncio.run(
            service.unpack_from_registry(
                registry_url=registry_url,
                output_path=output,
                registry_username=registry_username,
                registry_password=registry_password,
                insecure=insecure,
                progress_callback=progress_callback,
            )
        )

        click.echo(f"✓ Bundle fetched successfully to: {output_path}")
        click.echo(f"  - {count} item(s) extracted")

    except Exception as e:
        click.echo(f"❌ Fetch failed: {e!s}", err=True)
        ctx.exit(1)
