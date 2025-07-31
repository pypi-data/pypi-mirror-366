class CollibraAPIError(Exception):
    """Base exception for Collibra API errors"""
    pass

class UnauthorizedError(CollibraAPIError):
    """Raised when authentication fails"""
    pass

class ForbiddenError(CollibraAPIError):
    """Raised when access is forbidden"""
    pass

class NotFoundError(CollibraAPIError):
    """Raised when resource is not found"""
    pass

class ServerError(CollibraAPIError):
    """Raised when server returns 5xx errors"""
    pass
