"""
Implementation of the `pakto bundle` command.

This module implements the bundle command that resolves, caches, packs, and pushes bundles
to registries according to the CLI outline specification.
"""

import asyncio
import builtins
import contextlib
import hashlib
import json
import logging
import os
import re
import tempfile
import traceback
from pathlib import Path
from typing import Optional

import click
import yaml

from pakto.cli.context import AppContext
from pakto.commands.init import init
from pakto.core.bundle import Bundle
from pakto.security import SigningService
from pakto.services.unpack import UnpackService

from ..core.clients.oci_native import OciNativeRegistryClient
from .lock import lock
from .pack import pack

logger = logging.getLogger(__name__)


@click.group()
def bundle():
    """Bundle operations."""
    pass


bundle.add_command(init)


def _resolve_registry_reference(
    registry_ref, bundle_name, bundle_version, config_service
):
    """
    Resolve registry reference with intelligent fallbacks following OCI CLI norms.

    Priority:
    1. Explicit registry_ref (full OCI standard: registry.io/repo/name:tag)
    2. Config registry.default + bundle metadata (registry.default/name:version)
    3. Environment variable PAKTO_REGISTRY_DEFAULT + bundle metadata

    Args:
        registry_ref: Explicit registry reference from CLI
        bundle_name: Bundle name from CLI or metadata
        bundle_version: Bundle version from CLI or metadata
        config_service: Config service for defaults

    Returns:
        Full registry reference or None if can't resolve
    """
    # 1. Explicit registry reference (standard OCI way)
    if registry_ref:
        logger.debug("Loading manifest: %s", registry_ref)
        # If it's a complete reference (has both : and / and ends with :tag), use as-is
        if ":" in registry_ref and "/" in registry_ref and registry_ref.count(":") >= 2:
            return registry_ref
        # If it's just registry base, append bundle name:version
        return f"{registry_ref}/{bundle_name}:{bundle_version}"

    # 2. Try config registry.default
    if config_service:
        try:
            config = config_service.config
            if (
                hasattr(config, "registry")
                and hasattr(config.registry, "default")
                and config.registry.default
            ):
                default_registry = config.registry.default.rstrip("/")
                return f"{default_registry}/{bundle_name}:{bundle_version}"
        except Exception:
            pass

    # 3. Try environment variable
    env_registry = os.getenv("PAKTO_REGISTRY_DEFAULT")
    if env_registry:
        env_registry = env_registry.rstrip("/")
        return f"{env_registry}/{bundle_name}:{bundle_version}"

    # 4. No registry found
    return None


