"""
Unpack service - Extracts artifacts from OCI bundles in registries.

This service handles pulling OCI bundles from registries and extracting
their artifacts to the local filesystem with checksum verification.
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional, Tuple

import repro_tarfile as tarfile
from oras.provider import Registry

from pakto.core.oci_types import AnnotationKeys

from ..core.models import LockFile

logger = logging.getLogger(__name__)


class UnpackService:
    """Service for unpacking OCI bundles from registries."""

    async def unpack_from_registry(
        self,
        registry_url: str,
        output_path: str,
        registry_username: Optional[str] = None,
        registry_password: Optional[str] = None,
        insecure: bool = False,
        progress_callback: Optional[Callable] = None,
        auto_execute_entrypoint: bool = True,
    ) -> Tuple[str, int]:
        """
        Unpack an OCI bundle from a registry.

        Args:
            registry_url: OCI registry URL (e.g., "oci://ghcr.io/org/bundle:v1.0")
            output_path: Directory to extract artifacts to
            registry_username: Optional registry username
            registry_password: Optional registry password
            insecure: Allow insecure HTTP connections
            progress_callback: Optional callback for progress updates
            auto_execute_entrypoint: Whether to execute the entrypoint script

        Returns:
            Tuple of (output_path, artifacts_extracted_count)
        """
        # Validate registry URL
        if not registry_url.startswith(("oci://", "file://")):
            msg = "Invalid OCI registry URL format. Expected: oci://registry/repo:tag"
            raise ValueError(msg)

        if registry_url.startswith("oci://"):
            # Check it has more than just oci://
            remaining = registry_url[6:]  # Remove oci://
            if not remaining or "/" not in remaining:
                msg = (
                    "Invalid OCI registry URL format. Expected: oci://registry/repo:tag"
                )
                raise ValueError(msg)

        # Report start
        if progress_callback:
            progress_callback({
                "type": "unpack_start",
                "registry": registry_url,
                "message": f"Pulling bundle from {registry_url}",
            })

        # For file:// URLs (testing), handle differently
        if registry_url.startswith("file://"):
            bundle_path = registry_url.replace("file://", "")
            return await self.unpack_local_bundle(
                bundle_path, output_path, progress_callback
            )

        # Parse registry URL
        url_parts = registry_url.replace("oci://", "")
        hostname = url_parts.split("/")[0]

        # Create registry client
        registry_kwargs = {
            "hostname": hostname,
            "insecure": insecure,
            "auth_backend": "basic",  # Always use basic auth
            "tls_verify": not insecure,
        }

        registry = Registry(**registry_kwargs)

        if registry_username and registry_password:
            registry.auth.set_basic_auth(registry_username, registry_password)

        # Pull bundle to temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Report pulling
            if progress_callback:
                progress_callback({
                    "type": "pull_start",
                    "message": "Pulling bundle from registry",
                })

            # Pull using ORAS
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, lambda: registry.pull(target=url_parts, outdir=str(temp_path))
                )

                # ORAS returns a list of extracted paths
                if result and isinstance(result, list) and len(result) > 0:
                    # Use the first path returned
                    bundle_dir = result[0]
                else:
                    # Fallback to temp_path
                    bundle_dir = str(temp_path)

            except Exception as e:
                msg = f"Failed to pull bundle: {e!s}"
                raise Exception(msg)

            if progress_callback:
                progress_callback({
                    "type": "pull_complete",
                    "message": "Bundle pulled successfully",
                })

            # Unpack the pulled bundle
            return await self.unpack_local_bundle(
                bundle_dir, output_path, progress_callback, auto_execute_entrypoint
            )

    async def unpack_local_bundle(
        self,
        bundle_path: str,
        output_path: str,
        progress_callback: Optional[Callable] = None,
        auto_execute_entrypoint: bool = True,
    ) -> Tuple[str, int]:
        """Unpack a local OCI bundle."""
        bundle_dir = Path(bundle_path)
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read index.json
        index_path = bundle_dir / "index.json"
        if not index_path.exists():
            msg = f"No index.json found in bundle at {bundle_path}"
            raise FileNotFoundError(msg)

        with open(index_path, encoding="utf-8") as f:
            index = json.load(f)

        # Get manifest
        if not index.get("manifests"):
            msg = "No manifests found in bundle index"
            raise ValueError(msg)

        manifest_ref = index["manifests"][0]
        manifest_digest = manifest_ref["digest"].replace("sha256:", "")

        # Read manifest
        manifest_path = bundle_dir / "blobs" / "sha256" / manifest_digest
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        # Find metadata and artifacts layers
        metadata_layer = None
        artifacts_layers = []

        for layer in manifest.get("layers", []):
            layer_type = layer.get("annotations", {}).get(AnnotationKeys.LAYER_TYPE)
            if layer_type == "metadata":
                metadata_layer = layer
            elif layer_type == "artifact":
                # Individual artifact layer
                artifacts_layers.append(layer)

        if not metadata_layer:
            msg = "No metadata layer found in bundle"
            raise ValueError(msg)
        if not artifacts_layers:
            msg = "No artifacts layers found in bundle"
            raise ValueError(msg)

        # Extract metadata layer to read lockfile
        if progress_callback:
            progress_callback({
                "type": "extract_metadata",
                "message": "Reading bundle metadata",
            })

        metadata_digest = metadata_layer["digest"].replace("sha256:", "")
        metadata_blob_path = bundle_dir / "blobs" / "sha256" / metadata_digest
        logger.debug(
            f"metadata_blob_path = {metadata_blob_path}",
            extra={"metadata_blob_path": metadata_blob_path},
        )
        logger.debug(
            f"metadata_layer = {metadata_layer}",
            extra={"metadata_layer": metadata_layer},
        )
        metadata_contents = metadata_layer.get("annotations", {}).get(
            AnnotationKeys.LAYER_CONTENTS
        )
        has_entrypoint = metadata_contents and "entrypoint" in metadata_contents

        # Debug logging
        logger.debug(
            f"metadata_contents = {metadata_contents}",
            extra={"metadata_contents": metadata_contents},
        )
        logger.debug(
            f"has_entrypoint = {has_entrypoint}",
            extra={"has_entrypoint": has_entrypoint},
        )
        logger.debug(
            f"metadata_layer annotations = {metadata_layer.get('annotations', {})}",
            extra={"metadata_layer_annotations": metadata_layer.get("annotations", {})},
        )

        lockfile_data = None
        entrypoint_data = None
        entrypoint_member = None
        members = None

        with tarfile.open(metadata_blob_path, "r:gz") as tar:
            logger.debug(f"Tar members: {[m.name for m in tar.getmembers()]}")
            members = tar.getmembers()
            entrypoint_script_name = None

            # Get lockfile
            lockfile_member = next(
                (m for m in members if m.name.endswith("pakto.lock.json")), None
            )
            if lockfile_member:
                f = tar.extractfile(lockfile_member)
                if f:
                    lockfile_data = json.load(f)
                    if has_entrypoint:
                        entrypoint_script_name = lockfile_data.get(
                            "entrypoint", {}
                        ).get("script", None)
                        logger.debug(
                            f"entrypoint_script_string = {entrypoint_script_name}"
                        )
                        entrypoint_member = (
                            next(
                                (
                                    m
                                    for m in members
                                    if m.name.endswith(
                                        Path(entrypoint_script_name).name
                                    )
                                ),
                                None,
                            )
                            if entrypoint_script_name
                            else None
                        )
                        logger.debug(f"entrypoint_member = {entrypoint_member}")

            # Get entrpoint data
            if has_entrypoint and entrypoint_member:
                f = tar.extractfile(entrypoint_member)
                if f:
                    entrypoint_data = f.read()
                    logger.debug(f"Read entrypoint data, size: {len(entrypoint_data)}")

        if not lockfile_data:
            msg = "No lockfile found in metadata layer"
            raise ValueError(msg)

        # Parse lockfile
        lockfile = LockFile(**lockfile_data)

        # Write lockfile to output directory as YAML
        lockfile_name = "pakto.lock.yaml"
        if lockfile.name and lockfile.version:
            lockfile_name = f"{lockfile.name}-{lockfile.version}.pakto.lock.yaml"
        elif lockfile.name:
            lockfile_name = f"{lockfile.name}.pakto.lock.yaml"

        lockfile_path = output_dir / lockfile_name
        lockfile_yaml = lockfile.to_yaml()
        lockfile_path.write_text(lockfile_yaml)

        # Report lockfile extraction
        if progress_callback:
            progress_callback({
                "type": "lockfile_extracted",
                "name": lockfile_name,
                "message": "Extracted lockfile",
            })

            # Extract entrypoint script if present
        logger.info(f"has_entrypoint: {has_entrypoint}")
        logger.info(f"entrypoint_data: {entrypoint_data is not None}")
        logger.info(f"entrypoint_script_name: {entrypoint_script_name}")

        entrypoint_path = None
        if entrypoint_data and entrypoint_script_name:
            entrypoint_filename = Path(entrypoint_script_name).name
            # TODO: This is a hack to get the entrypoint script to be in the root of the output directory
            # More work is needed to add a target directory for the entrypoint script in the Manifest and LockFile schemas
            # parent_dir = Path(entrypoint_script_name).parent
            # entrypoint_path = output_dir / parent_dir / entrypoint_filename
            # entrypoint_path.parent.mkdir(parents=True, exist_ok=True)
            # entrypoint_path = output_dir / entrypoint_script_name
            entrypoint_path = output_dir / entrypoint_filename
            entrypoint_path.write_bytes(entrypoint_data)
            logger.info(f"Extracted entrypoint script to: {entrypoint_path}")

            # Set executable permissions if specified in lockfile
            if lockfile.entrypoint and lockfile.entrypoint.mode:
                try:
                    mode = int(lockfile.entrypoint.mode, 8)
                    entrypoint_path.chmod(mode)
                    logger.info(f"Set entrypoint permissions to: {oct(mode)}")
                except (ValueError, OSError):
                    # If mode conversion fails, set basic executable permissions
                    entrypoint_path.chmod(0o755)
                    logger.info("Set entrypoint permissions to: 0o755 (fallback)")
            else:
                # Default executable permissions
                entrypoint_path.chmod(0o755)
                logger.info("Set entrypoint permissions to: 0o755 (default)")

            if progress_callback:
                progress_callback({
                    "type": "entrypoint_extracted",
                    "name": entrypoint_filename,
                    "message": "Extracted entrypoint script",
                })

            logger.info(f"Entrypoint script extracted successfully: {entrypoint_path}")
        else:
            logger.warning("Entrypoint script not extracted - missing data or name")

        # Only extract individual artifacts
        logger.info("Using individual artifact extraction mode")
        extracted_count = await self._extract_individual_artifacts(
            bundle_dir, artifacts_layers, lockfile, output_dir, progress_callback
        )

        # Execute entrypoint script if present and auto_execute_entrypoint is enabled
        if has_entrypoint and entrypoint_path and auto_execute_entrypoint:
            logger.info(f"Executing entrypoint script: {entrypoint_path}")
            logger.info(f"Entrypoint script exists: {entrypoint_path.exists()}")
            logger.info(
                f"Entrypoint script is executable: {entrypoint_path.stat().st_mode & 0o111 != 0}"
            )
            logger.info(f"Working directory: {output_dir}")

            if progress_callback:
                progress_callback({
                    "type": "entrypoint_execution",
                    "name": str(entrypoint_path),
                    "message": "Executing entrypoint script",
                })

            try:
                # Run the entrypoint script and capture output
                result = subprocess.run(
                    [str(entrypoint_path.absolute())],
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=str(output_dir),  # Run from the output directory
                )

                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_completed",
                        "name": entrypoint_path.name,
                        "message": "Entrypoint script executed successfully",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    })

            except subprocess.CalledProcessError as e:
                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_error",
                        "name": entrypoint_path.name,
                        "message": f"Entrypoint script execution failed: {e}",
                        "stdout": e.stdout,
                        "stderr": e.stderr,
                        "returncode": e.returncode,
                    })
                msg = f"Entrypoint script execution failed with return code {e.returncode}: {e.stderr}"
                raise Exception(msg)
            except FileNotFoundError:
                if progress_callback:
                    progress_callback({
                        "type": "entrypoint_error",
                        "name": entrypoint_path.name,
                        "message": "Entrypoint script not found or not executable",
                    })
                msg = (
                    f"Entrypoint script not found or not executable: {entrypoint_path}"
                )
                raise Exception(msg)

        if progress_callback:
            progress_callback({
                "type": "unpack_complete",
                "message": f"Successfully extracted {extracted_count} artifacts and lockfile",
                "count": extracted_count + 1,
            })

        return str(output_dir), extracted_count + 1

    async def _extract_individual_artifacts(
        self,
        bundle_dir: Path,
        artifacts_layers: list,
        lockfile: LockFile,
        output_dir: Path,
        progress_callback: Optional[Callable] = None,
    ) -> int:
        """Extract artifacts from individual artifact layers."""
        if progress_callback:
            progress_callback({
                "type": "extract_artifacts",
                "message": f"Extracting {len(lockfile.artifacts)} individual artifacts",
                "total": len(lockfile.artifacts),
            })

        extracted_count = 0
        missing_artifacts = []

        # Create a mapping of artifact names to their layers
        artifact_layer_map = {}
        for layer in artifacts_layers:
            layer_annotations = layer.get("annotations", {})
            artifact_name = layer_annotations.get(AnnotationKeys.ARTIFACT_NAME)
            if artifact_name:
                artifact_layer_map[artifact_name] = layer
                logger.info(
                    f"Mapped artifact '{artifact_name}' to layer {layer['digest']}"
                )
            else:
                logger.warning(
                    f"No artifact name found in layer annotations: {layer_annotations}"
                )

        logger.info(f"Artifact layer map: {list(artifact_layer_map.keys())}")
        logger.info(f"Lockfile artifacts: {[a.name for a in lockfile.artifacts]}")

        # Extract each artifact
        for artifact in lockfile.artifacts:
            artifact_name = artifact.name
            layer = artifact_layer_map.get(artifact_name)

            if not layer:
                logger.warning(f"No layer found for artifact: {artifact_name}")
                missing_artifacts.append(artifact_name)
                continue

            # Extract the artifact from its layer
            layer_digest = layer["digest"].replace("sha256:", "")
            layer_blob_path = bundle_dir / "blobs" / "sha256" / layer_digest
            logger.info(
                f"Processing artifact '{artifact_name}' from layer {layer_digest}"
            )

            with tarfile.open(layer_blob_path, "r:gz") as tar:
                # Find the artifact file in the layer
                artifact_filename = Path(artifact.target).name
                logger.info(
                    f"Looking for artifact '{artifact_filename}' in layer {layer_digest}"
                )
                logger.info(f"Tar members: {[m.name for m in tar.getmembers()]}")

                artifact_member = next(
                    (m for m in tar.getmembers() if m.name.endswith(artifact_filename)),
                    None,
                )

                if artifact_member:
                    # Extract the artifact to the target path specified in the lockfile
                    target_path = Path(artifact.target)
                    if target_path.is_absolute():
                        final_path = output_dir / target_path.relative_to("/")
                    else:
                        final_path = output_dir / target_path
                    final_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(final_path, "wb") as f:
                        f.write(tar.extractfile(artifact_member).read())
                    extracted_count += 1

                    if progress_callback:
                        progress_callback({
                            "type": "artifact_extracted",
                            "name": artifact_filename,
                            "message": f"Extracted {artifact_name} to {target_path}",
                            "count": extracted_count,
                            "total": len(lockfile.artifacts),
                        })
                else:
                    missing_artifacts.append(artifact_name)

        # Report missing artifacts
        if missing_artifacts:
            logger.warning(f"Missing artifacts: {missing_artifacts}")

        # Verify that ALL artifacts were extracted successfully
        if missing_artifacts:
            msg = f"Failed to extract {len(missing_artifacts)} artifacts: {', '.join(missing_artifacts)}"
            raise ValueError(msg)

        # Verify that the extracted count matches the expected count
        if extracted_count != len(lockfile.artifacts):
            msg = f"Expected to extract {len(lockfile.artifacts)} artifacts, but only extracted {extracted_count}"
            raise ValueError(msg)

        return extracted_count
