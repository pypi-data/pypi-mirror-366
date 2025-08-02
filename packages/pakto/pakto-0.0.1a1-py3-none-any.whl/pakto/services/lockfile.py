"""
Lockfile service for Pakto manifests.

This module provides lockfile generation functionality including manifest hash
calculation, lockfile serialization, and coordination with handler factories.
"""

import asyncio
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import yaml
from pydantic import ValidationError

from pakto.cli.progress import ProgressEvent, ProgressEventType
from pakto.core.commands import CalculateMetadataCommand

from ..core.models import (
    LockFile,
    LockFileArtifact,
    LockFileEntrypoint,
    Manifest,
    ManifestEntrypoint,
)
from ..handlers.factory import HandlerFactory
from ..services.cache import CacheResolver
from .validation import SchemaValidationError, SchemaValidationService

logger = logging.getLogger()


class LockfileError(Exception):
    """Exception raised during lockfile processing."""

    pass


class LockfileService:
    """
    Service for handling lockfile operations in Pakto manifests.

    This service provides comprehensive lockfile functionality including:
    - Manifest hash calculation
    - Lockfile generation from manifests
    - YAML serialization
    - Integration with handler factories
    """

    def __init__(
        self,
        schema_validator: Optional[SchemaValidationService] = None,
        cache_service: Optional[CacheResolver] = None,
        handler_factory: Optional[HandlerFactory] = None,
    ):
        """Initialize the lockfile service."""
        self.schema_validator = schema_validator or SchemaValidationService()
        self._cache_service = cache_service or CacheResolver()
        self._handler_factory = handler_factory or HandlerFactory(
            cache_service=self._cache_service
        )

    def calculate_manifest_hash(self, manifest: Manifest) -> str:
        """
        Calculate SHA256 hash of the manifest content.

        Args:
            manifest: The Manifest model instance

        Returns:
            SHA256 hash in the format 'sha256:<hash>'
        """
        try:
            # Convert manifest to dict, then to sorted JSON and hash it
            manifest_dict = manifest.model_dump()
            manifest_json = json.dumps(manifest_dict, sort_keys=True)
            sha256_hash = hashlib.sha256(manifest_json.encode("utf-8"))
            return f"sha256:{sha256_hash.hexdigest()}"
        except Exception as e:
            msg = f"Failed to calculate manifest hash: {e}"
            raise LockfileError(msg)

    def determine_lockfile_filename(self, manifest: Manifest) -> str:
        """
        Determine the lockfile name based on manifest metadata or fallback.

        Args:
            manifest: The loaded manifest
            manifest_path: Path to the original manifest file

        Returns:
            Lockfile name following the naming convention
        """
        # iF name is empty, just use pakto.lock.yaml
        if not manifest.metadata.name:
            return "pakto.lock.yaml"
        return f"{manifest.metadata.name.strip()}-{manifest.metadata.version.strip()}.pakto.lock.yaml"

    def determine_lockfile_path(
        self, manifest: Manifest, manifest_path: str, output_path: Optional[str] = None
    ) -> str:
        """
        Determine the output path for the lockfile based on manifest metadata or provided output path.

        Args:
            manifest: The loaded manifest
            manifest_path: Path to the original manifest file
            output_path: Optional custom output path for the lockfile

        Returns:
            Full path where the lockfile should be saved
        """
        try:
            if output_path:
                output_path_obj = Path(output_path)
                lockfile_filename = self.determine_lockfile_filename(manifest)

                # If output_path is a directory (or ends with a slash), combine with lockfile_name
                if output_path_obj.is_dir() or str(output_path).endswith(
                    "/"
                ):  # Convert to string for endswith
                    return str(output_path_obj / lockfile_filename)
                # If it has a suffix similar to a lockfile, assume it's a full path and return as is
                if (
                    output_path_obj.suffix in [".yaml", ".yml"]
                    and ".lock" in output_path_obj.name
                ):
                    return str(output_path_obj)  # Ensure consistent return type
                # If it doesn't look like a file (no extension or doesn't end with known file patterns),
                # treat it as a directory and append the lockfile name
                if not output_path_obj.suffix or output_path_obj.suffix not in [
                    ".yaml",
                    ".yml",
                    ".json",
                ]:
                    return str(output_path_obj / lockfile_filename)
                # Has a file extension, treat as full path
                return str(output_path_obj)
            # No output_path provided, use default location relative to manifest
            lockfile_filename = self.determine_lockfile_filename(manifest)
            return str(Path(manifest_path).parent / lockfile_filename)

        except Exception as e:
            msg = f"Failed to determine lockfile path: {e}"
            raise LockfileError(msg)

    async def generate_lockfile_from_manifest_async(
        self,
        manifest: Manifest,
        handler_factory: Optional[HandlerFactory] = None,
        manifest_path: Optional[str] = None,
        lockfile_path: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> LockFile:
        """
        Generate a lock file from a validated manifest asynchronously.

        This method enables concurrent processing of HTTP artifacts while
        maintaining backwards compatibility for local files.

        Args:
            manifest: The validated Manifest model
            handler_factory: Optional Factory for creating appropriate handlers
            manifest_path: Optional path to the manifest file for resolving relative paths
            lockfile_path: Optional path where the lockfile will be saved (for calculating relative origins)
            progress_callback: Optional async callback for progress updates

        Returns:
            Generated Lockfile model

        Raises:
            LockfileError: If lock file generation fails
        """
        handler_factory = handler_factory or self._handler_factory

        try:
            # Calculate manifest hash
            manifest_hash = self.calculate_manifest_hash(manifest)

            # Process ALL artifacts concurrently through unified handler system
            all_tasks = []
            for artifact in manifest.artifacts:
                handler = handler_factory.get_handler(artifact.origin)
                command = CalculateMetadataCommand(
                    origin=artifact.origin,
                    artifact_name=artifact.name,
                    progress_callback=progress_callback,
                )
                task = handler.handle(command)
                all_tasks.append((artifact, task))

            # Execute all artifact processing concurrently with error resilience
            all_results = []

            # Use gather with return_exceptions=True to handle individual failures gracefully
            task_results = await asyncio.gather(
                *[task for _, task in all_tasks], return_exceptions=True
            )

            # Process results and handle errors
            for (artifact, _), result in zip(all_tasks, task_results, strict=False):
                if isinstance(result, Exception):
                    # Handle individual artifact failure
                    if progress_callback:
                        progress_callback({
                            "type": "download_error",
                            "name": artifact.name,
                            "url": artifact.origin,
                            "error": str(result),
                        })
                    msg = f"Failed to calculate metadata for {artifact.origin}: {result!s}"
                    raise LockfileError(msg)
                if not result.success:
                    # Handle handler-reported failure
                    if progress_callback:
                        progress_callback({
                            "type": "download_error",
                            "name": artifact.name,
                            "url": artifact.origin,
                            "error": result.error_message,
                        })
                    msg = f"Failed to calculate metadata for {artifact.origin}: {result.error_message}"
                    raise LockfileError(msg)
                # Success - add to results
                metadata = {
                    "checksum": result.checksum,
                    "size": result.size,
                    "type": result.type,
                }
                all_results.append((artifact, metadata))

            # Generate lock artifacts from results
            lock_artifacts = []
            for artifact, metadata in all_results:
                if metadata is None:
                    msg = f"Failed to process artifact: {artifact.name}"
                    raise LockfileError(msg)

                # Determine action and type based on handlers
                action = "copy_local"
                artifact_type = metadata.get("type", "file")

                # Calculate the appropriate origin path for the lockfile
                if (
                    lockfile_path
                    and manifest_path
                    and not self._is_remote_url(artifact.origin)
                ):
                    # Calculate relative path from lockfile to source (only for local files)
                    origin_path = self._calculate_relative_origin_path(
                        artifact.origin, manifest_path, lockfile_path
                    )
                else:
                    # For remote URLs or when we don't have enough info, keep original path
                    origin_path = artifact.origin

                # Create lock artifact
                lock_artifact = LockFileArtifact(
                    name=artifact.name,
                    type=artifact_type,
                    action=action,
                    origin=origin_path,
                    target=artifact.target,
                    checksum=metadata["checksum"],
                    size=metadata["size"],
                )
                lock_artifacts.append(lock_artifact)

            # Process entrypoint if present
            lockfile_entrypoint: Optional[LockFileEntrypoint] = None
            if manifest.entrypoint:
                lockfile_entrypoint = await self._process_entrypoint(
                    manifest.entrypoint,
                    manifest_path,
                    handler_factory,
                    progress_callback,
                )

            # Create and return the lock file
            return LockFile(
                name=manifest.metadata.name,
                version=manifest.metadata.version,
                apiVersion=manifest.apiVersion,
                manifestHash=manifest_hash,
                artifacts=lock_artifacts,
                entrypoint=lockfile_entrypoint,
            )

        except Exception as e:
            if isinstance(e, LockfileError):
                raise
            msg = f"Failed to generate lock file: {e}"
            raise LockfileError(msg)

    async def _process_entrypoint(
        self,
        entrypoint: Union[str, ManifestEntrypoint],
        manifest_path: Optional[str],
        handler_factory: HandlerFactory,
        progress_callback: Optional[Callable] = None,
    ) -> Optional[LockFileEntrypoint]:
        """
        Process entrypoint script and calculate checksum and size.

        Args:
            entrypoint: Either a string path or ManifestEntrypoint object
            manifest_path: Path to manifest for resolving relative paths
            handler_factory: Factory for creating handlers
            progress_callback: Optional callback for progress updates

        Returns:
            LockFileEntrypoint with checksum and size, or None if script not found
        """
        try:
            # Extract script path and normalize entrypoint to object format
            if isinstance(entrypoint, str):
                script_path = entrypoint
                mode = "0755"
                uid = None
                gid = None
            else:
                script_path = entrypoint.script
                mode = entrypoint.mode
                uid = entrypoint.uid
                gid = entrypoint.gid

            # Resolve script path relative to manifest if needed
            if manifest_path and not Path(script_path).is_absolute():
                script_path = str(Path(manifest_path).parent / script_path)

            # Log the resolved script path and existence
            logger.info(f"Resolved entrypoint script_path: {script_path}")
            logger.info(f"Entrypoint script exists: {Path(script_path).exists()}")

            # Calculate checksum and size using handler
            # Use the original script path from the manifest, not the resolved path
            original_script_path = (
                entrypoint.script
                if isinstance(entrypoint, ManifestEntrypoint)
                else entrypoint
            )
            handler = handler_factory.get_handler(original_script_path)
            command = CalculateMetadataCommand(
                origin=original_script_path, artifact_name="entrypoint-script"
            )
            result = await handler.handle(command)

            if not result.success:
                msg = f"Failed to process entrypoint script: {result.error_message}"
                raise LockfileError(msg)

            # Report caching progress
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        event_type=ProgressEventType.ENTRYPOINT_CACHING,
                        message=f"Caching entrypoint script: {Path(script_path).name}",
                        checksum=result.checksum,
                    )
                )

            # Cache the entrypoint script asynchronously
            script_path_obj = Path(script_path)
            if script_path_obj.exists():
                cached_path = await self._cache_service._content_store.store_content(
                    script_path_obj, result.checksum
                )
                logger.info(
                    f"Cached entrypoint script {script_path} with checksum {result.checksum}"
                )

                if progress_callback:
                    progress_callback(
                        ProgressEvent(
                            event_type=ProgressEventType.ENTRYPOINT_CACHED,
                            message=f"Entrypoint script cached successfully at {cached_path!s}",
                        )
                    )

                lfe = LockFileEntrypoint(
                    script=script_path,
                    mode=mode,
                    checksum=result.checksum,
                    size=result.size,
                    uid=uid or "",
                    gid=gid or "",
                )
            return lfe

        except Exception as e:
            if isinstance(e, LockfileError):
                raise
            msg = f"Failed to process entrypoint: {e}"
            raise LockfileError(msg)

    def generate_lockfile_yaml(self, lockfile: LockFile) -> str:
        """
        Serialize a Lockfile model to YAML string.

        Args:
            lockfile: The Lockfile model to serialize

        Returns:
            YAML string representation of the lock file

        Raises:
            LockfileError: If serialization fails
        """
        try:
            # Convert to dict and validate against schema before serialization
            lockfile_dict = lockfile.model_dump()

            # Validate against JSON schema
            try:
                self.schema_validator.validate_lockfile(lockfile_dict)
            except SchemaValidationError as e:
                msg = f"Lockfile validation failed: {e}"
                raise LockfileError(msg) from e

            # Delegate YAML serialization to the model
            return lockfile.to_yaml()

        except LockfileError:
            raise
        except Exception as e:
            msg = f"Failed to serialize lock file to YAML: {e}"
            raise LockfileError(msg)

    def _calculate_relative_origin_path(
        self, origin: str, manifest_path: str, lockfile_path: str
    ) -> str:
        """
        Calculate the relative path from the lockfile location to the source file.

        Args:
            origin: Original origin path from the manifest
            manifest_path: Path to the manifest file
            lockfile_path: Path where the lockfile will be saved

        Returns:
            Relative path from lockfile to source file
        """
        try:
            # Convert to Path objects
            manifest_dir = Path(manifest_path).parent
            lockfile_dir = Path(lockfile_path).parent
            origin_path = Path(origin)

            # If origin is absolute, use it as-is
            if origin_path.is_absolute():
                # Calculate relative path from lockfile directory to absolute source
                try:
                    return str(origin_path.relative_to(lockfile_dir))
                except ValueError:
                    # If they don't share a common path, return absolute path
                    return str(origin_path)
            else:
                # Origin is relative to manifest directory, resolve it to absolute first
                absolute_source = manifest_dir / origin_path
                absolute_source = absolute_source.resolve()

                # Now calculate relative path from lockfile directory to source
                try:
                    lockfile_dir_resolved = lockfile_dir.resolve()
                    relative_path = Path.relative_to(
                        absolute_source, lockfile_dir_resolved
                    )
                    return str(relative_path)
                except ValueError:
                    # If they don't share a common path, use os.path.relpath as fallback
                    import os

                    try:
                        return os.path.relpath(
                            str(absolute_source), str(lockfile_dir.resolve())
                        )
                    except ValueError:
                        # Last resort: return absolute path
                        return str(absolute_source)

        except Exception:
            # If anything goes wrong, return the original path
            return origin

    def _is_remote_url(self, origin: str) -> bool:
        """
        Check if the origin is a remote URL (HTTP, HTTPS, etc.).

        Args:
            origin: The origin path to check

        Returns:
            True if origin is a remote URL, False otherwise
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(origin)
            return parsed.scheme in ("http", "https", "ftp", "oci", "s3")
        except Exception:
            return False

    def load_lockfile(self, lockfile_path: Union[str, Path]) -> LockFile:
        """
        Load and validate a lockfile from a YAML file.

        Args:
            lockfile_path: Path to the lockfile YAML file

        Returns:
            Parsed and validated Lockfile model

        Raises:
            LockfileError: If the lockfile cannot be loaded or validated
        """
        lockfile_file = (
            lockfile_path if isinstance(lockfile_path, Path) else Path(lockfile_path)
        )
        try:
            lockfile_data = self.load_lockfile_data(lockfile_file)
            return LockFile(**lockfile_data)
        except ValidationError as e:
            msg = f"Invalid lockfile structure in {lockfile_path}: {e}"
            raise LockfileError(msg) from e

    def load_lockfile_data(self, lockfile_path: Path) -> Dict[str, Any]:
        """
        Load and validate a lockfile from a YAML file.

        Args:
            lockfile_path: Path to the lockfile YAML file

        Returns:
            Parsed and validated Lockfile model
        """
        if not lockfile_path.exists():
            msg = f"Lockfile not found: {lockfile_path}"
            raise LockfileError(msg)

        if lockfile_path.is_dir():
            msg = f"Expected a file path for lockfile, but got a directory: {lockfile_path}"
            raise LockfileError(msg)

        try:
            with lockfile_path.open("r", encoding="utf-8") as f:
                lockfile_data: Dict[str, Any] = yaml.safe_load(f)
                return lockfile_data
        except yaml.YAMLError as e:
            msg = f"Invalid YAML in lockfile {lockfile_path}: {e}"
            raise LockfileError(msg) from e
        except Exception as e:
            if isinstance(e, LockfileError):
                raise
            msg = f"Failed to load lockfile from {lockfile_path}: {e}"
            raise LockfileError(msg) from e
