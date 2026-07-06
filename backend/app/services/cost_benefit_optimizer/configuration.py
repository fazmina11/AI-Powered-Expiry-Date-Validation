"""
services/cost_benefit_optimizer/configuration.py — Configuration parameters for the Optimization Engine.
Loads custom weights from the database dynamically.
"""

from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.warehouse import OptimizationConfiguration


class OptimizationWeights:
    """Structure storing weights used to grade alternative actions."""
    def __init__(
        self,
        financial_weight: Decimal = Decimal("30.00"),
        demand_weight: Decimal = Decimal("25.00"),
        compatibility_weight: Decimal = Decimal("25.00"),
        transport_weight: Decimal = Decimal("30.00"),
        shelf_life_weight: Decimal = Decimal("20.00"),
        supplier_weight: Decimal = Decimal("30.00")
    ):
        self.financial_weight = financial_weight
        self.demand_weight = demand_weight
        self.compatibility_weight = compatibility_weight
        self.transport_weight = transport_weight
        self.shelf_life_weight = shelf_life_weight
        self.supplier_weight = supplier_weight


def load_optimization_weights(db: Session) -> OptimizationWeights:
    """Load weights from the database optimization_configurations table or fallback to default values."""
    db_config = db.query(OptimizationConfiguration).filter(
        OptimizationConfiguration.id == "default"
    ).first()

    if not db_config:
        return OptimizationWeights()

    return OptimizationWeights(
        financial_weight=Decimal(str(db_config.financial_weight)),
        demand_weight=Decimal(str(db_config.demand_weight)),
        compatibility_weight=Decimal(str(db_config.compatibility_weight)),
        transport_weight=Decimal(str(db_config.transport_weight)),
        shelf_life_weight=Decimal(str(db_config.shelf_life_weight)),
        supplier_weight=Decimal(str(db_config.supplier_weight)),
    )