def _push_signature_to_registry(
    signature_path: str,
    bundle_registry_ref: str,
    bundle_manifest_digest: Optional[str],
    registry_username: Optional[str] = None,
    registry_password: Optional[str] = None,
    insecure: bool = False,
) -> str:
    """
    Push a signature file to the registry as a separate OCI artifact with proper referrers linking.

    Args:
        signature_path: Path to the local signature file
        bundle_registry_ref: Registry reference of the bundle that was signed
        bundle_manifest_digest: Manifest digest of the pushed bundle
        registry_username: Registry username for authentication
        registry_password: Registry password for authentication
        insecure: Allow insecure HTTP connections

    Returns:
        Registry reference where signature was pushed
    """
    import json
    import tempfile
    from urllib.parse import urlparse

    from oras.provider import Registry

    # Parse the bundle registry reference to construct signature reference
    if "://" not in bundle_registry_ref:
        bundle_registry_ref = f"oci://{bundle_registry_ref}"

    parsed = urlparse(bundle_registry_ref)
    hostname = parsed.netloc.split("/")[0]
    bundle_target = bundle_registry_ref.replace("oci://", "")

    # Create signature reference using the signature file hash
    sig_file_path = Path(signature_path)
    sig_content_text = sig_file_path.read_text()
    sig_content = json.loads(sig_content_text)
    sig_hash = hashlib.sha256(sig_content_text.encode()).hexdigest()[:12]

    # Construct signature target: same repo, but with .sig suffix and hash-based tag
    if ":" in bundle_target:
        repo_part, _tag_part = bundle_target.rsplit(":", 1)
        signature_target = f"{repo_part}:sha256-{sig_hash}.sig"
    else:
        signature_target = f"{bundle_target}:sha256-{sig_hash}.sig"

    # Create registry client
    registry_kwargs = {
        "hostname": hostname,
        "insecure": insecure,
        "auth_backend": "basic",
        "tls_verify": not insecure,
    }

    client = Registry(**registry_kwargs)

    # Set authentication
    if registry_username and registry_password:
        client.auth.set_basic_auth(registry_username, registry_password)

    # Create signature artifact with proper annotations
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_sig_path = Path(temp_dir) / "signature.dsse.json"
        temp_sig_path.write_text(sig_content_text)

        # Create annotations following Pakto project standards and modern signing conventions
        from pakto.core.oci_types import AnnotationKeys

        # Extract signature metadata for proper annotations
        sig_algorithm = "unknown"
        sig_keyid = "unknown"
        if sig_content.get("signatures") and len(sig_content["signatures"]) > 0:
            first_sig = sig_content["signatures"][0]
            sig_keyid = first_sig.get("keyid", "unknown")
            # Detect algorithm from keyid or signature format
            if len(sig_keyid) == 32:  # ed25519 fingerprint length
                sig_algorithm = "ed25519"

        annotation_data = {
            "annotations": {
                "signature.dsse.json": {
                    # Standard OCI annotations
                    AnnotationKeys.TITLE: "signature.dsse.json",
                    AnnotationKeys.DESCRIPTION: "Pakto bundle signature in DSSE format",
                    AnnotationKeys.CREATED: sig_content.get("timestamp", ""),
                    AnnotationKeys.ARTIFACT_TYPE: "application/vnd.dev.pakto.signature.v1+json",
                    # Signature-specific annotations (following sigstore/cosign conventions)
                    "dev.sigstore.signature.format": "dsse",
                    "dev.sigstore.signature.algorithm": sig_algorithm,
                    # Pakto-specific annotations (following project convention)
                    "com.warrical.pakto.signature.version": "1.0",
                    "com.warrical.pakto.signature.type": "bundle",
                    "com.warrical.pakto.signature.keyid": sig_keyid,
                    "com.warrical.pakto.signature.hash": f"sha256:{sig_hash}",
                    # Subject reference (what this signature signs)
                    "dev.sigstore.signature.subject": bundle_target,
                }
            }
        }

        # Add subject digest if available (for referrers API)
        if bundle_manifest_digest:
            annotation_data["annotations"]["signature.dsse.json"][
                "dev.sigstore.signature.subject.digest"
            ] = bundle_manifest_digest

        # Write annotation file
        annotation_file_path = Path(temp_dir) / "annotations.json"
        annotation_file_path.write_text(json.dumps(annotation_data, indent=2))

        # Change to temp directory for push
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Create manifest annotations for the signature artifact
            manifest_annotations = {
                "org.opencontainers.artifact.type": "application/vnd.dev.pakto.signature.v1+json",
                "com.warrical.pakto.signature.type": "dsse",
                "com.warrical.pakto.signature.subject": bundle_target,
            }

            # Add subject digest if available
            if bundle_manifest_digest:
                manifest_annotations["com.warrical.pakto.signature.subject.digest"] = (
                    bundle_manifest_digest
                )

            # Create subject reference for OCI referrers API if we have the bundle digest
            subject = None
            if bundle_manifest_digest:
                from oras.oci import Subject

                # Note: We don't know the exact size, but ORAS should handle this
                subject = Subject(
                    mediaType="application/vnd.oci.image.manifest.v1+json",
                    digest=bundle_manifest_digest,
                    size=1024,  # Approximate size - registry will correct this
                )

            # Push signature artifact using ORAS Registry API
            result = client.push(
                target=signature_target,
                files=["signature.dsse.json"],
                annotation_file=str(annotation_file_path),
                manifest_annotations=manifest_annotations,
                subject=subject,
            )

            logger.debug(f"Signature push result: {result}")

        finally:
            os.chdir(original_cwd)

    return f"oci://{signature_target}"


