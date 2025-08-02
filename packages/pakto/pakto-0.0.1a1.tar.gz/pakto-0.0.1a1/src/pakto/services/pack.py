"""
Pack Service - Creates OCI bundles from lockfiles with cache integration.

This service coordinates the creation of OCI bundles, ensuring all artifacts
are downloaded through the cache service before bundling.
"""

import asyncio
import gzip
import hashlib
import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple
from urllib.parse import urlparse

import oras.client
import oras.defaults
import oras.oci
import oras.utils
import repro_tarfile as tarfile

from pakto.cli.progress import ProgressEvent, ProgressEventType
from pakto.utils import async_file_checksum, get_app_version

from ..core.commands import FetchArtifactCommand
from ..core.models import LockFile, LockFileArtifact
from ..core.oci_types import (
    AnnotationKeys,
    CompressionTypes,
    LayerTypes,
    MediaTypes,
    create_bundle_annotations,
)
from ..handlers.factory import HandlerFactory
from ..services.cache import CacheResolver
from ..services.lockfile import LockfileService

logger = logging.getLogger(__name__)


@dataclass
class PackProgress:
    """Progress information for pack operations."""

    total_artifacts: int
    downloaded_artifacts: int
    bundled_artifacts: int
    current_artifact: Optional[str] = None
    current_status: str = "initializing"


class PackServiceError(Exception):
    """Base exception for PackService errors."""

    pass


