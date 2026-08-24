from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base exception for application-level errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found", details: dict = None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", details: dict = None):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, details=details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Global handler for domain-specific AppExceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": str(exc),
            "status_code": 500,
        },
    )
