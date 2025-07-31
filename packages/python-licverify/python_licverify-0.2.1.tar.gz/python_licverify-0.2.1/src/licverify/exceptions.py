class LicenseError(Exception):
    """Base class for license-related errors."""


class SignatureError(LicenseError):
    """Raised when license signature validation fails."""


class HardwareBindingError(LicenseError):
    """Raised when current machine does not match license hardware binding."""


class ExpiredError(LicenseError):
    """Raised when license is expired."""
