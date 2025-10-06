"""Custom exception handlers for BWARM Dashboard API."""

from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: Union[str, dict]
    status_code: int


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions.

    Args:
        request: FastAPI request
        exc: HTTP exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON response with validation error details
    """
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "status_code": 422},
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors.

    Args:
        request: FastAPI request
        exc: SQLAlchemy error

    Returns:
        JSON response with generic error message (don't expose DB details)
    """
    # Log the actual error for debugging
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Database error: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An error occurred while processing your request. Please try again later.",
            "status_code": 500,
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON response with generic error message
    """
    # Log the actual error for debugging
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
        },
    )
