"""
Unified file handler for local file system operations.

Combines functionality of FileSourceHandler and FileDestinationHandler
into a single handler following the Command/Query pattern.
"""

import hashlib
import shutil
from pathlib import Path

from pakto.core.commands import (
    BaseCommand,
    BaseResult,
    CalculateMetadataCommand,
    CalculateMetadataResult,
    FetchArtifactCommand,
    FetchArtifactResult,
    ValidateTargetCommand,
    ValidateTargetResult,
)

from .base import BaseHandler


class FileHandler(BaseHandler):
    """
    Unified handler for local file system artifacts.

    Handles:
    - Metadata calculation (checksum, size)
    - File copying/fetching
    - Target validation
    """

    def can_handle(self, scheme: str) -> bool:
        """Check if this handler can handle the given scheme."""
        return scheme in ("file", "")  # Empty scheme = local path

    async def handle(self, command: BaseCommand) -> BaseResult:
        """
        Route command to appropriate handler method.

        Args:
            command: Command to execute

        Returns:
            Command execution result
        """
        if isinstance(command, CalculateMetadataCommand):
            return await self._calculate_metadata(command)
        if isinstance(command, FetchArtifactCommand):
            return await self._fetch_artifact(command)
        if isinstance(command, ValidateTargetCommand):
            return await self._validate_target(command)
        msg = f"Unsupported command type: {type(command)}"
        raise ValueError(msg)

    async def _calculate_metadata(
        self, command: CalculateMetadataCommand
    ) -> CalculateMetadataResult:
        """Calculate metadata for a local file."""
        try:
            file_path = self._resolve_path(command.origin)

            if not file_path.exists():
                return CalculateMetadataResult(
                    success=False,
                    checksum="",
                    size=0,
                    type="file",
                    error_message=f"File not found: {command.origin}",
                )

            if not file_path.is_file():
                return CalculateMetadataResult(
                    success=False,
                    checksum="",
                    size=0,
                    type="file",
                    error_message=f"Path is not a file: {command.origin}",
                )

            # Calculate checksum
            checksum = self._calculate_file_checksum(file_path)
            size = file_path.stat().st_size

            return CalculateMetadataResult(
                success=True,
                checksum=checksum,
                size=size,
                type="file",
                cached_path=str(file_path),  # For files, cached_path is the actual path
            )

        except Exception as e:
            return CalculateMetadataResult(
                success=False, checksum="", size=0, type="file", error_message=str(e)
            )

    async def _fetch_artifact(
        self, command: FetchArtifactCommand
    ) -> FetchArtifactResult:
        """Copy a local file to target location."""
        try:
            source_path = self._resolve_path(command.origin_url)
            target_path = Path(command.target_path)

            if not source_path.exists():
                return FetchArtifactResult(
                    success=False,
                    local_path="",
                    checksum="",
                    was_downloaded=False,
                    error_message=f"Source file not found: {command.origin_url}",
                )

            # Check if target already has correct content
            if target_path.exists() and command.expected_checksum:
                existing_checksum = self._calculate_file_checksum(target_path)
                if existing_checksum == command.expected_checksum:
                    return FetchArtifactResult(
                        success=True,
                        local_path=str(target_path),
                        checksum=existing_checksum,
                        was_downloaded=False,
                    )

            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source_path, target_path)

            # Calculate checksum of copied file
            checksum = self._calculate_file_checksum(target_path)

            return FetchArtifactResult(
                success=True,
                local_path=str(target_path),
                checksum=checksum,
                was_downloaded=True,
                bytes_downloaded=target_path.stat().st_size,
            )

        except Exception as e:
            return FetchArtifactResult(
                success=False,
                local_path="",
                checksum="",
                was_downloaded=False,
                error_message=str(e),
            )

    async def _validate_target(
        self, command: ValidateTargetCommand
    ) -> ValidateTargetResult:
        """Validate that a target path is writable."""
        try:
            target_path = self._resolve_path(command.target)

            # Check if parent directory exists and is writable
            if target_path.exists():
                if not target_path.is_file():
                    return ValidateTargetResult(
                        valid=False,
                        error_message=f"Target exists but is not a file: {command.target}",
                    )
                # Check if we can write to existing file
                if not target_path.parent.is_dir():
                    return ValidateTargetResult(
                        valid=False,
                        error_message=f"Parent directory is not a directory: {target_path.parent}",
                    )
            else:
                # Check if we can create the file
                parent = target_path.parent
                if parent.exists() and not parent.is_dir():
                    return ValidateTargetResult(
                        valid=False,
                        error_message=f"Parent path exists but is not a directory: {parent}",
                    )

            return ValidateTargetResult(valid=True)

        except Exception as e:
            return ValidateTargetResult(valid=False, error_message=str(e))

    def _resolve_path(self, path_str: str) -> Path:
        """Resolve a path string to an absolute Path object."""
        # Remove file:// prefix if present
        path_str = path_str.removeprefix("file://")

        path = Path(path_str)

        # Resolve relative to base_path if provided
        if not path.is_absolute() and self._base_path:
            path = Path(self._base_path) / path

        return path.resolve()

    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return f"sha256:{sha256_hash.hexdigest()}"
