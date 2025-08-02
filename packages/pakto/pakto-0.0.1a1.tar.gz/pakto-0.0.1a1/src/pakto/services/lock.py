"""
Generate service for Pakto workflows.

This module provides the GenerateService that orchestrates the complete
manifest processing and lockfile generation workflow using handlers and services.
"""

import os
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

from ..core.models import LockFile
from ..handlers.factory import HandlerFactory
from .cache import CacheResolver
from .lockfile import LockfileService
from .manifest import ManifestService
from .templating import TemplatingService


class LockError(Exception):
    """Exception raised during generate workflow."""

    pass


class LockService:
    """
    Service for orchestrating the complete lockfile workflow.

    This service coordinates all the components to process manifests
    and generate lockfiles with proper variable resolution and templating.
    """

    def __init__(
        self,
        templating_service: Optional[TemplatingService] = None,
        manifest_service: Optional[ManifestService] = None,
        lockfile_service: Optional[LockfileService] = None,
        handler_factory: Optional[HandlerFactory] = None,
        cache_service: Optional[CacheResolver] = None,
    ):
        """Initialize the generate service with all required components."""
        self.templating_service = templating_service or TemplatingService()
        self.manifest_service = manifest_service or ManifestService()
        self.lockfile_service = lockfile_service or LockfileService()
        self.cache_service = cache_service or CacheResolver()
        self.handler_factory = handler_factory or HandlerFactory(
            cache_service=self.cache_service
        )
        self.parsed_cli_variables: Optional[Dict[str, str]] = None

    async def generate_lockfile_async(
        self,
        manifest_file: str,
        cli_variables: Optional[Tuple[str, ...]] = None,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> Tuple[str, LockFile]:
        """
        Generate a lockfile from a manifest asynchronously with concurrent downloads.

        This method enables concurrent processing of HTTP artifacts while maintaining
        backwards compatibility for local files. It uses the async lockfile generation
        method for improved performance.

        Args:
            manifest_path: Path to the manifest YAML file
            cli_variables: Optional tuple of "key=value" CLI variable strings
            output_path: Optional custom output path for the lockfile
            progress_callback: Optional async callback for progress updates

        Returns:
            Tuple of (lockfile_path, Lockfile model)

        Raises:
            GenerateError: If lockfile generation fails
        """
        try:
            # Parse CLI variables if provided
            parsed_cli_variables = None
            if cli_variables:
                parsed_cli_variables = self.templating_service.parse_variables(
                    cli_variables
                )
                self.parsed_cli_variables = parsed_cli_variables  # Store for later use

            # Load and process the manifest
            manifest = self.manifest_service.load_manifest_from_file(
                manifest_file, self.templating_service, parsed_cli_variables
            )

            # Update the existing handler factory with the manifest directory as base path
            manifest_dir = Path(manifest_file).parent
            self.handler_factory.base_path = str(manifest_dir)

            # Determine output directory and file path first
            lockfile_path = self.lockfile_service.determine_lockfile_path(
                manifest, manifest_file, output_path
            )

            # Generate the lockfile asynchronously with the cache-aware handler factory
            lockfile: LockFile = (
                await self.lockfile_service.generate_lockfile_from_manifest_async(
                    manifest,
                    self.handler_factory,
                    manifest_file,
                    lockfile_path,
                    progress_callback,
                )
            )

            # Serialize to YAML and write to file
            lockfile_yaml = self.lockfile_service.generate_lockfile_yaml(lockfile)

            # Ensure the output directory exists
            Path(lockfile_path).parent.mkdir(parents=True, exist_ok=True)
            with open(lockfile_path, "w", encoding="utf-8") as f:
                f.write(lockfile_yaml)

            return lockfile_path, lockfile

        except Exception as e:
            if isinstance(e, LockError):
                raise
            msg = f"Failed to generate lockfile: {e} in {os.getcwd()}"
            raise LockError(msg) from e
