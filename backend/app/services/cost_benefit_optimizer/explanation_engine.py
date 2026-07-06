"""
services/cost_benefit_optimizer/explanation_engine.py — Rule-based Explanation Engine.
Generates human-readable explanations dynamically based on calculated scores and actions.
"""

from decimal import Decimal
from typing import List, Optional


def generate_explanations(
    recommended_action: str,
    destination_warehouse_name: Optional[str],
    product_category: str,
    transfer_cost: Decimal,
    expected_recovery: Decimal,
    net_benefit: Decimal,
    redistribute_score: Decimal,
    return_score: Decimal,
    dispose_score: Decimal,
    remaining_days: Optional[int],
    average_sell_through_days: int,
    supplier_allowed: bool,
) -> List[str]:
    """Generates a dynamic list of rule-based explanations for the selected action."""
    explanations = []

    # 1. Action-specific top summaries
    if recommended_action == "REDISTRIBUTE":
        dest_name = destination_warehouse_name or "destination warehouse"
        explanations.append(f"Warehouse {dest_name} has high demand for {product_category} products.")
        if transfer_cost < expected_recovery:
            explanations.append("Transfer cost is lower than expected recoverable value.")
        if remaining_days is not None and remaining_days >= average_sell_through_days:
            explanations.append("Remaining shelf life exceeds expected sell-through period.")
        explanations.append("Redistribution provides the highest financial return.")

    elif recommended_action == "RETURN_TO_SUPPLIER":
        explanations.append("Supplier return enables immediate capital recovery under return policy.")
        if supplier_allowed:
            explanations.append("Supplier allows product returns, enabling financial recovery.")
        if return_score > redistribute_score:
            explanations.append("Supplier return recovers more value than redistribution.")

    else:  # DISPOSE
        explanations.append("Disposal is recommended due to critical expiry risk.")
        if remaining_days is not None and remaining_days <= 0:
            explanations.append("Product is already expired; potential loss equals total inventory cost.")
        if transfer_cost > expected_recovery and redistribute_score > 0:
            explanations.append("Transfer cost to alternative warehouses exceeds expected recoverable value.")

    # 2. General comparative explanations
    if recommended_action != "RETURN_TO_SUPPLIER" and return_score > 0 and redistribute_score > return_score:
        explanations.append("Supplier return recovers less value than redistribution.")

    if net_benefit < 0:
        explanations.append("Warning: The optimal action still results in a net financial loss.")

    return explanations
