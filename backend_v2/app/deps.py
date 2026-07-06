import logging
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auth")

# Development fallback store shared with auth routes.
DEV_USERS: dict[str, dict[str, Any]] = {}


def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("authorization")
    if not auth_header:
        logger.warning(
            "auth_me_missing_credentials",
            extra={"event": "auth_me", "reason": "missing_auth_header"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1]:
        logger.warning(
            "auth_me_invalid_authorization_format",
            extra={"event": "auth_me", "reason": "invalid_auth_header_format"},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    token = parts[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str | None = payload.get("sub")
        if not email:
            logger.warning(
                "auth_me_invalid_token",
                extra={"event": "auth_me", "reason": "missing_sub_claim"},
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError as exc:
        logger.warning(
            "auth_me_invalid_token",
            extra={"event": "auth_me", "reason": "jwt_error", "error": str(exc)},
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if settings.APP_ENV == "development":
        dev_user = DEV_USERS.get(email)
        if dev_user:
            logger.info(
                "auth_me_dev_user",
                extra={"event": "auth_me", "email": email, "source": "dev_store"},
            )
            return dev_user

    try:
        user = db.query(User).filter(User.email == email).first()
    except SQLAlchemyError as exc:
        logger.exception(
            "auth_me_db_error",
            extra={"event": "auth_me", "email": email, "reason": "database_error"},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc

    if user is None:
        logger.warning(
            "auth_me_user_not_found",
            extra={"event": "auth_me", "email": email, "reason": "user_missing"},
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    logger.info(
        "auth_me_success",
        extra={"event": "auth_me", "email": email, "source": "database"},
    )
    return user
