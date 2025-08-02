"""
Command and Result models for handler operations.

This module defines the command/result patterns used throughout the application's
handler system, following Command Query Responsibility Segregation (CQRS) patterns.
"""

from abc import ABC
from dataclasses import dataclass
from typing import (
    Any,
    Callable,  # Add Callable
    Dict,
    Optional,
)


class BaseCommand(ABC):
    """Base class for all handler commands."""

    pass


class BaseResult(ABC):
    """Base class for all handler results."""

    pass


@dataclass
class CalculateMetadataCommand(BaseCommand):
    """Command to calculate metadata for an artifact."""

    origin: str
    artifact_name: Optional[str] = None  # For progress reporting
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = (
        None  # Add progress_callback
    )


@dataclass
class CalculateMetadataResult(BaseResult):
    """Result of metadata calculation."""

    success: bool
    checksum: str
    size: int
    type: str
    cached_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata


@dataclass
class FetchArtifactCommand(BaseCommand):
    """Command to fetch an artifact from a source to a target location."""

    origin_url: str
    target_path: str
    expected_checksum: Optional[str] = None


@dataclass
class FetchArtifactResult(BaseResult):
    """Result of a fetch artifact operation."""

    success: bool
    local_path: str
    checksum: str
    was_downloaded: bool  # False if file already existed and was valid
    error_message: Optional[str] = None
    bytes_downloaded: Optional[int] = None


@dataclass
class ValidateTargetCommand(BaseCommand):
    """Command to validate a destination target."""

    target: str


@dataclass
class ValidateTargetResult(BaseResult):
    """Result of target validation."""

    valid: bool
    error_message: Optional[str] = None
