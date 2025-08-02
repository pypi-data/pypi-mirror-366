"""
Content Addressable Store - Flyweight pattern for content deduplication.

GREEN phase implementation: Minimal code to make tests pass.
"""

import asyncio
import shutil
from pathlib import Path
from typing import Optional


class ContentAddressableStore:
    """Content-addressable storage implementing Flyweight pattern."""

    def __init__(self, cache_dir: Path):
        self._cache_dir = Path(cache_dir)
        self._blobs_dir = self._cache_dir / "blobs"
        self._blobs_dir.mkdir(parents=True, exist_ok=True)

    def get_content_path(self, content_hash: str) -> Path:
        """Get storage path for content hash using git-like structure."""
        # Parse hash format "sha256:abcd1234..."
        if ":" in content_hash:
            algorithm, hash_value = content_hash.split(":", 1)
        else:
            algorithm = "sha256"
            hash_value = content_hash

        # Git-like structure: blobs/sha256/ab/cd/abcd1234...
        return (
            self._blobs_dir / algorithm / hash_value[:2] / hash_value[2:4] / hash_value
        )

    async def store_content(self, content_path: Path, content_hash: str) -> Path:
        """Store content by hash, return cache path."""
        cache_path = self.get_content_path(content_hash)

        # If already cached, return existing path (Flyweight deduplication)
        if cache_path.exists():
            return cache_path

        # Create directory structure
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy content to cache (using thread pool for async)
        await asyncio.to_thread(shutil.copy2, content_path, cache_path)

        return cache_path

    async def get_content(self, content_hash: str) -> Optional[Path]:
        """Get cached content path by hash."""
        cache_path = self.get_content_path(content_hash)
        if cache_path.exists():
            return cache_path
        return None

    async def content_exists(self, content_hash: str) -> bool:
        """Check if content exists in cache."""
        cache_path = self.get_content_path(content_hash)
        return cache_path.exists()

    async def copy_to_target(self, content_hash: str, target_path: Path) -> bool:
        """Copy cached content to target location."""
        cache_path = self.get_content_path(content_hash)
        if not cache_path.exists():
            return False

        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy from cache to target (using thread pool for async)
        await asyncio.to_thread(shutil.copy2, cache_path, target_path)

        return True
