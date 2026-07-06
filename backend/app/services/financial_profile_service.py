"""
services/financial_profile_service.py — Service layer for ProductFinancialProfile.
Handles database CRUD, synthetic generation, and business rules verification.
"""

from decimal import Decimal
import random
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.financial_profile import ProductFinancialProfile
from app.models.product import Product
from app.schemas.financial_profile_schema import (
    ProductFinancialProfileCreate,
    ProductFinancialProfileUpdate,
)
from app.utils.exceptions import (
    ProductNotFoundError,
    FinancialProfileNotFoundError,
    DuplicateFinancialProfileError,
    InvalidPricingError,
)


def get_profile(db: Session, product_id: int) -> ProductFinancialProfile:
    """Fetch the financial profile for a given product_id."""
    profile = db.query(ProductFinancialProfile).filter(
        ProductFinancialProfile.product_id == product_id
    ).first()
    if not profile:
        raise FinancialProfileNotFoundError(f"Financial profile not found for product ID {product_id}")
    return profile


def create_profile(db: Session, payload: ProductFinancialProfileCreate) -> ProductFinancialProfile:
    """Create a new financial profile after validating product existence and uniqueness."""
    # 1. Verify product exists
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise ProductNotFoundError(f"Product not found for ID {payload.product_id}")

    # 2. Check for duplicate profile
    existing = db.query(ProductFinancialProfile).filter(
        ProductFinancialProfile.product_id == payload.product_id
    ).first()
    if existing:
        raise DuplicateFinancialProfileError(f"Financial profile already exists for product ID {payload.product_id}")

    # 3. Validation constraints
    if payload.mrp < payload.purchase_price:
        raise InvalidPricingError("MRP must be greater than or equal to purchase price")
    if payload.purchase_price <= 0:
        raise InvalidPricingError("Purchase price must be greater than zero")
    if not (Decimal("0.00") <= payload.supplier_return_percent <= Decimal("100.00")):
        raise InvalidPricingError("Supplier return percent must be between 0 and 100")

    # 4. Insert model
    new_profile = ProductFinancialProfile(
        product_id=payload.product_id,
        purchase_price=payload.purchase_price,
        mrp=payload.mrp,
        default_profit_margin_percent=payload.default_profit_margin_percent,
        currency=payload.currency,
        supplier_return_allowed=payload.supplier_return_allowed,
        supplier_return_percent=payload.supplier_return_percent,
    )
    db.add(new_profile)
    try:
        db.commit()
        db.refresh(new_profile)
    except IntegrityError:
        db.rollback()
        raise DuplicateFinancialProfileError(f"Integrity check failed: profile already exists for product ID {payload.product_id}")
    
    return new_profile


def update_profile(db: Session, product_id: int, payload: ProductFinancialProfileUpdate) -> ProductFinancialProfile:
    """Update an existing financial profile with cross-field price checks."""
    profile = db.query(ProductFinancialProfile).filter(
        ProductFinancialProfile.product_id == product_id
    ).first()
    if not profile:
        raise FinancialProfileNotFoundError(f"Financial profile not found for product ID {product_id}")

    # Merge updates and validate final state
    updated_purchase_price = payload.purchase_price if payload.purchase_price is not None else profile.purchase_price
    updated_mrp = payload.mrp if payload.mrp is not None else profile.mrp
    updated_return_percent = payload.supplier_return_percent if payload.supplier_return_percent is not None else profile.supplier_return_percent

    if Decimal(str(updated_purchase_price)) <= 0:
        raise InvalidPricingError("Purchase price must be greater than zero")
    if Decimal(str(updated_mrp)) < Decimal(str(updated_purchase_price)):
        raise InvalidPricingError("MRP must be greater than or equal to purchase price")
    if not (Decimal("0.00") <= Decimal(str(updated_return_percent)) <= Decimal("100.00")):
        raise InvalidPricingError("Supplier return percent must be between 0 and 100")

    # Save fields
    if payload.purchase_price is not None:
        profile.purchase_price = payload.purchase_price
    if payload.mrp is not None:
        profile.mrp = payload.mrp
    if payload.default_profit_margin_percent is not None:
        profile.default_profit_margin_percent = payload.default_profit_margin_percent
    if payload.currency is not None:
        profile.currency = payload.currency
    if payload.supplier_return_allowed is not None:
        profile.supplier_return_allowed = payload.supplier_return_allowed
    if payload.supplier_return_percent is not None:
        profile.supplier_return_percent = payload.supplier_return_percent

    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(db: Session, skip: int = 0, limit: int = 50) -> List[ProductFinancialProfile]:
    """Fetch a paginated list of financial profiles."""
    return db.query(ProductFinancialProfile).offset(skip).limit(limit).all()