@bundle.command("build")
@click.option(
    "-f",
    "--file",
    "input_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Input file (auto-detects manifest or lockfile via kind field)",
)
@click.option(
    "-m",
    "--manifest",
    "manifest_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Manifest file (explicit)",
)
@click.option(
    "-l",
    "--lockfile",
    "lockfile_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Lockfile (explicit)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False),
    help="Output bundle file (defaults to {input-name}.bundle)",
)
@click.option(
    "--output-lockfile",
    is_flag=True,
    help="Save generated lockfile alongside bundle (only for manifest input)",
)
@click.option("--var", multiple=True, help="Override variable (key=value) (repeatable)")
@click.pass_context
def build(
    ctx,
    input_file: str,
    manifest_file: str,
    lockfile_file: str,
    output: str,
    output_lockfile: bool,
    var,
):
    """Build a .bundle file from a manifest or lockfile."""

    # Validate mutually exclusive options
    input_options = [input_file, manifest_file, lockfile_file]
    provided_options = [opt for opt in input_options if opt is not None]

    if len(provided_options) == 0:
        msg = "Must specify one input: -f/--file, -m/--manifest, or -l/--lockfile"
        raise click.ClickException(msg)

    if len(provided_options) > 1:
        msg = "Cannot specify multiple input options. Use only one of: -f, -m, -l"
        raise click.ClickException(msg)

    try:
        click.echo("🏗️  Building bundle...")

        # Determine input type and file
        if input_file:
            # Auto-detect based on kind field
            try:
                with open(input_file, "r", encoding="utf-8") as f:
                    content = yaml.safe_load(f)
                    kind = content.get("kind", "").lower()

                if kind == "manifest":
                    manifest_file = input_file
                elif kind == "lockfile":
                    lockfile_file = input_file
                else:
                    msg = f"Unknown or missing 'kind' field in {input_file}. Expected 'manifest' or 'lockfile'"
                    raise click.ClickException(msg)
            except Exception as e:
                msg = f"Failed to parse {input_file}: {e}"
                raise click.ClickException(msg)

        # Get context for directory management
        cc: AppContext = ctx.obj if ctx.obj else AppContext()

        # # Store original context object and set up pack command context
        # original_ctx_obj: PaktoContext = ctx.obj

        # Handle manifest input (generate lockfile internally)
        if manifest_file:
            click.echo("📋 Step 1/3: Generating lockfile from manifest...")

            manifest_path = Path(manifest_file)
            manifest_name = manifest_path.stem.removesuffix(".manifest")
            manifest_dir = manifest_path.parent

            # Generate lockfile using lock command (must run from manifest directory)
            try:
                os.chdir(manifest_dir)
                if output_lockfile:
                    # Let the lock service determine the proper lockfile path based on manifest metadata
                    # Output to current directory (where bundle will be created)
                    ctx.invoke(
                        lock,
                        manifest_file=manifest_path.name,  # Use relative path since we're in the right directory
                        var=var,
                        no_progress=False,
                        output=str(
                            cc.calling_dir
                        ),  # Output to current directory, let service determine filename
                    )
                    # The lock service will determine the proper filename based on manifest metadata
                    # We need to find the generated lockfile in the current directory
                    lockfile_path = None
                    for lockfile in Path(cc.calling_dir).glob("*.pakto.lock.yaml"):
                        lockfile_path = lockfile
                        break
                    if not lockfile_path:
                        msg = "Failed to find generated lockfile"
                        raise click.ClickException(msg)
                else:
                    # Create temporary lockfile
                    temp_lockfile = tempfile.NamedTemporaryFile(
                        encoding="utf-8",
                        mode="w",
                        suffix=".pakto.lock.yaml",
                        delete=False,
                    )
                    lockfile_path = Path(temp_lockfile.name)
                    temp_lockfile.close()

                    ctx.invoke(
                        lock,
                        manifest_file=manifest_path.name,  # Use relative path since we're in the right directory
                        var=var,
                        no_progress=False,
                        output=str(
                            lockfile_path.resolve()
                        ),  # Use absolute path for output
                    )
            finally:
                os.chdir(cc.calling_dir)

            if output_lockfile:
                click.echo(f"✓ Lockfile saved: {lockfile_path}")
            else:
                click.echo("✓ Lockfile generated internally")

        # Handle lockfile input (use directly)
        elif lockfile_file:
            click.echo("📋 Step 1/3: Using provided lockfile...")
            lockfile_path = Path(lockfile_file)
            manifest_name = lockfile_path.stem.removesuffix(".pakto.lock")
            manifest_dir = lockfile_path.parent
            click.echo("✓ Lockfile loaded")

        # Step 2: Create OCI bundle
        click.echo("📦 Step 2/3: Creating OCI bundle...")

        # Create temporary directory for OCI bundle
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_bundle_dir = Path(temp_dir) / f"{manifest_name}-bundle"

            # Create OCI bundle (without pushing)
            # Run from manifest directory to resolve relative script paths
            # Resolve lockfile path before changing directories
            resolved_lockfile_path = lockfile_path.resolve()
            try:
                os.chdir(manifest_dir)
                ctx.invoke(
                    pack,
                    lockfile=str(resolved_lockfile_path),
                    output=str(temp_bundle_dir),
                )
            finally:
                os.chdir(cc.calling_dir)

            click.echo("✓ OCI bundle created")

            # Debug: Log OCI bundle structure before creating .bundle
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            ch.setFormatter(formatter)
            logger.addHandler(ch)

            logger.debug(f"OCI bundle created at: {temp_bundle_dir}")
            logger.debug("OCI bundle structure:")
            for root, _, files in os.walk(temp_bundle_dir):
                level = root.replace(str(temp_bundle_dir), "").count(os.sep)
                indent = " " * 2 * level
                logger.debug(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files[:5]:  # Limit to first 5 files per dir
                    logger.debug(f"{subindent}{file}")

            # Step 3: Convert OCI bundle to .bundle file
            click.echo("📁 Step 3/3: Creating .bundle file...")

            # Determine output filename
            if not output:
                if manifest_file:
                    output = f"{manifest_name}.bundle"
                else:
                    output = f"{manifest_name}.bundle"

            # Create .bundle file from OCI directory
            Bundle.from_oci(str(temp_bundle_dir), output)

            # Clean up temporary lockfile if it was created
            if (
                manifest_file
                and not output_lockfile
                and lockfile_path.name.startswith("tmp")
            ):
                with contextlib.suppress(builtins.BaseException):
                    os.unlink(lockfile_path)

        # Success summary
        click.echo("\n✅ Bundle build completed successfully!")
        click.echo(f"   Bundle: {output}")
        click.echo(f"   Size: {Path(output).stat().st_size / (1024 * 1024):.1f} MB")
        if manifest_file and output_lockfile:
            click.echo(f"   Lockfile: {lockfile_path}")

    except click.ClickException:
        raise
    except Exception as e:
        msg = f"Failed to build bundle: {e}"
        raise click.ClickException(msg)


@bundle.command("pull")
@click.argument("registry_ref", type=str)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False),
    help="Output bundle filename (defaults to {name}-{version}.bundle)",
)
@click.option(
    "--registry-username",
    "-u",
    envvar="PAKTO_REGISTRY_USERNAME",
    help="Registry username",
)
@click.option(
    "--registry-password",
    "-p",
    envvar="PAKTO_REGISTRY_PASSWORD",
    help="Registry password",
)
@click.option(
    "--insecure", "-I", is_flag=True, help="Allow insecure HTTP registry connections"
)
@click.pass_context
def bundle_pull(
    ctx,
    registry_ref: str,
    output: str,
    registry_username: str,
    registry_password: str,
    insecure: bool,
):
    """Pull a bundle from an OCI registry to a local .bundle file."""

    try:
        click.echo(f"📡 Pulling bundle from {registry_ref}")

        # Validate registry reference format
        if (
            not registry_ref.startswith(("oci://", "http://", "https://"))
            and "://" not in registry_ref
        ):
            # Add oci:// prefix if not specified
            registry_ref = f"oci://{registry_ref}"

        # Extract name and version from registry reference for filename
        if not output:
            # Parse registry reference to extract name and version
            # Format: oci://registry.io/repo/name:version
            ref_pattern = r"^oci://(?:[^/]+/)*([^/:]+):(.+)$"
            match = re.match(ref_pattern, registry_ref)

            if match:
                name, version = match.groups()
                output = f"{name}-{version}.bundle"
            else:
                # Fallback to generic name if parsing fails
                output = "bundle.bundle"

        # Handle registry authentication
        if registry_username and not registry_password:
            registry_password = click.prompt("Registry password", hide_input=True)

        # Progress callback for user feedback
        def progress_callback(progress_data):
            if isinstance(progress_data, dict):
                progress_type = progress_data.get("type", "")
                if progress_type == "pull_start":
                    click.echo("📦 Downloading bundle...")
                elif progress_type == "pull_complete":
                    click.echo("✓ Bundle downloaded")
                elif progress_type == "unpack_complete":
                    click.echo("✓ Bundle extracted")

        # Create temporary directory for pulled OCI bundle
        with tempfile.TemporaryDirectory() as temp_dir:
            click.echo("🔄 Pulling OCI bundle from registry...")

            # Pull OCI bundle directly using ORAS

            # Parse registry URL
            if not registry_ref.startswith("oci://"):
                registry_ref = f"oci://{registry_ref}"

            url_parts = registry_ref.replace("oci://", "")
            url_parts.split("/")[0]

            # Create registry client

            registry = OciNativeRegistryClient()

            if registry_username and registry_password:
                # OCI-Native client uses async login
                import asyncio

                asyncio.run(registry.login(registry_username, registry_password))

            # Pull bundle to temporary directory using OCI-Native client
            try:
                logger = logging.getLogger(__name__)
                logger.setLevel(logging.DEBUG)
                ch = logging.StreamHandler()
                ch.setLevel(logging.DEBUG)
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                ch.setFormatter(formatter)
                logger.addHandler(ch)

                logger.debug(f"Pulling from target: {url_parts}")
                logger.debug(f"Output directory: {temp_dir}")

                # OCI-Native client returns OciResult with manifest and layers
                result = asyncio.run(registry.pull(reference=url_parts))

                logger.debug(f"OCI pull result type: {type(result)}")
                logger.debug(f"OCI pull success: {result.success}")

                if not result.success:
                    msg = f"Pull failed: {result.error_message}"
                    raise click.ClickException(msg)

                logger.debug(
                    f"Retrieved manifest with {len(result.layers or [])} layers"
                )

                # Reconstruct OCI bundle structure from pulled data
                temp_path = Path(temp_dir)

                # Create OCI directory structure
                blobs_dir = temp_path / "blobs" / "sha256"
                blobs_dir.mkdir(parents=True, exist_ok=True)

                # Create oci-layout file
                oci_layout = {"imageLayoutVersion": "1.0.0"}
                with open(temp_path / "oci-layout", "w", encoding="utf-8") as f:
                    json.dump(oci_layout, f)

                # Save manifest blob
                manifest_data = json.dumps(
                    result.manifest, separators=(",", ":")
                ).encode()
                manifest_digest = hashlib.sha256(manifest_data).hexdigest()
                (blobs_dir / manifest_digest).write_bytes(manifest_data)

                # Save config blob if present - preserve OCI v1.1.0 empty config
                config_digest = (
                    result.manifest.get("config", {})
                    .get("digest", "")
                    .replace("sha256:", "")
                )
                if config_digest:
                    from ..core.oci_types import OCI_EMPTY_CONFIG_DIGEST

                    # Check if this is the OCI v1.1.0 empty config
                    if (
                        result.manifest.get("config", {}).get("digest")
                        == OCI_EMPTY_CONFIG_DIGEST
                    ):
                        # Write the proper empty config
                        config_data = b"{}"
                    else:
                        # Fallback for other config types
                        config_data = json.dumps(
                            {"architecture": "amd64", "os": "linux"},
                            separators=(",", ":"),
                        ).encode()

                    (blobs_dir / config_digest).write_bytes(config_data)

                # Save layer blobs
                for layer_info in result.layers or []:
                    layer_digest = layer_info["digest"].replace("sha256:", "")
                    layer_data = layer_info["data"]
                    (blobs_dir / layer_digest).write_bytes(layer_data)
                    logger.debug(f"Saved layer {layer_info['type']}: {layer_digest}")

                # Create index.json
                index = {
                    "schemaVersion": 2,
                    "mediaType": "application/vnd.oci.image.index.v1+json",
                    "manifests": [
                        {
                            "mediaType": "application/vnd.oci.image.manifest.v1+json",
                            "digest": f"sha256:{manifest_digest}",
                            "size": len(manifest_data),
                        }
                    ],
                }
                with open(temp_path / "index.json", "w", encoding="utf-8") as f:
                    json.dump(index, f, separators=(",", ":"))

                logger.debug(f"Reconstructed OCI bundle structure in {temp_path}")

                if progress_callback:
                    progress_callback({
                        "type": "pull_complete",
                        "message": "Bundle pulled successfully",
                    })
            except Exception as e:
                logger.error(f"Failed to pull from registry: {e}")
                logger.debug(f"Full error trace:\n{traceback.format_exc()}")
                msg = f"Failed to pull from registry: {e}"
                raise click.ClickException(msg)

            # Verify the OCI structure exists
            oci_bundle_dir = temp_path
            if (
                not (oci_bundle_dir / "oci-layout").exists()
                or not (oci_bundle_dir / "index.json").exists()
            ):
                msg = "Failed to reconstruct OCI bundle structure"
                raise click.ClickException(msg)

            click.echo("📁 Converting to .bundle file...")

            # Create .bundle file from OCI directory
            Bundle.from_oci(str(oci_bundle_dir), output)

        # Success summary
        click.echo("\n✅ Bundle pulled successfully!")
        click.echo(f"   Source: {registry_ref}")
        click.echo(f"   Bundle: {output}")
        click.echo(f"   Size: {Path(output).stat().st_size / (1024 * 1024):.1f} MB")

    except click.ClickException:
        raise
    except Exception as e:
        msg = f"Failed to pull bundle: {e}"
        raise click.ClickException(msg)


