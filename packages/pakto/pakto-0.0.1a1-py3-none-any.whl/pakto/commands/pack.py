"""
Implementation of the `pakto pack` command.

This module implements the CLI command for creating OCI bundles from lock files,
using the Command Handler pattern with ORAS integration for registry operations.
"""

import asyncio
from typing import Optional

import click

from pakto.cli.context import AppContext
from pakto.cli.progress import ProgressDisplay, create_progress_callback

from ..handlers.pack import PackCommand, PackCommandHandler


class PackError(Exception):
    """Exception raised during pack operations."""

    pass


@click.command(hidden=True)
@click.argument("lockfile", type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output bundle directory (default: auto-generated)",
)
@click.option(
    "--push", help="Push to registry after creating bundle (registry:tag format)"
)
@click.option(
    "--tag", help="Override the bundle version (default: use lockfile version)"
)
@click.option(
    "--registry-username",
    help="Registry username (can also use PAKTO_REGISTRY_USERNAME env var)",
)
@click.option(
    "--registry-password",
    help="Registry password (can also use PAKTO_REGISTRY_PASSWORD env var)",
)
@click.option(
    "--insecure", is_flag=True, help="Allow insecure HTTP registry connections"
)
@click.option(
    "--no-progress", is_flag=True, help="Disable progress display for downloads"
)
@click.pass_context
def pack(
    ctx,
    lockfile: str,
    output: Optional[str] = None,
    push: Optional[str] = None,
    tag: Optional[str] = None,
    registry_username: Optional[str] = None,
    registry_password: Optional[str] = None,
    insecure: bool = False,
    no_progress: bool = False,
):
    """
    Create OCI bundle from a lock file.

    LOCKFILE is the path to the Pakto lock file (.lock.yaml).

    This command creates an OCI-compliant bundle containing all artifacts
    defined in the lock file. The bundle can be used for distribution,
    storage, or deployment to OCI-compatible registries.

    Examples:

        pakto pack myapp.lock.yaml

        pakto pack myapp.lock.yaml --output ./dist/myapp-bundle

        pakto pack myapp.lock.yaml --tag v1.2.3

        pakto pack myapp.lock.yaml --push ghcr.io/org/myapp:v1.0

        pakto pack myapp.lock.yaml --push localhost:8080/pakto/bundle:v1.0.0 --registry-username admin --insecure

        pakto pack myapp.lock.yaml --push localhost:8443/pakto/bundle:v1.0.0 --registry-username admin

        pakto pack myapp.lock.yaml --no-progress  # Disable download progress
    """
    # Get config service from context
    cc: AppContext = ctx.obj if ctx.obj else AppContext()
    config_service = cc.config_service

    # Use config to provide defaults
    if config_service:
        config = config_service.config

        # If pushing and no explicit registry URL, use default from config
        # TODO: This is a hack and should not be present in production code
        if push and not any(
            push.startswith(prefix)
            for prefix in [
                "http://",
                "https://",
                "localhost:",
                "ghcr.io/",
                "docker.io/",
            ]
        ):
            # push might be just ":tag" or "repo:tag"
            if config.registry.default:
                # Prepend default registry if push doesn't look like a full URL
                if push.startswith(":"):
                    # Just a tag like ":v1.0"
                    push = f"{config.registry.default}/pakto/bundle{push}"
                elif "/" not in push:
                    # Just repo:tag like "myapp:v1.0"
                    push = f"{config.registry.default}/{push}"

        # Use auth from config if not provided via CLI
        if push and not registry_username and not registry_password:
            # Extract registry hostname from push URL
            registry_host = push.split("/")[0].split(":")[0]

            # Check if we have auth for this registry
            if registry_host in config.registry.auth:
                auth = config.registry.auth[registry_host]
                registry_username = registry_username or auth.username
                registry_password = registry_password or auth.password or auth.token

    # Handle registry authentication if pushing
    if push:
        # Prompt for password if username provided but password missing
        if registry_username and not registry_password:
            registry_password = click.prompt("Registry password", hide_input=True)

        # Validate registry URL format
        if not (":" in push and "/" in push):
            msg = "Registry URL must be in format 'host:port/repo:tag'"
            raise click.BadParameter(msg)

    async def async_pack():
        # Setup progress display unless disabled
        progress_callback = None
        display = None  # Initialize display to None
        if not no_progress:
            display = ProgressDisplay()
            progress_callback = create_progress_callback(display)
            display.start()

        try:
            # Create pack command
            command = PackCommand(
                lockfile_path=lockfile,
                output_path=output or "./bundle",
                registry_ref=push,
                tag=tag,
                registry_username=registry_username,
                registry_password=registry_password,
                insecure=insecure,
            )

            # Execute pack operation using command handler
            pack_handler = PackCommandHandler()
            result = await pack_handler.handle(
                command, progress_callback=progress_callback
            )

            # Stop progress display before printing results
            if (
                display and display.progress
            ):  # Check if display was initialized and started
                display.stop()

            click.echo(f"✓ Bundle created: {result.bundle_path}")
            click.echo(f"  - {result.artifacts_bundled} artifact(s) processed")
            click.echo(f"  - {result.layers_created} layer(s) created")
            if push:
                click.echo(f"  - Pushed to: {push}")

        finally:
            # Ensure display is stopped even on error
            if (
                display and display.progress
            ):  # Check if display was initialized and started
                display.stop()

    try:
        asyncio.run(async_pack())

    except PackError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from e
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise click.Abort() from e


if __name__ == "__main__":
    pack()
