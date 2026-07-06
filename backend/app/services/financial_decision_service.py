"""
services/financial_decision_service.py — Standalone Financial Decision Engine.

Calculates:
  - Inventory Cost Value
  - Potential Revenue
  - Potential Financial Loss (EXPIRED status checking)
  - Supplier Recoverable Value (return rules policy checking)
  - Maximum Recoverable Value (max of return policy vs potential revenue)
  - Financial Health Score (weighted scoring algorithm)
  - Financial Priority & Decision Readiness
  - Rule-based explainable financial explanations

All pricing calculations are performed using Decimal to maintain precision.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.inventory import InventoryItem
from app.models.financial_profile import ProductFinancialProfile
from app.models.validation_record import ValidationRecord
from app.utils.exceptions import InventoryItemNotFoundError


def calculate_inventory_cost(quantity: int, purchase_price: Decimal) -> Decimal:
    """Calculate: quantity * purchase_price using Decimal."""
    return Decimal(str(quantity)) * Decimal(str(purchase_price))


def calculate_potential_revenue(quantity: int, mrp: Decimal) -> Decimal:
    """Calculate: quantity * mrp using Decimal."""
    return Decimal(str(quantity)) * Decimal(str(mrp))


def calculate_potential_loss(prediction: str, inventory_cost: Decimal) -> Decimal:
    """If prediction is EXPIRED, loss is the total cost. Otherwise, 0."""
    if prediction.upper() == "EXPIRED":
        return inventory_cost
    return Decimal("0.00")


def calculate_supplier_recoverable_value(supplier_return_allowed: bool, inventory_cost: Decimal, supplier_return_percent: Decimal) -> Decimal:
    """If allowed, returns cost * return percent. Otherwise, 0."""
    if supplier_return_allowed:
        return inventory_cost * (Decimal(str(supplier_return_percent)) / Decimal("100.00"))
    return Decimal("0.00")


def calculate_financial_health_score(
    remaining_days: Optional[int],
    prediction_confidence: Decimal,
    quality_score: Decimal,
    inventory_cost: Decimal,
    supplier_return_allowed: bool,
    supplier_return_percent: Decimal,
) -> Decimal:
    """
    Weighted Scoring Algorithm for Financial Health (0 - 100):
    
    1. Remaining Shelf Life Score (S_shelf, Weight: 30%)
       - If remaining_days is None: 50.00
       - If remaining_days <= 0: 0.00
       - If remaining_days >= 90: 100.00
       - Otherwise: (remaining_days / 90.00) * 100.00
       
    2. Prediction Confidence Score (S_conf, Weight: 15%)
       - (prediction_confidence) * 100.00
       
    3. Quality Score (S_quality, Weight: 15%)
       - (quality_score) * 100.00
       
    4. Inventory Cost Risk Score (S_cost, Weight: 20%)
       - Higher cost means higher risk, which reduces health:
       - If cost <= 1,000: 100.00
       - If cost >= 50,000: 0.00
       - Otherwise: 100.00 - ((cost - 1,000) / (50,000 - 1,000)) * 100.00
       
    5. Supplier Return Score (S_return, Weight: 20%)
       - If return allowed: supplier_return_percent
       - Else: 0.00
       
    Formula:
      Score = 0.30 * S_shelf + 0.15 * S_conf + 0.15 * S_quality + 0.20 * S_cost + 0.20 * S_return
    """
    # 1. Shelf life score
    if remaining_days is None:
        s_shelf = Decimal("50.00")
    elif remaining_days <= 0:
        s_shelf = Decimal("0.00")
    elif remaining_days >= 90:
        s_shelf = Decimal("100.00")
    else:
        s_shelf = (Decimal(str(remaining_days)) / Decimal("90.00")) * Decimal("100.00")

    # 2. Confidence score
    s_conf = Decimal(str(prediction_confidence)) * Decimal("100.00")

    # 3. Quality score
    s_quality = Decimal(str(quality_score)) * Decimal("100.00")

    # 4. Cost risk score
    cost_val = Decimal(str(inventory_cost))
    if cost_val <= Decimal("1000.00"):
        s_cost = Decimal("100.00")
    elif cost_val >= Decimal("50000.00"):
        s_cost = Decimal("0.00")
    else:
        s_cost = Decimal("100.00") - ((cost_val - Decimal("1000.00")) / Decimal("49000.00")) * Decimal("100.00")

    # 5. Return score
    if supplier_return_allowed:
        s_return = Decimal(str(supplier_return_percent))
    else:
        s_return = Decimal("0.00")

    # Weighted calculation
    score = (
        Decimal("0.30") * s_shelf +
        Decimal("0.15") * s_conf +
        Decimal("0.15") * s_quality +
        Decimal("0.20") * s_cost +
        Decimal("0.20") * s_return
    )
    
    # Restrict to [0, 100] range
    return max(Decimal("0.00"), min(Decimal("100.00"), score))


def determine_financial_priority(
    health_score: Decimal,
    inventory_cost: Decimal,
    potential_loss: Decimal,
    remaining_days: Optional[int],
) -> str:
    """
    Classifies batch financial priority into: LOW, MEDIUM, HIGH, CRITICAL.
    
    Rules:
      - CRITICAL if potential loss >= 10,000 OR (cost >= 10,000 and remaining_days <= 15)
      - HIGH if potential loss >= 5,000 OR (cost >= 5,000 and remaining_days <= 30) OR (cost >= 15,000)
      - MEDIUM if potential loss > 0 OR remaining_days <= 45 OR cost >= 2,000
      - LOW otherwise
    """
    cost_val = Decimal(str(inventory_cost))
    loss_val = Decimal(str(potential_loss))
    days = remaining_days

    # Critical conditions
    if loss_val >= Decimal("10000.00") or (days is not None and cost_val >= Decimal("10000.00") and days <= 15):
        return "CRITICAL"
        
    # High conditions
    if loss_val >= Decimal("5000.00") or (days is not None and cost_val >= Decimal("5000.00") and days <= 30) or cost_val >= Decimal("15000.00"):
        return "HIGH"

    # Medium conditions
    if loss_val > Decimal("0.00") or (days is not None and days <= 45) or cost_val >= Decimal("2000.00"):
        return "MEDIUM"

    return "LOW"


def generate_explanations(
    remaining_days: Optional[int],
    inventory_cost: Decimal,
    supplier_return_allowed: bool,
    supplier_return_percent: Decimal,
    prediction_confidence: Decimal,
    priority: str,
) -> List[str]:
    """Generates a dynamic list of rule-based explanations for the financial assessment."""
    explanations = []

    # Shelf-life rules
    if remaining_days is None:
        explanations.append("Remaining shelf life is unknown; immediate manual review is required.")
    elif remaining_days <= 0:
        explanations.append("Product is expired; potential loss equals total inventory cost.")
    elif remaining_days < settings.REJECT_DAYS:
        explanations.append("Remaining shelf life is below the recommended rejection threshold.")
    elif remaining_days <= settings.WARNING_DAYS:
        explanations.append("Remaining shelf life is below the warning threshold; priority sale recommended.")

    # Inventory cost rules
    if inventory_cost >= Decimal("10000.00"):
        explanations.append("Inventory value exceeds the configured high financial risk threshold.")
    elif inventory_cost >= Decimal("2000.00"):
        explanations.append("Inventory value represents moderate financial risk.")

    # Supplier returns rules
    if supplier_return_allowed and supplier_return_percent > 0:
        explanations.append("Supplier allows product returns, enabling financial recovery.")
    else:
        explanations.append("Supplier does not allow returns; no financial recovery is possible through returns.")

    # Confidence rules
    if prediction_confidence >= Decimal("0.90"):
        explanations.append("Prediction confidence is high.")
    elif prediction_confidence < Decimal("0.80"):
        explanations.append("Prediction confidence is low; additional check recommended.")

    # Priority rules
    if priority in ["HIGH", "CRITICAL"]:
        explanations.append("Immediate financial review is recommended.")

    return explanations


def perform_financial_analysis(db: Session, inventory_item_id: int) -> Dict[str, Any]:
    """
    Fetch data and orchestrate the full financial risk assessment for an inventory item.
    Supports backward compatibility with legacy inventory records.
    """
    # 1. Load inventory item
    item = db.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
    if not item:
        raise InventoryItemNotFoundError(f"Inventory item ID {inventory_item_id} not found")

    # 2. Get latest validation record to extract ML prediction confidence
    validation = db.query(ValidationRecord).filter(
        ValidationRecord.inventory_item_id == item.id
    ).order_by(ValidationRecord.created_at.desc()).first()

    # Extract confidence (default to 0.95 if none exists)
    confidence_score = Decimal("0.95")
    quality_score = Decimal("0.90")  # Default placeholder for quality

    if validation:
        if validation.confidence_score is not None:
            confidence_score = Decimal(str(validation.confidence_score))
        if validation.validation_status == "VALID":
            quality_score = Decimal("1.00")
        elif validation.validation_status == "LOW_CONFIDENCE":
            quality_score = Decimal("0.70")
        elif validation.validation_status == "MANUAL_REVIEW":
            quality_score = Decimal("0.80")

    # 3. Resolve pricing variables
    quantity = item.quantity if item.quantity is not None else 1
    purchase_price = item.purchase_price
    mrp = item.mrp
    supplier_return_allowed = item.supplier_return_allowed
    supplier_return_percent = item.supplier_return_percent

    # Fallback to product financial profile if empty on the inventory item
    if purchase_price is None or mrp is None or supplier_return_allowed is None:
        profile = db.query(ProductFinancialProfile).filter(
            ProductFinancialProfile.product_id == item.product_id
        ).first()
        if profile:
            if purchase_price is None:
                purchase_price = profile.purchase_price
            if mrp is None:
                mrp = profile.mrp
            if supplier_return_allowed is None:
                supplier_return_allowed = profile.supplier_return_allowed
            if supplier_return_percent is None:
                supplier_return_percent = profile.supplier_return_percent

    # Extreme fallback to prevent division by zero / database crash on unmigrated data
    if purchase_price is None:
        purchase_price = Decimal("0.00")
    if mrp is None:
        mrp = Decimal("0.00")
    if supplier_return_allowed is None:
        supplier_return_allowed = False
    if supplier_return_percent is None:
        supplier_return_percent = Decimal("0.00")

    # Convert inputs to decimals
    dec_purchase_price = Decimal(str(purchase_price))
    dec_mrp = Decimal(str(mrp))
    dec_supplier_return_percent = Decimal(str(supplier_return_percent))

    # 4. Perform financial calculations
    inventory_cost = calculate_inventory_cost(quantity, dec_purchase_price)
    potential_revenue = calculate_potential_revenue(quantity, dec_mrp)

    # Determine shelf-life prediction status (EXPIRED vs non-expired)
    prediction = "EXPIRED" if (item.remaining_days is not None and item.remaining_days <= 0) or item.status == "REJECTED" else "VALID"
    potential_financial_loss = calculate_potential_loss(prediction, inventory_cost)

    supplier_recoverable_value = calculate_supplier_recoverable_value(
        supplier_return_allowed, inventory_cost, dec_supplier_return_percent
    )

    maximum_recoverable_value = max(supplier_recoverable_value, potential_revenue)

    health_score = calculate_financial_health_score(
        item.remaining_days,
        confidence_score,
        quality_score,
        inventory_cost,
        supplier_return_allowed,
        dec_supplier_return_percent,
    )

    # Round health score to 2 decimal places
    health_score = Decimal(f"{health_score:.2f}")

    # Map status
    if health_score >= Decimal("90.00"):
        financial_status = "EXCELLENT"
    elif health_score >= Decimal("70.00"):
        financial_status = "HEALTHY"
    elif health_score >= Decimal("40.00"):
        financial_status = "AT_RISK"
    else:
        financial_status = "CRITICAL"

    priority = determine_financial_priority(
        health_score, inventory_cost, potential_financial_loss, item.remaining_days
    )

    explanations = generate_explanations(
        item.remaining_days,
        inventory_cost,
        supplier_return_allowed,
        dec_supplier_return_percent,
        confidence_score,
        priority,
    )

    # Decision readiness logic
    decision_ready = False
    if (
        health_score < Decimal("70.00") or
        (item.remaining_days is not None and item.remaining_days <= settings.WARNING_DAYS) or
        potential_financial_loss >= Decimal("2000.00") or
        priority in ["HIGH", "CRITICAL"]
    ):
        decision_ready = True

    return {
        "inventory_item_id": item.id,
        "inventory_cost": Decimal(f"{inventory_cost:.2f}"),
        "potential_revenue": Decimal(f"{potential_revenue:.2f}"),
        "potential_financial_loss": Decimal(f"{potential_financial_loss:.2f}"),
        "supplier_recoverable_value": Decimal(f"{supplier_recoverable_value:.2f}"),
        "maximum_recoverable_value": Decimal(f"{maximum_recoverable_value:.2f}"),
        "financial_health_score": Decimal(f"{health_score:.2f}"),
        "financial_status": financial_status,
        "financial_priority": priority,
        "financial_explanations": explanations,
        "decision_ready": decision_ready,
    }

