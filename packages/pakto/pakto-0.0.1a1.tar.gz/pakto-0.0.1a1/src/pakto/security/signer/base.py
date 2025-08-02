"""
Abstract interfaces for signing and verifying Pakto bundles.

Concrete implementations live in
`pakto.security.signer.key_based`  and  `pakto.security.signer.keyless`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from pakto.core.types import AppPath

SIG_SUBDIR = (
    ".pakto/sig"  # Directory where signatures are stored relative to the bundle root.
)

# ----------------------------- #
# Shared models                 #
# ----------------------------- #


class SignatureMetadata(BaseModel):
    """
    Information returned after successfully signing a bundle.

    * `signature_path`  - path **inside the bundle directory** where the DSSE
      envelope was written.
    * `algorithm`       - name of the crypto algorithm (e.g. 'ed25519').
    * `key_id`          - fingerprint or certificate subject that will later
      be required for verification.
    """

    signature_path: str
    algorithm: str
    key_id: Optional[str] = Field(
        default=None, description="Fingerprint or certificate subject"
    )


class VerificationResult(BaseModel):
    """
    Outcome of a verification attempt.

    A verifier **must** set `success=False` and an explanatory `message`
    instead of raising, so callers can decide how to surface errors.
    """

    success: bool
    message: str
    key_id: Optional[str] = None


# ----------------------------- #
# Abstract Base Class           #
# ----------------------------- #


class BaseSigner(ABC):
    """
    Strategy interface for bundle signing and verification.

    Concrete subclasses **must**

    1. create or load a signing key/certificate,
    2. compute the bundle digest (if not already provided),
    3. write a DSSE envelope to disk, and
    4. return a populated `SignatureMetadata`.
    """

    # -------- signing ------- #

    @abstractmethod
    def sign(
        self,
        bundle_path: AppPath,
        *,
        key_password: Optional[str] = None,
        **kwargs,
    ) -> SignatureMetadata:
        """
        Sign a bundle file or directory.

        Parameters
        ----------
        bundle_path:
            Path to the `.bundle` file or exploded bundle directory.
        key_password:
            If the private key is encrypted, the caller can supply the
            pass-phrase here (UTF-8).  Implementations **may** prompt if None.
        **kwargs:
            Extensible keyword arguments for future flags.

        Returns
        -------
        SignatureMetadata
            Location of the signature and key/cert fingerprint.
        """
        raise NotImplementedError

    # -------- verification ------- #

    @abstractmethod
    def verify(
        self,
        bundle_path: AppPath,
        *,
        trusted_keys_dir: Optional[Path] = None,
        **kwargs,
    ) -> VerificationResult:
        """
        Verify the signature attached to `bundle_path`.

        Implementations should:
        1. locate the DSSE envelope,
        2. load public key / certificate,
        3. recompute digest and compare,
        4. return a populated `VerificationResult`.

        Parameters
        ----------
        trusted_keys_dir:
            Directory containing PEM-encoded public keys that are considered
            trusted for *offline* verification.  Ignored by key-less signers
            that rely solely on certificate transparency (Fulcio + Rekor).
        """
        raise NotImplementedError
