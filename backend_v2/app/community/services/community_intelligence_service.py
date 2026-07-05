"""
community/services/community_intelligence_service.py
Pure business logic for the PGN Community Intelligence Engine (CIE).
Computes risk, trend, activity, and spread analysis for all clusters dynamically.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.community.models.community_user import CommunityUser
from app.community.models.issue_cluster import IssueCluster, ClusterReport, ClusterLocation
from app.community.models.product_report import ProductReport
from app.community.models.report_credibility import ReportCredibility
from app.community.models.cluster_intelligence import ClusterIntelligence


def calculate_growth_rate(db: Session, cluster_id: uuid.UUID) -> float:
    """
    Compare reports in the last 24 hours vs the previous 24 hours.
    Returns the growth percentage.
    """
    now_utc = datetime.now(timezone.utc)
    t24h = now_utc - timedelta(hours=24)
    t48h = now_utc - timedelta(hours=48)

    # Today's reports
    today_count = (
        db.query(ClusterReport)
        .join(ProductReport, ProductReport.id == ClusterReport.report_id)
        .filter(
            ClusterReport.cluster_id == cluster_id,
            ProductReport.created_at >= t24h,
        )
        .count()
    )

    # Yesterday's reports
    yesterday_count = (
        db.query(ClusterReport)
        .join(ProductReport, ProductReport.id == ClusterReport.report_id)
        .filter(
            ClusterReport.cluster_id == cluster_id,
            ProductReport.created_at >= t48h,
            ProductReport.created_at < t24h,
        )
        .count()
    )

    if yesterday_count == 0:
        if today_count == 0:
            return 0.0
        return float(today_count * 100.0)

    growth = ((today_count - yesterday_count) / yesterday_count) * 100.0
    return round(float(growth), 2)


def calculate_trend(growth_rate: float) -> str:
    """
    Determine trend label from growth percentage:
    - Growth < -20%: DECLINING
    - -20% to +20%: STABLE
    - 20% to 75%: GROWING
    - Above 75%: RAPIDLY_GROWING
    """
    if growth_rate < -20.0:
        return "DECLINING"
    elif growth_rate <= 20.0:
        return "STABLE"
    elif growth_rate <= 75.0:
        return "GROWING"
    return "RAPIDLY_GROWING"


def calculate_spread(cities_count: int) -> str:
    """
    Determine spread level based on number of cities:
    - 1 city: LOCAL
    - 2-5 cities: REGIONAL
    - 6-10 cities: MULTI_REGION
    - More than 10 cities: NATIONAL
    """
    if cities_count <= 1:
        return "LOCAL"
    elif cities_count <= 5:
        return "REGIONAL"
    elif cities_count <= 10:
        return "MULTI_REGION"
    return "NATIONAL"


def calculate_risk_score(
    severity: str,
    avg_credibility: float,
    trend: str,
    spread: str,
    reports_count: int,
    reports_last_24h: int,
) -> int:
    """
    Calculate risk score between 0 and 100 based on severity, credibility, trend, and spread.
    """
    score = 0

    # 1. Severity points
    if severity == "CRITICAL":
        score += 60
    elif severity == "HIGH":
        score += 40
    elif severity == "MEDIUM":
        score += 25
    else:  # LOW
        score += 10

    # 2. Credibility points
    if avg_credibility >= 90.0:
        score += 20
    elif avg_credibility >= 75.0:
        score += 15
    elif avg_credibility >= 50.0:
        score += 10

    # 3. Growth trend points
    if trend == "RAPIDLY_GROWING":
        score += 20
    elif trend == "GROWING":
        score += 10
    elif trend == "STABLE":
        score += 5

    # 4. Spread level points
    if spread == "NATIONAL":
        score += 20
    elif spread == "MULTI_REGION":
        score += 10
    elif spread == "REGIONAL":
        score += 5

    # 5. Volume weighting
    score += int(min(reports_count * 0.5, 10))
    score += int(min(reports_last_24h * 2, 10))

    return max(0, min(score, 100))


def calculate_activity(reports_last_30_days: int, reports_last_7_days: int) -> str:
    """
    Determine activity level based on recent time frames:
    - 0 reports in last 30 days: DORMANT
    - 0 in last 7 days: LOW
    - 1-3 in last 7 days: MODERATE
    - 4-10 in last 7 days: HIGH
    - More than 10: CRITICAL
    """
    if reports_last_30_days == 0:
        return "DORMANT"
    
    if reports_last_7_days == 0:
        return "LOW"
    elif reports_last_7_days <= 3:
        return "MODERATE"
    elif reports_last_7_days <= 10:
        return "HIGH"
    return "CRITICAL"


def calculate_escalation(risk_score: int) -> str:
    """
    Determine escalation level based on risk score:
    - Risk < 25: NONE
    - Risk 25-49: WATCH
    - Risk 50-74: INVESTIGATE
    - Risk 75-89: URGENT
    - Risk 90+: CRITICAL
    """
    if risk_score < 25:
        return "NONE"
    elif risk_score < 50:
        return "WATCH"
    elif risk_score < 75:
        return "INVESTIGATE"
    elif risk_score < 90:
        return "URGENT"
    return "CRITICAL"


def recalculate_cluster(db: Session, cluster_id: uuid.UUID) -> ClusterIntelligence:
    """
    Re-evaluate risk score, growth trend, activity level, spread level,
    and escalation tags for a cluster.
    """
    cluster = db.query(IssueCluster).filter(IssueCluster.id == cluster_id).first()
    if not cluster:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Issue cluster '{cluster_id}' not found.")

    now_utc = datetime.now(timezone.utc)
    t24h = now_utc - timedelta(hours=24)
    t7d = now_utc - timedelta(days=7)
    t30d = now_utc - timedelta(days=30)

    # 1. Calculate time frame report volumes
    r_24h = db.query(ClusterReport).join(ProductReport).filter(
        ClusterReport.cluster_id == cluster_id, ProductReport.created_at >= t24h
    ).count()

    r_7d = db.query(ClusterReport).join(ProductReport).filter(
        ClusterReport.cluster_id == cluster_id, ProductReport.created_at >= t7d
    ).count()

    r_30d = db.query(ClusterReport).join(ProductReport).filter(
        ClusterReport.cluster_id == cluster_id, ProductReport.created_at >= t30d
    ).count()

    # 2. Count new cities (with reports created in last 7 days)
    new_cities = (
        db.query(func.count(func.distinct(CommunityUser.city)))
        .join(ProductReport, ProductReport.user_id == CommunityUser.id)
        .join(ClusterReport, ClusterReport.report_id == ProductReport.id)
        .filter(
            ClusterReport.cluster_id == cluster_id,
            ProductReport.created_at >= t7d,
            CommunityUser.city != "Unknown"
        )
        .scalar() or 0
    )

    # 3. Average Credibility score
    avg_cred = (
        db.query(func.avg(ReportCredibility.score))
        .join(ProductReport, ProductReport.id == ReportCredibility.report_id)
        .join(ClusterReport, ClusterReport.report_id == ProductReport.id)
        .filter(ClusterReport.cluster_id == cluster_id)
        .scalar() or 0.0
    )
    avg_cred = round(float(avg_cred), 2)

    # 4. Apply metric calculations
    growth = calculate_growth_rate(db, cluster_id)
    trend = calculate_trend(growth)
    spread = calculate_spread(cluster.affected_cities_count)
    activity = calculate_activity(r_30d, r_7d)
    
    risk = calculate_risk_score(
        cluster.severity, avg_cred, trend, spread,
        cluster.affected_reports_count, r_24h
    )
    escalation = calculate_escalation(risk)

    is_trending = (trend in ("GROWING", "RAPIDLY_GROWING")) or (r_24h >= 2)

    intelligence = db.query(ClusterIntelligence).filter(
        ClusterIntelligence.cluster_id == cluster_id
    ).first()

    if not intelligence:
        intelligence = ClusterIntelligence(
            cluster_id=cluster_id,
            risk_score=risk,
            growth_rate=growth,
            activity_level=activity,
            trend=trend,
            spread_level=spread,
            escalation_level=escalation,
            reports_last_24h=r_24h,
            reports_last_7_days=r_7d,
            reports_last_30_days=r_30d,
            new_cities=new_cities,
            average_credibility=avg_cred,
            is_trending=is_trending,
            last_calculated=now_utc,
        )
        db.add(intelligence)
    else:
        intelligence.risk_score = risk
        intelligence.growth_rate = growth
        intelligence.activity_level = activity
        intelligence.trend = trend
        intelligence.spread_level = spread
        intelligence.escalation_level = escalation
        intelligence.reports_last_24h = r_24h
        intelligence.reports_last_7_days = r_7d
        intelligence.reports_last_30_days = r_30d
        intelligence.new_cities = new_cities
        intelligence.average_credibility = avg_cred
        intelligence.is_trending = is_trending
        intelligence.last_calculated = now_utc

    db.commit()

    # Automatically evaluate safety alerts threshold rules for this cluster
    from app.community.services.community_alert_service import evaluate_cluster
    evaluate_cluster(db, cluster_id)

    db.refresh(intelligence)
    return intelligence


def recalculate_all_clusters(db: Session) -> int:
    """Force re-calculation across all clusters."""
    clusters = db.query(IssueCluster.id).all()
    count = 0
    for c in clusters:
        recalculate_cluster(db, c.id)
        count += 1
    return count


def get_cluster_intelligence(db: Session, cluster_id: uuid.UUID) -> ClusterIntelligence:
    """Fetch intelligence profile for a cluster, generating if missing."""
    intel = db.query(ClusterIntelligence).filter(
        ClusterIntelligence.cluster_id == cluster_id
    ).first()
    if not intel:
        intel = recalculate_cluster(db, cluster_id)
    return intel


def get_dashboard_statistics(db: Session) -> Dict[str, Any]:
    """Compiles dashboard metrics of critical groups (high risk, trending, dormant)."""
    # 1. Highest Risk
    highest_risk = (
        db.query(IssueCluster)
        .join(ClusterIntelligence, ClusterIntelligence.cluster_id == IssueCluster.id)
        .order_by(ClusterIntelligence.risk_score.desc())
        .first()
    )

    # 2. Fastest Growing
    fastest_growing = (
        db.query(IssueCluster)
        .join(ClusterIntelligence, ClusterIntelligence.cluster_id == IssueCluster.id)
        .order_by(ClusterIntelligence.growth_rate.desc())
        .first()
    )

    # 3. Most Active (highest reports count in last 7 days)
    most_active = (
        db.query(IssueCluster)
        .join(ClusterIntelligence, ClusterIntelligence.cluster_id == IssueCluster.id)
        .order_by(ClusterIntelligence.reports_last_7_days.desc())
        .first()
    )

    # 4. Newest Cluster
    newest_cluster = db.query(IssueCluster).order_by(IssueCluster.created_at.desc()).first()

    # 5. Dormant Clusters
    dormant_clusters = (
        db.query(IssueCluster)
        .join(ClusterIntelligence, ClusterIntelligence.cluster_id == IssueCluster.id)
        .filter(ClusterIntelligence.activity_level == "DORMANT")
        .limit(5)
        .all()
    )

    return {
        "highest_risk": highest_risk,
        "fastest_growing": fastest_growing,
        "most_active": most_active,
        "newest_cluster": newest_cluster,
        "dormant_clusters": dormant_clusters,
    }


def list_intelligence(
    db: Session,
    risk_score: Optional[int] = None,
    trend: Optional[str] = None,
    activity: Optional[str] = None,
    spread: Optional[str] = None,
    escalation: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[ClusterIntelligence]:
    """Search and filter intelligence profiles."""
    query = db.query(ClusterIntelligence)

    if risk_score is not None:
        query = query.filter(ClusterIntelligence.risk_score >= risk_score)
    if trend:
        query = query.filter(ClusterIntelligence.trend == trend)
    if activity:
        query = query.filter(ClusterIntelligence.activity_level == activity)
    if spread:
        query = query.filter(ClusterIntelligence.spread_level == spread)
    if escalation:
        query = query.filter(ClusterIntelligence.escalation_level == escalation)
    if severity:
        query = query.join(IssueCluster).filter(IssueCluster.severity == severity)

    return query.order_by(ClusterIntelligence.risk_score.desc()).offset(skip).limit(limit).all()
