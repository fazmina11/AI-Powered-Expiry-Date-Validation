"""
community/routes/user_routes.py
HTTP routes for /api/v1/community/users
All business logic delegated to community_user_service.
"""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.schemas.user_schemas import (
    CommunityUserCreate,
    CommunityUserResponse,
    CommunityUserUpdate,
)
from app.community import services as svc

router = APIRouter(prefix="/users", tags=["Community Users"])


@router.post(
    "",
    response_model=CommunityUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a community user",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
def create_user(
    payload: CommunityUserCreate,
    db: Session = Depends(get_db),
) -> CommunityUserResponse:
    """
    Register a new consumer who can submit product reports.

    - **email**: must be unique across all community users
    - **phone**: optional, must be E.164-compatible (e.g. +919876543210)
    """
    return svc.community_user_service.create_user(db, payload)


@router.get(
    "/{user_id}",
    response_model=CommunityUserResponse,
    summary="Get a community user by ID",
    responses={404: {"description": "User not found"}},
)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> CommunityUserResponse:
    """Fetch a single community user by their UUID."""
    return svc.community_user_service.get_user(db, user_id)


@router.put(
    "/{user_id}",
    response_model=CommunityUserResponse,
    summary="Update a community user",
    responses={
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
    },
)
def update_user(
    user_id: uuid.UUID,
    payload: CommunityUserUpdate,
    db: Session = Depends(get_db),
) -> CommunityUserResponse:
    """
    Partially update a community user's profile.
    Only the fields included in the request body are modified.
    """
    return svc.community_user_service.update_user(db, user_id, payload)
