"""
community/models/product_report.py
SQLAlchemy model for community.product_reports table.
"""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.community.enums import ReportType, ReportStatus, Severity


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProductReport(Base):
    """A consumer-submitted product quality / safety report."""

    __tablename__ = "product_reports"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    # Foreign key — references community.community_users
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.community_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    barcode: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    report_type: Mapped[ReportType] = mapped_column(
        SAEnum(ReportType, schema="community", name="report_type_enum"),
        nullable=False,
    )
    severity: Mapped[Severity] = mapped_column(
        SAEnum(Severity, schema="community", name="severity_enum"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    purchase_location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchase_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus, schema="community", name="report_status_enum"),
        nullable=False,
        default=ReportStatus.PENDING,
        server_default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    user: Mapped["CommunityUser"] = relationship(  # type: ignore[name-defined]
        "CommunityUser",
        back_populates="reports",
        lazy="select",
    )
    images: Mapped[list["ReportImage"]] = relationship(  # type: ignore[name-defined]
        "ReportImage",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="select",
    )
    credibility: Mapped["ReportCredibility"] = relationship(  # type: ignore[name-defined]
        "ReportCredibility",
        back_populates="report",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="select",
    )
    cluster_link: Mapped["ClusterReport"] = relationship(  # type: ignore[name-defined]
        "ClusterReport",
        back_populates="report",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ProductReport id={self.id} barcode={self.barcode} type={self.report_type}>"


from sqlalchemy import event

@event.listens_for(ProductReport, "before_delete")
def before_report_delete(mapper, connection, target):
    from sqlalchemy.orm import Session
    db = Session.object_session(target)
    if db:
        from app.community.services.issue_cluster_service import remove_report_from_cluster
        remove_report_from_cluster(db, target.id)
