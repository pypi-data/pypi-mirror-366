"""License model and loading helpers."""
from __future__ import annotations

import json
import struct
import time as _time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .exceptions import ExpiredError, HardwareBindingError, SignatureError
from .hardware import get_hardware_info
from .utils import rsa_verify_sha256

# RSA-2048 signature size in bytes
_SIGNATURE_SIZE = 256


@dataclass
class HardwareBinding:
    mac_addresses: List[str] = field(default_factory=list)
    disk_ids: List[str] = field(default_factory=list)
    host_names: List[str] = field(default_factory=list)
    custom_ids: List[str] = field(default_factory=list)


@dataclass
class License:
    # Core
    id: str
    customer_id: str
    product_id: str
    serial_number: str
    issue_date: datetime
    expiry_date: datetime
    features: List[str]

    # Hardware binding
    hardware_ids: HardwareBinding

    # internal raw signature
    _signature: bytes = field(repr=False)

    @classmethod
    def load(cls, path: str | Path) -> "License":
        """Load license file and split signature.

        Currently supports legacy JSON format (same as go impl fallback).
        Binary format TODO.
        """
        data = Path(path).read_bytes()
        if len(data) <= _SIGNATURE_SIZE:
            raise ValueError("License file too small")

        payload, signature = data[:-_SIGNATURE_SIZE], data[-_SIGNATURE_SIZE:]

        # Try JSON decode
        try:
            obj = json.loads(payload)
        except Exception as exc:
            raise ValueError("Unable to parse license JSON payload") from exc

        # Parse datetime ISO 8601
        def _parse(ts: str) -> datetime:
            return datetime.fromisoformat(ts.rstrip("Z")).replace(tzinfo=timezone.utc)

        hb = obj.get("hardware_ids", {})
        license_obj = cls(
            id=obj["id"],
            customer_id=obj["customer_id"],
            product_id=obj["product_id"],
            serial_number=obj.get("serial_number", ""),
            issue_date=_parse(obj["issue_date"]),
            expiry_date=_parse(obj["expiry_date"]),
            features=obj.get("features", []),
            hardware_ids=HardwareBinding(
                mac_addresses=hb.get("mac_addresses", []),
                disk_ids=hb.get("disk_ids", []),
                host_names=hb.get("host_names", []),
                custom_ids=hb.get("custom_ids", []),
            ),
            _signature=signature,
        )
        return license_obj

    # ------------------------------------------------------------------
    def verify(self, verifier: "Verifier") -> None:
        """Perform all verification steps.

        Raises an exception on failure. Returns None if OK.
        """
        # signature
        if not verifier.verify_signature(self):
            raise SignatureError("Invalid license signature")

        # hardware binding
        verifier.verify_hardware_binding(self)

        # expiry
        verifier.verify_expiry(self)

    # ------------------------------------------------------------------
    def to_payload_bytes(self) -> bytes:
        """Return payload used for signature verification (legacy JSON)."""
        payload_dict = {
            "id": self.id,
            "customer_id": self.customer_id,
            "product_id": self.product_id,
            "serial_number": self.serial_number,
            "issue_date": self.issue_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
            "features": self.features,
            "hardware_ids": {
                "mac_addresses": self.hardware_ids.mac_addresses,
                "disk_ids": self.hardware_ids.disk_ids,
                "host_names": self.hardware_ids.host_names,
                "custom_ids": self.hardware_ids.custom_ids,
            },
        }
        return json.dumps(payload_dict, separators=(",", ":"), sort_keys=True).encode()
