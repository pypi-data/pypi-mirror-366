"""
Unified OCI handler for container images from registries.

Combines functionality of OciSourceHandler and OciFetchHandler
into a single handler following the Command/Query pattern.
"""

import asyncio
import hashlib
import json
import shutil
import tempfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Callable, Dict, Optional

import aiohttp
import repro_tarfile as tarfile

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

from ..core.clients.http import HttpClient
from ..core.clients.registry import RegistryClient
from ..core.models import CacheMetadata
from ..services.cache import CacheResolver
from .base import BaseHandler


class OciHandler(BaseHandler):
    """
    Unified handler for OCI/Docker container images.

    Handles:
    - Pulling images from registries
    - Metadata calculation
    - Caching as tar files
    """

    def __init__(
        self,
        cache_service: Optional[CacheResolver] = None,
        http_client: Optional[HttpClient] = None,
        registry_client: Optional[RegistryClient] = None,
        base_path: Optional[str] = None,
    ):
        """
        Initialize OCI handler.

        Args:
            cache_service: Optional cache service for caching manifests/images
            http_client: Optional HTTP client (not used, OCI uses registry client)
            registry_client: Optional registry client for OCI operations
            base_path: Base path for resolving relative paths (not used for OCI)
        """
        super().__init__(cache_service, http_client, registry_client, base_path)

    def can_handle(self, scheme: str) -> bool:
        """Check if this handler can handle the given scheme."""
        return scheme == "oci"

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
        """
        Calculate metadata for OCI image by downloading to cache and returning tar checksum.

        This ensures consistent checksums between lock and pack commands by using
        the actual tar file representation rather than manifest digests.
        """
        try:
            parsed = self._parse_oci_reference(command.origin)

            # Check if already in cache
            if self._cache_service and await self._cache_service.is_available_locally(
                command.origin
            ):
                resolution = await self._cache_service.resolve_artifact(command.origin)
                if resolution.cached_metadata:
                    content_path = self._cache_service._content_store.get_content_path(
                        resolution.cached_metadata.content_hash
                    )
                    return CalculateMetadataResult(
                        success=True,
                        checksum=resolution.cached_metadata.content_hash,
                        size=resolution.cached_metadata.size,
                        type="oci",
                        cached_path=str(content_path),
                        metadata={
                            "registry": parsed["registry"],
                            "repository": parsed["repository"],
                            "tag": parsed["tag"],
                        },
                    )

            # Not in cache - download to cache and get tar checksum
            result = await self._pull_to_cache(
                command.origin,
                artifact_name=command.artifact_name,
                progress_callback=command.progress_callback,
            )

            return CalculateMetadataResult(
                success=True,
                checksum=result["checksum"],
                size=result["size"],
                type="oci",
                cached_path=result["cached_path"],
                metadata={
                    "registry": parsed["registry"],
                    "repository": parsed["repository"],
                    "tag": parsed["tag"],
                },
            )

        except Exception as e:
            return CalculateMetadataResult(
                success=False,
                checksum="",
                size=0,
                type="oci",
                error_message=f"Failed to fetch OCI image info: {e!s}",
            )

    async def _fetch_artifact(
        self, command: FetchArtifactCommand
    ) -> FetchArtifactResult:
        """
        Fetch OCI image to target location.

        Uses cache service if available, otherwise pulls directly.
        """
        try:
            target_path = Path(command.target_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if already in cache
            if self._cache_service:
                resolution = await self._cache_service.resolve_artifact(
                    command.origin_url
                )
                if resolution.cached_metadata:
                    # Copy from cache
                    content_path = self._cache_service._content_store.get_content_path(
                        resolution.cached_metadata.content_hash
                    )
                    if content_path and content_path.exists():
                        shutil.copy2(content_path, target_path)

                        return FetchArtifactResult(
                            success=True,
                            local_path=str(target_path),
                            checksum=resolution.cached_metadata.content_hash,
                            was_downloaded=False,  # From cache
                            bytes_downloaded=target_path.stat().st_size,
                        )

            # Not in cache, need to pull
            result = await self._pull_to_cache(command.origin_url)

            # Copy to target
            cached_path = Path(result["cached_path"])
            if cached_path.exists():
                shutil.copy2(cached_path, target_path)

                # Note: For OCI artifacts, checksums may differ since we're creating
                # a tar representation rather than the original manifest digest
                # In production, this would be handled differently

                return FetchArtifactResult(
                    success=True,
                    local_path=str(target_path),
                    checksum=result["checksum"],
                    was_downloaded=True,
                    bytes_downloaded=result["size"],
                )
            return FetchArtifactResult(
                success=False,
                local_path="",
                checksum="",
                was_downloaded=False,
                error_message="Failed to pull OCI image",
            )

        except Exception as e:
            return FetchArtifactResult(
                success=False,
                local_path="",
                checksum="",
                was_downloaded=False,
                error_message=str(e),
            )

    async def _validate_target(self, _: ValidateTargetCommand) -> ValidateTargetResult:
        """OCI handler doesn't handle targets, only sources."""
        return ValidateTargetResult(
            valid=False,
            error_message="OCI handler only supports artifact sources, not targets",
        )

    def _parse_oci_reference(self, url: str) -> Dict[str, str]:
        """Parse OCI reference into components."""
        if not url.startswith("oci://"):
            msg = f"Invalid OCI URL: {url}"
            raise ValueError(msg)

        # Remove oci:// prefix
        ref = url[6:]

        # Split registry from repository
        parts = ref.split("/", 1)
        if len(parts) < 2:
            msg = f"Invalid OCI reference format: {url}"
            raise ValueError(msg)

        registry = parts[0]
        repo_and_tag = parts[1]

        # Split repository from tag
        if ":" in repo_and_tag:
            repository, tag = repo_and_tag.rsplit(":", 1)
        else:
            repository = repo_and_tag
            tag = "latest"

        return {"registry": registry, "repository": repository, "tag": tag}

    async def _pull_to_cache(
        self,
        url: str,
        artifact_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> dict:
        """
        Pull OCI image to cache as tar file.

        Production implementation would use ORAS client.
        """
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            # Report start
            if progress_callback and artifact_name:
                progress_callback({
                    "type": "download_start",
                    "url": url,
                    "name": artifact_name,
                })

            # Parse reference
            parsed = self._parse_oci_reference(url)
            parsed["registry"]
            parsed["repository"]
            parsed["tag"]

            await self._oras_pull_async(
                url, artifact_name, progress_callback, temp_path
            )

            # Calculate checksum
            checksum = await self._calculate_file_checksum(temp_path)
            size = temp_path.stat().st_size

            # Store in cache if available
            if self._cache_service:
                metadata_repo = self._cache_service._metadata_repo
                content_store = self._cache_service._content_store

                await content_store.store_content(temp_path, checksum)
                content_path = content_store.get_content_path(checksum)

                # Store metadata
                cache_metadata = CacheMetadata(
                    url=url,
                    content_hash=checksum,
                    etag=None,
                    last_modified=None,
                    cache_time=datetime.now(timezone.utc),
                    headers={},
                    size=size,
                )
                await metadata_repo.store_metadata(cache_metadata)
            else:
                content_path = temp_path

            # Report completion
            if progress_callback and artifact_name:
                progress_callback({
                    "type": "download_complete",
                    "url": url,
                    "name": artifact_name,
                    "bytes_downloaded": size,
                    "total_bytes": size,
                })

            return {
                "checksum": checksum,
                "size": size,
                "cached_path": str(content_path),
            }

        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()

            if progress_callback and artifact_name:
                progress_callback({
                    "type": "download_error",
                    "url": url,
                    "name": artifact_name,
                    "error": str(e),
                })
            raise

    async def _oras_pull_async(
        self,
        url: str,
        artifact_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        temp_path: Optional[Path] = None,
    ):
        """
        Pull OCI image asynchronously with proper progress reporting.
        """

        # Parse reference
        parsed = self._parse_oci_reference(url)
        registry_url = parsed["registry"]
        repository = parsed["repository"]
        tag = parsed["tag"]

        # Create temporary directory for pulling layers
        with tempfile.TemporaryDirectory() as work_dir:
            work_path = Path(work_dir)
            layers_dir = work_path / "layers"
            layers_dir.mkdir()

            # Create async HTTP session
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                # Handle authentication for different registries
                auth_headers = {}
                if registry_url == "quay.io":
                    # Quay.io doesn't require auth for public images
                    pass
                elif registry_url in ["docker.io", "registry-1.docker.io"]:
                    # Get Docker Hub token
                    # Docker Hub official images need library/ prefix
                    scope_repository = (
                        repository if "/" in repository else f"library/{repository}"
                    )
                    token_url = "https://auth.docker.io/token"  # noqa: S105
                    token_params = {
                        "service": "registry.docker.io",
                        "scope": f"repository:{scope_repository}:pull",
                    }
                    async with session.get(
                        token_url, params=token_params
                    ) as token_resp:
                        token_resp.raise_for_status()
                        token_data = await token_resp.json()
                        token = token_data.get("token")
                        if token:
                            auth_headers["Authorization"] = f"Bearer {token}"
                elif registry_url == "ghcr.io":
                    # Get GitHub Container Registry token
                    token_url = "https://ghcr.io/token"  # noqa: S105
                    token_params = {
                        "service": "ghcr.io",
                        "scope": f"repository:{repository}:pull",
                    }
                    async with session.get(
                        token_url, params=token_params
                    ) as token_resp:
                        token_resp.raise_for_status()
                        token_data = await token_resp.json()
                        token = token_data.get("token")
                        if token:
                            auth_headers["Authorization"] = f"Bearer {token}"

                # Get manifest (use correct API endpoint for Docker Hub)
                api_registry = (
                    "registry-1.docker.io"
                    if registry_url in ["docker.io", "registry-1.docker.io"]
                    else registry_url
                )
                # Use library/ prefix for Docker Hub official images
                manifest_repository = (
                    repository
                    if "/" in repository
                    or registry_url not in ["docker.io", "registry-1.docker.io"]
                    else f"library/{repository}"
                )
                manifest_url = (
                    f"https://{api_registry}/v2/{manifest_repository}/manifests/{tag}"
                )
                manifest_headers = {
                    "Accept": "application/vnd.oci.image.index.v1+json,application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json",
                    **auth_headers,
                }

                async with session.get(
                    manifest_url, headers=manifest_headers
                ) as manifest_resp:
                    manifest_resp.raise_for_status()
                    manifest = await manifest_resp.json()

                # Handle manifest lists (multi-arch images)
                if "manifests" in manifest:
                    # Find linux/amd64 manifest
                    platform_manifest = None
                    for m in manifest["manifests"]:
                        platform = m.get("platform", {})
                        if (
                            platform.get("os") == "linux"
                            and platform.get("architecture") == "amd64"
                        ):
                            platform_manifest = m
                            break

                    if not platform_manifest:
                        # Use first manifest if no amd64 found
                        platform_manifest = manifest["manifests"][0]

                    # Fetch the specific platform manifest
                    platform_digest = platform_manifest["digest"]
                    platform_url = f"https://{api_registry}/v2/{manifest_repository}/manifests/{platform_digest}"
                    async with session.get(
                        platform_url, headers=manifest_headers
                    ) as platform_resp:
                        platform_resp.raise_for_status()
                        manifest = await platform_resp.json()

                # Calculate total download size for progress
                total_size = manifest["config"]["size"]
                for layer in manifest["layers"]:
                    total_size += layer["size"]

                # Report download start with total size
                if progress_callback and artifact_name:
                    progress_callback({
                        "type": "download_progress",
                        "url": url,
                        "name": artifact_name,
                        "bytes_downloaded": 0,
                        "total_bytes": total_size,
                    })

                downloaded_bytes = 0

                # Get config blob
                config_digest = manifest["config"]["digest"]
                config_url = f"https://{api_registry}/v2/{manifest_repository}/blobs/{config_digest}"
                async with session.get(config_url, headers=auth_headers) as config_resp:
                    config_resp.raise_for_status()
                    config_data = await config_resp.read()
                    downloaded_bytes += len(config_data)

                # Update progress after config download
                if progress_callback and artifact_name:
                    progress_callback({
                        "type": "download_progress",
                        "url": url,
                        "name": artifact_name,
                        "bytes_downloaded": downloaded_bytes,
                        "total_bytes": total_size,
                    })

                # Download all layer blobs with progress
                layer_files = []
                for layer in manifest["layers"]:
                    layer_digest = layer["digest"]
                    layer_url = f"https://{api_registry}/v2/{manifest_repository}/blobs/{layer_digest}"

                    layer_file = layers_dir / f"{layer_digest.replace(':', '_')}.tar.gz"

                    async with session.get(
                        layer_url, headers=auth_headers
                    ) as layer_resp:
                        layer_resp.raise_for_status()

                        # Save layer to file with progress updates
                        with open(layer_file, "wb") as f:
                            chunk_count = 0
                            async for chunk in layer_resp.content.iter_chunked(8192):
                                f.write(chunk)
                                downloaded_bytes += len(chunk)
                                chunk_count += 1

                                # Update progress every 10 chunks to avoid too many updates
                                if (
                                    progress_callback
                                    and artifact_name
                                    and chunk_count % 10 == 0
                                ):
                                    progress_callback({
                                        "type": "download_progress",
                                        "url": url,
                                        "name": artifact_name,
                                        "bytes_downloaded": downloaded_bytes,
                                        "total_bytes": total_size,
                                    })
                    layer_files.append(layer_file)

                # Final progress update
                if progress_callback and artifact_name:
                    progress_callback({
                        "type": "download_progress",
                        "url": url,
                        "name": artifact_name,
                        "bytes_downloaded": total_size,
                        "total_bytes": total_size,
                    })

                # Create docker-compatible tar archive
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self._create_tar_archive,
                    temp_path,
                    config_data,
                    config_digest,
                    layer_files,
                    repository,
                    tag,
                )

    def _create_tar_archive(
        self,
        temp_path,
        config_data,
        config_digest,
        layer_files,
        repository,
        tag,
    ):
        """Create tar archive synchronously."""
        with tarfile.open(temp_path, "w") as tar:
            # Add manifest.json (Docker format)
            docker_manifest = [
                {
                    "Config": f"{config_digest.replace(':', '_')}.json",
                    "RepoTags": [f"{repository}:{tag}"],
                    "Layers": [f"{Path(lf).name}" for lf in layer_files],
                }
            ]

            manifest_data = json.dumps(docker_manifest, indent=2).encode()
            manifest_info = tarfile.TarInfo(name="manifest.json")
            manifest_info.size = len(manifest_data)
            tar.addfile(manifest_info, BytesIO(manifest_data))

            # Add config file
            config_filename = f"{config_digest.replace(':', '_')}.json"
            config_info = tarfile.TarInfo(name=config_filename)
            config_info.size = len(config_data)
            tar.addfile(config_info, BytesIO(config_data))

            # Add all layer files
            for layer_file in layer_files:
                tar.add(layer_file, arcname=layer_file.name)

    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum asynchronously."""

        def _calc():
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)
            return f"sha256:{sha256_hash.hexdigest()}"

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _calc)
