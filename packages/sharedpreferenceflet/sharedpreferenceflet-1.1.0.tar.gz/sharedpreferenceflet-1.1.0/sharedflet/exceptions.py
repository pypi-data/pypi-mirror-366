class SharedPrefsError(Exception):
    """Base class for shared preference errors."""

class InvalidTypeError(SharedPrefsError):
    """Raised when the type of value is not as expected."""

class KeyNotFoundError(SharedPrefsError):
    """Raised when a key is not found in preferences."""

class DecryptionError(SharedPrefsError):
    """Raised when file decryption fails due to wrong password or corruption."""