@bundle.command("extract")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("output_dir", type=click.Path(file_okay=False))
@click.option(
    "--format",
    type=click.Choice(["oci", "files"]),
    default="files",
    help="Output format: 'files' for final artifacts (default), 'oci' for bundle layout",
)
def extract(bundle_file: str, output_dir: str, format: str):  # noqa: A002
    """Extract a .bundle file to OCI layout or final artifacts."""
    try:
        if format == "files":
            click.echo(f"📦 Extracting bundle {bundle_file} → final artifacts")
        else:
            click.echo(f"📦 Extracting bundle {bundle_file} → OCI layout")

        bundle = Bundle(bundle_file)

        if format == "files":
            extracted_path = bundle.extract_to_final(output_dir)
        else:
            extracted_path = bundle.extract_to_dir(output_dir)

        click.echo(f"✅ Extracted to: {extracted_path}")

    except Exception as e:
        msg = f"Failed to extract bundle: {e}"
        raise click.ClickException(msg)


@bundle.command("info")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def info(bundle_file: str, output_json: bool):
    """Show bundle information without extracting."""
    try:
        bundle = Bundle(bundle_file)
        info = bundle.get_info()

        if output_json:
            click.echo(json.dumps(info.model_dump(), indent=2))
        else:
            click.echo(f"📋 Bundle Info: {bundle_file}")
            click.echo(f"   Name: {info.name}")
            click.echo(f"   Version: {info.version}")
            click.echo(f"   Size: {info.size_human}")
            click.echo(f"   Artifact Total: {info.artifact_count}")
            if info.artifact_names:
                click.echo("   Artifacts:")
                for artifact_name in info.artifact_names:
                    click.echo(f"     - {artifact_name}")
            if info.description:
                click.echo(f"   Description: {info.description}")

    except Exception as e:
        msg = f"Failed to get bundle info: {e}"
        raise click.ClickException(msg)


