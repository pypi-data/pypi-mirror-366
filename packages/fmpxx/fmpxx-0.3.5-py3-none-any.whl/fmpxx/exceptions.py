"""Custom exceptions for the FMP API client."""

class FMPAPIError(Exception):
    """Base exception for FMP API errors."""
    pass

class InvalidAPIKeyError(FMPAPIError):
    """Raised when the provided API key is invalid or unauthorized (HTTP 401)."""
    pass

class SymbolNotFoundError(FMPAPIError):
    """Raised when a requested symbol or resource is not found (HTTP 404)."""
    pass

class RateLimitExceededError(FMPAPIError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""
    pass

class FMPConnectionError(FMPAPIError):
    """Raised for network-related errors during API requests."""
    pass
