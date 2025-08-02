"""
Pydantic models for Pakto manifests and lock files (MVP version).

This module defines minimal Pydantic models for the MVP implementation of the
`pakto generate` command, focusing on simple local file-to-file copy operations.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from packaging.version import InvalidVersion, Version
from pydantic import BaseModel, Field, field_validator

from .constants import ConfigDefaults


class ManifestEntrypoint(BaseModel):
    """Entrypoint for a manifest. Script placed at root of imported directory."""

    script: str = Field(
        description="Path to the script file to be placed at the root of the imported directory."
    )
    mode: str = Field(
        default="0755", description="File mode for the script (e.g., '0755')."
    )
    uid: Optional[str] = Field(
        default=None,
        description="Optional User to execute the script as. If not set, runs as the current user.",
    )
    gid: Optional[str] = Field(
        default=None,
        description="Optional Group to execute the script as. If not set, runs as the current group.",
    )


class LockFileEntrypoint(BaseModel):
    """Entrypoint for a lockfile with checksum and size."""

    script: str = Field(
        ...,
        description="Path to the script file to be placed at the root of the imported directory.",
    )
    mode: str = Field("0755", description="File mode for the script (e.g., '0755').")
    checksum: str = Field(
        ..., description="SHA256 checksum of the script file content."
    )
    size: int = Field(..., description="Size of the script file in bytes.")
    uid: Optional[str] = Field(
        default=None,
        description="Optional User to execute the script as. If not set, runs as the current user.",
    )
    gid: Optional[str] = Field(
        default=None,
        description="Optional Group to execute the script as. If not set, runs as the current group.",
    )


# Manifest Models (MVP)
class ManifestMetadata(BaseModel):
    """Minimal metadata for a manifest (MVP)."""

    name: str = Field(..., description="A unique name for this manifest")
    version: str = Field(
        default="latest", description="Version of the bundle this manifest represents"
    )
    description: Optional[str] = Field(
        default=None, description="Optional description of the manifest"
    )

    @field_validator("version")
    def _validate_version(cls, v: Union[None, str]) -> str:  # noqa: N805
        if not v:
            return ConfigDefaults.DEFAULT_TAG
        if v and v == ConfigDefaults.DEFAULT_TAG:
            return v
        try:
            return str(Version(v))
        except InvalidVersion as e:
            msg = f"Invalid version format: '{v}'. Must be a valid PEP 440 version."
            raise ValueError(msg) from e


class ManifestArtifact(BaseModel):
    """Minimal artifact definition for a manifest."""

    name: str = Field(
        ..., description="A unique identifier for the artifact within this manifest"
    )
    origin: str = Field(..., description="Path to the local source file")
    target: str = Field(..., description="Path to the local destination file")


class Manifest(BaseModel):
    """Minimal manifest model."""

    apiVersion: str = Field(
        default=ConfigDefaults.SCHEMA_VERSION_VALUE,
        description="Version of the Manifest API",
    )
    kind: str = Field(
        default="Manifest", description="Type of the configuration object"
    )
    metadata: ManifestMetadata = Field(..., description="Metadata for the manifest")
    variables: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Optional variables for templating"
    )
    entrypoint: Union[None, str, ManifestEntrypoint] = Field(
        default=None,
        description="Optional entrypoint script to be placed at the root of the imported directory",
    )
    artifacts: List[ManifestArtifact] = Field(
        ..., description="List of artifact definitions"
    )


# Lock File Models (MVP)
class LockFileArtifact(BaseModel):
    """Minimal artifact definition for a lock file."""

    name: str = Field(..., description="A unique identifier for the artifact")
    type: str = Field(..., description="The type of the artifact (e.g., 'file')")
    action: str = Field(..., description="The action to perform (e.g., 'copy_local')")
    origin: str = Field(..., description="Resolved path to the local source file")
    target: str = Field(..., description="Resolved path to the local destination file")
    checksum: str = Field(..., description="SHA256 checksum of the artifact content")
    size: int = Field(..., description="Size of the artifact content in bytes")
    # New fields for individual artifact bundling
    blob_digest: Optional[str] = Field(
        default=None,
        description="OCI blob digest when artifact is bundled individually",
    )
    blob_size: Optional[int] = Field(
        default=None, description="OCI blob size when artifact is bundled individually"
    )


class LockFile(BaseModel):
    """Minimal lock file model."""

    apiVersion: str = Field(
        default=ConfigDefaults.SCHEMA_VERSION_VALUE,
        description="Version of the Lock File API",
    )
    kind: str = Field(
        default="LockFile", description="Type of the configuration object"
    )
    name: str = Field(
        ..., description="A unique name for the manifest this lock file represents"
    )
    version: str = Field(
        ...,
        description="Version of the manifest this lock file represents. Taken from the manifest metadata.",
    )
    entrypoint: Union[None, LockFileEntrypoint] = Field(
        default=None,
        description="Optional entrypoint script to be placed at the root of the imported directory",
    )

    manifestHash: str = Field(
        ..., description="SHA256 hash of the resolved manifest content"
    )
    artifacts: List[LockFileArtifact] = Field(
        ..., description="List of fully resolved artifact definitions"
    )

    def dump_canonical_json(self) -> str:
        """
        Dump the model to a JSON string in a consistent, canonical format.

        This method ensures that JSON output is always formatted the same way,
        which is critical for generating consistent hashes of the lockfile content.

        Returns:
            str: JSON string representation in a format optimized for hashing
                 (no whitespace, sorted keys, exclude_none=True)
        """
        return self.model_dump_json(exclude_none=True)

    def to_yaml(self) -> str:
        """
        Serialize the LockFile model to YAML.

        Returns:
            YAML string representation of the lock file
        """
        lockfile_dict = self.model_dump(exclude_none=True)
        return yaml.dump(lockfile_dict, default_flow_style=False, sort_keys=True)


# Cache System Models (Production Cache)


@dataclass
class CacheMetadata:
    """HTTP cache metadata following RFC 7234."""

    url: str
    content_hash: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    cache_time: Optional[datetime] = None
    max_age: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    size: int = 0


@dataclass
class ArtifactResolution:
    """Result of artifact resolution (local vs remote)."""

    type: str  # "local" or "remote"
    path: Optional[Path] = None
    url: Optional[str] = None
    cached_metadata: Optional[CacheMetadata] = None


@dataclass
class FetchResult:
    """Result of fetch operation."""

    success: bool
    was_cached: bool = False
    error_message: Optional[str] = None
    bytes_downloaded: int = 0
