from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

__all__ = [
    "load_public_key",
    "rsa_verify_sha256",
]


def load_public_key(pem: str) -> rsa.RSAPublicKey:
    return serialization.load_pem_public_key(pem.encode())


def rsa_verify_sha256(pub: rsa.RSAPublicKey, data: bytes, signature: bytes) -> bool:
    from cryptography.hazmat.primitives import hashes as _hashes
    from cryptography.hazmat.primitives import constant_time
    from cryptography.hazmat.primitives.asymmetric import utils as asym_utils

    digest = _hashes.Hash(_hashes.SHA256())
    digest.update(data)
    hashed = digest.finalize()
    try:
        pub.verify(
            signature,
            hashed,
            padding.PKCS1v15(),
            asym_utils.Prehashed(_hashes.SHA256()),
        )
        return True
    except InvalidSignature:
        # constant time compare path fallback? no
        return False
