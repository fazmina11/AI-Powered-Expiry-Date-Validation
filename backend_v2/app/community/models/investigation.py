"""
community/models/investigation.py
SQLAlchemy models for Investigation & Case Management Engine (ICME).
Includes: InvestigationCase, InvestigationNote, CaseEvidence, CaseTimeline.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, text, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InvestigationCase(Base):
    """Investigation case spawned on top of a high-risk or critical safety alert."""

    __tablename__ = "investigation_cases"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    case_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.safety_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.issue_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assigned_officer: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="MEDIUM", index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN", index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    resolution: Mapped[str] = mapped_column(Text, nullable=True)
    final_decision: Mapped[str] = mapped_column(String(50), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    # Relationships
    alert: Mapped["SafetyAlert"] = relationship("SafetyAlert", back_populates="cases", lazy="select")  # type: ignore[name-defined]
    cluster: Mapped["IssueCluster"] = relationship("IssueCluster", back_populates="cases", lazy="select")  # type: ignore[name-defined]
    
    notes: Mapped[list["InvestigationNote"]] = relationship("InvestigationNote", back_populates="case", cascade="all, delete-orphan", lazy="select")
    evidence: Mapped[list["CaseEvidence"]] = relationship("CaseEvidence", back_populates="case", cascade="all, delete-orphan", lazy="select")
    timeline: Mapped[list["CaseTimeline"]] = relationship("CaseTimeline", back_populates="case", cascade="all, delete-orphan", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InvestigationCase number={self.case_number} priority={self.priority} status={self.status}>"


class InvestigationNote(Base):
    """Note recorded during the course of an investigation case."""

    __tablename__ = "investigation_notes"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.investigation_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="SYSTEM")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    case: Mapped["InvestigationCase"] = relationship("InvestigationCase", back_populates="notes", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<InvestigationNote case_id={self.case_id} by={self.created_by}>"


class CaseEvidence(Base):
    """File attachment or image proof uploaded during investigation."""

    __tablename__ = "case_evidence"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.investigation_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False, default="IMAGE")  # IMAGE, DOCUMENT, RECEIPT, etc.
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String(100), nullable=False, default="SYSTEM")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    case: Mapped["InvestigationCase"] = relationship("InvestigationCase", back_populates="evidence", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CaseEvidence case_id={self.case_id} type={self.evidence_type}>"


class CaseTimeline(Base):
    """Timeline logging of transition events for audit trace."""

    __tablename__ = "case_timeline"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.investigation_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Investigation Created", "Status Updated"
    event_description: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by: Mapped[str] = mapped_column(String(100), nullable=False, default="SYSTEM")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    case: Mapped["InvestigationCase"] = relationship("InvestigationCase", back_populates="timeline", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<CaseTimeline case_id={self.case_id} event={self.event_type}>"
