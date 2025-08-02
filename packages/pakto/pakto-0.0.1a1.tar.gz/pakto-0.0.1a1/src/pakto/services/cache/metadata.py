"""
Cache Metadata Repository - URL-first indexing for HTTP cache.

GREEN phase implementation: Minimal code to make tests pass.
"""

import json
from pathlib import Path
from typing import Dict, Optional

from pakto.core.models import CacheMetadata


class CacheMetadataRepository:
    """Repository for cache metadata with URL-first indexing."""

    def __init__(self, cache_dir: Path):
        self._cache_dir = Path(cache_dir)
        self._metadata_file = self._cache_dir / "metadata.json"
        self._url_index_file = self._cache_dir / "url_index.json"

        # In-memory stores for minimal implementation
        self._metadata: Dict[str, dict] = {}
        self._url_index: Dict[str, str] = {}

        # Load existing data synchronously for init
        self._load_data_sync()

    def _load_data_sync(self):
        """Load metadata and URL index from disk synchronously."""
        try:
            if self._metadata_file.exists():
                self._metadata = json.loads(self._metadata_file.read_text())
            if self._url_index_file.exists():
                self._url_index = json.loads(self._url_index_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    async def _load_data(self):
        """Load metadata and URL index from disk."""
        self._load_data_sync()

    async def store_metadata(self, metadata: CacheMetadata) -> None:
        """Store cache metadata with dual indexing (URL and hash)."""
        # Create unique key for this URL (URL-based storage)
        url_key = f"url:{metadata.url}"

        # Store metadata indexed by URL (primary storage)
        self._metadata[url_key] = {
            "url": metadata.url,
            "content_hash": metadata.content_hash,
            "etag": metadata.etag,
            "last_modified": metadata.last_modified,
            "cache_time": metadata.cache_time.isoformat()
            if metadata.cache_time
            else None,
            "max_age": metadata.max_age,
            "headers": metadata.headers or {},
            "size": metadata.size,
        }

        # Also store indexed by hash for hash-based lookups
        hash_key = f"hash:{metadata.content_hash}"
        self._metadata[hash_key] = self._metadata[url_key].copy()

        # Store in URL index for quick lookup
        self._url_index[metadata.url] = metadata.content_hash

        # Persist to disk
        await self._save_data()

    async def get_by_url(self, url: str) -> Optional[CacheMetadata]:
        """Get cache metadata by URL (primary lookup method)."""
        url_key = f"url:{url}"
        if url_key not in self._metadata:
            return None

        return self._metadata_to_object(self._metadata[url_key])

    async def get_by_hash(self, content_hash: str) -> Optional[CacheMetadata]:
        """Get cache metadata by content hash."""
        hash_key = f"hash:{content_hash}"
        if hash_key not in self._metadata:
            return None

        return self._metadata_to_object(self._metadata[hash_key])

    def _metadata_to_object(self, data: dict) -> CacheMetadata:
        """Convert metadata dict to CacheMetadata object."""
        cache_time = None
        if data.get("cache_time"):
            from datetime import datetime

            cache_time = datetime.fromisoformat(data["cache_time"])

        return CacheMetadata(
            url=data["url"],
            content_hash=data["content_hash"],
            etag=data.get("etag"),
            last_modified=data.get("last_modified"),
            cache_time=cache_time,
            max_age=data.get("max_age"),
            headers=data.get("headers", {}),
            size=data.get("size", 0),
        )

    async def get_conditional_headers(self, url: str) -> Dict[str, str]:
        """Get conditional request headers for URL."""
        metadata = await self.get_by_url(url)
        if not metadata:
            return {}

        headers = {}
        if metadata.etag:
            headers["If-None-Match"] = metadata.etag
        if metadata.last_modified:
            headers["If-Modified-Since"] = metadata.last_modified

        return headers

    async def _save_data(self):
        """Save metadata and URL index to disk."""
        # Ensure directory exists
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        # Write metadata
        self._metadata_file.write_text(json.dumps(self._metadata, indent=2))

        # Write URL index
        self._url_index_file.write_text(json.dumps(self._url_index, indent=2))
