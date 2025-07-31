"""python-licverify package.

Provides License loading/validation compatible with go-license verifier.
"""

from .license import License  # noqa: F401
from .verifier import Verifier  # noqa: F401
from .exceptions import LicenseError  # noqa: F401
