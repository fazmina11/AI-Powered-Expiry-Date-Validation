"""
models/warehouse.py — SQLAlchemy ORM models for Warehouse Intelligence.
"""

import uuid
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Uuid, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id   = Column(String(50), primary_key=True)  # e.g., "WH-BLR"
    name = Column(String(100), nullable=False)

    # Relationships
    configuration = relationship("WarehouseConfiguration", back_populates="warehouse", uselist=False, cascade="all, delete-orphan")
    demand_profiles = relationship("WarehouseDemandProfile", back_populates="warehouse", cascade="all, delete-orphan")


class TransportCostConfiguration(Base):
    __tablename__ = "transport_cost_configurations"

    id                    = Column(String(50), primary_key=True, default="default")
    fuel_cost_per_km      = Column(Numeric(10, 2), nullable=False)
    labour_cost_per_hour  = Column(Numeric(10, 2), nullable=False)
    good_handling_cost    = Column(Numeric(10, 2), nullable=False)
    moderate_handling_cost = Column(Numeric(10, 2), nullable=False)
    poor_handling_cost    = Column(Numeric(10, 2), nullable=False)
    updated_at            = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class WarehouseConfiguration(Base):
    __tablename__ = "warehouse_configurations"

    id                        = Column(Uuid, primary_key=True, default=uuid.uuid4)
    warehouse_id              = Column(String(50), ForeignKey("warehouses.id", ondelete="CASCADE"), unique=True, nullable=False)
    warehouse_capacity        = Column(Integer, nullable=False)
    warehouse_operating_hours = Column(String(50), nullable=False)
    maximum_daily_dispatch    = Column(Integer, nullable=False)
    cold_storage_available    = Column(Boolean, default=True, nullable=False)
    temperature_control       = Column(Boolean, default=True, nullable=False)
    priority_level            = Column(String(50), default="MEDIUM", nullable=False)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="configuration")


class WarehouseDemandProfile(Base):
    __tablename__ = "warehouse_demand_profiles"

    id                        = Column(Uuid, primary_key=True, default=uuid.uuid4)
    warehouse_id              = Column(String(50), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    product_category          = Column(String(100), nullable=False)
    average_daily_demand      = Column(Numeric(10, 2), nullable=False)
    average_weekly_demand     = Column(Numeric(10, 2), nullable=False)
    average_monthly_demand    = Column(Numeric(10, 2), nullable=False)
    demand_trend              = Column(String(50), default="STABLE", nullable=False)  # INCREASING, STABLE, DECREASING
    seasonality_factor        = Column(Numeric(5, 2), default=1.00, nullable=False)
    average_sell_through_days = Column(Integer, nullable=False)
    last_updated              = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="demand_profiles")


class WarehouseTransferMatrix(Base):
    __tablename__ = "warehouse_transfer_matrix"

    id                       = Column(Uuid, primary_key=True, default=uuid.uuid4)
    source_warehouse_id      = Column(String(50), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    destination_warehouse_id = Column(String(50), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False)
    distance_km              = Column(Numeric(10, 2), nullable=False)
    estimated_travel_hours   = Column(Numeric(5, 2), nullable=False)
    fuel_cost                = Column(Numeric(10, 2), nullable=False)
    labour_cost              = Column(Numeric(10, 2), nullable=False)
    handling_cost            = Column(Numeric(10, 2), nullable=False)
    total_transfer_cost      = Column(Numeric(12, 2), nullable=False)
    road_condition_factor    = Column(String(50), default="GOOD", nullable=False)  # GOOD, MODERATE, POOR
    created_at               = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SupplierReturnPolicy(Base):
    __tablename__ = "supplier_return_policies"

    id                           = Column(Uuid, primary_key=True, default=uuid.uuid4)
    supplier_id                  = Column(String(100), unique=True, nullable=False)  # e.g., "Amul", "Britannia"
    return_allowed               = Column(Boolean, default=True, nullable=False)
    return_window_days           = Column(Integer, nullable=False)
    maximum_return_percentage    = Column(Numeric(5, 2), nullable=False)
    minimum_remaining_shelf_life = Column(Integer, nullable=False)
    restocking_fee               = Column(Numeric(10, 2), nullable=False)
    minimum_return_quantity      = Column(Integer, nullable=False)
    maximum_return_quantity      = Column(Integer, nullable=False)
    updated_at                   = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class OptimizationConfiguration(Base):
    __tablename__ = "optimization_configurations"

    id                   = Column(String(50), primary_key=True, default="default")
    financial_weight     = Column(Numeric(5, 2), nullable=False)
    demand_weight        = Column(Numeric(5, 2), nullable=False)
    compatibility_weight = Column(Numeric(5, 2), nullable=False)
    transport_weight     = Column(Numeric(5, 2), nullable=False)
    shelf_life_weight    = Column(Numeric(5, 2), nullable=False)
    supplier_weight      = Column(Numeric(5, 2), nullable=False)
    updated_at           = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