@bundle.command("sign")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--key",
    "-k",
    envvar="PAKTO_SIGNING_KEY",
    help="Path or ID of the private key to use.",
)
@click.option(
    "--keyless",
    is_flag=True,
    envvar="PAKTO_KEYLESS_SIGNING",
    help="Use keyless signing with sigstore (requires internet)",
)
@click.option(
    "--passphrase",
    envvar="PAKTO_SIGNING_PASSPHRASE",
    help="Passphrase for encrypted key (will prompt if not provided)",
)
@click.pass_context
def sign(ctx, bundle_file: str, key: str, keyless: bool, passphrase: str):
    """Sign a bundle with a private key or keyless signing."""
    try:
        # Get context and config service
        app_ctx: AppContext = ctx.obj if ctx.obj else AppContext()
        config_service = app_ctx.config_service

        click.echo(f"🔏 Signing bundle: {bundle_file}")

        # Validate signing method
        if keyless and key:
            msg = "Cannot specify both --key and --keyless. Choose one signing method."
            raise click.ClickException(msg)

        key_to_use = key
        if not keyless and not key_to_use:
            # Check config for default signing key
            default_key = (
                config_service.get("signing.default_key") if config_service else None
            )
            if default_key:
                key_to_use = default_key
                click.echo(f"Using default signing key from config: {key_to_use}")
            else:
                msg = "Must specify either --key <path_or_id> or --keyless for signing method"
                raise click.ClickException(msg)

        # Check if it is a bundle file
        if not bundle_file.endswith(".bundle"):
            msg = "Bundle file must have .bundle extension"
            raise click.ClickException(msg)

        # Create signing service
        service = SigningService()

        if keyless:
            # TODO: Implement keyless signing with sigstore
            msg = (
                "Keyless signing with sigstore not yet implemented. Use --key for now."
            )
            raise click.ClickException(msg)
        # Key-based signing
        key_path = None
        if Path(key_to_use).is_file():
            key_path = key_to_use
        else:
            # Assume it's a key ID and resolve from keystore
            keystore = app_ctx.keystore
            for k in keystore.list_keys():
                if k.fingerprint.startswith(key_to_use):
                    key_path = str(k.file_path)
                    click.echo(f"Resolved key ID '{key_to_use}' to '{key_path}'")
                    break

        if not key_path:
            msg = f"Could not find key for '{key_to_use}' in keystore '{app_ctx.keystore.store_dir}' or as a file path."
            raise click.ClickException(msg)

        if not passphrase:
            # Check config for passphrase
            config_passphrase = (
                config_service.get("signing.passphrase") if config_service else None
            )
            if config_passphrase:
                passphrase = config_passphrase

        # Sign the bundle
        result = service.sign_key_based(
            bundle=bundle_file, key_path=key_path, passphrase=passphrase
        )

        click.echo("✅ Bundle signed successfully")
        click.echo(f"   Signature: {result.signature_path}")
        click.echo(f"   Algorithm: {result.algorithm}")
        click.echo(f"   Key ID: {result.key_id}")

    except Exception as e:
        msg = f"Failed to sign bundle: {e}"
        raise click.ClickException(msg)


