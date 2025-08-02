"""
Custom exceptions for the VRIN package.
"""


class VRINError(Exception):
    """Base exception for all VRIN-related errors."""
    
    def __init__(self, message: str, status_code: int = None, response_body: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
    
    def __str__(self):
        if self.status_code:
            return f"VRIN Error {self.status_code}: {self.message}"
        return f"VRIN Error: {self.message}"


class VRINAuthenticationError(VRINError):
    """Raised when authentication fails (invalid API key)."""
    
    def __init__(self, message: str = "Invalid API key", status_code: int = 401):
        super().__init__(message, status_code)


class VRINRateLimitError(VRINError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", status_code: int = 429):
        super().__init__(message, status_code)


class VRINTimeoutError(VRINError):
    """Raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out", status_code: int = 408):
        super().__init__(message, status_code)


class VRINValidationError(VRINError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Invalid input", status_code: int = 400):
        super().__init__(message, status_code)


class VRINServerError(VRINError):
    """Raised when the server encounters an error."""
    
    def __init__(self, message: str = "Server error", status_code: int = 500):
        super().__init__(message, status_code) 