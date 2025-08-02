"""Key management commands for bundle signing."""

import json
from pathlib import Path
from typing import Optional

import click
from cryptography.hazmat.primitives import serialization

from pakto.cli.context import AppContext
from pakto.security.keys import KeyStore

from ..security.utils import load_private_key


@click.group()
def keys():
    """Offline key-pair management."""
    pass


@keys.command("generate")
@click.option(
    "--algo",
    type=click.Choice(["ed25519", "rsa"]),
    default="ed25519",
    help="Algorithm to use",
)
@click.option("--passphrase", help="Passphrase (leave empty for prompt)")
@click.option("--output", "-o", help="Output key file path")
@click.pass_context
def generate_key(
    ctx: click.Context, algo: str, passphrase: Optional[str], output: Optional[str]
):
    """Create a new key-pair and store it encrypted."""
    try:
        # Prompt for passphrase if not provided
        if not passphrase:
            passphrase = click.prompt(
                "Enter passphrase for private key",
                hide_input=True,
                confirmation_prompt=True,
            )

        # Get KeyStore from context
        app_ctx: AppContext = ctx.obj
        keystore: KeyStore = app_ctx.keystore

        # Generate key
        key_meta = keystore.generate(
            algo=algo, passphrase=passphrase, output_path=output
        )

        click.echo("✅ Key pair generated successfully!")
        click.echo(f"   Algorithm: {key_meta.algo}")
        click.echo(f"   Key ID: {key_meta.fingerprint}")
        click.echo(f"   Private key: {key_meta.file_path}")
        click.echo(f"   Public key: {key_meta.file_path}.pub")
        click.echo(f"   Created: {key_meta.created}")

    except Exception as e:
        msg = f"Failed to generate key: {e}"
        raise click.ClickException(msg)


@keys.command("list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.pass_context
def list_keys(ctx: click.Context, output_json: bool):
    """List keys in the configured keystore directory."""
    try:
        # Get KeyStore from context
        app_ctx: AppContext = ctx.obj
        keystore: KeyStore = app_ctx.keystore

        # List keys
        keys_found = keystore.list_keys()

        if output_json:
            # Convert to dict for JSON serialization
            keys_data = [key.model_dump() for key in keys_found]
            click.echo(json.dumps(keys_data, indent=2))
        else:
            if not keys_found:
                click.echo(f"No keys found in {keystore.store_dir}")
            else:
                click.echo(f"Keys found in {keystore.store_dir}:")
                for key_meta in keys_found:
                    status = "🔒" if key_meta.encrypted else "🔓"
                    click.echo(f"  {status} {key_meta.file_path}")
                    click.echo(f"      Algorithm: {key_meta.algo}")
                    click.echo(f"      Key ID: {key_meta.fingerprint}")
                    click.echo(f"      Created: {key_meta.created}")

    except Exception as e:
        msg = f"Failed to list keys: {e}"
        raise click.ClickException(msg)


@keys.command("export")
@click.argument("key_file", type=click.Path(exists=True))
@click.option("--armor/--no-armor", default=True, help="Output ASCII-armored PEM")
def export_public_key(key_file: str, armor: bool):
    """Export public key from private key file."""
    try:
        key_path = Path(key_file)

        # Load private key (may prompt for passphrase)
        passphrase = None
        try:
            private_key = load_private_key(key_path, None)
        except Exception:
            passphrase = click.prompt(
                "Enter passphrase for private key", hide_input=True
            )
            private_key = load_private_key(key_path, passphrase)

        # Export public key
        public_key = private_key.public_key()

        if armor:
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            click.echo(public_pem.decode())
        else:
            public_der = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            click.echo(public_der.hex())

    except Exception as e:
        msg = f"Failed to export public key: {e}"
        raise click.ClickException(msg)
