"""
HandlerFactory for creating handlers based on URL schemes.

Single factory that creates appropriate handlers for all operations,
eliminating the need for separate source/destination/fetch factories.
"""

from typing import Dict, Optional, Type
from urllib.parse import urlparse

from ..core.clients.http import HttpClient
from ..core.clients.registry import RegistryClient
from ..services.cache import CacheResolver
from .base import BaseHandler
from .file import FileHandler
from .http import HttpHandler
from .oci import OciHandler


class HandlerFactory:
    """
    Factory for creating unified handlers based on URL schemes.

    This factory replaces the separate HandlerFactory and FetchHandlerFactory
    with a single, consolidated implementation.
    """

    def __init__(
        self,
        base_path: Optional[str] = None,
        cache_service: Optional[CacheResolver] = None,
        http_client: Optional[HttpClient] = None,
        registry_client: Optional[RegistryClient] = None,
    ):
        """
        Initialize the unified handler factory.

        Args:
            base_path: Base path for resolving relative paths
            cache_service: Optional cache service for handlers
            http_client: Optional HTTP client for network operations
        """
        self.base_path = base_path
        self.cache_service = cache_service
        self.http_client = http_client
        self.registry_client = registry_client

        # Map schemes to handler classes
        self._handler_map: Dict[str, Type[BaseHandler]] = {
            "file": FileHandler,
            "": FileHandler,  # No scheme = local file
            "http": HttpHandler,
            "https": HttpHandler,
            "oci": OciHandler,
        }

    def get_handler(self, url: str) -> BaseHandler:
        """
        Get appropriate handler for the given URL.

        Args:
            url: URL or path to get handler for

        Returns:
            Appropriate handler instance

        Raises:
            ValueError: If URL scheme is not supported
        """
        scheme = self._detect_scheme(url)

        if scheme not in self._handler_map:
            supported = ", ".join(s for s in self._handler_map if s)
            msg = f"Unsupported scheme: {scheme}. Supported schemes: {supported}"
            raise ValueError(msg)

        handler_class = self._handler_map[scheme]

        # Create handler with appropriate dependencies
        return handler_class(
            base_path=self.base_path,
            cache_service=self.cache_service,
            http_client=self.http_client,
            registry_client=self.registry_client,
        )

    def get_handler_for_scheme(self, scheme: str) -> BaseHandler:
        """
        Get handler for a specific scheme.

        Args:
            scheme: URL scheme (file, http, https, oci)

        Returns:
            Handler instance for the scheme

        Raises:
            ValueError: If scheme is not supported
        """
        if scheme not in self._handler_map:
            supported = ", ".join(s for s in self._handler_map if s)
            msg = f"Unsupported scheme: {scheme}. Supported schemes: {supported}"
            raise ValueError(msg)

        handler_class = self._handler_map[scheme]

        return handler_class(
            base_path=self.base_path,
            cache_service=self.cache_service,
            http_client=self.http_client,
            registry_client=self.registry_client,
        )

    @property
    def supported_schemes(self) -> list[str]:
        """Get list of supported URL schemes."""
        return [s for s in self._handler_map if s]

    def supports_scheme(self, scheme: str) -> bool:
        """Check if a scheme is supported."""
        return scheme in self._handler_map

    def _detect_scheme(self, url: str) -> str:
        """
        Detect the scheme from a URL or path.

        Args:
            url: URL or path to analyze

        Returns:
            The detected scheme (empty string for local paths)
        """
        try:
            parsed = urlparse(url)
            return parsed.scheme.lower() if parsed.scheme else ""
        except Exception:
            # If parsing fails, treat as local path
            return ""
