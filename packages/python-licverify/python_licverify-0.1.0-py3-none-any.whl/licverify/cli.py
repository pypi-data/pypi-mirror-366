"""Command-line interface for python-licverify.

Usage:
    licverify --public-key path/to/pub.pem --license path/to/license.lic
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .exceptions import LicenseError
from .verifier import Verifier


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="licverify", description="Verify go-license license file")
    parser.add_argument("--public-key", required=True, help="Path to RSA public key in PEM format")
    parser.add_argument("--license", dest="license_path", required=True, help="Path to license file (.lic)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = parse_args(argv)
    pub_pem = Path(args.public_key).read_text()
    verifier = Verifier(pub_pem)

    lic = verifier.load_license(args.license_path)
    try:
        lic.verify(verifier)
    except LicenseError as exc:
        print(f"License invalid: {exc}")
        sys.exit(1)
    else:
        print("License is valid!")
        sys.exit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
