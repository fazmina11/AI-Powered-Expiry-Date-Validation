"""
community/services/community_user_service.py
All business logic for community users. Zero SQL inside routes.
"""
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.community.models.community_user import CommunityUser
from app.community.schemas.user_schemas import (
    CommunityUserCreate,
    CommunityUserUpdate,
)


def create_user(db: Session, payload: CommunityUserCreate) -> CommunityUser:
    """
    Create a new community user.
    Raises 409 if the email is already registered.
    """
    user = CommunityUser(
        full_name=payload.full_name,
        email=payload.email.lower().strip(),
        phone=payload.phone,
        country=payload.country,
        state=payload.state,
        city=payload.city,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_EMAIL",
                "message": f"A community user with email '{payload.email}' already exists.",
            },
        )
    return user


def get_user(db: Session, user_id: uuid.UUID) -> CommunityUser:
    """
    Fetch a community user by UUID.
    Raises 404 if not found.
    """
    user = db.query(CommunityUser).filter(CommunityUser.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "USER_NOT_FOUND",
                "message": f"Community user '{user_id}' not found.",
            },
        )
    return user


def update_user(
    db: Session, user_id: uuid.UUID, payload: CommunityUserUpdate
) -> CommunityUser:
    """
    Partially update a community user.
    Only fields explicitly provided in the payload are updated.
    Raises 404 if not found.
    """
    user = get_user(db, user_id)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "INTEGRITY_ERROR", "message": "Update violated a database constraint."},
        )
    return user
