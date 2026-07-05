"""
community/services/issue_cluster_service.py
Pure business logic for Product Issue Clustering Engine (PICE).
Groups related consumer reports into issue clusters automatically.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.community.models.community_user import CommunityUser
from app.community.models.product_report import ProductReport
from app.community.models.issue_cluster import IssueCluster, ClusterReport, ClusterLocation


def _generate_cluster_code(db: Session) -> str:
    """Generate sequential unique code like IC-2026-000001."""
    year = datetime.now(timezone.utc).year
    prefix = f"IC-{year}-"
    
    # Check count of clusters for this prefix
    count = db.query(func.count(IssueCluster.id)).filter(
        IssueCluster.cluster_code.like(f"{prefix}%")
    ).scalar() or 0
    
    seq = count + 1
    while True:
        code = f"{prefix}{seq:06d}"
        exists = db.query(IssueCluster.id).filter(IssueCluster.cluster_code == code).first() is not None
        if not exists:
            return code
        seq += 1


def calculate_cluster_severity(db: Session, cluster_id: uuid.UUID) -> str:
    """
    Calculate cluster severity based on report count:
    - 1-3 reports: LOW
    - 4-10 reports: MEDIUM
    - 11-25 reports: HIGH
    - 26+ reports: CRITICAL
    """
    count = db.query(ClusterReport).filter(ClusterReport.cluster_id == cluster_id).count()
    if count >= 26:
        return "CRITICAL"
    elif count >= 11:
        return "HIGH"
    elif count >= 4:
        return "MEDIUM"
    return "LOW"


def find_matching_cluster(db: Session, report: ProductReport) -> Optional[IssueCluster]:
    """
    Search existing clusters. Join if:
    - Same barcode (product)
    - Same batch
    - Same report type
    - Report created within 30 days of the cluster's last activity
    """
    cutoff = report.created_at - timedelta(days=30)
    return (
        db.query(IssueCluster)
        .filter(
            IssueCluster.barcode            == report.barcode,
            IssueCluster.batch_number       == report.batch_number,
            IssueCluster.primary_issue_type == report.report_type,
            IssueCluster.last_reported_at   >= cutoff,
        )
        .order_by(IssueCluster.last_reported_at.desc())
        .first()
    )


def create_cluster(db: Session, report: ProductReport) -> IssueCluster:
    """Create a new Issue Cluster starting from a given report."""
    # Find matching master product ID
    prod_id = db.query(Product.id).filter(Product.barcode == report.barcode).scalar()

    code = _generate_cluster_code(db)
    cluster = IssueCluster(
        cluster_code=code,
        reported_product_id=prod_id,
        barcode=report.barcode,
        batch_number=report.batch_number,
        primary_issue_type=report.report_type,
        status="NEW",
        severity="LOW",
        affected_reports_count=0,
        affected_users_count=0,
        affected_cities_count=0,
        first_reported_at=report.created_at,
        last_reported_at=report.created_at,
    )
    db.add(cluster)
    db.commit()
    db.refresh(cluster)
    return cluster


def update_cluster_statistics(db: Session, cluster_id: uuid.UUID) -> None:
    """
    Update metrics (Reports, Users, Cities count, first/last reported date, severity)
    for a given cluster ID. Deletes the cluster if it has no reports left.
    """
    cluster = db.query(IssueCluster).filter(IssueCluster.id == cluster_id).first()
    if not cluster:
        return

    # Fetch all linked reports
    linked_reports = (
        db.query(ProductReport)
        .join(ClusterReport, ClusterReport.report_id == ProductReport.id)
        .filter(ClusterReport.cluster_id == cluster_id)
        .all()
    )

    if not linked_reports:
        # Delete empty cluster
        db.delete(cluster)
        db.commit()
        return

    cluster.affected_reports_count = len(linked_reports)

    # Unique users
    unique_users = {r.user_id for r in linked_reports}
    cluster.affected_users_count = len(unique_users)

    # Rebuild locations metrics
    db.query(ClusterLocation).filter(ClusterLocation.cluster_id == cluster_id).delete()
    
    loc_groups = {}
    for r in linked_reports:
        user = r.user
        country = user.country or "Unknown"
        state = user.state or "Unknown"
        city = user.city or "Unknown"
        key = (country, state, city)
        loc_groups[key] = loc_groups.get(key, 0) + 1

    for (country, state, city), count in loc_groups.items():
        db.add(
            ClusterLocation(
                cluster_id=cluster_id,
                country=country,
                state=state,
                city=city,
                report_count=count,
            )
        )

    # Count unique actual cities
    unique_cities = {city for (country, state, city) in loc_groups.keys() if city != "Unknown"}
    cluster.affected_cities_count = len(unique_cities)

    # Dates
    cluster.first_reported_at = min(r.created_at for r in linked_reports)
    cluster.last_reported_at = max(r.created_at for r in linked_reports)

    # Severity recalculation
    cluster.severity = calculate_cluster_severity(db, cluster_id)

    db.commit()

    # Automatically recalculate intelligence analytics for this cluster
    from app.community.services.community_intelligence_service import recalculate_cluster
    recalculate_cluster(db, cluster_id)

    db.refresh(cluster)


def add_report_to_cluster(db: Session, cluster_id: uuid.UUID, report_id: uuid.UUID) -> ClusterReport:
    """Link a report to a cluster, maintaining single-cluster mapping."""
    existing = db.query(ClusterReport).filter(ClusterReport.report_id == report_id).first()
    if existing:
        if existing.cluster_id == cluster_id:
            return existing
        
        # Move to the new cluster
        old_id = existing.cluster_id
        existing.cluster_id = cluster_id
        existing.linked_at = datetime.now(timezone.utc)
        db.commit()
        update_cluster_statistics(db, old_id)
        update_cluster_statistics(db, cluster_id)
        return existing

    link = ClusterReport(cluster_id=cluster_id, report_id=report_id)
    db.add(link)
    db.commit()
    update_cluster_statistics(db, cluster_id)
    return link


def remove_report_from_cluster(db: Session, report_id: uuid.UUID) -> None:
    """Unlink a report from its cluster (e.g. on report delete)."""
    link = db.query(ClusterReport).filter(ClusterReport.report_id == report_id).first()
    if link:
        cluster_id = link.cluster_id
        db.delete(link)
        db.commit()
        update_cluster_statistics(db, cluster_id)


def get_cluster(db: Session, cluster_id: uuid.UUID) -> IssueCluster:
    """Fetch single cluster details. Raises 404 if not found."""
    from fastapi import HTTPException
    cluster = db.query(IssueCluster).filter(IssueCluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "CLUSTER_NOT_FOUND",
                "message": f"Issue cluster '{cluster_id}' not found.",
            },
        )
    return cluster


def list_clusters(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    barcode: Optional[str] = None,
    batch: Optional[str] = None,
    product: Optional[str] = None,
    city: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[IssueCluster]:
    """Search and filter issue clusters."""
    query = db.query(IssueCluster)

    if status:
        query = query.filter(IssueCluster.status == status)
    if severity:
        query = query.filter(IssueCluster.severity == severity)
    if barcode:
        query = query.filter(IssueCluster.barcode == barcode)
    if batch:
        query = query.filter(IssueCluster.batch_number == batch)
        
    if product:
        query = query.join(Product, Product.id == IssueCluster.reported_product_id).filter(
            Product.name.ilike(f"%{product}%")
        )
        
    if city:
        query = query.join(ClusterLocation, ClusterLocation.cluster_id == IssueCluster.id).filter(
            ClusterLocation.city.ilike(city)
        )
        
    if date_from:
        query = query.filter(IssueCluster.last_reported_at >= date_from)
    if date_to:
        query = query.filter(IssueCluster.last_reported_at <= date_to)

    return query.order_by(IssueCluster.last_reported_at.desc()).offset(skip).limit(limit).all()


def rebuild_all_clusters(db: Session) -> int:
    """Clear all clusters and rebuild them chronologically from all existing reports."""
    db.query(ClusterReport).delete()
    db.query(ClusterLocation).delete()
    db.query(IssueCluster).delete()
    db.commit()

    reports = db.query(ProductReport).order_by(ProductReport.created_at.asc()).all()
    count = 0
    for r in reports:
        cluster = find_matching_cluster(db, r)
        if not cluster:
            cluster = create_cluster(db, r)
        add_report_to_cluster(db, cluster.id, r.id)
        count += 1
    return count


def get_statistics(db: Session) -> Dict[str, Any]:
    """Compiles summary stats across all issue clusters."""
    total = db.query(func.count(IssueCluster.id)).scalar() or 0
    
    # Status breakdown counts
    states = ["NEW", "MONITORING", "ACTIVE", "RESOLVED"]
    counts_map = {s: 0 for s in states}
    
    status_counts = db.query(
        IssueCluster.status, func.count(IssueCluster.id)
    ).group_by(IssueCluster.status).all()
    
    for s, count in status_counts:
        if s in counts_map:
            counts_map[s] = count
            
    avg_reports = db.query(func.avg(IssueCluster.affected_reports_count)).scalar() or 0.0
    
    # Largest cluster
    largest = db.query(IssueCluster).order_by(
        IssueCluster.affected_reports_count.desc()
    ).first()
    largest_code = largest.cluster_code if largest else None
    
    # Most reported product
    most_reported = db.query(
        IssueCluster.barcode, func.sum(IssueCluster.affected_reports_count)
    ).group_by(IssueCluster.barcode).order_by(
        func.sum(IssueCluster.affected_reports_count).desc()
    ).first()
    most_reported_barcode = most_reported[0] if most_reported else None

    return {
        "total_clusters": total,
        "new": counts_map["NEW"],
        "monitoring": counts_map["MONITORING"],
        "active": counts_map["ACTIVE"],
        "resolved": counts_map["RESOLVED"],
        "average_reports_per_cluster": round(float(avg_reports), 2),
        "largest_cluster": largest_code,
        "most_reported_product": most_reported_barcode,
    }
