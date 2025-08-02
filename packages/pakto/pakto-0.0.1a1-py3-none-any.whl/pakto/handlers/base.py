"""
Unified base handler architecture following Command/Query pattern.

This module provides the base classes for the consolidated handler system
that eliminates duplication between source, destination, and fetch handlers.
"""

from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from ..core.clients.http import HttpClient
from ..core.clients.registry import RegistryClient
from ..core.commands import BaseCommand, BaseResult
from ..services.cache import CacheResolver

TCommand = TypeVar("TCommand", bound=BaseCommand)
TResult = TypeVar("TResult", bound=BaseResult)


class BaseHandler(ABC, Generic[TCommand, TResult]):
    """
    Abstract base class for all unified handlers.

    Handlers process commands and return results, following CQRS patterns
    with dependency injection support.
    """

    def __init__(
        self,
        cache_service: Optional[CacheResolver] = None,
        http_client: Optional[HttpClient] = None,
        registry_client: Optional[RegistryClient] = None,
        base_path: Optional[str] = None,
    ):
        """
        Initialize handler with optional dependencies.

        Args:
            cache_service: Optional cache resolver for caching operations
            http_client: Optional HTTP client for network operations
            base_path: Optional base path for resolving relative paths
        """
        self._cache_service = cache_service
        self._http_client = http_client
        self._registry_client = registry_client
        self._base_path = base_path

    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        """
        Handle a command and return the result.

        Args:
            command: The command to execute

        Returns:
            Result of the command execution
        """
        pass

    @abstractmethod
    def can_handle(self, scheme: str) -> bool:
        """
        Check if this handler can handle artifacts with the given scheme.

        Args:
            scheme: URL scheme (file, http, https, oci, etc.)

        Returns:
            True if this handler supports the scheme
        """
        pass
