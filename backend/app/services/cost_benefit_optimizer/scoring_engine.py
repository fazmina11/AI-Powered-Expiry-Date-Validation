"""
services/cost_benefit_optimizer/scoring_engine.py — Weighted Scoring Engine for Phase 5.
Scores: REDISTRIBUTE, RETURN_TO_SUPPLIER, and DISPOSE deterministically.
"""

from decimal import Decimal
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem
from app.models.warehouse import (
    Warehouse,
    WarehouseConfiguration,
    WarehouseDemandProfile,
    WarehouseTransferMatrix,
    SupplierReturnPolicy,
)
from app.services.cost_benefit_optimizer.configuration import OptimizationWeights


def score_redistribute_action(
    db: Session,
    item: InventoryItem,
    category: str,
    inventory_cost: Decimal,
    weights: OptimizationWeights,
    source_warehouse_id: str = "WH-BLR",
) -> Tuple[Optional[str], Optional[str], Decimal, Decimal]:
    """
    Evaluates redistribution score for all other 9 warehouses.
    Returns: (best_dest_id, best_dest_name, best_score, transfer_cost)
    """
    warehouses = db.query(Warehouse).filter(Warehouse.id != source_warehouse_id).all()
    if not warehouses:
        return None, None, Decimal("0.00"), Decimal("0.00")

    best_score = Decimal("-1.00")
    best_dest_id = None
    best_dest_name = None
    best_transfer_cost = Decimal("0.00")

    for wh in warehouses:
        # 1. Demand Score (Weight: demand_weight)
        profile = db.query(WarehouseDemandProfile).filter(
            WarehouseDemandProfile.warehouse_id == wh.id,
            WarehouseDemandProfile.product_category.ilike(category)
        ).first()

        if profile:
            # Scale based on 300 base
            d_val = (profile.average_daily_demand / Decimal("300.00")) * Decimal("100.00")
            if profile.demand_trend == "INCREASING":
                d_val += Decimal("20.00")
            elif profile.demand_trend == "DECREASING":
                d_val -= Decimal("20.00")
            d_val *= profile.seasonality_factor
            demand_score = max(Decimal("0.00"), min(Decimal("100.00"), d_val))
            sell_through = profile.average_sell_through_days
        else:
            demand_score = Decimal("50.00")
            sell_through = 14

        # 2. Compatibility Score (Weight: compatibility_weight)
        config = db.query(WarehouseConfiguration).filter(
            WarehouseConfiguration.warehouse_id == wh.id
        ).first()

        if category.lower() == "dairy" and config and not config.cold_storage_available:
            compatibility_score = Decimal("0.00")
        else:
            compatibility_score = Decimal("100.00")

        # 3. Cost Factor Score (Weight: transport_weight)
        matrix = db.query(WarehouseTransferMatrix).filter(
            WarehouseTransferMatrix.source_warehouse_id == source_warehouse_id,
            WarehouseTransferMatrix.destination_warehouse_id == wh.id
        ).first()

        transfer_cost = Decimal("0.00")
        if matrix:
            transfer_cost = matrix.total_transfer_cost
            c_val = Decimal("100.00") - (transfer_cost / (inventory_cost + Decimal("1.00"))) * Decimal("100.00")
            cost_score = max(Decimal("0.00"), min(Decimal("100.00"), c_val))
        else:
            cost_score = Decimal("100.00")

        # 4. Shelf Life vs Sell-Through Score (Weight: shelf_life_weight)
        days = item.remaining_days
        if days is None:
            shelf_life_score = Decimal("50.00")
        elif days <= 0 or item.status == "REJECTED":
            shelf_life_score = Decimal("0.00")
        elif days >= sell_through:
            shelf_life_score = Decimal("100.00")
        else:
            shelf_life_score = (Decimal(str(days)) / Decimal(str(sell_through))) * Decimal("100.00")


        # Weighted calculation for this destination
        w_sum = (
            weights.demand_weight +
            weights.compatibility_weight +
            weights.transport_weight +
            weights.shelf_life_weight
        )
        if w_sum <= 0:
            w_sum = Decimal("1.00")

        score = (
            demand_score * weights.demand_weight +
            compatibility_score * weights.compatibility_weight +
            cost_score * weights.transport_weight +
            shelf_life_score * weights.shelf_life_weight
        ) / w_sum

        score = max(Decimal("0.00"), min(Decimal("100.00"), score))

        if score > best_score:
            best_score = score
            best_dest_id = wh.id
            best_dest_name = wh.name
            best_transfer_cost = transfer_cost

    return best_dest_id, best_dest_name, best_score, best_transfer_cost


