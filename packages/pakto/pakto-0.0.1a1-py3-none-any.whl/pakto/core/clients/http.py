"""
HTTP client interface and aiohttp implementation for artifact downloads.

Provides abstract HTTP client interface following the same pattern as RegistryClient.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import aiohttp


class HttpClient(ABC):
    """Abstract interface for HTTP operations."""

    @abstractmethod
    async def download_file(
        self, url: str, destination: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Download file from URL to destination.

        Args:
            url: Source URL to download from
            destination: Local file path to save to
            **kwargs: Additional options (headers, timeout, etc.)

        Returns:
            Dictionary with download metadata (bytes_downloaded, checksum, etc.)
        """
        pass

    @abstractmethod
    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get metadata about a resource without downloading.

        Args:
            url: URL to get metadata for
            **kwargs: Additional options

        Returns:
            Dictionary with metadata (content-length, etag, etc.)
        """
        pass


class AiohttpClient(HttpClient):
    """aiohttp-based HTTP client implementation for high-performance downloads."""

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        """
        Initialize HTTP client.

        Args:
            session: Optional aiohttp session for connection reuse
        """
        self._session = session
        self._session_owned = session is None

    async def __aenter__(self):
        """Async context manager entry."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session_owned and self._session:
            await self._session.close()

    async def download_file(
        self, url: str, destination: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Download file from URL using aiohttp for maximum performance.

        Args:
            url: Source URL to download from
            destination: Local file path to save to
            **kwargs: Additional options (progress_callback, etc.)

        Returns:
            Dictionary with download results
        """
        if not self._session:
            msg = "HTTP client session not initialized. Use async context manager."
            raise RuntimeError(msg)

        progress_callback = kwargs.get("progress_callback")

        try:
            async with self._session.get(url) as response:
                if response.status == 404:
                    return {"success": False, "error": f"HTTP 404: Not found - {url}"}

                response.raise_for_status()

                # Get content length for progress tracking
                content_length = response.headers.get("Content-Length")
                total_bytes = int(content_length) if content_length else None

                # Send download start event
                if progress_callback:
                    progress_callback({
                        "type": "download_start",
                        "url": url,
                        "total_bytes": total_bytes,
                    })

                bytes_downloaded = 0
                with open(destination, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        bytes_downloaded += len(chunk)

                        # Call progress callback if provided
                        if progress_callback:
                            progress_callback({
                                "type": "download_progress",
                                "url": url,
                                "bytes_downloaded": bytes_downloaded,
                                "total_bytes": total_bytes,
                                "progress_percent": (
                                    bytes_downloaded / total_bytes * 100
                                )
                                if total_bytes
                                else 0,
                            })

                # Send download complete event
                if progress_callback:
                    progress_callback({
                        "type": "download_complete",
                        "url": url,
                        "bytes_downloaded": bytes_downloaded,
                        "total_bytes": total_bytes,
                    })

                return {
                    "success": True,
                    "bytes_downloaded": bytes_downloaded,
                    "status_code": response.status,
                    "content_type": response.headers.get("content-type", ""),
                }

        except aiohttp.ClientError as e:
            return {"success": False, "error": f"HTTP client error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Download failed: {e}"}

    async def get_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get metadata about a resource using HEAD request.

        Args:
            url: URL to get metadata for
            **kwargs: Additional options

        Returns:
            Dictionary with metadata
        """
        if not self._session:
            msg = "HTTP client session not initialized. Use async context manager."
            raise RuntimeError(msg)

        try:
            async with self._session.head(url) as response:
                return {
                    "success": True,
                    "status_code": response.status,
                    "content_length": response.headers.get("content-length"),
                    "content_type": response.headers.get("content-type", ""),
                    "etag": response.headers.get("etag"),
                    "last_modified": response.headers.get("last-modified"),
                }
        except aiohttp.ClientError as e:
            return {"success": False, "error": f"HTTP client error: {e}"}
        except Exception as e:
            return {"success": False, "error": f"Metadata request failed: {e}"}
