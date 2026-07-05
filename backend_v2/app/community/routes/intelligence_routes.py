"""
community/routes/intelligence_routes.py
HTTP routes for PGN Community Intelligence Engine (CIE).
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.schemas.intelligence_schemas import (
    ClusterIntelligenceResponse,
    ClusterDashboardResponse,
)
from app.community.services import community_intelligence_service
from app.community.models.cluster_intelligence import ClusterIntelligence
from app.community.models.issue_cluster import IssueCluster

router = APIRouter(prefix="/intelligence", tags=["Community Intelligence Engine"])


@router.get(
    "",
    response_model=List[ClusterIntelligenceResponse],
    summary="List and filter cluster intelligence profiles",
)
def list_intelligence_profiles(
    risk_score: Optional[int] = Query(None, description="Filter for risk score greater or equal"),
    trend: Optional[str] = Query(None, description="Filter by trend (STABLE, GROWING, etc)"),
    activity: Optional[str] = Query(None, description="Filter by activity level"),
    spread: Optional[str] = Query(None, description="Filter by spread level"),
    escalation: Optional[str] = Query(None, description="Filter by escalation level"),
    severity: Optional[str] = Query(None, description="Filter by cluster severity"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[ClusterIntelligenceResponse]:
    """Get all issue cluster intelligence records matching specified filters."""
    return community_intelligence_service.list_intelligence(
        db,
        risk_score=risk_score,
        trend=trend,
        activity=activity,
        spread=spread,
        escalation=escalation,
        severity=severity,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/dashboard",
    response_model=ClusterDashboardResponse,
    summary="Get intelligence dashboard statistics",
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
) -> ClusterDashboardResponse:
    """
    Retrieve compiled statistics for the Community Intelligence dashboard:
    Highest Risk, Fastest Growing, Most Active, Newest, and Dormant clusters.
    """
    return community_intelligence_service.get_dashboard_statistics(db)


@router.post(
    "/recalculate",
    summary="Recalculate all cluster intelligence records",
    status_code=status.HTTP_200_OK,
)
def force_recalculate_all(
    db: Session = Depends(get_db),
):
    """Force re-calculation of growth, risk, activity, and spread across all clusters."""
    processed = community_intelligence_service.recalculate_all_clusters(db)
    return {
        "success": True,
        "message": f"Successfully recalculated intelligence profile for {processed} issue clusters.",
        "recalculated_count": processed,
    }


@router.get(
    "/trending",
    response_model=List[ClusterIntelligenceResponse],
    summary="List currently trending clusters",
)
def get_trending_clusters(
    db: Session = Depends(get_db),
) -> List[ClusterIntelligenceResponse]:
    """List all clusters marked as trending due to high recent growth or reports volumes."""
    return db.query(ClusterIntelligence).filter(ClusterIntelligence.is_trending == True).order_by(
        ClusterIntelligence.risk_score.desc()
    ).all()


@router.get(
    "/high-risk",
    response_model=List[ClusterIntelligenceResponse],
    summary="List high risk clusters",
)
def get_high_risk_clusters(
    db: Session = Depends(get_db),
) -> List[ClusterIntelligenceResponse]:
    """List all clusters with high risk scores (Risk >= 50), sorted by risk descending."""
    return db.query(ClusterIntelligence).filter(ClusterIntelligence.risk_score >= 50).order_by(
        ClusterIntelligence.risk_score.desc()
    ).all()


@router.get(
    "/dormant",
    response_model=List[ClusterIntelligenceResponse],
    summary="List dormant clusters",
)
def get_dormant_clusters(
    db: Session = Depends(get_db),
) -> List[ClusterIntelligenceResponse]:
    """List all clusters that are currently dormant (0 reports in the last 30 days)."""
    return db.query(ClusterIntelligence).filter(ClusterIntelligence.activity_level == "DORMANT").all()


@router.get(
    "/{cluster_id}",
    response_model=ClusterIntelligenceResponse,
    summary="Get intelligence profile for a specific cluster",
    responses={404: {"description": "Cluster not found"}},
)
def get_cluster_intelligence(
    cluster_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> ClusterIntelligenceResponse:
    """Fetch the intelligence record for a specific cluster by UUID. Automatically calculates if missing."""
    # Ensure cluster exists
    exists = db.query(IssueCluster.id).filter(IssueCluster.id == cluster_id).scalar() is not None
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CLUSTER_NOT_FOUND",
                "message": f"Issue cluster '{cluster_id}' not found.",
            },
        )
    return community_intelligence_service.get_cluster_intelligence(db, cluster_id)
