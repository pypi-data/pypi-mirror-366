"""
Pack command handler for creating OCI bundles from lockfiles.

This module implements the Command Handler pattern for pack operations,
creating OCI-compliant bundles from Pakto lockfiles.

Architecture Notes:
- OCIBundler: Current custom implementation for OCI bundle creation
- Future: Will be replaced with ORAS (OCI Registry As Storage) client
- OCIBundlerInterface: Abstraction layer to facilitate ORAS integration
"""

from dataclasses import dataclass
from typing import Callable, Optional

from ..services.pack import PackService


@dataclass
class PackCommand:
    """Command object for pack operations."""

    lockfile_path: str
    output_path: str
    registry_ref: Optional[str] = None
    tag: Optional[str] = None
    registry_username: Optional[str] = None
    registry_password: Optional[str] = None
    insecure: bool = False


@dataclass
class PackResult:
    """Result object for pack operations."""

    bundle_path: str
    layers_created: int
    artifacts_bundled: int


class PackCommandHandler:
    """Command handler for pack operations following the Command Handler pattern."""

    def __init__(
        self,
        pack_service: Optional[PackService] = None,
    ):
        """
        Initialize the pack command handler.

        Args:
            pack_service: Service for creating bundles with cache integration
        """
        self.pack_service = pack_service or PackService()

    async def handle(
        self, command: PackCommand, progress_callback: Optional[Callable] = None
    ) -> PackResult:
        """
        Handle a pack command to create an OCI bundle.

        Args:
            command: The pack command to execute
            progress_callback: Optional callback for progress updates

        Returns:
            Result containing bundle information

        Raises:
            Exception: If pack operation fails
        """
        # Create the OCI bundle using PackService (which downloads through cache and optionally pushes)
        (
            bundle_path,
            layers_created,
            artifacts_bundled,
        ) = await self.pack_service.create_bundle(
            lockfile_path=command.lockfile_path,
            output_path=command.output_path,
            tag=command.tag,
            progress_callback=progress_callback,
        )

        # Return result
        return PackResult(
            bundle_path=bundle_path,
            layers_created=layers_created,
            artifacts_bundled=artifacts_bundled,
        )
