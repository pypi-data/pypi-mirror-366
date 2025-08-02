"""Shared cryptographic helpers for the Pakto security layer.

These utilities are **stateless** and pure-Python so they can be reused by
multiple signer implementations, KeyStore helpers, and unit tests without
import cycles or extra dependencies.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import (
    ec,
    ed25519,
    padding,
    rsa,
)
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
)

from pakto.core.types import AppPath

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Generic helpers
# --------------------------------------------------------------------------- #


def sha256_hex(path: AppPath, *, chunk_size: int = 1 << 20) -> str:
    """Return the SHA-256 hex digest of *path* using a streaming reader."""
    h = hashlib.sha256()
    with Path(path).expanduser().open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def b64enc(data: bytes) -> str:
    """Return a base64-encoded string of *data*."""
    return base64.b64encode(data).decode()


def b64dec(data: str) -> bytes:
    """Return the base64-decoded bytes of *data*."""
    return base64.b64decode(data)


# --------------------------------------------------------------------------- #
# Key loading & fingerprinting
# --------------------------------------------------------------------------- #


def load_private_key(key_path: AppPath, password: Optional[str]) -> PrivateKeyTypes:
    raw = Path(key_path).expanduser().read_bytes()
    return load_pem_private_key(raw, password=password.encode() if password else None)


def load_public_key(pem_path: AppPath):
    return load_pem_public_key(Path(pem_path).expanduser().read_bytes())


def fingerprint_key(pub_key, *, length: int = 16) -> str:
    """Return the *length*-byte hex fingerprint of a public key."""
    der = pub_key.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    digest = hashlib.sha256(der).digest()
    return digest[:length].hex()


# --------------------------------------------------------------------------- #
# Signing / verification primitives
# --------------------------------------------------------------------------- #


def sign_bytes(priv_key, data: bytes) -> tuple[bytes, str]:
    """Sign *data* with *priv_key* and return (signature, algorithm)."""
    if isinstance(priv_key, ed25519.Ed25519PrivateKey):
        return priv_key.sign(data), "ed25519"

    if isinstance(priv_key, rsa.RSAPrivateKey):
        return (
            priv_key.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            ),
            "rsa-pss",
        )

    if isinstance(priv_key, ec.EllipticCurvePrivateKey):
        return priv_key.sign(data, ec.ECDSA(hashes.SHA256())), "ecdsa"

    msg = "unsupported key type for signing"
    raise TypeError(msg)


def verify_bytes(pub_key, signature: bytes, data: bytes) -> None:
    """Raise if *signature* is invalid for *data* and *pub_key*."""
    if isinstance(pub_key, ed25519.Ed25519PublicKey):
        pub_key.verify(signature, data)
        return

    if isinstance(pub_key, rsa.RSAPublicKey):
        pub_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return

    if isinstance(pub_key, ec.EllipticCurvePublicKey):
        pub_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        return

    msg = "unsupported key type for verification"
    raise TypeError(msg)


def find_public_key(key_id: str, trusted_dir: Optional[Path]):
    """Return public-key object whose fingerprint matches *key_id* or None."""
    if not trusted_dir:
        return None
    for pem in trusted_dir.glob("*.pem"):
        try:
            pub = load_public_key(pem)
            if fingerprint_key(pub) == key_id:
                return pub
        except Exception as exc:
            # src/pakto/security/utils.py:141:9: S112 `try`-`except`-`continue` detected, consider logging the exception
            logger.warning(f"Failed to load public key from {pem}: {exc}")
            continue
    return None
