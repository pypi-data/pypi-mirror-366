"""
Bundle class for creating and working with .bundle files.

This module provides a high-level interface for working with Pakto bundles
as single .bundle files, while maintaining compatibility with the existing
OCI bundle structure internally.
"""

import asyncio
import hashlib
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from urllib.parse import urlparse

import repro_tarfile as tarfile
from oras.provider import Registry
from pydantic import BaseModel

from pakto.core.models import LockFile
from pakto.core.oci_types import AnnotationKeys
from pakto.services.pack import PackService
from pakto.services.unpack import UnpackService

from .clients.oci_native import OciNativeRegistryClient
from .types import AppPath

logger = logging.getLogger(__name__)


class BundleInfo(BaseModel):
    """Information about a bundle without full extraction."""

    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    artifact_count: int = 0
    artifact_names: list[str] = []
    size_bytes: int = 0
    size_human: str = ""
    lockfile_hash: Optional[str] = None
    manifest_annotations: Optional[Dict[str, Any]] = None


class Bundle:
    """
    High-level interface for working with .bundle files.

    This class provides a wrapper around the existing PackService and UnpackService
    to create single-file .bundle archives containing OCI bundle structures.
    """

    def __init__(self, bundle_path: AppPath):
        """
        Initialize Bundle with path to .bundle file.

        Args:
            bundle_path: Path to the .bundle file
        """
        self.bundle_path = Path(bundle_path)
        self._pack_service = PackService()
        self._unpack_service = UnpackService()

    @classmethod
    def from_oci(cls, oci_dir: AppPath, bundle_path: AppPath) -> "Bundle":
        """
        Create a .bundle file from an existing OCI bundle directory.

        Args:
            oci_dir: Path to OCI bundle directory
            bundle_path: Output path for .bundle file

        Returns:
            Bundle instance for the created bundle
        """
        oci_path = Path(oci_dir)
        bundle_file_path = Path(bundle_path)

        # Validate OCI directory structure
        if not oci_path.exists():
            msg = f"OCI bundle directory not found: {oci_dir}"
            raise FileNotFoundError(msg)

        required_files = ["oci-layout", "index.json"]
        for required_file in required_files:
            if not (oci_path / required_file).exists():
                msg = f"Invalid OCI bundle: missing {required_file}"
                raise ValueError(msg)

        # Create tar archive of the OCI directory
        with tarfile.open(bundle_file_path, "w") as tar:
            # Add all files from OCI directory, preserving structure
            for item in oci_path.rglob("*"):
                if item.is_file():
                    # Calculate relative path from oci_dir
                    arcname = item.relative_to(oci_path)
                    tar.add(item, arcname=arcname)

        return cls(str(bundle_file_path))

    def extract_to_dir(self, output_dir: str) -> str:
        """
        Extract .bundle file to an OCI bundle directory.

        Args:
            output_dir: Directory to extract bundle to

        Returns:
            Path to extracted directory
        """
        logger.debug(f"Extracting bundle: {self.bundle_path}")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Extract tar archive
        with tarfile.open(self.bundle_path, "r") as tar:
            tar.extractall(output_path)

        # Verify extracted structure
        logger.debug(f"Extracted bundle to: {output_path}")
        return str(output_path)

    def extract_to_final(self, output_dir: str) -> str:
        """
        Extract .bundle file to final representation (lockfile + artifacts).

        This extracts the bundle contents to their final deployed state,
        ready for use, rather than the intermediate OCI layout.

        Args:
            output_dir: Directory to extract final artifacts to

        Returns:
            Path to extracted directory
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # First extract to temporary OCI directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_oci_path = self.extract_to_dir(temp_dir)

            # Use UnpackService to extract artifacts to final locations
            # Run the async method synchronously
            asyncio.run(
                self._unpack_service.unpack_local_bundle(
                    temp_oci_path,
                    str(output_path),
                    auto_execute_entrypoint=False,  # Don't auto-execute for manual extractions
                )
            )

        return str(output_path)

    def get_lockfile(self) -> LockFile:
        """
        Extract and parse the lockfile from the bundle.

        Returns:
            LockFile object from the bundle metadata
        """
        with tarfile.open(self.bundle_path, "r") as tar:
            # Find and read index.json to get manifest
            index_member = tar.getmember("index.json")
            index_file = tar.extractfile(index_member)
            if not index_file:
                msg = "Could not read index.json from bundle"
                raise ValueError(msg)

            index_data = json.load(index_file)

            # Get manifest digest
            if not index_data.get("manifests"):
                msg = "No manifests found in bundle index"
                raise ValueError(msg)

            manifest_ref = index_data["manifests"][0]
            manifest_digest = manifest_ref["digest"].replace("sha256:", "")

            # Read manifest
            manifest_path = f"blobs/sha256/{manifest_digest}"
            manifest_member = tar.getmember(manifest_path)
            manifest_file = tar.extractfile(manifest_member)
            if not manifest_file:
                msg = "Could not read manifest from bundle"
                raise ValueError(msg)

            manifest_data = json.load(manifest_file)

            # Find metadata layer
            metadata_layer = None
            for layer in manifest_data.get("layers", []):
                layer_annotations = layer.get("annotations", {})
                layer_type = layer_annotations.get(AnnotationKeys.LAYER_TYPE)
                if layer_type == "metadata":
                    metadata_layer = layer
                    break

            if not metadata_layer:
                msg = "No metadata layer found in bundle"
                raise ValueError(msg)

            # Extract lockfile from metadata layer
            metadata_digest = metadata_layer["digest"].replace("sha256:", "")
            metadata_blob_path = f"blobs/sha256/{metadata_digest}"
            metadata_member = tar.getmember(metadata_blob_path)
            metadata_file = tar.extractfile(metadata_member)
            if not metadata_file:
                msg = "Could not read metadata layer from bundle"
                raise ValueError(msg)

            # Extract lockfile from compressed tar
            with tarfile.open(fileobj=metadata_file, mode="r:gz") as metadata_tar:
                for member in metadata_tar.getmembers():
                    if member.name.endswith("pakto.lock.json"):
                        lockfile_file = metadata_tar.extractfile(member)
                        if lockfile_file:
                            lockfile_data = json.load(lockfile_file)
                            return LockFile(**lockfile_data)

            msg = "No lockfile found in metadata layer"
            raise ValueError(msg)

    def _get_manifest_annotations(self) -> Dict[str, Any]:
        """
        Extract manifest annotations from the bundle.

        Returns:
            Dictionary of manifest annotations
        """
        try:
            with tarfile.open(self.bundle_path, "r") as tar:
                # Find and read index.json to get manifest
                index_member = tar.getmember("index.json")
                index_file = tar.extractfile(index_member)
                if not index_file:
                    return {}

                index_data = json.load(index_file)

                # Get manifest digest
                if not index_data.get("manifests"):
                    return {}

                manifest_ref = index_data["manifests"][0]
                manifest_digest = manifest_ref["digest"].replace("sha256:", "")

                # Read manifest
                manifest_path = f"blobs/sha256/{manifest_digest}"
                manifest_member = tar.getmember(manifest_path)
                manifest_file = tar.extractfile(manifest_member)
                if not manifest_file:
                    return {}

                manifest_data = json.load(manifest_file)

                # Return manifest annotations
                return manifest_data.get("annotations", {})

        except Exception:
            return {}

    def get_info(self) -> BundleInfo:
        """
        Get bundle information without full extraction.

        Returns:
            BundleInfo object with bundle metadata
        """
        bundle_size = self.bundle_path.stat().st_size

        try:
            lockfile = self.get_lockfile()

            # Calculate lockfile hash
            lockfile_json = lockfile.dump_canonical_json()
            lockfile_hash = (
                f"sha256:{hashlib.sha256(lockfile_json.encode()).hexdigest()}"
            )

            # Extract manifest annotations
            manifest_annotations = self._get_manifest_annotations()

            return BundleInfo(
                name=lockfile.name or "unknown",
                version=lockfile.version,
                description=getattr(lockfile, "description", None),
                artifact_count=len(lockfile.artifacts),
                artifact_names=[artifact.target for artifact in lockfile.artifacts],
                size_bytes=bundle_size,
                size_human=f"{bundle_size / (1024 * 1024):.2f} MB",
                lockfile_hash=lockfile_hash,
                manifest_annotations=manifest_annotations,
            )
        except Exception:
            # Fallback to basic info if lockfile parsing fails
            return BundleInfo(
                name=self.bundle_path.stem,
                artifact_count=0,
                size_bytes=bundle_size,
                created=None,
            )

    def verify_integrity(self) -> bool:
        """
        Verify bundle integrity using SHA256 content-addressable storage.

        Returns:
            True if bundle integrity is valid, False otherwise
        """
        try:
            with tarfile.open(self.bundle_path, "r") as tar:
                # Check that all blobs have correct SHA256 names
                for member in tar.getmembers():
                    if member.name.startswith("blobs/sha256/"):
                        # Extract blob digest from path
                        blob_name = Path(member.name).name

                        # Extract and hash the content
                        blob_file = tar.extractfile(member)
                        if blob_file:
                            content = blob_file.read()
                            actual_hash = hashlib.sha256(content).hexdigest()

                            if actual_hash != blob_name:
                                return False

                # Verify basic structure
                required_members = ["oci-layout", "index.json"]
                member_names = {member.name for member in tar.getmembers()}

                return all(required in member_names for required in required_members)

        except Exception:
            return False

    def list_artifacts(self) -> list:
        """
        List artifacts in the bundle without full extraction.

        Returns:
            List of artifact information
        """
        try:
            lockfile = self.get_lockfile()
            return [
                {
                    "target": artifact.target,
                    "origin": artifact.origin,
                    "type": artifact.type,
                    "checksum": artifact.checksum,
                }
                for artifact in lockfile.artifacts
            ]
        except Exception:
            return []

    def push_to_registry(
        self,
        registry_ref: str,
        registry_username: Optional[str] = None,
        registry_password: Optional[str] = None,
        insecure: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Push bundle directly to an OCI registry.

        Args:
            registry_ref: Registry reference (e.g., "localhost:8080/repo/name:tag")
            registry_username: Optional registry username
            registry_password: Optional registry password
            insecure: Allow insecure HTTP connections
            progress_callback: Optional callback for progress updates

        Returns:
            Registry URL where bundle was pushed
        """
        # Parse registry URL
        if "://" not in registry_ref:
            registry_ref = f"oci://{registry_ref}"

        parsed = urlparse(registry_ref)
        hostname = parsed.netloc.split("/")[0]
        target = registry_ref.replace("oci://", "")

        # Extract bundle to temporary OCI directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_oci_path = self.extract_to_dir(temp_dir)

            # Debug: Check what we're about to push
            logger.debug(f"Extracted bundle to: {temp_oci_path}")
            logger.debug(f"Contents of {temp_oci_path}:")
            for root, _dirs, files in os.walk(temp_oci_path):
                level = root.replace(temp_oci_path, "").count(os.sep)
                indent = " " * 2 * level
                logger.debug(f"{indent}{os.path.basename(root)}/")
                subindent = " " * 2 * (level + 1)
                for file in files[:5]:  # Limit to first 5 files per dir
                    logger.debug(f"{subindent}{file}")

            # Create registry client
            registry_kwargs = {
                "hostname": hostname,
                "insecure": insecure,
                "auth_backend": "basic",  # Always use basic auth
                "tls_verify": not insecure,
            }

            client = Registry(**registry_kwargs)

            # Set authentication
            if registry_username and registry_password:
                client.auth.set_basic_auth(registry_username, registry_password)

            # Push bundle
            if progress_callback:
                progress_callback({
                    "type": "push_start",
                    "registry": registry_ref,
                    "message": f"Pushing bundle to {registry_ref}",
                })

            # Change to bundle directory for ORAS push
            original_cwd = os.getcwd()
            try:
                # Change to the extracted OCI bundle directory so ORAS can find the files
                os.chdir(temp_oci_path)
                logger.debug(f"Changed to directory: {os.getcwd()}")

                # Verify OCI structure
                if os.path.exists("oci-layout") and os.path.exists("index.json"):
                    logger.debug("Found OCI layout files")
                    with open("oci-layout", "r", encoding="utf-8") as f:
                        logger.debug(f"oci-layout content: {f.read()}")
                    with open("index.json", "r", encoding="utf-8") as f:
                        index_content = json.load(f)
                        logger.debug(
                            f"index.json content: {json.dumps(index_content, indent=2)}"
                        )
                else:
                    logger.warning("No OCI layout files found!")

                # # To preserve the exact directory structure of the OCI layout, we will push it
                # # as an artifact and use an annotation file to store the original file paths.

                # logger.debug(f"Pushing OCI layout as an artifact to target: {target}")
                # # 1. Find all files in the current directory (the extracted OCI layout).
                # # We use relative paths, as the process is running inside the temp dir.
                # all_files = [str(f) for f in Path(".").rglob("*") if f.is_file()]
                # logger.debug(f"Found {len(all_files)} files to package in the bundle.")

                # # 2. Create an annotation file to preserve the full relative paths.
                # # This is the key to ensuring the pull command reconstructs the directory correctly.
                # annotations_data = {"annotations": {}}
                # for file_path in all_files:
                #     # For each file, set the 'org.opencontainers.image.title' annotation
                #     # to its full relative path.
                #     annotations_data["annotations"][file_path] = {
                #         "org.opencontainers.image.title": file_path
                #     }
                # # 3. Write the annotations to a temporary file and push.
                # To preserve the exact directory structure, we will push the OCI layout
                # as an artifact. The key is to use an annotation file where each file's
                # 'title' is set to its relative path within the bundle.

                logger.debug(
                    f"Preparing to push OCI layout as an artifact to target: {target}"
                )

                # 1. Since we have chdir'd into the temp directory, we can find all files
                # with paths that are correctly relative to the bundle root.
                files_to_push = [str(p) for p in Path(".").rglob("*") if p.is_file()]
                logger.debug(
                    f"Found {len(files_to_push)} files to package in the bundle."
                )

                # 2. Create the annotation data. The keys and the 'title' values must
                # both be the relative paths we just found.
                annotation_data = {"annotations": {}}
                for path in files_to_push:
                    annotation_data["annotations"][path] = {
                        "org.opencontainers.image.title": path
                    }
                    logger.debug(f"Created annotation for {path}")
                logger.debug(f"Annotations: {annotation_data['annotations']}")
                # 3. Use a temporary file for the annotations to ensure it is handled safely.
                annotation_file_path = None
                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".json", encoding="utf-8"
                ) as temp_annot_file:
                    json.dump(annotation_data, temp_annot_file)
                    annotation_file_path = temp_annot_file.name
                logger.debug(
                    f"Created temporary annotation file at {annotation_file_path}"
                )

                # 4. Extract manifest annotations from the bundle for preservation
                # Read the original manifest to get the annotations
                with open("index.json", "r", encoding="utf-8") as f:
                    index_data = json.load(f)

                manifest_ref = index_data["manifests"][0]
                manifest_digest = manifest_ref["digest"].replace("sha256:", "")
                manifest_path = f"blobs/sha256/{manifest_digest}"

                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)

                manifest_annotations = manifest_data.get("annotations", {})
                logger.info(
                    f"Extracted {len(manifest_annotations)} manifest annotations from bundle"
                )

                # 5. Push with ORAS, attempting to preserve annotations
                # Use the standard push but with manifest annotations
                logger.info(
                    f"Pushing artifact with {len(files_to_push)} files to {target}"
                )
                result = client.push(
                    target=target,
                    files=files_to_push,
                    annotation_file=annotation_file_path,
                    manifest_annotations=manifest_annotations,
                )
                logger.debug(f"Push result: {result}")

                if progress_callback:
                    progress_callback({
                        "type": "push_complete",
                        "registry": registry_ref,
                        "message": "Bundle pushed successfully",
                    })

                # Extract manifest digest from push result
                manifest_digest = None
                if result and hasattr(result, "manifest_digest"):
                    manifest_digest = result.manifest_digest
                elif result and isinstance(result, dict):
                    manifest_digest = result.get("manifest_digest") or result.get(
                        "digest"
                    )

                return {
                    "registry_ref": registry_ref,
                    "manifest_digest": manifest_digest,
                }

            except Exception as e:
                if progress_callback:
                    progress_callback({"type": "push_error", "error": str(e)})
                raise
            finally:
                afp = Path(annotation_file_path) if annotation_file_path else None
                if afp and afp.exists():
                    afp.unlink()
                    logger.debug(
                        f"Removed temporary annotation file: {annotation_file_path}"
                    )

                # Restore original working directory
                os.chdir(original_cwd)

    async def push_to_registry_native(
        self,
        registry_ref: str,
        registry_username: Optional[str] = None,
        registry_password: Optional[str] = None,
        insecure: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> str:
        """
        Push bundle to OCI registry using native OCI client.

        This method preserves the 2-layer bundle structure and all annotations
        that the ORAS client typically corrupts.

        Args:
            registry_ref: Registry reference (e.g., "localhost:8080/repo/name:tag")
            registry_username: Optional registry username
            registry_password: Optional registry password
            insecure: Allow insecure HTTP connections (ignored - always allows for localhost)
            progress_callback: Optional callback for progress updates

        Returns:
            Registry URL where bundle was pushed
        """
        # Parse registry URL
        if "://" not in registry_ref:
            registry_ref = f"oci://{registry_ref}"

        urlparse(registry_ref)
        target = registry_ref.replace("oci://", "")

        # Parse target to separate repo from tag
        if ":" in target:
            repo_url, _tag = target.rsplit(":", 1)
        else:
            repo_url = target

        # Extract bundle to temporary OCI directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_oci_path = self.extract_to_dir(temp_dir)

            # Create OCI-Native client
            client = OciNativeRegistryClient()

            try:
                # Authenticate
                if registry_username and registry_password:
                    auth_result = await client.login(
                        registry_username, registry_password
                    )
                    if not auth_result.success:
                        msg = f"Authentication failed: {auth_result.error_message}"
                        raise RuntimeError(msg)

                if progress_callback:
                    progress_callback({
                        "type": "push_start",
                        "registry": registry_ref,
                        "message": f"Pushing bundle to {registry_ref} using OCI-Native client",
                    })

                # Read bundle structure
                with open(
                    os.path.join(temp_oci_path, "index.json"), "r", encoding="utf-8"
                ) as f:
                    index_data = json.load(f)

                manifest_ref = index_data["manifests"][0]
                manifest_digest = manifest_ref["digest"].replace("sha256:", "")
                manifest_path = os.path.join(
                    temp_oci_path, f"blobs/sha256/{manifest_digest}"
                )

                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)

                logger.info(
                    f"Bundle manifest has {len(manifest_data.get('layers', []))} layers"
                )
                logger.info(
                    f"Bundle annotations: {list(manifest_data.get('annotations', {}).keys())}"
                )

                # Upload all blobs first
                blobs_dir = os.path.join(temp_oci_path, "blobs/sha256")
                uploaded_blobs = {}

                blob_files = [
                    f
                    for f in os.listdir(blobs_dir)
                    if os.path.isfile(os.path.join(blobs_dir, f))
                ]
                logger.info(f"Uploading {len(blob_files)} blobs to registry")

                for i, blob_file in enumerate(blob_files):
                    blob_path = os.path.join(blobs_dir, blob_file)
                    blob_data = Path(blob_path).read_bytes()

                    if progress_callback:
                        progress_callback({
                            "type": "upload_progress",
                            "message": f"Uploading blob {i + 1}/{len(blob_files)}: {blob_file[:12]}...",
                            "current": i + 1,
                            "total": len(blob_files),
                        })

                    # Use repo_url without tag for blob upload
                    upload_result = await client._upload_blob(repo_url, blob_data)

                    if not upload_result.success:
                        msg = f"Failed to upload blob {blob_file}: {upload_result.error_message}"
                        raise RuntimeError(msg)

                    uploaded_blobs[f"sha256:{blob_file}"] = upload_result.digest
                    logger.debug(f"Uploaded blob {blob_file} -> {upload_result.digest}")

                # Push manifest with preserved structure
                push_result = await client.push(f"{target}", manifest_data)

                if not push_result.success:
                    msg = f"Failed to push manifest: {push_result.error_message}"
                    raise RuntimeError(msg)

                if progress_callback:
                    progress_callback({
                        "type": "push_complete",
                        "registry": registry_ref,
                        "message": "Bundle pushed successfully with preserved structure",
                    })

                logger.info(f"Successfully pushed bundle to {registry_ref}")
                logger.info(
                    f"Bundle structure preserved: {len(manifest_data.get('layers', []))} layers"
                )
                logger.info(
                    f"Bundle annotations preserved: {len(manifest_data.get('annotations', {}))}"
                )

                return {
                    "registry_ref": registry_ref,
                    "manifest_digest": push_result.digest,
                }

            except Exception as e:
                if progress_callback:
                    progress_callback({"type": "push_error", "error": str(e)})
                raise
            finally:
                # Cleanup client
                await client.logout()