@bundle.command("verify")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--require-signature", is_flag=True, help="Require valid signature for verification"
)
@click.option(
    "--keys-dir",
    help="Directory containing trusted public keys (overrides configured keys_dir)",
)
@click.pass_context
def verify(ctx, bundle_file: str, require_signature: bool, keys_dir: str):
    """Verify bundle integrity and optionally signature."""
    try:
        bundle = Bundle(bundle_file)
        is_valid = bundle.verify_integrity()

        if is_valid:
            click.echo(f"✅ Bundle integrity verified: {bundle_file}")
        else:
            click.echo(f"❌ Bundle integrity check failed: {bundle_file}")
            msg = "Bundle verification failed"
            raise click.ClickException(msg)

        # Check signature if required
        if require_signature:
            app_ctx: AppContext = ctx.obj if ctx.obj else AppContext()
            trusted_keys_dir = keys_dir or app_ctx.config_service.get("keys_dir")

            click.echo("🔍 Verifying signature...")
            if not keys_dir and trusted_keys_dir:
                click.echo(f"Using trusted keys from: {trusted_keys_dir}")

            service = SigningService()

            result = service.verify_key_based(
                bundle=bundle_file, trusted_keys_dir=trusted_keys_dir
            )

            if result.success:
                click.echo(f"✅ Signature verified: {result.message}")
                if result.key_id:
                    click.echo(f"   Key ID: {result.key_id}")
            else:
                click.echo(f"❌ Signature verification failed: {result.message}")
                msg = "Signature verification failed"
                raise click.ClickException(msg)

    except Exception as e:
        msg = f"Failed to verify bundle: {e}"
        raise click.ClickException(msg)


