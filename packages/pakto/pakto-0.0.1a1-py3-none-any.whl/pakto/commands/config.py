import json

import click

from pakto.cli.context import AppContext
from pakto.services.config import ConfigService


@click.group()
def config():
    """View and manage configuration settings."""
    pass


@config.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def config_list(ctx, output_json):
    """List all configuration values."""
    app_ctx: AppContext = ctx.obj
    config_service = app_ctx.config_service

    resolved_config = config_service.list()

    if output_json:
        output = {
            "config_file": str(config_service.config_file)
            if config_service.config_file
            else "N/A",
            "settings": resolved_config,
        }
        click.echo(json.dumps(output, indent=2))
    else:
        if config_service.config_file:
            click.echo(f"Configuration file: {config_service.config_file}")
        else:
            click.echo("No configuration file loaded.")

        click.echo("\nCurrent configuration settings:")
        for key, value in resolved_config.items():
            click.echo(f"  {key}: {value}")


@config.command("get")
@click.argument("key")
@click.pass_context
def config_get(ctx, key):
    """Get a specific configuration value."""
    app_ctx: AppContext = ctx.obj
    config_service: ConfigService = app_ctx.config_service

    value = config_service.get(key)

    if value is not None:
        click.echo(value)
    else:
        click.echo(f"Error: Key '{key}' not found.", err=True)
        ctx.exit(1)


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx, key, value):
    """Set a configuration value persistently."""
    app_ctx: AppContext = ctx.obj
    config_service: ConfigService = app_ctx.config_service

    try:
        # Attempt to convert value to a more specific type if possible
        if value.lower() in ["true", "false"]:
            value = value.lower() == "true"
        elif value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string
    except AttributeError:
        pass  # Value is not a string, leave as is

    config_service.set(key, value)
