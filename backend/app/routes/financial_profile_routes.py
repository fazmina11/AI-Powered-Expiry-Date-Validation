"""
routes/financial_profile_routes.py — CRUD endpoints for ProductFinancialProfile.
Mounted under /api/v1/financial-profiles.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.financial_profile_schema import (
    ProductFinancialProfileCreate,
    ProductFinancialProfileUpdate,
    ProductFinancialProfileResponse,
)
from app.services.financial_profile_service import (
    get_profile,
    create_profile,
    update_profile,
    list_profiles,
    generate_synthetic_profiles,
)
from app.utils.exceptions import (
    ProductNotFoundError,
    FinancialProfileNotFoundError,
    DuplicateFinancialProfileError,
    InvalidPricingError,
)
from app.utils.response import success_response, error_response

router = APIRouter()


# ── GET /financial-profiles ────────────────────────────────────

@router.get("")
def list_financial_profiles_endpoint(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Retrieve a paginated list of all product financial profiles."""
    profiles = list_profiles(db, skip=skip, limit=limit)
    return success_response(
        data=[ProductFinancialProfileResponse.model_validate(p) for p in profiles],
        message="Financial profiles fetched successfully",
    )


# ── GET /financial-profiles/{product_id} ───────────────────────

@router.get("/{product_id}")
def get_financial_profile_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Fetch the financial profile for a specific product ID."""
    try:
        profile = get_profile(db, product_id)
        return success_response(
            data=ProductFinancialProfileResponse.model_validate(profile),
            message="Financial profile fetched successfully",
        )
    except FinancialProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(str(exc), exc.error_code),
        )


# ── POST /financial-profiles ───────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
def create_financial_profile_endpoint(
    payload: ProductFinancialProfileCreate,
    db: Session = Depends(get_db),
):
    """Manually register a new product financial profile."""
    try:
        profile = create_profile(db, payload)
        return success_response(
            data=ProductFinancialProfileResponse.model_validate(profile),
            message="Financial profile created successfully",
        )
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(str(exc), exc.error_code),
        )
    except DuplicateFinancialProfileError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_response(str(exc), exc.error_code),
        )
    except InvalidPricingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(str(exc), exc.error_code),
        )


# ── PUT /financial-profiles/{product_id} ───────────────────────

@router.put("/{product_id}")
def update_financial_profile_endpoint(
    product_id: int,
    payload: ProductFinancialProfileUpdate,
    db: Session = Depends(get_db),
):
    """Update one or more fields on an existing product's financial profile."""
    try:
        profile = update_profile(db, product_id, payload)
        return success_response(
            data=ProductFinancialProfileResponse.model_validate(profile),
            message="Financial profile updated successfully",
        )
    except FinancialProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_response(str(exc), exc.error_code),
        )
    except InvalidPricingError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(str(exc), exc.error_code),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(str(exc), "INVALID_PRICING"),
        )


# ── POST /financial-profiles/generate-synthetic ───────────────

@router.post("/generate-synthetic")
def generate_synthetic_profiles_endpoint(
    seed: int = Query(default=42),
    db: Session = Depends(get_db),
):
    """
    Trigger the synthetic generator.
    Creates a financial profile for every product that doesn't have one.
    """
    created_count = generate_synthetic_profiles(db, seed=seed)
    return success_response(
        data={"created_count": created_count},
        message=f"Generated {created_count} synthetic financial profiles successfully",
    )
