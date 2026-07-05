"""
community/models/safety_alert.py
SQLAlchemy models for Community Safety Alert Engine (CSAE).
Includes: SafetyAlert, AlertHistory, AlertNotification.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SafetyAlert(Base):
    """Safety alert issued on top of an Issue Cluster meeting threshold criteria."""

    __tablename__ = "safety_alerts"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    alert_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.issue_clusters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alert_level: Mapped[str] = mapped_column(String(50), nullable=False, default="INFORMATION", index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE", index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    generated_reason: Mapped[str] = mapped_column(Text, nullable=False)
    generated_by: Mapped[str] = mapped_column(String(100), nullable=False, default="SYSTEM")

    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    affected_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    affected_users: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    affected_cities: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    cluster: Mapped["IssueCluster"] = relationship("IssueCluster", back_populates="alerts", lazy="select")  # type: ignore[name-defined]
    history: Mapped[list["AlertHistory"]] = relationship("AlertHistory", back_populates="alert", cascade="all, delete-orphan", lazy="select")
    notifications: Mapped[list["AlertNotification"]] = relationship("AlertNotification", back_populates="alert", cascade="all, delete-orphan", lazy="select")
    cases: Mapped[list["InvestigationCase"]] = relationship(  # type: ignore[name-defined]
        "InvestigationCase",
        back_populates="alert",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<SafetyAlert code={self.alert_code} level={self.alert_level} status={self.status}>"


class AlertHistory(Base):
    """History of status changes for a Safety Alert."""

    __tablename__ = "alert_history"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.safety_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    old_status: Mapped[str] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str] = mapped_column(String(100), nullable=False, default="SYSTEM")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    alert: Mapped["SafetyAlert"] = relationship("SafetyAlert", back_populates="history", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AlertHistory alert_id={self.alert_id} transition={self.old_status}->{self.new_status}>"


class AlertNotification(Base):
    """Log of recipient notifications sent for an alert."""

    __tablename__ = "alert_notifications"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.safety_alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., EMAIL, SMS, PUSH
    recipient: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(50), nullable=False, default="SENT")  # SENT, FAILED
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    alert: Mapped["SafetyAlert"] = relationship("SafetyAlert", back_populates="notifications", lazy="select")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AlertNotification alert_id={self.alert_id} recipient={self.recipient}>"
