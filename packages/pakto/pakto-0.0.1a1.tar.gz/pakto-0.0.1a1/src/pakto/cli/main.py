"""
Main CLI entry point for Pakto.

This module defines the main CLI group and registers available commands.
"""

import importlib.metadata as _ilmd

import click

from pakto.cli.context import CONTEXT_SETTINGS
from pakto.cli.global_group import CliGroup
from pakto.commands.bundle import bundle
from pakto.commands.config import config

from ..commands.keys import keys

_VERSION = _ilmd.version("pakto") if _ilmd.packages_distributions() else "dev"


@click.group(cls=CliGroup, context_settings=CONTEXT_SETTINGS)
@click.version_option(_VERSION, "-V", "--version", prog_name="Pakto")
def main():
    """Pakto CLI - Manage and deploy software artifacts."""


# Register commands
main.add_command(bundle)
main.add_command(keys)
main.add_command(config)
