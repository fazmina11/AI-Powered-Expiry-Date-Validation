"""
services/cost_benefit_optimizer/optimizer_service.py — Main Orchestrator for Phase 5.
Loads data, computes scores, and generates optimal recommended actions.
"""

from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.models.warehouse import SupplierReturnPolicy, WarehouseDemandProfile
from app.services.financial_decision_service import perform_financial_analysis
from app.services.cost_benefit_optimizer.configuration import load_optimization_weights
from app.services.cost_benefit_optimizer.scoring_engine import (
    score_redistribute_action,
    score_return_to_supplier_action,
    score_dispose_action,
)
from app.services.cost_benefit_optimizer.recommendation_engine import (
    rank_and_format_actions,
    calculate_financials,
)
from app.services.cost_benefit_optimizer.explanation_engine import generate_explanations as make_explanations
from app.utils.exceptions import InventoryItemNotFoundError


def optimize_inventory_item(db: Session, inventory_item_id: int) -> Dict[str, Any]:
    """Orchestrates the cost-benefit analysis and returns the optimal recommendation."""
    # 1. Load inventory item
    item = db.query(InventoryItem).filter(InventoryItem.id == inventory_item_id).first()
    if not item:
        raise InventoryItemNotFoundError(f"Inventory item ID {inventory_item_id} not found")

    # Resolve product and category
    product = db.query(Product).filter(Product.id == item.product_id).first()
    category = product.category if product else "Others"

    # 2. Get financial analytics results
    analysis = perform_financial_analysis(db, item.id)

    # 3. Load dynamic weights configuration
    weights = load_optimization_weights(db)

    # 4. Score REDISTRIBUTE
    dest_id, dest_name, redistribute_score, transfer_cost = score_redistribute_action(
        db, item, category, analysis["inventory_cost"], weights
    )

    # 5. Score RETURN_TO_SUPPLIER
    # Resolve supplier from product brand/details or use product supplier details
    brand = product.sku.split("-")[0] if product and "-" in product.sku else "Parle"
    policy = db.query(SupplierReturnPolicy).filter(SupplierReturnPolicy.supplier_id.ilike(brand)).first()
    
    return_score = score_return_to_supplier_action(item, policy, weights)

    # 6. Score DISPOSE
    dispose_score = score_dispose_action(item, analysis["financial_health_score"], analysis["inventory_cost"], weights)

    # 7. Extract ML prediction confidence score (from analysis metadata or default 0.95)
    # Perform confidence mapping
    pred_conf = Decimal("0.95")

    # 8. Rank actions and calculate overall confidence
    ranking, confidence = rank_and_format_actions(
        redistribute_score, return_score, dispose_score, pred_conf
    )

    recommended_action = ranking[0]["action"]

    # 9. Calculate extended financials
    financials = calculate_financials(
        recommended_action,
        analysis["inventory_cost"],
        analysis["potential_revenue"],
        analysis["potential_financial_loss"],
        analysis["supplier_recoverable_value"],
        transfer_cost,
    )

    # Resolve sell through days for category
    profile = db.query(WarehouseDemandProfile).filter(
        WarehouseDemandProfile.warehouse_id == "WH-BLR",
        WarehouseDemandProfile.product_category.ilike(category)
    ).first()
    sell_through = profile.average_sell_through_days if profile else 14

    # 10. Generate dynamic explanations
    explanations = make_explanations(
        recommended_action,
        dest_name,
        category,
        financials["transport_cost"],
        financials["expected_recovery"],
        financials["net_benefit"],
        redistribute_score,
        return_score,
        dispose_score,
        item.remaining_days,
        sell_through,
        policy.return_allowed if policy else False,
    )

    return {
        "recommended_action": recommended_action,
        "destination_warehouse_id": dest_id if recommended_action == "REDISTRIBUTE" else None,
        "destination_warehouse_name": dest_name if recommended_action == "REDISTRIBUTE" else None,
        "recommendation_ranking": ranking,
        "recommendation_confidence": confidence,
        "action_scores": {
            "REDISTRIBUTE": Decimal(f"{redistribute_score:.2f}"),
            "RETURN_TO_SUPPLIER": Decimal(f"{return_score:.2f}"),
            "DISPOSE": Decimal(f"{dispose_score:.2f}"),
        },
        "current_inventory_value": financials["current_inventory_value"],
        "expected_recovery": financials["expected_recovery"],
        "transport_cost": financials["transport_cost"],
        "net_benefit": financials["net_benefit"],
        "loss_avoided": financials["loss_avoided"],
        "roi_percent": financials["roi_percent"],
        "recommendation_explanation": explanations,
        "decision_engine_version": "1.0",
    }
