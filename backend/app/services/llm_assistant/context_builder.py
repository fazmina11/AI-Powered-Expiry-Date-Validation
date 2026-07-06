"""
services/llm_assistant/context_builder.py — Context Builder for the AI Assistant.
Extracts and builds clean JSON-serializable context structures from database models and optimization outputs.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.product import Product
from app.services.financial_decision_service import perform_financial_analysis
from app.services.cost_benefit_optimizer.optimizer_service import optimize_inventory_item


def build_inventory_context(db: Session, item: InventoryItem) -> Dict[str, Any]:
    """Compiles a strict JSON-serializable dictionary containing only relevant parameters for the item."""
    # 1. Resolve product
    product = db.query(Product).filter(Product.id == item.product_id).first()
    product_name = product.name if product else "Unknown Product"

    # 2. Get Financial Analysis
    financial_analysis = perform_financial_analysis(db, item.id)

    # 3. Get Cost-Benefit Optimization
    optimization = optimize_inventory_item(db, item.id)

    return {
        "Product Name": product_name,
        "Remaining Shelf Life": f"{item.remaining_days} days" if item.remaining_days is not None else "Unknown",
        "Predicted Status": item.status or "Unknown",
        "Financial Health Score": float(financial_analysis["financial_health_score"]),
        "Financial Status": financial_analysis["financial_status"],
        "Financial Priority": financial_analysis["financial_priority"],
        "Recommended Action": optimization["recommended_action"],
        "Recommendation Confidence": f"{optimization['recommendation_confidence']:.2f}%",
        "Destination Warehouse": optimization["destination_warehouse_name"] or "None",
        "Inventory Cost": float(optimization["current_inventory_value"]),
        "Potential Revenue": float(optimization["expected_recovery"]) if optimization["recommended_action"] == "REDISTRIBUTE" else float(financial_analysis["potential_revenue"]),
        "Transfer Cost": float(optimization["transport_cost"]),
        "Net Benefit": float(optimization["net_benefit"]),
        "Loss Avoided": float(optimization["loss_avoided"]),
        "Optimizer Explanations": optimization["recommendation_explanation"],
    }


def build_warehouse_summary_context(db: Session, items: List[InventoryItem]) -> Dict[str, Any]:
    """Compiles a summary context structure over multiple high-risk batches for the executive overview."""
    total_items = len(items)
    high_risk_count = 0
    total_preventable_loss = 0.0
    total_expected_savings = 0.0
    redistribute_count = 0
    return_count = 0
    dispose_count = 0


    for item in items:
        try:
            optimization = optimize_inventory_item(db, item.id)
            action = optimization["recommended_action"]
            
            # Count actions
            if action == "REDISTRIBUTE":
                redistribute_count += 1
            elif action == "RETURN_TO_SUPPLIER":
                return_count += 1
            elif action == "DISPOSE":
                dispose_count += 1

            if optimization["financial_priority"] in ["HIGH", "CRITICAL"]:
                high_risk_count += 1

            total_preventable_loss += float(optimization["loss_avoided"])
            total_expected_savings += float(optimization["expected_recovery"]) - float(optimization["transport_cost"])
        except Exception:
            # Skip unanalyzable batches gracefully
            continue

    return {
        "Total Scoped Batches": total_items,
        "Number of High-Risk Batches": high_risk_count,
        "Estimated Preventable Financial Loss": float(total_preventable_loss),
        "Total Expected Savings": float(total_expected_savings),
        "Redistribution Opportunities": redistribute_count,
        "Supplier Return Opportunities": return_count,
        "Disposal Recommendations": dispose_count,
    }
