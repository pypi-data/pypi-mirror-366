"""
Key-store service (generate / import / list / export)
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
from pydantic import BaseModel

from .utils import fingerprint_key, load_private_key


class KeyMeta(BaseModel):
    fingerprint: str
    algo: str = "ed25519"
    created: str
    file_path: Optional[str] = None
    encrypted: bool = True


class KeyStore:
    """Service for managing cryptographic keys."""

    def __init__(self, store_dir: Optional[Path] = None):
        """Initialize key store with optional directory."""
        self.store_dir = Path(store_dir) if store_dir else Path.cwd()
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        algo: str = "ed25519",
        passphrase: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> KeyMeta:
        """Generate a new key pair and store it encrypted."""
        # Generate key based on algorithm
        if algo == "ed25519":
            private_key = ed25519.Ed25519PrivateKey.generate()
        elif algo == "rsa":
            private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        else:
            msg = f"Unsupported algorithm: {algo}"
            raise ValueError(msg)

        # Get key fingerprint
        key_fingerprint = fingerprint_key(private_key.public_key())

        # Determine output filename
        if not output_path:
            output_path = str(self.store_dir / f"pakto-{algo}-{key_fingerprint}.pem")

        # Serialize private key with encryption
        if passphrase:
            encryption_algorithm = serialization.BestAvailableEncryption(
                passphrase.encode()
            )
        else:
            encryption_algorithm = serialization.NoEncryption()

        encrypted_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )

        # Write private key
        Path(output_path).write_bytes(encrypted_pem)

        # Generate corresponding public key file
        public_key_path = f"{output_path}.pub"
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        Path(public_key_path).write_bytes(public_pem)

        # Create metadata
        return KeyMeta(
            fingerprint=key_fingerprint,
            algo=algo,
            created=datetime.now(timezone.utc).isoformat(),
            file_path=output_path,
            encrypted=bool(passphrase),
        )

    def list_keys(self, directory: Optional[Path] = None) -> List[KeyMeta]:
        """List keys in directory."""
        search_dir = directory or self.store_dir
        if not search_dir.exists():
            return []

        keys_found = []

        # Find PEM files
        for pem_file in search_dir.glob("*.pem"):
            if pem_file.name.endswith(".pub"):
                continue  # Skip public key files

            try:
                # Try to load without password first (will fail for encrypted keys)
                try:
                    private_key = load_private_key(pem_file, None)
                    key_fingerprint = fingerprint_key(private_key.public_key())
                    encrypted = False
                except Exception:
                    # Key is probably encrypted, extract info from filename if possible
                    key_fingerprint = "encrypted"
                    encrypted = True

                # Determine algorithm from key content or filename
                algo = "unknown"
                if "ed25519" in pem_file.name.lower():
                    algo = "ed25519"
                elif "rsa" in pem_file.name.lower():
                    algo = "rsa"
                elif "ecdsa" in pem_file.name.lower():
                    algo = "ecdsa"

                # Get file creation time
                created_time = datetime.fromtimestamp(
                    pem_file.stat().st_ctime, tz=timezone.utc
                )

                keys_found.append(
                    KeyMeta(
                        fingerprint=key_fingerprint,
                        algo=algo,
                        created=created_time.isoformat(),
                        file_path=str(pem_file),
                        encrypted=encrypted,
                    )
                )

            except Exception:
                continue  # Skip files that can't be parsed

        return keys_found

    def export_public_key(
        self, key_file: Path, passphrase: Optional[str] = None
    ) -> bytes:
        """Export public key from private key file."""
        # Load private key (may require passphrase)
        try:
            private_key = load_private_key(key_file, passphrase)
        except Exception as e:
            msg = f"Failed to load private key: {e}"
            raise ValueError(msg)

        # Export public key
        public_key = private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
