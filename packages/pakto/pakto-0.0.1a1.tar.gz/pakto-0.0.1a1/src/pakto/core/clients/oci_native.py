"""OCI-Native Registry Client.

A native implementation of the OCI Distribution API that preserves bundle structure
and supports advanced OCI features including Referrers and Subjects.

This client serves as an alternative to the ORAS client, providing:
- Full OCI Distribution API compliance (v1.0+)
- Bundle structure preservation (2-layer semantic structure)
- Multi-registry authentication support
- Chunked upload functionality
- Session management and connection reuse
- Progress reporting
"""

import base64
import hashlib
import json
import ssl
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from pakto.core.clients.registry import RegistryClient
from pakto.core.oci_types import AnnotationKeys


@dataclass
class OciResult:
    """Result object for OCI operations."""

    success: bool
    error_message: Optional[str] = None
    digest: Optional[str] = None
    data: Optional[bytes] = None
    manifest: Optional[Dict[str, Any]] = None
    layers: Optional[List[Dict[str, Any]]] = None
    supported_versions: Optional[List[str]] = None
    referrers: Optional[List[Dict[str, Any]]] = None


class OciNativeRegistryClient(RegistryClient):
    """Native OCI Registry Client implementing OCI Distribution API.

    Provides direct HTTP-based implementation of the OCI Distribution specification
    with support for bundle structure preservation and advanced OCI features.
    """

    def __init__(self):
        """Initialize the OCI-Native Registry Client."""
        self._sessions: Dict[str, ClientSession] = {}
        self._auth_headers: Dict[str, str] = {}
        self._bearer_tokens: Dict[str, str] = {}
        self._timeout = ClientTimeout(total=300, connect=30)

    async def login(
        self, username: str | None = None, password: str | None = None, *args, **kwargs
    ) -> OciResult:
        """Login to registry with credentials.

        Args:
            username: Registry username
            password: Registry password

        Returns:
            OciResult with success status
        """
        try:
            if username and password:
                # Store basic auth credentials
                credentials = f"{username}:{password}"
                encoded = base64.b64encode(credentials.encode()).decode()
                self._auth_headers["Authorization"] = f"Basic {encoded}"

            return OciResult(success=True)

        except Exception as e:
            return OciResult(success=False, error_message=f"Login failed: {e}")

    async def logout(self, *args, **kwargs) -> OciResult:
        """Logout and cleanup sessions.

        Returns:
            OciResult with success status
        """
        try:
            # Close all sessions
            for session in self._sessions.values():
                await session.close()

            # Clear stored data
            self._sessions.clear()
            self._auth_headers.clear()
            self._bearer_tokens.clear()

            return OciResult(success=True)

        except Exception as e:
            return OciResult(success=False, error_message=f"Logout failed: {e}")

    async def push(
        self, reference: str, manifest: Dict[str, Any], *args, **kwargs
    ) -> OciResult:
        """Push a complete bundle to registry.

        Args:
            reference: Full registry reference (registry/repo:tag)
            manifest: OCI manifest to push

        Returns:
            OciResult with success status
        """
        try:
            # Parse reference
            registry_url, repo, tag = self._parse_reference(reference)

            # Validate manifest
            validation_result = await self._validate_manifest(manifest)
            if not validation_result.success:
                return validation_result

            # Push manifest
            return await self._put_manifest(f"{registry_url}/{repo}", tag, manifest)

        except Exception as e:
            return OciResult(success=False, error_message=f"Push failed: {e}")

    async def pull(self, reference: str, *args, **kwargs) -> OciResult:
        """Pull a complete bundle from registry.

        Args:
            reference: Full registry reference (registry/repo:tag)

        Returns:
            OciResult with manifest and layer data
        """
        try:
            # Parse reference
            registry_url, repo, tag = self._parse_reference(reference)

            # Get manifest
            manifest_result = await self._get_manifest(f"{registry_url}/{repo}", tag)
            if not manifest_result.success:
                return manifest_result

            manifest = manifest_result.manifest
            layers = []

            # Download all layers
            for layer in manifest.get("layers", []):
                layer_result = await self._download_blob(
                    f"{registry_url}/{repo}", layer["digest"]
                )

                if not layer_result.success:
                    return layer_result

                layer_type = layer.get("annotations", {}).get(
                    AnnotationKeys.LAYER_TYPE, "unknown"
                )

                layer_info = {
                    "type": layer_type,
                    "digest": layer["digest"],
                    "size": layer["size"],
                    "data": layer_result.data,
                }
                layers.append(layer_info)

            return OciResult(success=True, manifest=manifest, layers=layers)

        except Exception as e:
            return OciResult(success=False, error_message=f"Pull failed: {e}")

    async def _get_session(self, registry_url: str) -> ClientSession:
        """Get or create HTTP session for registry.

        Args:
            registry_url: Registry URL

        Returns:
            aiohttp ClientSession
        """
        if registry_url not in self._sessions:
            # Create SSL context that skips verification for localhost
            ssl_context = ssl.create_default_context()
            if "localhost" in registry_url:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)

            self._sessions[registry_url] = ClientSession(
                connector=connector,
                timeout=self._timeout,
                headers=self._auth_headers.copy(),
            )

        return self._sessions[registry_url]

    async def _get_bearer_token(
        self, registry: str, repository: str, scope: str
    ) -> str:
        """Get Bearer token for registry authentication.

        Args:
            registry: Registry hostname
            repository: Repository name
            scope: Access scope (pull, push, etc.)

        Returns:
            Bearer token string
        """
        auth_url = self._get_auth_url(registry)
        cache_key = f"{registry}:{repository}:{scope}"

        if cache_key in self._bearer_tokens:
            return self._bearer_tokens[cache_key]

        params = {"service": registry, "scope": f"repository:{repository}:{scope}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(auth_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token", "")
                    self._bearer_tokens[cache_key] = token
                    return token

        return ""

    def _get_auth_url(self, registry: str) -> str:
        """Get authentication URL for registry.

        Args:
            registry: Registry hostname

        Returns:
            Authentication URL
        """
        if registry in ["docker.io", "registry-1.docker.io"]:
            return "https://auth.docker.io/token"
        if registry == "ghcr.io":
            return "https://ghcr.io/token"
        # Default to registry's /token endpoint
        return f"http://{registry}/token"

    async def _get_manifest(self, repo_url: str, reference: str) -> OciResult:
        """Get manifest from registry.

        Args:
            repo_url: Repository URL (registry/repo)
            reference: Tag or digest

        Returns:
            OciResult with manifest data
        """
        try:
            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]
            url = f"http://{registry_url}/v2/{repo_name}/manifests/{reference}"

            headers = {
                "Accept": "application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json"
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    manifest = await response.json()
                    return OciResult(success=True, manifest=manifest)
                if response.status == 404:
                    return OciResult(success=False, error_message="Manifest not found")
                error_text = await response.text()
                return OciResult(
                    success=False,
                    error_message=f"Failed to get manifest: {response.status} {error_text}",
                )

        except Exception as e:
            return OciResult(
                success=False, error_message=f"Failed to get manifest: {e}"
            )

    async def _put_manifest(
        self, repo_url: str, reference: str, manifest: Dict[str, Any]
    ) -> OciResult:
        """Put manifest to registry.

        Args:
            repo_url: Repository URL (registry/repo)
            reference: Tag or digest
            manifest: Manifest data

        Returns:
            OciResult with success status and digest
        """
        try:
            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]
            url = f"http://{registry_url}/v2/{repo_name}/manifests/{reference}"

            manifest_json = json.dumps(manifest, separators=(",", ":"))

            headers = {"Content-Type": "application/vnd.oci.image.manifest.v1+json"}

            async with session.put(
                url, data=manifest_json, headers=headers
            ) as response:
                if response.status in [201, 200]:
                    digest = response.headers.get("Docker-Content-Digest", "")
                    return OciResult(success=True, digest=digest)
                error_text = await response.text()
                return OciResult(
                    success=False,
                    error_message=f"Failed to put manifest: {response.status} {error_text}",
                )

        except Exception as e:
            return OciResult(
                success=False, error_message=f"Failed to put manifest: {e}"
            )

    async def _upload_blob(
        self, repo_url: str, blob_data: bytes, progress_callback: Callable | None = None
    ) -> OciResult:
        """Upload blob to registry.

        Args:
            repo_url: Repository URL (registry/repo)
            blob_data: Blob data to upload
            progress_callback: Optional progress callback

        Returns:
            OciResult with success status and digest
        """
        try:
            # Calculate digest
            digest = f"sha256:{hashlib.sha256(blob_data).hexdigest()}"

            # Check if blob already exists
            blob_exists = await self._blob_exists(repo_url, digest)
            if blob_exists:
                return OciResult(success=True, digest=digest)

            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]

            # Start upload session
            upload_url = f"http://{registry_url}/v2/{repo_name}/blobs/uploads/"

            async with session.post(upload_url) as response:
                if response.status != 202:
                    error_text = await response.text()
                    return OciResult(
                        success=False,
                        error_message=f"Failed to start upload: {response.status} {error_text}",
                    )

                location = response.headers.get("Location", "")
                if not location:
                    return OciResult(
                        success=False, error_message="No upload location provided"
                    )

            # Complete upload
            upload_complete_url = f"http://{registry_url}{location}?digest={digest}"

            async with session.put(upload_complete_url, data=blob_data) as response:
                if response.status in [201, 200]:
                    final_digest = response.headers.get("Docker-Content-Digest", digest)

                    if progress_callback:
                        progress_callback({
                            "type": "upload_progress",
                            "bytes_uploaded": len(blob_data),
                            "total_bytes": len(blob_data),
                        })

                    return OciResult(success=True, digest=final_digest)
                error_text = await response.text()
                return OciResult(
                    success=False,
                    error_message=f"Failed to complete upload: {response.status} {error_text}",
                )

        except Exception as e:
            return OciResult(success=False, error_message=f"Failed to upload blob: {e}")

    async def _upload_blob_chunked(
        self,
        repo_url: str,
        blob_data: bytes,
        chunk_size: int = 64 * 1024,
        progress_callback: Callable | None = None,
    ) -> OciResult:
        """Upload blob using chunked transfer.

        Args:
            repo_url: Repository URL (registry/repo)
            blob_data: Blob data to upload
            chunk_size: Size of each chunk
            progress_callback: Optional progress callback

        Returns:
            OciResult with success status and digest
        """
        try:
            # Calculate digest
            digest = f"sha256:{hashlib.sha256(blob_data).hexdigest()}"

            # Check if blob already exists
            blob_exists = await self._blob_exists(repo_url, digest)
            if blob_exists:
                return OciResult(success=True, digest=digest)

            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]

            # Start upload session
            upload_url = f"http://{registry_url}/v2/{repo_name}/blobs/uploads/"

            async with session.post(upload_url) as response:
                if response.status != 202:
                    error_text = await response.text()
                    return OciResult(
                        success=False,
                        error_message=f"Failed to start chunked upload: {response.status} {error_text}",
                    )

                location = response.headers.get("Location", "")
                if not location:
                    return OciResult(
                        success=False, error_message="No upload location provided"
                    )

            # Upload chunks
            bytes_uploaded = 0
            current_location = location

            for i in range(0, len(blob_data), chunk_size):
                chunk = blob_data[i : i + chunk_size]
                is_final_chunk = (i + chunk_size) >= len(blob_data)

                if is_final_chunk:
                    # Final chunk - complete upload
                    upload_complete_url = (
                        f"http://{registry_url}{current_location}?digest={digest}"
                    )

                    async with session.put(upload_complete_url, data=chunk) as response:
                        if response.status in [201, 200]:
                            final_digest = response.headers.get(
                                "Docker-Content-Digest", digest
                            )
                            return OciResult(success=True, digest=final_digest)
                        error_text = await response.text()
                        return OciResult(
                            success=False,
                            error_message=f"Failed to complete chunked upload: {response.status} {error_text}",
                        )
                else:
                    # Intermediate chunk
                    chunk_url = f"http://{registry_url}{current_location}"

                    headers = {
                        "Content-Range": f"{bytes_uploaded}-{bytes_uploaded + len(chunk) - 1}"
                    }

                    async with session.patch(
                        chunk_url, data=chunk, headers=headers
                    ) as response:
                        if response.status != 202:
                            error_text = await response.text()
                            return OciResult(
                                success=False,
                                error_message=f"Failed to upload chunk: {response.status} {error_text}",
                            )

                        current_location = response.headers.get(
                            "Location", current_location
                        )

                bytes_uploaded += len(chunk)

                if progress_callback:
                    progress_callback({
                        "type": "upload_progress",
                        "bytes_uploaded": bytes_uploaded,
                        "total_bytes": len(blob_data),
                    })

            return OciResult(
                success=False,
                error_message="Chunked upload completed without final response",
            )

        except Exception as e:
            return OciResult(
                success=False, error_message=f"Failed to upload blob chunked: {e}"
            )

    async def _download_blob(
        self, repo_url: str, digest: str, progress_callback: Callable | None = None
    ) -> OciResult:
        """Download blob from registry.

        Args:
            repo_url: Repository URL (registry/repo)
            digest: Blob digest
            progress_callback: Optional progress callback

        Returns:
            OciResult with blob data
        """
        try:
            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]
            url = f"http://{registry_url}/v2/{repo_name}/blobs/{digest}"

            async with session.get(url) as response:
                if response.status == 200:
                    blob_data = await response.read()

                    if progress_callback:
                        progress_callback({
                            "type": "download_progress",
                            "bytes_downloaded": len(blob_data),
                            "total_bytes": len(blob_data),
                        })

                    return OciResult(success=True, data=blob_data)
                if response.status == 404:
                    return OciResult(success=False, error_message="Blob not found")
                error_text = await response.text()
                return OciResult(
                    success=False,
                    error_message=f"Failed to download blob: {response.status} {error_text}",
                )

        except Exception as e:
            return OciResult(
                success=False, error_message=f"Failed to download blob: {e}"
            )

    async def _blob_exists(self, repo_url: str, digest: str) -> bool:
        """Check if blob exists in registry.

        Args:
            repo_url: Repository URL (registry/repo)
            digest: Blob digest

        Returns:
            True if blob exists, False otherwise
        """
        try:
            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]
            url = f"http://{registry_url}/v2/{repo_name}/blobs/{digest}"

            async with session.head(url) as response:
                return response.status == 200

        except Exception:
            return False

    async def _get_referrers(self, repo_url: str, digest: str) -> OciResult:
        """Get referrers for a manifest.

        Args:
            repo_url: Repository URL (registry/repo)
            digest: Subject manifest digest

        Returns:
            OciResult with referrers list
        """
        try:
            registry_url = repo_url.split("/", maxsplit=1)[0]
            session = await self._get_session(registry_url)

            repo_name = repo_url.split("/", 1)[1]
            url = f"http://{repo_url}/v2/{repo_name}/referrers/{digest}"

            async with session.get(url) as response:
                if response.status == 200:
                    referrers_data = await response.json()
                    referrers = referrers_data.get("manifests", [])
                    return OciResult(success=True, referrers=referrers)
                if response.status == 404:
                    # No referrers found
                    return OciResult(success=True, referrers=[])
                error_text = await response.text()
                return OciResult(
                    success=False,
                    error_message=f"Failed to get referrers: {response.status} {error_text}",
                )

        except Exception as e:
            return OciResult(
                success=False, error_message=f"Failed to get referrers: {e}"
            )

    async def _get_api_version(self) -> OciResult:
        """Get supported API versions from registry.

        Returns:
            OciResult with supported versions
        """
        # For now, assume OCI Distribution API v1.0+ support
        return OciResult(success=True, supported_versions=["1.0", "1.1"])

    async def _discover_endpoints(self) -> Dict[str, str]:
        """Discover available API endpoints.

        Returns:
            Dictionary of endpoint names to paths
        """
        return {
            "manifests": "/v2/{name}/manifests/{reference}",
            "blobs": "/v2/{name}/blobs/{digest}",
            "uploads": "/v2/{name}/blobs/uploads/",
            "referrers": "/v2/{name}/referrers/{digest}",
        }

    async def _validate_manifest(self, manifest: Dict[str, Any]) -> OciResult:
        """Validate OCI manifest structure.

        Args:
            manifest: Manifest to validate

        Returns:
            OciResult with validation status
        """
        try:
            # Basic validation
            required_fields = ["schemaVersion", "mediaType"]

            for field in required_fields:
                if field not in manifest:
                    return OciResult(
                        success=False, error_message=f"Missing required field: {field}"
                    )

            # Check schema version
            if manifest["schemaVersion"] != 2:
                return OciResult(
                    success=False, error_message="Unsupported schema version"
                )

            # Check media type
            valid_media_types = [
                "application/vnd.oci.image.manifest.v1+json",
                "application/vnd.docker.distribution.manifest.v2+json",
            ]

            if manifest["mediaType"] not in valid_media_types:
                return OciResult(success=False, error_message="Invalid media type")

            return OciResult(success=True)

        except Exception as e:
            return OciResult(
                success=False, error_message=f"Manifest validation failed: {e}"
            )

    def _parse_reference(self, reference: str) -> tuple:
        """Parse registry reference into components.

        Args:
            reference: Full reference (registry/repo:tag)

        Returns:
            Tuple of (registry_url, repository, tag)
        """
        if "://" in reference:
            # Remove protocol
            reference = reference.split("://", 1)[1]

        if "/" not in reference:
            msg = "Invalid reference format"
            raise ValueError(msg)

        parts = reference.split("/")
        registry_url = parts[0]

        repo_and_tag = "/".join(parts[1:])

        if ":" in repo_and_tag:
            repo, tag = repo_and_tag.rsplit(":", 1)
        else:
            repo = repo_and_tag
            tag = "latest"

        return registry_url, repo, tag