class PackService:
    """
    Service for creating OCI bundles from lockfiles.

    Ensures all artifacts are downloaded through the cache service
    before creating the bundle.
    """

    def __init__(
        self,
        cache_service: Optional[CacheResolver] = None,
        lockfile_service: Optional[LockfileService] = None,
        handler_factory: Optional[HandlerFactory] = None,
    ):
        """
        Initialize the pack service.

        Args:
            cache_service: Service for caching artifacts
            lockfile_service: Service for loading lockfiles
            handler_factory: Factory for creating artifact handlers
        """
        self._cache_service = cache_service or CacheResolver()
        self._handler_factory = handler_factory or HandlerFactory(
            cache_service=self._cache_service
        )
        self._lockfile_service = lockfile_service or LockfileService(
            cache_service=self._cache_service, handler_factory=self._handler_factory
        )

    async def create_bundle(
        self,
        lockfile_path: str,
        output_path: str,
        tag: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[str, int, int]:
        """
        Create an OCI bundle from a lockfile.

        Args:
            lockfile_path: Path to the lockfile
            output_path: Path where the bundle should be created
            tag: Optional bundle version tag
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (bundle_path, layers_created, artifacts_bundled)
        """
        should_pack = True
        # Check if bundle already exists (idempotency)
        bundle_path_obj = Path(output_path)
        if bundle_path_obj.exists() and (bundle_path_obj / "index.json").exists():
            should_pack = False
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.BUNDLE_EXISTS,
                        message=f"✓ Bundle already exists at {output_path}",
                    )
                )

        # Load lockfile
        lockfile = self._lockfile_service.load_lockfile(Path(lockfile_path))

        if tag is None:
            tag = lockfile.version

        progress = PackProgress(
            total_artifacts=len(lockfile.artifacts),
            downloaded_artifacts=0,
            bundled_artifacts=0,
        )

        if should_pack:
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.PACK_START,
                        message=f"📦 Creating OCI bundle from lockfile...\n   Lockfile: {lockfile_path}\n   Artifacts: {progress.total_artifacts} total",
                        total_artifacts=progress.total_artifacts,
                    )
                )

            # Create temporary directory for staging artifacts
            with tempfile.TemporaryDirectory() as staging_dir:
                staging_path = Path(staging_dir)
                logger.debug("Staging directory", extra={"staging_path": staging_path})

                # Download all artifacts through cache
                await self._download_artifacts(
                    lockfile, staging_path, progress, progress_callback, lockfile_path
                )

                # Create the OCI bundle
                bundle_path = await self._create_oci_bundle(
                    lockfile,
                    lockfile_path,
                    staging_path,
                    output_path,
                    tag,
                    progress_callback,
                )

                return (
                    bundle_path,
                    1 + len(lockfile.artifacts),
                    len(lockfile.artifacts),
                )  # 1 metadata layer + 1 layer per artifact

        return (
            str(bundle_path_obj),
            1 + len(lockfile.artifacts),
            len(lockfile.artifacts),
        )

    async def _download_artifacts(
        self,
        lockfile: LockFile,
        staging_dir: Path,
        progress: PackProgress,
        progress_callback: Optional[Callable] = None,
        lockfile_path: Optional[str] = None,
    ) -> None:
        """
        Download all artifacts through the cache service.

        Args:
            lockfile: The lockfile containing artifacts
            staging_dir: Directory to stage downloaded artifacts
            progress: Progress tracking object
            progress_callback: Optional callback for progress updates
            lockfile_path: Path to lockfile for resolving relative paths
        """
        # Create handler factory with lockfile directory as base path
        base_path = None
        if lockfile_path:
            base_path = str(Path(lockfile_path).parent)

        handler_factory = HandlerFactory(
            base_path=base_path, cache_service=self._cache_service
        )

        # Process all artifacts concurrently
        async def process_artifact(artifact):
            """Process a single artifact with progress tracking."""
            # Create target path in staging directory
            target_path = staging_dir / artifact.target.lstrip("/")

            # Make directory creation async
            await asyncio.to_thread(
                target_path.parent.mkdir, parents=True, exist_ok=True
            )

            # Report start
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.ARTIFACT_START,
                        name=artifact.target,
                        message=f"Processing {artifact.target}...",
                    )
                )

            # Hybrid approach: Try cache first, fallback to download
            try:
                # Try to resolve from cache first (fast path)
                resolution = await self._cache_service.resolve_artifact(artifact.origin)

                if (
                    resolution.type == "remote"
                    and resolution.cached_metadata
                    and resolution.cached_metadata.content_hash
                ):
                    # Get cached file path from content store
                    content_store = self._cache_service._content_store
                    cached_file_path = content_store.get_content_path(
                        resolution.cached_metadata.content_hash
                    )

                    if cached_file_path.exists():
                        # Copy from cache (fast path) - make async
                        if progress_callback:
                            progress_callback(
                                ProgressEvent(
                                    event_type=ProgressEventType.ARTIFACT_PROGRESS,
                                    name=artifact.target,
                                    status="copying from cache",
                                )
                            )

                        # Make the copy operation async
                        await asyncio.to_thread(
                            shutil.copy2, cached_file_path, target_path
                        )

                        if progress_callback:
                            progress_callback(
                                ProgressEvent(
                                    event_type=ProgressEventType.ARTIFACT_PROGRESS,
                                    name=artifact.target,
                                    status="copied from cache",
                                )
                            )
                    else:
                        msg = "Cache file missing, will download"
                        raise Exception(msg)
                else:
                    msg = "Not in cache, will download"
                    raise Exception(msg)

            except Exception:
                # Fallback: Download using lockfile data (resilient path)
                if progress_callback:
                    progress_callback(
                        ProgressEvent(
                            event_type=ProgressEventType.ARTIFACT_PROGRESS,
                            name=artifact.target,
                            status="downloading",
                        )
                    )

                handler = handler_factory.get_handler_for_scheme(artifact.type)
                command = FetchArtifactCommand(
                    origin_url=artifact.origin,
                    target_path=str(target_path),
                    expected_checksum=artifact.checksum,
                )

                result = await handler.handle(command)

                if not result.success:
                    msg = f"Failed to fetch artifact {artifact.origin}: {result.error_message}"
                    raise Exception(msg)

            # Verify checksum - make async
            actual_checksum = await async_file_checksum(target_path)

            if actual_checksum != artifact.checksum:
                msg = f"Checksum mismatch for {artifact.origin}: expected {artifact.checksum}, got {actual_checksum}"
                raise Exception(msg)

            # Report completion
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.ARTIFACT_COMPLETE,
                        name=artifact.target,
                        status="complete",
                    )
                )

            return artifact

        # Execute all artifact processing concurrently
        completed_artifacts = await asyncio.gather(
            *[process_artifact(artifact) for artifact in lockfile.artifacts],
            return_exceptions=True,
        )

        # Check for errors
        for i, result in enumerate(completed_artifacts):
            if isinstance(result, Exception):
                artifact = lockfile.artifacts[i]
                msg = f"Failed to process {artifact.origin}: {result!s}"
                raise Exception(msg)

        progress.downloaded_artifacts = len(lockfile.artifacts)

        # Report download completion
        if progress_callback:
            progress_callback(
                ProgressEvent(
                    event_type=ProgressEventType.DOWNLOAD_COMPLETE,
                    message=f"📥 Processing artifacts...\n   All {len(lockfile.artifacts)} artifacts processed",
                )
            )

    async def _create_oci_bundle(
        self,
        lockfile: LockFile,
        lockfile_path: str,
        staging_dir: Path,
        output_path: str,
        tag: str,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Create OCI bundle structure from staged artifacts.

        Args:
            lockfile: The lockfile
            lockfile_path: Path to the original lockfile
            staging_dir: Directory containing staged artifacts
            output_path: Output path for the bundle
            tag: Bundle version tag

        Returns:
            Path to the created bundle
        """
        bundle_path = Path(output_path)
        bundle_path.mkdir(parents=True, exist_ok=True)

        # Create OCI directory structure
        blobs_dir = bundle_path / "blobs" / "sha256"
        blobs_dir.mkdir(parents=True, exist_ok=True)

        # Report bundle assembly start
        if progress_callback:
            progress_callback(
                ProgressEvent(
                    event_type=ProgressEventType.BUNDLE_ASSEMBLY,
                    message="🔧 Assembling OCI bundle...\n   - Creating metadata layer\n   - Packaging artifacts\n   - Writing bundle structure",
                )
            )

        # Create oci-layout file
        await self._create_oci_layout(bundle_path)

        # Create layers
        layers = []
        source_files = []

        # Create metadata layer
        metadata_layer, metadata_file = await self._create_metadata_layer(
            lockfile, progress_callback, lockfile_path
        )
        layers.append(metadata_layer)
        source_files.append(metadata_file)

        # Create individual artifact layers
        (
            artifact_layers,
            artifact_files,
        ) = await self._create_individual_artifact_layers(
            staging_dir, lockfile, progress_callback
        )
        layers.extend(artifact_layers)
        source_files.extend(artifact_files)

        # Create config and manifest
        config_obj, _ = self._create_config(layers)
        manifest = self._create_manifest(
            layers, config_obj, lockfile, lockfile_path, tag=tag
        )

        # Write objects to filesystem
        await self._write_objects_to_filesystem(
            bundle_path, manifest, config_obj, layers, source_files
        )

        # Create index.json
        manifest_digest = await self._write_manifest_and_get_digest(
            bundle_path, manifest
        )
        await self._create_index(bundle_path, manifest_digest)

        return str(bundle_path)

    async def _create_oci_layout(self, bundle_path: Path) -> None:
        """Create the oci-layout file asynchronously."""
        oci_layout = {"imageLayoutVersion": "1.0.0"}
        await asyncio.to_thread(
            lambda: json.dump(
                oci_layout, open(bundle_path / "oci-layout", "w", encoding="utf-8")
            )
        )

    async def _create_metadata_layer(
        self,
        lockfile: LockFile,
        progress_callback: Optional[Callable] = None,
        lockfile_path: Optional[str] = None,
    ) -> Tuple[dict, str]:
        """Create enhanced metadata layer with lockfile and artifact index."""
        # Create temporary directory for metadata
        base_temp = Path(await asyncio.to_thread(tempfile.mkdtemp))
        temp_dir = base_temp / "metadata"
        await asyncio.to_thread(temp_dir.mkdir, parents=True, exist_ok=True)

        try:
            # Write lockfile JSON
            lockfile_data = lockfile.dump_canonical_json()
            lockfile_json_path = os.path.join(temp_dir, "pakto.lock.json")
            await asyncio.to_thread(
                lambda: open(lockfile_json_path, "w", encoding="utf-8").write(
                    lockfile_data
                )
            )

            # Create artifact index for quick lookup
            artifact_index = {
                "version": "1.0",
                "artifact_count": len(lockfile.artifacts),
                "artifacts": [
                    {
                        "name": os.path.basename(a.target),
                        "type": a.type,
                        "target": a.target,
                        "origin": a.origin,
                        "checksum": a.checksum,
                        "blob_digest": getattr(a, "blob_digest", None),
                        "blob_size": getattr(a, "blob_size", None),
                        "metadata": getattr(a, "metadata", {}),
                    }
                    for a in lockfile.artifacts
                ],
            }

            index_path = os.path.join(temp_dir, "artifact-index.json")
            await asyncio.to_thread(
                lambda: json.dump(
                    artifact_index, open(index_path, "w", encoding="utf-8"), indent=2
                )
            )

            # Include entrypoint script if present
            if lockfile.entrypoint and lockfile.entrypoint.script:
                script_path = Path(lockfile.entrypoint.script)

                # Resolve script path relative to current working directory if it's relative
                if not script_path.is_absolute():
                    script_path = Path.cwd() / script_path

                # Report progress
                if progress_callback:
                    progress_callback(
                        ProgressEvent(
                            event_type=ProgressEventType.ENTRYPOINT_VERIFICATION,
                            message=f"Verifying entrypoint script: {script_path.name}",
                            checksum=lockfile.entrypoint.checksum,
                        )
                    )

                # Try cache first
                cached_path = await self._cache_service._content_store.get_content(
                    lockfile.entrypoint.checksum
                )

                if cached_path and cached_path.exists():
                    # Use cached version
                    script_dest = temp_dir / script_path.name
                    await asyncio.to_thread(shutil.copy2, cached_path, script_dest)
                    logger.info(
                        "Retrieved entrypoint script from cache",
                        extra={"entrypoint_checksum": lockfile.entrypoint.checksum},
                    )

                    if progress_callback:
                        progress_callback(
                            ProgressEvent(
                                event_type=ProgressEventType.ENTRYPOINT_RETRIEVED,
                                message="Entrypoint script retrieved from cache",
                                status="cache",
                                checksum=lockfile.entrypoint.checksum,
                            )
                        )
                elif script_path.exists():
                    # Verify checksum
                    actual_checksum = await async_file_checksum(script_path)
                    if actual_checksum != lockfile.entrypoint.checksum:
                        error_msg = (
                            f"Entrypoint script checksum mismatch: "
                            f"expected {lockfile.entrypoint.checksum}, got {actual_checksum}"
                        )
                        logger.error(error_msg)

                        if progress_callback:
                            progress_callback(
                                ProgressEvent(
                                    event_type=ProgressEventType.ENTRYPOINT_ERROR,
                                    message=error_msg,
                                    error="checksum_mismatch",
                                )
                            )

                        msg = f"Entrypoint script {script_path} has been modified"
                        raise PackServiceError(msg)

                    # Copy and cache
                    script_dest = os.path.join(temp_dir, script_path.name)
                    await asyncio.to_thread(shutil.copy2, script_path, script_dest)

                    # Cache for future use
                    await self._cache_service._content_store.store_content(
                        script_path, lockfile.entrypoint.checksum
                    )

                    logger.info(f"Entrypoint script verified and cached: {script_path}")

                    if progress_callback:
                        progress_callback(
                            ProgressEvent(
                                event_type=ProgressEventType.ENTRYPOINT_RETRIEVED,
                                message="Entrypoint script verified and cached",
                                status="verified",
                            )
                        )
                else:
                    error_msg = f"Entrypoint script not found: {script_path}"
                    if progress_callback:
                        progress_callback(
                            ProgressEvent(
                                event_type=ProgressEventType.ENTRYPOINT_ERROR,
                                message=error_msg,
                                error="not_found",
                            )
                        )
                    raise PackServiceError(error_msg)

                # Set appropriate permissions based on mode in lockfile
                if lockfile.entrypoint.mode:
                    try:
                        # Convert mode string (e.g., "0755") to octal
                        mode = int(lockfile.entrypoint.mode, 8)
                        await asyncio.to_thread(os.chmod, script_dest, mode)
                    except (ValueError, OSError):
                        # If mode conversion fails, keep default permissions
                        pass

            # Create tar.gz using deterministic method - archive from base_temp to include metadata/ prefix
            tar_gz_path = await asyncio.to_thread(
                self._create_deterministic_targz, Path(base_temp)
            )

            # Create layer descriptor
            layer = oras.oci.NewLayer(
                tar_gz_path,
                is_dir=False,
                media_type=MediaTypes.APP_METADATA_LAYER,
            )

            # Add enhanced annotations
            layer_contents = "lockfile,artifact-index"
            if lockfile.entrypoint:
                layer_contents += ",entrypoint-script"

            layer["annotations"] = {
                AnnotationKeys.TITLE: "Pakto Bundle Metadata",
                AnnotationKeys.DESCRIPTION: "Lockfile and artifact index for bundle verification",
                AnnotationKeys.LAYER_TYPE: LayerTypes.METADATA,
                AnnotationKeys.LAYER_COMPRESSION: CompressionTypes.GZIP,
                AnnotationKeys.LAYER_MEDIA_TYPE: MediaTypes.APP_METADATA_LAYER,
                AnnotationKeys.LAYER_CONTENTS: layer_contents,
                AnnotationKeys.LOCKFILE_VERSION: lockfile.apiVersion,
                AnnotationKeys.LOCKFILE_ARTIFACT_COUNT: str(len(lockfile.artifacts)),
                AnnotationKeys.METADATA_VERSION_KEY: "1.0",
            }

            return layer, tar_gz_path
        finally:
            await asyncio.to_thread(shutil.rmtree, base_temp)

    async def _create_individual_artifact_layers(
        self,
        staging_dir: Path,
        lockfile: LockFile,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[List[dict], List[str]]:
        """
        Create individual artifact layers for each artifact.

        Args:
            staging_dir: Directory containing staged artifacts
            lockfile: The lockfile with artifact definitions
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (layers, source_files)
        """
        # Report layer creation start
        if progress_callback:
            progress_callback(
                ProgressEvent(
                    event_type=ProgressEventType.BUNDLE_ASSEMBLY,
                    message=f"📦 Creating {len(lockfile.artifacts)} artifact layers...",
                )
            )

        async def create_artifact_layer(artifact, index):
            """Create a layer for an individual artifact asynchronously."""
            # Find the artifact file in staging directory
            artifact_path = staging_dir / artifact.target.lstrip("/")

            if not artifact_path.exists():
                logger.error(f"Artifact file not found: {artifact_path}")
                return None, None

            # Report individual layer creation start
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.LAYER_CREATION_START,
                        name=artifact.target,
                        message=f"Creating layer {index + 1}/{len(lockfile.artifacts)} for {artifact.target}",
                        status=f"creating layer {index + 1}/{len(lockfile.artifacts)}",
                    )
                )

            # Create individual artifact layer
            layer, source_file = await self._create_individual_artifact_layer_async(
                artifact_path, artifact, index, progress_callback
            )

            # Update artifact with blob information
            artifact.blob_digest = layer["digest"]
            artifact.blob_size = layer["size"]

            # Report individual layer completion
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.LAYER_CREATION_COMPLETE,
                        name=artifact.target,
                        message=f"Layer {index + 1}/{len(lockfile.artifacts)} complete for {artifact.target}",
                        status=f"layer {index + 1}/{len(lockfile.artifacts)} complete",
                    )
                )

            return layer, source_file

        # Process all artifacts concurrently
        layer_tasks = [
            create_artifact_layer(artifact, i)
            for i, artifact in enumerate(lockfile.artifacts)
        ]

        results = await asyncio.gather(*layer_tasks, return_exceptions=True)

        layers = []
        source_files = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                artifact = lockfile.artifacts[i]
                msg = f"Failed to create layer for {artifact.origin}: {result!s}"
                raise Exception(msg)
            if result[0] is not None:  # layer, source_file
                layers.append(result[0])
                source_files.append(result[1])

        # Report layer creation completion
        if progress_callback:
            progress_callback(
                ProgressEvent(
                    event_type=ProgressEventType.BUNDLE_ASSEMBLY,
                    message=f"✅ Created {len(layers)} artifact layers",
                )
            )

        return layers, source_files

    async def _create_individual_artifact_layer_async(
        self,
        artifact_path: Path,
        artifact: LockFileArtifact,
        layer_index: int,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[dict, str]:
        """
        Create a layer for an individual artifact asynchronously.

        Args:
            artifact_path: Path to the artifact file
            artifact: Artifact definition
            layer_index: Index of the layer

        Returns:
            Tuple of (layer_descriptor, source_file_path)
        """
        # Create a temporary directory for the artifact
        temp_dir = await asyncio.to_thread(tempfile.mkdtemp)
        temp_path = Path(temp_dir)

        try:
            # Report progress: copying artifact
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.LAYER_CREATION_PROGRESS,
                        name=artifact.target,
                        current=25,
                    )
                )

            # Copy artifact to temp directory with proper name - make async
            artifact_dest = temp_path / Path(artifact.target).name
            await asyncio.to_thread(shutil.copy2, artifact_path, artifact_dest)

            # Report progress: creating tar.gz
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.LAYER_CREATION_PROGRESS,
                        name=artifact.target,
                        current=50,
                    )
                )

            # Create tar.gz using deterministic method - make async
            tar_gz_path = await asyncio.to_thread(
                self._create_deterministic_targz, temp_path
            )

            # Report progress: creating layer descriptor
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.LAYER_CREATION_PROGRESS,
                        name=artifact.target,
                        current=75,
                    )
                )

            # Create layer descriptor
            layer = oras.oci.NewLayer(
                tar_gz_path,
                is_dir=False,
                media_type=MediaTypes.APP_ARTIFACTS_LAYER,
            )

            # Add comprehensive annotations
            layer["annotations"] = {
                AnnotationKeys.TITLE: artifact.name,
                AnnotationKeys.DESCRIPTION: f"Individual artifact: {artifact.name}",
                AnnotationKeys.LAYER_TYPE: LayerTypes.ARTIFACT,
                AnnotationKeys.LAYER_COMPRESSION: CompressionTypes.GZIP,
                AnnotationKeys.LAYER_MEDIA_TYPE: MediaTypes.APP_ARTIFACTS_LAYER,
                # Artifact-specific information
                AnnotationKeys.ARTIFACT_NAME: artifact.name,
                AnnotationKeys.ARTIFACT_TYPE: artifact.type,
                AnnotationKeys.ARTIFACT_TARGET: artifact.target,
                AnnotationKeys.ARTIFACT_ORIGIN: artifact.origin,
                AnnotationKeys.ARTIFACT_CHECKSUM: artifact.checksum,
                AnnotationKeys.ARTIFACT_SIZE: str(artifact.size),
                AnnotationKeys.ARTIFACT_ACTION: artifact.action,
                AnnotationKeys.LAYER_INDEX: str(layer_index),
            }

            # Add blob digest and size if available (for individual mode)
            if artifact.blob_digest:
                layer["annotations"][AnnotationKeys.ARTIFACT_BLOB_DIGEST] = (
                    artifact.blob_digest
                )
            if artifact.blob_size:
                layer["annotations"][AnnotationKeys.ARTIFACT_BLOB_SIZE] = str(
                    artifact.blob_size
                )

            # Report progress: layer creation complete
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.LAYER_CREATION_PROGRESS,
                        name=artifact.target,
                        current=100,
                    )
                )

            return layer, tar_gz_path
        finally:
            # Clean up temp directory asynchronously
            await asyncio.to_thread(shutil.rmtree, temp_dir)

    def _create_config(self, layers: list) -> Tuple[dict, Optional[str]]:
        """Create OCI v1.1.0 compliant empty config for artifacts."""
        from ..core.oci_types import (
            OCI_EMPTY_CONFIG_DIGEST,
            OCI_EMPTY_CONFIG_SIZE,
            MediaTypes,
        )

        # For OCI v1.1.0 artifacts, return empty config descriptor
        config_obj = {
            "mediaType": MediaTypes.OCI_EMPTY,
            "digest": OCI_EMPTY_CONFIG_DIGEST,  # Already includes sha256: prefix
            "size": OCI_EMPTY_CONFIG_SIZE,
        }

        return config_obj, None

    def _create_manifest(
        self,
        layers: list,
        config_obj: dict,
        lockfile: LockFile,
        lockfile_path: str,
        tag: Optional[str] = None,
    ) -> dict:
        """Create OCI manifest with proper annotations."""
        manifest = oras.oci.NewManifest()
        manifest["layers"] = layers
        manifest["config"] = config_obj

        # Add OCI v1.1.0 artifactType field
        manifest["artifactType"] = MediaTypes.BUNDLE_MANIFEST

        # Calculate total size including config
        config_size = config_obj.get("size", 0) if isinstance(config_obj, dict) else 0
        layers_size = sum(layer.get("size", 0) for layer in layers)
        total_size = layers_size + config_size

        # Generate artifact summary
        artifact_summary = self._generate_artifact_summary(lockfile.artifacts)

        # Create annotations using our standard helper
        annotations = create_bundle_annotations(
            lockfile=lockfile,
            description=f"Deployment bundle containing {len(lockfile.artifacts)} artifacts from {len(artifact_summary['types'])} sources",
            manifest_hash=getattr(lockfile, "manifestHash", "unknown"),
            lockfile_hash=self._calculate_lockfile_hash(lockfile),
            artifact_count=len(lockfile.artifacts),
            total_size=total_size,
            bundle_version=tag,
            vendor="Warrical",
            licenses="Apache-2.0",
        )

        # The title is already set by create_bundle_annotations, no need to override

        # Add enhanced annotations
        annotations.update({
            # Pakto schema info
            AnnotationKeys.SCHEMA_VERSION: lockfile.apiVersion,
            AnnotationKeys.LOCKFILE_PATH: os.path.basename(lockfile_path)
            if lockfile_path
            else "unknown",
            # Bundle configuration
            AnnotationKeys.BUNDLE_LAYER_COUNT: str(len(layers)),
            AnnotationKeys.BUNDLE_COMPRESSION: CompressionTypes.GZIP,
            AnnotationKeys.BUNDLE_FORMAT_VERSION: "1.0",
            # Artifact details
            AnnotationKeys.ARTIFACTS_LIST: self._create_artifact_list_annotation(
                lockfile.artifacts
            ),
            AnnotationKeys.ARTIFACTS_TYPES: ",".join(sorted(artifact_summary["types"])),
            AnnotationKeys.ARTIFACTS_TOTAL_SIZE_BYTES: str(
                artifact_summary["total_size"]
            ),
            AnnotationKeys.ARTIFACTS_TOTAL_SIZE_HUMAN: self._human_readable_size(
                artifact_summary["total_size"]
            ),
            # Source information
            AnnotationKeys.SOURCES_COUNT: str(len(artifact_summary["sources"])),
            AnnotationKeys.SOURCES_DOMAINS: ",".join(
                sorted(artifact_summary["sources"])[:5]
            ),  # Top 5 domains
            # Build information
            AnnotationKeys.BUILD_TOOL: "pakto-pack",
            AnnotationKeys.BUILD_TOOL_VERSION: get_app_version(),
        })

        # Add layer-specific annotations
        for i, layer in enumerate(layers):
            layer_type = layer.get("annotations", {}).get(
                AnnotationKeys.LAYER_TYPE, "unknown"
            )
            annotations[AnnotationKeys.layer_annotation(i, "type")] = layer_type
            annotations[AnnotationKeys.layer_annotation(i, "size")] = str(
                layer.get("size", 0)
            )

        manifest["annotations"] = annotations
        manifest["mediaType"] = MediaTypes.OCI_MANIFEST

        return manifest

    async def _write_objects_to_filesystem(
        self,
        bundle_path: Path,
        manifest: dict,
        config_obj: dict,
        layers: list,
        source_files: list,
    ) -> None:
        """Write OCI objects to filesystem asynchronously."""
        blobs_dir = bundle_path / "blobs" / "sha256"

        # Write the OCI v1.1.0 empty config blob
        from ..core.oci_types import OCI_EMPTY_CONFIG_DIGEST

        empty_config_data = b"{}"
        empty_config_filename = OCI_EMPTY_CONFIG_DIGEST.replace("sha256:", "")
        await asyncio.to_thread(
            (blobs_dir / empty_config_filename).write_bytes, empty_config_data
        )

        # Don't update manifest config - it's already set correctly in _create_manifest

        # Write layer blobs
        for layer, source_file in zip(layers, source_files, strict=False):
            if os.path.exists(source_file):
                # Read file asynchronously
                blob_data = await asyncio.to_thread(self._read_file_bytes, source_file)

                layer_digest = layer.get("digest", "").replace("sha256:", "")
                if layer_digest:
                    await asyncio.to_thread(
                        (blobs_dir / layer_digest).write_bytes, blob_data
                    )

                # Clean up source file asynchronously
                await asyncio.to_thread(os.unlink, source_file)

    def _read_file_bytes(self, file_path: str) -> bytes:
        """Read file bytes (helper for async operations)."""
        with open(file_path, "rb") as f:
            return f.read()

    async def _write_manifest_and_get_digest(
        self, bundle_path: Path, manifest: dict
    ) -> str:
        """Write manifest and return its digest asynchronously."""
        blobs_dir = bundle_path / "blobs" / "sha256"

        manifest_data = json.dumps(manifest, separators=(",", ":")).encode()
        manifest_digest = self._calculate_sha256(manifest_data)
        await asyncio.to_thread(
            (blobs_dir / manifest_digest).write_bytes, manifest_data
        )

        return f"sha256:{manifest_digest}"

    async def _create_index(self, bundle_path: Path, manifest_digest: str) -> None:
        """Create index.json file asynchronously."""
        blobs_dir = bundle_path / "blobs" / "sha256"
        manifest_blob_path = blobs_dir / manifest_digest.replace("sha256:", "")

        # Get file size asynchronously
        def get_file_size():
            return manifest_blob_path.stat().st_size

        manifest_size = await asyncio.to_thread(get_file_size)

        index = {
            "schemaVersion": 2,
            "mediaType": MediaTypes.OCI_INDEX,
            "manifests": [
                {
                    "mediaType": MediaTypes.OCI_MANIFEST,
                    "digest": manifest_digest,
                    "size": manifest_size,
                }
            ],
        }

        # Write index.json asynchronously
        def write_index():
            with open(bundle_path / "index.json", "w", encoding="utf-8") as f:
                json.dump(index, f, separators=(",", ":"))

        await asyncio.to_thread(write_index)

    def _calculate_sha256(self, data: bytes) -> str:
        """Calculate SHA256 digest of data."""
        return hashlib.sha256(data).hexdigest()

    def _calculate_lockfile_hash(self, lockfile: LockFile) -> str:
        """Calculate hash of the lockfile content."""
        lockfile_json = lockfile.dump_canonical_json()
        return f"sha256:{self._calculate_sha256(lockfile_json.encode())}"

    def _generate_artifact_summary(self, artifacts: list) -> dict:
        """Generate summary statistics about artifacts."""
        summary = {
            "types": set(),
            "sources": set(),
            "total_size": 0,
            "artifacts_by_type": {},
        }

        for artifact in artifacts:
            # Track types
            summary["types"].add(artifact.type)

            # Track source domains
            if artifact.origin.startswith(("http://", "https://")):
                domain = urlparse(artifact.origin).netloc
                summary["sources"].add(domain)
            elif artifact.type == "oci":
                # Extract registry from OCI references
                # Handle both 'registry.io/path' and 'oci://registry.io/path' formats
                origin = artifact.origin
                origin = origin.removeprefix("oci://")  # Remove 'oci://' prefix

                # Extract registry hostname (before first /)
                registry = origin.split("/")[0]

                # Only add if it looks like a valid registry hostname
                if registry and "." in registry:  # e.g., quay.io, docker.io
                    summary["sources"].add(registry)

            # Count by type
            if artifact.type not in summary["artifacts_by_type"]:
                summary["artifacts_by_type"][artifact.type] = 0
            summary["artifacts_by_type"][artifact.type] += 1

            # Add size from artifact
            if hasattr(artifact, "size") and artifact.size:
                summary["total_size"] += int(artifact.size)

        return summary

    def _create_artifact_list_annotation(self, artifacts: list) -> str:
        """Create a compact artifact listing for annotations."""
        # Create a structured but compact representation
        artifact_list = []

        for artifact in artifacts[:20]:  # Limit to first 20 to avoid huge annotations
            # Format: "name@type:target"
            name = os.path.basename(artifact.target)
            entry = f"{name}@{artifact.type}:{artifact.target}"
            artifact_list.append(entry)

        if len(artifacts) > 20:
            artifact_list.append(f"...and {len(artifacts) - 20} more")

        return ";".join(artifact_list)

    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable format."""
        size_float = float(size_bytes)
        for unit in ["B", "KB", "MB", "GB"]:
            if size_float < 1024.0:
                return f"{size_float:.1f}{unit}"
            size_float /= 1024.0
        return f"{size_float:.1f}TB"

    def _create_deterministic_targz(self, source_dir: Path) -> str:
        """
        Create a tar.gz file with deterministic content.

        Unlike oras.utils.make_targz, this ensures:
        - Consistent file ordering
        - No timestamps
        - Proper relative paths
        - Consistent permissions

        Args:
            source_dir: Directory to archive

        Returns:
            Path to created tar.gz file
        """

        # Create temporary tar.gz file
        fd, tar_gz_path = tempfile.mkstemp(suffix=".tar.gz")
        os.close(fd)

        with (
            open(tar_gz_path, "wb") as f,
            gzip.GzipFile(
                filename="", mode="wb", compresslevel=9, mtime=0, fileobj=f
            ) as gz,
            tarfile.open(fileobj=gz, mode="w") as tar,
        ):
            # Get all files sorted for deterministic ordering
            all_files = sorted(source_dir.rglob("*"))

            for file_path in all_files:
                if file_path.is_file():
                    # Calculate relative path from source_dir
                    rel_path = file_path.relative_to(source_dir)

                    # Create tarinfo with deterministic attributes
                    tarinfo = tar.gettarinfo(str(file_path), arcname=str(rel_path))

                    # Zero out timestamps for determinism
                    tarinfo.mtime = 0
                    tarinfo.uid = 0
                    tarinfo.gid = 0
                    tarinfo.uname = ""
                    tarinfo.gname = ""

                    # Add file to tar
                    with open(file_path, "rb") as f2:
                        tar.addfile(tarinfo, f2)

        return tar_gz_path
