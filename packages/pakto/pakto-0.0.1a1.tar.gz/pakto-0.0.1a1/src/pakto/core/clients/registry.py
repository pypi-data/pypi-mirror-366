from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from oras.client import OrasClient
from requests import Response

# --- Existing RegistryClient interface for push/pull (ORAS) ---


class RegistryClient(ABC):
    """All clients for the registry must be of this type"""

    @abstractmethod
    def login(self, *args, **kwargs) -> Union[Response, Any]:
        """Login to registry"""

    @abstractmethod
    def logout(self, *args, **kwargs) -> Union[Response, Any]:
        """Logout from registry"""

    @abstractmethod
    def push(self, *args, **kwargs) -> Union[Response, Any]:
        """Push content to registry"""

    @abstractmethod
    def pull(self, *args, **kwargs) -> Union[Response, Any]:
        """Pull content from registry"""


class OrasRegistryClient(RegistryClient):
    """
    Wrapper around OrasClient that satisfies both RegistryClient interface
    and transparently delegates all OrasClient methods.
    """

    def __init__(self, *args, **kwargs):
        """Initialize with same arguments as OrasClient"""
        self._client = OrasClient(*args, **kwargs)

    def __getattr__(self, name):
        """
        Transparently delegate any method/attribute access to the wrapped client.
        This is called when the attribute is not found in this class.
        """
        return getattr(self._client, name)

    def __repr__(self):
        return f"OrasRegistryClient(wrapped={self._client!r})"

    def login(self, *args, **kwargs):
        """Login to registry"""
        # self._client._tls_verify = kwargs.pop("insecure", True)
        return self._client.login(*args, **kwargs)

    def logout(self, *args, **kwargs):
        """Logout from registry"""
        return self._client.logout(*args, **kwargs)

    def push(self, *args, **kwargs):
        """Push content to registry"""
        return self._client.push(*args, **kwargs)

    def pull(self, *args, **kwargs):
        """Pull content from registry"""
        return self._client.pull(*args, **kwargs)


# --- New DockerRegistryClient for image metadata (digest/size) ---


class DockerRegistryClient:
    """Custom Docker Registry V2 client for image digest and size (anonymous access)."""

    def __init__(self):
        self.session = requests.Session()

    def _parse_image_name(self, image: str) -> Tuple[str, str, str]:
        """Parse image name into registry, repository, and reference (tag or digest)."""
        digest = None
        tag = None

        # Remove protocol if present
        if "://" in image:
            image = image.split("://", 1)[1]

        # Extract digest if present
        if "@" in image:
            image, digest = image.split("@", 1)

        # Extract tag if present
        if ":" in image:
            image, tag = image.rsplit(":", 1)

        # Split into parts
        parts = image.split("/")

        # Determine registry
        registry = parts.pop(0) if "." in parts[0] or ":" in parts[0] else "docker.io"

        # Build repository
        repository = "/".join(parts)

        # Handle Docker Hub official images
        if registry in ("docker.io", "index.docker.io") and "/" not in repository:
            repository = f"library/{repository}"

        # Determine reference
        reference = digest or (tag or "latest")

        return registry, repository, reference

    def _get_api_host(self, registry: str) -> str:
        """Get the API host for a registry."""
        return (
            "registry-1.docker.io"
            if registry in ("docker.io", "index.docker.io")
            else registry
        )

    def _get_token(self, registry: str, repository: str) -> Optional[str]:
        """Get anonymous token for registry."""
        if registry in ("docker.io", "index.docker.io"):
            url = "https://auth.docker.io/token"
            params = {
                "service": "registry.docker.io",
                "scope": f"repository:{repository}:pull",
            }
        elif registry == "ghcr.io":
            url = f"https://{registry}/token"
            params = {"service": registry, "scope": f"repository:{repository}:pull"}
        else:
            return None

        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp.json().get("token")

    def get_image_info(
        self, image: str, platform_os: str = "linux", platform_arch: str = "amd64"
    ) -> Tuple[str, int]:
        """
        Get digest and total size for an image.
        Returns (digest, size_bytes)
        """
        registry, repository, reference = self._parse_image_name(image)
        api_host = self._get_api_host(registry)
        token = self._get_token(registry, repository)

        headers = {
            "Accept": (
                "application/vnd.oci.image.index.v1+json,"
                "application/vnd.oci.image.manifest.v1+json,"
                "application/vnd.docker.distribution.manifest.v2+json,"
                "application/vnd.docker.distribution.manifest.list.v2+json"
            )
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"https://{api_host}/v2/{repository}/manifests/{reference}"
        resp = self.session.get(url, headers=headers)
        resp.raise_for_status()
        content = resp.json()

        if "manifests" in content:
            # Multi-arch image: select correct platform, then fetch manifest
            entry = next(
                m
                for m in content["manifests"]
                if m.get("platform", {}).get("os") == platform_os
                and m.get("platform", {}).get("architecture") == platform_arch
            )
            digest = entry["digest"]

            # Get specific manifest
            url = f"https://{api_host}/v2/{repository}/manifests/{digest}"
            man_headers = {"Accept": "application/vnd.oci.image.manifest.v1+json"}
            if token:
                man_headers["Authorization"] = f"Bearer {token}"

            resp = self.session.get(url, headers=man_headers)
            resp.raise_for_status()
            manifest = resp.json()

            # Calculate size
            size = sum(layer.get("size", 0) for layer in manifest.get("layers", []))
            if "config" in manifest:
                size += manifest["config"].get("size", 0)
            # Use config digest as canonical image digest
            digest = (
                manifest["config"]["digest"]
                if "config" in manifest and "digest" in manifest["config"]
                else digest
            )
        else:
            # Single-arch image
            digest = resp.headers.get("Docker-Content-Digest")
            manifest = content
            size = sum(layer.get("size", 0) for layer in manifest.get("layers", []))
            if "config" in manifest:
                size += manifest["config"].get("size", 0)
            if not digest and "config" in manifest and "digest" in manifest["config"]:
                digest = manifest["config"]["digest"]

        return digest, size

    def get_multiple_images_info(
        self, images: List[str], platform: str = "linux/amd64"
    ) -> Dict[str, Dict]:
        """Get digest and size info for multiple images."""
        results = {}
        platform_parts = platform.split("/")
        platform_os = platform_parts[0] if platform_parts else "linux"
        platform_arch = platform_parts[1] if len(platform_parts) > 1 else "amd64"

        for image in images:
            try:
                digest, size = self.get_image_info(image, platform_os, platform_arch)
                results[image] = {
                    "digest": digest,
                    "size": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                    "error": None,
                }
            except Exception as e:
                results[image] = {
                    "digest": None,
                    "size": None,
                    "size_mb": None,
                    "error": str(e),
                }

        return results
