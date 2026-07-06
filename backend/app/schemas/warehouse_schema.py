"""
schemas/warehouse_schema.py — Pydantic schemas for Warehouse Intelligence responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class WarehouseResponse(BaseModel):
    id: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class TransportCostConfigurationResponse(BaseModel):
    id: str
    fuel_cost_per_km: Decimal
    labour_cost_per_hour: Decimal
    good_handling_cost: Decimal
    moderate_handling_cost: Decimal
    poor_handling_cost: Decimal
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseConfigurationResponse(BaseModel):
    id: uuid.UUID
    warehouse_id: str
    warehouse_capacity: int
    warehouse_operating_hours: str
    maximum_daily_dispatch: int
    cold_storage_available: bool
    temperature_control: bool
    priority_level: str

    model_config = ConfigDict(from_attributes=True)


class WarehouseDemandProfileResponse(BaseModel):
    id: uuid.UUID
    warehouse_id: str
    product_category: str
    average_daily_demand: Decimal
    average_weekly_demand: Decimal
    average_monthly_demand: Decimal
    demand_trend: str
    seasonality_factor: Decimal
    average_sell_through_days: int
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class WarehouseTransferMatrixResponse(BaseModel):
    id: uuid.UUID
    source_warehouse_id: str
    destination_warehouse_id: str
    distance_km: Decimal
    estimated_travel_hours: Decimal
    fuel_cost: Decimal
    labour_cost: Decimal
    handling_cost: Decimal
    total_transfer_cost: Decimal
    road_condition_factor: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplierReturnPolicyResponse(BaseModel):
    id: uuid.UUID
    supplier_id: str
    return_allowed: bool
    return_window_days: int
    maximum_return_percentage: Decimal
    minimum_remaining_shelf_life: int
    restocking_fee: Decimal
    minimum_return_quantity: int
    maximum_return_quantity: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
