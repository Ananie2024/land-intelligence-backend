"""
Domain Exceptions
Land Intelligence System
"""


class DomainValidationError(Exception):
    """Raised when a business-rule or input validation fails (maps to HTTP 422)."""
    pass