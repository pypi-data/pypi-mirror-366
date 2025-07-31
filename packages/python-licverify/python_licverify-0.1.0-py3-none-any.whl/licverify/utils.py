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
    try:
        pub.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
