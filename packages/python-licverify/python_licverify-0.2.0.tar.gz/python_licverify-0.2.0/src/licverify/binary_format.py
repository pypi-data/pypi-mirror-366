"""Decode go-license binary license payload (v1).
Follows logic from pkg/licformat/binary.go in go-license repo.
Only implements *decoding*; encoding is not required for verification.
"""
from __future__ import annotations

import struct
from datetime import datetime, timezone
from typing import List, Tuple

from .license import HardwareBinding

_CURRENT_VERSION = 1


class _Buf:
    def __init__(self, data: bytes):
        self._data = memoryview(data)
        self._pos = 0

    def read(self, n: int) -> bytes:
        if self._pos + n > len(self._data):
            raise ValueError("unexpected EOF while decoding license")
        b = self._data[self._pos : self._pos + n].tobytes()
        self._pos += n
        return b

    def read_uint16(self) -> int:
        return struct.unpack_from("<H", self.read(2))[0]

    def read_int64(self) -> int:
        return struct.unpack_from("<q", self.read(8))[0]

    def read_string(self) -> str:
        length = self.read_uint16()
        return self.read(length).decode()

    def read_string_slice(self) -> List[str]:
        count = self.read_uint16()
        return [self.read_string() for _ in range(count)]


HEADER_STRUCT = struct.Struct("<BI")  # Version uint8 + Length uint32


def encode_license_payload(license_obj) -> bytes:
    """Return binary payload (no signature) matching Go licformat.EncodeLicense."""
    from .license import License  # local import to avoid cycle
    if not isinstance(license_obj, License):
        raise TypeError("expect License instance")

    parts: list[bytes] = []
    def _w_string(s: str):
        data = s.encode()
        parts.append(struct.pack("<H", len(data)))
        parts.append(data)

    def _w_slice(lst):
        parts.append(struct.pack("<H", len(lst)))
        for s in lst:
            _w_string(s)

    _w_string(license_obj.id)
    _w_string(license_obj.customer_id)
    _w_string(license_obj.product_id)
    _w_string(license_obj.serial_number)

    parts.append(struct.pack("<q", int(license_obj.issue_date.timestamp())))
    parts.append(struct.pack("<q", int(license_obj.expiry_date.timestamp())))

    _w_slice(license_obj.features)
    _w_slice(license_obj.hardware_ids.mac_addresses)
    _w_slice(license_obj.hardware_ids.disk_ids)
    _w_slice(license_obj.hardware_ids.host_names)
    _w_slice(license_obj.hardware_ids.custom_ids)

    body = b"".join(parts)
    header = HEADER_STRUCT.pack(_CURRENT_VERSION, len(body))
    return header + body


def decode_license_payload(payload: bytes):
    if len(payload) < HEADER_STRUCT.size:
        raise ValueError("payload too small for binary license")

    version, length = HEADER_STRUCT.unpack_from(payload)
    if version != _CURRENT_VERSION:
        raise ValueError("unsupported binary license version")

    # Not strictly necessary to use length; buffer checks will handle.
    buf = _Buf(payload[HEADER_STRUCT.size : HEADER_STRUCT.size + length])

    # Parse fields
    lid = buf.read_string()
    customer_id = buf.read_string()
    product_id = buf.read_string()
    serial = buf.read_string()

    issue_ts = buf.read_int64()
    expiry_ts = buf.read_int64()

    features = buf.read_string_slice()

    macs = buf.read_string_slice()
    disks = buf.read_string_slice()
    hosts = buf.read_string_slice()
    customs = buf.read_string_slice()

    from .license import License  # lazy import to avoid cycle

    license_obj = License(
        id=lid,
        customer_id=customer_id,
        product_id=product_id,
        serial_number=serial,
        issue_date=datetime.fromtimestamp(issue_ts, tz=timezone.utc),
        expiry_date=datetime.fromtimestamp(expiry_ts, tz=timezone.utc),
        features=features,
        hardware_ids=HardwareBinding(
            mac_addresses=macs,
            disk_ids=disks,
            host_names=hosts,
            custom_ids=customs,
        ),
        _signature=b"",  # placeholder, will be set by caller
    )
    return license_obj
