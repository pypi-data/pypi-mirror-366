"""Verifier implementation mirroring go-license behaviour."""
from __future__ import annotations

from datetime import datetime, timezone

from .exceptions import ExpiredError, HardwareBindingError
from .hardware import get_hardware_info
from .license import License
from .utils import load_public_key, rsa_verify_sha256

__all__ = ["Verifier"]


class Verifier:
    def __init__(self, public_key_pem: str):
        if not public_key_pem:
            raise ValueError("public key cannot be empty")
        self._pub = load_public_key(public_key_pem)

    # ------------------------------------------------------------------
    def load_license(self, path: str) -> License:
        return License.load(path)

    # ------------------------------------------------------------------
    def verify_signature(self, license: License) -> bool:  # noqa: A002
        # For now only support legacy JSON, replicate go fallback order
        payload = license.to_payload_bytes()
        return rsa_verify_sha256(self._pub, payload, license._signature)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    def verify_hardware_binding(self, license: License) -> None:  # noqa: A002
        hw = get_hardware_info()
        ids = license.hardware_ids

        if ids.mac_addresses and not _contains_any(hw.mac_addresses, ids.mac_addresses):
            raise HardwareBindingError("MAC address mismatch")
        if ids.disk_ids and not _contains_any(hw.disk_ids, ids.disk_ids):
            raise HardwareBindingError("Disk ID mismatch")
        if ids.host_names and hw.hostname not in ids.host_names:
            raise HardwareBindingError("Hostname mismatch")

    # ------------------------------------------------------------------
    @staticmethod
    def verify_expiry(license: License) -> None:  # noqa: A002
        now = datetime.now(tz=timezone.utc)
        if now > license.expiry_date:
            raise ExpiredError(f"License expired on {license.expiry_date.isoformat()}")


# helpers -----------------------------------------------------------------

def _contains_any(list1: list[str], list2: list[str]) -> bool:
    return any(item in list2 for item in list1)
