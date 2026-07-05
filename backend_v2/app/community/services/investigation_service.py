"""
community/services/investigation_service.py
Pure business logic for PGN Investigation & Case Management Engine (ICME).
Handles creation, assignments, notes, evidence, audit timelines, and case resolution.
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.community.models.safety_alert import SafetyAlert
from app.community.models.cluster_intelligence import ClusterIntelligence
from app.community.models.investigation import InvestigationCase, InvestigationNote, CaseEvidence, CaseTimeline


def _generate_case_number(db: Session) -> str:
    """Generate unique sequential case numbers like CASE-2026-000001."""
    year = datetime.now(timezone.utc).year
    prefix = f"CASE-{year}-"
    
    count = db.query(func.count(InvestigationCase.id)).filter(
        InvestigationCase.case_number.like(f"{prefix}%")
    ).scalar() or 0
    
    seq = count + 1
    while True:
        code = f"{prefix}{seq:06d}"
        exists = db.query(InvestigationCase.id).filter(InvestigationCase.case_number == code).first() is not None
        if not exists:
            return code
        seq += 1


def create_timeline_event(
    db: Session, case_id: uuid.UUID, event_type: str, event_description: str, performed_by: str
) -> CaseTimeline:
    """Save an audit trail event for the investigation timeline."""
    event = CaseTimeline(
        case_id=case_id,
        event_type=event_type,
        event_description=event_description,
        performed_by=performed_by,
        created_at=datetime.now(timezone.utc)
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def create_case(
    db: Session, alert_id: uuid.UUID, title: str, description: str,
    due_date: Optional[datetime] = None, priority: str = "MEDIUM"
) -> InvestigationCase:
    """Initialize an investigation case for a qualifying High Risk or Critical alert."""
    alert = db.query(SafetyAlert).filter(SafetyAlert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Safety alert '{alert_id}' not found.")

    # Rule: Only HIGH_RISK or CRITICAL alerts can spin up cases
    if alert.alert_level not in ("HIGH_RISK", "CRITICAL"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INELIGIBLE_ALERT_LEVEL",
                "message": f"Cannot start investigation for alert level '{alert.alert_level}'. Only HIGH_RISK or CRITICAL alerts qualify."
            }
        )

    # Rule: One active case per alert
    existing_active = db.query(InvestigationCase).filter(
        InvestigationCase.alert_id == alert_id,
        InvestigationCase.status.notin_(["RESOLVED", "CLOSED"])
    ).first()
    
    if existing_active:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail={
                "error": "ACTIVE_CASE_EXISTS",
                "message": f"An active investigation case '{existing_active.case_number}' already exists for this alert."
            }
        )

    case_num = _generate_case_number(db)
    case = InvestigationCase(
        case_number=case_num,
        alert_id=alert_id,
        cluster_id=alert.cluster_id,
        priority=priority,
        status="OPEN",
        title=title,
        description=description,
        opened_at=datetime.now(timezone.utc),
        due_date=due_date,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Audit timeline event
    create_timeline_event(
        db,
        case_id=case.id,
        event_type="Investigation Created",
        event_description="Case automatically spawned based on qualifying threshold safety alert.",
        performed_by="SYSTEM",
    )

    return case


def assign_case(db: Session, case_id: uuid.UUID, officer: str) -> InvestigationCase:
    """Assign case to a designated officer and update status."""
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' not found.")

    case.assigned_officer = officer
    
    if case.status == "OPEN":
        case.status = "ASSIGNED"

    create_timeline_event(
        db,
        case_id=case.id,
        event_type="Case Assigned",
        event_description=f"Case assigned to officer: {officer}. Status updated to ASSIGNED.",
        performed_by="SYSTEM",
    )
    
    db.commit()
    db.refresh(case)
    return case


def update_status(db: Session, case_id: uuid.UUID, status: str, remarks: Optional[str] = None) -> InvestigationCase:
    """Transition case status and record timeline entry."""
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' not found.")

    old_status = case.status
    case.status = status

    create_timeline_event(
        db,
        case_id=case.id,
        event_type="Status Updated",
        event_description=f"Status transitioned from {old_status} to {status}. Remarks: {remarks or 'None'}.",
        performed_by="SYSTEM",
    )

    db.commit()
    db.refresh(case)
    return case


def resolve_case(
    db: Session, case_id: uuid.UUID, resolution: str, final_decision: str, performed_by: str
) -> InvestigationCase:
    """Mark case as RESOLVED and record decision analysis."""
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' not found.")

    case.status = "RESOLVED"
    case.resolution = resolution
    case.final_decision = final_decision

    create_timeline_event(
        db,
        case_id=case.id,
        event_type="Case Resolved",
        event_description=f"Investigation completed with decision: {final_decision}. Resolution summary: {resolution}.",
        performed_by=performed_by,
    )

    db.commit()
    db.refresh(case)
    return case


def close_case(db: Session, case_id: uuid.UUID, performed_by: str) -> InvestigationCase:
    """Close case, log timeline entry, and auto-close the alert if no active risk remains."""
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' not found.")

    case.status = "CLOSED"
    case.closed_at = datetime.now(timezone.utc)

    create_timeline_event(
        db,
        case_id=case.id,
        event_type="Case Closed",
        event_description="Investigation case has been officially closed.",
        performed_by=performed_by,
    )

    # Rule: Case closed -> Auto mark alert CLOSED if no active risk exists
    alert = db.query(SafetyAlert).filter(SafetyAlert.id == case.alert_id).first()
    if alert:
        intel = db.query(ClusterIntelligence).filter(ClusterIntelligence.cluster_id == case.cluster_id).first()
        # If risk score fell below 75, we close the alert
        if not intel or intel.risk_score < 75:
            from app.community.services.community_alert_service import close_alert
            close_alert(db, alert.id, remarks="Automatically closed safety alert as associated investigation closed with resolved risk.")

    db.commit()
    db.refresh(case)
    return case


def add_note(db: Session, case_id: uuid.UUID, note_text: str, created_by: str) -> InvestigationNote:
    """Append a textual note log to the case case history."""
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' not found.")

    note = InvestigationNote(
        case_id=case_id,
        note=note_text,
        created_by=created_by,
        created_at=datetime.now(timezone.utc)
    )
    db.add(note)
    
    # Audit log
    create_timeline_event(
        db,
        case_id=case_id,
        event_type="Note Added",
        event_description=f"New analysis note recorded by {created_by}.",
        performed_by=created_by,
    )

    db.commit()
    db.refresh(note)
    return note


def upload_evidence(
    db: Session, case_id: uuid.UUID, evidence_type: str, file_url: str, description: str, uploaded_by: str
) -> CaseEvidence:
    """Attach evidence file URLs and logs to the case folder."""
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Investigation case '{case_id}' not found.")

    evidence = CaseEvidence(
        case_id=case_id,
        evidence_type=evidence_type,
        file_url=file_url,
        description=description,
        uploaded_by=uploaded_by,
        uploaded_at=datetime.now(timezone.utc)
    )
    db.add(evidence)
    
    # Audit log
    create_timeline_event(
        db,
        case_id=case_id,
        event_type="Evidence Uploaded",
        event_description=f"Uploaded evidence ({evidence_type}): {description}.",
        performed_by=uploaded_by,
    )

    db.commit()
    db.refresh(evidence)
    return evidence


def get_case(db: Session, case_id: uuid.UUID) -> InvestigationCase:
    """Fetch single case profile. Raises 404 if not found."""
    from fastapi import HTTPException
    case = db.query(InvestigationCase).filter(InvestigationCase.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "CASE_NOT_FOUND",
                "message": f"Investigation case '{case_id}' not found.",
            },
        )
    return case


def list_cases(
    db: Session,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    assigned_officer: Optional[str] = None,
    cluster_id: Optional[uuid.UUID] = None,
    alert_id: Optional[uuid.UUID] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[InvestigationCase]:
    """Search and filter investigation cases."""
    query = db.query(InvestigationCase)

    if priority:
        query = query.filter(InvestigationCase.priority == priority)
    if status:
        query = query.filter(InvestigationCase.status == status)
    if assigned_officer:
        query = query.filter(InvestigationCase.assigned_officer == assigned_officer)
    if cluster_id:
        query = query.filter(InvestigationCase.cluster_id == cluster_id)
    if alert_id:
        query = query.filter(InvestigationCase.alert_id == alert_id)
        
    if date_from:
        query = query.filter(InvestigationCase.created_at >= date_from)
    if date_to:
        query = query.filter(InvestigationCase.created_at <= date_to)

    return query.order_by(InvestigationCase.created_at.desc()).offset(skip).limit(limit).all()


def get_dashboard_statistics(db: Session) -> Dict[str, Any]:
    """Compile case dashboard KPIs."""
    total = db.query(func.count(InvestigationCase.id)).scalar() or 0
    
    open_statuses = ["OPEN", "ASSIGNED", "UNDER_INVESTIGATION", "WAITING_FOR_INFORMATION"]
    open_cases = db.query(func.count(InvestigationCase.id)).filter(
        InvestigationCase.status.in_(open_statuses)
    ).scalar() or 0

    critical_cases = db.query(func.count(InvestigationCase.id)).filter(
        InvestigationCase.priority == "CRITICAL"
    ).scalar() or 0

    assigned_statuses = ["ASSIGNED", "UNDER_INVESTIGATION"]
    assigned_cases = db.query(func.count(InvestigationCase.id)).filter(
        InvestigationCase.status.in_(assigned_statuses)
    ).scalar() or 0

    newest = db.query(InvestigationCase).order_by(InvestigationCase.created_at.desc()).first()
    
    oldest_open = db.query(InvestigationCase).filter(
        InvestigationCase.status.in_(open_statuses)
    ).order_by(InvestigationCase.opened_at.asc()).first()

    # Priorities breakdown counts
    pri_counts = {p: 0 for p in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]}
    pri_query = db.query(
        InvestigationCase.priority, func.count(InvestigationCase.id)
    ).group_by(InvestigationCase.priority).all()
    for p, val in pri_query:
        if p in pri_counts:
            pri_counts[p] = val

    # Status breakdown counts
    st_counts = {s: 0 for s in ["OPEN", "ASSIGNED", "UNDER_INVESTIGATION", "WAITING_FOR_INFORMATION", "MITIGATED", "RESOLVED", "CLOSED"]}
    st_query = db.query(
        InvestigationCase.status, func.count(InvestigationCase.id)
    ).group_by(InvestigationCase.status).all()
    for s, val in st_query:
        if s in st_counts:
            st_counts[s] = val

    # Average Resolution Time (in hours)
    resolved_cases = db.query(InvestigationCase.opened_at, InvestigationCase.closed_at).filter(
        InvestigationCase.closed_at.isnot(None)
    ).all()

    avg_res_hours = 0.0
    if resolved_cases:
        diffs = [(c - o).total_seconds() / 3600.0 for o, c in resolved_cases]
        avg_res_hours = round(sum(diffs) / len(diffs), 2)

    return {
        "total_cases": total,
        "open_cases": open_cases,
        "critical_cases": critical_cases,
        "assigned_cases": assigned_cases,
        "average_resolution_time": avg_res_hours,
        "cases_by_priority": pri_counts,
        "cases_by_status": st_counts,
        "newest_case": newest,
        "oldest_open_case": oldest_open,
    }