@bundle.command("push")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.argument("registry_ref", required=False, type=str)
@click.option("--name", "-n", help="Bundle name (overrides bundle metadata)")
@click.option("--version", "-v", help="Bundle version (overrides bundle metadata)")
@click.option(
    "--registry-username",
    "-u",
    envvar="PAKTO_REGISTRY_USERNAME",
    help="Registry username",
)
@click.option(
    "--registry-password",
    "-p",
    envvar="PAKTO_REGISTRY_PASSWORD",
    help="Registry password",
)
@click.option(
    "--insecure",
    "-I",
    is_flag=True,
    default=False,
    help="Allow insecure HTTP registry connections",
)
@click.option("--sign", is_flag=True, help="Sign the bundle during push")
@click.option(
    "--key",
    "-k",
    envvar="PAKTO_SIGNING_KEY",
    help="Path or ID of the private key to use for signing",
)
@click.option(
    "--keyless",
    is_flag=True,
    envvar="PAKTO_KEYLESS_SIGNING",
    help="Use keyless signing with sigstore (requires internet)",
)
@click.option(
    "--passphrase",
    envvar="PAKTO_SIGNING_PASSPHRASE",
    help="Passphrase for encrypted key (will prompt if not provided)",
)
@click.pass_context
def push(
    ctx,
    bundle_file: str,
    registry_ref: str,
    name: str,
    version: str,
    registry_username: str,
    registry_password: Optional[str],
    insecure: bool,
    sign: bool,
    key: str,
    keyless: bool,
    passphrase: str,
):
    """Push a .bundle file to an OCI registry. Supports intelligent defaults from config and bundle metadata."""
    try:
        bundle = Bundle(bundle_file)
        lockfile = bundle.get_lockfile()

        # Get config service from context
        app_ctx: AppContext = ctx.obj if ctx.obj else AppContext()
        config_service = app_ctx.config_service

        # Resolve bundle name and version (CLI > bundle metadata > defaults)
        bundle_name = name or lockfile.name or "bundle"
        bundle_version = version or lockfile.version or "latest"

        # Resolve registry reference with intelligent fallbacks
        final_registry_ref = _resolve_registry_reference(
            registry_ref, bundle_name, bundle_version, config_service
        )

        if not final_registry_ref:
            msg = (
                "Registry reference required. Either:\n"
                "  1. Provide: pakto bundle push bundle.tar registry.io/repo/name:tag\n"
                "  2. Configure: registry.default in config file\n"
                "  3. Use short form: pakto bundle push bundle.tar"
            )
            raise click.ClickException(msg)

        # Handle registry authentication with proper precedence: CLI → env vars → config → prompt
        if final_registry_ref:
            # Use config for auth if not provided via CLI or env vars
            if config_service and not registry_username and not registry_password:
                config = config_service.config

                # Extract registry hostname from registry URL
                registry_host = (
                    final_registry_ref.replace("oci://", "").split("/")[0].split(":")[0]
                )

                # Check if we have auth for this registry in config
                if (
                    hasattr(config, "registry")
                    and hasattr(config.registry, "auth")
                    and registry_host in config.registry.auth
                ):
                    auth = config.registry.auth[registry_host]
                    registry_username = registry_username or auth.username
                    registry_password = registry_password or auth.password or auth.token

            # Prompt for password if username provided but password missing
            if registry_username and not registry_password:
                registry_password = click.prompt("Registry password", hide_input=True)

        # Handle signing if requested
        signature_path = None
        if sign:
            click.echo("🔏 Signing bundle...")

            # Validate signing method
            if keyless and key:
                msg = "Cannot specify both --key and --keyless. Choose one signing method."
                raise click.ClickException(msg)

            if not keyless and not key:
                # Check config for default signing key
                default_key = (
                    config_service.get("signing.default_key")
                    if config_service
                    else None
                )
                if default_key:
                    key = default_key
                    click.echo(f"Using default signing key from config: {key}")
                else:
                    msg = "Must specify either --key <path_or_id> or --keyless for signing method"
                    raise click.ClickException(msg)

            # Create signing service
            signing_service = SigningService()

            if keyless:
                # TODO: Implement keyless signing with sigstore
                msg = "Keyless signing with sigstore not yet implemented. Use --key for now."
                raise click.ClickException(msg)
            # Key-based signing
            key_path = None
            if Path(key).is_file():
                key_path = key
            else:
                # Assume it's a key ID and resolve from keystore
                keystore = app_ctx.keystore
                for k in keystore.list_keys():
                    if k.fingerprint.startswith(key):
                        key_path = str(k.file_path)
                        click.echo(f"Resolved key ID '{key}' to '{key_path}'")
                        break

            if not key_path:
                msg = f"Could not find key for '{key}' in keystore '{app_ctx.keystore.store_dir}' or as a file path."
                raise click.ClickException(msg)

            if not passphrase:
                # Check config for passphrase
                config_passphrase = (
                    config_service.get("signing.passphrase") if config_service else None
                )
                if config_passphrase:
                    passphrase = config_passphrase

            # Sign the bundle
            result = signing_service.sign_key_based(
                bundle=bundle_file, key_path=key_path, passphrase=passphrase
            )

            signature_path = result.signature_path
            click.echo(
                f"✓ Bundle signed (Algorithm: {result.algorithm}, Key ID: {result.key_id})"
            )

        # Progress callback for user feedback
        def progress_callback(progress_data):
            if isinstance(progress_data, dict):
                progress_type = progress_data.get("type", "")
                if progress_type == "push_start":
                    click.echo(
                        f"📡 Uploading to {progress_data.get('registry', final_registry_ref)}"
                    )
                elif progress_type == "push_complete":
                    click.echo("✓ Push completed")
                elif progress_type == "push_error":
                    click.echo(f"❌ Push failed: {progress_data['error']}", err=True)

        click.echo(f"🚀 Pushing {bundle_name}:{bundle_version}")

        # Use the OCI-Native client for proper 2-layer structure preservation
        push_result = asyncio.run(
            bundle.push_to_registry_native(
                registry_ref=final_registry_ref,
                registry_username=registry_username,
                registry_password=registry_password,
                insecure=insecure,
                progress_callback=progress_callback,
            )
        )

        # Handle backward compatibility for return value
        if isinstance(push_result, dict):
            registry_ref_result = push_result["registry_ref"]
            manifest_digest = push_result["manifest_digest"]
        else:
            registry_ref_result = push_result
            manifest_digest = None

        # Push signature as separate OCI artifact if signing was enabled
        if signature_path:
            click.echo("📝 Pushing signature...")
            try:
                signature_ref = _push_signature_to_registry(
                    signature_path=signature_path,
                    bundle_registry_ref=final_registry_ref,
                    bundle_manifest_digest=manifest_digest,
                    registry_username=registry_username,
                    registry_password=registry_password,
                    insecure=insecure,
                )
                click.echo(f"✓ Signature pushed: {signature_ref}")
            except Exception as e:
                click.echo(f"⚠️  Failed to push signature to registry: {e}")
                click.echo(f"✓ Signature created locally: {signature_path}")

        click.echo(f"✅ {registry_ref_result}")

    except Exception as e:
        msg = f"Failed to push bundle: {e}"
        raise click.ClickException(msg)


