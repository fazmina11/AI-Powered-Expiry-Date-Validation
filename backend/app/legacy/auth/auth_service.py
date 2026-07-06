"""
services/auth.py — Authentication helpers.

  get_password_hash()    – bcrypt hash
  verify_password()      – bcrypt verify
  create_access_token()  – signed JWT
  get_current_user()     – FastAPI dependency: decodes JWT, loads User from DB

Error contract for get_current_user
-------------------------------------
  401  – Authorization header missing (raised by OAuth2PasswordBearer itself)
  401  – Token present but invalid / expired / malformed
  401  – Token payload has no 'sub' claim
  404  – Token is valid but user is not found in the database
  500  – Never: every exception is caught and re-raised as HTTPException
"""

import logging

from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.utils.logger import logger

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# auto_error=True (default) → FastAPI emits 401 automatically when the
# Authorization header is absent, before get_current_user is even called.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# ── Password helpers ──────────────────────────────────────────────────────────

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ── Current-user dependency ───────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the Bearer JWT and return the matching User row.

    Raises
    ------
    HTTP 401 – token invalid, expired, or missing 'sub' claim
    HTTP 404 – token valid but user not found in the database
    HTTP 500 – never (all unhandled exceptions are caught below)
    """

    # ── Step 1: decode JWT ────────────────────────────────────────────────────
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        logger.warning("auth.get_current_user | JWT expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as exc:
        logger.warning("auth.get_current_user | JWT decode error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as exc:
        # Catch-all: should not happen, but never let it become a 500
        logger.error("auth.get_current_user | unexpected JWT error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── Step 2: extract 'sub' claim ───────────────────────────────────────────
    username: str = payload.get("sub")
    if not username:
        logger.warning("auth.get_current_user | JWT payload missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is invalid: missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── Step 3: load user from database ──────────────────────────────────────
    try:
        user = db.query(User).filter(User.username == username).first()
    except SQLAlchemyError as exc:
        logger.error(
            "auth.get_current_user | database error for username=%s: %s",
            username, exc, exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching user",
        )
    except Exception as exc:
        logger.error(
            "auth.get_current_user | unexpected DB error for username=%s: %s",
            username, exc, exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while fetching user",
        )

    # ── Step 4: guard — user must exist ──────────────────────────────────────
    if user is None:
        logger.warning(
            "auth.get_current_user | user not found for username=%s (valid JWT)", username
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{username}' not found",
        )

    logger.debug("auth.get_current_user | resolved username=%s id=%d", user.username, user.id)
    return user
