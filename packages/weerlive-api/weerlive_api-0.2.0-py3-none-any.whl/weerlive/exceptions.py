"""Exceptions for the Weerlive API."""


class WeerliveAPIError(Exception):
    """Base exception for all errors raised by the Weerlive API."""


class WeerliveAPIConnectionError(WeerliveAPIError):
    """Exception raised for connection errors."""


class WeerliveAPIKeyError(WeerliveAPIError):
    """Exception raised for invalid API key errors."""


class WeerliveAPIRateLimitError(WeerliveAPIError):
    """Exception raised when the API key's daily limit is exceeded."""


class WeerliveAPIRequestTimeoutError(WeerliveAPIError):
    """Exception raised for request timeouts."""


class WeerliveDecodeError(WeerliveAPIError):
    """Exception raised for errors decoding the API response."""