def generate_synthetic_profiles(db: Session, seed: int = 42) -> int:
    """
    Generate deterministic financial profiles for all products lacking one.
    Analyzes name, category, SKU to select realistic profit margins & MRP.
    """
    # 1. Fetch all products lacking a financial profile
    subquery = db.query(ProductFinancialProfile.product_id)
    products_without_profile = db.query(Product).filter(~Product.id.in_(subquery)).all()

    created_count = 0

    for product in products_without_profile:
        category = (product.category or "").strip().lower()
        name = (product.name or "").strip().lower()

        # Deterministic settings: margins & retail pricing ranges (INR)
        margin = Decimal("0.20")
        mrp_min, mrp_max = 50.0, 200.0

        # Deterministic return values based on category
        supplier_return_allowed = True
        supplier_return_percent = Decimal("75.00")

        if "dairy" in category or any(w in name for w in ["milk", "yogurt", "curd", "cheese", "butter"]):
            margin = Decimal("0.12")
            supplier_return_allowed = True
            supplier_return_percent = Decimal("90.00")
            if "milk" in name:
                if any(w in name for w in ["1l", "1 l"]):
                    mrp_min, mrp_max = 60.0, 85.0
                elif "500" in name:
                    mrp_min, mrp_max = 28.0, 38.0
                else:
                    mrp_min, mrp_max = 30.0, 70.0
            elif any(w in name for w in ["yogurt", "curd"]):
                mrp_min, mrp_max = 35.0, 110.0
            elif "cheese" in name:
                mrp_min, mrp_max = 120.0, 280.0
            else:
                mrp_min, mrp_max = 40.0, 180.0

        elif "beverage" in category or any(w in name for w in ["juice", "soda", "cola", "tea", "coffee", "drink"]):
            margin = Decimal("0.15")
            supplier_return_allowed = True
            supplier_return_percent = Decimal("75.00")
            if "juice" in name:
                mrp_min, mrp_max = 45.0, 140.0
            elif any(w in name for w in ["soda", "cola"]):
                mrp_min, mrp_max = 20.0, 60.0
            elif any(w in name for w in ["coffee", "tea"]):
                mrp_min, mrp_max = 80.0, 450.0
            else:
                mrp_min, mrp_max = 30.0, 220.0

        elif "produce" in category or any(w in name for w in ["fruit", "vegetable", "apple", "tomato", "banana", "potato", "onion"]):
            margin = Decimal("0.18")
            mrp_min, mrp_max = 25.0, 130.0
            supplier_return_allowed = False
            supplier_return_percent = Decimal("0.00")

        elif "bakery" in category or any(w in name for w in ["bread", "bun", "cake", "cookie", "rusk"]):
            margin = Decimal("0.20")
            supplier_return_allowed = False
            supplier_return_percent = Decimal("0.00")
            if "bread" in name:
                mrp_min, mrp_max = 25.0, 65.0
            elif "cake" in name:
                mrp_min, mrp_max = 100.0, 350.0
            else:
                mrp_min, mrp_max = 30.0, 150.0

        elif "personal" in category or "care" in category:
            margin = Decimal("0.25")
            mrp_min, mrp_max = 80.0, 450.0
            supplier_return_allowed = True
            supplier_return_percent = Decimal("75.00")

        else:
            # General Packaged Foods/Other categories
            margin = Decimal("0.25")
            mrp_min, mrp_max = 45.0, 300.0
            supplier_return_allowed = True
            supplier_return_percent = Decimal("50.00")

        # Build repeatable seed using product properties
        prod_seed = f"{seed}_{product.id}_{product.sku}_{product.barcode}"
        seed_val = sum(ord(c) for c in prod_seed)
        rng = random.Random(seed_val)

        # Generate deterministic price attributes
        mrp_val = rng.uniform(mrp_min, mrp_max)
        mrp = Decimal(f"{mrp_val:.2f}")

        purchase_price_val = mrp * (Decimal("1.00") - margin)
        purchase_price = Decimal(f"{purchase_price_val:.2f}")

        # Validation guarantee: MRP must be greater than or equal to purchase price
        if mrp < purchase_price:
            mrp = purchase_price

        # Convert margin to percentage representation (e.g. 0.12 -> 12.00)
        margin_percent = margin * Decimal("100.00")

        # Create Profile
        new_profile = ProductFinancialProfile(
            product_id=product.id,
            purchase_price=purchase_price,
            mrp=mrp,
            default_profit_margin_percent=margin_percent,
            currency="INR",
            supplier_return_allowed=supplier_return_allowed,
            supplier_return_percent=supplier_return_percent,
        )
        db.add(new_profile)
        created_count += 1

    if created_count > 0:
        db.commit()

    return created_count