def score_return_to_supplier_action(
    item: InventoryItem,
    policy: Optional[SupplierReturnPolicy],
    weights: OptimizationWeights,
) -> Decimal:
    """Evaluates supplier return score based on return windows, policy allowed status, and quantity limits."""
    # If policy doesn't exist or return is disabled: score = 0
    if not policy or not policy.return_allowed or not item.supplier_return_allowed:
        return Decimal("0.00")

    # 1. Window & Shelf Life Fit (Weight: shelf_life_weight)
    days = item.remaining_days
    if days is None or days <= 0:
        window_score = Decimal("0.00")
    elif days < policy.minimum_remaining_shelf_life:
        window_score = Decimal("0.00")
    elif days >= (policy.minimum_remaining_shelf_life + policy.return_window_days):
        window_score = Decimal("100.00")
    else:
        window_score = Decimal("50.00")

    # 2. Recovery / Return Percent (Weight: supplier_weight)
    recovery_score = policy.maximum_return_percentage

    # 3. Quantity Fit (Weight: financial_weight)
    qty = item.quantity if item.quantity is not None else 1
    if qty >= policy.minimum_return_quantity and qty <= policy.maximum_return_quantity:
        quantity_score = Decimal("100.00")
    else:
        # Out of bounds receives partial penalty
        quantity_score = Decimal("40.00")

    # Normalization
    w_sum = weights.shelf_life_weight + weights.supplier_weight + weights.financial_weight
    if w_sum <= 0:
        w_sum = Decimal("1.00")

    score = (
        window_score * weights.shelf_life_weight +
        recovery_score * weights.supplier_weight +
        quantity_score * weights.financial_weight
    ) / w_sum

    return max(Decimal("0.00"), min(Decimal("100.00"), score))


def score_dispose_action(
    item: InventoryItem,
    financial_health_score: Decimal,
    inventory_cost: Decimal,
    weights: OptimizationWeights,
) -> Decimal:
    """Evaluates dispose score based on expiration risk, financial loss, and transit cost constraints."""
    # 1. Expiration Score (Weight: shelf_life_weight)
    days = item.remaining_days
    if days is None:
        expiry_score = Decimal("30.00")
    elif days <= 0:
        expiry_score = Decimal("100.00")
    elif days <= 15:
        expiry_score = Decimal("60.00")
    else:
        expiry_score = Decimal("10.00")

    # 2. Health Score Inverse (Weight: financial_weight)
    # Lower health score makes disposal more logical
    health_score_inverse = Decimal("100.00") - financial_health_score

    # 3. Low Value Transit Constraint (Weight: transport_weight)
    # If the batch value is very small, shipping cost outweighs benefits
    if inventory_cost < Decimal("200.00"):
        low_value_score = Decimal("90.00")
    else:
        low_value_score = Decimal("10.00")

    # Normalization
    w_sum = weights.shelf_life_weight + weights.financial_weight + weights.transport_weight
    if w_sum <= 0:
        w_sum = Decimal("1.00")

    score = (
        expiry_score * weights.shelf_life_weight +
        health_score_inverse * weights.financial_weight +
        low_value_score * weights.transport_weight
    ) / w_sum

    return max(Decimal("0.00"), min(Decimal("100.00"), score))
