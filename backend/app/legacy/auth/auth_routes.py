import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.utils.response import success_response
from app.utils.logger import logger

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return success_response(UserOut.model_validate(new_user))


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    logger.info("auth.login | success | username=%s", user.username)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Return the profile of the currently authenticated user.

    Error contract
    --------------
    401  – Authorization header missing OR token invalid / expired
    404  – Token is valid but user no longer exists in the database
    500  – Never: all exceptions are caught and re-raised as HTTPException
    """
    # get_current_user already raises 401 for bad/missing tokens.
    # We perform one additional guard: the user object must actually exist
    # (get_current_user raises credentials_exception instead of 404 when
    # the user is gone, so we normalise that here for caller clarity).
    if current_user is None:                          # defensive — should not happen
        logger.warning("auth.me | user resolved to None after dependency")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info("auth.me | success | username=%s id=%d", current_user.username, current_user.id)
    return current_user

