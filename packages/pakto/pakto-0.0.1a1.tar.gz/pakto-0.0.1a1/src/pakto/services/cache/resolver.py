"""
Cache Resolver - Unified interface for artifact resolution.

GREEN phase implementation: Minimal code to make tests pass.
"""

import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pakto.core.models import ArtifactResolution
from pakto.core.types import AppPath
from pakto.services.config import ConfigService, get_config_service

from .http_cache import HttpCacheService
from .metadata import CacheMetadataRepository
from .storage import ContentAddressableStore


class CacheResolver:
    """Unified interface for resolving artifacts."""

    def __init__(
        self,
        cache_dir: Optional[AppPath] = None,
        http_cache_service: Optional[HttpCacheService] = None,
        config_service: Optional[ConfigService] = None,
    ):
        # Use config service if provided, otherwise fall back to direct cache_dir
        config_service = config_service or get_config_service()

        cache_dir = cache_dir or Path(config_service.get("cache_dir"))
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        self._metadata_repo = CacheMetadataRepository(self._cache_dir / "metadata")
        self._metadata_repo._cache_dir.mkdir(parents=True, exist_ok=True)

        self._content_store = ContentAddressableStore(self._cache_dir / "content")
        self._content_store._cache_dir.mkdir(parents=True, exist_ok=True)

        self._http_cache = http_cache_service

    async def resolve_artifact(self, artifact_ref: str) -> ArtifactResolution:
        """Resolve artifact reference to local file or cached remote content."""
        if not artifact_ref:
            msg = "Artifact reference cannot be empty"
            raise ValueError(msg)

        # Parse to determine if it's a URL or local path
        parsed = urlparse(artifact_ref)

        if parsed.scheme in ("http", "https", "oci"):
            # Remote URL
            cached_metadata = await self._metadata_repo.get_by_url(artifact_ref)
            return ArtifactResolution(
                type="remote", url=artifact_ref, cached_metadata=cached_metadata
            )
        # Local file path
        path = Path(artifact_ref)
        return ArtifactResolution(type="local", path=path)

    async def is_available_locally(self, artifact_ref: str) -> bool:
        """Check if artifact is available locally (file or cache)."""
        resolution = await self.resolve_artifact(artifact_ref)

        if resolution.type == "local":
            return resolution.path.exists() if resolution.path else False
        if resolution.type == "remote":
            # Check if cached
            return resolution.cached_metadata is not None

        return False

    def clear_cache(self) -> None:
        """Clear the entire cache directory."""
        if self._cache_dir.exists():
            shutil.rmtree(self._cache_dir)
