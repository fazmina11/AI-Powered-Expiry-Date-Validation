"""
services/cost_benefit_optimizer/recommendation_engine.py — Recommendation Ranking & Financial Metrics Engine.
"""

from decimal import Decimal
from typing import List, Dict, Any, Tuple


def rank_and_format_actions(
    redistribute_score: Decimal,
    return_score: Decimal,
    dispose_score: Decimal,
    prediction_confidence: Decimal,
    completeness_score: Decimal = Decimal("100.00")
) -> Tuple[List[Dict[str, Any]], Decimal]:
    """
    Ranks the three actions, sorts descending, and calculates overall recommendation confidence.
    
    Formula for Confidence (C):
      C = 0.40 * PredConf + 0.45 * (BestScore - RunnerUpScore) + 0.15 * Completeness
    """
    actions = [
        {"action": "REDISTRIBUTE", "score": redistribute_score},
        {"action": "RETURN_TO_SUPPLIER", "score": return_score},
        {"action": "DISPOSE", "score": dispose_score},
    ]

    # Sort descending by score
    actions.sort(key=lambda x: x["score"], reverse=True)

    best_score = actions[0]["score"]
    runner_up_score = actions[1]["score"]
    margin = best_score - runner_up_score

    # Compute confidence
    pred_conf_part = Decimal(str(prediction_confidence)) * Decimal("100.00")
    confidence = (
        Decimal("0.40") * pred_conf_part +
        Decimal("0.45") * margin +
        Decimal("0.15") * completeness_score
    )

    # Restrict confidence to [0, 100] range
    confidence = max(Decimal("0.00"), min(Decimal("100.00"), confidence))
    
    # Round ranking score and format output
    formatted_ranking = []
    for a in actions:
        # Sort score and map individual action confidence as a derived percentage of total score
        ind_score = Decimal(f"{a['score']:.2f}")
        total_sum = redistribute_score + return_score + dispose_score
        if total_sum > 0:
            ind_conf = (a["score"] / total_sum) * Decimal("100.00")
        else:
            ind_conf = Decimal("0.00")

        formatted_ranking.append({
            "action": a["action"],
            "score": ind_score,
            "confidence": f"{ind_conf:.0f}%"
        })

    return formatted_ranking, Decimal(f"{confidence:.2f}")


def calculate_financials(
    recommended_action: str,
    inventory_cost: Decimal,
    potential_revenue: Decimal,
    potential_financial_loss: Decimal,
    supplier_recoverable_value: Decimal,
    transfer_cost: Decimal,
) -> Dict[str, Decimal]:
    """
    Calculates expected savings, loss avoided, remaining financial loss, net benefit, and ROI.
    
    Expected Savings = Recoverable Value − Transfer Cost
    Loss Avoided = Potential Financial Loss − Remaining Financial Loss
    Net Benefit = Expected Savings − Transfer Cost
    ROI = (Net Benefit / Transfer Cost) * 100
    """
    # 1. Map Recoverable Value and Transfer Cost based on recommendation
    if recommended_action == "REDISTRIBUTE":
        recoverable_value = potential_revenue
        transport_cost = transfer_cost
        remaining_loss = Decimal("0.00")
    elif recommended_action == "RETURN_TO_SUPPLIER":
        recoverable_value = supplier_recoverable_value
        transport_cost = Decimal("0.00")
        remaining_loss = potential_financial_loss - supplier_recoverable_value
    else:  # DISPOSE
        recoverable_value = Decimal("0.00")
        transport_cost = Decimal("0.00")
        remaining_loss = potential_financial_loss

    # Ensure remaining loss is never negative
    remaining_loss = max(Decimal("0.00"), remaining_loss)

    # 2. Financial Formulas
    expected_savings = recoverable_value - transport_cost
    loss_avoided = potential_financial_loss - remaining_loss
    net_benefit = expected_savings - transport_cost

    # Safe ROI
    if transport_cost > 0:
        roi = (net_benefit / transport_cost) * Decimal("100.00")
    else:
        roi = Decimal("0.00")

    return {
        "current_inventory_value": Decimal(f"{inventory_cost:.2f}"),
        "expected_recovery": Decimal(f"{recoverable_value:.2f}"),
        "transport_cost": Decimal(f"{transport_cost:.2f}"),
        "net_benefit": Decimal(f"{net_benefit:.2f}"),
        "loss_avoided": Decimal(f"{loss_avoided:.2f}"),
        "roi_percent": Decimal(f"{roi:.2f}"),
        "remaining_financial_loss": Decimal(f"{remaining_loss:.2f}"),
        "expected_savings": Decimal(f"{expected_savings:.2f}"),
    }
