"""
OCI types and media type definitions for Pakto bundles.

This module defines the media types, manifest structures, and annotations
following OCI Distribution Specification 1.1.1.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .constants import DEFAULTS
from .models import LockFile

# OCI v1.1.0 empty config constants
OCI_EMPTY_CONFIG_DIGEST = (
    "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
)
OCI_EMPTY_CONFIG_SIZE = 2
OCI_EMPTY_CONFIG_CONTENT = "{}"

METADATA_VERSION = "1.0"


# Media type definitions
class MediaTypes:
    """Standard media types for Pakto bundles and artifacts."""

    # Bundle-specific media types
    BUNDLE_MANIFEST = f"{DEFAULTS.APP_MEDIA_TYPE}.bundle.v1+json"
    BUNDLE_CONFIG = f"{DEFAULTS.APP_MEDIA_TYPE}.bundle.config.v1+json"

    # Artifact media types
    OCI_IMAGE_LAYER = "application/vnd.oci.image.layer.v1.tar+gzip"
    ARCHIVE_TAR_GZ = f"{DEFAULTS.APP_MEDIA_TYPE}.archive.v1+tar+gzip"
    CONFIG_JSON = f"{DEFAULTS.APP_MEDIA_TYPE}.config.v1+json"
    EXECUTABLE = f"{DEFAULTS.APP_MEDIA_TYPE}.executable.v1+octet-stream"

    # OCI standard media types
    OCI_MANIFEST = "application/vnd.oci.image.manifest.v1+json"
    OCI_INDEX = "application/vnd.oci.image.index.v1+json"
    OCI_LAYOUT = "application/vnd.oci.layout.header.v1+json"
    OCI_CONFIG = "application/vnd.oci.image.config.v1+json"
    OCI_EMPTY = "application/vnd.oci.empty.v1+json"

    # Custom App layer media types (OCI v1.1.0 compliant)
    APP_METADATA_LAYER = f"{DEFAULTS.APP_MEDIA_TYPE}.bundle.metadata.v1.tar+gzip"
    APP_ARTIFACTS_LAYER = f"{DEFAULTS.APP_MEDIA_TYPE}.bundle.artifacts.v1.tar+gzip"


class AnnotationKeys:
    """Standard annotation keys for Pakto bundles."""

    # org.opencontainers.image.documentation - URL to documentation

    # OCI standard annotations
    # org.opencontainers.image.title - Human-readable title
    TITLE = "org.opencontainers.image.title"

    # AnnotationUnpack is the annotation key for indication of unpacking. MUST BE ADDED TO ARTIFACTS LAYER
    UNPACK = "io.deis.oras.content.unpack"

    # AnnotationVersion is the annotation key for the version of the packaged software.
    # The version MAY match a label or tag in the source code repository.
    # The version MAY be Semantic versioning-compatible.
    # org.opencontainers.image.version - Version of the packaged software
    VERSION = "org.opencontainers.image.version"

    # org.opencontainers.image.revision - Annotation key for the source control revision identifier for the packaged software.
    REVISION = "org.opencontainers.image.revision"

    # org.opencontainers.image.description - Human-readable description
    DESCRIPTION = "org.opencontainers.image.description"

    # org.opencontainers.image.created - Creation date/time
    CREATED = "org.opencontainers.image.created"

    # org.opencontainers.image.authors - Contact details of people/organization
    AUTHORS = "org.opencontainers.image.authors"

    # org.opencontainers.image.vendor - Name of the distributing entity
    VENDOR = "org.opencontainers.image.vendor"

    # org.opencontainers.image.licenses - License(s) under which software is distributed
    LICENSES = "org.opencontainers.image.licenses"

    # org.opencontainers.image.url - URL to find more information
    URL = "org.opencontainers.image.url"

    # org.opencontainers.image.source - URL to source code
    SOURCE = "org.opencontainers.image.source"

    # org.opencontainers.image.ref.name - Reference name (tag) for the image
    REF_NAME = "org.opencontainers.image.ref.name"

    # org.opencontainers.image.documentation - URL to documentation
    DOCUMENTATION = "org.opencontainers.image.documentation"

    # org.opencontainers.image.base.digest - Digest of the image this image is based on
    BASE_DIGEST = "org.opencontainers.image.base.digest"

    # org.opencontainers.image.base.name - Image reference of the base image
    BASE_NAME = "org.opencontainers.image.base.name"

    # org.opencontainers.artifact.type - OCI artifact type annotation (deprecated in v1.1.0)
    ARTIFACT_TYPE = "org.opencontainers.artifact.type"

    # MediaTypeDescriptor specifies the media type for a content descriptor.
    # "application/vnd.oci.descriptor.v1+json",

    # MediaTypeLayoutHeader specifies the media type for the oci-layout.
    # "application/vnd.oci.layout.header.v1+json",

    # MediaTypeImageIndex specifies the media type for an image index.
    # "application/vnd.oci.image.index.v1+json",

    # MediaTypeImageManifest specifies the media type for an image manifest.
    # "application/vnd.oci.image.manifest.v1+json",

    # MediaTypeImageConfig specifies the media type for the image configuration.
    # "application/vnd.oci.image.config.v1+json",

    # MediaTypeEmptyJSON specifies the media type for an unused blob containing the value "{}".
    # "application/vnd.oci.empty.v1+json"

    # App-specific bundle annotations
    BUNDLE_NAME = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.name"
    BUNDLE_VERSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.version"
    BUNDLE_MANIFEST_HASH = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.manifest.hash"
    BUNDLE_LOCKFILE_HASH = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.lockfile.hash"
    BUNDLE_ARTIFACT_COUNT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.artifact.count"
    BUNDLE_TOTAL_SIZE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.total.size"

    BUNDLE_LAYER_COUNT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.layer.count"
    BUNDLE_COMPRESSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.compression"
    BUNDLE_FORMAT_VERSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.format.version"

    # Schema and metadata annotations
    SCHEMA_VERSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.schema.version"
    LOCKFILE_PATH = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.lockfile.path"
    LOCKFILE_GENERATED = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.lockfile.generated"
    LOCKFILE_GENERATOR = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.lockfile.generator"
    LOCKFILE_VERSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.lockfile.version"
    LOCKFILE_ARTIFACT_COUNT = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.lockfile.artifact.count"
    )
    MANIFEST_SOURCE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.manifest.source"
    METADATA_VERSION_KEY = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.metadata.version"

    # Entrypoint annotations
    ENTRYPOINT_SOURCE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.source"  # The full path to the script file when it was resolved
    ENTRYPOINT_SCRIPT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.script"  # The name of the script file in relation to the bundle
    ENTRYPOINT_CHECKSUM = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.checksum"
    ENTRYPOINT_SIZE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.size"
    ENTRYPOINT_UID = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.uid"
    ENTRYPOINT_GID = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.gid"
    ENTRYPOINT_MODE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.entrypoint.mode"

    # Artifact list and summary annotations
    ARTIFACTS_LIST = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.list"
    ARTIFACTS_TYPES = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.types"
    ARTIFACTS_COUNT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.count"
    ARTIFACTS_COUNT_BY_TYPE = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.count.by.type"
    )
    ARTIFACTS_TOTAL_SIZE_BYTES = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.total.size.bytes"
    )
    ARTIFACTS_TOTAL_SIZE_HUMAN = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.total.size.human"
    )
    ARTIFACTS_MANIFEST = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.manifest"

    # Source information annotations
    SOURCES_COUNT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.sources.count"
    SOURCES_DOMAINS = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.sources.domains"

    # Build information annotations
    BUILD_TIMESTAMP = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.build.timestamp"  # RFC 3339 timestamp when bundle was built
    BUILD_TOOL = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.build.tool"  # Name of the tool used to create the bundle
    BUILD_TOOL_VERSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.build.tool.version"  # Version of the build tool
    BUILD_ENVIRONMENT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.build.environment"  # Build environment (dev/staging/prod)
    BUILD_HOST = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.build.host"  # Hostname where bundle was built

    # Layer-specific annotations
    LAYER_TYPE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.type"  # Type of layer content (metadata, artifacts, config, etc.)
    LAYER_COMPRESSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.compression"  # Compression algorithm used (gzip, zstd, none)
    LAYER_CONTENTS = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.contents"  # Comma-separated list of layer contents
    LAYER_SIZE = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.size"  # Size of the layer in bytes
    )
    LAYER_CHECKSUM = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.checksum"  # SHA256 checksum of layer contents
    LAYER_INDEX = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.index"  # Index of the layer within the bundle
    LAYER_MEDIA_TYPE = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.media.type"  # Media type of the layer
    )

    # Per-artifact annotations (existing)
    ARTIFACT_NAME = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.name"
    ARTIFACT_TYPE_OLD = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.type"  # Renamed to avoid conflict
    )
    ARTIFACT_TARGET = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.target"
    ARTIFACT_ORIGIN = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.origin"
    ARTIFACT_CHECKSUM = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.checksum"
    ARTIFACT_SIZE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.size"
    ARTIFACT_INSTALL_PATH = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.install.path"
    ARTIFACT_ACTION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.action"
    ARTIFACT_BLOB_DIGEST = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.blob.digest"
    ARTIFACT_BLOB_SIZE = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifact.blob.size"

    # Index-specific annotations
    INDEX_VERSION = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.index.version"  # Version of the index format
    )
    INDEX_MANIFEST_COUNT = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.manifest.count"  # Number of manifests in index
    INDEX_BUNDLE_REFERENCE = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.bundle.reference"  # Bundle reference string
    )

    # Config-specific annotations
    CONFIG_VERSION = f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.config.version"  # Version of the config format
    CONFIG_LAYER_COUNT = (
        f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.count"  # Number of layers referenced
    )

    # ORAS compatibility annotations
    ORAS_UNPACK = "io.deis.oras.content.unpack"  # ORAS unpack indicator

    @classmethod
    def layer_annotation(cls, index: int, suffix: str) -> str:
        """Generate layer-specific annotation key."""
        return f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.layer.{index}.{suffix}"

    @classmethod
    def artifact_type_count(cls, artifact_type: str) -> str:
        """Generate artifact type count annotation key."""
        return f"{DEFAULTS.APP_ANNOTATION_DOMAIN}.artifacts.{artifact_type}.count"


class OrasDefaults:
    """Wrapper for ORAS default constants to maintain abstraction."""

    # Wrap ORAS annotation keys
    ANNOTATION_TITLE = "org.opencontainers.image.title"

    # Add any other ORAS defaults we use
    @classmethod
    def get_annotation_title(cls) -> str:
        """Get ORAS annotation title key."""
        return cls.ANNOTATION_TITLE


class LayerTypes:
    """Layer type constants for Pakto bundles."""

    METADATA = "metadata"
    ARTIFACT = "artifact"  # Individual artifact layer
    CONFIG = "config"
    SIGNATURE = "signature"


class CompressionTypes:
    """Compression type constants."""

    GZIP = "gzip"
    ZSTD = "zstd"
    NONE = "none"


class OCIDescriptor(BaseModel):
    """OCI content descriptor following the spec."""

    mediaType: str = Field(..., description="Media type of the referenced object")
    digest: str = Field(
        ..., description="Digest of the content (e.g., sha256:abc123...)"
    )
    size: int = Field(..., description="Size of the blob in bytes")
    urls: Optional[List[str]] = Field(
        None, description="Optional URLs for content retrieval"
    )
    annotations: Optional[Dict[str, str]] = Field(
        None, description="Optional annotations"
    )
    data: Optional[str] = Field(
        None, description="Optional embedded data (base64 encoded)"
    )


class OCIManifest(BaseModel):
    """OCI Image Manifest v1."""

    schemaVersion: int = Field(2, description="Manifest schema version")
    mediaType: str = Field(
        default=MediaTypes.OCI_MANIFEST, description="Media type of this manifest"
    )
    config: OCIDescriptor = Field(..., description="Configuration object descriptor")
    layers: List[OCIDescriptor] = Field(..., description="Layer descriptors")
    subject: Optional[OCIDescriptor] = Field(
        None, description="Subject manifest this artifact relates to"
    )
    annotations: Optional[Dict[str, str]] = Field(
        None, description="Annotations for this manifest"
    )


class OCIIndex(BaseModel):
    """OCI Image Index (manifest list)."""

    schemaVersion: int = Field(2, description="Index schema version")
    mediaType: str = Field(
        default=MediaTypes.OCI_INDEX, description="Media type of this index"
    )
    manifests: List[OCIDescriptor] = Field(..., description="Manifest descriptors")
    subject: Optional[OCIDescriptor] = Field(
        None, description="Subject this index relates to"
    )
    annotations: Optional[Dict[str, str]] = Field(
        None, description="Annotations for this index"
    )


class OCILayout(BaseModel):
    """OCI Layout header for local storage."""

    imageLayoutVersion: str = Field(default="1.0.0", description="OCI layout version")


class BundleConfig(BaseModel):
    """Configuration object for Pakto bundles."""

    mediaType: str = Field(
        default=MediaTypes.BUNDLE_CONFIG, description="Config media type"
    )
    bundleName: str = Field(..., description="Name of the bundle")
    bundleVersion: str = Field(..., description="Bundle version")
    created: datetime = Field(..., description="Bundle creation timestamp")
    artifacts: List[Dict[str, str]] = Field(
        ..., description="List of artifacts in the bundle"
    )
    metadata: Optional[Dict[str, str]] = Field(None, description="Additional metadata")


def get_media_type_for_file(filename: str) -> str:
    """
    Determine the appropriate media type for a file based on its extension.

    // MediaTypeDescriptor specifies the media type for a content descriptor.
        MediaTypeDescriptor = "application/vnd.oci.descriptor.v1+json"

        // MediaTypeLayoutHeader specifies the media type for the oci-layout.
        MediaTypeLayoutHeader = "application/vnd.oci.layout.header.v1+json"

        // MediaTypeImageIndex specifies the media type for an image index.
        MediaTypeImageIndex = "application/vnd.oci.image.index.v1+json"

        // MediaTypeImageManifest specifies the media type for an image manifest.
        MediaTypeImageManifest = "application/vnd.oci.image.manifest.v1+json"

        // MediaTypeImageConfig specifies the media type for the image configuration.
        MediaTypeImageConfig = "application/vnd.oci.image.config.v1+json"

        // MediaTypeEmptyJSON specifies the media type for an unused blob containing the value "{}".
        MediaTypeEmptyJSON = "application/vnd.oci.empty.v1+json"

    // MediaTypeImageLayer is the media type used for layers referenced by the manifest.
    MediaTypeImageLayer = "application/vnd.oci.image.layer.v1.tar"

        // MediaTypeImageLayerGzip is the media type used for gzipped layers
        // referenced by the manifest.
        MediaTypeImageLayerGzip = "application/vnd.oci.image.layer.v1.tar+gzip"

        // MediaTypeImageLayerZstd is the media type used for zstd compressed
        // layers referenced by the manifest.
        MediaTypeImageLayerZstd = "application/vnd.oci.image.layer.v1.tar+zstd"

    Args:
        filename: Name of the file

    Returns:
        Appropriate media type string
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".tar"):
        return MediaTypes.OCI_IMAGE_LAYER
    if filename_lower.endswith(".tar.gz") or filename_lower.endswith(".tgz"):
        return MediaTypes.OCI_IMAGE_LAYER
    if filename_lower.endswith(".json"):
        return MediaTypes.CONFIG_JSON
    if filename_lower.endswith(".sh") or filename_lower.endswith(".exe"):
        return MediaTypes.EXECUTABLE
    # Default to generic blob
    return "application/octet-stream"


