"""Key-based signing strategy (Ed25519 / RSA / ECDSA)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pakto.security.utils import (
    AppPath,
    b64dec,
    b64enc,
    find_public_key,
    fingerprint_key,
    load_private_key,
    sha256_hex,
    sign_bytes,
    verify_bytes,
)

from .base import SIG_SUBDIR, BaseSigner, SignatureMetadata, VerificationResult


class KeyBasedSigner(BaseSigner):
    """Offline signer that uses a local private-key PEM."""

    def __init__(self, key_path: AppPath) -> None:
        self.key_path = Path(key_path).expanduser()

    # --------------------------- signing --------------------------------- #

    def sign(
        self,
        bundle_path: AppPath,
        *,
        key_password: Optional[str] = None,
        **kwargs,  # noqa: ARG002
    ) -> SignatureMetadata:
        bundle = Path(bundle_path)
        digest_hex = sha256_hex(bundle)
        digest_bytes = bytes.fromhex(digest_hex)

        priv_key = load_private_key(self.key_path, key_password)
        signature, alg = sign_bytes(priv_key, digest_bytes)
        key_id = fingerprint_key(priv_key.public_key())

        envelope = {
            "payloadType": "application/vnd.cnr.bundle.digest",
            "payload": b64enc(digest_bytes),
            "signatures": [{"keyid": key_id, "sig": b64enc(signature)}],
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }

        sig_dir = bundle.parent / SIG_SUBDIR
        sig_dir.mkdir(parents=True, exist_ok=True)
        sig_path = sig_dir / f"{digest_hex}.dsse.json"
        sig_path.write_text(json.dumps(envelope, indent=2))

        return SignatureMetadata(
            signature_path=str(sig_path.relative_to(bundle.parent)),
            algorithm=alg,
            key_id=key_id,
        )

    # --------------------------- verification ---------------------------- #

    def verify(
        self,
        bundle_path: AppPath,
        *,
        trusted_keys_dir: Optional[Path] = None,
        **kwargs,  # noqa: ARG002
    ) -> VerificationResult:
        bundle = Path(bundle_path)
        digest_hex = sha256_hex(bundle)
        sig_path = bundle.parent / SIG_SUBDIR / f"{digest_hex}.dsse.json"

        if not sig_path.is_file():
            return VerificationResult(success=False, message="signature file missing")

        try:
            data = json.loads(sig_path.read_text())
            sig_entry = data["signatures"][0]
            signature = b64dec(sig_entry["sig"])
            key_id = sig_entry["keyid"]
        except Exception as exc:
            return VerificationResult(success=False, message=f"corrupt sig file: {exc}")

        pub = find_public_key(key_id, trusted_keys_dir)
        if pub is None:
            return VerificationResult(
                success=False, message="untrusted key", key_id=key_id
            )

        try:
            verify_bytes(pub, signature, bytes.fromhex(digest_hex))
            return VerificationResult(success=True, message="OK", key_id=key_id)
        except Exception as exc:
            return VerificationResult(
                success=False, message=f"bad signature: {exc}", key_id=key_id
            )
