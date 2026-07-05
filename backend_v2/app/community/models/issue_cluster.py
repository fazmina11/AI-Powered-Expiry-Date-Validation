"""
community/models/issue_cluster.py
SQLAlchemy models for Product Issue Clustering Engine (PICE).
Includes: IssueCluster, ClusterReport, ClusterLocation.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IssueCluster(Base):
    """An aggregate cluster grouping related product reports together."""

    __tablename__ = "issue_clusters"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    cluster_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    reported_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.products.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    # Store barcode and batch directly on the cluster for matching ease
    barcode: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    primary_issue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NEW")
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")

    affected_reports_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    affected_users_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    affected_cities_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    first_reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    last_reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow)

    # Relationships
    reports: Mapped[list["ClusterReport"]] = relationship(
        "ClusterReport",
        back_populates="cluster",
        cascade="all, delete-orphan",
        lazy="select",
    )
    locations: Mapped[list["ClusterLocation"]] = relationship(
        "ClusterLocation",
        back_populates="cluster",
        cascade="all, delete-orphan",
        lazy="select",
    )
    intelligence: Mapped["ClusterIntelligence"] = relationship(  # type: ignore[name-defined]
        "ClusterIntelligence",
        back_populates="cluster",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
    )
    alerts: Mapped[list["SafetyAlert"]] = relationship(  # type: ignore[name-defined]
        "SafetyAlert",
        back_populates="cluster",
        cascade="all, delete-orphan",
        lazy="select",
    )
    cases: Mapped[list["InvestigationCase"]] = relationship(  # type: ignore[name-defined]
        "InvestigationCase",
        back_populates="cluster",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<IssueCluster code={self.cluster_code} reports={self.affected_reports_count}>"


class ClusterReport(Base):
    """Link mapping table between an IssueCluster and a ProductReport."""

    __tablename__ = "cluster_reports"
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
        index=True,
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.product_reports.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    cluster: Mapped[IssueCluster] = relationship("IssueCluster", back_populates="reports")
    report: Mapped["ProductReport"] = relationship(  # type: ignore[name-defined]
        "ProductReport",
        back_populates="cluster_link",
        lazy="joined",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ClusterReport cluster_id={self.cluster_id} report_id={self.report_id}>"


class ClusterLocation(Base):
    """Location metrics breakdown for a cluster."""

    __tablename__ = "cluster_locations"
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
        index=True,
    )

    country: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    report_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=_utcnow)

    # Relationships
    cluster: Mapped[IssueCluster] = relationship("IssueCluster", back_populates="locations")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ClusterLocation city={self.city} count={self.report_count}>"
