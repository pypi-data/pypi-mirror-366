class ContentZenError(Exception):
    """Base exception for ContentZen SDK."""
    pass

class AuthenticationError(ContentZenError):
    """Raised when authentication fails (401/403)."""
    pass

class NotFoundError(ContentZenError):
    """Raised when a resource is not found (404)."""
    pass

class APIError(ContentZenError):
    """Raised for other API errors."""
    pass