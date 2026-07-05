"""
middleware/exception_handler.py — Centralized exception logging and handling.
Returns standardized JSON responses for all validation, database, and system errors.
"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.logger import get_logger

logger = get_logger("app.exceptions")


from fastapi.encoders import jsonable_encoder

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic request validation exceptions."""
    details = jsonable_encoder(exc.errors())
    logger.warning(f"Validation failure on {request.method} {request.url.path}: {details}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Request validation failed.",
            "details": details,
            "detail": details
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle FastAPI/Starlette HTTP exceptions."""
    logger.warning(f"HTTPException on {request.method} {request.url.path} (status={exc.status_code}): {exc.detail}")
    if isinstance(exc.detail, dict):
        error_msg = exc.detail.get("message") or exc.detail.get("error") or str(exc.detail)
    else:
        error_msg = str(exc.detail)
        
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": error_msg,
            "details": exc.detail,
            "detail": exc.detail
        }
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity conflicts (e.g. duplicate keys)."""
    error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
    logger.warning(f"Integrity conflict on {request.method} {request.url.path}: {error_msg}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": "Database integrity constraint violated (conflict).",
            "details": {"message": error_msg},
            "detail": {"error": "DB_INTEGRITY_CONFLICT", "message": error_msg}
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle generic database driver failures."""
    logger.error(f"Database error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "A database operation encountered an unexpected failure.",
            "details": None
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Fallback handler for unhandled internal code errors."""
    logger.error(f"Unhandled system error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected server error occurred.",
            "details": None
        }
    )
