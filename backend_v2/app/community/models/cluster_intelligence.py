"""
community/models/cluster_intelligence.py
SQLAlchemy model for community.cluster_intelligence table.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ClusterIntelligence(Base):
    """Intelligence analytics metrics associated with an Issue Cluster in a 1-to-1 mapping."""

    __tablename__ = "cluster_intelligence"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    cluster_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.issue_clusters.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    growth_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    activity_level: Mapped[str] = mapped_column(String(30), nullable=False, default="LOW", index=True)
    trend: Mapped[str] = mapped_column(String(30), nullable=False, default="STABLE", index=True)
    spread_level: Mapped[str] = mapped_column(String(30), nullable=False, default="LOCAL", index=True)
    escalation_level: Mapped[str] = mapped_column(String(30), nullable=False, default="NONE")

    reports_last_24h: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_last_7_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_last_30_days: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    new_cities: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_credibility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_trending: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    
    last_calculated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    cluster: Mapped["IssueCluster"] = relationship(  # type: ignore[name-defined]
        "IssueCluster",
        back_populates="intelligence",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ClusterIntelligence cluster_id={self.cluster_id} risk={self.risk_score}>"
