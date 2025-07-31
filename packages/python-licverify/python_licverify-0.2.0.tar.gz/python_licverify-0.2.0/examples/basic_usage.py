"""Example of using python-licverify to validate a license file.

Run with:
   python examples/basic_usage.py
Make sure `license.lic` and a valid public key are available.
"""
from pathlib import Path

from licverify import Verifier

# TODO: replace with real PEM string or read from env var
PUBLIC_KEY_PEM = (
    """
-----BEGIN PUBLIC KEY-----
PLACEYOURPUBLICKEYHERE
-----END PUBLIC KEY-----
"""
)


def main() -> None:
    verifier = Verifier(PUBLIC_KEY_PEM)
    lic_path = Path("license.lic")
    if not lic_path.exists():
        print("license.lic not found, skipping demo")
        return
    lic = verifier.load_license(lic_path)
    try:
        lic.verify(verifier)
    except Exception as exc:  # noqa: BLE001
        print(f"License invalid: {exc}")
    else:
        print("License is valid!")


if __name__ == "__main__":
    main()
