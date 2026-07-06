import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserProfile
from app.services.auth import create_access_token, hash_password, verify_password

from app.config import settings
from app.deps import DEV_USERS, get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("auth")


def _get_dev_user(email: str):
    return DEV_USERS.get(email)


def _save_dev_user(email: str, name: str, hashed_password: str):
    DEV_USERS[email] = {"email": email, "name": name, "hashed_password": hashed_password}


def _use_dev_auth():
    return settings.APP_ENV == "development"


@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    if _use_dev_auth():
        email = str(user_in.email)
        if _get_dev_user(email):
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = hash_password(user_in.password)
        _save_dev_user(email, user_in.name or "", hashed_password)
        access_token = create_access_token({"sub": email})
        return {"access_token": access_token, "token_type": "bearer"}

    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=user_in.email, name=user_in.name or "", hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: UserCreate, db: Session = Depends(get_db)):
    if _use_dev_auth():
        email = str(form_data.email)
        user = _get_dev_user(email)
        if user and verify_password(form_data.password, user["hashed_password"]):
            access_token = create_access_token({"sub": email})
            return {"access_token": access_token, "token_type": "bearer"}
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = db.query(User).filter(User.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserProfile)
def me(user: Any = Depends(get_current_user)):
    try:
        if isinstance(user, dict):
            email = user.get("email")
            name = user.get("name")
        else:
            email = getattr(user, "email", None)
            name = getattr(user, "name", None)

        if not email:
            logger.warning(
                "auth_me_route_missing_identity",
                extra={"event": "auth_me", "reason": "missing_user_identity"},
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        return {"email": str(email), "name": str(name or "")}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "auth_me_route_failed",
            extra={"event": "auth_me", "reason": "route_error"},
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable",
        ) from exc
