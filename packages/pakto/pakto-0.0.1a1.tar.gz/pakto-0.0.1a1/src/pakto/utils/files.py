import asyncio
import hashlib
import logging
import os
from pathlib import Path
from typing import Union

from pakto.core.types import AppPath

logger = logging.getLogger(__name__)


def set_file_mode(path: AppPath, mode: Union[str, int], follow_symlinks: bool = True):
    path = Path(path)
    if not path.exists():
        error_msg = f"File {path} does not exist"
        logger.error(
            error_msg,
            extra={"path": path, "mode": mode, "follow_symlinks": follow_symlinks},
        )
        return
    try:
        if isinstance(mode, str):
            mode = int(mode, 8)
        os.chmod(path, mode, follow_symlinks=follow_symlinks)
    except OSError as e:
        error_msg = f"Failed to set file mode for {path}"
        logger.exception(
            error_msg,
            extra={
                "path": path,
                "mode": mode,
                "follow_symlinks": follow_symlinks,
                "error": e,
            },
        )
        raise e


def file_checksum(file_path: Path, algo: str = "sha256") -> str:
    """Calculate file checksum.

    Args:
        file_path: The path to the file to calculate the checksum of.
        algo: The algorithm to use for the checksum. Defaults to "sha256". Supported algorithms: sha256, sha512, md5, sha1, sha3_256, sha3_512, blake2b, blake2s.
    """
    algo = algo.lower().strip()
    if algo not in hashlib.algorithms_available:
        error_msg = f"Invalid algorithm: {algo}"
        logger.error(error_msg, extra={"algo": algo})
        raise ValueError(error_msg)
    hash_func = getattr(hashlib, algo)
    hash_obj = hash_func()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return f"{algo}:{hash_obj.hexdigest()}"


async def async_file_checksum(file_path: Path, algo: str = "sha256") -> str:
    """Calculate file checksum asynchronously.

    Args:
        file_path: The path to the file to calculate the checksum of.
        algo: The algorithm to use for the checksum. Defaults to "sha256". Supported algorithms: sha256, sha512, md5, sha1, sha3_256, sha3_512, blake2b, blake2s.

    Returns:
        The checksum of the file.
    """
    return await asyncio.to_thread(file_checksum, file_path, algo)
