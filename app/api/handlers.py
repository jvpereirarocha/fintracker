# app/api/handlers.py
import logging

from fastapi import Request, status
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions.base import BaseDomainException, ExceptionType

logger = logging.getLogger(__name__)


def get_status_code_by_exception_type(exception_type: ExceptionType) -> int:
    match exception_type:
        case ExceptionType.BAD_REQUEST:
            return status.HTTP_400_BAD_REQUEST
        case ExceptionType.UNAUTHORIZED:
            return status.HTTP_401_UNAUTHORIZED
        case ExceptionType.FORBIDDEN:
            return status.HTTP_403_FORBIDDEN
        case ExceptionType.NOT_FOUND:
            return status.HTTP_404_NOT_FOUND
        case ExceptionType.CONFLICT:
            return status.HTTP_409_CONFLICT
        case ExceptionType.INTERNAL_SERVER_ERROR:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        case _:
            return status.HTTP_500_INTERNAL_SERVER_ERROR


async def domain_exception_handler(request: Request, exc: BaseDomainException):
    """
    Translates Use Case exceptions into HTTP 400/404 responses.
    """
    # You can map specific exception names to specific status codes if needed
    status_code = get_status_code_by_exception_type(exception_type=exc.type)

    return JSONResponse(status_code=status_code, content={"detail": exc.message})


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Keeps FastAPI's default 422 response and hands the names of the failing fields to the
    request logging middleware (never the values: they can hold personal data).
    """
    request.state.validation_errors = sorted(
        {".".join(str(part) for part in error["loc"]) for error in exc.errors()}
    )
    return await request_validation_exception_handler(request, exc)


async def global_500_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catches any unhandled exception (e.g., database connection drops, syntax errors).
    Returns a friendly message to the frontend and logs the real error.
    """
    # Set by RequestLoggingMiddleware; this response is built outside of it, so the
    # X-Request-ID header has to be added here
    request_id = getattr(request.state, "request_id", None)

    # Log the actual traceback for debugging purposes
    logger.error(
        "Unhandled exception at %s (request_id=%s): %s",
        request.url.path,
        request_id,
        exc,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
        headers={"X-Request-ID": request_id} if request_id else None,
    )
