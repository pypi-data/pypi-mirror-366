"""Platform-independent hardware information collection.

Only what is needed for license verification (MAC, disk UUID/serial, hostname).
"""
from __future__ import annotations

import platform
import socket
import subprocess
from pathlib import Path
from typing import List

import psutil

__all__ = [
    "HardwareInfo",
    "get_hardware_info",
]


class HardwareInfo:
    """Subset of machine identifiers used in license binding."""

    def __init__(
        self,
        mac_addresses: List[str],
        disk_ids: List[str],
        hostname: str,
    ) -> None:
        self.mac_addresses = mac_addresses
        self.disk_ids = disk_ids
        self.hostname = hostname

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "HardwareInfo(mac_addresses=%s, disk_ids=%s, hostname=%s)"
            % (self.mac_addresses, self.disk_ids, self.hostname)
        )


# --- helpers --------------------------------------------------------------

def _get_mac_addresses() -> List[str]:
    addrs = []
    for iface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == psutil.AF_LINK and snic.address and iface != "lo":
                addrs.append(snic.address)
    return addrs


def _get_disk_ids() -> List[str]:
    system = platform.system().lower()
    if system == "linux":
        return _linux_disk_ids()
    if system == "windows":
        return _windows_disk_ids()
    if system == "darwin":
        return _macos_disk_ids()
    return []


def _linux_disk_ids() -> List[str]:
    # Try lsblk SERIAL first
    try:
        output = subprocess.check_output(["lsblk", "-ndo", "SERIAL", "-d"], text=True)
        return [line.strip() for line in output.splitlines() if line.strip()]
    except Exception:
        # Fallback /dev/disk/by-id
        path = Path("/dev/disk/by-id")
        if path.exists():
            return sorted(p.name for p in path.iterdir())
    return []


def _windows_disk_ids() -> List[str]:
    try:
        output = subprocess.check_output(
            ["wmic", "diskdrive", "get", "SerialNumber"], text=True
        )
        return [line.strip() for line in output.splitlines()[1:] if line.strip()]
    except Exception:
        return []


def _macos_disk_ids() -> List[str]:
    try:
        output = subprocess.check_output(["diskutil", "info", "/dev/disk0"], text=True)
        ids: List[str] = []
        for line in output.splitlines():
            if "Serial Number" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    ids.append(parts[1].strip())
        return ids
    except Exception:
        return []


def get_hardware_info() -> HardwareInfo:
    """Collect minimal hardware identifiers."""

    macs = _get_mac_addresses()
    disks = _get_disk_ids()
    hostname = socket.gethostname()

    return HardwareInfo(mac_addresses=macs, disk_ids=disks, hostname=hostname)
