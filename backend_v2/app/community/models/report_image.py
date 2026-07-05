"""
community/models/report_image.py
SQLAlchemy model for community.report_images table.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ReportImage(Base):
    """An image URL attached to a product report. No physical upload — URL only."""

    __tablename__ = "report_images"
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
        index=True,
    )

    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )

    # Relationships
    report: Mapped["ProductReport"] = relationship(  # type: ignore[name-defined]
        "ProductReport",
        back_populates="images",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ReportImage id={self.id} report_id={self.report_id}>"
