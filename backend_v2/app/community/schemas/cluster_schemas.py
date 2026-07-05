"""
community/schemas/cluster_schemas.py
Pydantic schemas for Product Issue Clustering Engine (PICE).
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict


class ClusterLocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    country: str
    state: str
    city: str
    report_count: int


class IssueClusterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cluster_code: str
    reported_product_id: Optional[uuid.UUID]
    barcode: str
    batch_number: str
    primary_issue_type: str
    status: str
    severity: str
    affected_reports_count: int
    affected_users_count: int
    affected_cities_count: int
    first_reported_at: datetime
    last_reported_at: datetime
    created_at: datetime
    updated_at: datetime
    locations: List[ClusterLocationResponse] = []


class IssueClusterSummary(BaseModel):
    total_clusters: int
    new: int
    monitoring: int
    active: int
    resolved: int
    average_reports_per_cluster: float
    largest_cluster: Optional[str]        # code of largest cluster
    most_reported_product: Optional[str]  # barcode of most reported product
