"""Public interface for Pakto's signing subsystem.

At the top level we export:

* ``SigningService`` - façade that callers (CLI or higher-level services)
  instantiate.  It selects an appropriate concrete signer implementation
  based on the supplied parameters or sensible defaults.

* Concrete signer classes (only ``KeyBasedSigner`` for now).  Additional
  strategies - e.g. ``KeylessSigner`` - can be added later without
  changing the public imports.

* Typed return models ``SignatureMetadata`` and ``VerificationResult`` so
  downstream code can rely on a stable schema regardless of which signer
  produced the signature.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .base import AppPath, SignatureMetadata, VerificationResult  # re-export
from .key_based import KeyBasedSigner

# from .keyless import KeylessSigner  # ── to be implemented later

__all__ = [
    "KeyBasedSigner",
    # "KeylessSigner",   # when implemented
    "SignatureMetadata",
    "SigningService",
    "VerificationResult",
]


class SigningService:
    """Facade that hides concrete signer selection.

    Usage examples
    --------------
    ```python
    svc = SigningService()
    meta = svc.sign_key_based("dist/app.bundle", key_fp="deadbeef1234")

    verify = svc.verify_key_based("dist/app.bundle", trusted_keys_dir="~/.keys")
    ```
    """

    # ------------------------------------------------------------------
    # Key-based API (available today)
    # ------------------------------------------------------------------

    @staticmethod
    def create_key_based_signer(key_path: AppPath) -> KeyBasedSigner:
        """Return a *stateful* :class:`KeyBasedSigner` bound to *key_path*."""

        return KeyBasedSigner(Path(key_path))

    # Convenience wrappers (thin pass-through so CLI needn't touch KeyBasedSigner)

    def sign_key_based(
        self,
        bundle: AppPath,
        *,
        key_path: AppPath,
        passphrase: Optional[str] = None,
    ) -> SignatureMetadata:
        signer = self.create_key_based_signer(key_path)
        return signer.sign(bundle, key_password=passphrase)

    def verify_key_based(
        self,
        bundle: AppPath,
        *,
        trusted_keys_dir: AppPath | None = None,
    ) -> VerificationResult:
        signer = self.create_key_based_signer(key_path="dummy")  # signer needs no key
        return signer.verify(
            bundle,
            trusted_keys_dir=Path(trusted_keys_dir) if trusted_keys_dir else None,
        )

    # ------------------------------------------------------------------
    # Future keyless hooks
    # ------------------------------------------------------------------

    # def create_keyless_signer(self, oidc_token: str | None = None) -> KeylessSigner:
    #     """Return key-less signer once implemented (Fulcio / Rekor)."""
    #     ...
