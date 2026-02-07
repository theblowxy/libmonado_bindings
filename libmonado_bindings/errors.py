"""
Exception classes for libmonado Python bindings.
"""


class MonadoError(Exception):
    """Base exception for all Monado-related errors."""
    pass


class MonadoConnectionError(MonadoError):
    """Raised when connection to Monado fails."""
    pass


class MonadoVersionError(MonadoError):
    """Raised when API version is incompatible."""
    pass


class MonadoInvalidValueError(MonadoError):
    """Raised when an invalid value is provided."""
    pass


class MonadoUnsupportedOperationError(MonadoError):
    """Raised when an unsupported operation is attempted."""
    pass
