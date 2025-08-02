"""
HTTP Cache Service - Cache-Aside pattern with RFC 7234 semantics.

GREEN phase implementation: Minimal code to make tests pass.
"""

import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from pakto.core.clients.http import HttpClient
from pakto.core.models import CacheMetadata, FetchResult

from .metadata import CacheMetadataRepository
from .storage import ContentAddressableStore


class HttpCacheService:
    """HTTP cache service implementing Cache-Aside pattern with RFC 7234 semantics."""

    def __init__(
        self,
        metadata_repo: CacheMetadataRepository,
        content_store: ContentAddressableStore,
        http_client: HttpClient,
    ):
        self._metadata = metadata_repo
        self._content = content_store
        self._http_client = http_client

    async def get_or_fetch(
        self, url: str, target_path: Path, progress_callback: Optional[Callable] = None
    ) -> FetchResult:
        """
        Get artifact from cache or fetch from remote with conditional requests.

        Implements Cache-Aside pattern:
        1. Check metadata repository for URL
        2. If cached and fresh, return from content store
        3. If cached but stale, make conditional request
        4. If 304 Not Modified, return cached content
        5. If 200 OK or cache miss, download and cache
        """
        # Check cache first
        cached_metadata = await self._metadata.get_by_url(url)

        if cached_metadata:
            # Check if content exists in store
            if await self._content.content_exists(cached_metadata.content_hash):
                # For simplicity in GREEN phase, return cached content
                # TODO: Add freshness checking and conditional requests
                success = await self._content.copy_to_target(
                    cached_metadata.content_hash, target_path
                )
                if success:
                    return FetchResult(
                        success=True, was_cached=True, bytes_downloaded=0
                    )

        # Cache miss or content not available - fetch from remote
        return await self.fetch_and_cache(url, target_path, progress_callback)

    async def fetch_and_cache(
        self, url: str, target_path: Path, progress_callback: Optional[Callable] = None
    ) -> FetchResult:
        """Fetch from remote and store in cache."""
        try:
            # Check for cached metadata to send conditional headers
            cached_metadata = await self._metadata.get_by_url(url)

            # Prepare headers including conditional ones
            headers = {}
            if cached_metadata:
                conditional_headers = await self._metadata.get_conditional_headers(url)
                headers.update(conditional_headers)

            # Prepare download arguments
            download_kwargs = {"url": url, "destination": str(target_path)}
            if progress_callback:
                download_kwargs["progress_callback"] = progress_callback
            if headers:
                download_kwargs["headers"] = headers

            # Download using HTTP client
            response = await self._http_client.download_file(**download_kwargs)

            if not response.get("success", False):
                return FetchResult(
                    success=False,
                    was_cached=False,
                    error_message=response.get("error", "Download failed"),
                )

            # Handle 304 Not Modified response
            if response.get("status") == 304 and cached_metadata:
                # Content not modified, use cached version
                success = await self._content.copy_to_target(
                    cached_metadata.content_hash, target_path
                )
                if success:
                    return FetchResult(
                        success=True, was_cached=True, bytes_downloaded=0
                    )

            # Ensure target file exists before processing
            if not target_path.exists():
                # This shouldn't happen with proper HTTP client, but handle gracefully
                return FetchResult(
                    success=False,
                    was_cached=False,
                    error_message=f"Download completed but file not found: {target_path}",
                )

            # Calculate content hash
            content_hash = await self._calculate_content_hash(target_path)

            # Store in cache
            await self._content.store_content(target_path, content_hash)

            # Store metadata
            response_headers = response.get("headers", {})
            metadata = CacheMetadata(
                url=url,
                content_hash=content_hash,
                etag=response_headers.get("ETag"),
                last_modified=response_headers.get("Last-Modified"),
                cache_time=datetime.utcnow(),
                headers=response_headers,
                size=target_path.stat().st_size,
            )
            await self._metadata.store_metadata(metadata)

            return FetchResult(
                success=True,
                was_cached=False,
                bytes_downloaded=response.get(
                    "bytes_downloaded", target_path.stat().st_size
                ),
            )

        except Exception as e:
            return FetchResult(success=False, was_cached=False, error_message=str(e))

    async def _calculate_content_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content."""

        def _calc_hash():
            hash_obj = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_obj.update(chunk)
            return f"sha256:{hash_obj.hexdigest()}"

        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(_calc_hash)