def create_bundle_annotations(
    lockfile: LockFile,
    description: str,
    manifest_hash: str,
    lockfile_hash: str,
    artifact_count: int,
    total_size: int,
    bundle_name: Optional[str] = None,
    bundle_version: Optional[str] = None,
    authors: Optional[str] = None,
    vendor: Optional[str] = None,
    licenses: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create standard annotations for a Pakto bundle.

    Args:
        lockfile: Lockfile object
        description: Human-readable description
        manifest_hash: Hash of the source manifest
        lockfile_hash: Hash of the lockfile
        artifact_count: Number of artifacts in the bundle
        total_size: Total size in bytes
        bundle_name: Optional name of the bundle (defaults to lockfile name)
        bundle_version: Optional version of the bundle (defaults to lockfile version)
        authors: Optional authors information
        vendor: Optional vendor name
        licenses: Optional license information

    Returns:
        Dictionary of annotations
    """
    bundle_name = bundle_name or lockfile.name
    bundle_version = bundle_version or lockfile.version

    entrypoint = lockfile.entrypoint

    annotations = {
        AnnotationKeys.TITLE: bundle_name,
        AnnotationKeys.DESCRIPTION: description,
        AnnotationKeys.VERSION: bundle_version,
        AnnotationKeys.BUNDLE_NAME: bundle_name,
        AnnotationKeys.BUNDLE_VERSION: bundle_version,
        AnnotationKeys.BUNDLE_MANIFEST_HASH: manifest_hash,
        AnnotationKeys.BUNDLE_LOCKFILE_HASH: lockfile_hash,
        AnnotationKeys.BUNDLE_ARTIFACT_COUNT: str(artifact_count),
        AnnotationKeys.BUNDLE_TOTAL_SIZE: f"{total_size / (1024 * 1024):.1f}MB",
    }

    if authors:
        annotations[AnnotationKeys.AUTHORS] = authors
    if vendor:
        annotations[AnnotationKeys.VENDOR] = vendor
    if licenses:
        annotations[AnnotationKeys.LICENSES] = licenses
    if entrypoint:
        entrypoint_script_path = Path(entrypoint.script)
        entrypoint_script_name = entrypoint_script_path.name
        annotations[AnnotationKeys.ENTRYPOINT_SOURCE] = str(entrypoint_script_path)
        annotations[AnnotationKeys.ENTRYPOINT_SCRIPT] = entrypoint_script_name
        annotations[AnnotationKeys.ENTRYPOINT_CHECKSUM] = entrypoint.checksum
        annotations[AnnotationKeys.ENTRYPOINT_MODE] = entrypoint.mode
        annotations[AnnotationKeys.ENTRYPOINT_SIZE] = str(entrypoint.size)
        if entrypoint.uid:
            annotations[AnnotationKeys.ENTRYPOINT_UID] = entrypoint.uid
        if entrypoint.gid:
            annotations[AnnotationKeys.ENTRYPOINT_GID] = entrypoint.gid
    return annotations


def create_artifact_annotations(
    artifact_name: str,
    artifact_type: str,
    target_path: str,
    origin_url: str,
    checksum: str,
    install_path: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create annotations for an individual artifact layer.

    Args:
        artifact_name: Name of the artifact
        artifact_type: Type (oci, file, http, etc.)
        target_path: Target installation path
        origin_url: Original source URL
        checksum: Artifact checksum
        install_path: Optional installation directory

    Returns:
        Dictionary of annotations
    """
    annotations = {
        AnnotationKeys.ARTIFACT_NAME: artifact_name,
        AnnotationKeys.ARTIFACT_TYPE_OLD: artifact_type,
        AnnotationKeys.ARTIFACT_TARGET: target_path,
        AnnotationKeys.ARTIFACT_ORIGIN: origin_url,
        AnnotationKeys.ARTIFACT_CHECKSUM: checksum,
    }

    if install_path:
        annotations[AnnotationKeys.ARTIFACT_INSTALL_PATH] = install_path

    return annotations


class OCIGateway:
    """Centralized gateway for OCI 1.1 compliant bundle creation and annotation management."""

    # Media Type Methods
    @staticmethod
    def get_layer_media_type(layer_type: str, compression: str = "gzip") -> str:
        """Get appropriate media type for layer based on type and compression."""
        if layer_type == LayerTypes.METADATA:
            return MediaTypes.APP_METADATA_LAYER
        if layer_type == LayerTypes.ARTIFACT:
            return MediaTypes.APP_ARTIFACTS_LAYER
        # Fallback to generic OCI layer types
        if compression == CompressionTypes.GZIP:
            return "application/vnd.oci.image.layer.v1.tar+gzip"
        if compression == CompressionTypes.ZSTD:
            return "application/vnd.oci.image.layer.v1.tar+zstd"
        if compression == CompressionTypes.NONE:
            return "application/vnd.oci.image.layer.v1.tar"
        return "application/vnd.oci.image.layer.v1.tar+gzip"  # Default to gzip

    @staticmethod
    def get_manifest_media_type() -> str:
        """Get OCI manifest media type."""
        return MediaTypes.OCI_MANIFEST

    @staticmethod
    def get_config_media_type() -> str:
        """Get OCI config media type."""
        return MediaTypes.OCI_CONFIG

    @staticmethod
    def get_empty_config_media_type() -> str:
        """Get OCI empty config media type for artifacts."""
        return MediaTypes.OCI_EMPTY

    @staticmethod
    def get_empty_config_descriptor() -> Dict[str, any]:
        """Get OCI empty config descriptor for artifacts."""
        return {
            "mediaType": MediaTypes.OCI_EMPTY,
            "digest": OCI_EMPTY_CONFIG_DIGEST,
            "size": OCI_EMPTY_CONFIG_SIZE,
        }

    @staticmethod
    def get_index_media_type() -> str:
        """Get OCI index media type."""
        return MediaTypes.OCI_INDEX

    # Annotation Methods
    @staticmethod
    def create_metadata_layer_annotations(lockfile: LockFile) -> Dict[str, str]:
        """
        Create OCI 1.1 compliant annotations for metadata layer.

        Args:
            lockfile: Lockfile object to analyze for contents

        Returns:
            Dictionary of OCI standard and App-specific annotations
        """

        # Dynamically determine what's in the metadata layer
        contents = ["lockfile", "artifact-index"]
        if getattr(lockfile, "entrypoint", None):
            contents.append("entrypoint")

        return {
            # OCI Standard annotations
            AnnotationKeys.TITLE: "Pakto Bundle Metadata",
            AnnotationKeys.DESCRIPTION: "Lockfile and artifact index for bundle verification",
            # App-specific layer annotations
            AnnotationKeys.LAYER_TYPE: LayerTypes.METADATA,
            AnnotationKeys.LAYER_CONTENTS: ",".join(contents),
            AnnotationKeys.LAYER_COMPRESSION: CompressionTypes.GZIP,
            # Lockfile-specific annotations
            AnnotationKeys.LOCKFILE_VERSION: getattr(lockfile, "apiVersion", "unknown"),
            AnnotationKeys.LOCKFILE_ARTIFACT_COUNT: str(len(lockfile.artifacts or [])),
            AnnotationKeys.METADATA_VERSION_KEY: METADATA_VERSION,
        }

    @staticmethod
    def create_config_annotations(lockfile: LockFile, layers: list) -> Dict[str, str]:
        """
        Create OCI 1.1 compliant annotations for config object.

        Args:
            lockfile: Lockfile object
            layers: List of layer objects

        Returns:
            Dictionary of config-specific annotations
        """

        return {
            # OCI Standard annotations
            AnnotationKeys.TITLE: "Bundle Configuration",
            AnnotationKeys.DESCRIPTION: "Configuration for Pakto bundle",
            # App-specific annotations
            AnnotationKeys.CONFIG_VERSION: "1.0",
            AnnotationKeys.CONFIG_LAYER_COUNT: str(len(layers)),
        }

    @staticmethod
    def create_manifest_annotations(
        lockfile: LockFile,
        bundle_name: str,
        tag: str = "latest",
        lockfile_path: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Create comprehensive OCI 1.1 compliant annotations for manifest.

        Args:
            lockfile: Lockfile object
            bundle_name: Name of the bundle
            tag: Bundle version tag
            lockfile_path: Path to the lockfile (for filename extraction)
            **kwargs: Additional optional parameters

        Returns:
            Dictionary of comprehensive manifest annotations
        """
        import os
        import subprocess
        from datetime import datetime, timezone
        from urllib.parse import urlparse

        from .constants import DEFAULTS

        # Calculate artifact statistics
        artifacts = lockfile.artifacts or []
        artifact_count = len(artifacts)

        # Calculate artifact types and counts
        artifact_types = set()
        for artifact in artifacts:
            artifact_types.add(artifact.type)

        # Calculate total artifact size
        total_size_bytes = sum(getattr(artifact, "size", 0) for artifact in artifacts)
        total_size_human = (
            f"{total_size_bytes / (1024 * 1024 * 1024):.1f}GB"
            if total_size_bytes > 1024 * 1024 * 1024
            else f"{total_size_bytes / (1024 * 1024):.1f}MB"
        )

        # Extract source domains
        source_domains = set()
        for artifact in artifacts:
            origin = artifact.origin
            if origin.startswith(("http://", "https://")):
                domain = urlparse(origin).netloc
                source_domains.add(domain)
            elif origin.startswith("oci://"):
                oci_part = origin.replace("oci://", "")
                if "/" in oci_part:
                    domain = oci_part.split("/")[0]
                    source_domains.add(domain)

        # Create artifact list for annotation
        artifact_list_items = [
            f"{artifact.name}@{artifact.type}:{artifact.target}"
            for artifact in artifacts
        ]
        artifact_list = ";".join(artifact_list_items)

        # Generate hashes if available
        lockfile_hash = getattr(
            lockfile, "lockfileHash", getattr(lockfile, "hash", "unknown")
        )
        manifest_hash = getattr(
            lockfile, "manifestHash", getattr(lockfile, "manifest_hash", "unknown")
        )

        # Determine actual lockfile name
        actual_lockfile_name = DEFAULTS.DEFAULT_LOCKFILE_NAME
        if lockfile_path:
            actual_lockfile_name = Path(lockfile_path).name

        # Get git revision if available
        git_revision = "unknown"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                git_revision = result.stdout.strip()[:12]  # Short hash
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Get build environment
        build_environment = os.getenv("PAKTO_BUILD_ENV", "development")
        build_host = os.getenv("HOSTNAME", os.getenv("COMPUTERNAME", "unknown"))

        # Current timestamp
        datetime.now(timezone.utc).isoformat()

        return {
            # OCI Standard Bundle Identity (11 annotations) - removed timestamp, ref_name, and artifact_type
            AnnotationKeys.TITLE: f"{bundle_name}-v{tag}",
            AnnotationKeys.DESCRIPTION: f"Deployment bundle containing {artifact_count} artifacts from {len(source_domains)} sources",
            AnnotationKeys.VERSION: tag,
            AnnotationKeys.VENDOR: "Warrical",
            AnnotationKeys.LICENSES: "Apache-2.0",
            AnnotationKeys.URL: "https://warrical.com",
            AnnotationKeys.DOCUMENTATION: "https://docs.warrical.com/pakto",
            AnnotationKeys.SOURCE: "https://github.com/warrical/pakto",
            AnnotationKeys.REVISION: git_revision,
            AnnotationKeys.BASE_NAME: "scratch",
            # App-specific annotations
            AnnotationKeys.BUNDLE_NAME: bundle_name,
            AnnotationKeys.BUNDLE_VERSION: tag,
            AnnotationKeys.BUNDLE_MANIFEST_HASH: manifest_hash,
            AnnotationKeys.BUNDLE_LOCKFILE_HASH: lockfile_hash,
            AnnotationKeys.BUNDLE_ARTIFACT_COUNT: str(artifact_count),
            AnnotationKeys.BUNDLE_TOTAL_SIZE: total_size_human,
            AnnotationKeys.SCHEMA_VERSION: getattr(
                lockfile, "apiVersion", DEFAULTS.SCHEMA_VERSION_VALUE
            ),
            AnnotationKeys.LOCKFILE_PATH: actual_lockfile_name,
            # Artifact Summary (5 annotations)
            AnnotationKeys.ARTIFACTS_LIST: artifact_list,
            AnnotationKeys.ARTIFACTS_TYPES: ",".join(sorted(artifact_types)),
            AnnotationKeys.ARTIFACTS_TOTAL_SIZE_BYTES: str(total_size_bytes),
            AnnotationKeys.ARTIFACTS_TOTAL_SIZE_HUMAN: total_size_human,
            AnnotationKeys.SOURCES_DOMAINS: ",".join(sorted(source_domains)),
            # Build & Environment (4 annotations) - removed timestamp for reproducibility
            AnnotationKeys.BUILD_TOOL: "pakto-pack",
            AnnotationKeys.BUILD_TOOL_VERSION: "0.0.1",
            AnnotationKeys.BUILD_ENVIRONMENT: build_environment,
            AnnotationKeys.BUILD_HOST: build_host,
            AnnotationKeys.SOURCES_COUNT: str(len(source_domains)),
        }

    @staticmethod
    def create_index_annotations(
        bundle_name: str, tag: str = "latest"
    ) -> Dict[str, str]:
        """
        Create OCI 1.1 compliant annotations for index.

        Args:
            bundle_name: Name of the bundle
            tag: Bundle version tag

        Returns:
            Dictionary of index-specific annotations
        """

        return {
            # OCI Standard annotations
            AnnotationKeys.TITLE: "Bundle Index",
            AnnotationKeys.DESCRIPTION: "Index for Pakto bundle manifests",
            # App-specific annotations
            AnnotationKeys.INDEX_VERSION: "1.0",
            AnnotationKeys.INDEX_MANIFEST_COUNT: "1",
            AnnotationKeys.INDEX_BUNDLE_REFERENCE: f"{bundle_name}:{tag}",
        }

    @staticmethod
    def add_layer_size_annotations(
        annotations: Dict[str, str], layers: list
    ) -> Dict[str, str]:
        """
        Add dynamic layer size annotations to manifest.

        Args:
            annotations: Existing annotations dictionary
            layers: List of layer objects with size information

        Returns:
            Updated annotations with layer size information
        """
        for i, layer in enumerate(layers):
            layer_type = LayerTypes.METADATA if i == 0 else LayerTypes.ARTIFACT
            annotations[AnnotationKeys.layer_annotation(i, "type")] = layer_type
            annotations[AnnotationKeys.layer_annotation(i, "size")] = str(
                layer.get("size", 0)
            )

        return annotations
