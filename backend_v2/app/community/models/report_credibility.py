"""
community/models/report_credibility.py
SQLAlchemy model for community.report_credibility table.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReportCredibility(Base):
    """Credibility score and factor analysis for a consumer report."""

    __tablename__ = "report_credibility"
    __table_args__ = {"schema": "community"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("community.product_reports.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    barcode_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    batch_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    images_uploaded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    receipt_uploaded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    verified_user: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duplicate_reports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    location_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    purchase_date_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    credibility_level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    report: Mapped["ProductReport"] = relationship(  # type: ignore[name-defined]
        "ProductReport",
        back_populates="credibility",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ReportCredibility report_id={self.report_id} score={self.score}>"
