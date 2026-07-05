"""
community/routes/cluster_routes.py
HTTP routes for Product Issue Clustering Engine (PICE).
"""
import uuid
from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.community.schemas.cluster_schemas import (
    IssueClusterResponse,
    IssueClusterSummary,
)
from app.community.schemas.report_schemas import ProductReportResponse
from app.community.services import issue_cluster_service
from app.community.models.issue_cluster import IssueCluster, ClusterReport

router = APIRouter(tags=["Product Issue Clustering Engine"])


@router.get(
    "/clusters",
    response_model=List[IssueClusterResponse],
    summary="List issue clusters with filtering",
)
def list_clusters(
    status: Optional[str] = Query(None, description="Filter by cluster status"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    barcode: Optional[str] = Query(None, description="Filter by product barcode"),
    batch: Optional[str] = Query(None, description="Filter by batch number"),
    product: Optional[str] = Query(None, description="Filter by product name substring"),
    city: Optional[str] = Query(None, description="Filter by affected city"),
    date_from: Optional[datetime] = Query(None, description="Filter clusters active from this datetime"),
    date_to: Optional[datetime] = Query(None, description="Filter clusters active until this datetime"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[IssueClusterResponse]:
    """Get a paginated list of issue clusters matching query filters."""
    return issue_cluster_service.list_clusters(
        db,
        status=status,
        severity=severity,
        barcode=barcode,
        batch=batch,
        product=product,
        city=city,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/clusters/statistics",
    response_model=IssueClusterSummary,
    summary="Get global issue cluster statistics",
)
def get_global_statistics(
    db: Session = Depends(get_db),
) -> IssueClusterSummary:
    """Compile global statistics across all issue clusters."""
    return issue_cluster_service.get_statistics(db)


@router.get(
    "/clusters/{cluster_id}/statistics",
    response_model=IssueClusterSummary,
    summary="Get issue cluster statistics (aliased to global stats)",
)
def get_cluster_statistics_alias(
    cluster_id: str,  # String to allow '/statistics' or UUIDs
    db: Session = Depends(get_db),
) -> IssueClusterSummary:
    """
    Alias path matching either specific cluster requests or global requests.
    Returns the PICE global statistics.
    """
    return issue_cluster_service.get_statistics(db)


@router.get(
    "/clusters/code/{cluster_code}",
    response_model=IssueClusterResponse,
    summary="Get single issue cluster by code",
    responses={404: {"description": "Cluster not found"}},
)
def get_cluster_by_code(
    cluster_code: str,
    db: Session = Depends(get_db),
) -> IssueClusterResponse:
    """Retrieve details of a single cluster by its unique code (e.g. IC-2026-000001)."""
    cluster = db.query(IssueCluster).filter(IssueCluster.cluster_code == cluster_code).first()
    if not cluster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "CLUSTER_NOT_FOUND",
                "message": f"Issue cluster with code '{cluster_code}' not found.",
            },
        )
    return cluster


@router.get(
    "/clusters/product/{barcode}",
    response_model=List[IssueClusterResponse],
    summary="Get clusters for a specific barcode",
)
def get_clusters_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
) -> List[IssueClusterResponse]:
    """Retrieve all issue clusters related to a specific product barcode."""
    return db.query(IssueCluster).filter(IssueCluster.barcode == barcode).order_by(
        IssueCluster.last_reported_at.desc()
    ).all()


@router.get(
    "/clusters/{cluster_id}",
    response_model=IssueClusterResponse,
    summary="Get single issue cluster by ID",
    responses={404: {"description": "Cluster not found"}},
)
def get_cluster_by_id(
    cluster_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> IssueClusterResponse:
    """Retrieve details of a single cluster by its UUID."""
    return issue_cluster_service.get_cluster(db, cluster_id)


@router.get(
    "/clusters/{cluster_id}/reports",
    response_model=List[ProductReportResponse],
    summary="Get all reports in a cluster",
    responses={404: {"description": "Cluster not found"}},
)
def get_reports_in_cluster(
    cluster_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> List[ProductReportResponse]:
    """Retrieve a list of all consumer reports currently grouped within this cluster."""
    # Verify cluster exists
    issue_cluster_service.get_cluster(db, cluster_id)
    
    # Query linked reports
    links = db.query(ClusterReport).filter(ClusterReport.cluster_id == cluster_id).all()
    return [l.report for l in links]


@router.post(
    "/clusters/recalculate",
    summary="Rebuild issue clusters index from scratch",
    status_code=status.HTTP_200_OK,
)
def recalculate_clusters(
    db: Session = Depends(get_db),
):
    """
    Clear all issue clusters, mappings, and location summaries, and completely 
    re-evaluate all consumer reports chronologically to rebuild the clusters index.
    """
    rebuilt_count = issue_cluster_service.rebuild_all_clusters(db)
    return {
        "success": True,
        "message": f"Successfully cleared and rebuilt issue clusters index using {rebuilt_count} reports.",
        "processed_reports_count": rebuilt_count
    }