@bundle.command("apply")
@click.argument("bundle_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False),
    help="Output directory (defaults to current directory)",
)
def apply(bundle_file: str, output: str):
    """Apply a bundle - extract artifacts and execute entrypoints."""

    try:
        # Default output to current directory if not specified
        if not output:
            output = "."

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        click.echo(f"🚀 Applying bundle: {bundle_file}")
        click.echo(f"📁 Output directory: {output_path.absolute()}")

        # Create bundle instance
        bundle = Bundle(bundle_file)

        # Progress callback for user feedback
        def progress_callback(progress_data):
            if isinstance(progress_data, dict):
                progress_type = progress_data.get("type", "")
                if progress_type == "extract_metadata":
                    click.echo("📋 Reading bundle metadata...")
                elif progress_type == "lockfile_extracted":
                    lockfile_name = progress_data.get("name", "lockfile")
                    click.echo(f"✓ Extracted: {lockfile_name}")
                elif progress_type == "entrypoint_extracted":
                    entrypoint_name = progress_data.get("name", "entrypoint")
                    click.echo(f"✓ Extracted: {entrypoint_name}")
                elif progress_type == "extract_artifacts":
                    total = progress_data.get("total", 0)
                    click.echo(f"📦 Extracting {total} artifacts...")
                elif progress_type == "artifact_extracted":
                    name = progress_data.get("name", "")
                    count = progress_data.get("count", 0)
                    total = progress_data.get("total", 0)
                    click.echo(f"✓ [{count}/{total}] {name}")
                elif progress_type == "entrypoint_execution":
                    entrypoint_name = progress_data.get("name", "entrypoint")
                    click.echo(f"🏃 Executing: {entrypoint_name}")
                elif progress_type == "entrypoint_completed":
                    click.echo("✓ Entrypoint execution completed")
                elif progress_type == "entrypoint_error":
                    error_msg = progress_data.get("message", "Entrypoint failed")
                    click.echo(f"❌ {error_msg}", err=True)

        # Extract bundle to temporary OCI directory first
        with tempfile.TemporaryDirectory() as temp_dir:
            click.echo("🔄 Extracting bundle...")

            # Extract bundle to OCI format in temp directory
            temp_oci_path = bundle.extract_to_dir(temp_dir)

            # Use UnpackService to apply the bundle (extract artifacts + run entrypoints)
            unpack_service = UnpackService()

            final_output_path, artifact_count = asyncio.run(
                unpack_service.unpack_local_bundle(
                    bundle_path=temp_oci_path,
                    output_path=str(output_path),
                    progress_callback=progress_callback,
                    auto_execute_entrypoint=True,  # Execute entrypoints during apply
                )
            )

        # Success summary
        click.echo("\n✅ Bundle applied successfully!")
        click.echo(f"   Bundle: {bundle_file}")
        click.echo(f"   Output: {final_output_path}")
        click.echo(f"   Files: {artifact_count}")

    except click.ClickException:
        raise
    except Exception as e:
        msg = f"Failed to apply bundle: {e}"
        raise click.ClickException(msg)
